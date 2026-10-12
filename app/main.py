from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.core.application import BoltApplication
from app.ui.main_window import MainWindow


def main() -> int:
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Bolt AI")
    qt_app.setApplicationDisplayName("Bolt AI")
    qt_app.setOrganizationName("Bolt AI")
    qt_app.setStyle("Fusion")

    application = BoltApplication()
    window = MainWindow(application)
    window.show()

    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

