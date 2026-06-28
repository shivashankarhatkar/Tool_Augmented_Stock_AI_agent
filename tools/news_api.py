"""NewsAPI.org tool: recent news headlines relevant to a company or topic."""
from typing import Any, Dict
import requests
from tools.base_tool import BaseTool
from utils.exceptions import ToolExecutionError, ConfigError
from utils.helpers import retry
from config.settings import settings

BASE_URL = "https://newsapi.org/v2/everything"


class NewsAPITool(BaseTool):
    name = "news_api"
    description = "Fetch recent news articles about a company, ticker, or financial topic."

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords, e.g. 'Apple Inc earnings'"},
                    "page_size": {"type": "integer", "description": "Number of articles to return.", "default": 5},
                },
                "required": ["query"],
            },
        }

    @retry(max_attempts=2, delay_seconds=1.0)
    def _run(self, query: str, page_size: int = 5) -> Dict[str, Any]:
        if not settings.news_api_key:
            raise ConfigError("NEWS_API_KEY is not configured.")
        params = {
            "q": query,
            "pageSize": min(max(page_size, 1), 20),
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": settings.news_api_key,
        }
        resp = requests.get(BASE_URL, params=params, timeout=15)
        if resp.status_code != 200:
            raise ToolExecutionError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")
        payload = resp.json()
        articles = [
            {
                "title": a.get("title"),
                "source": (a.get("source") or {}).get("name"),
                "publishedAt": a.get("publishedAt"),
                "url": a.get("url"),
                "description": a.get("description"),
            }
            for a in payload.get("articles", [])
        ]
        return {"query": query, "articles": articles}
