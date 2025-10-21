#!/usr/bin/env python3
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

    print("\n🎯 INSTALANDO PAQUETES ESENCIALES")
    print("-" * 40)

    failed_packages = []
    for package in essential_packages:
        if not install_package(package):
            failed_packages.append(package)

    print("\n📋 INSTALANDO PAQUETES OPCIONALES")
    print("-" * 40)

    for category, packages in optional_packages.items():
        print(f"\n{category}:")
        for package in packages:
            install_package(package)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE INSTALACIÓN")
    print("=" * 60)

    if failed_packages:
        print(f"⚠️  Paquetes que fallaron: {', '.join(failed_packages)}")
        print("💡 Revisa los errores e instala manualmente si es necesario")
    else:
        print("✅ Todas las librerías esenciales instaladas correctamente")

    print("\n🚀 ¡Listo para comenzar con UI moderna en PySide6!")
    print("💡 Revisa la documentación de cada librería para ejemplos")
    print("=" * 60)

if __name__ == "__main__":
    main()
