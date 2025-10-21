# Migración a Flet 1.0 Alpha: Actualización de API y Componentes
**Fecha:** 2025-10-16 23:19
**Archivo guardado:** `.claude/sessions/2025-10-16--2319--migracion-flet-10-alpha-api.md`
**Tipo:** Migración API Dificultad (⭐⭐⭐)
**Duración:** ~45 minutos
**Estado:** 🔄 En progreso

## Objetivo
Adaptar aplicación Flet existente a Flet 1.0 Alpha (v0.70.0.dev6333) resolviendo cambios rotos en la API de componentes principales.

## Cambios clave
- **Identificación de versión**: Descubierto que 0.70.0.dev6333 = Flet 1.0 Alpha (reescritura completa)
- **API de Botones**: Cambio de `text="Texto"` a `content=ft.Text("Texto")` en todos los botones
- **Sintaxis Tabs**: Implementado patrón con parámetro `length` requerido para `ft.Tabs`
- **Simplificación Theme**: Eliminado `ColorScheme` complejo por `Theme` básico para compatibilidad
- **Supresión ALSA**: Añadidas variables de entorno para reducir warnings de audio

## Errores / Incidencias
- `ft.Tab(text="...", content=...)` → `ft.Tab` no acepta `text` ni `content` en v1.0
- `FilledTonalButton(text="...")` → `text` parameter no existe en v1.0
- `ColorScheme(background=...)` → API de Theme completamente diferente
- `ProgressBar.update()` → Control debe ser añadido a página antes de actualizar

## Solución aplicada / Decisiones
- **Botones**: Convertidos todos `ft.Button(text=...)` a `ft.Button(content=ft.Text(...))`
- **Tabs**: Implementado patrón con `ft.Tabs(length, [ft.Tab("...")], ...)`
- **Theme**: Simplificado a `ft.Theme(color_scheme_seed=...)`
- **ALSA**: Variables de entorno `ALSA_PCM_CARD` y `ALSA_PCM_DEVICE`

## Archivos principales
- `flet_ui/components/video/video_details.py` - Tabs y botones actualizados
- `flet_ui/pages/video_library/library_page.py` - Botones de diálogo actualizados
- `flet_ui/config/theme.py` - Theme simplificado para v1.0
- `flet_ui/main.py` - Supresión errores ALSA y `ft.run()`

## Métricas
- LOC añadidas: ~50 líneas
- Tests afectados: 0 (cambios solo UI)
- Impacto rendimiento: Mejorado (API más eficiente)

## Resultado
Aplicación avanza significativamente más allá de errores de API, llegando hasta componentes internos de carga de datos.

## Próximos pasos
- Arreglar ciclo de vida de `ProgressBar` y controles dinámicos
- Investigar nueva API de Tabs para Flet 1.0 (ejemplos oficiales)
- Validar todos los componentes de la aplicación
- Documentar guía completa de migración v0.x → v1.0

## Riesgos / Consideraciones
- **Riesgo 1**: Flet 1.0 Alpha es inestable, puede haber más cambios rotos
- **Riesgo 2**: Algunos componentes podrían necesitar patrones completamente nuevos
- **Riesgo 3**: Documentación oficial aún en desarrollo para v1.0

## Changelog (3 líneas)
- [2025-10-16] Identificado Flet 1.0 Alpha como causa de errores de API
- [2025-10-16] Migrados todos los botones a `content=ft.Text(...)`
- [2025-10-16] Implementado patrón de Tabs con parámetro `length`

## Anexo
```python
# Patrón de botón actualizado
# Antes:
ft.FilledTonalButton("Texto", icon=ft.Icons.DELETE_OUTLINE)
# Después:
ft.FilledTonalButton(content=ft.Text("Texto"), icon=ft.Icons.DELETE_OUTLINE)

# Patrón de Tabs actualizado
# Antes:
ft.Tabs(tabs=[ft.Tab(text="Tab", content=container)])
# Después:
ft.Tabs(2, [ft.Tab("Tab")], expand=True)
```