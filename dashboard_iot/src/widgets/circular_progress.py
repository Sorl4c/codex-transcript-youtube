"""
Simple circular progress indicator tailored for sensor percentages.
"""
from __future__ import annotations

from typing import Tuple

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QConicalGradient,
    QFont,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget


class CircularProgress(QWidget):
    """
    Custom widget that renders a circular progress arc with a gradient outline.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        diameter: int = 140,
        thickness: int = 12,
        gradient: Tuple[QColor, QColor] = (QColor("#4facfe"), QColor("#00f2fe")),
    ) -> None:
        super().__init__(parent)
        self._value: float = 0.0
        self._max_value: float = 100.0
        self._diameter = diameter
        self._thickness = max(4, thickness)
        self._gradient = gradient
        self._text_color = QColor("#F0F4FF")
        self._font = QFont("Segoe UI", 12, QFont.Weight.Bold)

        self.setMinimumSize(self._diameter, self._diameter)
        self.setMaximumSize(self._diameter, self._diameter)

    def set_value(self, value: float, max_value: float | None = None) -> None:
        if max_value is not None:
            self._max_value = max(float(max_value), 1e-6)
        self._value = max(0.0, min(float(value), self._max_value))
        self.update()

    def set_gradient(self, start: QColor, end: QColor) -> None:
        self._gradient = (start, end)
        self.update()

    def set_text_color(self, color: QColor) -> None:
        self._text_color = color
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(
            self._thickness,
            self._thickness,
            -self._thickness,
            -self._thickness,
        )

        # Draw background arc
        background_pen = QPen(QColor(60, 70, 110), self._thickness)
        background_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(background_pen)
        painter.drawArc(rect, 90 * 16, -360 * 16)

        # Draw progress arc with gradient
        span_angle = -int(360 * 16 * (self._value / max(self._max_value, 1e-6)))
        gradient = QConicalGradient(QPointF(rect.center()), 90)
        gradient.setColorAt(0.0, self._gradient[0])
        gradient.setColorAt(1.0, self._gradient[1])

        progress_pen = QPen()
        progress_pen.setWidth(self._thickness)
        progress_pen.setBrush(gradient)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(rect, 90 * 16, span_angle)

        # Draw text
        painter.setFont(self._font)
        painter.setPen(self._text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self._value:.0f}%")
