# RAG Development Plan & Study Guide

## Estado Actual del Sistema RAG (Octubre 2025)

### ✅ Componentes Funcionales:
- **RAG CLI**: `python -m rag_engine.rag_cli stats` y `query` funcionan
- **Base de datos**: SQLite con sqlite-vec (18 documentos, 0.23 MB)
- **Embeddings**: Locales con `all-MiniLM-L6-v2`
- **Modelo Gemini**: `gemini-2.0-flash-exp` actualizado y funcionando
- **Agentic chunking**: Función `chunk_text_with_gemini` operativa
- **Tests**: Unitarios pasando (3/3)

### ❌ Problemas Conocidos:
- Inconsistencia en nombres de funciones: `perform_agentic_chunking` vs `chunk_text_with_gemini`
- Warnings de deprecación (pkg_resources, Streamlit)
- Errores intermitentes de cuota de Gemini API

---

## Guía de Estudio y Desarrollo RAG

### Paso 1: Entender la Arquitectura Actual

```bash
# Explorar la estructura del sistema RAG
find rag_engine/ -name "*.py" | head -10

# Leer la documentación existente
cat docs/RAG_ROADMAP.md

# Probar el sistema básico
python -m rag_engine.rag_cli stats
python -m rag_engine.rag_cli query "test" --top-k 3
```

### Paso 2: Identificar Componentes Faltantes

1. **UI para RAG**: No hay interfaz gráfica dedicada
2. **Sistema de ingesta**: Flujo completo para procesar documentos
3. **Evaluación**: Métricas de calidad del sistema RAG
4. **Integración con Streamlit**: Actualmente solo maneja YouTube

### Paso 3: Plan de Desarrollo

#### Fase 1: UI y Pruebas Básicas (1-2 semanas)
- [ ] Crear UI simple para RAG (¿Streamlit dedicada?)
- [ ] Implementar ingesta de documentos desde UI
- [ ] Sistema de búsqueda y visualización de resultados
- [ ] Pruebas manuales de calidad de búsqueda

#### Fase 2: Mejora de Componentes (2-3 semanas)
- [ ] Corregir inconsistencia de nombres de funciones
- [ ] Implementar híbrido search (vectorial + BM25)
- [ ] Mejorar sistema de chunking agentic
- [ ] Sistema de evaluación automática

#### Fase 3: Integración y Optimización (1-2 semanas)
- [ ] Integrar RAG con Streamlit principal
- [ ] Optimizar uso de embeddings y almacenamiento
- [ ] Implementar cache para reducir llamadas API
- [ ] Documentación completa y tutoriales

---

## Prompt para Análisis en Nueva Terminal

Copia este prompt y ejecútalo en una terminal limpia con contexto completo:

```
Actúa como un experto en sistemas RAG (Retrieval-Augmented Generation) y arquitectura de software. Necesito que analices completamente el sistema RAG de este proyecto y me proporciones un plan de desarrollo detallado.

CONTEXTO DEL PROYECTO:
- Proyecto principal: YouTube subtitle downloader con IA
- Sistema RAG en desarrollo en directorio rag_engine/
- Usa SQLite con sqlite-vec para base de datos vectorial
- Embeddings locales con sentence-transformers
- Gemini API para chunking agentic
- Modelo actual: gemini-2.0-flash-exp

TAREAS A REALIZAR:

1. ANÁLISIS DE ARQUITECTURA ACTUAL:
   - Explorar todos los archivos en rag_engine/
   - Identificar componentes faltantes
   - Evaluar calidad del código existente
   - Identificar problemas de diseño o arquitectura

2. DIAGNÓSTICO DE PROBLEMAS:
   - Buscar referencias a 'perform_agentic_chunking' en todo el código
   - Identificar inconsistencias en la API
   - Evaluar problemas de dependencias y deprecación
   - Analizar rendimiento y escalabilidad

3. PLAN DE DESARROLLO DETALLADO:
   - Roadmap con fases claras
   - Tecnologías recomendadas
   - Patrones de diseño sugeridos
   - Estrategia de testing
   - Plan de integración con sistema principal

4. GUÍA DE IMPLEMENTACIÓN:
   - Pasos concretos para arrancar el sistema
   - Cómo probar cada componente
   - Cómo desarrollar nuevas funcionalidades
   - Mejores prácticas y patrones

5. RECOMENDACIONES ESPECÍFICAS:
   - ¿Qué UI usar? (Streamlit, FastAPI, otra)
   - ¿Cómo integrar con sistema actual de YouTube?
   - ¿Cómo mejorar el sistema de chunking?
   - ¿Cómo implementar evaluación de calidad?

ENTREGABLES ESPERADOS:
- Análisis completo del estado actual
- Plan de desarrollo priorizado
- Código de ejemplo para componentes clave
- Guías paso a paso para implementación
- Recomendaciones técnicas específicas

Por favor, sé exhaustivo, práctico y proporciona código concreto donde sea relevante. Enfócate en crear un sistema RAG robusto y escalable que se integre bien con el proyecto existente.
```

---

## Próximos Pasos Inmediatos

### Para ti (ahora mismo):
1. Copiar el prompt anterior y ejecutarlo en nueva terminal
2. Obtener análisis completo y plan de desarrollo
3. Tener roadmap claro para implementación

### Para el sistema (futuro):
1. Corregir problemas de nombres de funciones
2. Crear UI dedicada para RAG
3. Implementar flujo completo de ingesta
4. Integrar con sistema principal de Streamlit

---

## Notas Técnicas

### Comandos Útiles:
```bash
# Activar entorno
venv-yt-ia\Scripts\activate

# Probar RAG CLI
python -m rag_engine.rag_cli stats
python -m rag_engine.rag_cli query "tu pregunta" --top-k 5

# Probar agentic chunking
python -c "from rag_engine.agentic_chunking import chunk_text_with_gemini; print('OK')"

# Verificar modelo Gemini
python -c "from ia.gemini_api import GEMINI_MODEL_NAME; print(GEMINI_MODEL_NAME)"
```

### Archivos Clave:
- `rag_engine/rag_cli.py` - CLI principal
- `rag_engine/agentic_chunking.py` - Chunking con IA
- `rag_engine/database.py` - Base de datos vectorial
- `ia/gemini_api.py` - Configuración de Gemini
- `docs/RAG_ROADMAP.md` - Documentación existente

### Estado de Integración:
- RAG funciona independientemente ✅
- No integrado con Streamlit principal ❌
- No hay UI dedicada ❌
- Sistema de ingesta incompleto ❌