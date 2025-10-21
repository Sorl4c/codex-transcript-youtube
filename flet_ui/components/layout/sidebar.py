from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from flet_utils.helpers import run_handler


class Sidebar:
    """Left navigation rail for the application."""

    def __init__(self, *, on_nav: Optional[Callable[[str], None]] = None) -> None:
        self._on_nav = on_nav
        self._destinations = [
            ("library", "Videoteca", ft.Icons.VIDEO_LIBRARY_OUTLINED),
            ("ingest", "Ingesta (próximamente)", ft.Icons.CLOUD_UPLOAD_OUTLINED),
        ]
        self._rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            bgcolor=ft.Colors.WHITE,
            min_width=72,
            min_extended_width=200,
            group_alignment=-0.9,
            extended=True,
            on_change=self._handle_change,
            destinations=[
                ft.NavigationRailDestination(
                    icon=icon,
                    selected_icon=icon,
                    label=label,
                )
                for _, label, icon in self._destinations
            ],
        )

    @property
    def control(self) -> ft.NavigationRail:
        return self._rail

    def set_selected(self, key: str) -> None:
        index = next(
            (idx for idx, (dest_key, _, _) in enumerate(self._destinations) if dest_key == key),
            0,
        )
        self._rail.selected_index = index
        self._rail.update()

    async def _handle_change(self, event: ft.ControlEvent) -> None:
        index = int(event.control.selected_index)
        key, _, _ = self._destinations[index]
        await run_handler(self._on_nav, key)
