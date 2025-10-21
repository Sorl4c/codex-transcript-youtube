#!/usr/bin/env python3
"""
Glassmorphism Example for Modern PySide6 UI
Ejemplo de implementación moderna para PySide6
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# Glassmorphism Effect Example
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

class GlassmorphismWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        label = QLabel("Glassmorphism Effect")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        button = QPushButton("Modern Button")
        layout.addWidget(button)

        # Add hover animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style

    # Crear y mostrar el ejemplo
    window = YourWidget()  # Reemplazar con la clase específica
    window.setWindowTitle("Glassmorphism Example")
    window.resize(400, 300)
    window.show()

    sys.exit(app.exec())
