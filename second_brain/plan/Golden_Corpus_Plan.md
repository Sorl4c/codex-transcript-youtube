# Golden Corpus para Evaluación RAG - Plan de Implementación

**Fecha:** 2025-10-18
**Archivo:** `second_brain/plan/Golden_Corpus_Plan.md`
**Tipo:** [Investigación + Plan] Dificultad (⭐⭐⭐)
**Estado:** 📋 Planificado para Fase 2.5+

## Objetivo

Definir e implementar un golden corpus estándar para evaluación de sistemas RAG, basado en mejores prácticas de la industria y referencias académicas.

## Fuentes Principales Investigadas

### 1. Hugging Face Cookbook - RAG Evaluation ⭐⭐⭐⭐⭐
- **URL**: https://huggingface.co/learn/cookbook/rag_evaluation
- **Enfoque**: Síntesis con LLMs + filtros de calidad
- **Key Insight**: Chunk size tuning es "fácil y muy impactante"

### 2. RAGAS Documentation ⭐⭐⭐⭐
- **URL**: https://docs.ragas.io
- **Enfoque**: Métricas comprehensivas para RAG
- **Key Insight**: Framework de evaluación con métricas específicas

### 3. A Comprehensive Review on RAG (arXiv:2402.19473) ⭐⭐⭐⭐
- **URL**: https://arxiv.org/abs/2402.19473
- **Enfoque**: Framework de evaluación actualizado
- **Key Insight**: "No single good recipe" cuando se tunea RAG

---

## Mejores Prácticas Identificadas

### 🏗️ **Construcción del Dataset**

#### **Síntesis con LLMs**
- Usar LLMs para generar QA pairs desde la knowledge base
- Implementar filtros de calidad con agentes LLM

#### **Filtros de Calidad (Escala 1-5)**
- **✅ Groundedness**: "¿La pregunta puede responderse desde el contexto?"
- **✅ Relevance**: "¿Útil para practicantes de ML construyendo apps NLP?"
- **✅ Standalone**: "Claridad de la pregunta independiente del contexto"

### 📏 **Criterios de Representatividad**

#### **Chunk Size Recomendado**
- **200+ tokens** (según Hugging Face)
- Chunk size tuning es "fácil y muy impactante"

#### **Query Selection**
- Queries representativas del use case real
- Diversidad de tipos de preguntas
- Diferentes niveles de dificultad

### 🎯 **Evaluación de Retrieval**

#### **Métricas Clave**
- **Answer Correctness** como métrica end-to-end
- **GPT-4 como juez** con rubric detallada (1-5 scale)
- **Rationale antes del scoring** para mejor consistencia

#### **Tests de Configuración**
- Chunk sizes (200+ tokens recomendado)
- Embedding models
- Reranking on/off

### 🎨 **Principios de Diseño**

#### **Características del Golden Corpus**
- **Reducido pero representativo**: No necesita ser masivo
- **Variabilidad temática**: Cubrir dominios diferentes
- **Dificultad graduada**: Queries fáciles y difíciles
- **Ground truth verificable**: Respuestas conocidas

---

## Estado Actual vs Ideal

### 📊 **Dataset Actual (18 chunks) - Evaluación**

#### ✅ **Fortalezas**
- Temas técnicos relevantes (Docker, PostgreSQL, embeddings)
- Tamaño manejable para experimentación
- Queries representativas ya probadas
- Performance < 10ms por búsqueda
- Scores de similitud 0.60-0.71 funcionales

#### 🔧 **Mejoras Aplicables**
1. **Añadir QA pairs** con Ground truth known
2. **Implementar filtros** de groundedness (1-5)
3. **Diversificar queries** para diferentes dominios
4. **Documentar metadata** de cada chunk
5. **Expandir a 30-50 chunks** con más diversidad temática

---

## Plan de Implementación

### 🚀 **Fase 2.5: Golden Corpus Enhancement**

#### **Paso 1: Análisis del Dataset Actual**
```python
# Evaluación de chunks existentes
- Analizar diversidad temática actual
- Identificar gaps de cobertura
- Evaluar calidad de contenido
- Documentar metadata existente
```

#### **Paso 2: Expansión Controlada con Corpus Sintético**
```python
# Crear corpus sintético multitemático: 15 chunks por categoría = 45 total
- Distribución: 15 chunks tecnología + 15 chunks aprendizaje/productividad + 15 chunks deporte/bienestar
- Formato: document_id + chunk_index (mantiener compatibilidad)
- Chunk size: 200+ tokens optimizado para RAG
- Metadata enriquecida por chunk:
  * categoria (tecnologia/aprendizaje/deporte)
  * fuente (ficticia pero realista)
  * titulo (descriptivo del contenido)
  * resumen (breve descripción)
- Preservar estructura actual para compatibilidad
- Objetivo: Medir relevancia cruzada entre dominios
```

#### **Paso 3: Generación QA Pairs por Chunk**
```python
# Síntesis con LLMs - 3 QA pairs por chunk = 135 QA pairs totales
- Tipos de preguntas por chunk:
  * 1 pregunta factual (qué, quién, dónde, cuándo)
  * 1 pregunta procedimental (cómo, paso a paso)
  * 1 pregunta reflexiva (por qué, qué pasaría si, comparación)
- Sistema de scoring 1-5 por criterio:
  * Groundedness: ¿Se puede responder desde el chunk?
  * Relevance: ¿Es útil para usuarios reales?
  * Claridad: ¿Es independiente y comprensible?
- Validación con GPT-4 + filtros automáticos
- Crear respuestas ground truth con citas textuales
- Total: 45 chunks × 3 QA pairs = 135 pares QA completos
```

#### **Paso 4: Métricas de Evaluación**
```python
# Framework completo
- Retrieval metrics (precision, recall, F1)
- Answer correctness (GPT-4 como juez)
- Relevance scoring (1-5)
- Groundedness assessment
```

### 📈 **Fase 4: Refactorización con Golden Corpus**

#### **Integración con Nuevo Schema**
- Aplicar principios de golden corpus al schema normalizado
- Mantener compatibilidad con queries existentes
- Añadir vistas para evaluación específica
- Documentar best practices para futuros datasets

---

## Métricas de Success

### 📊 **KPIs del Golden Corpus**

#### **Calidad del Dataset**
- **Diversidad temática**: ≥ 5 dominios diferentes
- **Complejidad variada**: Queries fáciles, medias, difíciles
- **Ground truth verificable**: 100% de QA pairs validados
- **Filtros de calidad**: Promedio ≥ 4.0/5.0

#### **Performance de Retrieval**
- **Coverage**: ≥ 80% de queries con resultados relevantes
- **Precision**: Top-3 relevance ≥ 0.7
- **Speed**: < 50ms por query
- **Consistency**: Scores estables across runs

#### **Evalución End-to-End**
- **Answer correctness**: ≥ 4.0/5.0 (GPT-4 judge)
- **Groundedness**: ≥ 4.0/5.0
- **Relevance**: ≥ 4.0/5.0
- **User satisfaction**: Métricas cualitativas

---

## Dataset de Referencia Propuesto

### 🏆 **Estructura Ideal del Golden Corpus**

#### **Categorías Temáticas (30-50 chunks)**
1. **DevOps & Infrastructure** (20%)
   - Docker, Kubernetes, CI/CD
   - Cloud platforms (AWS, GCP, Azure)
   - Monitoring & observability

2. **Machine Learning & AI** (25%)
   - Modelos y algoritmos
   - Frameworks (TensorFlow, PyTorch)
   - MLOps y deployment

3. **Software Architecture** (20%)
   - Microservicios y distributed systems
   - Design patterns
   - API development

4. **Data Engineering** (15%)
   - Databases (SQL, NoSQL, vector)
   - Data pipelines
   - Streaming y real-time

5. **Security & Best Practices** (10%)
   - Cybersecurity fundamentals
   - Code security
   - Compliance

6. **Domain Specific** (10%)
   - Industry verticals
   - Specialized applications
   - Emerging technologies

#### **QA Pairs por Chunk**
- **3-5 preguntas** por chunk
- **Diferentes tipos**: Factual, conceptual, procedimental
- **Complejidad graduada**: Fácil → Difícil
- **Ground truth documentado**

---

## Herramientas y Frameworks

### 🛠️ **Tecnologías Recomendadas**

#### **Generación y Evaluación**
- **RAGAS**: Métricas comprehensivas
- **Hugging Face**: Síntesis con LLMs
- **GPT-4**: Judge para answer correctness
- **Custom filters**: Groundedness y relevance

#### **Almacenamiento y Retrieval**
- **PostgreSQL + pgvector**: Nuestra implementación actual
- **Metadata enriquecida**: JSON schema extendido
- **Versioning**: Track de cambios en dataset

#### **Testing y Validación**
- **Unit tests**: Validación de QA pairs
- **Integration tests**: End-to-end evaluation
- **Benchmarking**: Comparación de configuraciones

---

## Plan de Testing y Fixtures

### 🧪 **Roadmap de Testing para Corpus Sintético**

#### **Unit Tests**
```python
# Test de generación de corpus sintético
def test_corpus_generation():
    - Validar 45 chunks totales (15 por categoría)
    - Verificar metadata requerida (categoria, fuente, titulo, resumen)
    - Comprobar chunk size >= 200 tokens
    - Validar formatos document_id + chunk_index

# Test de QA pairs generation
def test_qa_pairs_quality():
    - Verificar 3 QA pairs por chunk
    - Validar tipos: factual, procedimental, reflexiva
    - Comprobar scoring >= 4.0/5.0 en todos los criterios
    - Test de ground truth citations
```

#### **Integration Tests**
```python
# Test de ingestión multitemática
def test_multitematic_ingestion():
    - Ingerir corpus sintético completo
    - Validar distribución por categorías
    - Verificar búsqueda cruzada entre dominios
    - Comprobar performance < 50ms

# Test de evaluación RAG
def test_rag_evaluation():
    - Ejecutar 135 QA pairs queries
    - Medir answer correctness
    - Validar groundedness y relevance
    - Comprobar cross-domain relevance
```

#### **Fixtures Generados**
```python
# Fixtures por categoría
@pytest.fixture
def tecnologia_corpus():
    return generate_synthetic_chunks("tecnologia", count=15)

@pytest.fixture
def aprendizaje_corpus():
    return generate_synthetic_chunks("aprendizaje", count=15)

@pytest.fixture
def deporte_corpus():
    return generate_synthetic_chunks("deporte", count=15)

# Fixture completo del corpus
@pytest.fixture
def corpus_multitematico():
    return {
        "tecnologia": tecnologia_corpus(),
        "aprendizaje": aprendizaje_corpus(),
        "deporte": deporte_corpus()
    }

# Fixture de QA pairs
@pytest.fixture
def qa_pairs_by_category():
    return generate_qa_pairs(corpus_multitematico())
```

### 🎯 **Objetivos de Testing**

1. **Validar generación consistente** de corpus sintético
2. **Asegurar calidad de QA pairs** con scoring automático
3. **Verificar cross-domain relevance** entre categorías
4. **Medir rendimiento** con dataset multitemático real
5. **Comprobar backward compatibility** con estructura actual

## Riesgos y Mitigación

### ⚠️ **Riesgos Identificados**

#### **Quality Control**
- **Riesgo**: QA pairs de baja calidad
- **Mitigación**: Filtros LLM + validación humana

#### **Bias y Representatividad**
- **Riesgo**: Dataset sesgado hacia dominios específicos
- **Mitigación**: Diversificación intencional y métricas de balance

#### **Scalability**
- **Riesgo**: Dataset crece demasiado
- **Mitigación**: Principios de minimalidad efectiva

#### **Maintainability**
- **Riesgo**: Dataset se vuelve obsoleto
- **Mitigación**: Versioning y actualización periódica

---

## Timeline Sugerido

### 📅 **Fechas Estimadas**

#### **Sprint 1 (Week 1-2): Analysis & Planning**
- Evaluar dataset actual
- Definir requerimientos específicos
- Diseñar estructura del golden corpus

#### **Sprint 2 (Week 3-4): Expansion**
- Generar chunks adicionales
- Implementar diversidad temática
- Añadir metadata enriquecida

#### **Sprint 3 (Week 5-6): QA Generation**
- Síntesis de QA pairs con LLMs
- Implementar filtros de calidad
- Validación iterativa

#### **Sprint 4 (Week 7-8): Integration**
- Integrar con pipeline RAG existente
- Implementar métricas de evaluación
- Documentación completa

---

## Success Metrics Dashboard

### 📊 **KPIs para Seguimiento**

#### **Dataset Quality**
- [ ] Total chunks: 30-50
- [ ] Dominios cubiertos: ≥5
- [ ] QA pairs totales: ≥100
- [ ] Quality score promedio: ≥4.0/5.0

#### **Performance Metrics**
- [ ] Retrieval precision@3: ≥0.7
- [ ] Answer correctness: ≥4.0/5.0
- [ ] Query response time: <50ms
- [ ] Coverage rate: ≥80%

#### **Evaluation Framework**
- [ ] Métricas automatizadas funcionando
- [ ] Dashboard de monitoreo activo
- [ ] Reports generados automáticamente
- [ ] Benchmark baseline establecido

---

## Próximos Pasos

### 🎯 **Acciones Inmediatas**

1. **Validación del Plan**: Review con stakeholder
2. **Priorización**: Definir qué dominios expandir primero
3. **Tool Setup**: Preparar entorno de generación QA
4. **Baseline Capture**: Documentar estado actual como referencia

### 🔄 **Proceso Iterativo**

1. **Sprint Planning**: Definir objetivos por sprint
2. **Development**: Implementación incremental
3. **Testing**: Validación continua
4. **Review**: Retroalimentación y ajustes

---

## Referencias Adicionales

### 📚 **Material de Estudio**

#### **Papers Académicos**
- RAG Survey: https://arxiv.org/abs/2402.19473
- RAG Evaluation: https://arxiv.org/abs/2312.10997

#### **Documentación Técnica**
- RAGAS: https://docs.ragas.io
- Hugging Face Cookbook: https://huggingface.co/learn/cookbook/rag_evaluation

#### **Industry Best Practices**
- Pinecone RAG Evaluation Series
- Weaviate RAG Best Practices
- IBM RAG Evaluation Guidelines

---

## Conclusiones

### 💡 **Key Takeaways**

1. **Dataset actual es buen punto de partida** pero necesita expansión
2. **Calidad sobre cantidad**: 30-50 chunks bien curados > miles sin validar
3. **Filtros LLM son esenciales** para mantener calidad
4. **Métricas estandarizadas** cruciales para comparación
5. **Iteración continua** para mantener relevancia

### 🚀 **Ready for Implementation**

El golden corpus propuesto seguirá las mejores prácticas de la industria y proporcionará una base sólida para evaluación de sistemas RAG, permitiendo comparaciones justas y mejoras medibles en nuestro pipeline.

---

*Última actualización: 2025-10-18*
*Status: Planificado para implementación en Fase 2.5*
*Corpus Sintético: 45 chunks (15×3 categorías) con 135 QA pairs*