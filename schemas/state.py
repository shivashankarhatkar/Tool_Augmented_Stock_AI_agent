"""Shared state passed between LangGraph nodes."""
from typing import Any, Dict, List, Optional, TypedDict
from schemas.task import Task
from schemas.tool_result import ToolResult
from schemas.rag_result import RAGResult


class AgentState(TypedDict, total=False):
    query: str
    session_id: Optional[str]

    route: Optional[str]                 # "tool" | "rag" | "both" | "direct"
    plan: List[Task]                     # tasks produced by the planner
    tool_results: List[ToolResult]       # results of executed tasks
    rag_result: Optional[RAGResult]      # retrieval results, if any

    final_answer: Optional[str]
    error: Optional[str]

    # raw history of messages exchanged with the LLM, for debugging/tracing
    messages: List[Dict[str, Any]]
