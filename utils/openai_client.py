"""OpenAI client using chat.completions.parse() for structured Pydantic output. Retries, no framework."""
import logging
import time
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=OPENAI_API_KEY)


def chat_with_structured_output(
    system_prompt: str,
    user_prompt: str,
    response_model: type[T],
    model: str | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
) -> T:
    """
    Call OpenAI chat.completions.parse() with your Pydantic model as response_format.
    The API returns guaranteed schema-conforming JSON and the SDK parses it into response_model.
    Retries on 429/5xx.
    """
    client = _get_client()
    model = model or OPENAI_MODEL
    max_tokens = max_tokens or OPENAI_MAX_TOKENS

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(max_retries):
        try:
            start = time.perf_counter()
            completion = client.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
                max_tokens=max_tokens,
            )
            elapsed = time.perf_counter() - start
            usage = getattr(completion, "usage", None)
            token_usage = (
                f"prompt={getattr(usage, 'prompt_tokens', 0)} completion={getattr(usage, 'completion_tokens', 0)}"
                if usage
                else "n/a"
            )
            logger.info(
                "openai_parse agent=%s elapsed_sec=%.2f %s",
                response_model.__name__,
                elapsed,
                token_usage,
            )

            message = completion.choices[0].message
            if getattr(message, "refusal", None):
                raise ValueError(f"Model refused the request: {message.refusal}")
            if not getattr(message, "parsed", None):
                raise ValueError(
                    "No parsed response (model may have returned content that did not match the schema)"
                )
            return message.parsed
        except Exception as e:
            is_retryable = (
                "429" in str(e)
                or "500" in str(e)
                or "503" in str(e)
                or "rate" in str(e).lower()
            )
            if is_retryable and attempt < max_retries - 1:
                wait = 2**attempt
                logger.warning(
                    "openai_retry attempt=%s error=%s wait_sec=%s",
                    attempt + 1,
                    e,
                    wait,
                )
                time.sleep(wait)
            else:
                raise
