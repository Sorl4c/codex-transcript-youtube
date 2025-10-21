"""
Design tokens bridge for the Calm Tech UI.

This module reutiliza `ui.theme` (compartido entre Tkinter y PySide6) y expone
helpers específicos de Qt para mantener sincronizados colores, tipografía y
espaciados.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Literal, TypedDict

from ui.theme import Theme, ThemeMode, get_theme, toggle_mode


class ThemeTokens(TypedDict):
    mode: ThemeMode
    palette: Dict[str, str]
    typography: Dict[str, int | str]
    spaces: Dict[str, int]
    radii: Dict[str, int]
    shadows: Dict[str, str]


def build_tokens(mode: ThemeMode = "light") -> ThemeTokens:
    """Return a serializable dict with all tokens for the requested mode."""
    theme = get_theme(mode)
    return _serialize_theme(theme)


def _serialize_theme(theme: Theme) -> ThemeTokens:
    return ThemeTokens(
        mode=theme.mode,
        palette=asdict(theme.palette),
        typography=asdict(theme.typography),
        spaces=asdict(theme.spaces),
        radii=asdict(theme.radii),
        shadows=asdict(theme.shadows),
    )


def next_mode(current: ThemeMode) -> ThemeMode:
    """Convenience helper to switch theme mode."""
    return toggle_mode(current)

