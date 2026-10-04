import logging
from datetime import date

from src.gemini import call_gemini

from .utils import build_sql_prompt, clean_question, strip_code_fences
from .validator import UnsafeSQLError, validate_sql

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_QUESTION_LENGTH = 500


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

    text = strip_code_fences(reply)
    if text.strip().strip(".").upper() == "REFUSE":
        logger.info("question refused by the model")
        raise QuestionRefusedError("question refused")

    try:
        return validate_sql(text)
    except UnsafeSQLError as exc:
        logger.warning("generated sql rejected: %s", exc.reason)
        raise
