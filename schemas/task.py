"""Schema representing a single planned task/tool-call."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    task_id: str = Field(..., description="Unique identifier for this task within the plan.")
    tool_name: str = Field(..., description="Name of the registered tool to invoke.")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments passed to the tool.")
    description: str = Field(default="", description="Human-readable purpose of this task.")
    depends_on: Optional[str] = Field(default=None, description="task_id this task depends on, if any.")
