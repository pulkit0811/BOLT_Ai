from __future__ import annotations

import os
from pathlib import Path

from app.ai.base_provider import AIProvider, ProviderError
from app.ai.mock_provider import MockProvider
from app.ai.provider_factory import create_provider
from app.core.config import AppConfig
from app.core.models import Conversation
from app.storage.database import Database


class BoltApplication:
    def __init__(
        self,
        provider: AIProvider | None = None,
        database_path: str | Path | None = None,
    ) -> None:
        configured_path = database_path or os.getenv("BOLT_DATABASE_PATH") or AppConfig.default_database_path()
        self.database = Database(configured_path)
        self.config = self._load_config()
        self.voice_draft: str | None = None
        if provider is not None:
            self.provider = provider
        else:
            try:
                self.provider = create_provider(self.config)
            except ProviderError:
                self.config.provider = "mock"
                self.provider = MockProvider()
        self.conversations = self.database.load_conversations()
        if self.conversations:
            self.active_conversation = self.conversations[0]
        else:
            self.active_conversation = self.create_conversation()

    def create_conversation(self, title: str = "New conversation") -> Conversation:
        conversation = Conversation(title=title)
        self.conversations.insert(0, conversation)
        self.active_conversation = conversation
        self.database.save_conversation(conversation)
        return conversation

    def save_conversation(self, conversation: Conversation | None = None) -> None:
        self.database.save_conversation(conversation or self.active_conversation)

    def delete_conversation(self, conversation: Conversation) -> None:
        self.database.delete_conversation(conversation.id)
        self.conversations = [item for item in self.conversations if item.id != conversation.id]
        if not self.conversations:
            self.create_conversation()
        else:
            self.active_conversation = self.conversations[0]

    def save_config(self, config: AppConfig) -> None:
        provider = create_provider(config)
        self.database.save_settings(
            {
                "provider": config.provider,
                "model": config.model,
                "endpoint": config.endpoint,
                "timeout": str(config.timeout),
                "streaming": str(config.streaming).lower(),
            }
        )
        self.config = config
        self.provider = provider

    def set_voice_draft(self, content: str) -> None:
        self.voice_draft = content.strip() or None

    def clear_voice_draft(self) -> None:
        self.voice_draft = None

    def close(self) -> None:
        self.database.close()

    def _load_config(self) -> AppConfig:
        config = AppConfig.from_environment()
        stored = self.database.load_settings()
        if "provider" in stored and "AI_PROVIDER" not in os.environ:
            config.provider = stored["provider"]
        if "model" in stored and "AI_MODEL" not in os.environ:
            config.model = stored["model"]
        if "endpoint" in stored and "AI_API_ENDPOINT" not in os.environ:
            config.endpoint = stored["endpoint"]
        if "timeout" in stored and "AI_REQUEST_TIMEOUT" not in os.environ:
            try:
                config.timeout = float(stored["timeout"])
            except ValueError:
                pass
        if "streaming" in stored and "AI_STREAMING" not in os.environ:
            config.streaming = stored["streaming"] == "true"
        return config
