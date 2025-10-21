#!/usr/bin/env python3
"""
Integration Example: Qdarkstyle Integration
Ejemplo de integración de librerías modernas con PySide6
"""


# QDarkStyle Integration Example
import sys
import qdarkstyle
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QLabel, QLineEdit)

class DarkModeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark Mode Demo")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Widgets con tema oscuro
        title = QLabel("Dark Mode Application")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter text here...")
        layout.addWidget(input_field)

        button = QPushButton("Modern Dark Button")
        button.setMinimumHeight(40)
        layout.addWidget(button)

        toggle_btn = QPushButton("Toggle Theme")
        toggle_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(toggle_btn)

        self.is_dark = True

    def toggle_theme(self):
        """Cambia entre tema oscuro y claro"""
        app = QApplication.instance()

        if self.is_dark:
            # Cambiar a tema claro
            app.setStyleSheet("")
            self.is_dark = False
            self.setWindowTitle("Light Mode Demo")
        else:
            # Cambiar a tema oscuro
            dark_stylesheet = qdarkstyle.load_stylesheet()
            app.setStyleSheet(dark_stylesheet)
            self.is_dark = True
            self.setWindowTitle("Dark Mode Demo")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Aplicar tema oscuro por defecto
    dark_stylesheet = qdarkstyle.load_stylesheet()
    app.setStyleSheet(dark_stylesheet)

    window = DarkModeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = YourAppClass()  # Reemplazar con la clase específica
    window.show()

    sys.exit(app.exec())
