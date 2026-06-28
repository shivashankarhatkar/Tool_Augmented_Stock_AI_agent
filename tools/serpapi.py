"""SerpAPI tool: general-purpose Google web search for things not covered by other tools."""
from typing import Any, Dict
import requests
from tools.base_tool import BaseTool
from utils.exceptions import ToolExecutionError, ConfigError
from utils.helpers import retry
from config.settings import settings

BASE_URL = "https://serpapi.com/search"


class SerpAPITool(BaseTool):
    name = "serpapi"
    description = "Run a general web search (Google) for facts not covered by financial data tools."

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string."},
                    "num_results": {"type": "integer", "description": "Number of results.", "default": 5},
                },
                "required": ["query"],
            },
        }

    @retry(max_attempts=2, delay_seconds=1.0)
    def _run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        if not settings.serpapi_api_key:
            raise ConfigError("SERPAPI_API_KEY is not configured.")
        params = {
            "q": query,
            "num": min(max(num_results, 1), 10),
            "api_key": settings.serpapi_api_key,
            "engine": "google",
        }
        resp = requests.get(BASE_URL, params=params, timeout=15)
        if resp.status_code != 200:
            raise ToolExecutionError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")
        payload = resp.json()
        results = [
            {
                "title": r.get("title"),
                "link": r.get("link"),
                "snippet": r.get("snippet"),
            }
            for r in payload.get("organic_results", [])
        ]
        return {"query": query, "results": results}
