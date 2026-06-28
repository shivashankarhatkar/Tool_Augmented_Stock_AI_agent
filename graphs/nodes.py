"""Node functions executed within the LangGraph workflow."""
from typing import Any, Dict, List
from schemas.state import AgentState
from schemas.task import Task
from schemas.tool_result import ToolResult
from llm.llm_factory import get_llm_client
from llm.response_parser import parse_json_response
from prompts.router_prompt import build_router_prompt
from prompts.planner_prompt import build_planner_prompt
from prompts.synthesis_prompt import build_synthesis_prompt
from prompts.system_prompt import SYSTEM_PROMPT
from tools.tool_registry import tool_registry
from rag.retriever import Retriever
from config.constants import ROUTE_TOOL, ROUTE_RAG, ROUTE_BOTH, ROUTE_DIRECT, MAX_PLANNER_TASKS
from utils.logger import get_logger
from utils.exceptions import AgentBaseException

logger = get_logger(__name__)

_retriever: Retriever = None  # lazily initialized to avoid loading embedding model unless needed


def _get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


# 
def _llm_chat(prompt: str) -> str:
    """
    Send a prompt to the configured LLM and return its response.

    Args:
        prompt: User prompt to be sent to the language model.

    Returns:
        The generated response text from the LLM.
    """
    # Get the configured LLM client (e.g., Gemini or OpenAI).
    client = get_llm_client()

    # Construct the conversation with a system prompt and the user's prompt.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    # Send the request to the LLM.
    response = client.chat(messages=messages)

    # Return only the generated text from the response.
    return response.get("content", "")


# ---------------------------------------------------------------------------
# Router node
# ---------------------------------------------------------------------------
def router_node(state: AgentState) -> AgentState:
    query = state["query"]
    try:
        raw = _llm_chat(build_router_prompt(query))
        parsed = parse_json_response(raw, default={"route": ROUTE_DIRECT})
        route = parsed.get("route", ROUTE_DIRECT) if isinstance(parsed, dict) else ROUTE_DIRECT
        if route not in (ROUTE_TOOL, ROUTE_RAG, ROUTE_BOTH, ROUTE_DIRECT):
            route = ROUTE_DIRECT
        logger.info(f"Router decided route='{route}' for query='{query}'")
        return {**state, "route": route}
    except AgentBaseException as exc:
        logger.error(f"Router node failed, defaulting to direct: {exc}")
        return {**state, "route": ROUTE_DIRECT, "error": str(exc)}


# ---------------------------------------------------------------------------
# Planner node (produces tasks for the tool node)
# ---------------------------------------------------------------------------
# def planner_node(state: AgentState) -> AgentState:
#     query = state["query"]
#     try:
#         raw = _llm_chat(
#             build_planner_prompt(query, tool_registry.all_schemas(), max_tasks=MAX_PLANNER_TASKS)
#         )
#         parsed = parse_json_response(raw, default=[])
#         tasks: List[Task] = []
#         if isinstance(parsed, list):
#             for i, item in enumerate(parsed[:MAX_PLANNER_TASKS]):
#                 try:
#                     tasks.append(
#                         Task(
#                             task_id=item.get("task_id", f"t{i}"),
#                             tool_name=item["tool_name"],
#                             args=item.get("args", {}),
#                             description=item.get("description", ""),
#                         )
#                     )
#                 except Exception as exc:  # noqa: BLE001
#                     logger.warning(f"Skipping malformed planner task {item}: {exc}")
#         logger.info(f"Planner produced {len(tasks)} task(s).")
#         return {**state, "plan": tasks}
#     except AgentBaseException as exc:
#         logger.error(f"Planner node failed: {exc}")
#         return {**state, "plan": [], "error": str(exc)}

def planner_node(state: AgentState) -> AgentState:
    """
    Generate an execution plan for the user's query.

    This node uses the LLM to analyze the user's query and create a list
    of tool-calling tasks that will be executed later in the workflow.

    Args:
        state: Current workflow state containing the user's query.

    Returns:
        Updated workflow state containing the generated execution plan.
        If planning fails, an empty plan and error message are returned.
    """
    query = state["query"]

    try:
        # Ask the LLM to generate a structured execution plan.
        raw = _llm_chat(
            build_planner_prompt(
                query,
                tool_registry.all_schemas(),
                max_tasks=MAX_PLANNER_TASKS,
            )
        )

        # Parse the LLM response into JSON.
        parsed = parse_json_response(raw, default=[])

        tasks: List[Task] = []

        # Convert each JSON task into a Task object.
        if isinstance(parsed, list):
            for i, item in enumerate(parsed[:MAX_PLANNER_TASKS]):
                try:
                    tasks.append(
                        Task(
                            task_id=item.get("task_id", f"t{i}"),
                            tool_name=item["tool_name"],
                            args=item.get("args", {}),
                            description=item.get("description", ""),
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    # Skip invalid tasks instead of stopping the workflow.
                    logger.warning(f"Skipping malformed planner task {item}: {exc}")

        logger.info(f"Planner produced {len(tasks)} task(s).")

        # Store the generated execution plan in the workflow state.
        return {**state, "plan": tasks}

    except AgentBaseException as exc:
        # Return an empty plan if planning fails.
        logger.error(f"Planner node failed: {exc}")
        return {**state, "plan": [], "error": str(exc)}




# ---------------------------------------------------------------------------
# Tool execution node
# ---------------------------------------------------------------------------
def tool_node(state: AgentState) -> AgentState:
    plan: List[Task] = state.get("plan", [])
    results: List[ToolResult] = []

    for task in plan:
        try:
            tool = tool_registry.get(task.tool_name)
            result = tool.run(**task.args)
            result.task_id = task.task_id
            results.append(result)
        except AgentBaseException as exc:
            logger.error(f"Task '{task.task_id}' failed: {exc}")
            results.append(
                ToolResult(tool_name=task.tool_name, task_id=task.task_id, success=False, error=str(exc))
            )

    return {**state, "tool_results": results}


# ---------------------------------------------------------------------------
# RAG retrieval node
# ---------------------------------------------------------------------------
def rag_node(state: AgentState) -> AgentState:
    query = state["query"]
    try:
        retriever = _get_retriever()
        rag_result = retriever.retrieve(query)
        return {**state, "rag_result": rag_result}
    except AgentBaseException as exc:
        logger.error(f"RAG node failed: {exc}")
        return {**state, "rag_result": None, "error": str(exc)}


# ---------------------------------------------------------------------------
# Synthesis node (final answer)
# ---------------------------------------------------------------------------
def synthesis_node(state: AgentState) -> AgentState:
    query = state["query"]
    route = state.get("route", ROUTE_DIRECT)

    if route == ROUTE_DIRECT:
        try:
            answer = _llm_chat(query)
        except AgentBaseException as exc:
            answer = f"I couldn't process that request: {exc}"
        return {**state, "final_answer": answer}

    tool_results: List[ToolResult] = state.get("tool_results", []) or []
    tool_text_lines = []
    for r in tool_results:
        if r.success:
            tool_text_lines.append(f"[{r.tool_name}] {r.data}")
        else:
            tool_text_lines.append(f"[{r.tool_name}] ERROR: {r.error}")
    tool_results_text = "\n".join(tool_text_lines)

    rag_result = state.get("rag_result")
    rag_context_text = rag_result.context_text if rag_result and rag_result.chunks else ""

    try:
        prompt = build_synthesis_prompt(query, tool_results_text, rag_context_text)
        answer = _llm_chat(prompt)
    except AgentBaseException as exc:
        answer = f"I gathered some data but couldn't synthesize a final answer: {exc}"

    return {**state, "final_answer": answer}
