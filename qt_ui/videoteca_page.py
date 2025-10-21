"""
PySide6 widget that replicates the "Videoteca" workflow.
"""
from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtWidgets

from ia.summarize_transcript import process_transcript as get_summary

from .backend import DatabaseManager, Video


class VideoTableModel(QtCore.QAbstractTableModel):
    headers = ["ID", "Título", "Canal", "Fecha"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[dict] = []

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self.headers)

    def data(self, index, role=QtCore.Qt.DisplayRole):  # noqa: N802, ANN001
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        column_key = ["id", "title", "channel", "upload_date"][index.column()]
        if role == QtCore.Qt.DisplayRole:
            value = row.get(column_key, "")
            return "" if value is None else str(value)
        return None

    def headerData(self, section: int, orientation, role=QtCore.Qt.DisplayRole):  # noqa: N802
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
        return str(section + 1)

    def set_rows(self, rows: list[dict]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def get_row(self, row: int) -> Optional[dict]:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None


class SummaryWorker(QtCore.QObject):
    finished = QtCore.Signal(str)
    failed = QtCore.Signal(str)

    def __init__(self, db_manager: DatabaseManager, video_id: int):
        super().__init__()
        self.db_manager = db_manager
        self.video_id = video_id

    @QtCore.Slot()
    def run(self) -> None:
        try:
            video_data = self.db_manager.get_video_by_id(self.video_id)
            if not video_data:
                self.failed.emit("No se encontró el vídeo seleccionado.")
                return
            summary, *_ = get_summary(video_data["transcript"], pipeline_type="native")
            self.db_manager.update_summary(self.video_id, summary)
            self.finished.emit(summary)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"No se pudo generar el resumen: {exc}")


class VideoLibraryWidget(QtWidgets.QWidget):
    data_changed = QtCore.Signal()

    def __init__(self, db_manager: DatabaseManager, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_video_id: Optional[int] = None
        self._summary_thread: Optional[QtCore.QThread] = None
        self._summary_worker: Optional[SummaryWorker] = None

        self._build_ui()
        self.refresh_table()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        filters_layout = QtWidgets.QGridLayout()
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Título o canal…")
        self.search_edit.returnPressed.connect(self.refresh_table)  # type: ignore[arg-type]

        self.sort_column_combo = QtWidgets.QComboBox()
        self.sort_column_combo.addItems(["Fecha", "Título", "Canal"])
        self.sort_column_combo.currentIndexChanged.connect(self.refresh_table)  # type: ignore[arg-type]

        self.sort_direction_combo = QtWidgets.QComboBox()
        self.sort_direction_combo.addItems(["Descendente", "Ascendente"])
        self.sort_direction_combo.currentIndexChanged.connect(self.refresh_table)  # type: ignore[arg-type]

        filters_layout.addWidget(QtWidgets.QLabel("Buscar:"), 0, 0)
        filters_layout.addWidget(self.search_edit, 0, 1)
        filters_layout.addWidget(QtWidgets.QLabel("Ordenar por:"), 0, 2)
        filters_layout.addWidget(self.sort_column_combo, 0, 3)
        filters_layout.addWidget(QtWidgets.QLabel("Dirección:"), 0, 4)
        filters_layout.addWidget(self.sort_direction_combo, 0, 5)

        layout.addLayout(filters_layout)

        self.table_view = QtWidgets.QTableView()
        self.table_model = VideoTableModel(self)
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_view.selectionModel().selectionChanged.connect(self._on_selection_changed)  # type: ignore[arg-type]

        layout.addWidget(self.table_view, stretch=1)

        details_group = QtWidgets.QGroupBox("Detalles del vídeo")
        details_layout = QtWidgets.QGridLayout(details_group)

        details_layout.addWidget(QtWidgets.QLabel("Resumen:"), 0, 0)
        self.summary_edit = QtWidgets.QTextEdit()
        self.summary_edit.setReadOnly(True)
        self.summary_edit.setMinimumHeight(140)
        details_layout.addWidget(self.summary_edit, 1, 0, 1, 3)

        details_layout.addWidget(QtWidgets.QLabel("Transcripción:"), 2, 0)
        self.transcript_edit = QtWidgets.QTextEdit()
        self.transcript_edit.setReadOnly(True)
        self.transcript_edit.setMinimumHeight(200)
        details_layout.addWidget(self.transcript_edit, 3, 0, 1, 3)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.generate_summary_button = QtWidgets.QPushButton("Generar resumen")
        self.generate_summary_button.clicked.connect(self._generate_summary)  # type: ignore[arg-type]
        self.copy_summary_button = QtWidgets.QPushButton("Copiar resumen")
        self.copy_summary_button.clicked.connect(
            lambda: self._copy_to_clipboard(self.summary_edit.toPlainText())
        )
        self.copy_transcript_button = QtWidgets.QPushButton("Copiar transcripción")
        self.copy_transcript_button.clicked.connect(
            lambda: self._copy_to_clipboard(self.transcript_edit.toPlainText())
        )
        self.delete_button = QtWidgets.QPushButton("Eliminar vídeo")
        self.delete_button.clicked.connect(self._delete_video)  # type: ignore[arg-type]

        buttons_layout.addWidget(self.generate_summary_button)
        buttons_layout.addWidget(self.copy_summary_button)
        buttons_layout.addWidget(self.copy_transcript_button)
        buttons_layout.addWidget(self.delete_button)
        details_layout.addLayout(buttons_layout, 4, 0, 1, 3)

        layout.addWidget(details_group, stretch=1)

    def refresh_table(self) -> None:
        df = self.db_manager.get_videos_df(
            self.search_edit.text(),
            self.sort_column_combo.currentText(),
            "asc" if self.sort_direction_combo.currentText() == "Ascendente" else "desc",
        )
        rows = df.to_dict("records") if not df.empty else []
        self.table_model.set_rows(rows)
        self.summary_edit.clear()
        self.transcript_edit.clear()
        self.selected_video_id = None

    def _on_selection_changed(self, selected, _deselected) -> None:  # noqa: ANN001
        indexes = selected.indexes()
        if not indexes:
            return
        row_index = indexes[0].row()
        row_data = self.table_model.get_row(row_index)
        if not row_data:
            return
        self.selected_video_id = int(row_data["id"])
        video_data = self.db_manager.get_video_by_id(self.selected_video_id)
        if not video_data:
            QtWidgets.QMessageBox.warning(
                self, "Error", "No se pudo cargar el vídeo seleccionado."
            )
            return
        video = Video(video_data)
        self.summary_edit.setPlainText(video.summary or "Sin resumen disponible.")
        self.transcript_edit.setPlainText(video.transcript or "Sin transcripción disponible.")

    def _ensure_selection(self) -> Optional[int]:
        if self.selected_video_id is None:
            QtWidgets.QMessageBox.information(
                self,
                "Selección requerida",
                "Selecciona un vídeo en la tabla para continuar.",
            )
            return None
        return self.selected_video_id

    def _generate_summary(self) -> None:
        video_id = self._ensure_selection()
        if video_id is None:
            return

        if self._summary_thread and self._summary_thread.isRunning():
            QtWidgets.QMessageBox.information(
                self, "Proceso en curso", "Ya se está generando un resumen."
            )
            return

        self.generate_summary_button.setEnabled(False)
        self._summary_thread = QtCore.QThread(self)
        self._summary_worker = SummaryWorker(self.db_manager, video_id)
        self._summary_worker.moveToThread(self._summary_thread)

        self._summary_thread.started.connect(self._summary_worker.run)  # type: ignore[arg-type]
        self._summary_worker.finished.connect(self._on_summary_finished)
        self._summary_worker.failed.connect(self._on_summary_failed)
        self._summary_worker.finished.connect(self._summary_thread.quit)
        self._summary_worker.failed.connect(self._summary_thread.quit)
        self._summary_worker.finished.connect(self._summary_worker.deleteLater)
        self._summary_worker.failed.connect(self._summary_worker.deleteLater)
        self._summary_thread.finished.connect(self._summary_thread.deleteLater)
        self._summary_thread.start()

    def _on_summary_finished(self, summary: str) -> None:
        self.generate_summary_button.setEnabled(True)
        self.summary_edit.setPlainText(summary)
        QtWidgets.QMessageBox.information(
            self, "Resumen generado", "El resumen se generó correctamente."
        )
        self.data_changed.emit()

    def _on_summary_failed(self, message: str) -> None:
        self.generate_summary_button.setEnabled(True)
        QtWidgets.QMessageBox.critical(self, "Error", message)

    def _copy_to_clipboard(self, text: str) -> None:
        if not text.strip():
            QtWidgets.QMessageBox.information(
                self, "Sin contenido", "No hay texto para copiar."
            )
            return
        QtWidgets.QApplication.clipboard().setText(text)
        QtWidgets.QMessageBox.information(self, "Copiado", "Texto copiado al portapapeles.")

    def _delete_video(self) -> None:
        video_id = self._ensure_selection()
        if video_id is None:
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Eliminar vídeo",
            "¿Estás seguro de que deseas eliminar el vídeo seleccionado?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return
        self.db_manager.delete_video(video_id)
        QtWidgets.QMessageBox.information(
            self,
            "Vídeo eliminado",
            "El vídeo se eliminó correctamente.",
        )
        self.data_changed.emit()
        self.refresh_table()
