"""Outgoing API response schema."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class QueryResponse(BaseModel):
    answer: str
    session_id: Optional[str] = None
    route: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = []
    sources: List[str] = []
    error: Optional[str] = None
