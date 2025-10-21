# Migración desde Flet a PySide6 - Decisión de Framework UI

**Fecha:** 2025-10-17 14:16
**Archivo guardado:** `.claude/sessions/2025-10-17--1416--migracion-flet-pyside6-y-decision-tecnologica.md`
**Tipo:** Framework GUI / Migración Tecnológica Dificultad (⭐⭐)
**Duración:** ~1 hora
**Estado:** 🔄 En progreso

## Objetivo
Evaluar y migrar la interfaz gráfica desde Flet a PySide6 debido a problemas de rendimiento y estabilidad con Flet.

## Cambios clave
- Migración exitosa desde Flet 0.70.0.dev6333 (alpha) a Flet 0.28.3 (estable)
- Corrección de imports relativos en todos los archivos del directorio `flet_ui/`
- Solución de conflictos de nombres entre `utils.py` (proyecto) y `utils/` (Flet UI)
- Renombrado de `utils/` a `flet_utils/` para evitar colisiones
- Configuración de PYTHONPATH para imports relativos y módulos del proyecto
- Instalación de librería multimedia `libmpv2` y creación de symlink para compatibilidad

## Errores / Incidencias
- **Error de versión Flet:** `ft.app() is deprecated` en versión alpha
- **Error de módulos:** `ModuleNotFoundError: No module named 'flet_ui'`
- **Conflicto de nombres:** `utils.py` vs `utils/` directory
- **Error de librería multimedia:** `libmpv.so.1: cannot open shared object file`
- **Problema de imports:** Relative imports no funcionaban sin configuración adecuada

## Solución aplicada / Decisiones
- **Downgrade de Flet:** Migración desde versión alpha a estable 0.28.3
- **Corrección sistemática de imports:** Conversión de `from flet_ui.*` a imports relativos
- **Renombrado de directorio:** `utils/` → `flet_utils/` para evitar conflictos
- **Configuración de path:** Agregar directorios actual y padre al PYTHONPATH
- **Solución multimedia:** Crear symlink `libmpv.so.1 → libmpv.so.2`

## Archivos principales
- `flet_ui/main.py` - Punto de entrada con configuración de path
- `flet_ui/core/app.py` - Controlador principal de aplicación
- `flet_ui/requirements-flet.txt` - Dependencias con versión estable
- `test_flet_tabs.py` - Ejemplo de prueba para verificar funcionalidad
- Múltiples archivos de componentes con imports corregidos

## Métricas
- LOC añadidas: ~50 líneas (configuración de path y correcciones)
- Tests afectados: 1 (test_flet_tabs.py)
- Impacto rendimiento: Flet estable significativamente más estable que alpha

## Resultado
Flet UI completamente funcional con versión estable, pero se descarta en favor de PySide6 por mejor rendimiento.

## Próximos pasos
- Implementar interfaz principal con PySide6
- Migrar componentes clave desde Flet a PySide6
- Mejorar apariencia gráfica de la interfaz PySide6
- Integrar con módulos existentes del proyecto (db, parser, downloader)
- Pruebas de rendimiento comparativas entre frameworks

## Riesgos / Consideraciones
- **Curva de aprendizaje:** PySide6 requiere熟悉 con Qt framework
- **Compatibilidad:** Asegurar que todos los módulos del proyecto funcionen con PySide6
- **Estética:** PySide6 requiere más trabajo para apariencia atractiva vs Flet
- **Mantenimiento:** Qt/PySide6 tiene dependencias más pesadas que Flet

## Changelog (3 líneas)
- [2025-10-17] Migración Flet desde versión alpha a estable 0.28.3
- [2025-10-17] Corrección completa de imports relativos en directorio flet_ui/
- [2025-10-17] Decisión de migrar a PySide6 por mejor rendimiento

## Anexo
```bash
# Comandos clave ejecutados
pip uninstall flet flet-cli flet-desktop -y
pip install flet==0.28.3
find flet_ui -name "*.py" -exec sed -i 's/from flet_ui\./from /g' {} \;
cd flet_ui && mv utils flet_utils
find . -name "*.py" -exec sed -i 's/from utils\./from flet_utils./g' {} \;
sudo ln -sf /usr/lib/x86_64-linux-gnu/libmpv.so.2 /usr/lib/x86_64-linux-gnu/libmpv.so.1
```