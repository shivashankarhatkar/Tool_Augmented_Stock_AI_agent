"""Generic helper functions shared across modules."""
import functools
import json
import time
from typing import Any, Callable, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def timed(func: Callable) -> Callable:
    """Decorator that logs the execution time of a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        return result

    return wrapper


def retry(max_attempts: int = 3, delay_seconds: float = 1.0, backoff: float = 2.0):
    """Simple retry decorator with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay_seconds
            last_exc: Optional[Exception] = None
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    attempt += 1
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {exc}"
                    )
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Parse JSON, stripping markdown code fences if present, with a safe fallback."""
    if not text:
        return default
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from LLM output: {text[:200]}")
        return default
