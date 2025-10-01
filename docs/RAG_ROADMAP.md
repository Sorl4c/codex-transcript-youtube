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

## 📋 SESIÓN 3: Reranking con Cross-Encoder

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
- Embeddings (local con sentence-transformers + API externa)
- Base de datos vectorial (SQLite + sqlite-vec)
- Búsqueda por similitud (`search_similar()`)
- Pipeline de ingesta completo
- **✅ Interfaz de consulta/retriever de alto nivel** (SimpleRetriever + HybridRetriever)
- **✅ Búsqueda híbrida** (vector + keyword/BM25 con RRF)
- **✅ Métricas de evaluación** (Recall@5, MRR)
- **✅ CLI completo** con 3 modos de búsqueda

### ❌ Faltante (por implementar)
- Reranking después del top-k (cross-encoder)
- Integración con Streamlit (pestaña RAG Search)
- Métricas adicionales (NDCG)
- Migración masiva de subtitles.db → rag_database.db

---

## 📖 REPASO: Estado del Sistema RAG (Octubre 2025)

### 🎯 Progreso General: 40% completado (2/6 sesiones)

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

#### 🚧 PRÓXIMAS SESIONES

**Sesión 3 - Reranking** (próxima prioritaria)
- Cross-encoder para reranking profundo (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Mejora de precisión en top-k
- Flag `--rerank` en CLI

**Sesión 4 - Integración Streamlit**
- Pestaña "RAG Search" en `gui_streamlit.py`
- Visualización de resultados con provenance
- Configuración interactiva (top-k, modo, reranking)

**Sesión 5 - Métricas Avanzadas** ⚠️ Parcialmente completada
- NDCG y métricas de diversidad
- Dataset de evaluación más extenso
- Reportes en múltiples formatos

**Sesión 6 - Migración Masiva**
- Script para procesar `subtitles.db` → `rag_database.db`
- Migración de datos históricos con metadata

---

### 📦 Inventario de Componentes RAG

#### Core RAG Engine

| Componente | Estado | Archivo | Descripción |
|------------|--------|---------|-------------|
| **Chunking** | ✅ Completo | `chunker.py` | 4 estrategias: caracteres, palabras, semántico, agentic |
| **Embeddings** | ✅ Completo | `embedder.py` | Local (`all-MiniLM-L6-v2`) + API externa |
| **Vector DB** | ✅ Completo | `database.py` | SQLite + sqlite-vec extension |
| **Ingesta** | ✅ Completo | `ingestor.py` | Pipeline completo de procesamiento |
| **Retrieval Vector** | ✅ Completo | `retriever.py` | SimpleRetriever con búsqueda semántica |
| **Retrieval Híbrido** | ✅ Completo | `hybrid_retriever.py` | BM25 + Vector + RRF fusion |
| **Evaluación** | ✅ Completo | `evaluate.py` | Recall@5, MRR con test queries |
| **Reranking** | ❌ Pendiente | - | Cross-encoder para reordenamiento |

#### Interfaces de Usuario

| Interfaz | Estado | Archivo | Descripción |
|----------|--------|---------|-------------|
| **CLI RAG** | ✅ Completo | `rag_cli.py` | 3 comandos (stats, query, ingest) + 3 modos |
| **GUI Streamlit Principal** | ✅ Completo | `gui_streamlit.py` | Library de videos con transcripts |
| **GUI Streamlit RAG** | ❌ Pendiente | - | Pestaña dedicada a búsqueda RAG |

---

### 🔢 Estadísticas del Sistema

**Base de Datos RAG (`rag_database.db`):**
- **Documentos**: 88 chunks
- **Tamaño**: ~1.03 MB
- **Estrategia de chunking**: Mixta (caracteres/semántico)
- **Modelo de embeddings**: `all-MiniLM-L6-v2` (384 dimensiones)
- **Vector DB**: SQLite 3.49.1 + sqlite-vec v0.1.6

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

#### Inmediato (Sesión 3)
1. **Implementar reranking con cross-encoder**
   - Modelo: `cross-encoder/ms-marco-MiniLM-L-6-v2`
   - Integrar en pipeline después de retrieval inicial
   - Agregar flag `--rerank` al CLI

#### Corto Plazo (Sesión 4-5)
2. **Integración Streamlit**: Crear pestaña RAG Search en GUI
3. **Métricas avanzadas**: Implementar NDCG
4. **Testing**: Agregar más test queries (objetivo: 50+)

#### Medio Plazo (Sesión 6)
5. **Migración masiva**: Procesar `subtitles.db` completo
6. **Optimización**: Cache de embeddings para queries frecuentes
7. **Documentación**: Docstrings completos + diagramas

#### Largo Plazo
8. **Unit tests**: Suite de pruebas automatizadas
9. **Monitoreo**: Logging y métricas de uso
10. **Escalabilidad**: Evaluación con corpus >10k documentos

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

#### ⚠️ Consideraciones Futuras
1. **BM25 en memoria**: Limita escalabilidad a <10k docs
2. **Falta de reranking**: Top-k inicial podría mejorarse
3. **Test queries limitadas**: 12 queries es insuficiente para conclusiones robustas
4. **Sin cache**: Queries repetidas recalculan embeddings
5. **Metadata limitada**: Sin tracking de fuente, fecha, autor

---

### 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/Sorl4c/codex-transcript-youtube
- **sqlite-vec docs**: https://github.com/asg017/sqlite-vec
- **sentence-transformers**: https://www.sbert.net/
- **rank-bm25**: https://github.com/dorianbrown/rank_bm25
