# Calm Tech Qt Design Notes

Este paquete reutiliza el documento principal `docs/calm_tech_design_system.md`
ubicado en la raíz del repositorio. Aquí se incluyen notas concretas sobre cómo
se traslada ese diseño a PySide6 + PyQt-Fluent-Widgets.

- Tokens compartidos se obtienen desde `ui/theme.py` y se serializan mediante
  `qt_ui/ui/design_tokens.py`.
- Los estilos base se almacenan en `qt_ui/ui/themes/*.qss`.
- Componentes Fluent se importan a través de `qt_ui/ui/components/fluent_base.py`
  para facilitar el manejo de entornos sin la librería instalada.
- Componentes personalizados (VideoCard, CalmSidebar, etc.) residen en
  `qt_ui/ui/components/calm_custom.py` y evolucionarán con el roadmap.

> Para detalles completos de colores, tipografía, microcopy y accesibilidad,
> consulta el documento principal en `docs/calm_tech_design_system.md`.

