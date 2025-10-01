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

## 📋 SESIÓN 5: Métricas de Evaluación

### Features
- Recall@k, MRR, NDCG
- Crear dataset de evaluación manual
- CLI: `benchmark` comando
- Reportes comparativos de estrategias

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
