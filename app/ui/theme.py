from __future__ import annotations


def application_stylesheet() -> str:
    return """
    QWidget {
        color: #29233d;
        font-family: "Segoe UI";
        font-size: 10pt;
    }
    QMainWindow, QDialog { background: #f8f7fc; }
    QFrame#sidebar { background: #ffffff; border-right: 1px solid #e8e3f2; }
    QFrame#brandMark { background: #f0eafd; border: 1px solid #d8c7ff; border-radius: 12px; }
    QLabel#brandBolt { color: #7045d6; font-size: 17pt; font-weight: 800; }
    QLabel#brandName { color: #251d3a; font-size: 15pt; font-weight: 750; letter-spacing: 1px; }
    QLabel#brandSubtitle, QLabel#muted { color: #887e9f; }
    QPushButton { background: #ffffff; border: 1px solid #e4def0; border-radius: 9px; color: #4d4363; min-height: 36px; padding: 0 13px; }
    QPushButton:hover { background: #f7f3ff; border-color: #c9b5f3; color: #5e35ba; }
    QPushButton:pressed { background: #eee7fc; }
    QPushButton#newChatButton { background: #7045d6; border: none; color: white; font-weight: 700; min-height: 42px; }
    QPushButton#newChatButton:hover { background: #5f36c5; }
    QPushButton#sendButton { background: #7045d6; border: none; border-radius: 9px; color: white; font-weight: 700; min-width: 86px; min-height: 38px; }
    QPushButton#sendButton:hover { background: #5f36c5; }
    QPushButton#sendButton:disabled { background: #cfc6e7; color: #ffffff; }
    QListWidget { background: transparent; border: none; outline: none; padding: 5px 0; }
    QListWidget::item { border-radius: 9px; color: #716783; padding: 12px 11px; }
    QListWidget::item:hover { background: #f7f3ff; color: #4e2d9d; }
    QListWidget::item:selected { background: #eee7fc; color: #5130a8; font-weight: 650; }
    QFrame#content { background: #f8f7fc; }
    QFrame#header { border-bottom: 1px solid #e9e5f1; }
    QLabel#eyebrow { color: #8869cf; font-size: 8pt; font-weight: 750; letter-spacing: 1px; }
    QLabel#title { color: #27203b; font-size: 14pt; font-weight: 700; }
    QLabel#providerPill { background: #f1ebff; border: 1px solid #d9c9fa; border-radius: 13px; color: #633bbd; padding: 6px 11px; }
    QLabel#providerDot { color: #7045d6; }
    QScrollArea { background: transparent; border: none; }
    QScrollBar:vertical { background: transparent; width: 9px; margin: 6px 0; }
    QScrollBar::handle:vertical { background: #d5cbe8; border-radius: 4px; min-height: 30px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QFrame#composerShell { background: #ffffff; border: 1px solid #ded5ed; border-radius: 15px; }
    QFrame#composerShell:focus-within { border: 1px solid #9a78e4; }
    QPlainTextEdit#composer { background: transparent; border: none; color: #2c2540; padding: 10px 6px; selection-background-color: #dcd0f8; }
    QToolButton { background: transparent; border: none; color: #9a8eaf; padding: 5px 8px; }
    QToolButton:hover { color: #7045d6; }
    QFrame#messageBubbleUser { background: #7045d6; border: 1px solid #7045d6; border-radius: 15px; }
    QFrame#messageBubbleAssistant { background: #ffffff; border: 1px solid #e4deef; border-radius: 15px; }
    QLabel#messageRole { color: #8060c8; font-weight: 750; }
    QLabel#messageText { color: #373047; }
    QFrame#messageBubbleUser QLabel#messageRole, QFrame#messageBubbleUser QLabel#messageText { color: #ffffff; }
    QFrame#emptyState { background: transparent; }
    QFrame#heroCard { background: #ffffff; border: 1px solid #e7e0f2; border-radius: 22px; }
    QLabel#emptyOrb { background: #f0eafd; border: 1px solid #cdb9f6; border-radius: 38px; color: #7045d6; font-size: 27pt; font-weight: 800; }
    QLabel#emptyTitle { color: #28203f; font-size: 24pt; font-weight: 750; }
    QLabel#emptySubtitle { color: #857b99; font-size: 10pt; }
    QFrame#suggestion { background: #fbfaff; border: 1px solid #e7def5; border-radius: 12px; }
    QFrame#suggestion:hover { background: #f4efff; border-color: #bda6ed; }
    QLabel#settingsStatus { color: #7045d6; font-weight: 700; }
    QLabel#dialogTitle { color: #29213e; font-size: 16pt; font-weight: 750; }
    QLineEdit, QComboBox, QSpinBox { background: #ffffff; border: 1px solid #ddd4eb; border-radius: 8px; color: #332a48; min-height: 34px; padding: 0 9px; }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #9a78e4; }
    QCheckBox { color: #554b68; spacing: 8px; }
    """
