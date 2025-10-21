"""
Pequeña demo para verificar la estructura Calm Tech en PySide6.

Ejecutar con:
    PYTHONPATH=. python qt_ui/examples/calm_demo.py
"""
from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from qt_ui.ui.components.calm_custom import CalmSidebar, LogViewer, VideoCard
from qt_ui.ui.design_tokens import build_tokens


def load_qss(mode: str = "light") -> str:
    base = Path(__file__).resolve().parent.parent / "ui" / "themes"
    filename = {
        "light": "calm_light.qss",
        "dark": "calm_dark.qss",
        "high": "high_contrast.qss",
    }.get(mode, "calm_light.qss")
    with open(base / filename, "r", encoding="utf-8") as file:
        return file.read()


def build_window() -> QWidget:
    root = QWidget()
    root.setWindowTitle("Calm Tech Demo")
    layout = QHBoxLayout(root)
    layout.setContentsMargins(0, 0, 0, 0)

    sidebar = CalmSidebar(
        [
            ("library", "Videoteca"),
            ("tasks", "Tareas"),
            ("insights", "Insights"),
            ("settings", "Configuración"),
        ],
        parent=root,
    )
    layout.addWidget(sidebar)

    content = QVBoxLayout()
    content.setContentsMargins(28, 32, 28, 24)
    content.setSpacing(24)

    card = VideoCard(
        "NotebookLM + Perplexity: Flujo de IA que te Ahorra el 80% de tu Tiempo",
        status="Listo",
        language="ES",
        summary="Resumen generado en 4.6s. Tokens: 4202 in, 422 out.",
        parent=root,
    )
    content.addWidget(card)

    logs = LogViewer(parent=root)
    logs.append_log("[INFO] Subtítulos encontrados para el idioma solicitado: 'es'")
    logs.append_log("[INFO] Usando el pipeline de Gemini API.")
    content.addWidget(logs, 1)

    layout.addLayout(content, 1)
    return root


def main() -> None:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication([])
    tokens = build_tokens("light")
    app.setStyleSheet(load_qss(tokens["mode"]))
    window = build_window()
    window.resize(1100, 720)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

