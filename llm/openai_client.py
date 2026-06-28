"""Thin wrapper around the OpenAI Python SDK for chat completions + function calling."""
from typing import Any, Dict, List, Optional
from openai import OpenAI
from utils.exceptions import LLMError, ConfigError
from utils.helpers import retry
from config.settings import settings


class OpenAIClient:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ConfigError("OPENAI_API_KEY is not configured.")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @retry(max_attempts=3, delay_seconds=1.5)
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if tools:
                kwargs["tools"] = [{"type": "function", "function": t} for t in tools]
                kwargs["tool_choice"] = "auto"

            response = self._client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            tool_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    tool_calls.append(
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    )
            return {
                "content": choice.message.content or "",
                "tool_calls": tool_calls,
                "raw": response,
            }
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"OpenAI chat call failed: {exc}") from exc
