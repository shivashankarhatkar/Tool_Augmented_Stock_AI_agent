"""Thin wrapper around Google's Generative AI SDK (Gemini)."""
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from utils.exceptions import LLMError, ConfigError
from utils.helpers import retry
from config.settings import settings


class GeminiClient:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ConfigError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self._model = genai.GenerativeModel(self.model_name)

    @staticmethod
    def _to_gemini_messages(messages: List[Dict[str, str]]) -> str:
        """Gemini's basic generate_content takes plain text; flatten chat history."""
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            prefix = "System" if role == "system" else ("Assistant" if role == "assistant" else "User")
            parts.append(f"{prefix}: {content}")
        return "\n\n".join(parts)

    @retry(max_attempts=3, delay_seconds=1.5)
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        # Note: function-calling schema for Gemini differs from OpenAI; for this template
        # we rely on the router/planner prompting the model to emit structured JSON instead,
        # which response_parser.py then parses uniformly across providers.
        try:
            prompt = self._to_gemini_messages(messages)
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            text = response.text if hasattr(response, "text") else ""
            return {"content": text, "tool_calls": [], "raw": response}
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Gemini chat call failed: {exc}") from exc
