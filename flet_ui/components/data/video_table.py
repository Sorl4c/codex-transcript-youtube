from __future__ import annotations

from functools import partial
from typing import Callable, Iterable, Optional

import flet as ft

from models.video import Video
from flet_utils.helpers import pluralize, run_handler


class VideoTableState:
    """State container for VideoTable functionality."""

    def __init__(
        self,
        *,
        on_select: Optional[Callable[[int], None]] = None,
        on_sort: Optional[Callable[[str, str], None]] = None,
        on_page_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._on_select = on_select
        self._on_sort = on_sort
        self._on_page_change = on_page_change
        self._column_index = {"upload_date": 0, "title": 1, "channel": 2}
        self._data_table: Optional[ft.DataTable] = None
        self._page_label: Optional[ft.Text] = None
        self._prev_button: Optional[ft.IconButton] = None
        self._next_button: Optional[ft.IconButton] = None
        self._loading_indicator: Optional[ft.ProgressBar] = None

    async def handle_row_selection(self, video_id: int, event: ft.ControlEvent) -> None:
        if not event.data or event.data == "false":
            return
        await run_handler(self._on_select, video_id)

    async def handle_sort(self, field: str, event: ft.DataColumnSortEvent) -> None:
        direction = "asc" if event.ascending else "desc"
        await run_handler(self._on_sort, field, direction)

    async def previous_page(self, _event: ft.ControlEvent) -> None:
        await run_handler(self._on_page_change, "prev")

    async def next_page(self, _event: ft.ControlEvent) -> None:
        await run_handler(self._on_page_change, "next")

    def set_loading(self, loading: bool) -> None:
        if self._loading_indicator:
            self._loading_indicator.visible = loading
            # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
            try:
                self._loading_indicator.update()
            except RuntimeError:
                # Control no está montado aún, lo cual es normal durante inicialización
                pass

    def update_data(
        self,
        videos: Iterable[Video],
        *,
        page_index: int,
        total_pages: int,
        total_items: int,
        sort_field: str,
        sort_direction: str,
        selected_video_id: Optional[int],
    ) -> None:
        if not self._data_table or not self._page_label or not self._prev_button or not self._next_button:
            return

        rows = []
        for video in videos:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(video.upload_date or "—")),
                        ft.DataCell(ft.Text(video.title, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(video.channel, overflow=ft.TextOverflow.ELLIPSIS)),
                    ],
                    selected=video.id == selected_video_id,
                )
            )
        self._data_table.rows = rows

        self._data_table.sort_column_index = self._column_index.get(sort_field, 0)
        self._data_table.sort_ascending = sort_direction.lower() == "asc"

        self._page_label.value = f"Página {page_index + 1} de {max(total_pages, 1)} · {pluralize(total_items, 'vídeo')}"
        self._prev_button.disabled = page_index <= 0
        self._next_button.disabled = page_index >= total_pages - 1

        # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
        try:
            self._data_table.update()
        except RuntimeError:
            pass
        try:
            self._prev_button.update()
        except RuntimeError:
            pass
        try:
            self._next_button.update()
        except RuntimeError:
            pass
        try:
            self._page_label.update()
        except RuntimeError:
            pass


def create_video_table(
    *,
    on_select: Optional[Callable[[int], None]] = None,
    on_sort: Optional[Callable[[str, str], None]] = None,
    on_page_change: Optional[Callable[[str], None]] = None,
) -> ft.Column:
    """Create a paginated table to display video listings."""
    state = VideoTableState(
        on_select=on_select,
        on_sort=on_sort,
        on_page_change=on_page_change,
    )

    data_table = ft.DataTable(
        expand=True,
        column_spacing=20,
        heading_row_height=42,
        data_row_min_height=44,
        data_row_max_height=72,
        sort_column_index=state._column_index["upload_date"],
        sort_ascending=False,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        border_radius=ft.BorderRadius.all(8),
        columns=[
            ft.DataColumn(
                label=ft.Text("Fecha", weight=ft.FontWeight.BOLD),
                on_sort=partial(state.handle_sort, "upload_date"),
            ),
            ft.DataColumn(
                label=ft.Text("Título", weight=ft.FontWeight.BOLD),
                on_sort=partial(state.handle_sort, "title"),
            ),
            ft.DataColumn(
                label=ft.Text("Canal", weight=ft.FontWeight.BOLD),
                on_sort=partial(state.handle_sort, "channel"),
            ),
        ],
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    loading_indicator = ft.ProgressBar(visible=False)
    page_label = ft.Text("", size=12, opacity=0.8)
    prev_button = ft.IconButton(
        icon=ft.Icons.CHEVRON_LEFT,
        tooltip="Página anterior",
        on_click=state.previous_page,
        disabled=True,
    )
    next_button = ft.IconButton(
        icon=ft.Icons.CHEVRON_RIGHT,
        tooltip="Página siguiente",
        on_click=state.next_page,
        disabled=True,
    )

    footer = ft.Row(
        controls=[
            prev_button,
            page_label,
            next_button,
            ft.Container(expand=True),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Store references in state
    state._data_table = data_table
    state._page_label = page_label
    state._prev_button = prev_button
    state._next_button = next_button
    state._loading_indicator = loading_indicator

    column = ft.Column(
        controls=[
            ft.Container(loading_indicator, height=4),
            ft.Container(data_table, expand=True, padding=ft.Padding.only(bottom=4)),
            footer,
        ],
        expand=True,
        spacing=8,
    )

    # Store state reference in column for later access
    column._table_state = state

    return column


def set_video_table_loading(video_table: ft.Column, loading: bool) -> None:
    """Set loading state of a video table created with create_video_table."""
    if hasattr(video_table, '_table_state'):
        video_table._table_state.set_loading(loading)


def update_video_table(
    video_table: ft.Column,
    videos: Iterable[Video],
    *,
    page_index: int,
    total_pages: int,
    total_items: int,
    sort_field: str,
    sort_direction: str,
    selected_video_id: Optional[int],
) -> None:
    """Update data of a video table created with create_video_table."""
    if hasattr(video_table, '_table_state'):
        video_table._table_state.update_data(
            videos,
            page_index=page_index,
            total_pages=total_pages,
            total_items=total_items,
            sort_field=sort_field,
            sort_direction=sort_direction,
            selected_video_id=selected_video_id,
        )
