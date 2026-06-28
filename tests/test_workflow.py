"""Unit tests for LangGraph conditional routing logic (pure functions, no LLM calls)."""
from graphs.edges import route_after_router, route_after_planner, route_after_tool
from schemas.task import Task
from config.constants import ROUTE_TOOL, ROUTE_RAG, ROUTE_BOTH, ROUTE_DIRECT


def test_route_after_router_tool():
    assert route_after_router({"route": ROUTE_TOOL}) == "planner"


def test_route_after_router_rag():
    assert route_after_router({"route": ROUTE_RAG}) == "rag"


def test_route_after_router_direct():
    assert route_after_router({"route": ROUTE_DIRECT}) == "synthesis"


def test_route_after_planner_with_tasks():
    task = Task(task_id="t1", tool_name="calculator", args={"expression": "1+1"})
    assert route_after_planner({"route": ROUTE_TOOL, "plan": [task]}) == "tool"


def test_route_after_planner_no_tasks():
    assert route_after_planner({"route": ROUTE_TOOL, "plan": []}) == "synthesis"


def test_route_after_tool_both_goes_to_rag():
    assert route_after_tool({"route": ROUTE_BOTH}) == "rag"


def test_route_after_tool_tool_only_goes_to_synthesis():
    assert route_after_tool({"route": ROUTE_TOOL}) == "synthesis"
