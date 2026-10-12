from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPlainTextEdit


class MessageComposer(QPlainTextEdit):
    send_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("composer")
        self.setPlaceholderText("Message Bolt AI… (Enter to send, Shift+Enter for a new line)")
        self.setFixedHeight(76)
        self.setTabChangesFocus(False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        is_enter = event.key() in (Qt.Key_Return, Qt.Key_Enter)
        is_shift = bool(event.modifiers() & Qt.ShiftModifier)
        if is_enter and not is_shift:
            event.accept()
            self.send_requested.emit()
            return
        super().keyPressEvent(event)

