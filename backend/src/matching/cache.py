import hashlib
import json
import logging

from pydantic import ValidationError

from ..background_jobs.redis_client import r
from ..profile.schemas import ProfileResponse
from .schemas import MatchingOutput

logger = logging.getLogger(__name__)

PROMPT_VERSION = "analysis-v1"
CACHE_TTL_SECONDS = 30 * 24 * 60 * 60
KEY_PREFIX = "analysis_cache:"


def cache_key(job_description: str, profile: ProfileResponse) -> str:
    data = profile.model_dump(mode="json", exclude={"id"})
    data["skills"] = sorted({name.strip().casefold() for name in data["skills"]})
    payload = json.dumps(
        {"prompt_version": PROMPT_VERSION, "job_description": job_description, "profile": data},
        sort_keys=True,
        ensure_ascii=False,
    )
    return KEY_PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_cached(key: str) -> MatchingOutput | None:
    try:
        raw = r.get(key)
    except Exception:
        logger.warning("analysis cache read failed key=%s", key, exc_info=True)
        return None
    if raw is None:
        return None
    try:
        return MatchingOutput(**json.loads(raw))
    except (ValueError, TypeError, ValidationError):
        logger.warning("analysis cache entry invalid key=%s", key)
        return None


def store_cached(key: str, output: MatchingOutput) -> None:
    try:
        r.set(key, output.model_dump_json(), ex=CACHE_TTL_SECONDS)
    except Exception:
        logger.warning("analysis cache write failed key=%s", key, exc_info=True)
