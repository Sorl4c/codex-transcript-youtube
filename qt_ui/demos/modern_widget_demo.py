"""
Mini demo of a modern-looking dashboard using QtWidgets + Qt Style Sheets.
Run standalone with:
    PYTHONPATH=. python qt_ui/demos/modern_widget_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets


CARD_STYLE = """
QFrame#card {
    background-color: rgba(36, 37, 43, 190);
    border-radius: 16px;
    border: 1px solid rgba(90, 132, 255, 40);
    color: #f7f7f7;
}

QLabel#title {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#metricLabel {
    font-size: 14px;
    color: #cdd7ff;
}

QLabel#metricValue {
    font-size: 32px;
    font-weight: 700;
    color: #8ec5ff;
}

QPushButton#pillButton {
    background-color: rgba(78, 115, 255, 180);
    border-radius: 20px;
    padding: 10px 24px;
    color: #fdfdfd;
    font-weight: 600;
}

QPushButton#pillButton:hover {
    background-color: rgba(108, 145, 255, 220);
}
"""


MAIN_STYLESHEET = """
QWidget {
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #1f1f2f, stop:1 #12121c
    );
    color: #f0f4ff;
    font-family: "Inter", "Segoe UI", sans-serif;
}

QLabel {
    font-size: 13px;
}

QProgressBar {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    text-align: center;
    height: 18px;
    color: #0b0d17;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #6f8dff, stop:1 #4ac7ff
    );
    border-radius: 10px;
}

QListWidget {
    background-color: transparent;
    border: none;
    color: #dbe4ff;
    font-size: 14px;
}

QListWidget::item {
    padding: 8px 6px;
}

QListWidget::item:selected {
    background-color: rgba(120, 158, 255, 60);
    border-radius: 8px;
}
"""


def build_card(title: str, metric: str, subtext: str) -> QtWidgets.QFrame:
    card = QtWidgets.QFrame()
    card.setObjectName("card")
    card.setStyleSheet(CARD_STYLE)
    layout = QtWidgets.QVBoxLayout(card)
    header = QtWidgets.QLabel(title)
    header.setObjectName("title")
    layout.addWidget(header)

    metric_value = QtWidgets.QLabel(metric)
    metric_value.setObjectName("metricValue")
    layout.addWidget(metric_value, alignment=QtCore.Qt.AlignLeft)

    metric_label = QtWidgets.QLabel(subtext)
    metric_label.setObjectName("metricLabel")
    layout.addWidget(metric_label)

    layout.addStretch(1)
    return card


class ModernDashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern PySide6 Dashboard")
        self.resize(1080, 720)

        central = QtWidgets.QWidget()
        central.setStyleSheet(MAIN_STYLESHEET)
        self.setCentralWidget(central)

        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)

        header_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Resumen diario")
        title.setObjectName("title")
        header_layout.addWidget(title)
        header_layout.addStretch(1)

        action_btn = QtWidgets.QPushButton("Ver reportes")
        action_btn.setObjectName("pillButton")
        action_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        header_layout.addWidget(action_btn)
        main_layout.addLayout(header_layout)

        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.addWidget(build_card("Videos procesados", "128", "+24% vs ayer"))
        cards_layout.addWidget(build_card("Resúmenes generados", "64", "+12% vs promedio"))
        cards_layout.addWidget(build_card("Consultas RAG", "483", "Top-3 precisión 92%"))
        main_layout.addLayout(cards_layout)

        activity_card = QtWidgets.QFrame()
        activity_card.setObjectName("card")
        activity_card.setStyleSheet(CARD_STYLE)
        activity_layout = QtWidgets.QVBoxLayout(activity_card)
        activity_layout.addWidget(QtWidgets.QLabel("Actividad reciente"), alignment=QtCore.Qt.AlignTop)

        list_widget = QtWidgets.QListWidget()
        for text in [
            "10:24 · Ingestado 'TensorFlow Agents'",
            "10:12 · Generado resumen 'Curso LangChain'",
            "09:58 · Consulta RAG 'mejores prompts visión'",
            "09:41 · Eliminado video duplicado",
            "09:12 · Ingestado 'PySide6 modern UI'",
        ]:
            list_widget.addItem(text)
        activity_layout.addWidget(list_widget)

        progress_container = QtWidgets.QWidget()
        progress_layout = QtWidgets.QGridLayout(progress_container)
        progress_layout.setVerticalSpacing(12)

        progress_layout.addWidget(QtWidgets.QLabel("Procesamiento diario"), 0, 0)
        processing_bar = QtWidgets.QProgressBar()
        processing_bar.setValue(72)
        progress_layout.addWidget(processing_bar, 0, 1)

        progress_layout.addWidget(QtWidgets.QLabel("Cobertura RAG"), 1, 0)
        rag_bar = QtWidgets.QProgressBar()
        rag_bar.setValue(86)
        progress_layout.addWidget(rag_bar, 1, 1)

        progress_layout.addWidget(QtWidgets.QLabel("Calidad de resúmenes"), 2, 0)
        summary_bar = QtWidgets.QProgressBar()
        summary_bar.setValue(94)
        progress_layout.addWidget(summary_bar, 2, 1)

        activity_layout.addWidget(progress_container)
        main_layout.addWidget(activity_card, stretch=1)


def main() -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    # Attempt to register a custom font if bundled alongside this script.
    font_path = Path(__file__).with_name("Inter-SemiBold.ttf")
    if font_path.exists():
        QtGui.QFontDatabase.addApplicationFont(str(font_path))

    window = ModernDashboard()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
