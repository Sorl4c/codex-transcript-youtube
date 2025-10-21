from __future__ import annotations

import flet as ft

from components.layout.header import Header
from components.layout.sidebar import Sidebar
from config.settings import get_settings
from config.theme import build_theme
from core.session import SessionState
from pages.video_library.library_page import LibraryPage
from services.database_service import DatabaseService


class App:
    """Main controller wiring pages, navigation, and shared state."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.settings = get_settings()
        self.session = SessionState()
        self.database_service = DatabaseService()
        self.header = Header(on_refresh=self._refresh_current_page)
        self.sidebar = Sidebar(on_nav=self._handle_navigation)
        self.content_container = ft.Container(expand=True, padding=ft.Padding.all(16))
        self.current_route = "library"

        self.library_page = LibraryPage(
            page=page,
            session=self.session,
            database_service=self.database_service,
            on_stats_change=self._update_stats,
        )

    def run(self) -> None:
        self._configure_page()
        self._compose_shell()
        self._show_page("library")

    # --- Setup ----------------------------------------------------------------------

    def _configure_page(self) -> None:
        self.page.title = self.settings.app_title
        self.page.theme = build_theme()
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_100
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.window_min_height = 720
        self.page.window_min_width = 1024
        self.page.appbar = self.header.control

    def _compose_shell(self) -> None:
        shell = ft.Row(
            controls=[
                ft.Container(
                    content=self.sidebar.control,
                    bgcolor=ft.Colors.WHITE,
                    width=240,
                    height=600,
                ),
                ft.VerticalDivider(width=1, thickness=1, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
                self.content_container,
            ],
            expand=True,
        )
        self.page.add(shell)

    # --- Navigation -----------------------------------------------------------------

    def _show_page(self, route: str) -> None:
        self.current_route = route
        self.sidebar.set_selected(route)

        if route == "library":
            self.library_page.mount()
            self.content_container.content = self.library_page.control
        else:
            placeholder = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CONSTRUCTION, size=64, color=ft.Colors.GREY),
                        ft.Text("Sección en construcción.", size=16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
            )
            self.content_container.content = placeholder

        self.content_container.update()
        self.page.update()

    # --- Callbacks ------------------------------------------------------------------

    async def _handle_navigation(self, route: str) -> None:
        if route == self.current_route:
            return
        self._show_page(route)

    async def _refresh_current_page(self) -> None:
        if self.current_route == "library":
            self.library_page.refresh()

    def _update_stats(self, total: int, filtered: int) -> None:
        self.header.update_stats(total=total, filtered=filtered)
