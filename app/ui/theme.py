from __future__ import annotations


def application_stylesheet() -> str:
    return """
    QWidget {
        color: #e8e4dc;
        font-family: "Segoe UI";
        font-size: 10pt;
    }
    QMainWindow, QDialog { background: #090a0b; }
    QFrame#sidebar { background: #0b0d0e; border-right: 1px solid #222628; }
    QFrame#brandMark { background: #f05255; border: 1px solid #ff7774; border-radius: 7px; }
    QLabel#brandBolt { color: #fff8ef; font-size: 19pt; font-weight: 800; }
    QLabel#brandName { color: #f2eee6; font-family: Georgia; font-size: 16pt; font-weight: 700; }
    QLabel#brandSubtitle, QLabel#muted { color: #777d7d; }
    QLabel#eyebrow { color: #8a9090; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
    QLabel#title { color: #eee9df; font-family: Georgia; font-size: 15pt; font-weight: 700; }
    QLabel#providerPill { background: #111516; border: 1px solid #2a3030; border-radius: 6px; color: #9faaa5; padding: 8px 12px; }
    QLabel#providerDot { color: #79d5a6; }
    QPushButton { background: transparent; border: 1px solid #2a3031; border-radius: 6px; color: #b5b8b3; min-height: 36px; padding: 0 13px; }
    QPushButton:hover { background: #171a1b; border-color: #505555; color: #f3eee5; }
    QPushButton:pressed { background: #202324; }
    QPushButton#newChatButton { background: #191314; border: 1px solid #713438; border-left: 3px solid #ee5558; color: #e8e2d9; font-weight: 700; min-height: 48px; text-align: left; }
    QPushButton#newChatButton:hover { background: #241719; border-color: #ba4a4e; }
    QPushButton#sendButton { background: #f05255; border: 1px solid #ff7774; border-radius: 4px; color: #fff8ef; font-size: 14pt; font-weight: 700; min-width: 42px; max-width: 42px; min-height: 40px; max-height: 40px; padding: 0; }
    QPushButton#sendButton:hover { background: #ff6668; }
    QPushButton#sendButton:disabled { background: #683639; border-color: #774144; color: #cda0a0; }
    QListWidget { background: transparent; border: none; outline: none; padding: 8px 0; }
    QListWidget::item { border-radius: 5px; color: #929795; padding: 13px 11px; }
    QListWidget::item:hover { background: #161919; color: #e8e4dc; }
    QListWidget::item:selected { background: #1b1e1e; color: #f2eee6; border-left: 2px solid #ee5558; font-weight: 650; }
    QLineEdit { background: #101314; border: 1px solid #272c2d; border-radius: 5px; color: #eee9df; min-height: 38px; padding: 0 12px; }
    QLineEdit:focus { border-color: #8e4548; }
    QLineEdit::placeholder { color: #666c6c; }
    QFrame#content { background: #090a0b; }
    QFrame#header { border-bottom: 1px solid #202426; }
    QScrollArea { background: #090a0b; border: none; }
    QScrollArea#messagesScroll { background: #090a0b; border: none; border-radius: 0; }
    QScrollArea#messagesScroll QWidget#qt_scrollarea_viewport { background: #090a0b; }
    QWidget#messageCanvas { background: #090a0b; }
    QScrollBar:vertical { background: transparent; width: 8px; margin: 6px 0; }
    QScrollBar::handle:vertical { background: #343a3a; border-radius: 4px; min-height: 30px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QFrame#composerShell { background: #111415; border: 1px solid #343a3b; border-radius: 6px; }
    QFrame#composerShell:focus-within { border: 1px solid #e04e52; }
    QPlainTextEdit#composer { background: transparent; border: none; color: #eee9df; font-family: Georgia; font-size: 12pt; padding: 8px 8px; selection-background-color: #6b3034; }
    QToolButton { background: transparent; border: none; color: #777d7d; padding: 5px 8px; }
    QToolButton:hover { color: #f05255; }
    QFrame#messageBubbleUser { background: #211517; border: 1px solid #74383b; border-radius: 6px; }
    QFrame#messageBubbleAssistant { background: #111415; border: 1px solid #2b3031; border-radius: 6px; }
    QLabel#messageRole { color: #f05255; font-size: 8pt; font-weight: 800; letter-spacing: 1px; }
    QLabel#messageText { color: #e5e2dc; font-size: 10pt; }
    QFrame#messageBubbleUser QLabel#messageRole, QFrame#messageBubbleUser QLabel#messageText { color: #f5e9e4; }
    QFrame#messageAvatar { background: #f05255; border: 1px solid #ff7774; border-radius: 4px; }
    QLabel#avatarText { color: #fff8ef; font-weight: 800; }
    QFrame#emptyState { background: transparent; }
    QFrame#heroCard { background: transparent; border: none; }
    QFrame#emptyOrb { background: #f05255; border: 1px solid #ff7774; border-radius: 5px; }
    QLabel#emptyOrbText { color: #fff8ef; font-size: 20pt; font-weight: 800; }
    QLabel#emptyTitle { color: #eee9df; font-family: Georgia; font-size: 30pt; font-weight: 700; }
    QLabel#emptySubtitle { color: #b1b4ae; font-size: 11pt; }
    QFrame#suggestion { background: transparent; border: none; border-top: 1px solid #303536; border-radius: 0; }
    QFrame#suggestion:hover { background: #111415; border-top-color: #8e4548; }
    QLabel#suggestionIndex { color: #8d4a4d; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
    QLabel#suggestionText { color: #d8d3ca; font-family: Georgia; font-size: 10pt; }
    QLabel#suggestionArrow { color: #777d7d; font-size: 14pt; }
    QFrame#engineCard { background: #101413; border: 1px solid #28302c; border-radius: 5px; }
    QLabel#engineTitle { color: #d9ddd5; font-weight: 700; }
    QLabel#engineMeta { color: #777d7d; font-size: 8pt; }
    QLabel#onlineDot { color: #79d5a6; font-size: 13pt; }
    QLabel#footerNote { color: #727877; font-size: 8pt; }
    QLabel#settingsStatus { color: #f05255; font-weight: 700; }
    QLabel#dialogTitle { color: #eee9df; font-family: Georgia; font-size: 16pt; font-weight: 700; }
    QComboBox, QSpinBox { background: #101314; border: 1px solid #2d3334; border-radius: 5px; color: #eee9df; min-height: 34px; padding: 0 9px; }
    QComboBox QAbstractItemView { background: #151819; color: #eee9df; selection-background-color: #6c3034; }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #e04e52; }
    QCheckBox { color: #c7c9c3; spacing: 8px; }
    QMenu { background: #151819; border: 1px solid #343a3b; color: #e8e4dc; padding: 5px; }
    QMenu::item { padding: 8px 24px; border-radius: 3px; }
    QMenu::item:selected { background: #6c3034; }
    QMessageBox, QInputDialog { background: #111415; }
    """
