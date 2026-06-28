"""Calculator tool: safe arithmetic evaluation for financial calculations (CAGR, P/E, ratios, etc.)."""
from typing import Any, Dict
import numexpr
from tools.base_tool import BaseTool
from utils.validators import is_safe_math_expression
from utils.exceptions import ToolExecutionError, ValidationError


class CalculatorTool(BaseTool):
    name = "calculator"
    description = (
        "Evaluate a numeric arithmetic expression, e.g. for computing ratios, growth rates, "
        "or compound returns. Only numbers and + - * / ( ) ^ % are supported."
    )

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression, e.g. '(150-100)/100*100'",
                    }
                },
                "required": ["expression"],
            },
        }

    def _run(self, expression: str) -> Dict[str, Any]:
        if not is_safe_math_expression(expression):
            raise ValidationError(f"Expression contains disallowed characters: {expression}")
        try:
            normalized = expression.replace("^", "**")
            result = numexpr.evaluate(normalized).item()
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(self.name, f"Could not evaluate expression: {exc}") from exc
        return {"expression": expression, "result": result}
