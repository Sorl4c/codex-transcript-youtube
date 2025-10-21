"""
Utilities to work with PyQt-Fluent-Widgets.

El objetivo es centralizar la importación opcional de la librería para poder
degradar elegantemente si no está instalada (por ejemplo, en entornos CI).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

FluentWindow = Any


@dataclass
class FluentImports:
    window: Any
    button: Any
    card: Any
    line_edit: Any
    progress_bar: Any
    combo_box: Any
    toggle_button: Any
    info_bar: Any


_CACHE: Optional[FluentImports] = None
_ERROR: Optional[ImportError] = None


def ensure_fluent_available() -> FluentImports:
    """
    Attempt to import qfluentwidgets and cache the result.

    Raises:
        ImportError: si la librería no se encuentra disponible.
    """
    global _CACHE, _ERROR

    if _CACHE:
        return _CACHE

    if _ERROR:
        raise _ERROR

    try:
        from qfluentwidgets import (
            FluentWindow,
            PrimaryPushButton,
            CardWidget,
            LineEdit,
            ProgressBar,
            ComboBox,
            ToggleButton,
            InfoBar,
        )
    except ImportError as exc:  # pragma: no cover - depende del entorno
        _ERROR = exc
        raise

    _CACHE = FluentImports(
        window=FluentWindow,
        button=PrimaryPushButton,
        card=CardWidget,
        line_edit=LineEdit,
        progress_bar=ProgressBar,
        combo_box=ComboBox,
        toggle_button=ToggleButton,
        info_bar=InfoBar,
    )
    return _CACHE

