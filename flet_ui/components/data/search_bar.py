from __future__ import annotations

import asyncio
from typing import Callable, Optional

import flet as ft

from config.settings import get_settings
from flet_utils.helpers import run_handler


class SearchBarState:
    """State container for SearchBar functionality."""

    def __init__(self, *, on_search: Optional[Callable[[str], None]] = None) -> None:
        self._settings = get_settings()
        self._on_search = on_search
        self._debounce_task: Optional[asyncio.Task] = None
        self._last_value = ""
        self._input: Optional[ft.TextField] = None

    async def dispatch_search(self, value: str) -> None:
        await run_handler(self._on_search, value)

    async def handle_change(self, event: ft.ControlEvent) -> None:
        value = event.control.value or ""
        self._last_value = value
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        self._debounce_task = asyncio.create_task(self._debounce_and_trigger(value))

    async def debounce_and_trigger(self, value: str) -> None:
        try:
            await asyncio.sleep(self._settings.search_debounce_seconds)
            await self.dispatch_search(value)
        except asyncio.CancelledError:
            return

    async def handle_clear(self, event: ft.ControlEvent, input_field: ft.TextField) -> None:
        input_field.value = ""
        # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
        try:
            input_field.update()
        except RuntimeError:
            # Control no está montado aún, lo cual es normal durante inicialización
            pass
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        await self.dispatch_search("")


def create_search_bar(*, on_search: Optional[Callable[[str], None]] = None) -> ft.Container:
    """Create a search input with debounce to reduce database queries."""
    state = SearchBarState(on_search=on_search)

    input_field = ft.TextField(
        prefix_icon=ft.Icons.SEARCH,
        hint_text="Buscar por título o canal...",
        on_change=state.handle_change,
        expand=True,
        autofocus=False,
    )

    # Store reference to input field for clear functionality
    state._input = input_field

    clear_button = ft.IconButton(
        icon=ft.Icons.CLEAR,
        tooltip="Limpiar búsqueda",
        on_click=lambda e: asyncio.create_task(state.handle_clear(e, input_field)),
    )

    container = ft.Container(
        content=ft.Row(
            controls=[input_field, clear_button],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=4, right=4),
    )

    # Store state reference in container for later access
    container._search_state = state
    container._input_field = input_field

    return container


def set_search_bar_value(search_bar: ft.Container, value: str) -> None:
    """Set the value of a search bar created with create_search_bar."""
    if hasattr(search_bar, '_input_field'):
        search_bar._input_field.value = value
        # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
        try:
            search_bar._input_field.update()
        except RuntimeError:
            # Control no está montado aún, lo cual es normal durante inicialización
            pass
