"""Custom exception hierarchy for the agent."""


class AgentBaseException(Exception):
    """Base class for all custom exceptions in this project."""


class ToolExecutionError(AgentBaseException):
    """Raised when a tool fails to execute successfully."""

    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"[{tool_name}] {message}")


class RAGError(AgentBaseException):
    """Raised when retrieval-augmented generation fails."""


class LLMError(AgentBaseException):
    """Raised when an LLM call fails after retries."""


class ConfigError(AgentBaseException):
    """Raised when required configuration (e.g. API keys) is missing."""


class ValidationError(AgentBaseException):
    """Raised when input validation fails."""
