from __future__ import annotations

import json
import os
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from PySide6.QtCore import QEvent, QObject, QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

from app.core.application import BoltApplication
from app.voice_engine import VoiceEngine
from app.web_server import create_server


class GlowOverlay(QWidget):
    dismissed = Signal()

    def __init__(self) -> None:
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(16)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)

    def show_listening(self) -> None:
        self._position()
        self._timer.start(40)
        self.show()
        self.raise_()

    def show_message(self, message: str) -> None:
        del message
        self._position()
        self._timer.start(40)
        self.show()
        self.raise_()

    def hide_overlay(self) -> None:
        self._timer.stop()
        self.hide()
        self.dismissed.emit()

    def paintEvent(self, event: QEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pulse = (self._phase % 100) / 100
        glow = int(78 + 70 * abs(0.5 - pulse) * 2)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor("#ff4d6d"))
        gradient.setColorAt(0.5, QColor("#ffb36b"))
        gradient.setColorAt(1.0, QColor("#ff4d6d"))
        for width, alpha in ((16, glow // 3), (8, glow // 2)):
            painter.setPen(QPen(QColor(255, 78, 104, alpha), width))
            painter.drawLine(0, 8, self.width(), 8)
        painter.setPen(QPen(QBrush(gradient), 2))
        painter.drawLine(0, 8, self.width(), 8)

    def _animate(self) -> None:
        self._phase = (self._phase + 1) % 100
        self.update()

    def _position(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.setFixedWidth(area.width())
        self.move(QPoint(area.left(), area.bottom() - self.height()))


class QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class DesktopLauncher(QObject):
    voice_result = Signal(bool, str)

    def __init__(self, qt_app: QApplication) -> None:
        super().__init__()
        self.qt_app = qt_app
        self.project_root = Path(__file__).resolve().parent.parent
        self.frontend_root = self.project_root / "frontend"
        self.application = BoltApplication()
        self.api_server = create_server(self.application)
        self.api_thread = threading.Thread(target=self.api_server.serve_forever, daemon=True)
        self.frontend_server: ThreadingHTTPServer | None = None
        self.frontend_thread: threading.Thread | None = None
        self.overlay = GlowOverlay()
        self.voice = VoiceEngine()
        self.voice.listening_changed.connect(self._voice_state)
        self.voice.transcript_ready.connect(self._send_voice_transcript)
        self.voice.status_changed.connect(self._voice_status)
        self.voice.error.connect(self._voice_error)
        self.voice_result.connect(self._voice_finished)
        self.tray = QSystemTrayIcon(self._tray_icon(), self.qt_app)
        self._build_tray_menu()
        self.qt_app.aboutToQuit.connect(self.shutdown)

    def start(self) -> None:
        self.api_thread.start()
        self._start_frontend()
        self.tray.show()
        self.voice.start()
        if os.getenv("BOLT_OPEN_BROWSER", "0") != "0":
            QTimer.singleShot(1300, self.open_workspace)

    def open_workspace(self) -> None:
        webbrowser.open("http://127.0.0.1:5173")

    def show_listening_preview(self) -> None:
        self.overlay.show_listening()
        QTimer.singleShot(2400, self.overlay.hide_overlay)

    def shutdown(self) -> None:
        self.overlay.hide_overlay()
        self.tray.hide()
        self.voice.stop()
        self.api_server.shutdown()
        self.api_server.server_close()
        if self.frontend_server is not None:
            self.frontend_server.shutdown()
            self.frontend_server.server_close()
        self.application.close()

    def _build_tray_menu(self) -> None:
        menu = QMenu()
        open_action = menu.addAction("Open Bolt")
        open_action.triggered.connect(self.open_workspace)
        preview_action = menu.addAction("Preview listening glow")
        preview_action.triggered.connect(self.show_listening_preview)
        self.voice_action = menu.addAction("Voice listening")
        self.voice_action.setCheckable(True)
        self.voice_action.setChecked(True)
        self.voice_action.toggled.connect(self._toggle_voice)
        menu.addSeparator()
        quit_action = menu.addAction("Quit Bolt")
        quit_action.triggered.connect(self.qt_app.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.setToolTip("Bolt AI")

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_workspace()

    def _toggle_voice(self, enabled: bool) -> None:
        if enabled:
            self.voice.start()
        else:
            self.voice.stop()

    def _voice_state(self, active: bool, state: str) -> None:
        if active:
            self.overlay.show_listening()
        elif state == "Sending":
            self.overlay.show_message("Sending to Bolt")
        else:
            self.overlay.hide_overlay()

    def _voice_status(self, status: str) -> None:
        self.tray.setToolTip(f"Bolt AI · {status}")

    def _voice_error(self, message: str) -> None:
        self.voice_action.setChecked(False)
        self.overlay.show_message(message[:72])
        QTimer.singleShot(4000, self.overlay.hide_overlay)

    def _send_voice_transcript(self, transcript: str) -> None:
        thread = threading.Thread(target=self._post_voice_transcript, args=(transcript,), daemon=True)
        thread.start()

    def _post_voice_transcript(self, transcript: str) -> None:
        try:
            body = json.dumps({"content": transcript}).encode("utf-8")
            request = Request(
                "http://127.0.0.1:8765/api/voice-draft",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=180) as response:
                response.read()
            self.voice_result.emit(True, transcript)
        except (OSError, URLError) as exc:
            self.voice_result.emit(False, str(exc) or "Bolt could not receive the voice query.")

    def _voice_finished(self, succeeded: bool, message: str) -> None:
        if succeeded:
            self.overlay.show_message("Opening Bolt with your question")
            self.open_workspace()
            QTimer.singleShot(1800, self.overlay.hide_overlay)
        else:
            self._voice_error(message)

    def _start_frontend(self) -> None:
        distribution = self.frontend_root / "dist"
        if not (distribution / "index.html").exists():
            raise RuntimeError("Build the frontend with npm run build before starting Bolt.")
        handler = partial(QuietStaticHandler, directory=str(distribution))
        self.frontend_server = ThreadingHTTPServer(("127.0.0.1", 5173), handler)
        self.frontend_thread = threading.Thread(target=self.frontend_server.serve_forever, daemon=True)
        self.frontend_thread.start()

    def _tray_icon(self) -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#f05255"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#fff8ef"))
        painter.setFont(QFont("Georgia", 34, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "B")
        painter.end()
        return QIcon(pixmap)


def main() -> int:
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Bolt AI")
    qt_app.setQuitOnLastWindowClosed(False)
    launcher = DesktopLauncher(qt_app)
    launcher.start()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
