"""
Loads the modern QML dashboard demo in a QQuickView.
Run with:
    PYTHONPATH=. python qt_ui/demos/modern_qml_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    view = QQuickView()
    qml_path = Path(__file__).with_name("modern_dashboard.qml")
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource(QUrl.fromLocalFile(str(qml_path)))
    view.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
