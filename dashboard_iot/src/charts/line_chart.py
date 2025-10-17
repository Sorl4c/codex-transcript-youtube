"""
Matplotlib line chart embedded in a PySide6 widget.
"""
from __future__ import annotations

from typing import Iterable, List

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


class LineChartWidget(QWidget):
    """Wraps a Matplotlib figure to display activity trends."""

    def __init__(
        self,
        *,
        title: str = "Actividad de Dispositivos",
        color: str = "#4facfe",
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

        self._line = None
        self._color = color

    def plot_series(self, values: Iterable[float]) -> None:
        data = list(values)
        if not data:
            data = [0.0]

        x = list(range(1, len(data) + 1))

        if self._line is None:
            (self._line,) = self.ax.plot(
                x,
                data,
                color=self._color,
                linewidth=2.5,
                marker="o",
                markersize=6,
                markerfacecolor="#00f2fe",
                alpha=0.85,
            )
        else:
            self._line.set_data(x, data)

        self.ax.set_xlim(1, max(x))
        self.ax.set_ylim(0, max(data) * 1.2 if max(data) > 0 else 1)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()
