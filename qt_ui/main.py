"""
Calm Tech entry point for the PySide6 UI.

Combina componentes personalizados con la futura integración de
PyQt-Fluent-Widgets para lograr una experiencia moderna y consistente.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtCore, QtWidgets

from qt_ui.add_videos_page import AddVideosWidget
from qt_ui.backend import bootstrap_components
from qt_ui.videoteca_page import VideoLibraryWidget
from qt_ui.ui import build_tokens
from qt_ui.ui.components import CalmSidebar, LogViewer

try:  # Opcional: verificar si PyQt-Fluent-Widgets está disponible
    from qt_ui.ui.components import ensure_fluent_available

    ensure_fluent_available()
    FLUENT_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    FLUENT_AVAILABLE = False


THEME_DIR = Path(__file__).resolve().parent / "ui" / "themes"
THEME_FILES: Dict[str, str] = {
    "light": "calm_light.qss",
    "dark": "calm_dark.qss",
    "high": "high_contrast.qss",
}


def _load_stylesheet(mode: str) -> str:
    filename = THEME_FILES.get(mode, THEME_FILES["light"])
    qss_path = THEME_DIR / filename
    try:
        return qss_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


class MainWindow(QtWidgets.QMainWindow):
    """Ventana principal con sidebar, stack de páginas y panel de logs."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gestor Calm Tech para YouTube")
        self.resize(1300, 840)
        self.theme_mode = "light"

        db_manager, rag_interface, processor = bootstrap_components()
        self.db_manager = db_manager
        self.rag_interface = rag_interface
        self.processor = processor

        self._page_keys = ["library", "tasks", "insights", "settings"]
        self._page_titles = {
            "library": "Videoteca",
            "tasks": "Agregar videos",
            "insights": "Insights (próximamente)",
            "settings": "Configuración (próximamente)",
        }
        self._page_widgets: Dict[str, QtWidgets.QWidget] = {}

        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        tokens = build_tokens(self.theme_mode)
        font_family = tokens["typography"]["family"].split(",")[0]

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        root_layout = QtWidgets.QVBoxLayout(central)
        root_layout.setContentsMargins(24, 20, 24, 18)
        root_layout.setSpacing(16)

        # Header
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(12)

        header_texts = QtWidgets.QVBoxLayout()
        header_texts.setSpacing(2)
        self.header_title = QtWidgets.QLabel("Videoteca asistida por IA")
        title_font = self.header_title.font()
        title_font.setFamily(font_family)
        title_font.setPointSize(int(tokens["typography"]["h1"] * 0.75))
        self.header_title.setFont(title_font)

        self.section_label = QtWidgets.QLabel("")
        subtitle_font = self.section_label.font()
        subtitle_font.setFamily(font_family)
        subtitle_font.setPointSize(int(tokens["typography"]["h2"] * 0.72))
        self.section_label.setFont(subtitle_font)
        self.section_label.setStyleSheet("color: rgba(71, 85, 105, 0.85);")

        header_texts.addWidget(self.header_title)
        header_texts.addWidget(self.section_label)
        header_layout.addLayout(header_texts)

        header_layout.addStretch(1)
        self.theme_toggle = QtWidgets.QPushButton("Modo oscuro", self)
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.toggled.connect(self._on_theme_toggled)
        header_layout.addWidget(self.theme_toggle, alignment=QtCore.Qt.AlignRight)
        root_layout.addLayout(header_layout)

        # Body: sidebar + stacked pages
        body_layout = QtWidgets.QHBoxLayout()
        body_layout.setSpacing(24)

        self.sidebar = CalmSidebar(
            [
                ("library", "📚 Videoteca"),
                ("tasks", "➕ Agregar videos"),
                ("insights", "📊 Insights"),
                ("settings", "⚙️ Configuración"),
            ],
            parent=central,
        )
        self.sidebar.activated.connect(self._switch_section)
        body_layout.addWidget(self.sidebar)

        self.page_stack = QtWidgets.QStackedWidget(central)
        body_layout.addWidget(self.page_stack, 1)
        root_layout.addLayout(body_layout, 1)

        # Log viewer
        self.log_viewer = LogViewer(parent=central)
        root_layout.addWidget(self.log_viewer)

        # Instantiate pages
        self.library_widget = VideoLibraryWidget(self.db_manager, parent=central)
        self.add_widget = AddVideosWidget(
            processor=self.processor,
            rag_available=self.rag_interface.is_available(),
            rag_stats_provider=self.rag_interface.get_stats,
            parent=central,
        )
        self.add_widget.log_emitted.connect(self.log_viewer.append_log)
        self.add_widget.data_changed.connect(self.library_widget.refresh_table)

        self._register_page("library", self.library_widget)
        self._register_page("tasks", self.add_widget)
        self._register_page("insights", self._build_placeholder_widget("Insights en construcción."))
        self._register_page("settings", self._build_placeholder_widget("Configura la experiencia calm tech aquí."))

        self.sidebar.select_key("library")
        self._switch_section("library")

        if FLUENT_AVAILABLE:
            self.log_viewer.append_log("[UI] PyQt-Fluent-Widgets disponible para integración.")
        else:
            self.log_viewer.append_log("[UI] PyQt-Fluent-Widgets no encontrado, usando componentes base.")

    def _register_page(self, key: str, widget: QtWidgets.QWidget) -> None:
        self._page_widgets[key] = widget
        self.page_stack.addWidget(widget)

    def _build_placeholder_widget(self, message: str) -> QtWidgets.QWidget:
        placeholder = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        label = QtWidgets.QLabel(message, placeholder)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("color: rgba(71, 85, 105, 0.7); font-size: 15px;")
        layout.addWidget(label)
        layout.addStretch(1)
        return placeholder

    def _on_theme_toggled(self, checked: bool) -> None:
        self.theme_mode = "dark" if checked else "light"
        self._apply_theme()
        self.log_viewer.append_log(f"[UI] Tema cambiado a '{self.theme_mode}'.")

    def _apply_theme(self) -> None:
        app = QtWidgets.QApplication.instance()
        if app is None:
            return

        stylesheet = _load_stylesheet(self.theme_mode)
        app.setStyleSheet(stylesheet)

        label = "Modo claro" if self.theme_mode == "dark" else "Modo oscuro"
        self.theme_toggle.blockSignals(True)
        self.theme_toggle.setChecked(self.theme_mode == "dark")
        self.theme_toggle.setText(label)
        self.theme_toggle.blockSignals(False)

    def _switch_section(self, key: str) -> None:
        if key not in self._page_widgets:
            return
        index = self._page_keys.index(key)
        self.page_stack.setCurrentIndex(index)
        self.section_label.setText(self._page_titles.get(key, ""))
        self.sidebar.select_key(key)

    def closeEvent(self, event) -> None:  # noqa: N802, ANN001
        if hasattr(self, "add_widget"):
            self.add_widget.abort_processing()
        super().closeEvent(event)


def launch() -> None:
    """Launch the PySide6 application."""
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    launch()
