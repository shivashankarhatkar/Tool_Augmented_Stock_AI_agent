"""Abstract base class that every tool must implement."""
from abc import ABC, abstractmethod
from typing import Any, Dict
from schemas.tool_result import ToolResult
from utils.logger import get_logger

logger = get_logger(__name__)


# class BaseTool(ABC):
#     name: str = "base_tool"
#     description: str = "Base tool. Override in subclasses."

#     @abstractmethod
#     def _run(self, **kwargs: Any) -> Any:
#         """Implement the actual tool logic. Raise on failure."""
#         raise NotImplementedError

#     def run(self, **kwargs: Any) -> ToolResult:
#         """Public entrypoint: wraps `_run` with consistent error handling."""
#         try:
#             data = self._run(**kwargs)
#             return ToolResult(tool_name=self.name, success=True, data=data)
#         except Exception as exc:  # noqa: BLE001
#             logger.error(f"Tool '{self.name}' failed: {exc}")
#             return ToolResult(tool_name=self.name, success=False, error=str(exc))

#     def schema(self) -> Dict[str, Any]:
#         """Return an OpenAI/Gemini-style function-calling schema. Override for richer schemas."""
#         return {
#             "name": self.name,
#             "description": self.description,
#             "parameters": {"type": "object", "properties": {}, "required": []},
#         }

class BaseTool(ABC):
    """
    Abstract base class for all tools.

    Provides a common interface for executing tools, handling errors,
    and exposing tool metadata for LLM function calling.
    """

    # Unique identifier of the tool.
    name: str = "base_tool"

    # Short description of the tool's functionality.
    description: str = "Base tool. Override in subclasses."

    @abstractmethod
    def _run(self, **kwargs: Any) -> Any:
        """
        Implement the core business logic of the tool.

        This method must be implemented by every concrete tool.
        It should return the tool's output or raise an exception on failure.
        """
        raise NotImplementedError

    def run(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool with standardized error handling.

        Args:
            **kwargs: Input parameters required by the tool.

        Returns:
            A ToolResult object indicating whether the execution
            succeeded or failed.
        """
        try:
            # Execute the tool's core logic.
            data = self._run(**kwargs)

            return ToolResult(
                tool_name=self.name,
                success=True,
                data=data,
            )

        except Exception as exc:  # noqa: BLE001
            # Log the error and return a standardized failure response.
            logger.error(f"Tool '{self.name}' failed: {exc}")

            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(exc),
            )

    def schema(self) -> Dict[str, Any]:
        """
        Return the tool's function-calling schema.

        Subclasses can override this method to define
        richer input parameters for LLM tool calling.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
