#!/usr/bin/env python3
"""
Integration Example: Qtawesome Integration
Ejemplo de integración de librerías modernas con PySide6
"""


# QtAwesome Integration Example
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QToolBar)
import qtawesome as qta

class IconRichInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QtAwesome Icons Demo")
        self.setGeometry(100, 100, 500, 400)

        # Crear toolbar con iconos
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Acciones con iconos Font Awesome
        action_play = qta.icon("fa.play", color="green")
        toolbar.addAction(action_play, "Play")

        action_pause = qta.icon("fa.pause", color="orange")
        toolbar.addAction(action_pause, "Pause")

        action_stop = qta.icon("fa.stop", color="red")
        toolbar.addAction(action_stop, "Stop")

        # Botones con iconos en el contenido
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Botón con icono de usuario
        btn_user = QPushButton(" User Profile")
        btn_user.setIcon(qta.icon("fa.user", color="blue"))
        layout.addWidget(btn_user)

        # Botón con icono de configuración
        btn_settings = QPushButton(" Settings")
        btn_settings.setIcon(qta.icon("fa.cog", color="gray"))
        layout.addWidget(btn_settings)

        # Botón con icono personalizado
        btn_custom = QPushButton(" Custom Icon")
        custom_icon = qta.icon("fa5s.star", color="gold",
                              options=[{"scale_factor": 1.5}])
        btn_custom.setIcon(custom_icon)
        layout.addWidget(btn_custom)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IconRichInterface()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = YourAppClass()  # Reemplazar con la clase específica
    window.show()

    sys.exit(app.exec())
