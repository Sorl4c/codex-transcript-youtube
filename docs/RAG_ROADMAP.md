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

## 📋 SESIÓN 2: RAG Híbrido + BM25 (Próxima sesión)

### ⚠️ IMPORTANTE: Preparación de sesión
1. **Activar venv PRIMERO:**
   ```bash
   venv-yt-ia\Scripts\activate
   ```

2. **Verificar estado:**
   ```bash
   python -m rag_engine.rag_cli stats
   git log --oneline -5
   ```

3. **Crear branch (opcional):**
   ```bash
   git checkout -b feature/rag-hybrid-search
   ```

### Features a implementar
- Implementar búsqueda por palabras clave (BM25) con `rank-bm25`
- Combinar resultados vector + keyword
- Estrategia de fusión simple (Reciprocal Rank Fusion - RRF)
- CLI: `--mode hybrid|vector|keyword`

### Archivos nuevos
- `rag_engine/hybrid_retriever.py` - HybridRetriever con BM25 + vectorial
- `rag_engine/test_hybrid_search.py` - Tests unitarios

### Nuevas dependencias
```bash
pip install rank-bm25>=0.2.0
```

### Plan de implementación
1. Instalar `rank-bm25` en venv
2. Crear `HybridRetriever` que extienda `SimpleRetriever`
3. Implementar BM25 sobre textos de chunks en BD
4. Implementar Reciprocal Rank Fusion (RRF)
5. Agregar flag `--mode` a CLI
6. Probar con queries mixtas (términos específicos + semántica)
7. Actualizar `requirements.txt`
8. Commit y documentar resultados

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
