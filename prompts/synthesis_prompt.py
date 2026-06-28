"""Prompt that synthesizes tool results + RAG context into a final answer."""

SYNTHESIS_PROMPT_TEMPLATE = """Answer the user's query using ONLY the evidence provided below.
If the evidence is insufficient or a tool failed, clearly say what is missing rather than guessing.
Cite sources inline (tool name or book title) where you use them.

User query:
{query}

--- Tool results ---
{tool_results}

--- Book / RAG context ---
{rag_context}

Write a clear, well-organized final answer for the user now.
"""


def build_synthesis_prompt(query: str, tool_results_text: str, rag_context_text: str) -> str:
    return SYNTHESIS_PROMPT_TEMPLATE.format(
        query=query,
        tool_results=tool_results_text or "(none)",
        rag_context=rag_context_text or "(none)",
    )
