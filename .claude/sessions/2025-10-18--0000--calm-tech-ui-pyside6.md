# Calm Tech UI PySide6
**Fecha:** 2025-10-18 00:00  
**Archivo guardado:** `.claude/sessions/2025-10-18--0000--calm-tech-ui-pyside6.md`  
**Tipo:** UI/UX ⭐⭐  
**Duración:** —  
**Estado:** ✅ Completado

## Objetivo
Introducir el diseño calm tech en la interfaz PySide6 y preparar la infraestructura híbrida Fluent/custom.

## Cambios clave
- Añadidos tokens compartidos, temas QSS y componentes base calm tech.
- Main window reorganizada con sidebar, toggle de tema y panel de logs.
- Demo y documentación técnica para la nueva arquitectura Qt.

## Errores / Incidencias
- Warnings `Unknown property transition` al cargar dashboard IoT (no bloqueante).
- Necesidad de `QT_QPA_PLATFORM=offscreen` cuando no hay servidor gráfico.

## Solución aplicada / Decisiones
- Usar enfoque híbrido Fluent + componentes propios.
- Mantener PySide6 nativo con theming calm tech reutilizable.
- Documentar tokens y roadmap en `docs/`.

## Archivos principales
- docs/calm_tech_design_system.md
- qt_ui/main.py
- qt_ui/ui/components/calm_custom.py

## Métricas
- LOC añadidas: —  
- Tests afectados: —  
- Impacto rendimiento: —

## Resultado
Interfaz PySide6 lista con layout calm tech, detección de Fluent widgets y demo funcional.

## Próximos pasos
- Sustituir widgets críticos por variantes Fluent.
- Implementar vistas reales para Insights/Configuración.
- Ajustar estilos con servidor gráfico y feedback en vivo.

## Riesgos / Consideraciones
- Dependencia de PyQt-Fluent-Widgets aún no aprovechada del todo.
- Necesidad de servidor gráfico en WSL para validar visualmente.
- Posible migración futura de SQLite a Postgres (evaluar impacto UI).

## Changelog (3 líneas)
- [2025-10-18] Añadido design system calm tech y tokens compartidos.
- [2025-10-18] Reorganizada main window PySide6 con sidebar y log viewer.
- [2025-10-18] Creada demo Qt y documentación técnica para la nueva capa UI.

## Anexo
—
