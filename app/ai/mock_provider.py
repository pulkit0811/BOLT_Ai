from __future__ import annotations

from collections.abc import Sequence

from app.ai.base_provider import AIProvider
from app.core.models import Message


class MockProvider(AIProvider):
    name = "Bolt demo engine"
    model = "mock-v1"

    def complete(self, messages: Sequence[Message]) -> str:
        latest_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "your message",
        )
        return (
            "This is a local demo response from Bolt AI.\n\n"
            f"You asked: {latest_user_message}\n\n"
            "This local provider is ready for development. Configure AI_PROVIDER=openai "
            "and AI_API_KEY to connect a real model."
        )
