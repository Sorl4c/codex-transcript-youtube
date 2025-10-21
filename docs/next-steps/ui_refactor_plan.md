
# UI Refactor Roadmap (Iteración Actual)

Este plan detalla los siguientes pasos para implementar el diseño calm tech en las interfaces Tkinter y PySide6.

## 1. Preparación y Diseño

- ~~Validar tokens de `ui/theme.py` en ambos frameworks; ajustar si hay incompatibilidades.~~ ✔️
- Crear mockups de alta fidelidad para:
  - Pantalla principal (videoteca + panel de tareas).
  - Wizard de ingesta en modal.
  - Panel de logs plegable.
- Documentar microcopy clave (mensajes de error/éxito) en `docs/microcopy.md`.

## 2. Refactorización de Tkinter (`gui.py`)

- Introducir `NavigationPane`, `TaskBoard`, `LogDrawer` y `VideoDetailCard` como clases separadas.
- Integrar `apply_tkinter_theme` para colores base.
- Reemplazar lista actual por vista de tabla + tarjetas con badges.
- Implementar panel de tareas con barra de progreso y acceso rápido a logs.
- Añadir wizard de ingesta (3 pasos) reutilizando la lógica existente.

## 3. Refactorización de PySide6 (`qt_ui/`)

- ~~Crear `ui/themes/calm_tech.qss` usando `generate_qss`.~~ ✔️
- ~~Actualizar `qt_ui/main.py` para montar layout maestro (sidebar + tabs + log drawer).~~ ✔️
- Reutilizar componentes creados en Tkinter como guía funcional (nomenclatura, flujos).
- ~~Añadir soporte de tema oscuro/claro con toggle que use `toggle_mode`.~~ ✔️

## 4. Accesibilidad y Feedback

- Definir atajos globales (`Ctrl+L`, `Ctrl+Shift+A`, `Ctrl+Tab`).
- Implementar toasts simples (Tkinter: ventanas transient, PySide6: `QSystemTrayIcon` o overlay).
- Añadir barra de progreso persistente en panel de tareas; log estructurado con filtros por severidad.

## 5. Validación

- Ejecutar `python -m compileall gui.py qt_ui` para asegurar consistencia.
- Probar flujos clave manualmente (ingesta única, batch, visualización de resumen).
- Revisar contraste y tamaños con checklist WCAG 2.1 AA.
- Capturar screenshots antes/después para documentar en `docs/calm_tech_design_system.md`.

> Este roadmap se basa en el borrador de diseño calm tech y evolucionará con feedback práctico.
