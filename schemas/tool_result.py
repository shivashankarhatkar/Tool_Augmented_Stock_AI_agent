"""Schema representing the outcome of a tool execution."""
from typing import Any, Optional
from pydantic import BaseModel


class ToolResult(BaseModel):
    tool_name: str
    task_id: Optional[str] = None
    success: bool
    data: Any = None
    error: Optional[str] = None
