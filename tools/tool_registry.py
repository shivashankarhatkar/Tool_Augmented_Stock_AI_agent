"""Central registry mapping tool names to tool instances."""
from typing import Dict, List
from tools.base_tool import BaseTool
from tools.alpha_vantage import AlphaVantageTool
from tools.yahoo_finance import YahooFinanceTool
from tools.news_api import NewsAPITool
from tools.serpapi import SerpAPITool
from tools.calculator import CalculatorTool
from utils.exceptions import ConfigError


class ToolRegistry:
    """Holds all available tools and exposes lookup/listing helpers."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        for tool in (
            AlphaVantageTool(),
            YahooFinanceTool(),
            NewsAPITool(),
            SerpAPITool(),
            CalculatorTool(),
        ):
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ConfigError(f"Tool '{name}' is not registered. Available: {list(self._tools)}")
        return self._tools[name]

    def list_names(self) -> List[str]:
        return list(self._tools.keys())

    def all_schemas(self) -> List[dict]:
        return [tool.schema() for tool in self._tools.values()]


# Singleton instance used throughout the app
tool_registry = ToolRegistry()
