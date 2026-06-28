"""Helpers for parsing structured data out of raw LLM responses."""
from typing import Any, Dict, List
from utils.helpers import safe_json_loads
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_json_response(content: str, default: Any = None) -> Any:
    """Parse a JSON object/array the LLM was instructed to return."""
    parsed = safe_json_loads(content, default=default)
    if parsed is None and default is None:
        logger.warning("LLM response could not be parsed as JSON.")
    return parsed


def parse_native_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize OpenAI-style native tool_calls (JSON string args) into plain dicts."""
    normalized = []
    for tc in tool_calls:
        args = safe_json_loads(tc.get("arguments", "{}"), default={})
        normalized.append({"name": tc.get("name"), "args": args, "id": tc.get("id")})
    return normalized
