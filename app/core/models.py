from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(slots=True)
class Message:
    role: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class Conversation:
    title: str = "New conversation"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    messages: list[Message] = field(default_factory=list)

    @property
    def updated_at(self) -> datetime:
        if self.messages:
            return self.messages[-1].created_at
        return self.created_at

