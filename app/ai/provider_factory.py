from __future__ import annotations

from app.ai.base_provider import AIProvider, ProviderError
from app.ai.mock_provider import MockProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.openai_provider import OpenAIProvider
from app.core.config import AppConfig


def create_provider(config: AppConfig) -> AIProvider:
    if config.provider == "mock":
        return MockProvider()
    if config.provider == "openai":
        return OpenAIProvider(
            api_key=config.api_key,
            model=config.model,
            endpoint=config.endpoint,
            timeout=config.timeout,
        )
    if config.provider == "ollama":
        return OllamaProvider(
            model=config.model,
            endpoint=config.endpoint,
            api_key=config.api_key,
            timeout=config.timeout,
        )
    raise ProviderError(f"Unsupported provider: {config.provider}")
