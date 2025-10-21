from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from models.video import Video
from flet_utils.helpers import run_handler


class VideoDetailsState:
    """State container for VideoDetails functionality."""

    def __init__(
        self,
        *,
        on_copy: Optional[Callable[[str, str], None]] = None,
        on_delete: Optional[Callable[[Video], None]] = None,
    ) -> None:
        self._on_copy = on_copy
        self._on_delete = on_delete
        self._video: Optional[Video] = None
        self._title: Optional[ft.Text] = None
        self._subtitle: Optional[ft.Text] = None
        self._summary_text: Optional[ft.Text] = None
        self._transcript_text: Optional[ft.Text] = None
        self._delete_button: Optional[ft.FilledTonalButton] = None
        self._loading_indicator: Optional[ft.ProgressBar] = None
        self._card: Optional[ft.Container] = None
        self._empty_state: Optional[ft.Column] = None
        self._content: Optional[ft.Column] = None

    async def copy_summary(self, _event: ft.ControlEvent) -> None:
        if self._video and self._video.summary:
            await run_handler(self._on_copy, "Resumen copiado al portapapeles.", self._video.summary)

    async def copy_transcript(self, _event: ft.ControlEvent) -> None:
        if self._video and self._video.transcript:
            await run_handler(self._on_copy, "Transcripción copiada al portapapeles.", self._video.transcript)

    async def handle_delete(self, _event: ft.ControlEvent) -> None:
        if self._video:
            await run_handler(self._on_delete, self._video)

    def set_loading(self, loading: bool) -> None:
        if self._loading_indicator:
            self._loading_indicator.visible = loading
            # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
            try:
                self._loading_indicator.update()
            except RuntimeError:
                # Control no está montado aún, lo cual es normal durante inicialización
                pass

    def update_video(self, video: Optional[Video]) -> None:
        self._video = video
        if not self._card or not self._delete_button or not self._title or not self._subtitle or not self._summary_text or not self._transcript_text or not self._content or not self._empty_state:
            return

        if not video:
            self._card.content = self._empty_state
            self._delete_button.disabled = True
        else:
            self._title.value = video.title
            self._subtitle.value = f"{video.channel} · {video.upload_date or 'Sin fecha'}"
            self._summary_text.value = video.summary or "Sin resumen disponible."
            self._transcript_text.value = video.transcript or "Sin transcripción disponible."
            self._delete_button.disabled = False
            self._card.content = self._content
        # Intentar actualizar solo si no hay error de montaje (Flet 1.0)
        try:
            self._card.update()
        except RuntimeError:
            pass


def create_video_details(
    *,
    on_copy: Optional[Callable[[str, str], None]] = None,
    on_delete: Optional[Callable[[Video], None]] = None,
) -> ft.Container:
    """Create a display for detailed information about a selected video."""
    state = VideoDetailsState(on_copy=on_copy, on_delete=on_delete)

    empty_state = ft.Column(
        controls=[
            ft.Icon(ft.Icons.VIDEO_LIBRARY_OUTLINED, size=48, color=ft.Colors.GREY),
            ft.Text("Selecciona un vídeo para ver los detalles.", size=14, text_align=ft.TextAlign.CENTER),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    title = ft.Text("", size=18, weight=ft.FontWeight.BOLD, selectable=True)
    subtitle = ft.Text("", size=12, opacity=0.75, selectable=True)
    summary_text = ft.Text("", selectable=True, expand=True, no_wrap=False)
    transcript_text = ft.Text("", selectable=True, expand=True, no_wrap=False)

    summary_tab = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextButton(content=ft.Text("Copiar resumen"), icon=ft.Icons.COPY_ALL, on_click=state.copy_summary),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[summary_text],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=ft.Padding.all(8),
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.BLUE_GREY),
                border_radius=ft.BorderRadius.all(6),
                expand=True,
            ),
        ],
        expand=True,
        spacing=8,
    )

    transcript_tab = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextButton(content=ft.Text("Copiar transcripción"), icon=ft.Icons.COPY_ALL, on_click=state.copy_transcript),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[transcript_text],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=ft.Padding.all(8),
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.BLUE_GREY),
                border_radius=ft.BorderRadius.all(6),
                expand=True,
            ),
        ],
        expand=True,
        spacing=8,
    )

    # Temporarily replace tabs with simple buttons (Flet 1.0 compatibility)
    def show_summary(_e):
        active_content.content = summary_tab
        active_content.update()
        summary_button.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE_100)
        transcript_button.style = ft.ButtonStyle()
        summary_button.update()
        transcript_button.update()

    def show_transcript(_e):
        active_content.content = transcript_tab
        active_content.update()
        transcript_button.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE_100)
        summary_button.style = ft.ButtonStyle()
        transcript_button.update()
        summary_button.update()

    summary_button = ft.Button(
        content=ft.Text("Resumen"),
        on_click=show_summary,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_100)
    )

    transcript_button = ft.Button(
        content=ft.Text("Transcripción"),
        on_click=show_transcript
    )

    # Container for active content
    active_content = ft.Container(
        content=summary_tab,
        expand=True
    )

    delete_button = ft.FilledTonalButton(
        content=ft.Text("Eliminar vídeo"),
        icon=ft.Icons.DELETE_OUTLINE,
        style=ft.ButtonStyle(color=ft.Colors.RED),
        on_click=state.handle_delete,
        disabled=True,
    )

    loading_indicator = ft.ProgressBar(visible=False)

    content = ft.Column(
        controls=[
            loading_indicator,
            title,
            subtitle,
            ft.Row(
                controls=[summary_button, transcript_button],
                spacing=8,
            ),
            active_content,
            delete_button,
        ],
        spacing=12,
        expand=True,
    )

    card = ft.Container(
        content=empty_state,
        expand=True,
        padding=ft.Padding.all(16),
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.BorderRadius.all(12),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    # Store references in state
    state._title = title
    state._subtitle = subtitle
    state._summary_text = summary_text
    state._transcript_text = transcript_text
    state._delete_button = delete_button
    state._loading_indicator = loading_indicator
    state._card = card
    state._empty_state = empty_state
    state._content = content

    # Store state reference in card for later access
    card._details_state = state

    return card


def set_video_details_loading(video_details: ft.Container, loading: bool) -> None:
    """Set loading state of a video details component created with create_video_details."""
    if hasattr(video_details, '_details_state'):
        video_details._details_state.set_loading(loading)


def update_video_details(video_details: ft.Container, video: Optional[Video]) -> None:
    """Update video data in a video details component created with create_video_details."""
    if hasattr(video_details, '_details_state'):
        video_details._details_state.update_video(video)
