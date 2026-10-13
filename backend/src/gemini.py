import logging
import time
from google import genai
from google.genai import errors, types
from src.config import settings

logger = logging.getLogger(__name__)

FALLBACK_MODEL = "gemini-3.5-flash-lite"
FALLBACK_STATUS_CODES = (429, 503)

client = genai.Client(api_key=settings.gemini_api_key)

def build_config(temperature: float | None, thinking_level: str | None):
    if temperature is None and thinking_level is None:
        return None
    options = {}
    if temperature is not None:
        options["temperature"] = temperature
    if thinking_level is not None:
        options["thinking_config"] = types.ThinkingConfig(thinking_level=types.ThinkingLevel(thinking_level))
    return types.GenerateContentConfig(**options)


def _generate(prompt, max_retries, model_name, config, thinking_level, started):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            logger.info(
                "gemini call model=%s thinking=%s attempts=%s retried=%s seconds=%.2f",
                model_name, thinking_level or "default", attempt, attempt > 1, time.perf_counter() - started,
            )
            return response.text
        except errors.APIError:
            if attempt == max_retries:
                logger.warning(
                    "gemini call failed model=%s attempts=%s seconds=%.2f",
                    model_name, attempt, time.perf_counter() - started,
                )
                raise
            wait_time = 2 **attempt
            time.sleep(wait_time)


def call_gemini(
    prompt: str,
    max_retries: int,
    model_name: str,
    temperature: float | None = None,
    thinking_level: str | None = None,
) -> str:
    config = build_config(temperature, thinking_level)
    started = time.perf_counter()
    try:
        return _generate(prompt, max_retries, model_name, config, thinking_level, started)
    except errors.APIError as original:
        if original.code not in FALLBACK_STATUS_CODES or model_name == FALLBACK_MODEL:
            raise
        logger.warning(
            "gemini fallback original_model=%s status=%s fallback_model=%s",
            model_name, original.code, FALLBACK_MODEL,
        )
        try:
            return _generate(prompt, 1, FALLBACK_MODEL, config, thinking_level, started)
        except errors.APIError:
            raise original
