from __future__ import annotations

from collections.abc import Iterable, Sequence

from app.ai.base_provider import AIProvider, ProviderError
from app.core.models import Message


class OpenAIProvider(AIProvider):
    name = "OpenAI"

    def __init__(self, api_key: str, model: str, endpoint: str = "", timeout: float = 60.0) -> None:
        if not api_key:
            raise ProviderError("AI_API_KEY is required when the OpenAI provider is selected.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderError("Install the openai package to use the OpenAI provider.") from exc
        self.model = model
        options = {"api_key": api_key, "timeout": timeout}
        if endpoint:
            options["base_url"] = endpoint
        self.client = OpenAI(**options)

    def complete(self, messages: Sequence[Message]) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=_to_input(messages),
                stream=False,
                store=False,
            )
            return response.output_text
        except Exception as exc:
            raise ProviderError(_safe_error(exc)) from exc

    def stream(self, messages: Sequence[Message]) -> Iterable[str]:
        try:
            response_stream = self.client.responses.create(
                model=self.model,
                input=_to_input(messages),
                stream=True,
                store=False,
            )
            for event in response_stream:
                if getattr(event, "type", "") == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    if delta:
                        yield delta
        except Exception as exc:
            raise ProviderError(_safe_error(exc)) from exc


def _to_input(messages: Sequence[Message]) -> list[dict[str, str]]:
    return [{"role": message.role, "content": message.content} for message in messages]


def _safe_error(error: Exception) -> str:
    text = str(error).strip()
    if not text:
        return "The OpenAI provider returned an unknown error."
    if len(text) > 280:
        return f"OpenAI request failed: {text[:277]}..."
    return f"OpenAI request failed: {text}"
