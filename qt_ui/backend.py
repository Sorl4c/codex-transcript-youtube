"""
Shared backend helpers for the PySide6 UI.
Reuses the same business logic as gui_streamlit.py / gui.py but decoupled from UI widgets.
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import pandas as pd

import db
from downloader import download_vtt
from ia.summarize_transcript import process_transcript as get_summary
from parser import format_transcription, vtt_to_plain_text
from rag_interface import RAGInterface, get_rag_interface

logger = logging.getLogger(__name__)


class Video:
    """Simple value object to wrap video records."""

    def __init__(self, data: Dict):
        self.id: Optional[int] = data.get("id")
        self.title: str = data.get("title", "Sin título")
        self.channel: str = data.get("channel", "Desconocido")
        self.upload_date: str = data.get("upload_date", "")
        self.transcript: str = data.get("transcript", "")
        self.summary: str = data.get("summary", "")
        self.url: str = data.get("url", "")
        self.video_id: str = data.get("video_id", "")
        self.key_ideas: Optional[str] = data.get("key_ideas")
        self.ai_categorization: Optional[str] = data.get("ai_categorization")


class DatabaseManager:
    """Wrapper for db module that returns pandas DataFrames for UI consumption."""

    def __init__(self):
        start = time.perf_counter()
        self.db_module = db
        self.db_module.init_db()
        logger.info("DatabaseManager inicializado en %.2fs", time.perf_counter() - start)

    def get_all_videos(self) -> List[Dict]:
        return self.db_module.get_all_videos()

    def get_videos_df(
        self, search_query: str, sort_column: str, sort_direction: str
    ) -> pd.DataFrame:
        column_mapping = {"Fecha": "upload_date", "Título": "title", "Canal": "channel"}
        db_sort_column = column_mapping.get(sort_column, "upload_date")
        videos_data = self.get_all_videos()
        if not videos_data:
            return pd.DataFrame()

        df = pd.DataFrame(videos_data)
        if search_query:
            df = df[
                df["title"].str.contains(search_query, case=False, na=False)
                | df["channel"].str.contains(search_query, case=False, na=False)
            ]

        if db_sort_column in df.columns:
            df = df.sort_values(
                by=db_sort_column, ascending=(sort_direction.lower() == "asc")
            )
        return df

    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        return self.db_module.get_video_by_id(video_id)

    def get_video_by_url(self, video_id: str) -> Optional[Dict]:
        return self.db_module.get_video_by_url(video_id)

    def insert_video(self, video_data: Dict) -> None:
        self.db_module.insert_video(video_data)

    def delete_video(self, video_id: int) -> None:
        self.db_module.delete_video(video_id)

    def update_summary(self, video_id: int, summary: str) -> None:
        self.db_module.update_summary(video_id, summary)


@dataclass
class ProcessorCallbacks:
    update_status: Callable[[str], None]
    update_progress: Callable[[float], None]
    add_log: Callable[[str], None]
    on_complete: Callable[[], None]


class YouTubeProcessor:
    """Processing pipeline used by the UI to ingest videos."""

    def __init__(self, db_manager: DatabaseManager, rag_interface: RAGInterface):
        self.db_manager = db_manager
        self.rag_interface = rag_interface

    @staticmethod
    def get_video_id_from_url(url: str) -> str:
        if not url or not isinstance(url, str):
            return ""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/e/|youtube\.com/watch\?.*&v=)([^#\&\?\n]*)",
            r"youtube\.com/shorts/([^#\&\?\n]*)",
            r"youtube\.com/live/([^#\&\?\n]*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match and match.groups():
                return match.group(1)
        return url.strip()

    def _ingest_in_rag(
        self,
        video_id: str,
        title: str,
        transcript: str,
        callbacks: ProcessorCallbacks,
    ) -> None:
        if not self.rag_interface or not self.rag_interface.is_available():
            callbacks.add_log("[RAG] Sistema no disponible, omitiendo ingestión.")
            return

        callbacks.add_log(f"[RAG] Ingestando '{title}'...")
        rag_result = self.rag_interface.ingest_transcript(
            video_id=video_id,
            title=title or "Sin título",
            transcript=transcript,
            strategy="semantico",
            use_docling=True,
        )
        if rag_result["status"] == "success":
            callbacks.add_log(f"[RAG] '{title}' ingestado correctamente.")
        else:
            callbacks.add_log(
                f"[RAG] Error al ingresar '{title}': {rag_result['message']}"
            )

    def process_urls_locally(
        self,
        urls: List[str],
        keep_timestamps: bool,
        ingest_in_rag: bool,
        callbacks: ProcessorCallbacks,
    ) -> None:
        total_urls = len(urls)
        callbacks.update_status("Iniciando proceso local...")
        for index, url in enumerate(urls, start=1):
            callbacks.update_progress((index - 1) / max(total_urls, 1))
            callbacks.add_log(f"[LOCAL] Procesando URL {index}/{total_urls}: {url}")
            video_id = self.get_video_id_from_url(url)
            if not video_id:
                callbacks.add_log("[WARN] No se pudo extraer el ID del vídeo, se omite.")
                continue
            if self.db_manager.get_video_by_url(video_id):
                callbacks.add_log("[INFO] Vídeo ya existe en la base de datos, se omite.")
                continue

            try:
                vtt_content, _, video_info = download_vtt(video_id)
                if not vtt_content or not video_info:
                    callbacks.add_log("[ERROR] No se encontró contenido VTT.")
                    continue

                plain_text = vtt_to_plain_text(
                    vtt_content, remove_timestamps=not keep_timestamps
                )
                formatted_transcript = format_transcription(
                    plain_text,
                    title=video_info.get("title", "Sin título"),
                    url=url,
                )
                video_data = {
                    "url": url,
                    "channel": video_info.get("channel", "N/A"),
                    "title": video_info.get("title", "Sin título"),
                    "upload_date": video_info.get("upload_date", "N/A"),
                    "transcript": formatted_transcript,
                    "summary": "",
                    "key_ideas": "",
                    "ai_categorization": "",
                    "video_id": video_id,
                }
                self.db_manager.insert_video(video_data)
                callbacks.add_log(
                    f"[OK] '{video_data['title']}' guardado en la base de datos."
                )

                if ingest_in_rag:
                    self._ingest_in_rag(video_id, video_data["title"], plain_text, callbacks)
            except Exception as exc:  # noqa: BLE001
                callbacks.add_log(f"[FATAL] Error procesando '{url}': {exc}")
            finally:
                callbacks.update_progress(index / max(total_urls, 1))

        callbacks.update_status("Proceso local completado.")
        callbacks.on_complete()

    def process_urls_with_api(
        self,
        urls: List[str],
        keep_timestamps: bool,
        ingest_in_rag: bool,
        callbacks: ProcessorCallbacks,
    ) -> None:
        total_urls = len(urls)
        callbacks.update_status("Iniciando procesamiento con API...")
        for index, url in enumerate(urls, start=1):
            callbacks.update_progress((index - 1) / max(total_urls, 1))
            callbacks.add_log(f"[API] Procesando URL {index}/{total_urls}: {url}")
            try:
                vtt_content, _, metadata = download_vtt(url)
                if not vtt_content:
                    callbacks.add_log("[WARN] No se encontraron subtítulos.")
                    continue

                plain_text = vtt_to_plain_text(
                    vtt_content, remove_timestamps=not keep_timestamps
                )
                summary_text = get_summary(plain_text, pipeline_type="gemini")[0]
                if summary_text and "Error:" not in summary_text:
                    formatted_transcript = format_transcription(
                        plain_text, title=metadata.get("title", "Sin título"), url=url
                    )
                    video_id = self.get_video_id_from_url(url)
                    video_data = {
                        "url": url,
                        "channel": metadata.get("channel", "N/A"),
                        "title": metadata.get("title", "Título no disponible"),
                        "upload_date": metadata.get("upload_date"),
                        "transcript": formatted_transcript,
                        "summary": summary_text,
                        "key_ideas": None,
                        "ai_categorization": None,
                        "video_id": video_id,
                    }
                    self.db_manager.insert_video(video_data)
                    callbacks.add_log(
                        f"[OK] '{video_data['title']}' procesado y guardado."
                    )
                    if ingest_in_rag:
                        self._ingest_in_rag(video_id, video_data["title"], plain_text, callbacks)
                else:
                    callbacks.add_log(f"[ERROR] Error de la API: {summary_text}")
            except Exception as exc:  # noqa: BLE001
                callbacks.add_log(f"[FATAL] Error crítico procesando '{url}': {exc}")
            finally:
                callbacks.update_progress(index / max(total_urls, 1))

        callbacks.update_status("Proceso con API completado.")
        callbacks.on_complete()


def bootstrap_components() -> tuple[DatabaseManager, RAGInterface, YouTubeProcessor]:
    """Helper used by the PySide6 app to instantiate core services."""
    db_manager = DatabaseManager()
    rag_interface = get_rag_interface()
    processor = YouTubeProcessor(db_manager, rag_interface)
    return db_manager, rag_interface, processor
