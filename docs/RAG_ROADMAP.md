# Plan MVP RAG + Roadmap Multi-Sesión

## 🎯 SESIÓN 1: MVP CLI RAG Query (En progreso)

### Commit de Seguridad Primero
- ✅ Crear commit con estado actual antes de cualquier cambio

### Objetivo
Crear CLI mínimo funcional para probar recuperación RAG sin llamadas API continuas

### Tareas
1. **Mock Data Setup**
   - Ya existe: `transcripts_for_rag/sample_transcript.txt` ✅
   - Crear chunks pre-procesados con agentic chunking en modo mock (sin LLM)
   - Guardar resultados en `rag_database.db` para reutilización

2. **Crear `rag_engine/rag_cli.py`**
   - Comando: `ingest <file>` - Ingestar transcripción con chunking local
   - Comando: `query <pregunta>` - Buscar chunks relevantes por similitud
   - Comando: `stats` - Ver estadísticas de la BD vectorial
   - Flag: `--mock` - Usar chunking simple sin LLM para testing rápido

3. **Usar LocalEmbedder (sentence-transformers)**
   - Ya configurado en `config.py`: `all-MiniLM-L6-v2` ✅
   - No requiere microservicio activo
   - Embeddings locales rápidos

4. **Implementar `rag_engine/retriever.py` (MVP básico)**
   - Clase `SimpleRetriever`:
     - `query(question: str, top_k: int) -> List[Tuple[str, float]]`
     - Usa `database.search_similar()` ya existente
   - Sin híbrido, sin reranking (próxima sesión)

### Entregables CLI
```bash
# Ingestar transcripción mock
python -m rag_engine.rag_cli ingest transcripts_for_rag/sample_transcript.txt --mock

# Hacer consulta
python -m rag_engine.rag_cli query "¿Qué es machine learning?" --top-k 3

# Ver stats
python -m rag_engine.rag_cli stats
```

---

## 📋 SESIÓN 2: RAG Híbrido + BM25

### Features
- Implementar búsqueda por palabras clave (BM25) con `rank-bm25`
- Combinar resultados vector + keyword
- Estrategia de fusión simple (Reciprocal Rank Fusion)
- CLI: `--mode hybrid|vector|keyword`

### Archivos nuevos
- `rag_engine/hybrid_retriever.py`
- Tests: `rag_engine/test_hybrid_search.py`

### Dependencias
```bash
pip install rank-bm25
```

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

### ❌ Faltante (por implementar)
- Interfaz de consulta/retriever de alto nivel
- Búsqueda híbrida (vector + keyword/BM25)
- Reranking después del top-k
- Integración con Streamlit
- Métricas de evaluación (recall, MRR, NDCG)
