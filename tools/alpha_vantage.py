"""Alpha Vantage API tool: fundamental + quote data for a stock ticker."""
from typing import Any, Dict
import requests
from tools.base_tool import BaseTool
from utils.validators import validate_ticker
from utils.exceptions import ToolExecutionError, ConfigError
from utils.helpers import retry
from config.settings import settings

BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageTool(BaseTool):
    name = "alpha_vantage"
    description = "Fetch real-time stock quote and company overview/fundamentals for a ticker symbol."

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL"},
                    "function": {
                        "type": "string",
                        "enum": ["GLOBAL_QUOTE", "OVERVIEW"],
                        "description": "Which Alpha Vantage endpoint to call.",
                    },
                },
                "required": ["ticker"],
            },
        }

    @retry(max_attempts=2, delay_seconds=1.0)
    def _run(self, ticker: str, function: str = "GLOBAL_QUOTE") -> Dict[str, Any]:
        if not settings.alpha_vantage_api_key:
            raise ConfigError("ALPHA_VANTAGE_API_KEY is not configured.")
        ticker = validate_ticker(ticker)
        params = {
            "function": function,
            "symbol": ticker,
            "apikey": settings.alpha_vantage_api_key,
        }
        resp = requests.get(BASE_URL, params=params, timeout=15)
        if resp.status_code != 200:
            raise ToolExecutionError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")
        payload = resp.json()
        if "Note" in payload or "Information" in payload:
            raise ToolExecutionError(self.name, payload.get("Note") or payload.get("Information"))
        return payload
