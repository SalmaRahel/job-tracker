import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import ValidationError

from ..auth.dependencies import get_current_user
from ..auth.models import User
from ..background_jobs.redis_client import check_and_set_cooldown
from ..config import settings
from .schemas import AskRequest, AskResponse
from .service import (
    InvalidQuestionError,
    QueryExecutionError,
    QueryPermissionError,
    QueryTimeoutError,
    QuestionRefusedError,
    SqlGenerationError,
    execute_query,
    format_answer,
    generate_sql,
)
from .validator import UnsafeSQLError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/job-search", tags=["job-search"])

COOLDOWN_ACTION = "job_search_ask"

INVALID_QUESTION = "Please ask a question between 1 and 500 characters."
REFUSED = "I can only answer questions about your own job applications."
UNSAFE = "I could not turn that into a safe query. Try rephrasing."
CANNOT_ANSWER = "I could not answer that."
TIMEOUT = "That question took too long. Try something simpler."
UNAVAILABLE = "I could not reach the assistant. Please try again."
INTERNAL = "Something went wrong. Please try again."
COOLDOWN = "Please wait a moment before asking another question."

ERROR_RESPONSES = (
    (InvalidQuestionError, 400, INVALID_QUESTION),
    (QuestionRefusedError, 400, REFUSED),
    (UnsafeSQLError, 400, UNSAFE),
    (QueryTimeoutError, 504, TIMEOUT),
    (SqlGenerationError, 502, UNAVAILABLE),
    ((QueryPermissionError, QueryExecutionError), 400, CANNOT_ANSWER),
)


def _error_for(exc: Exception) -> tuple[int, str]:
    for kind, status_code, message in ERROR_RESPONSES:
        if isinstance(exc, kind):
            return status_code, message
    logger.warning("ask failed: %s", type(exc).__name__)
    return 500, INTERNAL


@router.post("/ask", response_model=AskResponse)
def ask(payload: Any = Body(default=None), user: User = Depends(get_current_user)):
    try:
        question = AskRequest.model_validate(payload).question
    except ValidationError:
        raise HTTPException(status_code=400, detail=INVALID_QUESTION) from None

    try:
        allowed = check_and_set_cooldown(
            user.id, 0, COOLDOWN_ACTION, settings.job_search_cooldown_seconds
        )
    except Exception as exc:
        logger.warning("ask failed: %s", type(exc).__name__)
        raise HTTPException(status_code=500, detail=INTERNAL) from None
    if not allowed:
        raise HTTPException(status_code=429, detail=COOLDOWN)

    try:
        sql = generate_sql(question)
        result = execute_query(sql, user.id)
        answer = format_answer(question, result)
    except Exception as exc:
        status_code, message = _error_for(exc)
        raise HTTPException(status_code=status_code, detail=message) from None

    return AskResponse(answer=answer, row_count=len(result.rows))
