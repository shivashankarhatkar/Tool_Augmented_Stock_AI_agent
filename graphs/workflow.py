"""High-level Workflow class: the main entrypoint for running a query through the agent."""
from typing import Any, Dict
from graphs.graph_builder import build_graph
from schemas.response import QueryResponse
from utils.logger import get_logger

logger = get_logger(__name__)


# class Workflow:
#     def __init__(self):
#         self._graph = build_graph()

#     def run(self, query: str, session_id: str = None) -> QueryResponse:
#         initial_state: Dict[str, Any] = {
#             "query": query,
#             "session_id": session_id,
#             "messages": [],
#         }
#         final_state = self._graph.invoke(initial_state)

#         tool_results = final_state.get("tool_results", []) or []
#         rag_result = final_state.get("rag_result")

#         sources = [r.tool_name for r in tool_results if r.success]
#         if rag_result and rag_result.chunks:
#             sources.extend(sorted({c.source for c in rag_result.chunks}))

#         return QueryResponse(
#             answer=final_state.get("final_answer") or "I wasn't able to generate an answer.",
#             session_id=session_id,
#             route=final_state.get("route"),
#             tool_calls=[r.model_dump() for r in tool_results],
#             sources=sources,
#             error=final_state.get("error"),
#         )

class Workflow:
    """
    Orchestrates the LangGraph workflow for processing user queries.
    """

    def __init__(self):
        # Build and compile the LangGraph workflow.
        self._graph = build_graph()

    def run(self, query: str, session_id: str = None) -> QueryResponse:
        """
        Execute the workflow for a given user query.

        Args:
            query: User's input question.
            session_id: Optional session identifier for maintaining conversation state.

        Returns:
            A QueryResponse containing the generated answer, tool usage,
            retrieved sources, routing information, and any errors.
        """
        # Initialize the workflow state.
        initial_state: Dict[str, Any] = {
            "query": query,
            "session_id": session_id,
            "messages": [],
        }

        # Execute the LangGraph workflow.
        final_state = self._graph.invoke(initial_state)

        # Extract tool execution results and RAG retrieval results.
        tool_results = final_state.get("tool_results", []) or []
        rag_result = final_state.get("rag_result")

        # Collect the names of successfully executed tools.
        sources = [r.tool_name for r in tool_results if r.success]

        # Add unique document sources retrieved through RAG.
        if rag_result and rag_result.chunks:
            sources.extend(sorted({c.source for c in rag_result.chunks}))

        # Build and return the final API response.
        return QueryResponse(
            answer=final_state.get("final_answer") or "I wasn't able to generate an answer.",
            session_id=session_id,
            route=final_state.get("route"),
            tool_calls=[r.model_dump() for r in tool_results],
            sources=sources,
            error=final_state.get("error"),
        )

# Singleton, built once per process
_workflow_instance: Workflow = None


def get_workflow() -> Workflow:
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = Workflow()
    return _workflow_instance
