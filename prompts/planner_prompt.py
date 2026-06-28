"""Prompt that turns a query into a concrete list of tool-call tasks."""
import json

PLANNER_PROMPT_TEMPLATE = """You are a task planner. Break the user's query into a short ordered
list of tool calls needed to answer it. Use only the tools listed below.

Available tools (name: description -> parameters):
{tool_descriptions}

Rules:
- Use the minimum number of tasks needed (max {max_tasks}).
- Each task must reference a real tool name from the list above.
- If the query needs no tools, return an empty list.
- Respond with ONLY a JSON array, no prose, no markdown fences. Example:
[{{"task_id": "t1", "tool_name": "yahoo_finance", "args": {{"ticker": "AAPL"}}, "description": "Get current AAPL price"}}]

User query: {query}
"""


def build_planner_prompt(query: str, tool_schemas: list, max_tasks: int = 5) -> str:
    tool_descriptions = "\n".join(
        f"- {t['name']}: {t['description']} -> params: {json.dumps(t['parameters'])}"
        for t in tool_schemas
    )
    return PLANNER_PROMPT_TEMPLATE.format(
        tool_descriptions=tool_descriptions, query=query, max_tasks=max_tasks
    )
