"""Factory that returns the configured LLM client (OpenAI or Gemini)."""
from typing import Union
from llm.openai_client import OpenAIClient
from llm.gemini_client import GeminiClient
from utils.exceptions import ConfigError
from config.settings import settings

LLMClient = Union[OpenAIClient, GeminiClient]

_client_cache: dict = {}


def get_llm_client(provider: str = None) -> LLMClient:  # type: ignore[assignment]
    """Return a cached LLM client instance for the given (or configured) provider."""
    provider = (provider or settings.llm_provider).lower()

    if provider in _client_cache:
        return _client_cache[provider]

    if provider == "openai":
        client: LLMClient = OpenAIClient()
    elif provider == "gemini":
        client = GeminiClient()
    else:
        raise ConfigError(f"Unsupported LLM_PROVIDER '{provider}'. Use 'openai' or 'gemini'.")

    _client_cache[provider] = client
    return client
