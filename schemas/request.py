"""Incoming API request schema."""
from typing import Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="User's natural language question.")
    session_id: Optional[str] = Field(default=None, description="Optional session/conversation identifier.")
