# Plan MVP RAG + Roadmap Multi-Sesión

## 🎯 SESIÓN 1: MVP CLI RAG Query ✅ COMPLETADA

**Fecha:** 30 Septiembre 2025
**Commits:** `80b7440`, `0d6131e`, `21c796b`

### Objetivo
Crear CLI mínimo funcional para probar recuperación RAG sin llamadas API continuas

### ✅ Implementado

1. **`rag_engine/retriever.py`** - SimpleRetriever con búsqueda semántica
   - Clase `SimpleRetriever` con método `query(question, top_k)`
   - Usa `database.search_similar()` existente
   - Retorna `List[SearchResult]` con contenido y score

2. **`rag_engine/rag_cli.py`** - CLI completo con 3 comandos
   - `stats` - Estadísticas de BD (88 documentos, 1.03 MB)
   - `query "<pregunta>" --top-k N` - Búsqueda semántica
   - `ingest <file> --mock` - Ingesta con chunking simple (sin LLM)

3. **LocalEmbedder configurado**
   - Modelo: `all-MiniLM-L6-v2` (sentence-transformers)
   - Forzado a CPU para evitar problemas CUDA sm_120 (RTX 5070 Ti)
   - Sin dependencias de APIs externas

4. **Dependencias agregadas a `requirements.txt`**
   - `sentence-transformers>=5.1.0`
   - `sqlite-vec>=0.1.6`
   - `scikit-learn>=1.7.0`

5. **Venv recreado correctamente**
   - Eliminado venv roto (symlinks Linux/Windows)
   - Creado nuevo venv con Python 3.13.5
   - Todas las deps instaladas en `venv-yt-ia/`

### ✅ Probado y funcionando
```bash
# Activar venv PRIMERO
venv-yt-ia\Scripts\activate

# Comandos CLI
python -m rag_engine.rag_cli stats
python -m rag_engine.rag_cli query "What is deep learning?" --top-k 3
python -m rag_engine.rag_cli ingest transcripts_for_rag/sample.txt --mock
```

### 📝 Notas importantes
- ⚠️ **SIEMPRE activar venv antes de cualquier comando**
- Embeddings 100% locales, sin costos de API
- Base de datos ya tiene 88 documentos de sesiones anteriores
- CLI compatible con Windows (sin emojis, encoding UTF-8)

---

## 📋 SESIÓN 2: RAG Híbrido + BM25 ✅ COMPLETADA

**Fecha:** 01 Octubre 2025

### Objetivo
Implementar búsqueda híbrida combinando retrieval semántico (vector) y lexical (BM25) con fusión RRF

### ✅ Implementado

1. **`rag_engine/hybrid_retriever.py`** - HybridRetriever con 3 modos
   - Clase `HybridRetriever` extendiendo `SimpleRetriever`
   - **Vector mode**: Búsqueda semántica pura (embeddings)
   - **Keyword mode**: Búsqueda lexical BM25 (rank-bm25)
   - **Hybrid mode**: Reciprocal Rank Fusion (RRF) de ambas
   - RRF con k=60 (paper original)
   - Provenance tracking (vector_rank, bm25_rank, scores individuales)

2. **`rag_engine/rag_cli.py`** - CLI actualizado con flag `--mode`
   - `query "<pregunta>" --mode vector|keyword|hybrid`
   - Modo vector como default (compatibilidad con Sesión 1)
   - Display de provenance para resultados híbridos

3. **`rag_engine/test_queries.json`** - 12 queries de evaluación
   - Queries de fitness (triceps, brazos, hipertrofia)
   - Queries de AI/tech (deep learning, inteligencia artificial)
   - Queries irrelevantes (clima, cambio climático)
   - Cada query con relevant_keywords para evaluación automática

4. **`rag_engine/evaluate.py`** - Sistema de evaluación con métricas IR
   - **Recall@5**: Proporción de documentos relevantes en top-5
   - **MRR (Mean Reciprocal Rank)**: Promedio de reciprocal rank del primer relevante
   - Evaluación automática con keyword matching como ground truth
   - Reporte comparativo de los 3 modos
   - Guardado de resultados en JSON

5. **Dependencia agregada**: `rank-bm25>=0.2.0` en `requirements.txt`

### 📊 Resultados de Evaluación

**Comparativa sobre 88 documentos y 12 test queries:**

| Modo    | Recall@5 | MRR    | Observaciones |
|---------|----------|--------|---------------|
| Vector  | 0.8333   | 0.9583 | Buena semántica, pierde algunos términos exactos |
| Keyword | 0.9667   | 1.0000 | **MEJOR** - Excelente para matching exacto |
| Hybrid  | 0.9333   | 1.0000 | Segundo mejor, combina ambas fortalezas |

**Conclusiones:**
- ✅ **BM25 keyword search es superior** en este dataset específico
- El corpus actual tiene mucha terminología específica (nombres de ejercicios, conceptos técnicos)
- BM25 captura mejor los términos exactos ("press francés", "cabeza larga")
- Hybrid mantiene MRR perfecto (1.0) pero Recall@5 ligeramente menor que keyword puro
- Vector search (semántico) es el menos efectivo en este caso específico
- **Recomendación**: Usar `--mode keyword` o `--mode hybrid` para mejor rendimiento

### ✅ Probado y funcionando

```bash
# Activar venv PRIMERO
venv-yt-ia\Scripts\activate

# Queries con diferentes modos
python -m rag_engine.rag_cli query "ejercicios para triceps" --mode vector
python -m rag_engine.rag_cli query "ejercicios para triceps" --mode keyword
python -m rag_engine.rag_cli query "ejercicios para triceps" --mode hybrid

# Evaluación completa
python -m rag_engine.evaluate
```

### ⚠️ Nota importante sobre sintaxis CLI
El flag `--mode` requiere un **ESPACIO** antes de los guiones:
- ✅ **CORRECTO**: `query "pregunta" --mode vector` (con espacio)
- ❌ **INCORRECTO**: `query "pregunta"--mode vector` (sin espacio - error de parsing)

### 📝 Notas importantes
- ⚠️ **SIEMPRE activar venv antes de cualquier comando**
- BM25 requiere cargar todo el corpus en memoria (acceptable para <10k docs)
- RRF usa k=60 (configurable en HybridRetriever)
- Evaluation usa keyword matching como proxy de relevancia (no requiere anotaciones manuales)
- Results saved to `rag_engine/evaluation_results.json`

---

## 📋 SESIÓN 3: Schema v2 Multi-Chunking ✅ COMPLETADA

**Fecha:** 01 Octubre 2025

### Objetivo
Implementar schema de base de datos mejorado (v2) que almacene metadata de chunking strategy, permitiendo comparar estrategias semantic vs agentic en el mismo sistema RAG.

### ✅ Implementado

1. **`rag_engine/database.py`** - Schema v2 con metadata completo
   - Tabla `vector_store` con 14 columnas:
     - Tracking: `source_document`, `source_hash`, `chunking_strategy`
     - Posicionamiento: `chunk_index`, `char_start`, `char_end`
     - Metadata agentic: `semantic_title`, `semantic_summary`, `semantic_overlap`
     - Extensible: `metadata_json` (JSON para keywords y otros)
     - Timestamp: `created_at`
   - Método nuevo: `add_documents_with_metadata()`
   - Método legacy: `add_documents()` (backward compatible)
   - 4 índices para búsquedas eficientes (strategy, source, hash, content)

2. **`rag_engine/ingestor.py`** - Pipeline mejorado con metadata tracking
   - Parámetro `source_document` para tracking de origen
   - Calcula `source_hash` (MD5) para deduplicación
   - Extrae automáticamente metadata de Chunk objects
   - Guarda keywords en `metadata_json`
   - Summary mejorado con strategy y hash info

3. **`rag_engine/rag_cli.py`** - CLI actualizado
   - Pasa filepath absoluto como `source_document`
   - Display mejorado mostrando strategy, source_hash
   - Compatible con schema v2

4. **`rag_engine/agentic_chunking.py`** - Metadata enriquecido vía LLM
   - Prompt mejorado para extraer:
     - `title`: Título descriptivo (5-10 palabras)
     - `summary`: Resumen conciso (2-3 frases)
     - `keywords`: Lista de 5-7 palabras clave
     - `semantic_overlap`: Conexión con chunk anterior
   - Parser actualizado para procesar keywords
   - Keywords guardados en `additional_metadata['keywords']`
   - Soporte para LLM local (llm_service) y Gemini API

5. **`rag_engine/inspect_db.py`** - Herramienta de inspección completa
   - Estadísticas por chunking_strategy
   - Lista de source_documents con chunk counts
   - Detección de duplicados por source_hash
   - Samples de metadata agentic (title, summary, keywords)
   - Análisis de diversidad de contenido (top 20 palabras)

6. **Corpus de prueba diverso** - 5 topics + 1 test
   - `transcripts_for_rag/test_agentic.txt` (prueba rápida de IA/ML)
   - `transcripts_for_rag/test_corpus/fitness.txt` (triceps, entrenamiento)
   - `transcripts_for_rag/test_corpus/ai_ml.txt` (IA, deep learning, GPT)
   - `transcripts_for_rag/test_corpus/history.txt` (Renacimiento italiano)
   - `transcripts_for_rag/test_corpus/cooking.txt` (cocina italiana)
   - `transcripts_for_rag/test_corpus/science.txt` (mecánica cuántica)

### ✅ Base de datos limpiada
- Backup creado: `rag_database.db.backup`
- BD antigua eliminada (88 documentos duplicados con datos de prueba)
- Nueva BD se creará automáticamente con schema v2 en primera ingesta

### 📝 Notas importantes
- ⚠️ **Schema v2 es automático**: Primera ingesta crea tabla nueva
- ⚠️ **Embeddings 100% locales**: `all-MiniLM-L6-v2` (sentence-transformers)
- ⚠️ **Agentic chunking NO probado aún**: Requiere llm_service activo (Sesión 4)
- ✅ **Backward compatible**: Código antiguo sigue funcionando
- 🔮 **Futuro**: Opción de cambiar modelo embeddings y re-generar todos los chunks

### 🎯 Siguiente paso
Pasar a **Sesión 4** para probar agentic chunking con LLM local end-to-end.

---

## 📋 SESIÓN 4: Testing LLM Local + Agentic Chunking (PRÓXIMA)

**Objetivo:** Validar agentic chunking completo con LLM local y comparar con semantic chunking

### Features

1. **Verificar llm_service funcional**
   - Puerto 8000 accesible
   - Modelo GGUF cargado correctamente
   - Test de endpoint `/v1/chat/completions`
   - Revisar `llm_service/config.py` y `main.py`

2. **Testing agentic chunking con archivo pequeño**
   - Ingestar `test_agentic.txt` con `--strategy agentic`
   - Verificar que usa LLM local (no Gemini fallback)
   - Inspeccionar metadata extraído: title, summary, keywords
   - Comando: `python -m rag_engine.inspect_db`

3. **Comparación semantic vs agentic**
   - Ingestar mismo archivo con `--strategy semantico`
   - Comparar metadata: semantic (básico) vs agentic (rico)
   - Evaluar calidad de títulos/resúmenes/keywords del LLM
   - Decisión: ¿Vale la pena el costo computacional de agentic?

4. **Ingesta corpus completo** (si agentic funciona bien)
   - 5 documentos × 2 strategies = 10 entradas en BD
   - Script batch para ingesta automatizada
   - Validación de diversidad con `inspect_db.py`
   - Verificar NO hay duplicados por source_hash

5. **Testing retrieval multi-topic**
   - Queries diversas cubriendo los 5 topics
   - Confirmar NO hay hardcoding de resultados (problema original)
   - Verificar que devuelve chunks de diferentes sources
   - Probar los 3 modos: vector, keyword, hybrid

### Archivos a revisar/modificar
- `llm_service/main.py` - Verificar configuración del servicio
- `llm_service/config.py` - Path al modelo GGUF
- `rag_engine/agentic_chunking.py` - Ajustar prompt si la calidad es baja
- Crear script batch de ingesta (opcional)

### ⚠️ Decisiones importantes
- **Embeddings**: SIEMPRE local (`all-MiniLM-L6-v2`)
- **LLM local**: SOLO para agentic chunking metadata
- **Gemini API**: Fallback opcional, no requerido
- **Estrategia default**: Semantic (rápido, sin LLM)
- **Estrategia avanzada**: Agentic (lento, metadata rico)

---

## 📋 SESIÓN 5: Reranking con Cross-Encoder (POSPUESTO)

### Features
- Implementar reranking con `sentence-transformers` cross-encoder
- Modelo: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Reordenar top-k resultados por relevancia semántica profunda
- CLI: `--rerank` flag

### Archivos nuevos
- `rag_engine/reranker.py`

---

## 📋 SESIÓN 4: Integración Streamlit

### Features
- Pestaña "RAG Search" en `gui_streamlit.py`
- Input de pregunta + resultados visuales
- Mostrar chunks + scores + metadata
- Configuración: top-k, modo (vector/híbrido), reranking

---

## 📋 SESIÓN 5: Métricas de Evaluación ⚠️ PARCIALMENTE COMPLETADA

### ✅ Ya implementado (Sesión 2)
- **Recall@5** ✅ - Proporción de documentos relevantes en top-5
- **MRR (Mean Reciprocal Rank)** ✅ - Promedio de reciprocal ranks
- Sistema de evaluación automático con test queries ✅
- Archivo: `rag_engine/evaluate.py`

### ❌ Faltante (por implementar)
- **NDCG** (Normalized Discounted Cumulative Gain)
- Dataset de evaluación manual más extenso (actualmente 12 queries)
- CLI: comando `benchmark` dedicado (actualmente es `evaluate`)
- Reportes comparativos en diferentes formatos (CSV, HTML)
- Métricas de diversidad de resultados
- A/B testing framework

---

## 📋 SESIÓN 6: Migración de Transcripciones Existentes

### Features
- Script para procesar `subtitles.db` → `rag_database.db`
- Procesamiento por lotes con progress bar
- Opción de agentic chunking real con LLM
- Preservar metadata (título, canal, fecha)

---

## 🔧 Estructura de Archivos

### Sesión 1 (MVP)
```
rag_engine/
├── rag_cli.py          ← NUEVO (CLI principal)
├── retriever.py        ← NUEVO (SimpleRetriever)
├── database.py         ✅ (ya existe search_similar)
├── embedder.py         ✅ (LocalEmbedder ya configurado)
├── chunker.py          ✅ (4 estrategias disponibles)
├── ingestor.py         ✅ (pipeline completo)
└── config.py           ✅ (configuración centralizada)
```

### Sesión 2 (Hybrid Search)
```
rag_engine/
├── hybrid_retriever.py    ← NUEVO (HybridRetriever con BM25 + RRF)
├── test_queries.json      ← NUEVO (12 queries de evaluación)
├── evaluate.py            ← NUEVO (métricas Recall@5 y MRR)
├── evaluation_results.json ← GENERADO (resultados cuantitativos)
└── rag_cli.py             ✅ ACTUALIZADO (flag --mode)
```

---

## ⚡ Ventajas del Enfoque

1. **Testing sin API**: Embeddings 100% locales, sin costos
2. **Iteración rápida**: CLI permite experimentar sin GUI
3. **Mock data reutilizable**: Chunks pre-generados en BD
4. **Modular**: Cada sesión añade features independientes
5. **Git worktrees friendly**: Features aisladas por rama

---

## 📊 Estado Actual del Sistema RAG

### ✅ Implementado
- Chunking (4 estrategias: caracteres, palabras, semántico, agentic)
- Embeddings (100% local con `all-MiniLM-L6-v2` via sentence-transformers)
- Base de datos vectorial (SQLite + sqlite-vec)
- **✅ Schema v2 con metadata tracking** (chunking_strategy, source_document, source_hash, etc.)
- **✅ Agentic chunking con metadata enriquecido** (title, summary, keywords vía LLM)
- Búsqueda por similitud (`search_similar()`)
- Pipeline de ingesta completo con metadata extraction
- **✅ Interfaz de consulta/retriever de alto nivel** (SimpleRetriever + HybridRetriever)
- **✅ Búsqueda híbrida** (vector + keyword/BM25 con RRF)
- **✅ Métricas de evaluación** (Recall@5, MRR)
- **✅ CLI completo** con 3 modos de búsqueda + tracking de metadata
- **✅ Herramienta de inspección** (`inspect_db.py` para debugging)
- **✅ Corpus de prueba diverso** (5 topics: fitness, AI, history, cooking, science)

### ❌ Faltante (por implementar)
- Testing completo de agentic chunking con LLM local (Sesión 4)
- Evaluación cuantitativa semantic vs agentic chunking
- Reranking después del top-k (cross-encoder) - Sesión 5
- Integración con Streamlit (pestaña RAG Search) - Sesión 6
- Métricas adicionales (NDCG)
- Migración masiva de subtitles.db → rag_database.db
- Sistema de re-embedding con modelos alternativos (opción futura)

---

## 📖 REPASO: Estado del Sistema RAG (Octubre 2025)

### 🎯 Progreso General: 50% completado (3/6 sesiones core)

#### ✅ SESIONES COMPLETADAS

**Sesión 1 - MVP CLI RAG Query** ✅ (30 Sept 2025)
- CLI funcional con 3 comandos (`stats`, `query`, `ingest`)
- Búsqueda semántica con embeddings locales (`all-MiniLM-L6-v2`)
- 88 documentos en BD vectorial
- Commits: `80b7440`, `0d6131e`, `21c796b`

**Sesión 2 - RAG Híbrido + BM25** ✅ (01 Oct 2025)
- 3 modos de búsqueda (vector, keyword, hybrid)
- Reciprocal Rank Fusion (RRF) con k=60
- Sistema de evaluación con Recall@5 y MRR
- **Keyword search superior** para corpus con terminología técnica
- Commit: `123e232`

**Sesión 3 - Schema v2 Multi-Chunking** ✅ (01 Oct 2025)
- Schema v2 con 14 columnas de metadata
- Agentic chunking con metadata enriquecido (title, summary, keywords)
- Herramienta `inspect_db.py` para debugging
- Corpus de prueba diverso (5 topics)
- BD antigua limpiada (backup creado)

#### 🚧 PRÓXIMAS SESIONES

**Sesión 4 - Testing LLM Local + Agentic Chunking** (próxima inmediata)
- Verificar llm_service funcional
- Testing agentic chunking end-to-end
- Comparación semantic vs agentic
- Ingesta corpus completo + validación retrieval

**Sesión 5 - Reranking** (pospuesto)
- Cross-encoder para reranking profundo (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Mejora de precisión en top-k
- Flag `--rerank` en CLI

**Sesión 6 - Integración Streamlit**
- Pestaña "RAG Search" en `gui_streamlit.py`
- Visualización de resultados con metadata agentic
- Selector de chunking strategy
- Configuración interactiva (top-k, modo, reranking)

**Sesión 7 - Migración Masiva** (futuro)
- Script para procesar `subtitles.db` → `rag_database.db`
- Migración de datos históricos con metadata

---

### 📦 Inventario de Componentes RAG

#### Core RAG Engine

| Componente | Estado | Archivo | Descripción |
|------------|--------|---------|-------------|
| **Chunking** | ✅ Completo | `chunker.py` | 4 estrategias: caracteres, palabras, semántico, agentic |
| **Agentic Chunking** | ⚠️ Implementado | `agentic_chunking.py` | Metadata LLM (title, summary, keywords) - NO probado |
| **Embeddings** | ✅ Completo | `embedder.py` | 100% Local (`all-MiniLM-L6-v2`) |
| **Vector DB v2** | ✅ Completo | `database.py` | Schema v2 con 14 columnas + metadata tracking |
| **Ingesta v2** | ✅ Completo | `ingestor.py` | Pipeline con metadata extraction + source tracking |
| **Retrieval Vector** | ✅ Completo | `retriever.py` | SimpleRetriever con búsqueda semántica |
| **Retrieval Híbrido** | ✅ Completo | `hybrid_retriever.py` | BM25 + Vector + RRF fusion |
| **Evaluación** | ✅ Completo | `evaluate.py` | Recall@5, MRR con test queries |
| **Inspección DB** | ✅ Completo | `inspect_db.py` | Debugging, stats por strategy, metadata samples |
| **Reranking** | ❌ Pendiente | - | Cross-encoder para reordenamiento |

#### Interfaces de Usuario

| Interfaz | Estado | Archivo | Descripción |
|----------|--------|---------|-------------|
| **CLI RAG v2** | ✅ Completo | `rag_cli.py` | 3 comandos + 3 modos + metadata display |
| **GUI Streamlit Principal** | ✅ Completo | `gui_streamlit.py` | Library de videos con transcripts |
| **GUI Streamlit RAG** | ❌ Pendiente | - | Pestaña dedicada a búsqueda RAG |

#### Datos de Prueba

| Dataset | Estado | Ubicación | Descripción |
|---------|--------|-----------|-------------|
| **Test Agentic** | ✅ Creado | `test_agentic.txt` | Archivo pequeño para prueba rápida (IA/ML) |
| **Corpus Fitness** | ✅ Creado | `test_corpus/fitness.txt` | Entrenamiento triceps, hipertrofia |
| **Corpus AI/ML** | ✅ Creado | `test_corpus/ai_ml.txt` | Deep learning, GPT, transformers |
| **Corpus History** | ✅ Creado | `test_corpus/history.txt` | Renacimiento italiano, Leonardo, Médici |
| **Corpus Cooking** | ✅ Creado | `test_corpus/cooking.txt` | Cocina italiana, pasta, pizza |
| **Corpus Science** | ✅ Creado | `test_corpus/science.txt` | Mecánica cuántica, entrelazamiento |
| **Test Queries** | ⚠️ Limitado | `test_queries.json` | 12 queries (necesita expansión a 30+) |

---

### 🔢 Estadísticas del Sistema

**Base de Datos RAG (`rag_database.db`):**
- **Estado**: Limpiada (backup en `rag_database.db.backup`)
- **Documentos actuales**: 0 (BD nueva con schema v2)
- **Documentos previos**: 88 chunks (datos de prueba duplicados - eliminados)
- **Schema**: v2 con 14 columnas + 4 índices
- **Modelo de embeddings**: `all-MiniLM-L6-v2` (384 dimensiones, 100% local)
- **Vector DB**: SQLite 3.49.1 + sqlite-vec v0.1.6

**Corpus de Prueba Disponible:**
- **Total archivos**: 6 (1 test + 5 corpus completo)
- **Topics cubiertos**: 5 (Fitness, AI/ML, History, Cooking, Science)
- **Tamaño promedio**: ~1500 palabras por documento
- **Listo para ingesta**: ✅ Sí (Sesión 4)

**Rendimiento de Retrieval (evaluado sobre 12 test queries):**

| Modo | Recall@5 | MRR | Observación |
|------|----------|-----|-------------|
| **Keyword (BM25)** | **96.67%** | **100%** | 🏆 Mejor para terminología exacta |
| Hybrid (RRF) | 93.33% | 100% | 🥈 Balance entre ambos |
| Vector (Semantic) | 83.33% | 95.83% | 🥉 Bueno para búsqueda conceptual |

**Conclusión**: BM25 keyword search es superior para corpus con terminología técnica específica (nombres de ejercicios, conceptos técnicos). Hybrid mantiene MRR perfecto.

---

### 🎬 Comandos Rápidos de Referencia

```bash
# ========================================
# ACTIVAR ENTORNO (SIEMPRE PRIMERO)
# ========================================
venv-yt-ia\Scripts\activate

# ========================================
# ESTADÍSTICAS DE LA BASE DE DATOS
# ========================================
python -m rag_engine.rag_cli stats

# ========================================
# BÚSQUEDA RAG (3 MODOS)
# ========================================
# Modo 1: Vector (semántico)
python -m rag_engine.rag_cli query "ejercicios para triceps" --mode vector

# Modo 2: Keyword (BM25 - mejor para términos exactos)
python -m rag_engine.rag_cli query "ejercicios para triceps" --mode keyword

# Modo 3: Hybrid (RRF - balance entre ambos)
python -m rag_engine.rag_cli query "ejercicios para triceps" --mode hybrid

# Con top-k personalizado
python -m rag_engine.rag_cli query "deep learning" --mode hybrid --top-k 10

# ========================================
# INGESTA DE DOCUMENTOS
# ========================================
# Mock mode (rápido, sin LLM)
python -m rag_engine.rag_cli ingest archivo.txt --mock

# Con estrategia específica
python -m rag_engine.rag_cli ingest archivo.txt --strategy semantico
python -m rag_engine.rag_cli ingest archivo.txt --strategy agentic

# ========================================
# EVALUACIÓN COMPLETA
# ========================================
python -m rag_engine.evaluate

# ========================================
# GUI PRINCIPAL (CON LIBRARY DE VIDEOS)
# ========================================
streamlit run gui_streamlit.py
```

---

### 🚀 Próximos Pasos Recomendados

#### 🔴 Inmediato (Sesión 4 - Testing LLM)
1. **Verificar llm_service funcional**
   - Iniciar servicio en puerto 8000
   - Test endpoint `/v1/chat/completions`
   - Confirmar modelo GGUF cargado

2. **Testing agentic chunking end-to-end**
   - Ingestar `test_agentic.txt` con `--strategy agentic`
   - Verificar metadata extraído (title, summary, keywords)
   - Usar `inspect_db.py` para validación

3. **Comparación semantic vs agentic**
   - Ingestar mismo archivo con ambas estrategias
   - Evaluar calidad de metadata del LLM
   - Decisión: ¿Vale la pena el costo computacional?

4. **Ingesta corpus completo + validación retrieval**
   - 5 docs × 2 strategies = 10 entradas
   - Queries diversas en todos los topics
   - Confirmar NO hay hardcoding de resultados

#### 🟡 Corto Plazo (Sesión 5-6)
5. **Reranking con cross-encoder** (Sesión 5)
   - Modelo: `cross-encoder/ms-marco-MiniLM-L-6-v2`
   - Flag `--rerank` en CLI

6. **Integración Streamlit** (Sesión 6)
   - Pestaña RAG Search en GUI
   - Selector de chunking strategy
   - Visualización de metadata agentic

7. **Expandir test queries**
   - De 12 a 30+ queries
   - Cubrir los 5 topics del corpus
   - Queries irrelevantes (control negativo)

#### 🟢 Medio Plazo
8. **Métricas avanzadas**: Implementar NDCG
9. **Migración masiva**: Script para `subtitles.db` → `rag_database.db`
10. **Optimización**: Cache de embeddings para queries frecuentes

#### 🔵 Largo Plazo
11. **Sistema de re-embedding**: Cambiar modelo y regenerar chunks
12. **Unit tests**: Suite de pruebas automatizadas
13. **Monitoreo**: Logging y métricas de uso
14. **Escalabilidad**: Evaluación con corpus >10k documentos

---

### 📚 Referencias Técnicas

#### Algoritmos Implementados
- **BM25**: Okapi BM25 ranking function (lexical matching)
- **RRF**: Reciprocal Rank Fusion (Cormack et al. 2009) - k=60
- **Embeddings**: Sentence-BERT (all-MiniLM-L6-v2, 384 dims)

#### Métricas de Evaluación
- **Recall@K**: Proporción de documentos relevantes en top-k
- **MRR**: Mean Reciprocal Rank (promedio de 1/rank del primer relevante)
- **NDCG**: Normalized Discounted Cumulative Gain (pendiente)

#### Tecnologías
- **Vector DB**: `sqlite-vec` (SQLite extension para vectores)
- **Embeddings**: `sentence-transformers` (Hugging Face)
- **BM25**: `rank-bm25` (implementación Python)
- **Backend**: Python 3.13.5
- **GUI**: Streamlit

#### Papers de Referencia
1. BM25: Robertson & Zaragoza (2009) - "The Probabilistic Relevance Framework: BM25 and Beyond"
2. RRF: Cormack, Clarke & Büttcher (2009) - "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning"
3. Sentence-BERT: Reimers & Gurevych (2019) - "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"

---

### 💡 Lecciones Aprendidas

#### ✅ Decisiones Acertadas
1. **Embeddings locales**: Sin costos de API, reproducible
2. **SQLite + sqlite-vec**: Simple, portable, sin servidor externo
3. **CLI primero**: Permite iteración rápida sin GUI
4. **Evaluación automática**: Ground truth con keyword matching
5. **Múltiples modos**: Flexibilidad para diferentes tipos de queries

#### ⚠️ Consideraciones y Mejoras (Actualizadas Sesión 3)
1. **BM25 en memoria**: Limita escalabilidad a <10k docs
2. **Falta de reranking**: Top-k inicial podría mejorarse (Sesión 5)
3. **Test queries limitadas**: 12 queries es insuficiente para conclusiones robustas
4. **Sin cache**: Queries repetidas recalculan embeddings
5. ~~**Metadata limitada**: Sin tracking de fuente, fecha, autor~~ → ✅ **RESUELTO en Sesión 3** (schema v2)
6. **Agentic chunking no probado**: Requiere testing con LLM local (Sesión 4)
7. **BD anterior con duplicados**: ✅ **RESUELTO** (limpiada, backup creado)

---

### 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/Sorl4c/codex-transcript-youtube
- **sqlite-vec docs**: https://github.com/asg017/sqlite-vec
- **sentence-transformers**: https://www.sbert.net/
- **rank-bm25**: https://github.com/dorianbrown/rank_bm25

---

## 📌 RESUMEN EJECUTIVO: Sesión 3 (01 Oct 2025)

### 🎯 Objetivo Cumplido
Implementar arquitectura multi-chunking con metadata tracking completo, permitiendo comparar estrategias semantic vs agentic en el mismo sistema RAG.

### ✅ Logros Principales

1. **Schema v2 Implementado**
   - 14 columnas de metadata (vs 3 anteriores)
   - Tracking completo: source_document, source_hash, chunking_strategy
   - 4 índices para búsquedas eficientes
   - Backward compatible con código antiguo

2. **Agentic Chunking Mejorado**
   - Prompt actualizado para extraer: title, summary, keywords
   - Keywords guardados en metadata_json
   - Soporte LLM local + Gemini API fallback

3. **Herramienta de Inspección**
   - `inspect_db.py` para debugging completo
   - Stats por strategy, detección duplicados, análisis diversidad
   - Samples de metadata agentic

4. **Corpus de Prueba Diverso**
   - 5 topics diferentes (Fitness, AI/ML, History, Cooking, Science)
   - 6 archivos listos para ingesta
   - Elimina el problema de "solo resultados de triceps"

5. **BD Limpiada**
   - Backup creado de BD antigua
   - 88 documentos duplicados eliminados
   - Lista para empezar con datos limpios

### 🔄 Cambios en Pipeline de Ingesta

**Antes (Sesión 1-2):**
```python
ingestor.ingest_text(text)
→ DB: (content, embedding)  # Solo 2 campos
```

**Ahora (Sesión 3):**
```python
ingestor = RAGIngestor(..., source_document=filepath)
ingestor.ingest_text(text)
→ DB: (content, embedding, source_document, source_hash,
      chunking_strategy, chunk_index, char_start, char_end,
      semantic_title, semantic_summary, keywords, ...)  # 14 campos
```

### 📊 Comparación de Schemas

| Campo | Schema v1 | Schema v2 |
|-------|-----------|-----------|
| `id` | ✅ | ✅ |
| `content` | ✅ | ✅ |
| `embedding` | ✅ | ✅ |
| `source_document` | ❌ | ✅ NUEVO |
| `source_hash` | ❌ | ✅ NUEVO |
| `chunking_strategy` | ❌ | ✅ NUEVO |
| `chunk_index` | ❌ | ✅ NUEVO |
| `char_start/end` | ❌ | ✅ NUEVO |
| `semantic_title` | ❌ | ✅ NUEVO |
| `semantic_summary` | ❌ | ✅ NUEVO |
| `semantic_overlap` | ❌ | ✅ NUEVO |
| `metadata_json` | ❌ | ✅ NUEVO |
| `created_at` | ❌ | ✅ NUEVO |

### 🚀 Próximo Paso Inmediato

**Sesión 4**: Probar agentic chunking con LLM local end-to-end

**Comandos clave:**
```bash
# 1. Test rápido con semantic
python -m rag_engine.rag_cli ingest test_agentic.txt --strategy semantico

# 2. Test con agentic (requiere llm_service activo)
python -m rag_engine.rag_cli ingest test_agentic.txt --strategy agentic

# 3. Inspeccionar resultados
python -m rag_engine.inspect_db

# 4. Comparar metadata
# → Semantic: title/summary/keywords = NULL
# → Agentic: title/summary/keywords = extraídos por LLM
```

### 💡 Decisión Pendiente (Sesión 4)

¿Agentic chunking vale la pena el costo computacional?

**Evaluaremos:**
- Calidad de títulos generados por LLM
- Utilidad de resúmenes automáticos
- Relevancia de keywords extraídos
- Tiempo de procesamiento vs semantic

**Resultado esperado:**
- ✅ Si la calidad es alta → Usar agentic para corpus importantes
- ⚠️ Si la calidad es baja/media → Semantic como default (más rápido)
