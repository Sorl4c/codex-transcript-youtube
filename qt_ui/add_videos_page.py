"""
PySide6 widget that replicates the "Agregar Videos" workflow.
"""
from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

from .backend import ProcessorCallbacks, YouTubeProcessor


class ProcessWorker(QtCore.QObject):
    progress_changed = QtCore.Signal(float)
    status_changed = QtCore.Signal(str)
    log_added = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(
        self,
        processor: YouTubeProcessor,
        urls: list[str],
        mode: str,
        keep_timestamps: bool,
        ingest_in_rag: bool,
    ):
        super().__init__()
        self.processor = processor
        self.urls = urls
        self.mode = mode
        self.keep_timestamps = keep_timestamps
        self.ingest_in_rag = ingest_in_rag

    @QtCore.Slot()
    def run(self) -> None:
        finished_called = False

        def on_complete() -> None:
            nonlocal finished_called
            finished_called = True
            self.finished.emit()

        callbacks = ProcessorCallbacks(
            update_status=self.status_changed.emit,
            update_progress=self.progress_changed.emit,
            add_log=self.log_added.emit,
            on_complete=on_complete,
        )

        try:
            if self.mode == "Local":
                self.processor.process_urls_locally(
                    self.urls, self.keep_timestamps, self.ingest_in_rag, callbacks
                )
            else:
                self.processor.process_urls_with_api(
                    self.urls, self.keep_timestamps, self.ingest_in_rag, callbacks
                )
        except Exception as exc:  # noqa: BLE001
            self.log_added.emit(f"[FATAL] Error inesperado: {exc}")
        finally:
            if not finished_called:
                self.finished.emit()


class AddVideosWidget(QtWidgets.QWidget):
    """Widget covering URL ingestion UI."""

    data_changed = QtCore.Signal()
    log_emitted = QtCore.Signal(str)

    def __init__(
        self,
        processor: YouTubeProcessor,
        rag_available: bool,
        rag_stats_provider,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.processor = processor
        self.rag_available = rag_available
        self.rag_stats_provider = rag_stats_provider
        self._thread: Optional[QtCore.QThread] = None
        self._worker: Optional[ProcessWorker] = None

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        self.url_edit = QtWidgets.QPlainTextEdit()
        self.url_edit.setPlaceholderText("Pega aquí las URLs de YouTube, una por línea…")
        self.url_edit.setMinimumHeight(140)

        layout.addWidget(QtWidgets.QLabel("URLs (una por línea):"))
        layout.addWidget(self.url_edit)

        options_group = QtWidgets.QGroupBox("Opciones de procesamiento")
        options_layout = QtWidgets.QGridLayout(options_group)

        self.mode_api = QtWidgets.QRadioButton("API")
        self.mode_local = QtWidgets.QRadioButton("Local")
        self.mode_api.setChecked(True)

        options_layout.addWidget(QtWidgets.QLabel("Modo:"), 0, 0)
        options_layout.addWidget(self.mode_api, 0, 1)
        options_layout.addWidget(self.mode_local, 0, 2)

        self.keep_timestamps = QtWidgets.QCheckBox("Mantener marcas de tiempo")
        options_layout.addWidget(self.keep_timestamps, 1, 0, 1, 3)

        self.ingest_rag = QtWidgets.QCheckBox("Ingestar en RAG automáticamente")
        self.ingest_rag.setEnabled(self.rag_available)
        options_layout.addWidget(self.ingest_rag, 2, 0, 1, 3)

        if not self.rag_available:
            rag_label = QtWidgets.QLabel("⚠️ Sistema RAG no disponible.")
            rag_label.setStyleSheet("color: orange;")
            options_layout.addWidget(rag_label, 3, 0, 1, 3)
        else:
            stats = self.rag_stats_provider()
            stats_group = QtWidgets.QGroupBox("Estadísticas RAG")
            stats_layout = QtWidgets.QGridLayout(stats_group)
            stats_layout.addWidget(
                QtWidgets.QLabel(f"Documentos: {stats.total_documents}"), 0, 0
            )
            stats_layout.addWidget(
                QtWidgets.QLabel(f"Embeddings: {stats.embedder_type}"), 0, 1
            )
            stats_layout.addWidget(
                QtWidgets.QLabel(f"Base de datos: {stats.database_type}"), 1, 0
            )
            stats_layout.addWidget(
                QtWidgets.QLabel(f"Tamaño BD: {stats.database_size_mb:.2f} MB"), 1, 1
            )
            options_layout.addWidget(stats_group, 4, 0, 1, 3)

        layout.addWidget(options_group)

        self.process_button = QtWidgets.QPushButton("Procesar vídeos")
        self.process_button.clicked.connect(self._start_processing)  # type: ignore[arg-type]
        layout.addWidget(self.process_button)

        self.status_label = QtWidgets.QLabel("Listo.")
        layout.addWidget(self.status_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 1000)
        layout.addWidget(self.progress_bar)

        layout.addWidget(QtWidgets.QLabel("Registro de actividad:"))
        self.log_edit = QtWidgets.QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMinimumHeight(220)
        layout.addWidget(self.log_edit)

        layout.addStretch(1)

    def _start_processing(self) -> None:
        if self._thread and self._thread.isRunning():
            QtWidgets.QMessageBox.information(
                self,
                "Procesamiento en curso",
                "Ya hay un proceso en ejecución.",
            )
            return

        raw_urls = [line.strip() for line in self.url_edit.toPlainText().splitlines()]
        urls = [url for url in raw_urls if url]
        if not urls:
            QtWidgets.QMessageBox.warning(
                self,
                "Entrada inválida",
                "Introduce al menos una URL.",
            )
            return

        mode = "Local" if self.mode_local.isChecked() else "API"
        keep_timestamps = self.keep_timestamps.isChecked()
        ingest_rag = self.ingest_rag.isChecked() and self.rag_available

        self._clear_log()
        self.process_button.setEnabled(False)
        self.status_label.setText("Inicializando proceso…")
        self.progress_bar.setValue(0)

        self._thread = QtCore.QThread(self)
        self._worker = ProcessWorker(
            self.processor, urls, mode, keep_timestamps, ingest_rag
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)  # type: ignore[arg-type]
        self._worker.progress_changed.connect(
            lambda value: self.progress_bar.setValue(int(value * 1000))
        )
        self._worker.status_changed.connect(self.status_label.setText)
        self._worker.log_added.connect(self._append_log)
        self._worker.finished.connect(self._handle_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _handle_finished(self) -> None:
        self.process_button.setEnabled(True)
        self.status_label.setText("Proceso finalizado.")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.data_changed.emit()
        self._thread = None
        self._worker = None
        QtWidgets.QMessageBox.information(
            self,
            "Proceso completado",
            "La ingestión de vídeos ha finalizado. Revisa el registro para más detalles.",
        )

    def _append_log(self, message: str) -> None:
        self.log_edit.appendPlainText(message)
        cursor = self.log_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.log_edit.setTextCursor(cursor)
        self.log_emitted.emit(message)

    def _clear_log(self) -> None:
        self.log_edit.clear()

    def abort_processing(self) -> None:
        """Ensure threads are cleaned up when closing the app."""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)
            self._thread = None
            self._worker = None
