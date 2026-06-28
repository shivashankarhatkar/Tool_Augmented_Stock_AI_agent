"""Prompt that decides how to route an incoming query."""

ROUTER_PROMPT_TEMPLATE = """Classify the user's query into exactly one route.

Routes:
- "tool": the query needs real-time/factual data (prices, fundamentals, news, calculations).
- "rag": the query is about timeless investing principles/strategy best answered from books.
- "both": the query needs both live data AND conceptual/book knowledge.
- "direct": the query is conversational/general and needs neither (e.g. greetings, clarifications).

Respond with ONLY a JSON object, no prose, no markdown fences:
{{"route": "<tool|rag|both|direct>", "reasoning": "<one short sentence>"}}

User query: {query}
"""


def build_router_prompt(query: str) -> str:
    return ROUTER_PROMPT_TEMPLATE.format(query=query)
