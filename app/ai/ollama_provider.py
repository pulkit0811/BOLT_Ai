from __future__ import annotations

from collections.abc import Iterable, Sequence

from app.ai.base_provider import AIProvider, ProviderError
from app.core.models import Message


class OllamaProvider(AIProvider):
    name = "Ollama"

    def __init__(
        self,
        model: str,
        endpoint: str = "http://localhost:11434/v1",
        api_key: str = "",
        timeout: float = 120.0,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderError("Install the openai package to use Ollama.") from exc
        self.model = model
        self.client = OpenAI(
            base_url=endpoint or "http://localhost:11434/v1",
            api_key=api_key or "ollama",
            timeout=timeout,
        )

    def complete(self, messages: Sequence[Message]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=_to_messages(messages),
                stream=False,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise ProviderError(_safe_error(exc)) from exc

    def stream(self, messages: Sequence[Message]) -> Iterable[str]:
        try:
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=_to_messages(messages),
                stream=True,
            )
            for chunk in response_stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as exc:
            raise ProviderError(_safe_error(exc)) from exc


def _to_messages(messages: Sequence[Message]) -> list[dict[str, str]]:
    return [{"role": message.role, "content": message.content} for message in messages]


def _safe_error(error: Exception) -> str:
    text = str(error).strip()
    if not text:
        return "The Ollama provider returned an unknown error."
    if len(text) > 280:
        return f"Ollama request failed: {text[:277]}..."
    return f"Ollama request failed: {text}"
