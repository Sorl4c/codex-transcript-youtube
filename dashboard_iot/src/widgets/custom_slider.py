"""
Compound slider widget with a caption and live value label.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class CustomSlider(QWidget):
    """
    Horizontal slider with a title and dynamic value label.
    """

    valueChanged = Signal(int)

    def __init__(
        self,
        title: str,
        *,
        minimum: int = 0,
        maximum: int = 100,
        suffix: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._suffix = suffix
        self._formatter = lambda value: f"{value}{f' {self._suffix}' if self._suffix else ''}"

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #D6DBF5; font-weight: 600;")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setStyleSheet("QSlider::handle:horizontal { background: #4facfe; }")

        self.value_label = QLabel("0")
        self.value_label.setStyleSheet("color: #A7B0D8;")

        slider_row = QHBoxLayout()
        slider_row.addWidget(self.slider)
        slider_row.addWidget(self.value_label)
        slider_row.setContentsMargins(0, 0, 0, 0)
        slider_row.setSpacing(12)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addLayout(slider_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.slider.valueChanged.connect(self._on_value_changed)

    def set_value(self, value: int) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self._update_value_label(value)

    def set_suffix(self, suffix: str) -> None:
        self._suffix = suffix
        self._formatter = lambda value: f"{value}{f' {self._suffix}' if self._suffix else ''}"
        self._update_value_label(self.slider.value())

    def set_formatter(self, formatter: Callable[[int], str]) -> None:
        """
        Provide a callable that receives the slider value and returns a string.
        """
        self._formatter = formatter
        self._update_value_label(self.slider.value())

    def _on_value_changed(self, value: int) -> None:
        self._update_value_label(value)
        self.valueChanged.emit(value)

    def _update_value_label(self, value: int) -> None:
        self.value_label.setText(str(self._formatter(value)))
