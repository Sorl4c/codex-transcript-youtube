#!/usr/bin/env python3
"""
Modern UI Libraries and Tools for PySide6
Librerías complementarias y herramientas para UI moderna
"""

import sys
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path

@dataclass
class UILibrary:
    """Representa una librería o herramienta para UI moderna"""
    name: str
    category: str
    description: str
    website: str
    pip_install: str
    compatibility: str  # PySide6, Qt6, General
    rating: int  # 1-5 stars
    pros: List[str]
    cons: List[str]
    use_case: str

class ModernUILibraries:
    """Catálogo de librerías y herramientas para UI moderna en PySide6"""

    def __init__(self):
        self.libraries = self._initialize_libraries()
        self.categories = self._categorize_libraries()

    def _initialize_libraries(self) -> List[UILibrary]:
        """Inicializa el catálogo de librerías"""
        return [
            # Icon Libraries
            UILibrary(
                name="PyQt-Fluent-Widgets",
                category="Icon Libraries",
                description="Colección completa de iconos al estilo Microsoft Fluent Design",
                website="https://github.com/zhiyiYo/PyQt-Fluent-Widgets",
                pip_install="pip install pyqt-fluent-widgets",
                compatibility="PyQt6/PySide6",
                rating=5,
                pros=[
                    "Iconos modernos y consistentes",
                    "Soporte completo para temas claro/oscuro",
                    "Integración perfecta con PySide6",
                    "Gran variedad de iconos",
                    "Documentación clara"
                ],
                cons=[
                    "Enfoque específico en estilo Microsoft",
                    "Requiere adaptación para otros estilos"
                ],
                use_case="Aplicaciones Windows o con estilo Microsoft moderno"
            ),

            UILibrary(
                name="qtawesome",
                category="Icon Libraries",
                description="Librería de iconos para Qt/PySide basada en Font Awesome",
                website="https://github.com/spyder-ide/qtawesome",
                pip_install="pip install qtawesome",
                compatibility="PyQt5/PyQt6/PySide2/PySide6",
                rating=4,
                pros=[
                    "Basado en Font Awesome (iconos conocidos)",
                    "Múltiples estilos (regular, solid, brands)",
                    "Personalización de colores fácil",
                    "Compatible con todas las versiones de Qt",
                    "Liviano y rápido"
                ],
                cons=[
                    "Limitado a iconos Font Awesome",
                    "No incluye iconos personalizados modernos"
                ],
                use_case="Aplicaciones que necesitan iconos web estándar"
            ),

            # Animation Libraries
            UILibrary(
                name="pyqtgraph",
                category="Animation & Graphics",
                description="Librería gráfica científica con capacidades de animación avanzadas",
                website="https://github.com/pyqtgraph/pyqtgraph",
                pip_install="pip install pyqtgraph",
                compatibility="PyQt5/PyQt6/PySide2/PySide6",
                rating=4,
                pros=[
                    "Excelente para visualización de datos",
                    "Animaciones suaves y optimizadas",
                    "Gráficos 2D y 3D",
                    "Alto rendimiento con grandes conjuntos de datos",
                    "Integración perfecta con PySide6"
                ],
                cons=[
                    "Enfoque científico/gráfico, no UI general",
                    "Curva de aprendizaje para personalización"
                ],
                use_case="Dashboards, visualización de datos, aplicaciones científicas"
            ),

            # Theming & Styling
            UILibrary(
                name="QDarkStyleSheet",
                category="Theming & Styling",
                description="Hoja de estilos oscura para aplicaciones Qt/PySide",
                website="https://github.com/ColinDuquesnoy/QDarkStyleSheet",
                pip_install="pip install qdarkstyle",
                compatibility="PyQt5/PyQt6/PySide2/PySide6",
                rating=4,
                pros=[
                    "Tema oscuro profesional y consistente",
                    "Fácil implementación",
                    "Actualizaciones regulares",
                    "Soporte para múltiples widgets",
                    "Buen rendimiento"
                ],
                cons=[
                    "Limitado a tema oscuro",
                    "No tan personalizable como CSS nativo"
                ],
                use_case="Aplicaciones que necesitan un tema oscuro profesional rápido"
            ),

            # Component Libraries
            UILibrary(
                name="SuperQt",
                category="Component Libraries",
                description="Colección de widgets mejorados y utilidades para Qt",
                website="https://github.com/gmcmarquez/superqt",
                pip_install="pip install superqt",
                compatibility="PyQt5/PyQt6/PySide2/PySide6",
                rating=5,
                pros=[
                    "Sliders avanzados con múltiples controles",
                    "Widgets de color mejorados",
                    "Componentes de fecha/hora modernos",
                    "Buen rendimiento",
                    "Documentación completa"
                ],
                cons=[
                    "Librería grande (peso)",
                    "Algunos widgets pueden ser excesivos"
                ],
                use_case="Aplicaciones que necesitan widgets avanzados específicos"
            ),

            # Chart & Data Visualization
            UILibrary(
                name="PyQt-Charts",
                category="Charts & Data Viz",
                description="Bindings de Qt Charts para Python",
                website="https://doc.qt.io/qtforpython-6/PySide6/QtCharts/",
                pip_install="pip install PySide6-Charts",
                compatibility="PySide6",
                rating=4,
                pros=[
                    "Integración nativa con Qt",
                    "Soporte completo para diferentes tipos de gráficos",
                    "Animaciones suaves",
                    "Personalización completa",
                    "Buen rendimiento"
                ],
                cons=[
                    "Requiere instalación separada",
                    "Curva de aprendizaje moderada"
                ],
                use_case="Aplicaciones con necesidades de gráficos integrados"
            ),

            # Modern Components
            UILibrary(
                name="PyQtModernUI",
                category="Component Libraries",
                description="Colección de widgets modernos con efectos visuales",
                website="https://github.com/yjg30737/PyQtModernUI",
                pip_install="pip install PyQtModernUI",
                compatibility="PyQt5/PyQt6",
                rating=3,
                pros=[
                    "Widgets con efectos modernos",
                    "Botones con animaciones",
                    "Efectos de glassmorphism",
                    "Facil de usar"
                ],
                cons=[
                    "Limitado a widgets específicos",
                    "Menos mantenido últimamente",
                    "Principalmente para PyQt"
                ],
                use_case="Prototipado rápido con efectos modernos"
            ),

            # Color & Design Systems
            UILibrary(
                name="Colour",
                category="Color & Design",
                description="Librería de manipulación de colores para Python",
                website="https://github.com/vaab/colour",
                pip_install="pip install colour",
                compatibility="General Python",
                rating=4,
                pros=[
                    "Manipulación avanzada de colores",
                    "Conversión entre espacios de color",
                    "Generación de paletas",
                    "Útil para temas dinámicos",
                    "Integración con PySide6"
                ],
                cons=[
                    "Librería general, no específica de UI",
                    "Requiere código de integración"
                ],
                use_case="Sistemas de theming complejos y dinámicos"
            ),

            # 3D Graphics
            UILibrary(
                name="PyOpenGL",
                category="3D Graphics",
                description="Bindings de OpenGL para Python",
                website="http://pyopengl.sourceforge.net/",
                pip_install="pip install PyOpenGL PyOpenGL_accelerate",
                compatibility="General Python",
                rating=3,
                pros=[
                    "Acceso completo a OpenGL",
                    "Efectos 3D avanzados",
                    "Integración con PySide6 OpenGL widgets",
                    "Alto rendimiento gráfico"
                ],
                cons=[
                    "Curva de aprendizaje muy alta",
                    "Complejo de implementar",
                    "Requiere conocimiento de OpenGL"
                ],
                use_case="Aplicaciones con gráficos 3D complejos"
            ),

            # Icon Fonts
            UILibrary(
                name="Pillow (PIL)",
                category="Image Processing",
                description="Librería de procesamiento de imágenes para Python",
                website="https://pillow.readthedocs.io/",
                pip_install="pip install Pillow",
                compatibility="General Python",
                rating=5,
                pros=[
                    "Manipulación completa de imágenes",
                    "Redimensionamiento y filtros",
                    "Soporte para múltiples formatos",
                    "Integración con PySide6",
                    "Esencial para recursos gráficos"
                ],
                cons=[
                    "Librería general, no específica de UI",
                    "Puede ser lento para operaciones complejas"
                ],
                use_case="Procesamiento de imágenes, icons, recursos de aplicación"
            )
        ]

    def _categorize_libraries(self) -> Dict[str, List[UILibrary]]:
        """Organiza las librerías por categorías"""
        categories = {}
        for lib in self.libraries:
            if lib.category not in categories:
                categories[lib.category] = []
            categories[lib.category].append(lib)
        return categories

    def get_recommendations_by_use_case(self) -> Dict[str, List[UILibrary]]:
        """Obtiene recomendaciones basadas en casos de uso"""
        use_cases = {
            "Modern Desktop Application": [
                lib for lib in self.libraries
                if "PyQt-Fluent-Widgets" in lib.name or "SuperQt" in lib.name
            ],
            "Data Visualization Dashboard": [
                lib for lib in self.libraries
                if "pyqtgraph" in lib.name or "PyQt-Charts" in lib.name
            ],
            "Dark Mode Application": [
                lib for lib in self.libraries
                if "QDarkStyleSheet" in lib.name or "Colour" in lib.name
            ],
            "Prototype with Modern Effects": [
                lib for lib in self.libraries
                if "PyQtModernUI" in lib.name or "Glassmorphism" in lib.description
            ],
            "Icon-heavy Application": [
                lib for lib in self.libraries
                if lib.category == "Icon Libraries"
            ],
            "3D Graphics Application": [
                lib for lib in self.libraries
                if "3D" in lib.category or "OpenGL" in lib.name
            ]
        }
        return use_cases

    def generate_installation_script(self) -> str:
        """Genera un script de instalación para librerías recomendadas"""
        script = '''#!/usr/bin/env python3
"""
Modern UI Libraries Installation Script
Instala las librerías recomendadas para UI moderna en PySide6
"""

import subprocess
import sys
from typing import List

def install_package(package: str) -> bool:
    """Instala un paquete usando pip"""
    try:
        print(f"📦 Instalando {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {package} instalado correctamente")
            return True
        else:
            print(f"❌ Error instalando {package}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error crítico instalando {package}: {e}")
        return False

def main():
    """Función principal de instalación"""
    print("=" * 60)
    print("MODERN UI LIBRARIES INSTALLATION")
    print("=" * 60)

    # Librerías esenciales para UI moderna
    essential_packages = [
        "superqt",              # Widgets avanzados
        "qdarkstyle",           # Tema oscuro profesional
        "qtawesome",            # Iconos Font Awesome
        "colour",               # Manipulación de colores
        "Pillow",               # Procesamiento de imágenes
    ]

    # Librerías opcionales por categoría
    optional_packages = {
        "Iconos Modernos": [
            "pyqt-fluent-widgets",  # Iconos Fluent Design
        ],
        "Gráficos y Visualización": [
            "pyqtgraph",            # Gráficos científicos
        ],
        "Gráficos Qt": [
            "PySide6-Charts",       # Charts nativos de Qt
        ],
        "Gráficos 3D": [
            "PyOpenGL",             # OpenGL bindings
            "PyOpenGL-accelerate",  # Acelerador OpenGL
        ]
    }

    print("\\n🎯 INSTALANDO PAQUETES ESENCIALES")
    print("-" * 40)

    failed_packages = []
    for package in essential_packages:
        if not install_package(package):
            failed_packages.append(package)

    print("\\n📋 INSTALANDO PAQUETES OPCIONALES")
    print("-" * 40)

    for category, packages in optional_packages.items():
        print(f"\\n{category}:")
        for package in packages:
            install_package(package)

    # Resumen
    print("\\n" + "=" * 60)
    print("RESUMEN DE INSTALACIÓN")
    print("=" * 60)

    if failed_packages:
        print(f"⚠️  Paquetes que fallaron: {', '.join(failed_packages)}")
        print("💡 Revisa los errores e instala manualmente si es necesario")
    else:
        print("✅ Todas las librerías esenciales instaladas correctamente")

    print("\\n🚀 ¡Listo para comenzar con UI moderna en PySide6!")
    print("💡 Revisa la documentación de cada librería para ejemplos")
    print("=" * 60)

if __name__ == "__main__":
    main()
'''
        return script

    def create_integration_examples(self) -> Dict[str, str]:
        """Crea ejemplos de integración de librerías"""
        examples = {
            "superqt_integration": '''
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
''',

            "qtawesome_integration": '''
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
''',

            "qdarkstyle_integration": '''
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
'''
        }

        return examples

def main():
    """Función principal para demostrar el catálogo de librerías"""
    catalog = ModernUILibraries()

    print("=" * 70)
    print("MODERN UI LIBRARIES & TOOLS CATALOG FOR PYSIDE6")
    print("=" * 70)

    # Mostrar categorías
    print("\n📚 CATEGORÍAS DE LIBRERÍAS:")
    print("-" * 40)
    for category, libraries in catalog.categories.items():
        print(f"\n{category}:")
        for lib in libraries:
            rating_stars = "⭐" * lib.rating
            print(f"  • {lib.name} ({rating_stars}) - {lib.description[:50]}...")

    # Recomendaciones por caso de uso
    print("\n🎯 RECOMENDACIONES POR CASO DE USO:")
    print("-" * 40)
    recommendations = catalog.get_recommendations_by_use_case()

    for use_case, libs in recommendations.items():
        print(f"\n{use_case}:")
        for lib in libs:
            print(f"  • {lib.name}")

    # Generar script de instalación
    print("\n💻 GENERANDO SCRIPT DE INSTALACIÓN...")
    install_script = catalog.generate_installation_script()

    with open("install_modern_ui_libraries.py", 'w', encoding='utf-8') as f:
        f.write(install_script)
    print("✅ Creado: install_modern_ui_libraries.py")

    # Generar ejemplos de integración
    print("\n🔧 GENERANDO EJEMPLOS DE INTEGRACIÓN...")
    examples = catalog.create_integration_examples()

    for name, code in examples.items():
        filename = f"{name}_example.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'''#!/usr/bin/env python3
"""
Integration Example: {name.replace('_', ' ').title()}
Ejemplo de integración de librerías modernas con PySide6
"""

{code}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = YourAppClass()  # Reemplazar con la clase específica
    window.show()

    sys.exit(app.exec())
''')
        print(f"✅ Creado: {filename}")

    # Generar catálogo JSON
    print("\n📋 GENERANDO CATÁLOGO JSON...")
    catalog_data = {
        "generated_at": "2024-10-17",
        "categories": {},
        "recommendations": {}
    }

    for category, libraries in catalog.categories.items():
        catalog_data["categories"][category] = [
            {
                "name": lib.name,
                "description": lib.description,
                "rating": lib.rating,
                "compatibility": lib.compatibility,
                "install": lib.pip_install
            }
            for lib in libraries
        ]

    for use_case, libs in recommendations.items():
        catalog_data["recommendations"][use_case] = [lib.name for lib in libs]

    with open("modern_ui_libraries_catalog.json", 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)
    print("✅ Creado: modern_ui_libraries_catalog.json")

    print("\n" + "=" * 70)
    print("✅ CATÁLOGO COMPLETADO")
    print("\n📋 ARCHIVOS GENERADOS:")
    print("  • install_modern_ui_libraries.py - Script de instalación")
    print("  • [nombre]_example.py - Ejemplos de integración")
    print("  • modern_ui_libraries_catalog.json - Catálogo en JSON")
    print("\n💡 EJECUTA 'python install_modern_ui_libraries.py' para instalar")
    print("=" * 70)

if __name__ == "__main__":
    main()