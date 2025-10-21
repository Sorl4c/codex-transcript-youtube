#!/usr/bin/env python3
"""
Modern_Card Example for Modern PySide6 UI
Ejemplo de implementación moderna para PySide6
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# Modern Card Component
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PySide6.QtGui import QFont, QPalette

class ModernCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, title="", subtitle="", icon=""):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        self.setFixedSize(300, 150)
        self.setStyleSheet("""
            ModernCard {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            ModernCard:hover {
                background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

    def setup_animations(self):
        self.shadow_animation = QPropertyAnimation(self, b"geometry")
        self.shadow_animation.setDuration(200)
        self.shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        # Animate on hover
        current_geom = self.geometry()
        new_geom = current_geom.adjusted(-5, -5, 5, 5)
        self.shadow_animation.setStartValue(current_geom)
        self.shadow_animation.setEndValue(new_geom)
        self.shadow_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Restore original size
        current_geom = self.geometry()
        original_geom = current_geom.adjusted(5, 5, -5, -5)
        self.shadow_animation.setStartValue(current_geom)
        self.shadow_animation.setEndValue(original_geom)
        self.shadow_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style

    # Crear y mostrar el ejemplo
    window = YourWidget()  # Reemplazar con la clase específica
    window.setWindowTitle("Modern_Card Example")
    window.resize(400, 300)
    window.show()

    sys.exit(app.exec())
