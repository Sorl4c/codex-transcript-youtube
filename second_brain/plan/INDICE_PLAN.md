# 📋 Índice del Plan RAG PostgreSQL

## 🎯 Objetivo del Plan
Crear un MVP PostgreSQL funcional que resuelva el problema de chunks duplicados y mejore la relevancia del retrieval mediante un experimento controlado de embedders.

## 📁 Estructura de Documentos

### 🌍 Documento Principal
- **[RAG_PostgreSQL_Migration_Plan_Global.md](RAG_PostgreSQL_Migration_Plan_Global.md)**
  - Visión completa del experimento de 3 días
  - Conexiones entre fases y criterios de éxito
  - Timeline resumido y pre-requisitos

### 📅 Documentos por Fase

#### 🗓️ Fase 1: Setup PostgreSQL + Ingestión Controlada
- **[Fase_1_Setup_Limpio.md](Fase_1_Setup_Limpio.md)**
  - **Duración:** 3-4 horas
  - **Objetivo:** Infraestructura limpia funcionando
  - **Checklists:** 7 pasos detallados ✅
  - **Entregables:** PostgreSQL + pgvector + 15 chunks ingeridos

#### 🔬 Fase 2: Experimento con Embedders Candidatos
- **[Fase_2_Experimento_Embedders.md](Fase_2_Experimento_Embedders.md)**
  - **Duración:** 4-5 horas
  - **Objetivo:** Comparar rendimiento y calidad
  - **Checklists:** 5 pasos con cache invalidation ✅
  - **Entregables:** Matriz de ingestión + 3 embedders probados
  - **Dataset con tres dominios (tecnología, aprendizaje, deporte) y chunks sintéticos**

#### ⚖️ Fase 3: Validación y Decisión Final
- **[Fase_3_Validacion_Decision.md](Fase_3_Validacion_Decision.md)**
  - **Duración:** 4-5 horas
  - **Objetivo:** Comparar calidad y decidir embedder
  - **Checklists:** 5 pasos con queries de prueba ✅
  - **Entregables:** Matriz de decisión + embedder seleccionado

## 🎛️ Configuración Clave

### Variables de Entorno
```bash
# Backend PostgreSQL
DATABASE_BACKEND=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_experiments
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password

# Embedding configurable
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIM=384
```

### Embedders en Evaluación
1. **all-MiniLM-L6-v2** (Control) - 384d, 80MB
2. **all-mpnet-base-v2** (Alta calidad) - 768d, 400MB
3. **paraphrase-multilingual-MiniLM-L12-v2** (Español) - 384d, 120MB

## 📊 Queries de Referencia

### Dataset de Prueba (5 queries)
1. **Query Técnica:** "¿Qué es Docker y cómo funciona?"
2. **Query Proceso:** "¿Cómo se instala PostgreSQL?"
3. **Query Definición:** "¿Qué son los embeddings?"
4. **Query Práctica:** "¿Para qué sirve el chunking?"
5. **Query Ambigua:** "Sistemas de bases de datos"

## 🎯 Criterios de Decisión

### Ponderación de Métricas
- **Relevancia (35%)**: Calidad de resultados 0-5
- **Tiempo Respuesta (25%)**: Latencia en ms
- **Recursos (15%)**: Uso de memoria
- **Soporte Español (15%)**: Cobertura lingüística
- **Estabilidad (10%)**: Consistencia de resultados

### Umbrales de Decisión
- **Score > 75/100**: Decisión clara ✅
- **Score 60-75/100**: Decisión moderada ⚖️
- **Score < 60/100**: Decisión dudosa ❓

## 📋 Checklist de Preparación

### Antes de Empezar
- [ ] PostgreSQL instalado localmente
- [ ] pgvector disponible
- [ ] Virtual environment activado
- [ ] transcripts_for_rag disponibles
- [ ] Dependencias instaladas

### Comandos Iniciales
```bash
# Verificar instalación
psql --version
python --version

# Crear BD experimental
createdb rag_experiments

# Activar entorno
source .venv/Scripts/activate

# Instalar dependencias
pip install psycopg[binary,pool] sentence-transformers
```

## 🏁 Punto de Partida

### Para Empezar Hoy
1. **Revisar el documento global** para entender la visión completa
2. **Verificar requisitos previos** en Fase 1, Paso 1
3. **Empezar con Fase 1** cuando estés listo
4. **Seguir checklists** paso a paso
5. **Documentar resultados** en los logs previstos

### Cache Invalidation Crítica
⚠️ **MUY IMPORTANTE:** Cada vez que cambies `EMBEDDING_DIM`:
```bash
# Limpiar cache de modelos
rm -rf ~/.cache/torch/sentence_transformers/
rm -rf ~/.cache/huggingface/

# Limpiar base de datos
psql -d rag_experiments -c "DROP TABLE IF EXISTS document_embeddings CASCADE;"

# Recrear schema con nueva dimensión
EMBEDDING_DIM=NUEVO_VALOR python setup_schema.py
```

## 📊 Archivos Generados

### Logs y Métricas
```
second_brain/plan/logs/
├── fase_1_metrics.json
├── fase_2a_mpnet_metrics.json
├── fase_2b_multilingual_metrics.json
├── fase_3_minilm_validation.json
├── fase_3_mpnet_validation.json
└── fase_3_multilingual_validation.json
```

### Resultados y Decisiones
```
second_brain/plan/results/
├── ingestion_matrix.json
├── fase_2_summary.json
├── final_decision_report.json
└── executive_summary.md
```

## 🔗 Validaciones Incluidas

### ✅ Schema con Duplicados Prevención
- `source_hash` UNIQUE (ya existe en pipeline)
- `CHECK array_length(embedding, 1) = EMBEDDING_DIM`
- `UNIQUE(document_id, embedding_type)`

### ✅ Cache Invalidation Strategy
- Limpieza completa entre cambios de embedder
- Reconstrucción de embeddings desde cero
- Validación de outputs crudos

### ✅ Query Fairness
- Mismos 10-20 chunks para todos los embedders
- Mismas 5 queries de referencia
- Outputs crudos guardados por separado

## 🚀 Progreso del Experimento

### Fase 1: Setup PostgreSQL (Día 1)
- [ ] Verificar instalación PostgreSQL + pgvector
- [ ] Crear schema paramétrico con EMBEDDING_DIM
- [ ] Seleccionar dataset 10-20 chunks representativos
- [ ] Ingerir con MiniLM (384 dimensiones)

### Fase 2: Experimento Embedders (Día 2)
- [ ] Probar MPNet (768 dimensiones)
- [ ] Probar Multilingual (384 dimensiones)
- [ ] Registrar métricas de ingestión
- [ ] Crear matriz de rendimiento

### Fase 3: Validación (Día 3)
- [ ] Ejecutar 5 queries por embedder
- [ ] Evaluar relevancia y tiempos
- [ ] Completar matriz de decisión
- [ ] Seleccionar embedder final

## 🎖️ Éxito del Proyecto

### ✅ Éxito si:
- PostgreSQL funciona sin duplicados
- Al menos un embedder supera claramente a los demás
- Tiempos de respuesta aceptables (< 500ms)
- Relevancia mejorada vs actual
- Sistema listo para producción con backend seleccionado

### ❌ Fracaso si:
- PostgreSQL también genera duplicados
- Todos los embedders tienen rendimiento similar
- Ningún embedder mejora la relevancia actual
- Tiempos de respuesta inaceptables (> 2s)

## 🔄 Próximos Pasos Después del Experimento

### Si Éxito (Score > 70)
1. **Implementar PostgreSQLVectorDatabase** definitiva
2. **Refactorizar retriever** actual con nuevo backend
3. **Testing completo** de integración
4. **Documentar patrones** aprendidos

### Si Fracaso (Score < 60)
1. **Investigar root cause** del problema de retrieval
2. **Experimentar con configuraciones adicionales**
3. **Considerar otros embedders** no probados
4. **Revisar enfoque general** del problema

---

**📅 Fecha de creación:** $(date)
**🎯 Estado:** Listo para ejecución
**📋 Preparado por:** Sistema de Planificación Automática