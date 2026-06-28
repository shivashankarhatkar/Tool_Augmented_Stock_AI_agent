"""Unit tests for orchestrator-level schemas and validation helpers."""
import pytest
from schemas.task import Task
from schemas.tool_result import ToolResult
from utils.validators import validate_ticker, validate_query
from utils.exceptions import ValidationError


def test_task_schema_defaults():
    task = Task(task_id="t1", tool_name="calculator", args={"expression": "1+1"})
    assert task.description == ""
    assert task.depends_on is None


def test_tool_result_failure_state():
    result = ToolResult(tool_name="calculator", success=False, error="boom")
    assert result.data is None
    assert result.error == "boom"


def test_validate_ticker_normalizes_case():
    assert validate_ticker("aapl") == "AAPL"


def test_validate_ticker_rejects_garbage():
    with pytest.raises(ValidationError):
        validate_ticker("123-not-a-ticker!!")


def test_validate_query_rejects_too_short():
    with pytest.raises(ValidationError):
        validate_query("hi")
