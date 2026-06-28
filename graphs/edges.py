"""Conditional edge functions used to wire up the LangGraph workflow."""
from schemas.state import AgentState
from config.constants import ROUTE_TOOL, ROUTE_RAG, ROUTE_BOTH, ROUTE_DIRECT


def route_after_router(state: AgentState) -> str:
    """Decide the next node after the router has classified the query."""
    route = state.get("route", ROUTE_DIRECT)
    if route == ROUTE_TOOL:
        return "planner"
    if route == ROUTE_RAG:
        return "rag"
    if route == ROUTE_BOTH:
        return "planner"  # planner runs first, then rag, then synthesis (see graph_builder)
    return "synthesis"  # direct route skips straight to synthesis/LLM answer


def route_after_planner(state: AgentState) -> str:
    """After planning, decide whether to also run RAG (route == 'both') or go straight to tools."""
    route = state.get("route", ROUTE_TOOL)
    return "tool" if state.get("plan") else "synthesis"


def route_after_tool(state: AgentState) -> str:
    """After tools run, decide whether RAG retrieval is also needed (route == 'both')."""
    route = state.get("route", ROUTE_TOOL)
    return "rag" if route == ROUTE_BOTH else "synthesis"
