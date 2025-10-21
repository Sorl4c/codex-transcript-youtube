# Implementación Técnica (Qt Calm Tech)

## Objetivo

Construir una capa de componentes modernos utilizando PySide6 como base y
PyQt-Fluent-Widgets para acelerar la entrega de UI contemporánea.

## Paquetes Clave

- `ui/theme.py`: tokens compartidos entre Tkinter, Streamlit y PySide6.
- `qt_ui/ui/design_tokens.py`: serializa tokens a un formato simple para Qt/QSS.
- `qt_ui/ui/components/fluent_base.py`: punto único de importación de
  PyQt-Fluent-Widgets (cachea y controla errores).
- `qt_ui/ui/components/calm_custom.py`: widgets personalizados con estética calm tech.
- `qt_ui/ui/themes/*.qss`: estilos base por modo (light, dark, high contrast).

## Flujo de Integración

1. Llamar a `ensure_fluent_available()` durante la inicialización de la app Qt
   para validar que PyQt-Fluent-Widgets esté presente.
2. Cargar el QSS adecuado según modo seleccionado (`calm_light.qss`, etc.).
3. Construir la ventana usando mezcla de componentes Fluent + custom.
4. Conectar eventos a los componentes custom (p. ej. `CalmSidebar.activated`).
5. Para el panel principal, utilizar helpers de `layout_manager.ColumnConfig`
   al calcular anchos en diseños manuales.

## Próximos pasos

- Crear wrappers específicos (por ejemplo `CalmFluentButton`) que apliquen los
  tokens directamente sobre componentes Fluent.
- Añadir pruebas de snapshot para confirmar que los QSS cargan correctamente.
- Integrar el wizard de ingestión y dashboards según el roadmap aprobado.

