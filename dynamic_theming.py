#!/usr/bin/env python3
"""
Dynamic Theming System for PySide6
Sistema completo de theming dinámico con light/dark mode y transiciones suaves
"""

import sys
import json
from typing import Dict, Any, Optional, Callable
from enum import Enum
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QSlider,
                               QComboBox, QGroupBox, QScrollArea)
from PySide6.QtCore import (Qt, QObject, Signal, Property, QTimer, QEvent,
                          QPropertyAnimation, QEasingCurve, pyqtSignal)
from PySide6.QtGui import (QPalette, QColor, QFont, QLinearGradient,
                           QRadialGradient, QPainter, QBrush)

class ThemeType(Enum):
    """Tipos de temas predefinidos"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Cambia automáticamente con el sistema
    CUSTOM = "custom"

class ThemeManager(QObject):
    """Gestor central de temas dinámicos"""

    theme_changed = Signal(str, dict)  # theme_name, theme_data
    transition_started = Signal()
    transition_finished = Signal()

    def __init__(self):
        super().__init__()
        self.current_theme = ThemeType.LIGHT
        self.themes = self._load_default_themes()
        self.custom_themes = {}
        self.animation_duration = 300
        self.is_transitioning = False
        self.widgets_to_update = []

    def _load_default_themes(self) -> Dict[str, Dict[str, Any]]:
        """Carga los temas predefinidos"""
        return {
            "light": {
                "name": "Light Theme",
                "type": ThemeType.LIGHT.value,
                "colors": {
                    "primary": "#2196F3",
                    "secondary": "#6C757D",
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "danger": "#DC3545",
                    "info": "#17A2B8",
                    "background": "#FFFFFF",
                    "surface": "#F8F9FA",
                    "surface_variant": "#E9ECEF",
                    "text_primary": "#212529",
                    "text_secondary": "#6C757D",
                    "text_disabled": "#ADB5BD",
                    "border": "#DEE2E6",
                    "outline": "#CED4DA",
                    "shadow": "rgba(0, 0, 0, 0.1)",
                    "overlay": "rgba(0, 0, 0, 0.5)"
                },
                "palettes": {
                    "window": "#FFFFFF",
                    "window_text": "#212529",
                    "base": "#FFFFFF",
                    "base_text": "#212529",
                    "alternate_base": "#F8F9FA",
                    "tooltip_base": "#212529",
                    "tooltip_text": "#FFFFFF",
                    "text": "#212529",
                    "button": "#F8F9FA",
                    "button_text": "#212529",
                    "bright_text": "#FF0000",
                    "link": "#2196F3",
                    "highlight": "#2196F3",
                    "highlighted_text": "#FFFFFF"
                },
                "fonts": {
                    "primary_family": "Arial",
                    "secondary_family": "Arial",
                    "mono_family": "Consolas",
                    "size_small": 12,
                    "size_medium": 14,
                    "size_large": 16,
                    "size_xlarge": 18,
                    "weight_normal": 400,
                    "weight_medium": 500,
                    "weight_bold": 700
                },
                "effects": {
                    "shadow_blur": 10,
                    "shadow_spread": 0,
                    "shadow_offset_x": 0,
                    "shadow_offset_y": 2,
                    "border_radius_small": 4,
                    "border_radius_medium": 8,
                    "border_radius_large": 12,
                    "border_radius_xlarge": 16
                }
            },
            "dark": {
                "name": "Dark Theme",
                "type": ThemeType.DARK.value,
                "colors": {
                    "primary": "#90CAF9",
                    "secondary": "#9CA3AF",
                    "success": "#81C784",
                    "warning": "#FFD54F",
                    "danger": "#E57373",
                    "info": "#4FC3F7",
                    "background": "#121212",
                    "surface": "#1E1E1E",
                    "surface_variant": "#2D2D30",
                    "text_primary": "#FFFFFF",
                    "text_secondary": "#B3B3B3",
                    "text_disabled": "#666666",
                    "border": "#3C3C3C",
                    "outline": "#555555",
                    "shadow": "rgba(0, 0, 0, 0.3)",
                    "overlay": "rgba(0, 0, 0, 0.7)"
                },
                "palettes": {
                    "window": "#1E1E1E",
                    "window_text": "#FFFFFF",
                    "base": "#2D2D30",
                    "base_text": "#FFFFFF",
                    "alternate_base": "#1E1E1E",
                    "tooltip_base": "#FFFFFF",
                    "tooltip_text": "#121212",
                    "text": "#FFFFFF",
                    "button": "#2D2D30",
                    "button_text": "#FFFFFF",
                    "bright_text": "#FF0000",
                    "link": "#90CAF9",
                    "highlight": "#90CAF9",
                    "highlighted_text": "#121212"
                },
                "fonts": {
                    "primary_family": "Arial",
                    "secondary_family": "Arial",
                    "mono_family": "Consolas",
                    "size_small": 12,
                    "size_medium": 14,
                    "size_large": 16,
                    "size_xlarge": 18,
                    "weight_normal": 400,
                    "weight_medium": 500,
                    "weight_bold": 700
                },
                "effects": {
                    "shadow_blur": 15,
                    "shadow_spread": 0,
                    "shadow_offset_x": 0,
                    "shadow_offset_y": 4,
                    "border_radius_small": 4,
                    "border_radius_medium": 8,
                    "border_radius_large": 12,
                    "border_radius_xlarge": 16
                }
            }
        }

    def register_widget(self, widget: QWidget):
        """Registra un widget para actualización automática de tema"""
        if widget not in self.widgets_to_update:
            self.widgets_to_update.append(widget)

    def unregister_widget(self, widget: QWidget):
        """Desregistra un widget de la actualización automática"""
        if widget in self.widgets_to_update:
            self.widgets_to_update.remove(widget)

    def set_theme(self, theme_name: str, animated: bool = True):
        """Cambia el tema actual"""
        if theme_name not in self.themes and theme_name not in self.custom_themes:
            return False

        if animated and not self.is_transitioning:
            self._animate_theme_transition(theme_name)
        else:
            self._apply_theme(theme_name)

        return True

    def _animate_theme_transition(self, theme_name: str):
        """Animación de transición entre temas"""
        self.is_transitioning = True
        self.transition_started.emit()

        # Crear animaciones de fade para todos los widgets registrados
        animations = []
        for widget in self.widgets_to_update:
            fade_out = QPropertyAnimation(widget, b"windowOpacity")
            fade_out.setDuration(self.animation_duration // 2)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.7)
            fade_out.setEasingCurve(QEasingCurve.InOutQuad)
            animations.append(fade_out)

        # Ejecutar fade out
        for animation in animations:
            animation.start()

        # Cambiar tema después del fade out
        QTimer.singleShot(self.animation_duration // 2,
                         lambda: self._complete_theme_transition(theme_name))

    def _complete_theme_transition(self, theme_name: str):
        """Completa la transición del tema"""
        self._apply_theme(theme_name)

        # Animar fade in
        animations = []
        for widget in self.widgets_to_update:
            fade_in = QPropertyAnimation(widget, b"windowOpacity")
            fade_in.setDuration(self.animation_duration // 2)
            fade_in.setStartValue(0.7)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutQuad)
            animations.append(fade_in)

        for animation in animations:
            animation.start()

        # Finalizar transición
        QTimer.singleShot(self.animation_duration // 2,
                         lambda: self._finish_transition())

    def _apply_theme(self, theme_name: str):
        """Aplica un tema a la aplicación"""
        theme_data = self.themes.get(theme_name) or self.custom_themes.get(theme_name)
        if not theme_data:
            return

        # Actualizar paleta de la aplicación
        self._update_application_palette(theme_data)

        # Actualizar widgets registrados
        for widget in self.widgets_to_update:
            self._update_widget_theme(widget, theme_data)

        self.current_theme = ThemeType(theme_data["type"])
        self.theme_changed.emit(theme_name, theme_data)

    def _update_application_palette(self, theme_data: Dict[str, Any]):
        """Actualiza la paleta de la aplicación"""
        app = QApplication.instance()
        if not app:
            return

        palette = QPalette()

        # Configurar colores desde el tema
        palettes = theme_data.get("palettes", {})

        # Mapeo de colores de tema a paleta Qt
        color_mappings = {
            "window": QPalette.Window,
            "window_text": QPalette.WindowText,
            "base": QPalette.Base,
            "base_text": QPalette.Text,
            "alternate_base": QPalette.AlternateBase,
            "tooltip_base": QPalette.ToolTipBase,
            "tooltip_text": QPalette.ToolTipText,
            "text": QPalette.Text,
            "button": QPalette.Button,
            "button_text": QPalette.ButtonText,
            "bright_text": QPalette.BrightText,
            "link": QPalette.Link,
            "highlight": QPalette.Highlight,
            "highlighted_text": QPalette.HighlightedText
        }

        for color_name, color_value in palettes.items():
            if color_name in color_mappings:
                palette.setColor(color_mappings[color_name], QColor(color_value))

        app.setPalette(palette)

    def _update_widget_theme(self, widget: QWidget, theme_data: Dict[str, Any]):
        """Actualiza el tema de un widget específico"""
        # Este método puede ser sobreescrito por widgets personalizados
        # para implementar estilos específicos
        pass

    def _finish_transition(self):
        """Finaliza la transición del tema"""
        self.is_transitioning = False
        self.transition_finished.emit()

    def get_current_theme(self) -> Dict[str, Any]:
        """Obtiene los datos del tema actual"""
        theme_name = self.current_theme.value
        return self.themes.get(theme_name, {})

    def get_color(self, color_name: str) -> str:
        """Obtiene un color del tema actual"""
        theme = self.get_current_theme()
        return theme.get("colors", {}).get(color_name, "#000000")

    def add_custom_theme(self, name: str, theme_data: Dict[str, Any]):
        """Agrega un tema personalizado"""
        self.custom_themes[name] = theme_data

    def export_theme(self, theme_name: str, file_path: str):
        """Exporta un tema a un archivo JSON"""
        theme_data = self.themes.get(theme_name) or self.custom_themes.get(theme_name)
        if theme_data:
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=2)

    def import_theme(self, file_path: str, theme_name: str):
        """Importa un tema desde un archivo JSON"""
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
            self.add_custom_theme(theme_name, theme_data)
            return True
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False

class ThemedWidget(QWidget):
    """Widget base con soporte para theming"""

    def __init__(self, theme_manager: Optional[ThemeManager] = None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager or ThemeManager.instance()
        if self.theme_manager:
            self.theme_manager.register_widget(self)

    def update_theme(self, theme_data: Dict[str, Any]):
        """Método para actualizar el tema del widget"""
        # Implementar en subclases específicas
        pass

    def get_theme_color(self, color_name: str) -> str:
        """Obtiene un color del tema actual"""
        if self.theme_manager:
            return self.theme_manager.get_color(color_name)
        return "#000000"

    def apply_theme_style(self, style_template: str, **kwargs) -> str:
        """Aplica un estilo de tema con variables"""
        theme_colors = {}
        if self.theme_manager:
            theme_data = self.theme_manager.get_current_theme()
            theme_colors = theme_data.get("colors", {})

        # Reemplazar variables en el estilo
        style = style_template
        for key, value in {**theme_colors, **kwargs}.items():
            style = style.replace(f"${key}", value)

        return style

class ThemeAwareButton(ThemedWidget, QPushButton):
    """Botón con soporte para theming automático"""

    def __init__(self, text: str, style_type: str = "primary",
                 theme_manager: Optional[ThemeManager] = None, parent=None):
        ThemedWidget.__init__(self, theme_manager, parent)
        QPushButton.__init__(self, text, parent)
        self.style_type = style_type
        self.update_style()

    def update_style(self):
        """Actualiza el estilo del botón según el tema"""
        style_template = f"""
            QPushButton {{
                background-color: $primary;
                color: $text_primary;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: $primary;
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                background-color: $primary;
                opacity: 0.6;
            }}
            QPushButton:disabled {{
                background-color: $outline;
                color: $text_disabled;
            }}
        """

        self.setStyleSheet(self.apply_theme_style(style_template))

class ThemeAwareCard(ThemedWidget):
    """Card con soporte para theming automático"""

    def __init__(self, title: str = "", subtitle: str = "",
                 theme_manager: Optional[ThemeManager] = None, parent=None):
        super().__init__(theme_manager, parent)
        self.title = title
        self.subtitle = subtitle
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        """Configura la UI del card"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            layout.addWidget(title_label)

        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setFont(QFont("Arial", 12))
            subtitle_label.setStyleSheet("color: $text_secondary;")
            layout.addWidget(subtitle_label)

    def update_style(self):
        """Actualiza el estilo del card según el tema"""
        style_template = f"""
            ThemeAwareCard {{
                background-color: $surface;
                border: 1px solid $border;
                border-radius: 12px;
            }}
            QLabel {{
                color: $text_primary;
            }}
        """

        self.setStyleSheet(self.apply_theme_style(style_template))

class DynamicThemingDemo(QMainWindow):
    """Demostración del sistema de theming dinámico"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Theming System Demo")
        self.setGeometry(100, 100, 1200, 800)

        # Crear gestor de temas
        self.theme_manager = ThemeManager()
        ThemeManager._instance = self.theme_manager  # Singleton

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Panel de control de temas
        self.create_theme_controls(main_layout)

        # Área de demostración
        self.create_demo_area(main_layout)

    def create_theme_controls(self, parent_layout):
        """Crea los controles de theming"""
        controls_group = QGroupBox("Theme Controls")
        controls_layout = QHBoxLayout(controls_group)

        # Selector de tema
        theme_combo = QComboBox()
        theme_combo.addItems(["light", "dark"])
        theme_combo.currentTextChanged.connect(self.on_theme_changed)

        controls_layout.addWidget(QLabel("Theme:"))
        controls_layout.addWidget(theme_combo)

        # Botón de toggle rápido
        toggle_btn = QPushButton("Toggle Theme")
        toggle_btn.clicked.connect(self.toggle_theme)
        controls_layout.addWidget(toggle_btn)

        # Slider de duración de animación
        controls_layout.addWidget(QLabel("Animation Duration:"))
        duration_slider = QSlider(Qt.Horizontal)
        duration_slider.setRange(100, 1000)
        duration_slider.setValue(300)
        duration_slider.valueChanged.connect(self.on_animation_duration_changed)
        controls_layout.addWidget(duration_slider)

        duration_label = QLabel("300ms")
        controls_layout.addWidget(duration_label)

        parent_layout.addWidget(controls_group)

    def create_demo_area(self, parent_layout):
        """Crea el área de demostración de componentes con tema"""
        demo_group = QGroupBox("Themed Components")
        demo_layout = QVBoxLayout(demo_group)

        # Título
        title = QLabel("Themed Components Demo")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        demo_layout.addWidget(title)

        # Grid de componentes
        grid_layout = QHBoxLayout()

        # Columna 1 - Botones
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Buttons:"))

        for style_type in ["primary", "secondary", "success", "danger"]:
            btn = ThemeAwareButton(f"{style_type.capitalize()} Button",
                                   style_type, self.theme_manager)
            col1.addWidget(btn)

        grid_layout.addLayout(col1)

        # Columna 2 - Cards
        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Cards:"))

        card1 = ThemeAwareCard("Primary Card",
                               "This card adapts to the current theme automatically",
                               self.theme_manager)
        col2.addWidget(card1)

        card2 = ThemeAwareCard("Secondary Card",
                               "Another themed card with consistent styling",
                               self.theme_manager)
        col2.addWidget(card2)

        grid_layout.addLayout(col2)

        demo_layout.addLayout(grid_layout)
        parent_layout.addWidget(demo_group)

    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.theme_manager.theme_changed.connect(self.on_theme_changed_signal)

    def on_theme_changed(self, theme_name: str):
        """Maneja el cambio de tema desde el combo box"""
        self.theme_manager.set_theme(theme_name)

    def toggle_theme(self):
        """Alterna entre temas light y dark"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == ThemeType.LIGHT else "light"
        self.theme_manager.set_theme(new_theme)

    def on_animation_duration_changed(self, duration: int):
        """Cambia la duración de la animación de transición"""
        self.theme_manager.animation_duration = duration

    def on_theme_changed_signal(self, theme_name: str, theme_data: Dict[str, Any]):
        """Señal emitida cuando cambia el tema"""
        print(f"Theme changed to: {theme_name}")

def main():
    """Función principal de demostración"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    demo = DynamicThemingDemo()
    demo.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()