#!/usr/bin/env python3
"""
Dark_Mode Example for Modern PySide6 UI
Ejemplo de implementación moderna para PySide6
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# Dark Mode Implementation
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QPalette, QColor

class DarkModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark = False
        self.setup_ui()
        self.apply_light_theme()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.toggle_button = QPushButton("Toggle Dark Mode")
        self.toggle_button.clicked.connect(self.toggle_theme)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                background-color: #007acc;
                color: white;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)

        layout.addWidget(self.toggle_button)

    def toggle_theme(self):
        if self.is_dark:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()
        self.is_dark = not self.is_dark

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
            }
        """)

        palette = QApplication.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
        palette.setColor(QPalette.Base, QColor(248, 249, 250))
        palette.setColor(QPalette.AlternateBase, QColor(233, 236, 239))
        palette.setColor(QPalette.ToolTipBase, QColor(44, 62, 80))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(44, 62, 80))
        palette.setColor(QPalette.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(44, 62, 80))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 122, 204))
        palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.setPalette(palette)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
        """)

        palette = QApplication.palette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipBase, QColor(224, 224, 224))
        palette.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
        palette.setColor(QPalette.Text, QColor(224, 224, 224))
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(100, 149, 237))
        palette.setColor(QPalette.Highlight, QColor(100, 149, 237))
        palette.setColor(QPalette.HighlightedText, QColor(30, 30, 30))
        QApplication.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style

    # Crear y mostrar el ejemplo
    window = YourWidget()  # Reemplazar con la clase específica
    window.setWindowTitle("Dark_Mode Example")
    window.resize(400, 300)
    window.show()

    sys.exit(app.exec())
