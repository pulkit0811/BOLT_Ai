from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence

from app.core.models import Message


class ProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    name = "Unknown provider"
    model = "Unknown model"

    @abstractmethod
    def complete(self, messages: Sequence[Message]) -> str:
        raise NotImplementedError

    def stream(self, messages: Sequence[Message]) -> Iterable[str]:
        yield self.complete(messages)

