#!/usr/bin/env python3
"""
Modern UI Components Library for PySide6
Componentes personalizados modernos y reutilizables
"""

import sys
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QFrame, QSlider, QProgressBar, QLineEdit,
                               QComboBox, QSpinBox, QCheckBox, QGroupBox,
                               QScrollArea, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer,
                          QRect, pyqtSignal, QParallelAnimationGroup,
                          QSequentialAnimationGroup, QEvent)
from PySide6.QtGui import (QPainter, QColor, QLinearGradient, QRadialGradient,
                           QPen, QBrush, QFont, QPalette, QMouseEvent,
                           QEnterEvent, QPaintEvent, QResizeEvent)

class ModernButton(QPushButton):
    """Botón moderno con múltiples estilos y animaciones"""

    # Estilos predefinidos
    STYLES = {
        'primary': {'bg': '#2196F3', 'hover': '#1976D2', 'text': '#ffffff'},
        'secondary': {'bg': '#6C757D', 'hover': '#5A6268', 'text': '#ffffff'},
        'success': {'bg': '#28A745', 'hover': '#218838', 'text': '#ffffff'},
        'danger': {'bg': '#DC3545', 'hover': '#C82333', 'text': '#ffffff'},
        'warning': {'bg': '#FFC107', 'hover': '#E0A800', 'text': '#212529'},
        'info': {'bg': '#17A2B8', 'hover': '#138496', 'text': '#ffffff'},
        'light': {'bg': '#F8F9FA', 'hover': '#E2E6EA', 'text': '#212529'},
        'dark': {'bg': '#343A40', 'hover': '#23272B', 'text': '#ffffff'},
    }

    def __init__(self, text: str = "", style_type: str = 'primary',
                 size: str = 'medium', parent=None):
        super().__init__(text, parent)
        self.style_type = style_type
        self.size = size
        self.is_hovered = False
        self.setup_animations()
        self.apply_style()

    def setup_animations(self):
        """Configura las animaciones del botón"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(150)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def apply_style(self):
        """Aplica el estilo basado en el tipo y tamaño"""
        colors = self.STYLES.get(self.style_type, self.STYLES['primary'])

        # Tamaños predefinidos
        sizes = {
            'small': {'padding': '4px 8px', 'font': '12px', 'min-height': '24px'},
            'medium': {'padding': '8px 16px', 'font': '14px', 'min-height': '36px'},
            'large': {'padding': '12px 24px', 'font': '16px', 'min-height': '48px'},
        }

        size_config = sizes.get(self.size, sizes['medium'])

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: none;
                padding: {size_config['padding']};
                border-radius: 8px;
                font-size: {size_config['font']};
                font-weight: 600;
                min-height: {size_config['min-height']};
            }}
            QPushButton:hover {{
                background-color: {colors['hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['bg']};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)

    def enterEvent(self, event):
        """Animación de entrada"""
        self.is_hovered = True
        if self.isEnabled():
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
            self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Animación de salida"""
        self.is_hovered = False
        if self.isEnabled():
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
            self.hover_animation.start()
        super().leaveEvent(event)

class ModernCard(QFrame):
    """Card moderno con sombras y múltiples variantes"""

    clicked = pyqtSignal()

    def __init__(self, title: str = "", subtitle: str = "",
                 variant: str = 'elevated', parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.variant = variant
        self.is_hovered = False
        self.setup_ui()
        self.setup_animations()
        self.apply_style()

    def setup_ui(self):
        """Configura la UI del card"""
        self.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header con título
        if self.title:
            header_layout = QVBoxLayout()
            header_layout.setSpacing(4)

            self.title_label = QLabel(self.title)
            self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
            self.title_label.setWordWrap(True)
            header_layout.addWidget(self.title_label)

            if self.subtitle:
                self.subtitle_label = QLabel(self.subtitle)
                self.subtitle_label.setFont(QFont("Arial", 12))
                self.subtitle_label.setWordWrap(True)
                self.subtitle_label.setStyleSheet("color: #6C757D;")
                header_layout.addWidget(self.subtitle_label)

            layout.addLayout(header_layout)

        # Content area (puede ser extendido)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        layout.addWidget(self.content_area)

        # Footer area opcional
        self.footer_area = QWidget()
        self.footer_layout = QHBoxLayout(self.footer_area)
        layout.addWidget(self.footer_area)

    def setup_animations(self):
        """Configura las animaciones"""
        self.shadow_animation = QPropertyAnimation(self, b"geometry")
        self.shadow_animation.setDuration(200)
        self.shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

    def apply_style(self):
        """Aplica estilos según la variante"""
        if self.variant == 'elevated':
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                }
                QFrame:hover {
                    border-color: #2196F3;
                }
            """)
        elif self.variant == 'outlined':
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #2196F3;
                    border-radius: 12px;
                }
            """)
        elif self.variant == 'filled':
            self.setStyleSheet("""
                QFrame {
                    background-color: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 12px;
                }
            """)

    def add_content_widget(self, widget: QWidget):
        """Agrega un widget al área de contenido"""
        self.content_layout.addWidget(widget)

    def add_footer_button(self, button: QPushButton):
        """Agrega un botón al área de footer"""
        self.footer_layout.addWidget(button)

    def enterEvent(self, event):
        """Animación de hover"""
        self.is_hovered = True
        if self.variant == 'elevated':
            current_rect = self.rect()
            elevated_rect = current_rect.adjusted(-4, -4, 4, 4)
            self.shadow_animation.setStartValue(current_rect)
            self.shadow_animation.setEndValue(elevated_rect)
            self.shadow_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Animación de salida"""
        self.is_hovered = False
        if self.variant == 'elevated':
            current_rect = self.rect()
            original_rect = current_rect.adjusted(4, 4, -4, -4)
            self.shadow_animation.setStartValue(current_rect)
            self.shadow_animation.setEndValue(original_rect)
            self.shadow_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Emit signal de click"""
        self.clicked.emit()
        super().mousePressEvent(event)

class ModernInput(QLineEdit):
    """Input field moderno con validación y estados"""

    # Estados de validación
    STATES = {
        'normal': {'border': '#CED4DA', 'bg': '#FFFFFF'},
        'focus': {'border': '#2196F3', 'bg': '#FFFFFF'},
        'error': {'border': '#DC3545', 'bg': '#FFF5F5'},
        'success': {'border': '#28A745', 'bg': '#F8FFF9'},
        'warning': {'border': '#FFC107', 'bg': '#FFFAF0'},
    }

    validation_changed = pyqtSignal(str)  # Emite el estado de validación

    def __init__(self, placeholder: str = "", validator=None, parent=None):
        super().__init__(placeholder, parent)
        self.validator = validator
        self.current_state = 'normal'
        self.setup_style()
        self.setup_connections()

    def setup_style(self):
        """Aplica el estilo base"""
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #CED4DA;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #FFFFFF;
                selection-background-color: #2196F3;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                outline: none;
            }
        """)

    def setup_connections(self):
        """Conecta señales para validación"""
        self.textChanged.connect(self.validate_text)
        self.focusInEvent = self._on_focus_in
        self.focusOutEvent = self._on_focus_out

    def _on_focus_in(self, event):
        """Maneja el evento de focus in"""
        self.set_state('focus')
        super().focusInEvent(event)

    def _on_focus_out(self, event):
        """Maneja el evento de focus out"""
        self.validate_text(self.text())
        if self.current_state == 'focus':
            self.set_state('normal')
        super().focusOutEvent(event)

    def set_state(self, state: str):
        """Establece el estado visual del input"""
        if state in self.STATES:
            self.current_state = state
            colors = self.STATES[state]
            self.setStyleSheet(f"""
                QLineEdit {{
                    border: 2px solid {colors['border']};
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 14px;
                    background-color: {colors['bg']};
                    selection-background-color: #2196F3;
                }}
                QLineEdit:focus {{
                    border-color: #2196F3;
                    outline: none;
                }}
            """)
            self.validation_changed.emit(state)

    def validate_text(self, text: str):
        """Valida el texto del input"""
        if self.validator:
            try:
                is_valid, message = self.validator(text)
                if not text:  # Empty text
                    self.set_state('normal')
                elif is_valid:
                    self.set_state('success')
                else:
                    self.set_state('error')
                return is_valid, message
            except Exception:
                self.set_state('normal')
        return True, ""

class ModernProgressBar(QProgressBar):
    """Progress bar moderna con animaciones y múltiples estilos"""

    def __init__(self, variant: str = 'determinate', parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_style()
        self.setup_animations()

    def setup_style(self):
        """Aplica estilos modernos"""
        self.setFixedHeight(8)
        self.setTextVisible(False)

        if self.variant == 'determinate':
            self.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: #E9ECEF;
                }
                QProgressBar::chunk {
                    border-radius: 4px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2196F3, stop:1 #1976D2);
                }
            """)
        elif self.variant == 'indeterminate':
            self.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: #E9ECEF;
                }
                QProgressBar::chunk {
                    border-radius: 4px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2196F3, stop:0.5 #1976D2, stop:1 #2196F3);
                }
            """)

    def setup_animations(self):
        """Configura animaciones si es indeterminado"""
        if self.variant == 'indeterminate':
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_indeterminate)
            self.value = 0
            self.direction = 1

    def start_indeterminate(self):
        """Inicia la animación indeterminada"""
        if self.variant == 'indeterminate':
            self.timer.start(30)

    def stop_indeterminate(self):
        """Detiene la animación indeterminada"""
        if hasattr(self, 'timer'):
            self.timer.stop()

    def update_indeterminate(self):
        """Actualiza la animación indeterminada"""
        self.value += self.direction * 2
        if self.value >= 100:
            self.value = 100
            self.direction = -1
        elif self.value <= 0:
            self.value = 0
            self.direction = 1
        super().setValue(self.value)

class ModernBadge(QLabel):
    """Badge moderno para notificaciones y estados"""

    VARIANTS = {
        'primary': '#2196F3',
        'secondary': '#6C757D',
        'success': '#28A745',
        'danger': '#DC3545',
        'warning': '#FFC107',
        'info': '#17A2B8',
    }

    def __init__(self, text: str = "", variant: str = 'primary',
                 size: str = 'medium', parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self.apply_style()

    def apply_style(self):
        """Aplica el estilo del badge"""
        color = self.VARIANTS.get(self.variant, self.VARIANTS['primary'])

        # Tamaños
        sizes = {
            'small': {'padding': '2px 6px', 'font': '10px', 'radius': '4px'},
            'medium': {'padding': '4px 8px', 'font': '12px', 'radius': '6px'},
            'large': {'padding': '6px 12px', 'font': '14px', 'radius': '8px'},
        }

        size_config = sizes.get(self.size, sizes['medium'])

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: {size_config['padding']};
                border-radius: {size_config['radius']};
                font-size: {size_config['font']};
                font-weight: 600;
            }}
        """)

class ModernTabBar(QWidget):
    """Tab bar moderna con animaciones y estilos personalizados"""

    tab_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs = []
        self.current_index = 0
        self.setup_ui()

    def setup_ui(self):
        """Configura la UI del tab bar"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

    def add_tab(self, text: str, icon=None):
        """Agrega un nuevo tab"""
        tab_button = ModernButton(text, 'light', 'small')
        tab_button.setCheckable(True)
        tab_button.clicked.connect(lambda: self.set_tab_index(len(self.tabs)))

        if len(self.tabs) == 0:
            tab_button.setChecked(True)
            tab_button.setStyleSheet(tab_button.styleSheet() + """
                QPushButton:checked {
                    background-color: #2196F3;
                    color: white;
                }
            """)

        self.tabs.append({'button': tab_button, 'text': text, 'icon': icon})
        self.layout.addWidget(tab_button)

    def set_tab_index(self, index: int):
        """Establece el tab activo"""
        if 0 <= index < len(self.tabs):
            # Actualizar estados de los botones
            for i, tab in enumerate(self.tabs):
                tab['button'].setChecked(i == index)
                if i == index:
                    tab['button'].setStyleSheet(tab['button'].styleSheet() + """
                        QPushButton:checked {
                            background-color: #2196F3;
                            color: white;
                        }
                    """)
                else:
                    # Restablecer estilo normal
                    tab['button'].setStyleSheet(tab['button'].styleSheet().replace("""
                        QPushButton:checked {
                            background-color: #2196F3;
                            color: white;
                        }
                    """, ""))

            self.current_index = index
            self.tab_changed.emit(index)

class ModernComponentsDemo(QWidget):
    """Demostración de todos los componentes modernos"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern UI Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de demostración"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # Título
        title = QLabel("Modern UI Components Library")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Scroll area para todos los componentes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(40)

        # Buttons Demo
        self.create_buttons_demo(content_layout)

        # Cards Demo
        self.create_cards_demo(content_layout)

        # Input Fields Demo
        self.create_inputs_demo(content_layout)

        # Progress Bars Demo
        self.create_progress_demo(content_layout)

        # Badges Demo
        self.create_badges_demo(content_layout)

        # Tab Bar Demo
        self.create_tabs_demo(content_layout)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def create_buttons_demo(self, layout):
        """Crea demostración de botones"""
        group = QGroupBox("Buttons")
        group_layout = QHBoxLayout(group)

        styles = ['primary', 'secondary', 'success', 'danger', 'warning', 'info']
        for style in styles:
            btn = ModernButton(f"{style.capitalize()} Button", style)
            group_layout.addWidget(btn)

        layout.addWidget(group)

    def create_cards_demo(self, layout):
        """Crea demostración de cards"""
        group = QGroupBox("Cards")
        group_layout = QHBoxLayout(group)

        variants = ['elevated', 'outlined', 'filled']
        for variant in variants:
            card = ModernCard(f"{variant.capitalize()} Card",
                              f"This is a {variant} card with modern styling",
                              variant)

            # Agregar un botón al footer
            action_btn = ModernButton("Action", 'primary', 'small')
            card.add_footer_button(action_btn)

            group_layout.addWidget(card)

        layout.addWidget(group)

    def create_inputs_demo(self, layout):
        """Crea demostración de inputs"""
        group = QGroupBox("Input Fields")
        group_layout = QVBoxLayout(group)

        # Input con validación de email
        email_validator = lambda text: (len(text) == 0 or '@' in text,
                                       "Invalid email format" if len(text) > 0 and '@' not in text else "")

        email_input = ModernInput("Enter your email...", email_validator)
        group_layout.addWidget(email_input)

        # Input con validación de contraseña
        password_validator = lambda text: (len(text) >= 8 or len(text) == 0,
                                         "Password must be at least 8 characters" if len(text) > 0 and len(text) < 8 else "")

        password_input = ModernInput("Enter your password...", password_validator)
        password_input.setEchoMode(QLineEdit.Password)
        group_layout.addWidget(password_input)

        layout.addWidget(group)

    def create_progress_demo(self, layout):
        """Crea demostración de progress bars"""
        group = QGroupBox("Progress Bars")
        group_layout = QVBoxLayout(group)

        # Progress bar determinada
        progress_determinate = ModernProgressBar('determinate')
        progress_determinate.setValue(75)
        group_layout.addWidget(progress_determinate)

        # Progress bar indeterminada
        progress_indeterminate = ModernProgressBar('indeterminate')
        progress_indeterminate.start_indeterminate()
        group_layout.addWidget(progress_indeterminate)

        layout.addWidget(group)

    def create_badges_demo(self, layout):
        """Crea demostración de badges"""
        group = QGroupBox("Badges")
        group_layout = QHBoxLayout(group)

        variants = ['primary', 'secondary', 'success', 'danger', 'warning', 'info']
        for variant in variants:
            badge = ModernBadge(variant.upper(), variant, 'medium')
            group_layout.addWidget(badge)

        layout.addWidget(group)

    def create_tabs_demo(self, layout):
        """Crea demostración de tab bar"""
        group = QGroupBox("Tab Bar")
        group_layout = QVBoxLayout(group)

        tab_bar = ModernTabBar()
        tab_bar.add_tab("Overview")
        tab_bar.add_tab("Features")
        tab_bar.add_tab("Documentation")
        tab_bar.add_tab("Settings")

        group_layout.addWidget(tab_bar)

        # Contenido del tab seleccionado
        tab_content = QLabel("Tab content will appear here")
        tab_content.setStyleSheet("padding: 20px; background-color: #f8f9fa; border-radius: 8px;")
        group_layout.addWidget(tab_content)

        def on_tab_changed(index):
            tab_names = ["Overview", "Features", "Documentation", "Settings"]
            tab_content.setText(f"Content for: {tab_names[index]}")

        tab_bar.tab_changed.connect(on_tab_changed)

        layout.addWidget(group)

def main():
    """Función principal de demostración"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    demo = ModernComponentsDemo()
    demo.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()