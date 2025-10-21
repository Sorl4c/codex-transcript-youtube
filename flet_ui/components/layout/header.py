from __future__ import annotations

from typing import Optional

import flet as ft

from config.settings import get_settings
from flet_utils.helpers import run_handler


class Header:
    """Top application bar with title and quick actions."""

    def __init__(self, *, on_refresh: Optional[ft.EventHandler] = None) -> None:
        self._settings = get_settings()
        self._on_refresh = on_refresh
        self._stats_text = ft.Text("", size=12, color=ft.Colors.ON_PRIMARY, opacity=0.9)

        self._appbar = ft.AppBar(
            title=ft.Column(
                controls=[
                    ft.Text(
                        self._settings.app_title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY,
                    ),
                    self._stats_text,
                ],
                tight=True,
                spacing=2,
            ),
            center_title=False,
            bgcolor=ft.Colors.BLUE_600,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Actualizar datos",
                    icon_color=ft.Colors.ON_PRIMARY,
                    on_click=self._handle_refresh,
                )
            ],
        )

    @property
    def control(self) -> ft.AppBar:
        return self._appbar

    def update_stats(self, *, total: int, filtered: int) -> None:
        if filtered == total:
            self._stats_text.value = f"{total} vídeo(s) en la biblioteca"
        else:
            self._stats_text.value = f"{filtered} de {total} vídeo(s) visibles"
        # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
        try:
            self._appbar.update()
        except RuntimeError:
            pass

    async def _handle_refresh(self, _event: ft.ControlEvent) -> None:
        await run_handler(self._on_refresh)
