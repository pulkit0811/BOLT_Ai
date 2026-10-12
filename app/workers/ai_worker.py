from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QObject, Signal, Slot

from app.ai.base_provider import AIProvider
from app.core.models import Message


class AIWorker(QObject):
    succeeded = Signal(str)
    delta = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        provider: AIProvider,
        messages: Sequence[Message],
        streaming: bool = True,
    ) -> None:
        super().__init__()
        self._provider = provider
        self._messages = list(messages)
        self._streaming = streaming

    @Slot()
    def run(self) -> None:
        try:
            if not self._streaming:
                self.succeeded.emit(self._provider.complete(self._messages))
                return
            chunks: list[str] = []
            for chunk in self._provider.stream(self._messages):
                chunks.append(chunk)
                self.delta.emit(chunk)
            self.succeeded.emit("".join(chunks))
        except Exception as exc:
            self.failed.emit(str(exc) or "The AI provider returned an unknown error.")
        finally:
            self.finished.emit()

