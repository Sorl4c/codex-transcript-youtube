from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    """Application-level configuration values."""

    app_title: str = "Videoteca Flet"
    page_size: int = 25
    search_debounce_seconds: float = 0.35
    max_page_size: int = 100
    default_sort_field: str = "upload_date"
    default_sort_direction: str = "desc"
    stats_refresh_seconds: int = 10


DEFAULT_SETTINGS = AppSettings()


def get_settings() -> AppSettings:
    """Return immutable application settings."""

    return DEFAULT_SETTINGS
