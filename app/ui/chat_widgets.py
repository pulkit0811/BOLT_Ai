from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout

from app.core.models import Message


class MessageBubble(QFrame):
    copy_requested = Signal(str)

    def __init__(self, message: Message) -> None:
        super().__init__()
        bubble_name = "messageBubbleUser" if message.role == "user" else "messageBubbleAssistant"
        self.setObjectName(bubble_name)
        self.setMaximumWidth(760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 13)
        layout.setSpacing(5)

        role_row = QHBoxLayout()
        role = QLabel("YOU" if message.role == "user" else "BOLT AI")
        role.setObjectName("messageRole")
        role_row.addWidget(role)
        role_row.addStretch()
        if message.role == "assistant":
            copy = QToolButton()
            copy.setText("Copy")
            copy.setToolTip("Copy response")
            copy.clicked.connect(lambda: self.copy_requested.emit(message.content))
            role_row.addWidget(copy)
        text = QLabel(message.content)
        text.setObjectName("messageText")
        text.setWordWrap(True)
        text.setTextFormat(Qt.MarkdownText if message.role == "assistant" else Qt.PlainText)
        text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addLayout(role_row)
        layout.addWidget(text)


class SuggestionCard(QFrame):
    def __init__(self, prompt: str, index: str) -> None:
        super().__init__()
        self.setObjectName("suggestion")
        self.setProperty("prompt", prompt)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 12, 6, 12)
        layout.setSpacing(14)
        number = QLabel(index)
        number.setObjectName("suggestionIndex")
        layout.addWidget(number)
        label = QLabel(prompt)
        label.setObjectName("suggestionText")
        label.setWordWrap(True)
        layout.addWidget(label, 1)
        arrow = QLabel(">")
        arrow.setObjectName("suggestionArrow")
        layout.addWidget(arrow)

