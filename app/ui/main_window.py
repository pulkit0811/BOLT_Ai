from __future__ import annotations

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.ai.base_provider import ProviderError
from app.core.application import BoltApplication
from app.core.models import Conversation, Message
from app.ui.chat_widgets import MessageBubble, SuggestionCard
from app.ui.message_composer import MessageComposer
from app.ui.settings_dialog import SettingsDialog
from app.ui.theme import application_stylesheet
from app.workers.ai_worker import AIWorker


class MainWindow(QMainWindow):
    def __init__(self, application: BoltApplication) -> None:
        super().__init__()
        self.application = application
        self._threads: list[QThread] = []
        self._workers: list[AIWorker] = []
        self._busy = False
        self._pending_response = False

        self.setWindowTitle("Bolt AI")
        self.setMinimumSize(1020, 680)
        self.resize(1280, 820)
        self.setStyleSheet(application_stylesheet())
        self._build_ui()
        self._refresh_provider_display()
        self._refresh_conversation_list()
        self._render_conversation()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_sidebar())
        root_layout.addWidget(self._build_content(), 1)
        self.setCentralWidget(root)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(292)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 24, 22, 20)
        layout.setSpacing(13)

        brand_row = QHBoxLayout()
        mark = QFrame()
        mark.setObjectName("brandMark")
        mark.setFixedSize(42, 42)
        mark_layout = QVBoxLayout(mark)
        mark_layout.setContentsMargins(0, 0, 0, 0)
        bolt = QLabel("B")
        bolt.setObjectName("brandBolt")
        bolt.setAlignment(Qt.AlignCenter)
        mark_layout.addWidget(bolt)
        brand_row.addWidget(mark)
        brand_text = QVBoxLayout()
        name = QLabel("BOLT AI")
        name.setObjectName("brandName")
        subtitle = QLabel("Personal intelligence")
        subtitle.setObjectName("brandSubtitle")
        brand_text.addWidget(name)
        brand_text.addWidget(subtitle)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        self.new_chat_button = QPushButton("+   New chat")
        self.new_chat_button.setObjectName("newChatButton")
        self.new_chat_button.clicked.connect(self._new_chat)
        layout.addWidget(self.new_chat_button)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search conversations")
        self.search_box.textChanged.connect(self._refresh_conversation_list)
        layout.addWidget(self.search_box)

        history_label = QLabel("RECENT CONVERSATIONS")
        history_label.setObjectName("muted")
        history_label.setStyleSheet("font-size: 8pt; font-weight: 750; letter-spacing: 1px;")
        layout.addWidget(history_label)

        self.conversation_list = QListWidget()
        self.conversation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.conversation_list.customContextMenuRequested.connect(self._show_conversation_menu)
        self.conversation_list.currentRowChanged.connect(self._select_conversation)
        layout.addWidget(self.conversation_list, 1)

        status = QFrame()
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(4, 10, 4, 3)
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #9f8acb; font-size: 11pt;")
        status_text = QLabel("Voice listener off")
        status_text.setObjectName("muted")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        layout.addWidget(status)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self._open_settings)
        layout.addWidget(self.settings_button)
        return sidebar

    def _build_content(self) -> QFrame:
        content = QFrame()
        content.setObjectName("content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 0, 34, 26)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 22, 0, 18)
        header_text = QVBoxLayout()
        eyebrow = QLabel("BOLT AI  /  PERSONAL WORKSPACE")
        eyebrow.setObjectName("eyebrow")
        self.title_label = QLabel("New conversation")
        self.title_label.setObjectName("title")
        header_text.addWidget(eyebrow)
        header_text.addWidget(self.title_label)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        self.provider_pill = QLabel()
        self.provider_pill.setObjectName("providerPill")
        header_layout.addWidget(self.provider_pill)
        layout.addWidget(header)

        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.messages_scroll, 1)

        composer_shell = QFrame()
        composer_shell.setObjectName("composerShell")
        composer_layout = QVBoxLayout(composer_shell)
        composer_layout.setContentsMargins(14, 10, 14, 10)
        composer_layout.setSpacing(4)
        self.composer = MessageComposer()
        self.composer.send_requested.connect(self._send_message)
        composer_layout.addWidget(self.composer)
        controls = QHBoxLayout()
        self.composer_hint = QLabel()
        self.composer_hint.setObjectName("muted")
        self.composer_hint.setStyleSheet("font-size: 8pt;")
        controls.addWidget(self.composer_hint)
        controls.addStretch()
        mic = QToolButton()
        mic.setText("Mic")
        mic.setToolTip("Voice input will be added in Stage 3")
        mic.setEnabled(False)
        controls.addWidget(mic)
        self.send_button = QPushButton("Send   >")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self._send_message)
        controls.addWidget(self.send_button)
        composer_layout.addLayout(controls)
        layout.addWidget(composer_shell)
        return content

    def _refresh_provider_display(self) -> None:
        config = self.application.config
        if config.provider == "mock":
            provider = "Local mock"
            hint = "Local demo mode - conversations are saved on this computer"
        elif config.provider == "ollama":
            cloud = config.endpoint.lower().startswith("https://")
            provider = "Ollama Cloud" if cloud else "Ollama local"
            hint = "Ollama Cloud - messages use your Ollama account" if cloud else "Local Ollama - messages stay on this computer"
        else:
            provider = "OpenAI"
            hint = "OpenAI API - messages are sent only when you press Send"
        self.provider_pill.setText(f"●  {provider}  /  {config.model}")
        self.composer_hint.setText(hint)

    def _refresh_conversation_list(self) -> None:
        current_id = self.application.active_conversation.id
        query = self.search_box.text().strip().lower() if hasattr(self, "search_box") else ""
        self.conversation_list.blockSignals(True)
        self.conversation_list.clear()
        selected_row = 0
        visible_row = 0
        for conversation in self.application.conversations:
            if query and query not in conversation.title.lower():
                continue
            item = QListWidgetItem(conversation.title)
            item.setData(Qt.UserRole, conversation.id)
            self.conversation_list.addItem(item)
            if conversation.id == current_id:
                selected_row = visible_row
            visible_row += 1
        if self.conversation_list.count():
            self.conversation_list.setCurrentRow(selected_row)
        self.conversation_list.blockSignals(False)

    def _select_conversation(self, row: int) -> None:
        item = self.conversation_list.item(row)
        if item is None:
            return
        conversation_id = item.data(Qt.UserRole)
        conversation = next(
            (item for item in self.application.conversations if item.id == conversation_id), None
        )
        if conversation is not None:
            self.application.active_conversation = conversation
            self._render_conversation()

    def _new_chat(self) -> None:
        if self._busy:
            return
        self.application.create_conversation()
        self._refresh_conversation_list()
        self._render_conversation()
        self.composer.setFocus()

    def _show_conversation_menu(self, position) -> None:
        item = self.conversation_list.itemAt(position)
        if item is None:
            return
        conversation = next(
            (entry for entry in self.application.conversations if entry.id == item.data(Qt.UserRole)),
            None,
        )
        if conversation is None:
            return
        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.conversation_list.mapToGlobal(position))
        if action == rename_action:
            self._rename_conversation(conversation)
        elif action == delete_action:
            self._delete_conversation(conversation)

    def _rename_conversation(self, conversation: Conversation) -> None:
        title, accepted = QInputDialog.getText(self, "Rename conversation", "Conversation name", text=conversation.title)
        if accepted and title.strip():
            conversation.title = title.strip()
            self.application.save_conversation(conversation)
            self._refresh_conversation_list()
            self._render_conversation()

    def _delete_conversation(self, conversation: Conversation) -> None:
        answer = QMessageBox.question(
            self,
            "Delete conversation",
            f"Delete {conversation.title}? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.application.delete_conversation(conversation)
            self._refresh_conversation_list()
            self._render_conversation()

    def _render_conversation(self) -> None:
        conversation = self.application.active_conversation
        self.title_label.setText(conversation.title)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 30, 8, 30)
        container_layout.setSpacing(16)
        if not conversation.messages:
            container_layout.addWidget(self._empty_state())
        else:
            for message in conversation.messages:
                row = QHBoxLayout()
                row.setContentsMargins(0, 0, 0, 0)
                bubble = MessageBubble(message)
                bubble.copy_requested.connect(self._copy_text)
                if message.role == "user":
                    row.addStretch(1)
                    row.addWidget(bubble)
                else:
                    row.addWidget(bubble)
                    row.addStretch(1)
                container_layout.addLayout(row)
        container_layout.addStretch()
        self.messages_scroll.setWidget(container)
        self._scroll_to_bottom()

    def _empty_state(self) -> QWidget:
        state = QFrame()
        state.setObjectName("heroCard")
        layout = QVBoxLayout(state)
        layout.setContentsMargins(40, 48, 40, 48)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(11)
        orb = QLabel("B")
        orb.setObjectName("emptyOrb")
        orb.setAlignment(Qt.AlignCenter)
        orb.setFixedSize(76, 76)
        layout.addWidget(orb, alignment=Qt.AlignCenter)
        eyebrow = QLabel("INTELLIGENCE, BEAUTIFULLY SIMPLE")
        eyebrow.setObjectName("eyebrow")
        layout.addWidget(eyebrow, alignment=Qt.AlignCenter)
        title = QLabel("Think bigger. Build faster.")
        title.setObjectName("emptyTitle")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        subtitle = QLabel("A focused AI workspace for ideas, decisions, and momentum.")
        subtitle.setObjectName("emptySubtitle")
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        suggestions = QHBoxLayout()
        suggestions.setSpacing(12)
        prompts = ("Explain a complex idea", "Plan my next project", "Improve my Python")
        for prompt in prompts:
            card = SuggestionCard(prompt)
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda _event, value=prompt: self._use_suggestion(value)
            suggestions.addWidget(card)
        layout.addLayout(suggestions)
        return state

    def _use_suggestion(self, prompt: str) -> None:
        self.composer.setPlainText(prompt)
        self.composer.setFocus()

    def _send_message(self) -> None:
        if self._busy:
            return
        text = self.composer.toPlainText().strip()
        if not text:
            return
        conversation = self.application.active_conversation
        if not conversation.messages:
            conversation.title = text[:42] + ("..." if len(text) > 42 else "")
        conversation.messages.append(Message(role="user", content=text))
        self.composer.clear()
        self.application.save_conversation(conversation)
        self._refresh_conversation_list()
        self._render_conversation()
        self._set_busy(True)

        thread = QThread(self)
        worker = AIWorker(
            self.application.provider,
            conversation.messages,
            streaming=self.application.config.streaming,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.delta.connect(self._handle_ai_delta)
        worker.succeeded.connect(self._handle_ai_response)
        worker.failed.connect(self._handle_ai_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._remove_thread(thread, worker))
        self._threads.append(thread)
        self._workers.append(worker)
        thread.start()

    def _handle_ai_delta(self, delta: str) -> None:
        conversation = self.application.active_conversation
        if not self._pending_response:
            conversation.messages.append(Message(role="assistant", content=""))
            self._pending_response = True
        conversation.messages[-1].content += delta
        self._render_conversation()

    def _handle_ai_response(self, response: str) -> None:
        conversation = self.application.active_conversation
        if self._pending_response and conversation.messages and conversation.messages[-1].role == "assistant":
            conversation.messages[-1].content = response
        else:
            conversation.messages.append(Message(role="assistant", content=response))
        self._pending_response = False
        self.application.save_conversation(conversation)
        self._render_conversation()

    def _handle_ai_error(self, error: str) -> None:
        conversation = self.application.active_conversation
        if self._pending_response and conversation.messages and not conversation.messages[-1].content:
            conversation.messages.pop()
            self._pending_response = False
            self._render_conversation()
        QMessageBox.warning(self, "Bolt AI could not respond", error)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.application.config, self)
        if dialog.exec() != dialog.Accepted:
            return
        try:
            self.application.save_config(dialog.config)
        except ProviderError as exc:
            QMessageBox.warning(self, "Settings not applied", str(exc))
            return
        self._refresh_provider_display()

    def _copy_text(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.composer.setEnabled(not busy)
        self.send_button.setEnabled(not busy)
        self.new_chat_button.setEnabled(not busy)
        self.conversation_list.setEnabled(not busy)
        self.settings_button.setEnabled(not busy)
        self.send_button.setText("Thinking..." if busy else "Send   >")

    def _remove_thread(self, thread: QThread, worker: AIWorker) -> None:
        if thread in self._threads:
            self._threads.remove(thread)
        if worker in self._workers:
            self._workers.remove(worker)
        self._set_busy(False)

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event: QCloseEvent) -> None:
        for thread in self._threads:
            thread.quit()
            thread.wait(1500)
        self.application.save_conversation()
        self.application.close()
        event.accept()
