"""
Matplotlib bar chart embedded in a PySide6 widget.
"""
from __future__ import annotations

from typing import Iterable, Sequence, Tuple

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


class BarChartWidget(QWidget):
    """Displays energy consumption per device."""

    def __init__(
        self,
        *,
        title: str = "Consumo Energético",
        color: str = "#43e97b",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(4.5, 3.0), facecolor="#2B345E")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#273056")
        self.ax.tick_params(colors="#A7B0D8")
        self.ax.spines["bottom"].set_color("#4A5689")
        self.ax.spines["left"].set_color("#4A5689")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_title(title, color="#F0F4FF", pad=16)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)

        self._bars = None
        self._color = color

    def plot_items(self, items: Iterable[Tuple[str, float]]) -> None:
        labels, values = zip(*items) if items else (["Sin datos"], [0.0])
        x = range(len(labels))

        if self._bars is None:
            self._bars = self.ax.bar(
                x,
                values,
                color=self._color,
                alpha=0.85,
                edgecolor="#24fe41",
            )
            self.ax.set_xticks(list(x), labels, rotation=15, ha="right")
        else:
            for bar, value in zip(self._bars, values, strict=False):
                bar.set_height(value)
            self.ax.set_xticks(list(x), labels, rotation=15, ha="right")

        self.ax.set_ylim(0, max(values) * 1.25 if max(values) > 0 else 1)
        self.canvas.draw_idle()
