"""
Tkinter GUI replicating the main workflows from gui_streamlit.py.
Provides navigation between video library, ingestion, RAG search,
and detailed analysis views.
"""
from __future__ import annotations

import logging
import queue
import re
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd
import pyperclip
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import db
from downloader import download_vtt
from ia.summarize_transcript import process_transcript as get_summary
from parser import format_transcription, vtt_to_plain_text
from rag_interface import RAGInterface, get_rag_interface

logger = logging.getLogger("gui_tkinter")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# --------------------------------------------------------------------------- #
# Data models and backend helpers
# --------------------------------------------------------------------------- #


class Video:
    """Encapsulates video data returned by the database layer."""

    def __init__(self, video_data: Dict):
        self.id: Optional[int] = video_data.get("id")
        self.title: str = video_data.get("title", "Sin título")
        self.channel: str = video_data.get("channel", "Desconocido")
        self.upload_date: str = video_data.get("upload_date", "")
        self.transcript: str = video_data.get("transcript", "")
        self.summary: str = video_data.get("summary", "")
        self.url: str = video_data.get("url", "")
        self.video_id: str = video_data.get("video_id", "")
        self.key_ideas: Optional[str] = video_data.get("key_ideas")
        self.ai_categorization: Optional[str] = video_data.get("ai_categorization")


class DatabaseManager:
    """Wrapper around db module to provide pandas-friendly utilities."""

    def __init__(self):
        start = time.perf_counter()
        self.db_module = db
        self.db_module.init_db()
        logger.info(
            "DatabaseManager inicializado en %.2fs", time.perf_counter() - start
        )

    def get_all_videos(self) -> List[Dict]:
        return self.db_module.get_all_videos()

    def get_videos_df(
        self, search_query: str, sort_column: str, sort_direction: str
    ) -> pd.DataFrame:
        """Return filtered/sorted video dataframe."""
        column_mapping = {"Fecha": "upload_date", "Título": "title", "Canal": "channel"}
        db_sort_column = column_mapping.get(sort_column, "upload_date")
        videos_data = self.get_all_videos()
        if not videos_data:
            return pd.DataFrame()

        df = pd.DataFrame(videos_data)
        if search_query:
            df = df[
                df["title"]
                .str.contains(search_query, case=False, na=False)
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
    """Processes YouTube URLs for ingestion, mirroring Streamlit logic."""

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


# --------------------------------------------------------------------------- #
# GUI Pages
# --------------------------------------------------------------------------- #


class BasePage(ttk.Frame):
    """Base frame for navigable pages."""

    def __init__(self, master: tk.Widget, app: "App"):
        super().__init__(master)
        self.app = app

    def on_show(self) -> None:
        """Hook executed each time the page becomes visible."""

    def refresh(self) -> None:
        """Optional hook to refresh data."""


class AddVideosPage(BasePage):
    """Page to ingest new videos by URL."""

    def __init__(self, master: tk.Widget, app: "App"):
        super().__init__(master, app)
        self.mode_var = tk.StringVar(value="API")
        self.keep_timestamps_var = tk.BooleanVar(value=False)
        self.ingest_rag_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Listo para procesar URLs.")

        self.log_queue: "queue.Queue[Tuple[str, Optional[float]]]" = queue.Queue()
        self.processing_thread: Optional[threading.Thread] = None

        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self) -> None:
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Label(control_frame, text="URLs (una por línea):").pack(anchor=tk.W, padx=5)
        self.url_text = scrolledtext.ScrolledText(self, height=8, width=100)
        self.url_text.pack(fill=tk.BOTH, expand=False, padx=5)

        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Label(options_frame, text="Modo de procesamiento:").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            options_frame,
            text="API",
            variable=self.mode_var,
            value="API",
        ).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        ttk.Radiobutton(
            options_frame,
            text="Local",
            variable=self.mode_var,
            value="Local",
        ).grid(row=0, column=2, sticky=tk.W)

        ttk.Checkbutton(
            options_frame,
            text="Mantener marcas de tiempo",
            variable=self.keep_timestamps_var,
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)

        rag_available = self.app.rag_interface.is_available()
        self.ingest_checkbox = ttk.Checkbutton(
            options_frame,
            text="Ingestar en RAG",
            variable=self.ingest_rag_var,
            state=tk.NORMAL if rag_available else tk.DISABLED,
        )
        self.ingest_checkbox.grid(row=2, column=0, columnspan=3, sticky=tk.W)
        if not rag_available:
            ttk.Label(
                options_frame,
                text="⚠️ RAG no disponible actualmente.",
                foreground="orange",
            ).grid(row=3, column=0, columnspan=3, sticky=tk.W)
        else:
            self._build_rag_stats(options_frame)

        process_button = ttk.Button(
            self,
            text="Procesar vídeos",
            command=self.start_processing,
        )
        process_button.pack(pady=5)

        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, padx=5)
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W)
        ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=1.0,
        ).pack(fill=tk.X, pady=5)

        ttk.Label(self, text="Registro de actividad:").pack(anchor=tk.W, padx=5)
        self.log_text = scrolledtext.ScrolledText(self, height=10, width=100, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 10))

    def _build_rag_stats(self, master: ttk.Frame) -> None:
        stats = self.app.rag_interface.get_stats()
        stats_frame = ttk.LabelFrame(master, text="Estadísticas RAG")
        stats_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady=10)
        stats_frame.columnconfigure((0, 1), weight=1)

        ttk.Label(stats_frame, text=f"Documentos: {stats.total_documents}").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(stats_frame, text=f"Embeddings: {stats.embedder_type}").grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(stats_frame, text=f"Base de datos: {stats.database_type}").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(stats_frame, text=f"Tamaño BD: {stats.database_size_mb:.2f} MB").grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2
        )

    def start_processing(self) -> None:
        if self.processing_thread and self.processing_thread.is_alive():
            messagebox.showinfo("Procesamiento en curso", "Ya hay un procesamiento en ejecución.")
            return

        raw_urls = self.url_text.get("1.0", tk.END).strip().splitlines()
        urls = [url.strip() for url in raw_urls if url.strip()]
        if not urls:
            messagebox.showwarning("Entrada inválida", "Introduce al menos una URL válida.")
            return

        self.status_var.set("Inicializando procesamiento...")
        self.progress_var.set(0.0)
        self._clear_log()

        keep_timestamps = self.keep_timestamps_var.get()
        ingest_rag = self.ingest_rag_var.get()
        mode = self.mode_var.get()

        callbacks = ProcessorCallbacks(
            update_status=lambda msg: self.log_queue.put(("status", msg)),
            update_progress=lambda value: self.log_queue.put(("progress", value)),
            add_log=lambda msg: self.log_queue.put(("log", msg)),
            on_complete=lambda: self.log_queue.put(("complete", None)),
        )

        def runner() -> None:
            if mode == "Local":
                self.app.yt_processor.process_urls_locally(
                    urls, keep_timestamps, ingest_rag, callbacks
                )
            else:
                self.app.yt_processor.process_urls_with_api(
                    urls, keep_timestamps, ingest_rag, callbacks
                )

        self.processing_thread = threading.Thread(target=runner, daemon=True)
        self.processing_thread.start()

    def _clear_log(self) -> None:
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _append_log(self, message: str) -> None:
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_text.insert(tk.END, f"{timestamp}{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _poll_log_queue(self) -> None:
        try:
            while True:
                message_type, payload = self.log_queue.get_nowait()
                if message_type == "log":
                    self._append_log(str(payload))
                elif message_type == "status":
                    self.status_var.set(str(payload))
                elif message_type == "progress" and isinstance(payload, (int, float)):
                    self.progress_var.set(max(0.0, min(1.0, payload)))
                elif message_type == "complete":
                    self.status_var.set("Proceso finalizado.")
                    self.app.refresh_all()
        except queue.Empty:
            pass
        self.after(100, self._poll_log_queue)


class VideoLibraryPage(BasePage):
    """Page to inspect stored videos."""

    def __init__(self, master: tk.Widget, app: "App"):
        super().__init__(master, app)
        self.search_var = tk.StringVar()
        self.sort_column_var = tk.StringVar(value="Fecha")
        self.sort_direction_var = tk.StringVar(value="Descendente")
        self.summary_text: Optional[scrolledtext.ScrolledText] = None
        self.transcript_text: Optional[scrolledtext.ScrolledText] = None
        self.selected_video_id: Optional[int] = None

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        filters_frame = ttk.Frame(self)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filters_frame, text="Buscar:").grid(row=0, column=0, sticky=tk.W)
        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        search_entry.bind("<Return>", lambda _: self.refresh())

        ttk.Label(filters_frame, text="Ordenar por:").grid(row=0, column=2, padx=10)
        sort_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.sort_column_var,
            values=["Fecha", "Título", "Canal"],
            state="readonly",
            width=12,
        )
        sort_combo.grid(row=0, column=3, sticky=tk.W)
        sort_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        ttk.Label(filters_frame, text="Dirección:").grid(row=0, column=4, padx=10)
        direction_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.sort_direction_var,
            values=["Descendente", "Ascendente"],
            state="readonly",
            width=12,
        )
        direction_combo.grid(row=0, column=5, sticky=tk.W)
        direction_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "title", "channel", "upload_date")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Título")
        self.tree.heading("channel", text="Canal")
        self.tree.heading("upload_date", text="Fecha")

        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("title", width=300)
        self.tree.column("channel", width=180)
        self.tree.column("upload_date", width=120, anchor=tk.CENTER)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        details_frame = ttk.LabelFrame(self, text="Detalles del vídeo")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(details_frame, text="Resumen:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.summary_text = scrolledtext.ScrolledText(details_frame, height=10, width=80)
        self.summary_text.grid(row=1, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="nsew")

        ttk.Label(details_frame, text="Transcripción:").grid(
            row=2, column=0, sticky=tk.W, padx=5
        )
        self.transcript_text = scrolledtext.ScrolledText(
            details_frame, height=12, width=80
        )
        self.transcript_text.grid(
            row=3, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="nsew"
        )

        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        details_frame.rowconfigure(3, weight=1)

        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)

        ttk.Button(
            button_frame, text="Generar resumen", command=self.generate_summary
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="Copiar resumen", command=self.copy_summary
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="Copiar transcripción", command=self.copy_transcript
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="Eliminar vídeo", command=self.delete_video
        ).pack(side=tk.LEFT, padx=5)

    def refresh(self) -> None:
        df = self.app.db_manager.get_videos_df(
            self.search_var.get(),
            self.sort_column_var.get(),
            "asc" if self.sort_direction_var.get() == "Ascendente" else "desc",
        )
        self.tree.delete(*self.tree.get_children())
        for _, row in df.iterrows():
            self.tree.insert(
                "",
                tk.END,
                iid=str(row["id"]),
                values=(row["id"], row["title"], row["channel"], row["upload_date"]),
            )
        self._clear_details()

    def _clear_details(self) -> None:
        if self.summary_text:
            self.summary_text.delete("1.0", tk.END)
        if self.transcript_text:
            self.transcript_text.delete("1.0", tk.END)
        self.selected_video_id = None

    def _on_select(self, event: tk.Event) -> None:  # noqa: ANN001
        selected = self.tree.selection()
        if not selected:
            return
        video_id = int(selected[0])
        video_data = self.app.db_manager.get_video_by_id(video_id)
        if not video_data:
            messagebox.showerror("Error", f"No se encontró el vídeo ID {video_id}.")
            return
        video = Video(video_data)
        self.selected_video_id = video.id

        if self.summary_text:
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert(tk.END, video.summary or "Sin resumen disponible.")

        if self.transcript_text:
            self.transcript_text.delete("1.0", tk.END)
            self.transcript_text.insert(
                tk.END, video.transcript or "Sin transcripción disponible."
            )

    def _ensure_video_selected(self) -> Optional[int]:
        if not self.selected_video_id:
            messagebox.showinfo(
                "Sin selección", "Selecciona un vídeo en la tabla para continuar."
            )
            return None
        return self.selected_video_id

    def generate_summary(self) -> None:
        video_id = self._ensure_video_selected()
        if video_id is None:
            return
        video_data = self.app.db_manager.get_video_by_id(video_id)
        if not video_data:
            messagebox.showerror("Error", "No se pudo cargar el vídeo seleccionado.")
            return

        def worker() -> None:
            try:
                summary, *_ = get_summary(video_data["transcript"], pipeline_type="native")
                self.app.db_manager.update_summary(video_id, summary)
                self.app.run_on_ui_thread(
                    lambda: self._update_summary_text(summary),
                    description="Actualizar resumen",
                )
                self.app.run_on_ui_thread(
                    lambda: messagebox.showinfo(
                        "Resumen generado", "El resumen se generó correctamente."
                    ),
                    description="Aviso resumen generado",
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error generando resumen: %s", exc)
                self.app.run_on_ui_thread(
                    lambda: messagebox.showerror(
                        "Error", f"No se pudo generar el resumen: {exc}"
                    ),
                    description="Aviso error resumen",
                )

        threading.Thread(target=worker, daemon=True).start()

    def _update_summary_text(self, summary: str) -> None:
        if self.summary_text:
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert(tk.END, summary)

    def copy_summary(self) -> None:
        if not self.summary_text:
            return
        content = self.summary_text.get("1.0", tk.END).strip()
        if content:
            pyperclip.copy(content)
            messagebox.showinfo("Copiado", "Resumen copiado al portapapeles.")

    def copy_transcript(self) -> None:
        if not self.transcript_text:
            return
        content = self.transcript_text.get("1.0", tk.END).strip()
        if content:
            pyperclip.copy(content)
            messagebox.showinfo("Copiado", "Transcripción copiada al portapapeles.")

    def delete_video(self) -> None:
        video_id = self._ensure_video_selected()
        if video_id is None:
            return
        confirm = messagebox.askyesno(
            "Eliminar vídeo",
            "¿Estás seguro de que deseas eliminar el vídeo seleccionado?",
        )
        if not confirm:
            return
        self.app.db_manager.delete_video(video_id)
        self.refresh()
        self.app.refresh_all()
        messagebox.showinfo("Eliminado", "El vídeo se eliminó correctamente.")


class RAGSearchPage(BasePage):
    """Page to query the RAG engine."""

    def __init__(self, master: tk.Widget, app: "App"):
        super().__init__(master, app)
        self.question_var = tk.StringVar()
        self.mode_var = tk.StringVar()
        self.top_k_var = tk.IntVar(value=5)
        self.status_var = tk.StringVar(value="Listo.")
        self.results_container = ttk.Frame(self)
        self._build_ui()

    def _build_ui(self) -> None:
        if not self.app.rag_interface.is_available():
            ttk.Label(
                self,
                text="❌ Sistema RAG no disponible. Verifica dependencias necesarias.",
                foreground="red",
            ).pack(padx=10, pady=10)
            return

        config_frame = ttk.LabelFrame(self, text="Configuración de búsqueda")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(config_frame, text="Pregunta:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(config_frame, textvariable=self.question_var, width=70).grid(
            row=0, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W
        )

        modes = self.app.rag_interface.get_available_modes()
        self.mode_var.set(modes[0] if modes else "hybrid")
        ttk.Label(config_frame, text="Modo:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Combobox(
            config_frame,
            textvariable=self.mode_var,
            values=modes,
            state="readonly",
            width=20,
        ).grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(config_frame, text="Resultados (Top-K):").grid(
            row=1, column=2, sticky=tk.W
        )
        ttk.Spinbox(
            config_frame,
            from_=1,
            to=10,
            textvariable=self.top_k_var,
            width=5,
        ).grid(row=1, column=3, sticky=tk.W, padx=5)

        ttk.Button(self, text="Buscar", command=self.run_query).pack(pady=5)
        ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, padx=10)

        stats_frame = ttk.LabelFrame(self, text="Estadísticas RAG")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        stats = self.app.rag_interface.get_stats()
        ttk.Label(stats_frame, text=f"Documentos: {stats.total_documents}").grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        ttk.Label(stats_frame, text=f"Embeddings: {stats.embedder_type}").grid(
            row=0, column=1, sticky=tk.W, padx=5
        )
        ttk.Label(stats_frame, text=f"Base de datos: {stats.database_type}").grid(
            row=1, column=0, sticky=tk.W, padx=5
        )
        ttk.Label(stats_frame, text=f"Tamaño BD: {stats.database_size_mb:.2f} MB").grid(
            row=1, column=1, sticky=tk.W, padx=5
        )

        self.results_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

    def run_query(self) -> None:
        if not self.app.rag_interface.is_available():
            messagebox.showerror("RAG", "Sistema RAG no disponible.")
            return
        question = self.question_var.get().strip()
        if not question:
            messagebox.showwarning("Entrada requerida", "Introduce una pregunta.")
            return

        mode = self.mode_var.get()
        top_k = max(1, min(10, self.top_k_var.get()))
        self.status_var.set("Ejecutando búsqueda...")

        def worker() -> None:
            try:
                results, error = self.app.rag_interface.query(
                    question, mode=mode, top_k=top_k
                )
                self.app.run_on_ui_thread(
                    lambda: self._display_results(results, error),
                    description="Mostrar resultados RAG",
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error en consulta RAG: %s", exc)
                self.app.run_on_ui_thread(
                    lambda: messagebox.showerror(
                        "Error RAG", f"No se pudo completar la búsqueda: {exc}"
                    ),
                    description="Error RAG",
                )
            finally:
                self.status_var.set("Listo.")

        threading.Thread(target=worker, daemon=True).start()

    def _display_results(self, results, error) -> None:
        for child in self.results_container.winfo_children():
            child.destroy()

        if error:
            ttk.Label(
                self.results_container, text=f"❌ Error en la búsqueda: {error}", foreground="red"
            ).pack(anchor=tk.W)
            return

        if not results:
            ttk.Label(
                self.results_container,
                text="⚠️ No se encontraron resultados. Ajusta la pregunta o ingesta más transcripciones.",
            ).pack(anchor=tk.W)
            return

        for idx, result in enumerate(results, start=1):
            frame = ttk.LabelFrame(
                self.results_container,
                text=f"Resultado #{idx} (Score: {result.score:.4f})",
            )
            frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(frame, text="Contenido:").pack(anchor=tk.W, padx=5)
            content_text = scrolledtext.ScrolledText(frame, height=6, wrap=tk.WORD)
            content_text.insert(tk.END, result.content)
            content_text.config(state=tk.DISABLED)
            content_text.pack(fill=tk.X, padx=5, pady=5)

            meta_parts = [f"Score: {result.score:.4f}"]
            if result.vector_rank is not None:
                meta_parts.append(f"Vector rank #{result.vector_rank} (score {result.vector_score:.4f})")
            if result.bm25_rank is not None:
                meta_parts.append(f"BM25 rank #{result.bm25_rank} (score {result.bm25_score:.4f})")
            ttk.Label(frame, text=" | ".join(meta_parts)).pack(anchor=tk.W, padx=5, pady=(0, 5))

            ttk.Button(
                frame,
                text=f"Copiar resultado #{idx}",
                command=lambda text=result.content: self._copy_result(text),
            ).pack(side=tk.RIGHT, padx=5, pady=5)

    def _copy_result(self, text: str) -> None:
        pyperclip.copy(text)
        messagebox.showinfo("Copiado", "Resultado copiado al portapapeles.")


class DetailedAnalysisPage(BasePage):
    """Allows deeper exploration per channel/video."""

    def __init__(self, master: tk.Widget, app: "App"):
        super().__init__(master, app)
        self.channel_var = tk.StringVar(value="Todos")
        self.video_listbox: Optional[tk.Listbox] = None
        self.summary_text: Optional[scrolledtext.ScrolledText] = None
        self.transcript_text: Optional[scrolledtext.ScrolledText] = None
        self.selected_video_id: Optional[int] = None

        self._build_ui()

    def _build_ui(self) -> None:
        selection_frame = ttk.Frame(self)
        selection_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(selection_frame, text="Canal:").grid(row=0, column=0, sticky=tk.W)
        self.channel_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.channel_var,
            state="readonly",
            width=30,
        )
        self.channel_combo.grid(row=0, column=1, padx=5)
        self.channel_combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_video_list())

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(list_frame, text="Vídeos:").pack(anchor=tk.W)
        self.video_listbox = tk.Listbox(list_frame, height=10)
        self.video_listbox.pack(fill=tk.BOTH, expand=True)
        self.video_listbox.bind("<<ListboxSelect>>", self._on_select_video)

        details_frame = ttk.LabelFrame(self, text="Detalles del vídeo")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(details_frame, text="Resumen:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.summary_text = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD)
        self.summary_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(details_frame, text="Transcripción:").grid(
            row=2, column=0, sticky=tk.W, padx=5
        )
        self.transcript_text = scrolledtext.ScrolledText(
            details_frame, height=12, wrap=tk.WORD
        )
        self.transcript_text.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        details_frame.rowconfigure(1, weight=1)
        details_frame.rowconfigure(3, weight=1)
        details_frame.columnconfigure(0, weight=1)

    def on_show(self) -> None:
        self._refresh_channels()
        self._refresh_video_list()

    def _refresh_channels(self) -> None:
        videos = self.app.db_manager.get_all_videos()
        channels = sorted({video.get("channel", "Desconocido") for video in videos})
        self.channel_combo["values"] = ["Todos"] + channels
        if self.channel_var.get() not in self.channel_combo["values"]:
            self.channel_var.set("Todos")

    def _refresh_video_list(self) -> None:
        if not self.video_listbox:
            return
        channel = self.channel_var.get()
        videos = self.app.db_manager.get_all_videos()
        filtered = (
            [video for video in videos if video.get("channel") == channel]
            if channel != "Todos"
            else videos
        )
        self.video_listbox.delete(0, tk.END)
        for video in filtered:
            self.video_listbox.insert(
                tk.END, f"{video.get('title', 'Sin título')} (ID: {video.get('id')})"
            )
        self.video_listbox.videos = filtered  # type: ignore[attr-defined]
        self._clear_details()

    def _on_select_video(self, event: tk.Event) -> None:  # noqa: ANN001
        if not self.video_listbox:
            return
        selection = self.video_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        video = getattr(self.video_listbox, "videos", [])[index]
        self.selected_video_id = video.get("id")
        self._populate_details(Video(video))

    def _populate_details(self, video: Video) -> None:
        if self.summary_text:
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert(tk.END, video.summary or "Sin resumen disponible.")
        if self.transcript_text:
            self.transcript_text.delete("1.0", tk.END)
            self.transcript_text.insert(
                tk.END, video.transcript or "Sin transcripción disponible."
            )

    def _clear_details(self) -> None:
        if self.summary_text:
            self.summary_text.delete("1.0", tk.END)
        if self.transcript_text:
            self.transcript_text.delete("1.0", tk.END)
        self.selected_video_id = None


# --------------------------------------------------------------------------- #
# Main Application
# --------------------------------------------------------------------------- #


class App(tk.Tk):
    """Main Tkinter application."""

    def __init__(self):
        super().__init__()
        self.title("Gestor de vídeos YouTube - Tkinter")
        self.geometry("1200x800")

        self.db_manager = DatabaseManager()
        self.rag_interface = get_rag_interface()
        self.yt_processor = YouTubeProcessor(self.db_manager, self.rag_interface)

        self.status_var = tk.StringVar(value="Listo.")

        self._build_layout()

    def _build_layout(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=0, column=0, sticky="ew")
        for column in range(4):
            nav_frame.columnconfigure(column, weight=1)

        ttk.Button(nav_frame, text="Videoteca", command=lambda: self.show_page("library")).grid(
            row=0, column=0, sticky="ew", padx=5, pady=5
        )
        ttk.Button(nav_frame, text="Agregar vídeos", command=lambda: self.show_page("add")).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Button(nav_frame, text="Búsqueda RAG", command=lambda: self.show_page("rag")).grid(
            row=0, column=2, sticky="ew", padx=5, pady=5
        )
        ttk.Button(
            nav_frame,
            text="Análisis detallado",
            command=lambda: self.show_page("analysis"),
        ).grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W, padx=5, pady=5)

        self.pages: Dict[str, BasePage] = {
            "library": VideoLibraryPage(self.content_frame, self),
            "add": AddVideosPage(self.content_frame, self),
            "rag": RAGSearchPage(self.content_frame, self),
            "analysis": DetailedAnalysisPage(self.content_frame, self),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.current_page: Optional[str] = None
        self.show_page("library")

    def show_page(self, key: str) -> None:
        if key not in self.pages:
            return
        if self.current_page:
            self.pages[self.current_page].grid_remove()
        page = self.pages[key]
        page.grid()
        page.on_show()
        page.refresh()
        self.current_page = key
        self.status_var.set(f"Vista actual: {self._page_title(key)}.")

    @staticmethod
    def _page_title(key: str) -> str:
        return {
            "library": "Videoteca",
            "add": "Agregar vídeos",
            "rag": "Búsqueda RAG",
            "analysis": "Análisis detallado",
        }.get(key, key)

    def refresh_all(self) -> None:
        for key, page in self.pages.items():
            if key != self.current_page:
                page.refresh()

    def run_on_ui_thread(
        self,
        callback: Callable[[], None],
        *,
        description: str = "UI callback",
        delay_ms: int = 0,
    ) -> None:
        """Ensures a callable executes in the Tk thread."""

        def safe_callback() -> None:
            try:
                callback()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error en callback %s: %s", description, exc)

        self.after(delay_ms, safe_callback)


if __name__ == "__main__":
    app = App()
    app.mainloop()
