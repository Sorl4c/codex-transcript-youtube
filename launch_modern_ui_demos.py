#!/usr/bin/env python3
"""
Modern UI Demo Launcher
Lanzador para todas las demos de UI moderna en PySide6
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFrame,
                               QScrollArea, QGroupBox, QStackedWidget,
                               QGraphicsOpacityEffect, QPropertyAnimation,
                               QFont, QPixmap)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QIcon

class DemoLauncher(QMainWindow):
    """Ventana principal del lanzador de demos"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern UI Demo Launcher - PySide6")
        self.setGeometry(100, 100, 1000, 700)
        self.demos = []
        self.setup_ui()
        self.setup_animations()
        self.load_demo_info()

    def setup_ui(self):
        """Configura la interfaz del lanzador"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.create_header(main_layout)

        # Área de contenido
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        # Panel de demos
        self.create_demos_panel(content_layout)

        # Panel de información
        self.create_info_panel(content_layout)

        main_layout.addWidget(content_widget)

        # Footer
        self.create_footer(main_layout)

    def create_header(self, parent_layout):
        """Crea el header principal"""
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border: none;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(40, 20, 40, 20)

        # Título principal
        title = QLabel("Modern UI Showcase")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: white; margin: 10px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Subtítulo
        subtitle = QLabel("PySide6 Modern Components & Effects")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        header_layout.addWidget(subtitle)

        parent_layout.addWidget(header)

    def create_demos_panel(self, parent_layout):
        """Crea el panel de selección de demos"""
        demos_container = QWidget()
        demos_container.setMinimumWidth(600)

        demos_layout = QVBoxLayout(demos_container)
        demos_layout.setSpacing(20)

        # Título del panel
        panel_title = QLabel("Available Demos")
        panel_title.setFont(QFont("Arial", 18, QFont.Bold))
        panel_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        demos_layout.addWidget(panel_title)

        # Scroll area para lista de demos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #f8f9fa;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self.demos_content = QWidget()
        self.demos_layout = QVBoxLayout(self.demos_content)
        self.demos_layout.setContentsMargins(20, 20, 20, 20)
        self.demos_layout.setSpacing(15)

        scroll_area.setWidget(self.demos_content)
        demos_layout.addWidget(scroll_area)

        parent_layout.addWidget(demos_container)

    def create_info_panel(self, parent_layout):
        """Crea el panel de información de demos"""
        info_container = QWidget()
        info_container.setMinimumWidth(350)

        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(20)

        # Título del panel
        panel_title = QLabel("Demo Information")
        panel_title.setFont(QFont("Arial", 18, QFont.Bold))
        panel_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        info_layout.addWidget(panel_title)

        # Área de información
        self.info_area = QWidget()
        self.info_area.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
            }
        """)

        self.info_layout = QVBoxLayout(self.info_area)
        self.info_layout.setSpacing(15)

        # Información por defecto
        self.show_default_info()

        info_layout.addWidget(self.info_area)

        # Botón de lanzar demo
        self.launch_button = QPushButton("Launch Selected Demo")
        self.launch_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.launch_button.setFixedHeight(50)
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.launch_button.clicked.connect(self.launch_selected_demo)
        self.launch_button.setEnabled(False)
        info_layout.addWidget(self.launch_button)

        # Botón de lanzar todas las demos
        launch_all_button = QPushButton("Launch All Demos")
        launch_all_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        launch_all_button.clicked.connect(self.launch_all_demos)
        info_layout.addWidget(launch_all_button)

        info_layout.addStretch()

        parent_layout.addWidget(info_container)

    def create_footer(self, parent_layout):
        """Crea el footer con información"""
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
        """)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 10, 30, 10)

        # Información del proyecto
        info_text = QLabel("PySide6 Modern UI Showcase | Built with Qt6 | 2024")
        info_text.setStyleSheet("color: white; font-size: 12px;")
        footer_layout.addWidget(info_text)

        footer_layout.addStretch()

        # Créditos
        credits = QLabel("Created with ❤️ for modern desktop applications")
        credits.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 12px;")
        footer_layout.addWidget(credits)

        parent_layout.addWidget(footer)

    def load_demo_info(self):
        """Carga información de todas las demos disponibles"""
        self.demos = [
            {
                "name": "Modern Components Library",
                "description": "Complete library of modern UI components with Material Design inspiration",
                "script": "modern_components.py",
                "icon": "🎨",
                "features": [
                    "Modern buttons with multiple styles",
                    "Cards with hover effects",
                    "Input fields with validation",
                    "Progress bars and badges",
                    "Tab bars with smooth transitions"
                ],
                "difficulty": "Beginner",
                "category": "Components"
            },
            {
                "name": "Dynamic Theming System",
                "description": "Advanced theming system with light/dark mode and smooth transitions",
                "script": "dynamic_theming.py",
                "icon": "🌓",
                "features": [
                    "Light and dark themes",
                    "Smooth theme transitions",
                    "Custom theme creation",
                    "Auto theme detection",
                    "Animation effects"
                ],
                "difficulty": "Intermediate",
                "category": "Theming"
            },
            {
                "name": "Modern Visual Effects",
                "description": "Collection of modern visual effects including glassmorphism and animations",
                "script": "modern_effects_demo.py",
                "icon": "✨",
                "features": [
                    "Glassmorphism effects",
                    "Animated backgrounds",
                    "Floating action buttons",
                    "Blur and shadow effects",
                    "Smooth animations"
                ],
                "difficulty": "Intermediate",
                "category": "Effects"
            },
            {
                "name": "Material Design 3 Showcase",
                "description": "Complete Material Design 3 implementation with QML and Python",
                "script": "material_design_3_demo.py",
                "icon": "📱",
                "features": [
                    "Material Design 3 components",
                    "QML integration",
                    "Dynamic color theming",
                    "Adaptive layouts",
                    "Native controls"
                ],
                "difficulty": "Advanced",
                "category": "Design Systems"
            },
            {
                "name": "Complete UI Showcase",
                "description": "Full application showcasing all modern UI techniques and best practices",
                "script": "modern_ui_showcase.py",
                "icon": "🚀",
                "features": [
                    "Dashboard with metrics",
                    "Activity feeds",
                    "Interactive charts",
                    "Navigation system",
                    "Responsive design"
                ],
                "difficulty": "Advanced",
                "category": "Complete App"
            },
            {
                "name": "Modern UI Research",
                "description": "Research analysis and implementation of modern UI trends",
                "script": "modern_ui_research.py",
                "icon": "📊",
                "features": [
                    "Trend analysis",
                    "Component examples",
                    "Best practices guide",
                    "Implementation patterns",
                    "Design recommendations"
                ],
                "difficulty": "Beginner",
                "category": "Research"
            }
        ]

        self.create_demo_buttons()

    def create_demo_buttons(self):
        """Crea botones para cada demo"""
        for demo in self.demos:
            demo_widget = self.create_demo_button(demo)
            self.demos_layout.addWidget(demo_widget)

        self.demos_layout.addStretch()

    def create_demo_button(self, demo):
        """Crea un widget de botón para una demo"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #2196F3;
                background-color: #f8f9fa;
            }
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Icono
        icon_label = QLabel(demo["icon"])
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setFixedWidth(40)
        layout.addWidget(icon_label)

        # Información
        info_layout = QVBoxLayout()

        # Nombre
        name_label = QLabel(demo["name"])
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("color: #2c3e50;")
        info_layout.addWidget(name_label)

        # Descripción
        desc_label = QLabel(demo["description"])
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #6c757d;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        # Tags
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)

        # Tag de categoría
        category_tag = QLabel(demo["category"])
        category_tag.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
            }
        """)
        tags_layout.addWidget(category_tag)

        # Tag de dificultad
        difficulty_colors = {
            "Beginner": "#28a745",
            "Intermediate": "#ffc107",
            "Advanced": "#dc3545"
        }
        diff_color = difficulty_colors.get(demo["difficulty"], "#6c757d")

        difficulty_tag = QLabel(demo["difficulty"])
        difficulty_tag.setStyleSheet(f"""
            QLabel {{
                background-color: rgba({int(diff_color[1:3], 16)}, {int(diff_color[3:5], 16)}, {int(diff_color[5:7], 16)}, 0.1);
                color: {diff_color};
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
            }}
        """)
        tags_layout.addWidget(difficulty_tag)

        tags_layout.addStretch()
        info_layout.addLayout(tags_layout)

        layout.addLayout(info_layout)

        # Botón de seleccionar
        select_btn = QPushButton("Select")
        select_btn.setFixedWidth(80)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        select_btn.clicked.connect(lambda: self.select_demo(demo))
        layout.addWidget(select_btn)

        # Guardar referencia al botón y demo
        widget.demo = demo
        widget.select_btn = select_btn

        # Efecto hover
        widget.enterEvent = lambda event: self.on_demo_hover(widget, True)
        widget.leaveEvent = lambda event: self.on_demo_hover(widget, False)

        return widget

    def on_demo_hover(self, widget, is_hovering):
        """Maneja el efecto hover en las demos"""
        if is_hovering:
            widget.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 2px solid #2196F3;
                    border-radius: 12px;
                    padding: 15px;
                }
            """)
        else:
            widget.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 15px;
                }
            """)

    def select_demo(self, demo):
        """Selecciona una demo y muestra su información"""
        self.selected_demo = demo
        self.show_demo_info(demo)
        self.launch_button.setEnabled(True)

        # Actualizar estado visual de los botones
        for i in range(self.demos_layout.count()):
            widget = self.demos_layout.itemAt(i).widget()
            if hasattr(widget, 'demo') and hasattr(widget, 'select_btn'):
                if widget.demo == demo:
                    widget.select_btn.setText("✓ Selected")
                    widget.select_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #28A745;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: bold;
                            font-size: 11px;
                        }
                    """)
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: #e8f5e8;
                            border: 2px solid #28A745;
                            border-radius: 12px;
                            padding: 15px;
                        }
                    """)
                else:
                    widget.select_btn.setText("Select")
                    widget.select_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: bold;
                            font-size: 11px;
                        }
                    """)
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: white;
                            border: 2px solid #e0e0e0;
                            border-radius: 12px;
                            padding: 15px;
                        }
                    """)

    def show_demo_info(self, demo):
        """Muestra información detallada de una demo"""
        # Limpiar información previa
        for i in reversed(range(self.info_layout.count())):
            child = self.info_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        # Icono y título
        header_layout = QHBoxLayout()

        icon_label = QLabel(demo["icon"])
        icon_label.setFont(QFont("Arial", 32))
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()

        title_label = QLabel(demo["name"])
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(title_label)

        script_label = QLabel(f"Script: {demo['script']}")
        script_label.setFont(QFont("Arial", 10))
        script_label.setStyleSheet("color: #6c757d; font-family: monospace;")
        title_layout.addWidget(script_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        self.info_layout.addLayout(header_layout)

        # Descripción
        desc_label = QLabel(demo["description"])
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setStyleSheet("color: #495057;")
        desc_label.setWordWrap(True)
        self.info_layout.addWidget(desc_label)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e0e0e0;")
        self.info_layout.addWidget(line)

        # Características
        features_label = QLabel("Key Features:")
        features_label.setFont(QFont("Arial", 12, QFont.Bold))
        features_label.setStyleSheet("color: #2c3e50;")
        self.info_layout.addWidget(features_label)

        for feature in demo["features"]:
            feature_label = QLabel(f"• {feature}")
            feature_label.setFont(QFont("Arial", 10))
            feature_label.setStyleSheet("color: #6c757d; margin-left: 10px;")
            self.info_layout.addWidget(feature_label)

        self.info_layout.addStretch()

    def show_default_info(self):
        """Muestra información por defecto"""
        welcome_label = QLabel("🎨 Welcome to Modern UI Showcase")
        welcome_label.setFont(QFont("Arial", 18, QFont.Bold))
        welcome_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        welcome_label.setAlignment(Qt.AlignCenter)
        self.info_layout.addWidget(welcome_label)

        info_text = QLabel("""
        Select a demo from the left panel to see detailed information.

        Each demo showcases different aspects of modern UI development with PySide6:

        • Modern components and widgets
        • Advanced theming systems
        • Visual effects and animations
        • Material Design implementations
        • Best practices and patterns
        """)
        info_text.setFont(QFont("Arial", 11))
        info_text.setStyleSheet("color: #6c757d; line-height: 1.5;")
        info_text.setWordWrap(True)
        info_text.setAlignment(Qt.AlignCenter)
        self.info_layout.addWidget(info_text)

        self.info_layout.addStretch()

    def launch_selected_demo(self):
        """Lanza la demo seleccionada"""
        if hasattr(self, 'selected_demo'):
            self.launch_demo(self.selected_demo)

    def launch_demo(self, demo):
        """Lanza una demo específica"""
        try:
            print(f"Launching demo: {demo['name']}")
            print(f"Script: {demo['script']}")

            # Importar y ejecutar la demo
            script_name = demo['script'].replace('.py', '')

            if script_name == 'modern_components':
                from modern_components import main
                main()
            elif script_name == 'dynamic_theming':
                from dynamic_theming import main
                main()
            elif script_name == 'modern_effects_demo':
                from modern_effects_demo import main
                main()
            elif script_name == 'material_design_3_demo':
                from material_design_3_demo import main
                main()
            elif script_name == 'modern_ui_showcase':
                from modern_ui_showcase import main
                main()
            elif script_name == 'modern_ui_research':
                from modern_ui_research import main
                main()
            else:
                print(f"Demo script not found: {demo['script']}")

        except ImportError as e:
            print(f"Error importing demo {demo['script']}: {e}")
        except Exception as e:
            print(f"Error launching demo {demo['script']}: {e}")

    def launch_all_demos(self):
        """Lanza todas las demos secuencialmente"""
        print("Launching all demos sequentially...")

        # Mostrar mensaje
        msg_widget = QWidget()
        msg_layout = QVBoxLayout(msg_widget)

        msg_label = QLabel("🚀 Launching all demos...")
        msg_label.setFont(QFont("Arial", 16, QFont.Bold))
        msg_label.setStyleSheet("color: #2c3e50; margin: 20px;")
        msg_label.setAlignment(Qt.AlignCenter)
        msg_layout.addWidget(msg_label)

        note_label = QLabel("Each demo will open in a separate window.\nClose each demo to continue to the next one.")
        note_label.setFont(QFont("Arial", 11))
        note_label.setStyleSheet("color: #6c757d; margin: 10px;")
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setWordWrap(True)
        msg_layout.addWidget(note_label)

        self.info_layout.addWidget(msg_widget)

        # Lanzar demos con un pequeño retraso entre cada una
        for i, demo in enumerate(self.demos):
            QTimer.singleShot(i * 1000, lambda d=demo: self.launch_demo(d))

    def setup_animations(self):
        """Configura animaciones de entrada"""
        self.setWindowOpacity(0.0)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        QTimer.singleShot(100, lambda: self.fade_animation.start())

def main():
    """Función principal del lanzador"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Configurar información de la aplicación
    app.setApplicationName("Modern UI Demo Launcher")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PySide6 Examples")

    # Crear y mostrar el lanzador
    launcher = DemoLauncher()
    launcher.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())