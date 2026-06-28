"""Lightweight input validators used across tools and API layer."""
import re
from utils.exceptions import ValidationError

_TICKER_RE = re.compile(r"^[A-Z]{1,6}([.\-][A-Z]{1,4})?$")


# 
def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize a stock ticker symbol.

    Args:
        ticker: Stock ticker symbol provided by the user.

    Returns:
        The normalized ticker symbol in uppercase.

    Raises:
        ValidationError: If the ticker is empty or does not match
        the expected ticker format.
    """
    # Ensure the ticker is a non-empty string.
    if not ticker or not isinstance(ticker, str):
        raise ValidationError("Ticker must be a non-empty string.")

    # Remove surrounding whitespace and convert to uppercase.
    cleaned = ticker.strip().upper()

    # Validate the ticker against the allowed pattern.
    if not _TICKER_RE.match(cleaned):
        raise ValidationError(f"'{ticker}' does not look like a valid ticker symbol.")

    return cleaned


def validate_query(query: str, min_len: int = 3, max_len: int = 2000) -> str:
    """Validate a free-text user query."""
    if not query or not isinstance(query, str):
        raise ValidationError("Query must be a non-empty string.")
    cleaned = query.strip()
    if len(cleaned) < min_len:
        raise ValidationError(f"Query is too short (min {min_len} characters).")
    if len(cleaned) > max_len:
        raise ValidationError(f"Query is too long (max {max_len} characters).")
    return cleaned


def is_safe_math_expression(expression: str) -> bool:
    """Whitelist-based check that an expression contains only arithmetic characters."""
    return bool(re.fullmatch(r"[0-9eE+\-*/().,\s%^]+", expression or ""))
