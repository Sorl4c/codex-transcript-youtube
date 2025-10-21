from __future__ import annotations

import flet as ft


def build_theme() -> ft.Theme:
    """Return the default theme for the Flet application."""

    # Simple theme for Flet 0.7 compatibility
    return ft.Theme(
        color_scheme_seed=ft.Colors.BLUE_600,
        visual_density=ft.VisualDensity.COMPACT,
        font_family="Roboto",
    )
