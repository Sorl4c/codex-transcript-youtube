#!/usr/bin/env python3
"""
Modern Visual Effects Demo for PySide6
Demostración de efectos visuales modernos: glassmorphism, blur, sombras, animaciones
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QSlider,
                               QGraphicsOpacityEffect, QFrame, QScrollArea)
from PySide6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve,
                           QParallelAnimationGroup, QSequentialAnimationGroup,
                           QRect, pyqtSignal)
from PySide6.QtGui import (QPainter, QColor, QLinearGradient, QRadialGradient,
                           QPen, QBrush, QFont, QPalette, QPixmap, QTransform)

class GlassmorphismWidget(QWidget):
    """Widget con efecto glassmorphism (cristal esmerilado)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        self.blur_radius = 10
        self.opacity = 0.8

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo con efecto glassmorphism
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
        painter.drawRoundedRect(self.rect(), 20, 20)

        # Gradiente sutil para profundidad
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 30))
        gradient.setColorAt(1, QColor(255, 255, 255, 10))
        painter.fillRect(self.rect(), gradient)

        # Texto del widget
        painter.setPen(QColor(255, 255, 255, 200))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "Glassmorphism Effect")

class ModernCard(QWidget):
    """Card moderno con sombras y efectos hover"""

    hovered = pyqtSignal()
    unhovered = pyqtSignal()

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.setFixedSize(280, 180)
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # Título
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.title_label)

        # Subtítulo
        self.subtitle_label = QLabel(self.subtitle)
        self.subtitle_label.setFont(QFont("Arial", 10))
        self.subtitle_label.setStyleSheet("color: #7f8c8d;")
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)

        layout.addStretch()

        # Botón
        self.button = QPushButton("Learn More")
        self.button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.button)

        self.apply_modern_style()

    def apply_modern_style(self):
        """Aplica el estilo moderno con sombras"""
        self.setStyleSheet("""
            ModernCard {
                background-color: #ffffff;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }
            ModernCard:hover {
                background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)

    def setup_animations(self):
        """Configura las animaciones de hover"""
        self.shadow_animation = QPropertyAnimation(self, b"geometry")
        self.shadow_animation.setDuration(200)
        self.shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        """Evento de mouse enter"""
        self.hovered.emit()
        # Animación de elevación
        current_rect = self.rect()
        elevated_rect = current_rect.adjusted(-5, -5, 5, 5)
        self.shadow_animation.setStartValue(current_rect)
        self.shadow_animation.setEndValue(elevated_rect)
        self.shadow_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Evento de mouse leave"""
        self.unhovered.emit()
        # Restaurar tamaño original
        current_rect = self.rect()
        original_rect = current_rect.adjusted(5, 5, -5, -5)
        self.shadow_animation.setStartValue(current_rect)
        self.shadow_animation.setEndValue(original_rect)
        self.shadow_animation.start()
        super().leaveEvent(event)

class AnimatedBackground(QWidget):
    """Fondo animado con gradiente dinámico"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gradient_angle = 0
        self.setup_animation()

    def setup_animation(self):
        """Configura la animación del gradiente"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_gradient)
        self.animation_timer.start(50)  # 20 FPS

    def update_gradient(self):
        """Actualiza el ángulo del gradiente"""
        self.gradient_angle = (self.gradient_angle + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradiente animado
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setSpread(QLinearGradient.PadSpread)

        # Colores que cambian con el tiempo
        import math
        angle_rad = math.radians(self.gradient_angle)

        r1 = int(127 + 127 * math.sin(angle_rad))
        g1 = int(127 + 127 * math.sin(angle_rad + 2*math.pi/3))
        b1 = int(127 + 127 * math.sin(angle_rad + 4*math.pi/3))

        r2 = int(127 + 127 * math.sin(angle_rad + math.pi))
        g2 = int(127 + 127 * math.sin(angle_rad + 5*math.pi/3))
        b2 = int(127 + 127 * math.sin(angle_rad + math.pi/3))

        gradient.setColorAt(0, QColor(r1, g1, b1, 100))
        gradient.setColorAt(0.5, QColor(r2, g2, b2, 150))
        gradient.setColorAt(1, QColor(r1, g1, b1, 100))

        painter.fillRect(self.rect(), gradient)

class FloatingButton(QPushButton):
    """Botón flotante (FAB) moderno con animación de ripple"""

    def __init__(self, icon="", parent=None):
        super().__init__(icon, parent)
        self.setup_modern_style()
        self.setup_ripple_animation()

    def setup_modern_style(self):
        """Configura el estilo moderno del botón flotante"""
        self.setFixedSize(56, 56)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 28px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

    def setup_ripple_animation(self):
        """Configura la animación de ripple"""
        self.ripple_animation = QPropertyAnimation(self, b"geometry")
        self.ripple_animation.setDuration(150)
        self.ripple_animation.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event):
        """Implementa el efecto ripple al presionar"""
        current_rect = self.rect()
        ripple_rect = current_rect.adjusted(-3, -3, 3, 3)
        self.ripple_animation.setStartValue(current_rect)
        self.ripple_animation.setEndValue(ripple_rect)
        self.ripple_animation.start()
        super().mousePressEvent(event)

class BlurEffectWidget(QWidget):
    """Widget con efectos de blur personalizados"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título con efecto blur
        title = QLabel("Blur Effects Demo")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Slider para controlar blur
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 20)
        self.blur_slider.setValue(10)
        self.blur_slider.valueChanged.connect(self.update_blur)
        self.blur_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255,255,255,0.3);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
        """)
        layout.addWidget(self.blur_slider)

        # Widget con blur aplicado
        self.blur_widget = QWidget()
        self.blur_widget.setFixedSize(200, 100)
        self.blur_layout = QVBoxLayout(self.blur_widget)

        blur_label = QLabel("Blurred Content")
        blur_label.setStyleSheet("color: white; font-weight: bold;")
        self.blur_layout.addWidget(blur_label, alignment=Qt.AlignCenter)

        layout.addWidget(self.blur_widget, alignment=Qt.AlignCenter)

    def update_blur(self, value):
        """Actualiza el efecto blur"""
        blur_effect = QGraphicsOpacityEffect()
        blur_effect.setOpacity(1.0 - (value / 40.0))
        self.blur_widget.setGraphicsEffect(blur_effect)

class ModernEffectsDemo(QMainWindow):
    """Ventana principal de demostración de efectos modernos"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Visual Effects Demo - PySide6")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Fondo animado
        self.background = AnimatedBackground(self)
        self.background.setGeometry(0, 0, self.width(), self.height())

        # Widget principal con efecto glassmorphism
        main_widget = QWidget(self)
        main_widget.setGeometry(50, 50, 1100, 700)
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)

        # Layout principal
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Panel izquierdo - Glassmorphism y Blur
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)

        # Título
        title = QLabel("Modern Visual Effects")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        left_layout.addWidget(title)

        # Glassmorphism widgets
        glass_container = QWidget()
        glass_layout = QHBoxLayout(glass_container)
        glass_layout.setSpacing(15)

        for i in range(3):
            glass_widget = GlassmorphismWidget()
            glass_layout.addWidget(glass_widget)

        left_layout.addWidget(glass_container)

        # Blur effects demo
        blur_widget = BlurEffectWidget()
        blur_widget.setStyleSheet("""
            BlurEffectWidget {
                background-color: rgba(33, 150, 243, 0.2);
                border-radius: 12px;
                margin: 10px;
            }
        """)
        left_layout.addWidget(blur_widget)

        main_layout.addWidget(left_panel)

        # Panel derecho - Cards modernas
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_panel.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(20)

        # Cards demo
        card_data = [
            ("Animation & Motion", "Smooth transitions and micro-interactions enhance user experience"),
            ("Material Design 3", "Dynamic color, elevation, and adaptive theming"),
            ("Glassmorphism", "Frosted glass effects with transparency and blur"),
            ("Dark Mode Support", "Automatic theme switching with smooth transitions"),
            ("Responsive Design", "Adaptive layouts that work on all screen sizes")
        ]

        for title, subtitle in card_data:
            card = ModernCard(title, subtitle)
            cards_layout.addWidget(card)

        right_panel.setWidget(cards_container)
        main_layout.addWidget(right_panel)

        # Floating Action Button
        self.fab = FloatingButton("+")
        self.fab.setParent(self)
        self.fab.move(1050, 650)
        self.fab.clicked.connect(self.add_new_effect)

    def setup_animations(self):
        """Configura animaciones globales"""
        # Animación de entrada para los elementos
        self.fade_in_timer = QTimer()
        self.fade_in_timer.timeout.connect(self.fade_in_elements)
        self.fade_in_timer.start(100)

    def fade_in_elements(self):
        """Animación de entrada para los elementos"""
        # Implementar animación de entrada suave
        pass

    def add_new_effect(self):
        """Acción del FAB - agregar nuevo efecto"""
        print("Adding new modern effect...")

    def resizeEvent(self, event):
        """Ajusta el tamaño del fondo al cambiar el tamaño"""
        self.background.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

def main():
    """Función principal de la demostración"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Usar estilo Fusion para mejor apariencia

    # Configurar paleta de colores moderna
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(30, 30, 30))
    app.setPalette(palette)

    # Crear y mostrar la ventana principal
    window = ModernEffectsDemo()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()