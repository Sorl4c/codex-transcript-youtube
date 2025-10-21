# Plan RAG PostgreSQL Migration - Experimento Controlado de Embedders

**Fecha:** 2025-01-18 23:36
**Archivo guardado:** `.claude/sessions/2025-01-18--2336--plan-rag-postgresql-migration.md`
**Tipo:** [Infraestructura] Dificultad (⭐⭐)
**Duración:** 3-4 días (3 fases principales)
**Estado:** ✅ Completado

## Objetivo
Crear un MVP PostgreSQL funcional que resuelva el problema de chunks duplicados en el sistema RAG mediante un experimento controlado de 3 embedders diferentes.

## Cambios clave
- Diseño de experimento controlado con backends separados (SQLite solo lectura, PostgreSQL experimental limpia)
- Schema paramétrico con EMBEDDING_DIM configurable (384/768 dimensiones)
- Estrategia de cache invalidación completa entre cambios de embedder
- Sistema de evaluación con 5 queries de referencia y métricas ponderadas
- Matriz de decisión objetiva con scores calculados automáticamente

## Errores / Incidencias
- Necesidad de validar que source_hash ya existía en el pipeline actual para evitar duplicados
- Corrección de schema paramétrico para que vector(384) se reemplace dinámicamente
- Definición clara de estructura de archivos para logs, resultados y outputs crudos

## Solución aplicada / Decisiones
- Enfoque MVP sin factory pattern inicialmente para evitar distracciones
- Dataset controlado de 15 chunks representativos del transcripts_for_rag existente
- Ponderación de decisiones: Relevancia(35%) + Tiempo(25%) + Recursos(15%) + Español(15%) + Estabilidad(10%)
- Umbrales claros: Score > 75/100 = decisión clara, 60-75 = moderada, < 60 = dudosa

## Archivos principales
- `RAG_PostgreSQL_Migration_Plan_Global.md` - Visión completa y conexiones entre fases
- `Fase_1_Setup_Limpio.md` - 7 pasos con checklists detallados (3-4 horas)
- `Fase_2_Experimento_Embedders.md` - 5 pasos con cache invalidation (4-5 horas)
- `Fase_3_Validacion_Decision.md` - 5 pasos con queries de prueba (4-5 horas)
- `INDICE_PLAN.md` - Navegación rápida y punto de partida ideal
- Scripts de implementación: setup_schema.py, ingest_fase1.py, create_decision_matrix.py

## Métricas
- LOC añadidas: ~2,000 líneas de documentación + scripts
- Tests afectados: 0 (fase de planificación)
- Impacto rendimiento: Potencial mejora de retrieval (eliminación de duplicados)
- Documentos creados: 5 archivos principales + índice + scripts auxiliares

## Resultado
Plan completo y validado para migrar el sistema RAG de SQLite a PostgreSQL con selección objetiva del mejor embedder mediante experimento controlado.

## Próximos pasos
- Ejecutar Fase 1: Verificación de PostgreSQL + pgvector + ingestión controlada
- Ejecutar Fase 2: Experimento con 3 embedders (MiniLM, MPNet, Multilingüe)
- Ejecutar Fase 3: Validación comparativa y decisión final basada en matriz objetiva
- Opcional Fase 4: Refactor del retriever con embedder ganador seleccionado

## Riesgos / Consideraciones
- Riesgo de que PostgreSQL también genere duplicados (indicaría problema en el algoritmo, no en el backend)
- Complejidad de cache invalidación requiere seguimiento estricto entre cambios de embedder
- Tiempo total estimado: 11-18 horas distribuidas en 3-4 días
- Dependencia de instalación local de PostgreSQL + pgvector

## Changelog (3 líneas)
- [2025-01-18] Diseño completo del plan de migración RAG a PostgreSQL con experimento controlado
- [2025-01-18] Creación de documentación detallada con checklists y validaciones específicas
- [2025-01-18] Definición de estrategia de evaluación objetiva con matriz de decisión ponderada

## Anexo
Estructura del experimento:

**Embedders a evaluar:**
1. all-MiniLM-L6-v2 (Control) - 384d, 80MB, inglés básico
2. all-mpnet-base-v2 (Alta calidad) - 768d, 400MB, inglés mejorado
3. paraphrase-multilingual-MiniLM-L12-v2 (Español) - 384d, 120MB, multilingüe

**Criterios de evaluación:**
- Relevancia de resultados (0-5 subjetivo)
- Tiempo de respuesta (< 500ms ideal)
- Uso de memoria (menor es mejor)
- Soporte para español (crítico para use case)
- Estabilidad/consistencia de resultados

**Estructura de archivos generada:**
```
second_brain/plan/
├── logs/                    # Métricas por fase
├── results/                 # Matrices y decisiones
├── outputs/                  # Outputs crudos
├── *.md                     # Documentación principal
└── *.py                     # Scripts de implementación
```