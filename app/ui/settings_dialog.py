from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from app.core.config import AppConfig


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Bolt AI settings")
        self.setMinimumWidth(470)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Workspace settings")
        title.setObjectName("dialogTitle")
        subtitle = QLabel("Tune the model connection without changing your local chat history.")
        subtitle.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)

        self.provider = QComboBox()
        self.provider.addItem("Local mock", "mock")
        self.provider.addItem("OpenAI API", "openai")
        self.provider.addItem("Ollama local or cloud", "ollama")
        provider_index = {"mock": 0, "openai": 1, "ollama": 2}.get(self.config.provider, 0)
        self.provider.setCurrentIndex(provider_index)
        self.provider.currentIndexChanged.connect(self._provider_changed)
        form.addRow("Provider", self.provider)

        self.model = QLineEdit(self.config.model)
        self.model.setPlaceholderText("Model identifier")
        form.addRow("Model", self.model)

        self.endpoint = QLineEdit(self.config.endpoint)
        self.endpoint.setPlaceholderText("Optional compatible API base URL")
        form.addRow("API endpoint", self.endpoint)

        self.timeout = QSpinBox()
        self.timeout.setRange(5, 300)
        self.timeout.setSuffix(" seconds")
        self.timeout.setValue(int(self.config.timeout))
        form.addRow("Request timeout", self.timeout)

        self.streaming = QCheckBox("Stream responses as they are generated")
        self.streaming.setChecked(self.config.streaming)
        form.addRow("Response mode", self.streaming)
        layout.addLayout(form)

        key_status = QLabel(
            "API key: configured" if self.config.api_key else "API key: not configured"
        )
        key_status.setObjectName("settingsStatus")
        key_help = QLabel("Set AI_API_KEY for Ollama Cloud or OpenAI. Local Ollama uses a placeholder key. Keys are never stored in Bolt AI's database.")
        key_help.setObjectName("muted")
        key_help.setWordWrap(True)
        layout.addWidget(key_status)
        layout.addWidget(key_help)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _provider_changed(self, index: int) -> None:
        if self.provider.itemData(index) == "ollama" and not self.endpoint.text().strip():
            self.endpoint.setText("http://localhost:11434/v1")
        if self.provider.itemData(index) == "ollama" and self.model.text().strip() in {"", "gpt-5.5", "deepseek-v4.1-flash:cloud"}:
            self.model.setText("qwen3.5")

    def _save(self) -> None:
        model = self.model.text().strip()
        if not model:
            QMessageBox.warning(self, "Model required", "Enter a model identifier before saving.")
            return
        self.config = AppConfig(
            provider=self.provider.currentData(),
            model=model,
            endpoint=self.endpoint.text().strip(),
            timeout=float(self.timeout.value()),
            streaming=self.streaming.isChecked(),
            api_key=self.config.api_key,
        )
        self.accept()
