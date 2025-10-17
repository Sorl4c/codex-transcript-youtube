# Dashboard IoT Moderno con PySide6

Proyecto basado en el tutorial: "Crea un Dashboard IoT Moderno con Python | PyQt6 + Qt Designer", adaptado a PySide6.

## Características

- Dashboard IoT moderno con diseño profesional
- Menú lateral con 7 opciones de navegación
- Barras de progreso circulares personalizadas
- Gráficas interactivas (línea y barras)
- Tabla de dispositivos con datos JSON
- Calendario personalizado
- Sliders interactivos
- Diseño con degradados y colores modernos

## Instalación

1. Clonar el repositorio o descargar los archivos
2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
dashboard_iot/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias
├── assets/
│   ├── icons/             # Iconos SVG
│   └── images/            # Imágenes
├── ui/
│   ├── main_window.ui     # Diseño principal
│   └── styles/
│       └── dashboard.css  # Hojas de estilo
├── src/
│   ├── main_window.py     # Ventana principal
│   ├── charts/
│   │   ├── line_chart.py  # Gráfica de línea
│   │   └── bar_chart.py   # Gráfica de barras
│   ├── widgets/
│   │   ├── circular_progress.py
│   │   └── custom_slider.py
│   └── data_manager.py    # Gestión de datos
└── data/
    ├── devices.json       # Datos de dispositivos
    └── sensor_data.json   # Datos de sensores
```

## Ejecución

```bash
python main.py
```

## Desarrollo

Este proyecto está organizado en fases según el plan detallado en `Dashboard-tutorial.md`.

### Fases del Proyecto

1. **Configuración del entorno** - Dependencias y estructura
2. **Diseño en Qt Designer** - Interfaz visual principal
3. **Página del Dashboard** - Barras de progreso y gráficas
4. **Página de Dispositivos** - Tabla y calendario
5. **Funcionalidad** - Lógica y navegación
6. **Estilos** - CSS y personalización visual
7. **Datos IoT** - Simulación y conectividad
8. **Optimización** - Rendimiento y testing
9. **Características avanzadas** - Funcionalidades opcionales
10. **Deploy** - Empaquetado y distribución

## Requisitos

- Python 3.8+
- PySide6
- Matplotlib
- NumPy
- Qt Designer (incluido en PySide6)

## Licencia

Proyecto educativo basado en tutorial de YouTube.
