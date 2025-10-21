#!/usr/bin/env python3
"""
Modern UI Showcase - PySide6 Complete Application
Aplicación demo completa que integra todas las técnicas modernas de UI
"""

import sys
import os
from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QSlider,
                               QComboBox, QGroupBox, QScrollArea, QFrame,
                               QStackedWidget, QSplitter, QTabWidget,
                               QGraphicsOpacityEffect, QProgressBar,
                               QLineEdit, QTextEdit, QSpinBox, QCheckBox,
                               QRadioButton, QButtonGroup)
from PySide6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve,
                          QRect, pyqtSignal, QParallelAnimationGroup,
                          QSequentialAnimationGroup, QThread, Signal, Slot)
from PySide6.QtGui import (QPalette, QColor, QFont, QLinearGradient,
                           QRadialGradient, QPainter, QBrush, QPen,
                           QIcon, QPixmap, QMouseEvent, QPaintEvent)

# Importar nuestros componentes personalizados
from modern_components import (ModernButton, ModernCard, ModernInput,
                              ModernProgressBar, ModernBadge, ModernTabBar)
from dynamic_theming import (ThemeManager, ThemeAwareButton, ThemeAwareCard,
                           ThemedWidget, ThemeType)
from modern_effects_demo import (GlassmorphismWidget, AnimatedBackground,
                                FloatingButton, ModernCard as EffectsCard)

class DashboardMetrics(QWidget):
    """Widget de métricas del dashboard con animaciones"""

    def __init__(self, title: str, value: str, change: str, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui(title, value, change)
        self.apply_theme()

    def setup_ui(self, title: str, value: str, change: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        layout.addWidget(title_label)

        # Valor principal
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 28, QFont.Bold))
        layout.addWidget(value_label)

        # Cambio
        change_label = QLabel(change)
        change_label.setFont(QFont("Arial", 10))
        layout.addWidget(change_label)

        # Guardar referencias
        self.title_label = title_label
        self.value_label = value_label
        self.change_label = change_label

    def apply_theme(self):
        """Aplica el tema actual"""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()
        colors = theme.get("colors", {})

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('surface', '#F8F9FA')};
                border: 1px solid {colors.get('border', '#DEE2E6')};
                border-radius: 12px;
            }}
            QLabel {{
                color: {colors.get('text_primary', '#212529')};
            }}
        """)

class ActivityFeedWidget(QWidget):
    """Feed de actividades con animaciones suaves"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.activities = []
        self.setup_ui()
        self.add_sample_activities()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Recent Activity")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Feed de actividades
        self.feed_layout = QVBoxLayout()
        self.feed_layout.setSpacing(10)
        layout.addLayout(self.feed_layout)

        layout.addStretch()

    def add_sample_activities(self):
        """Agrega actividades de ejemplo"""
        activities = [
            ("User Login", "John Doe logged in", "2 minutes ago"),
            ("File Upload", "report.pdf uploaded successfully", "15 minutes ago"),
            ("Task Completed", "Data processing finished", "1 hour ago"),
            ("System Update", "New features deployed", "3 hours ago")
        ]

        for title, description, time in activities:
            self.add_activity(title, description, time)

    def add_activity(self, title: str, description: str, time: str):
        """Agrega una nueva actividad al feed"""
        activity_card = QWidget()
        activity_card.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(12, 12, 12, 12)
        activity_layout.setSpacing(4)

        # Título de actividad
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        activity_layout.addWidget(title_label)

        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #666666;")
        activity_layout.addWidget(desc_label)

        # Tiempo
        time_label = QLabel(time)
        time_label.setFont(QFont("Arial", 9))
        time_label.setStyleSheet("color: #999999;")
        activity_layout.addWidget(time_label)

        # Animación de entrada
        activity_card.setFixedHeight(0)
        self.feed_layout.addWidget(activity_card)

        # Animar entrada
        self.animate_activity_entry(activity_card)

        self.activities.append(activity_card)

    def animate_activity_entry(self, widget):
        """Anima la entrada de una nueva actividad"""
        animation = QPropertyAnimation(widget, b"maximumHeight")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(widget.sizeHint().height())
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()

class InteractiveChartsWidget(QWidget):
    """Widget con gráficos interactivos básicos"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("Performance Overview")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Chart canvas (simplificado)
        self.chart_canvas = ChartCanvas(self.theme_manager)
        layout.addWidget(self.chart_canvas)

        # Controles del chart
        controls_layout = QHBoxLayout()

        refresh_btn = ModernButton("Refresh", 'primary', 'small')
        refresh_btn.clicked.connect(self.refresh_chart)
        controls_layout.addWidget(refresh_btn)

        period_combo = QComboBox()
        period_combo.addItems(["Last 7 days", "Last 30 days", "Last 3 months"])
        controls_layout.addWidget(period_combo)

        layout.addLayout(controls_layout)

    def refresh_chart(self):
        """Refresca los datos del chart"""
        self.chart_canvas.generate_random_data()
        self.chart_canvas.update()

class ChartCanvas(QWidget):
    """Canvas simplificado para renderizar gráficos"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setFixedHeight(200)
        self.generate_random_data()

    def generate_random_data(self):
        """Genera datos aleatorios para el demo"""
        import random
        self.data = [random.randint(10, 100) for _ in range(7)]

    def paintEvent(self, event):
        """Dibuja el gráfico"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Obtener colores del tema
        primary_color = QColor("#2196F3")
        if self.theme_manager:
            primary_color = QColor(self.theme_manager.get_color("primary"))

        # Fondo
        painter.fillRect(self.rect(), QColor(250, 250, 250))

        # Dibujar barras simples
        bar_width = self.width() / len(self.data)
        max_value = max(self.data)

        for i, value in enumerate(self.data):
            bar_height = (value / max_value) * (self.height() - 40)
            bar_x = i * bar_width + 10
            bar_y = self.height() - bar_height - 20

            # Dibujar barra con gradiente
            gradient = QLinearGradient(bar_x, bar_y, bar_x, bar_y + bar_height)
            gradient.setColorAt(0, primary_color.lighter(150))
            gradient.setColorAt(1, primary_color)

            painter.fillRect(bar_x, bar_y, bar_width - 20, bar_height, gradient)

class ModernUIShowcase(QMainWindow):
    """Aplicación principal de showcase de UI moderna"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern UI Showcase - PySide6")
        self.setGeometry(100, 100, 1400, 900)

        # Inicializar gestor de temas
        self.theme_manager = ThemeManager()
        ThemeManager._instance = self.theme_manager

        # Configurar aplicación
        self.setup_application_style()
        self.setup_ui()
        self.setup_connections()
        self.show_welcome_animation()

    def setup_application_style(self):
        """Configura el estilo base de la aplicación"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def setup_ui(self):
        """Configura la interfaz principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar de navegación
        self.create_sidebar(main_layout)

        # Área principal con tabs
        self.create_main_content(main_layout)

        # Barra de estado flotante
        self.create_floating_actions()

    def create_sidebar(self, parent_layout):
        """Crea la barra lateral de navegación"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                color: white;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)

        # Logo/Título
        logo_label = QLabel("Modern UI")
        logo_label.setFont(QFont("Arial", 20, QFont.Bold))
        logo_label.setStyleSheet("color: white; margin: 20px 0;")
        sidebar_layout.addWidget(logo_label)

        subtitle_label = QLabel("PySide6 Showcase")
        subtitle_label.setStyleSheet("color: #BDC3C7; margin-bottom: 30px;")
        sidebar_layout.addWidget(subtitle_label)

        # Navigation tabs
        self.nav_tabs = ModernTabBar()
        self.nav_tabs.add_tab("Dashboard")
        self.nav_tabs.add_tab("Components")
        self.nav_tabs.add_tab("Effects")
        self.nav_tabs.add_tab("Themes")
        self.nav_tabs.add_tab("Settings")

        # Estilo personalizado para navigation
        self.nav_tabs.setStyleSheet("""
            ModernTabBar {
                background-color: transparent;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 12px 16px;
                border-radius: 8px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background-color: #3498DB;
            }
        """)

        sidebar_layout.addWidget(self.nav_tabs)

        sidebar_layout.addStretch()

        # Theme toggle
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
        """)

        theme_layout.addWidget(self.theme_combo)
        sidebar_layout.addWidget(theme_group)

        parent_layout.addWidget(self.sidebar)

    def create_main_content(self, parent_layout):
        """Crea el área principal de contenido"""
        # Contenedor principal con scroll
        self.main_area = QScrollArea()
        self.main_area.setWidgetResizable(True)
        self.main_area.setStyleSheet("QScrollArea { border: none; }")

        # Stacked widget para diferentes vistas
        self.content_stack = QStackedWidget()
        self.create_dashboard_view()
        self.create_components_view()
        self.create_effects_view()
        self.create_themes_view()
        self.create_settings_view()

        self.main_area.setWidget(self.content_stack)
        parent_layout.addWidget(self.main_area)

    def create_dashboard_view(self):
        """Crea la vista de dashboard"""
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(30, 30, 30, 30)
        dashboard_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Botones de acción
        refresh_btn = ModernButton("Refresh Data", 'primary')
        export_btn = ModernButton("Export", 'secondary')

        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(export_btn)

        dashboard_layout.addLayout(header_layout)

        # Métricas principales
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        metrics_data = [
            ("Total Users", "1,234", "+12% from last month"),
            ("Revenue", "$45,678", "+8% from last month"),
            ("Active Sessions", "89", "-2% from last hour"),
            ("Server Load", "67%", "Normal operation")
        ]

        for title, value, change in metrics_data:
            metric_widget = DashboardMetrics(title, value, change, self.theme_manager)
            metric_widget.setMinimumWidth(250)
            metrics_layout.addWidget(metric_widget)

        dashboard_layout.addLayout(metrics_layout)

        # Contenido principal con splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Panel de actividades
        activity_widget = QWidget()
        activity_layout = QVBoxLayout(activity_widget)
        activity_layout.setContentsMargins(0, 0, 0, 0)

        activity_title = QLabel("Activity Feed")
        activity_title.setFont(QFont("Arial", 16, QFont.Bold))
        activity_layout.addWidget(activity_title)

        self.activity_feed = ActivityFeedWidget(self.theme_manager)
        activity_layout.addWidget(self.activity_feed)

        main_splitter.addWidget(activity_widget)

        # Panel de gráficos
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)

        charts_title = QLabel("Analytics")
        charts_title.setFont(QFont("Arial", 16, QFont.Bold))
        charts_layout.addWidget(charts_title)

        self.charts_widget = InteractiveChartsWidget(self.theme_manager)
        charts_layout.addWidget(self.charts_widget)

        main_splitter.addWidget(charts_widget)

        main_splitter.setSizes([400, 600])
        dashboard_layout.addWidget(main_splitter)

        self.content_stack.addWidget(dashboard_widget)

    def create_components_view(self):
        """Crea la vista de componentes"""
        components_widget = QWidget()
        components_layout = QVBoxLayout(components_widget)
        components_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Modern Components Library")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        components_layout.addWidget(title)

        # Importar y mostrar el demo de componentes
        try:
            from modern_components import ModernComponentsDemo
            demo = ModernComponentsDemo()
            components_layout.addWidget(demo)
        except ImportError:
            error_label = QLabel("Components demo not available")
            components_layout.addWidget(error_label)

        self.content_stack.addWidget(components_widget)

    def create_effects_view(self):
        """Crea la vista de efectos visuales"""
        effects_widget = QWidget()
        effects_layout = QVBoxLayout(effects_widget)
        effects_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Visual Effects Showcase")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        effects_layout.addWidget(title)

        # Demo de efectos
        effects_demo = QWidget()
        effects_demo_layout = QHBoxLayout(effects_demo)

        # Glassmorphism demo
        glass_container = QWidget()
        glass_layout = QVBoxLayout(glass_container)
        glass_layout.addWidget(QLabel("Glassmorphism:"))

        for i in range(3):
            glass_widget = GlassmorphismWidget()
            glass_layout.addWidget(glass_widget)

        effects_demo_layout.addWidget(glass_container)

        # Cards con efectos
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.addWidget(QLabel("Modern Cards:"))

        card_data = [
            ("Animated Entry", "Smooth animations and transitions"),
            ("Shadow Effects", "Dynamic shadows on hover"),
            ("Modern Styling", "Contemporary design patterns")
        ]

        for title, subtitle in card_data:
            card = ModernCard(title, subtitle, 'elevated')
            cards_layout.addWidget(card)

        effects_demo_layout.addWidget(cards_container)

        effects_layout.addWidget(effects_demo)
        self.content_stack.addWidget(effects_widget)

    def create_themes_view(self):
        """Crea la vista de theming"""
        themes_widget = QWidget()
        themes_layout = QVBoxLayout(themes_widget)
        themes_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Dynamic Theming System")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        themes_layout.addWidget(title)

        # Demo de theming
        try:
            from dynamic_theming import DynamicThemingDemo
            demo = DynamicThemingDemo()
            themes_layout.addWidget(demo)
        except ImportError:
            error_label = QLabel("Theming demo not available")
            themes_layout.addWidget(error_label)

        self.content_stack.addWidget(themes_widget)

    def create_settings_view(self):
        """Crea la vista de configuración"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Settings")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        settings_layout.addWidget(title)

        # Opciones de configuración
        settings_group = QGroupBox("Application Settings")
        settings_group_layout = QVBoxLayout(settings_group)

        # Animations
        animations_check = QCheckBox("Enable Animations")
        animations_check.setChecked(True)
        settings_group_layout.addWidget(animations_check)

        # Auto theme
        auto_theme_check = QCheckBox("Auto-switch theme based on system")
        auto_theme_check.setChecked(False)
        settings_group_layout.addWidget(auto_theme_check)

        # Animation speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Animation Speed:"))

        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setRange(100, 1000)
        speed_slider.setValue(300)
        speed_layout.addWidget(speed_slider)

        speed_label = QLabel("300ms")
        speed_layout.addWidget(speed_label)

        settings_group_layout.addLayout(speed_layout)

        settings_layout.addWidget(settings_group)
        settings_layout.addStretch()

        self.content_stack.addWidget(settings_widget)

    def create_floating_actions(self):
        """Crea botones de acción flotantes"""
        # FAB principal
        self.fab = FloatingButton("+")
        self.fab.setParent(self)
        self.fab.move(self.width() - 80, self.height() - 80)
        self.fab.clicked.connect(self.show_quick_actions)

    def setup_connections(self):
        """Configura las conexiones de señales"""
        # Navigation
        self.nav_tabs.tab_changed.connect(self.switch_view)

        # Theme switching
        self.theme_combo.currentTextChanged.connect(self.change_theme)

        # Register widgets for theming
        if self.theme_manager:
            self.theme_manager.register_widget(self)

    def switch_view(self, index):
        """Cambia entre diferentes vistas"""
        self.content_stack.setCurrentIndex(index)

    def change_theme(self, theme_name):
        """Cambia el tema de la aplicación"""
        if theme_name.lower() == "dark":
            self.theme_manager.set_theme("dark")
        else:
            self.theme_manager.set_theme("light")

    def show_welcome_animation(self):
        """Muestra animación de bienvenida"""
        # Animación de entrada suave
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.start()

    def show_quick_actions(self):
        """Muestra acciones rápidas desde el FAB"""
        print("Quick actions menu would appear here")

    def resizeEvent(self, event):
        """Ajusta la posición del FAB al cambiar tamaño"""
        if hasattr(self, 'fab'):
            self.fab.move(self.width() - 80, self.height() - 80)
        super().resizeEvent(event)

def main():
    """Función principal de la aplicación showcase"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Configurar información de la aplicación
    app.setApplicationName("Modern UI Showcase")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PySide6 Examples")

    # Crear y mostrar la ventana principal
    showcase = ModernUIShowcase()
    showcase.show()

    # Iniciar el bucle de eventos
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())