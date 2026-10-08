import logging
from dataclasses import dataclass
from datetime import date

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from src.config import settings
from src.gemini import call_gemini

from .utils import (
    build_answer_prompt,
    build_fallback_summary,
    build_sql_prompt,
    clean_question,
    get_readonly_engine,
    sanitize_rows,
    strip_code_fences,
)
from .validator import UnsafeSQLError, validate_sql

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_QUESTION_LENGTH = 500
TIMEOUT_SQLSTATE = "57014"
PERMISSION_SQLSTATE = "42501"
MAX_ANSWER_LENGTH = 1000
NO_ROWS_MESSAGE = "I could not find any applications matching your question."


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[dict]


class QueryError(Exception):
    pass


class QueryTimeoutError(QueryError):
    pass


class QueryPermissionError(QueryError):
    pass


class QueryExecutionError(QueryError):
    pass


class InvalidQuestionError(Exception):
    pass


class QuestionRefusedError(Exception):
    pass


class SqlGenerationError(Exception):
    pass


def _prepare_question(question: str) -> str:
    if not isinstance(question, str) or len(question) > MAX_QUESTION_LENGTH:
        raise InvalidQuestionError("question is missing or too long")
    cleaned = clean_question(question)
    if not cleaned:
        raise InvalidQuestionError("question is empty")
    return cleaned


def generate_sql(question: str) -> str:
    cleaned = _prepare_question(question)
    prompt = build_sql_prompt(cleaned, date.today())

    try:
        reply = call_gemini(prompt, max_retries=1, model_name=MODEL_NAME)
    except Exception as exc:
        logger.warning("gemini call failed: %s", type(exc).__name__)
        raise SqlGenerationError("gemini call failed") from None

    if not reply or not reply.strip():
        logger.warning("gemini returned an empty reply")
        raise SqlGenerationError("empty reply")

    candidate = strip_code_fences(reply)
    if candidate.strip().strip(".").upper() == "REFUSE":
        logger.info("question refused by the model")
        raise QuestionRefusedError("question refused")

    try:
        return validate_sql(candidate)
    except UnsafeSQLError as exc:
        logger.warning("generated sql rejected: %s", exc.reason)
        raise


def _timeout_ms() -> int:
    seconds = settings.job_search_statement_timeout_seconds
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds <= 0:
        raise ValueError("statement timeout must be a positive integer")
    return seconds * 1000


def execute_query(sql: str, user_id: int) -> QueryResult:
    timeout_ms = _timeout_ms()
    user_id_text = str(int(user_id))
    max_rows = settings.job_search_max_rows
    engine = get_readonly_engine()

    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.exec_driver_sql("SET TRANSACTION READ ONLY")
                conn.exec_driver_sql(f"SET LOCAL statement_timeout = {timeout_ms}")
                conn.execute(
                    text("SELECT set_config('app.user_id', :id, true)"),
                    {"id": user_id_text},
                )
                result = conn.exec_driver_sql(sql.replace("%", "%%"))
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchmany(max_rows)]
    except DBAPIError as exc:
        code = getattr(exc.orig, "pgcode", None)
        logger.warning("query failed: sqlstate=%s", code)
        if code == TIMEOUT_SQLSTATE:
            raise QueryTimeoutError("query timed out") from None
        if code == PERMISSION_SQLSTATE:
            raise QueryPermissionError("query not permitted") from None
        raise QueryExecutionError("query failed") from None

    return QueryResult(columns=columns, rows=rows)


def _cap_answer(answer: str) -> str:
    answer = answer.strip()
    if len(answer) <= MAX_ANSWER_LENGTH:
        return answer
    return answer[: MAX_ANSWER_LENGTH - 3].rstrip() + "..."


def format_answer(question: str, result: QueryResult) -> str:
    total = len(result.rows)
    if total == 0:
        return _cap_answer(NO_ROWS_MESSAGE)

    rows = sanitize_rows(result.rows, settings.job_search_max_rows)
    cleaned_question = clean_question(question)[:MAX_QUESTION_LENGTH] if isinstance(question, str) else ""
    prompt = build_answer_prompt(cleaned_question, rows, total)

    try:
        reply = call_gemini(prompt, max_retries=1, model_name=MODEL_NAME)
    except Exception as exc:
        logger.warning("answer generation failed: %s", type(exc).__name__)
        return _cap_answer(build_fallback_summary(rows, total))

    if not isinstance(reply, str) or not reply.strip():
        logger.warning("answer reply was empty")
        return _cap_answer(build_fallback_summary(rows, total))

    return _cap_answer(reply)
