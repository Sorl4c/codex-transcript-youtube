# /crear_historial

Genera un documento de historial de sesión en formato Markdown.  
El título debe deducirse automáticamente según el contexto (archivos modificados, cambios recientes, propósito de la sesión).  
El resultado se guarda automáticamente en `.claude/sessions/` con nombre `YYYY-MM-DD--HHmm--<slug-del-titulo>.md`.

El documento debe tener esta estructura:

# <Título detectado>
**Fecha:** YYYY-MM-DD HH:MM  
**Archivo guardado:** `.claude/sessions/YYYY-MM-DD--HHmm--<slug>.md`  
**Tipo:** [Categoría deducida] Dificultad (⭐–⭐⭐⭐)  
**Duración:** —  
**Estado:** ✅ Completado | 🔄 En progreso | ❌ Falló

## Objetivo
Frase breve deducida del propósito.

## Cambios clave
- Punto 1  
- Punto 2  
- Punto 3  

## Errores / Incidencias
- —

## Solución aplicada / Decisiones
- —

## Archivos principales
- —

## Métricas
- LOC añadidas: —  
- Tests afectados: —  
- Impacto rendimiento: —  

## Resultado
Resumen en una línea del valor final.

## Próximos pasos
- Tarea 1  
- Tarea 2  
- Tarea 3  

## Riesgos / Consideraciones
- Riesgo 1  
- Riesgo 2  
- Riesgo 3  

## Changelog (3 líneas)
- [YYYY-MM-DD] Cambio breve 1  
- [YYYY-MM-DD] Cambio breve 2  
- [YYYY-MM-DD] Cambio breve 3  

## Anexo
Fragmento de diff/logs/notas o “—”.
