"""Application entry point for the IoT dashboard demo."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.data_manager import DataManager
from src.main_window import MainWindow


def main() -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Dashboard IoT")
    app.setStyle("Fusion")

    base_path = Path(__file__).resolve().parent
    data_manager = DataManager(base_path)
    window = MainWindow(data_manager)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
