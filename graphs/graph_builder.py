"""Builds and compiles the LangGraph StateGraph for the agent."""
from langgraph.graph import StateGraph, END
from schemas.state import AgentState
from graphs.nodes import router_node, planner_node, tool_node, rag_node, synthesis_node
from graphs.edges import route_after_router, route_after_planner, route_after_tool


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("planner", planner_node)
    graph.add_node("tool", tool_node)
    graph.add_node("rag", rag_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {"planner": "planner", "rag": "rag", "synthesis": "synthesis"},
    )
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {"tool": "tool", "synthesis": "synthesis"},
    )
    graph.add_conditional_edges(
        "tool",
        route_after_tool,
        {"rag": "rag", "synthesis": "synthesis"},
    )
    graph.add_edge("rag", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()
