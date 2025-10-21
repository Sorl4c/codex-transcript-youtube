"""
Cross-framework theming helpers for the Calm Tech design system.

The goal is to expose a minimal API that Tkinter, PySide6 and Streamlit
frontends can reuse without duplicating color constants or typography rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional

ThemeMode = Literal["light", "dark"]


@dataclass(frozen=True)
class Palette:
    surface: str
    surface_alt: str
    primary: str
    accent: str
    warning: str
    error: str
    success: str
    text_primary: str
    text_secondary: str


@dataclass(frozen=True)
class Typography:
    family: str
    display: int
    h1: int
    h2: int
    body: int
    caption: int


@dataclass(frozen=True)
class Spaces:
    xs: int
    sm: int
    md: int
    lg: int
    xl: int


@dataclass(frozen=True)
class Radii:
    sm: int
    lg: int


@dataclass(frozen=True)
class Shadows:
    soft: str
    inner: str


@dataclass(frozen=True)
class Theme:
    mode: ThemeMode
    palette: Palette
    typography: Typography
    spaces: Spaces
    radii: Radii
    shadows: Shadows


_BASE_TYPOGRAPHY = Typography(
    family="Inter, Roboto, system-ui, -apple-system",
    display=32,
    h1=24,
    h2=18,
    body=14,
    caption=12,
)

_BASE_SPACES = Spaces(xs=4, sm=8, md=16, lg=24, xl=32)
_BASE_RADII = Radii(sm=8, lg=16)
_LIGHT_SHADOWS = Shadows(
    soft="0 12px 32px rgba(15, 23, 42, 0.08)",
    inner="inset 0 1px 2px rgba(148, 163, 184, 0.25)",
)
_DARK_SHADOWS = Shadows(
    soft="0 12px 32px rgba(15, 23, 42, 0.35)",
    inner="inset 0 1px 2px rgba(148, 163, 184, 0.35)",
)

_PALETTES: Dict[ThemeMode, Palette] = {
    "light": Palette(
        surface="#F8FAFC",
        surface_alt="#EEF2FF",
        primary="#2563EB",
        accent="#10B981",
        warning="#F59E0B",
        error="#EF4444",
        success="#0EA5E9",
        text_primary="#0F172A",
        text_secondary="#475569",
    ),
    "dark": Palette(
        surface="#1E293B",
        surface_alt="#27364D",
        primary="#60A5FA",
        accent="#34D399",
        warning="#FBBF24",
        error="#F87171",
        success="#38BDF8",
        text_primary="#E2E8F0",
        text_secondary="#94A3B8",
    ),
}


def get_theme(mode: ThemeMode = "light") -> Theme:
    """Return the theme for the requested mode."""
    palette = _PALETTES.get(mode, _PALETTES["light"])
    shadows = _LIGHT_SHADOWS if mode == "light" else _DARK_SHADOWS
    return Theme(
        mode=mode,
        palette=palette,
        typography=_BASE_TYPOGRAPHY,
        spaces=_BASE_SPACES,
        radii=_BASE_RADII,
        shadows=shadows,
    )


def toggle_mode(current: ThemeMode) -> ThemeMode:
    """Utility to flip theme mode."""
    return "dark" if current == "light" else "light"


# --------------------------------------------------------------------------- #
# Framework helpers (stubs for future integration)
# --------------------------------------------------------------------------- #


def apply_tkinter_theme(root, theme: Optional[Theme] = None) -> None:
    """
    Apply minimal colors to a Tkinter app.

    Notes:
        - Tkinter no soporta CSS; se asignan colores base y fonts.
        - Cada widget complejo deberá ajustar estilos manualmente.
    """
    if theme is None:
        theme = get_theme()

    try:
        family = theme.typography.family.split(",")[0]
        root.configure(bg=theme.palette.surface)
        root.option_add("*Font", f"{family} {theme.typography.body}")
        root.option_add("*Background", theme.palette.surface)
        root.option_add("*Foreground", theme.palette.text_primary)
        root.option_add("*Button.Background", theme.palette.primary)
        root.option_add("*Button.Foreground", "#FFFFFF")
    except Exception:  # pragma: no cover - depende del entorno
        # El objetivo es no romper la app si Tkinter no acepta algún ajuste.
        pass


def get_qt_palette(theme: Optional[Theme] = None) -> Dict[str, str]:
    """
    Generate a dict that mapea roles de color para PySide6.

    Se devolverá un diccionario simple que puede convertirse en QPalette/QSS.
    """
    if theme is None:
        theme = get_theme()

    return {
        "BACKGROUND": theme.palette.surface,
        "BACKGROUND_ALT": theme.palette.surface_alt,
        "PRIMARY": theme.palette.primary,
        "ACCENT": theme.palette.accent,
        "TEXT": theme.palette.text_primary,
        "TEXT_SECONDARY": theme.palette.text_secondary,
        "SUCCESS": theme.palette.success,
        "WARNING": theme.palette.warning,
        "ERROR": theme.palette.error,
    }


def generate_qss(theme: Optional[Theme] = None) -> str:
    """
    Build a basic Qt Style Sheet snippet based on the theme tokens.
    """
    if theme is None:
        theme = get_theme()

    palette = get_qt_palette(theme)
    return f"""
        QWidget {{
            background-color: {palette['BACKGROUND']};
            color: {palette['TEXT']};
            font-family: {theme.typography.family};
            font-size: {theme.typography.body}px;
        }}

        QPushButton {{
            background-color: {palette['PRIMARY']};
            color: #FFFFFF;
            border-radius: {theme.radii.sm}px;
            padding: {theme.spaces.sm}px {theme.spaces.md}px;
        }}

        QPushButton:hover {{
            background-color: {palette['ACCENT']};
        }}

        QLineEdit, QComboBox {{
            background-color: {palette['BACKGROUND_ALT']};
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: {theme.radii.sm}px;
            padding: {theme.spaces.sm}px;
        }}

        QTableWidget {{
            alternate-background-color: {palette['BACKGROUND_ALT']};
            gridline-color: rgba(148, 163, 184, 0.2);
        }}
    """
