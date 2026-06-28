"""Unit tests for individual tools."""
import pytest
from tools.calculator import CalculatorTool
from tools.tool_registry import ToolRegistry
from utils.exceptions import ValidationError


def test_calculator_basic():
    tool = CalculatorTool()
    result = tool.run(expression="(150-100)/100*100")
    assert result.success is True
    assert result.data["result"] == pytest.approx(50.0)


def test_calculator_rejects_unsafe_expression():
    tool = CalculatorTool()
    result = tool.run(expression="__import__('os').system('echo hi')")
    assert result.success is False


def test_tool_registry_lists_all_tools():
    registry = ToolRegistry()
    names = registry.list_names()
    for expected in ("alpha_vantage", "yahoo_finance", "news_api", "serpapi", "calculator"):
        assert expected in names


def test_tool_registry_unknown_tool_raises():
    registry = ToolRegistry()
    with pytest.raises(Exception):
        registry.get("not_a_real_tool")
