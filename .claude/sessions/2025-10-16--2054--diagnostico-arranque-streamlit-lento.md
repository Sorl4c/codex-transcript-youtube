# Diagnóstico de arranque Streamlit lento
**Fecha:** 2025-10-16 20:54  
**Archivo guardado:** `.claude/sessions/2025-10-16--2054--diagnostico-arranque-streamlit-lento.md`  
**Tipo:** Debugging ⭐⭐  
**Duración:** —  
**Estado:** 🔄 En progreso

## Objetivo
Analizar la lentitud del arranque de la app Streamlit y mejorar la visibilidad del proceso de carga.

## Cambios clave
- Refactor del `RAGInterface` para inicializar base/vector y embedder bajo demanda.
- Instrumentación con logs y tiempos de inicialización en `gui_streamlit.py`.
- Confirmación de que la carga sigue lenta en WSL pese a lazy-loading.

## Errores / Incidencias
- Arranque de Streamlit continúa tardando varios minutos en WSL.

## Solución aplicada / Decisiones
- Mantener lazy-loading de RAG y añadir telemetría detallada para detectar el cuello de botella.

## Archivos principales
- `rag_interface.py`
- `gui_streamlit.py`

## Métricas
- LOC añadidas: ~110  
- Tests afectados: —  
- Impacto rendimiento: Visibilidad de tiempos de arranque, sin resolver lentitud

## Resultado
Se documentó la sesión y se dejaron logs para investigar el arranque lento que permanece pendiente.

## Próximos pasos
- Revisar los nuevos logs de arranque para ubicar la fase que bloquea.
- Comparar desempeño entre WSL y Windows nativo para aislar diferencias de entorno.
- Diseñar una estrategia de precarga opcional o profiling profundo según hallazgos.

## Riesgos / Consideraciones
- Persistencia del cuello de botella sin diagnóstico completo.
- Verbosidad de logs en producción si no se acota.
- Posibles issues de E/S en WSL que requieran cambios sistémicos.

## Changelog (3 líneas)
- [2025-10-16] Lazy-loading y reutilización de recursos en `rag_interface.py`.
- [2025-10-16] Logs de inicialización y métricas de arranque en `gui_streamlit.py`.
- [2025-10-16] Registro de pendientes para resolver demora en WSL.

## Anexo
—
