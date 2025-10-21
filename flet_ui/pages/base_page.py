from __future__ import annotations

import abc
from typing import Optional

import flet as ft

from core.session import SessionState


class BasePage(abc.ABC):
    """Simple lifecycle interface for application pages."""

    def __init__(self, page: ft.Page, session: SessionState) -> None:
        self.page = page
        self.session = session
        self._is_initialized = False

    @property
    @abc.abstractmethod
    def control(self) -> ft.Control:
        """Return the root control for the page."""

    def mount(self) -> None:
        if not self._is_initialized:
            self.on_mount()
            self._is_initialized = True
        self.refresh()

    @abc.abstractmethod
    def on_mount(self) -> None:
        """Hook executed the first time the page is displayed."""

    @abc.abstractmethod
    def refresh(self) -> None:
        """Refresh page data and visuals."""
