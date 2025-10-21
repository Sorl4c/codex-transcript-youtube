"""
Minimal custom widgets aligned with the Calm Tech design direction.

Estas implementaciones son intencionalmente ligeras: servirán como base que
iremos enriqueciendo conforme se integre PyQt-Fluent-Widgets y el resto de
componentes personalizados.
"""
from __future__ import annotations

from typing import Callable, Optional, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.theme import Theme, get_theme


class CalmSidebar(QFrame):
    """Navigation pane with calm tech styling."""

    activated = Signal(str)

    def __init__(
        self,
        entries: Sequence[tuple[str, str]],
        *,
        theme: Optional[Theme] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or get_theme()
        self.setObjectName("CalmSidebar")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(12)

        title = QLabel("Videoteca AI", self)
        title_font = QFont(self._theme.typography.family.split(",")[0], 14, QFont.DemiBold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title)

        self._list = QListWidget(self)
        self._list.setObjectName("CalmSidebarList")
        self._list.itemActivated.connect(self._emit_selection)

        for key, text in entries:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self._list.addItem(item)

        layout.addWidget(self._list, 1)
        self._apply_palette()

    def select_key(self, key: str) -> None:
        for index in range(self._list.count()):
            item = self._list.item(index)
            if item.data(Qt.UserRole) == key:
                self._list.setCurrentItem(item)
                break

    def _emit_selection(self, item: QListWidgetItem) -> None:
        key = item.data(Qt.UserRole)
        if isinstance(key, str):
            self.activated.emit(key)

    def _apply_palette(self) -> None:
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(self._theme.palette.surface))
        palette.setColor(QPalette.Highlight, QColor(self._theme.palette.primary))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        palette.setColor(QPalette.Window, QColor(self._theme.palette.surface))
        self.setPalette(palette)
        self.setStyleSheet(
            """
            QListWidget#CalmSidebarList {
                border: none;
                outline: 0;
                background: transparent;
            }
            QListWidget#CalmSidebarList::item {
                padding: 10px 12px;
                border-radius: 12px;
                color: rgba(15, 23, 42, 0.75);
            }
            QListWidget#CalmSidebarList::item:selected {
                color: #ffffff;
                background-color: rgba(37, 99, 235, 0.85);
            }
            QListWidget#CalmSidebarList::item:hover {
                background-color: rgba(37, 99, 235, 0.15);
            }
            """
        )


class VideoCard(QFrame):
    """Small card to present video metadata."""

    def __init__(
        self,
        title: str,
        *,
        status: str = "Listo",
        language: str = "ES",
        summary: Optional[str] = None,
        theme: Optional[Theme] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or get_theme()
        self.setObjectName("VideoCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title_label = QLabel(title, self)
        title_font = QFont(self._theme.typography.family.split(",")[0], 13, QFont.DemiBold)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        badge_row = QGridLayout()
        badge_row.setHorizontalSpacing(12)
        badge_row.setVerticalSpacing(8)

        badge_row.addWidget(self._build_badge(status, "#10B981"), 0, 0)
        badge_row.addWidget(self._build_badge(language, "#3B82F6"), 0, 1)

        layout.addLayout(badge_row)

        if summary:
            summary_label = QLabel(summary, self)
            summary_label.setWordWrap(True)
            summary_label.setStyleSheet("color: rgba(71, 85, 105, 0.9);")
            layout.addWidget(summary_label)

        actions = ActionRow(self)
        actions.add_button("Ver resumen")
        actions.add_button("Exportar")
        layout.addLayout(actions.layout)

        self.setStyleSheet(
            f"""
            QFrame#VideoCard {{
                background-color: {self._theme.palette.surface_alt};
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: {self._theme.radii.lg}px;
            }}
            """
        )

    def _build_badge(self, text: str, color: str) -> QLabel:
        badge = QLabel(text, self)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"""
            background-color: {color};
            color: white;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 11px;
            """
        )
        return badge


class ActionRow:
    """
    Helper para crear filas de botones sin depender aún de Fluent.

    Mantiene API simple (`add_button`) y expone `layout` para integrarse en
    cualquier QLayout.
    """

    def __init__(self, parent: QWidget) -> None:
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 8, 0, 0)
        self.layout.setHorizontalSpacing(12)
        self.layout.setVerticalSpacing(0)
        self._col = 0
        self._parent = parent

    def add_button(self, text: str, callback: Optional[Callable[[], None]] = None) -> QPushButton:
        button = QPushButton(text, self._parent)
        button.setCursor(Qt.PointingHandCursor)
        button.setObjectName("CalmButton")
        button.setStyleSheet(
            """
            QPushButton#CalmButton {
                background-color: rgba(37, 99, 235, 0.12);
                border: none;
                color: rgba(37, 99, 235, 0.9);
                padding: 6px 14px;
                border-radius: 18px;
                font-weight: 600;
            }
            QPushButton#CalmButton:hover {
                background-color: rgba(37, 99, 235, 0.2);
            }
            QPushButton#CalmButton:pressed {
                background-color: rgba(37, 99, 235, 0.3);
            }
            """
        )
        if callback:
            button.clicked.connect(callback)  # type: ignore[arg-type]
        self.layout.addWidget(button, 0, self._col)
        self._col += 1
        return button


class LogViewer(QFrame):
    """Structured log panel placeholder."""

    def __init__(self, *, theme: Optional[Theme] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._theme = theme or get_theme()
        self.setObjectName("LogViewer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        header = QLabel("Actividad reciente", self)
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStyleSheet("font-weight: 600;")
        layout.addWidget(header)

        self._log_list = QListWidget(self)
        self._log_list.setAlternatingRowColors(True)
        layout.addWidget(self._log_list)

        self.setStyleSheet(
            f"""
            QFrame#LogViewer {{
                background-color: {self._theme.palette.surface};
                border-top: 1px solid rgba(148, 163, 184, 0.25);
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item {{
                padding: 6px 2px;
            }}
            """
        )

    def append_log(self, message: str) -> None:
        item = QListWidgetItem(message)
        self._log_list.addItem(item)
        self._log_list.scrollToBottom()
