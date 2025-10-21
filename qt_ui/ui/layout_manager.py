"""
Responsive layout helpers for the Calm Tech dashboard.

Por ahora solo se incluyen utilidades ligeras para distribuir widgets en una
rejilla pensada para 12 columnas virtuales. A medida que el diseño evolucione,
podremos migrar a layouts más sofisticados o integrar directamente componentes
de PyQt-Fluent-Widgets.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColumnConfig:
    columns: int
    gutter: int = 16

    def width_for(self, span: int, total_width: int) -> int:
        """
        Calcula el ancho asignado a un widget que ocupa `span` columnas.
        """
        if span <= 0:
            raise ValueError("span must be positive")
        span = min(span, self.columns)
        column_width = (total_width - (self.columns - 1) * self.gutter) / self.columns
        return int(span * column_width + (span - 1) * self.gutter)

