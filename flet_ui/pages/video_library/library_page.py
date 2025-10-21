from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from components.data.search_bar import create_search_bar, set_search_bar_value
from components.data.video_table import create_video_table, set_video_table_loading, update_video_table
from components.video.video_details import create_video_details, set_video_details_loading, update_video_details
from core.session import SessionState
from models.video import Video
from pages.base_page import BasePage
from services.database_service import DatabaseService


class LibraryPage(BasePage):
    """Main video library page with table, filters, and details panel."""

    def __init__(
        self,
        *,
        page: ft.Page,
        session: SessionState,
        database_service: DatabaseService,
        on_stats_change: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        super().__init__(page, session)
        self._database = database_service
        self._on_stats_change = on_stats_change
        self._root = ft.Column(expand=True)

        self._search_bar = create_search_bar(on_search=self._handle_search)
        self._video_table = create_video_table(
            on_select=self._handle_select_video,
            on_sort=self._handle_sort,
            on_page_change=self._handle_page_change,
        )
        self._video_details = create_video_details(
            on_copy=self._handle_copy_to_clipboard,
            on_delete=self._request_delete,
        )

        self._snack_bar = ft.SnackBar(
            content=ft.Text("", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE_GREY_700,
            duration=3000,
        )

        self._pending_delete: Optional[Video] = None

    @property
    def control(self) -> ft.Control:
        return self._root

    def on_mount(self) -> None:
        self.page.snack_bar = self._snack_bar
        self._compose_layout()

    def refresh(self) -> None:
        self._load_videos()

    # --- Layout ---------------------------------------------------------------------

    def _compose_layout(self) -> None:
        content = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self._video_table,
                    col={"xs": 12, "md": 7, "lg": 8},
                    expand=True,
                ),
                ft.Container(
                    content=self._video_details,
                    col={"xs": 12, "md": 5, "lg": 4},
                    expand=True,
                ),
            ],
            expand=True,
            run_spacing=16,
        )
        self._status_text = ft.Text("", size=12, opacity=0.7)
        self._root.controls = [
            ft.Column(
                controls=[
                    self._status_text,
                    self._search_bar,
                    content,
                ],
                expand=True,
                spacing=12,
            )
        ]

    # --- Data loading ----------------------------------------------------------------

    def _load_videos(self) -> None:
        self._set_loading(True)
        try:
            videos = self._database.get_all_videos()
            self.session.set_videos(videos)
        finally:
            self._set_loading(False)
        self._ensure_selection()
        self._update_components()

    def _ensure_selection(self) -> None:
        if self.session.selected_video_id is None and self.session.filtered_videos:
            first_video = self.session.filtered_videos[0]
            self.session.select_video(first_video.id)
            self._fetch_and_cache_details(first_video.id)

    def _fetch_and_cache_details(self, video_id: int) -> Optional[Video]:
        details = self.session.detail_cache.get(video_id)
        if details:
            return details
        details = self._database.get_video_details(video_id)
        if details:
            self.session.cache_details(details)
        return details

    # --- UI updates ------------------------------------------------------------------

    def _update_components(self) -> None:
        set_search_bar_value(self._search_bar, self.session.search_query)
        self._update_table()
        self._update_status_text()
        self._update_details()
        self._notify_stats()

    def _update_table(self) -> None:
        videos = self.session.get_current_page_items()
        update_video_table(
            self._video_table,
            videos,
            page_index=self.session.current_page,
            total_pages=self.session.total_pages,
            total_items=self.session.total_filtered,
            sort_field=self.session.sort_field,
            sort_direction=self.session.sort_direction,
            selected_video_id=self.session.selected_video_id,
        )

    def _update_details(self) -> None:
        video = self.session.selected_video
        if video and not video.transcript:
            video = self._fetch_and_cache_details(video.id)
        update_video_details(self._video_details, video)

    def _update_status_text(self) -> None:
        total = self.session.total_videos
        filtered = self.session.total_filtered
        if total == 0:
            self._status_text.value = "No hay vídeos en la biblioteca."
        elif filtered == total:
            self._status_text.value = f"{total} vídeo(s) disponibles."
        else:
            self._status_text.value = f"{filtered} resultado(s) filtrados de {total} vídeo(s)."
        # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
        try:
            self._status_text.update()
        except RuntimeError:
            pass

    def _notify_stats(self) -> None:
        if self._on_stats_change:
            self._on_stats_change(self.session.total_videos, self.session.total_filtered)

    def _set_loading(self, loading: bool) -> None:
        self.session.is_loading = loading
        set_video_table_loading(self._video_table, loading)
        set_video_details_loading(self._video_details, loading)

    # --- Event handlers --------------------------------------------------------------

    async def _handle_search(self, query: str) -> None:
        self.session.update_search(query)
        self._update_components()

    async def _handle_sort(self, field: str, direction: str) -> None:
        self.session.update_sort(field, direction)
        self._update_components()

    async def _handle_page_change(self, action: str) -> None:
        if action == "prev":
            self.session.set_page(self.session.current_page - 1)
        elif action == "next":
            self.session.set_page(self.session.current_page + 1)
        self._update_components()

    async def _handle_select_video(self, video_id: int) -> None:
        self.session.select_video(video_id)
        set_video_details_loading(self._video_details, True)
        details = self._fetch_and_cache_details(video_id)
        set_video_details_loading(self._video_details, False)
        update_video_details(self._video_details, details)
        self._update_table()

    async def _handle_copy_to_clipboard(self, message: str, content: str) -> None:
        if not content:
            return
        self.page.set_clipboard(content)
        self._snack_bar.content.value = message
        self._snack_bar.open = True
        self.page.update()

    async def _request_delete(self, video: Video) -> None:
        self._pending_delete = video
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar vídeo"),
            content=ft.Text(f"¿Deseas eliminar '{video.title}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=self._cancel_delete),
                ft.FilledButton(
                    content=ft.Text("Eliminar"),
                    icon=ft.Icons.DELETE_FOREVER,
                    style=ft.ButtonStyle(color={ft.MaterialState.DEFAULT: ft.Colors.RED}),
                    on_click=self._confirm_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    async def _cancel_delete(self, _event: ft.ControlEvent) -> None:
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
        self._pending_delete = None

    async def _confirm_delete(self, _event: ft.ControlEvent) -> None:
        if not self._pending_delete:
            return
        video = self._pending_delete
        success = self._database.delete_video(video.id)
        if success:
            self.session.remove_video(video.id)
            self._snack_bar.content.value = f"Vídeo '{video.title}' eliminado."
            self._snack_bar.open = True
        else:
            self._snack_bar.content.value = "No se pudo eliminar el vídeo."
            self._snack_bar.open = True
        self._pending_delete = None
        if self.page.dialog:
            self.page.dialog.open = False
        self._ensure_selection()
        self._update_components()
        self.page.update()
