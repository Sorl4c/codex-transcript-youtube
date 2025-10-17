"""
Main window composition for the IoT dashboard demo.
"""
from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QBrush
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
    QSpacerItem,
)

from .charts import BarChartWidget, LineChartWidget
from .data_manager import DataManager, SensorReading
from .widgets import CircularProgress, CustomSlider


class MainWindow(QMainWindow):
    """Assembles the navigation menu, stacked pages, and content widgets."""

    NAV_ITEMS = [
        ("dashboard", "Panel"),
        ("devices", "Dispositivos"),
        ("sensors", "Sensores"),
        ("charts", "Gráficas"),
        ("reports", "Reportes"),
        ("settings", "Configuración"),
        ("help", "Ayuda"),
    ]

    SENSOR_ORDER = ["temperatura", "humedad", "co2", "luz"]

    def __init__(self, data_manager: DataManager) -> None:
        super().__init__()
        self.data_manager = data_manager
        self.data_manager.load()

        self.setWindowTitle("Dashboard IoT Moderno")
        self.resize(1280, 840)

        self.navigation_buttons: Dict[str, QPushButton] = {}
        self.sensor_gauges: Dict[str, CircularProgress] = {}
        self.sensor_value_labels: Dict[str, QLabel] = {}
        self.sensor_sliders: Dict[str, CustomSlider] = {}

        self._configure_palette()
        self._apply_stylesheet()
        self._build_ui()

    # -- UI assembly ----------------------------------------------------------
    def _configure_palette(self) -> None:
        palette = self.palette()
        base_color = QColor("#1F2747")
        palette.setColor(QPalette.ColorRole.Window, base_color)
        palette.setColor(QPalette.ColorRole.Base, QColor("#222A4B"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#253058"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#F0F4FF"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#D6DBF5"))
        self.setPalette(palette)

    def _apply_stylesheet(self) -> None:
        style_path = Path(__file__).resolve().parents[1] / "ui" / "styles" / "dashboard.css"
        if style_path.exists():
            try:
                stylesheet = style_path.read_text(encoding="utf-8")
            except OSError:
                return
            self.setStyleSheet(self.styleSheet() + "\n" + stylesheet)

    def _build_ui(self) -> None:
        container = QWidget()
        root_layout = QHBoxLayout(container)
        root_layout.setContentsMargins(0, 0, 0, 0)

        nav_frame = self._build_navigation()
        root_layout.addWidget(nav_frame)

        self.stack = QStackedWidget()
        self.stack.setObjectName("stackedPages")
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(container)

        # Build pages
        dashboard_page = self._create_dashboard_page()
        devices_page = self._create_devices_page()
        self.pages: Dict[str, QWidget] = {
            "dashboard": dashboard_page,
            "devices": devices_page,
            "sensors": self._create_placeholder_page("Sensores"),
            "charts": self._create_placeholder_page("Gráficas"),
            "reports": self._create_placeholder_page("Reportes"),
            "settings": self._create_placeholder_page("Configuración"),
            "help": self._create_placeholder_page("Ayuda"),
        }

        for key, _ in self.NAV_ITEMS:
            self.stack.addWidget(self.pages[key])

        self._switch_page("dashboard")

    def _build_navigation(self) -> QFrame:
        nav_frame = QFrame()
        nav_frame.setFixedWidth(200)
        nav_frame.setStyleSheet(
            """
            QFrame {
                background-color: #293567;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
            QPushButton {
                background-color: transparent;
                color: #E4E8FF;
                text-align: left;
                padding: 10px 18px;
                border-radius: 12px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QPushButton:checked {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe
                );
                color: #0F1737;
                font-weight: 600;
            }
            """
        )

        layout = QVBoxLayout(nav_frame)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(12)

        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 600;")
        layout.addWidget(title_label)

        layout.addSpacing(12)

        for key, text in self.NAV_ITEMS:
            button = QPushButton(text)
            button.setCheckable(True)
            button.clicked.connect(partial(self._switch_page, key))
            layout.addWidget(button)
            self.navigation_buttons[key] = button

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        footer = QLabel("IoT Control\nv0.1")
        footer.setStyleSheet("color: rgba(255, 255, 255, 0.45); font-size: 12px;")
        layout.addWidget(footer)

        return nav_frame

    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        header = self._build_header_bar()
        layout.addWidget(header)

        sensors_frame = self._build_sensor_grid()
        layout.addWidget(sensors_frame)

        charts_row = self._build_charts_row()
        layout.addLayout(charts_row)

        sliders_frame = self._build_sensor_sliders()
        layout.addWidget(sliders_frame)

        return page

    def _build_header_bar(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: rgba(41, 53, 103, 0.6);
                border-radius: 18px;
            }
            QLineEdit {
                background-color: #20284B;
                border-radius: 12px;
                padding: 10px 16px;
                color: #F0F4FF;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QPushButton {
                background-color: rgba(79, 172, 254, 0.2);
                border-radius: 12px;
                padding: 10px 18px;
                color: #E4E8FF;
                border: 1px solid rgba(79, 172, 254, 0.25);
            }
            QPushButton:hover {
                background-color: rgba(79, 172, 254, 0.35);
            }
            """
        )

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar dispositivos o sensores...")
        layout.addWidget(search_input, 1)

        search_button = QPushButton("Buscar")
        notifications_button = QPushButton("Notificaciones")
        layout.addWidget(search_button)
        layout.addWidget(notifications_button)

        return frame

    def _build_sensor_grid(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #222A4B;
                border-radius: 20px;
            }
            QLabel {
                color: #D6DBF5;
            }
            """
        )

        grid = QGridLayout(frame)
        grid.setContentsMargins(18, 18, 18, 18)
        grid.setSpacing(18)

        gradients = {
            "temperatura": (QColor("#F45C43"), QColor("#FF6B6B")),
            "humedad": (QColor("#4facfe"), QColor("#00f2fe")),
            "co2": (QColor("#43e97b"), QColor("#38f9d7")),
            "luz": (QColor("#fdfc47"), QColor("#24fe41")),
        }

        for index, key in enumerate(self.SENSOR_ORDER):
            sensor = self.data_manager.get_sensor(key)
            if sensor is None:
                continue
            card = self._build_sensor_card(key, sensor, gradients.get(key))
            row, col = divmod(index, 2)
            grid.addWidget(card, row, col)

        return frame

    def _build_sensor_card(
        self,
        key: str,
        sensor: SensorReading,
        gradient: tuple[QColor, QColor] | None,
    ) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #293567;
                border-radius: 18px;
            }
            QLabel {
                color: #E4E8FF;
            }
            """
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel(sensor.name)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        progress = CircularProgress(diameter=140, thickness=14)
        if gradient:
            progress.set_gradient(*gradient)
        progress.set_value(sensor.as_percentage())
        layout.addWidget(progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        value_label = QLabel(f"{sensor.value:.1f} {sensor.unit}")
        value_label.setStyleSheet("color: #A7B0D8; font-size: 13px;")
        layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.sensor_gauges[key] = progress
        self.sensor_value_labels[key] = value_label

        return frame

    def _build_charts_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(18)

        self.line_chart = LineChartWidget()
        self.line_chart.plot_series(self.data_manager.get_activity_series())
        line_card = self._wrap_in_card(self.line_chart)

        self.bar_chart = BarChartWidget()
        self.bar_chart.plot_items(self.data_manager.get_consumption_items())
        bar_card = self._wrap_in_card(self.bar_chart)

        layout.addWidget(line_card, 1)
        layout.addWidget(bar_card, 1)
        return layout

    def _build_sensor_sliders(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #222A4B;
                border-radius: 20px;
            }
            """
        )
        layout = QGridLayout(frame)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        for index, key in enumerate(self.SENSOR_ORDER):
            sensor = self.data_manager.get_sensor(key)
            if sensor is None:
                continue

            slider = CustomSlider(sensor.name, minimum=0, maximum=100)
            slider.set_formatter(
                lambda percentage, s=sensor: self._format_sensor_value_from_percentage(
                    s, percentage
                )
            )
            slider.set_value(int(round(sensor.as_percentage())))
            slider.valueChanged.connect(partial(self._on_sensor_slider_changed, key))

            row, col = divmod(index, 2)
            layout.addWidget(slider, row, col)
            self.sensor_sliders[key] = slider

        return frame

    def _create_devices_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        table_frame = self._wrap_in_card(self._build_devices_table())
        layout.addWidget(table_frame)

        calendar_frame = self._wrap_in_card(self._build_calendar())
        layout.addWidget(calendar_frame)

        controls_frame = self._wrap_in_card(self._build_device_controls())
        layout.addWidget(controls_frame)

        return page

    def _build_devices_table(self) -> QWidget:
        table = QTableWidget()
        headers = ["Dispositivo", "Ubicación", "Estado", "Batería (%)", "Consumo (W)"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setStyleSheet(
            """
            QTableWidget {
                background-color: #222A4B;
                alternate-background-color: #253058;
                color: #E4E8FF;
                gridline-color: rgba(255,255,255,0.08);
            }
            QHeaderView::section {
                background-color: #293567;
                color: #F0F4FF;
                padding: 8px;
                border: none;
            }
            """
        )

        devices = self.data_manager.devices
        table.setRowCount(len(devices))
        for row, device in enumerate(devices):
            table.setItem(row, 0, QTableWidgetItem(device.get("dispositivo", "")))
            table.setItem(row, 1, QTableWidgetItem(device.get("ubicacion", "")))
            estado_item = QTableWidgetItem(device.get("estado", ""))
            battery = int(device.get("bateria", 0))
            consumo = float(device.get("consumo", 0.0))
            bateria_item = QTableWidgetItem(f"{battery}")
            consumo_item = QTableWidgetItem(f"{consumo:.1f}")

            color = self._battery_color(battery)
            brush = QBrush(color)
            estado_item.setBackground(brush)
            bateria_item.setBackground(brush)

            for item in (estado_item, bateria_item, consumo_item):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            table.setItem(row, 2, estado_item)
            table.setItem(row, 3, bateria_item)
            table.setItem(row, 4, consumo_item)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def _build_calendar(self) -> QWidget:
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setStyleSheet(
            """
            QCalendarWidget QWidget {
                background-color: #222A4B;
                color: #E4E8FF;
            }
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: rgba(79, 172, 254, 0.4);
                selection-color: #0F1737;
                gridline-color: rgba(255,255,255,0.05);
            }
            """
        )
        return calendar

    def _build_device_controls(self) -> QWidget:
        frame = QWidget()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        label = QLabel("Control de dispositivos (demo)")
        label.setStyleSheet("color: #D6DBF5; font-weight: 600;")
        layout.addWidget(label)

        for device in self.data_manager.devices:
            control = CustomSlider(device.get("dispositivo", "Dispositivo"))
            control.set_formatter(lambda v: f"{v}% de potencia")
            control.set_value(100)
            layout.addWidget(control)

        return frame

    def _create_placeholder_page(self, title: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        placeholder = QLabel(f"{title} estará disponible próximamente.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #A7B0D8; font-size: 16px;")
        layout.addWidget(placeholder, alignment=Qt.AlignmentFlag.AlignCenter)
        return page

    def _wrap_in_card(self, widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #222A4B;
                border-radius: 20px;
            }
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addWidget(widget)
        return frame

    # -- Interaction handlers --------------------------------------------------
    def _switch_page(self, key: str) -> None:
        button = self.navigation_buttons.get(key)
        if button is not None:
            button.setChecked(True)
        for other_key, other_button in self.navigation_buttons.items():
            if other_key != key:
                other_button.setChecked(False)

        index = list(self.pages.keys()).index(key)
        self.stack.setCurrentIndex(index)

    def _on_sensor_slider_changed(self, key: str, percentage: int) -> None:
        value = self.data_manager.set_sensor_percentage(key, percentage)
        sensor = self.data_manager.get_sensor(key)
        if sensor is None:
            return
        gauge = self.sensor_gauges.get(key)
        if gauge:
            gauge.set_value(sensor.as_percentage())
        label = self.sensor_value_labels.get(key)
        if label:
            label.setText(f"{value:.1f} {sensor.unit}")

    # -- Helpers ----------------------------------------------------------------
    @staticmethod
    def _battery_color(value: int) -> QColor:
        if value >= 70:
            return QColor(67, 233, 123, 160)
        if value >= 30:
            return QColor(255, 193, 7, 160)
        return QColor(244, 62, 62, 160)

    @staticmethod
    def _format_sensor_value_from_percentage(sensor: SensorReading, percentage: int) -> str:
        temp_value = sensor.minimum + (sensor.maximum - sensor.minimum) * (percentage / 100.0)
        if sensor.unit.lower() in {"°c", "c", "lux"}:
            return f"{temp_value:.1f} {sensor.unit}"
        if sensor.unit.lower() in {"ppm", "%"}:
            return f"{temp_value:.0f} {sensor.unit}"
        return f"{temp_value:.2f} {sensor.unit}"
