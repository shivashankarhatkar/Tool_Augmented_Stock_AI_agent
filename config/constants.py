"""Static constants used across the project."""

# Tool names (must match keys registered in ToolRegistry)
TOOL_ALPHA_VANTAGE = "alpha_vantage"
TOOL_YAHOO_FINANCE = "yahoo_finance"
TOOL_NEWS_API = "news_api"
TOOL_SERPAPI = "serpapi"
TOOL_CALCULATOR = "calculator"

ALL_TOOL_NAMES = [
    TOOL_ALPHA_VANTAGE,
    TOOL_YAHOO_FINANCE,
    TOOL_NEWS_API,
    TOOL_SERPAPI,
    TOOL_CALCULATOR,
]

# Routing decisions used by the router node
ROUTE_TOOL = "tool"
ROUTE_RAG = "rag"
ROUTE_BOTH = "both"
ROUTE_DIRECT = "direct"

# Misc
MAX_PLANNER_TASKS = 5
DEFAULT_TIMEOUT_SECONDS = 20
MAX_LLM_RETRIES = 3
