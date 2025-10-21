#!/usr/bin/env python3
"""
Integration Example: Superqt Integration
Ejemplo de integración de librerías modernas con PySide6
"""


# SuperQt Integration Example
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from superqt import QLabeledSlider, QLabeledDoubleSlider
from superqt.color import QColorPushButton

class ModernControlsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperQt Modern Controls")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Sliders avanzados
        int_slider = QLabeledSlider()
        int_slider.setRange(0, 100)
        int_slider.setValue(50)
        int_slider.setOrientation(1)  # Horizontal
        layout.addWidget(int_slider)

        double_slider = QLabeledDoubleSlider()
        double_slider.setRange(0.0, 1.0)
        double_slider.setValue(0.5)
        double_slider.setOrientation(1)
        layout.addWidget(double_slider)

        # Selector de color moderno
        color_button = QColorPushButton()
        color_button.setText("Choose Color")
        layout.addWidget(color_button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernControlsDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = YourAppClass()  # Reemplazar con la clase específica
    window.show()

    sys.exit(app.exec())
