import time
from google import genai
from google.genai import errors, types
from src.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

def call_gemini(prompt: str, max_retries: int, model_name: str, temperature: float | None = None) -> str:
    config = None if temperature is None else types.GenerateContentConfig(temperature=temperature)
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            return response.text
        except errors.APIError:
            if attempt == max_retries:
                raise
            wait_time = 2 **attempt
            time.sleep(wait_time)
