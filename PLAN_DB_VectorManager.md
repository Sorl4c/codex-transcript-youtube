# Plan Detallado: RAGDatabaseManager - Sistema de Reconstrucción RAG con Docling

## Overview
Crear una clase `RAGDatabaseManager` especializada en la reconstrucción completa de la base de datos RAG, utilizando Docling para preprocesamiento de texto de alta calidad.

## Problemas Identificados

### Calidad de Chunks Actual
- **Fragmentación pobre**: Los chunks pueden estar demasiado fragmentados o con información irrelevante
- **Estrategias ineficaces**: Las estrategias actuales (caracteres, palabras, semántico, agentic) pueden no ser óptimas
- **Falta de preprocesamiento**: No se utiliza Docling para limpiar y estructurar el texto antes del chunking

### Embeddings Obsoletos
- **Baja calidad**: Los embeddings fueron generados con chunks de baja calidad
- **Modelo desactualizado**: Posible necesidad de actualizar el modelo de embeddings
- **Contaminación**: Base de datos contaminada con chunks de mala calidad

### Gestión de Base de Datos
- **Sin rollback**: No hay forma de volver a versiones anteriores
- **Sin experimentación**: No se pueden probar configuraciones sin riesgo
- **Sin validación**: No hay métricas de calidad del proceso

## Issues Atómicas

### Issue 1: Estructura Base de la Clase
- **Crear archivo**: `rag_engine/database_manager.py`
- **Definir clase**: `RAGDatabaseManager`
- **Métodos básicos**: `__init__`, `backup_database`, `restore_database`
- **Configuración**: rutas de archivos, configuraciones por defecto

**Implementación**:
```python
class RAGDatabaseManager:
    def __init__(self, db_path: str = None, backup_dir: str = None):
        self.db_path = db_path or DB_PATH
        self.backup_dir = backup_dir or os.path.join(PROJECT_ROOT, 'rag_backups')
        os.makedirs(self.backup_dir, exist_ok=True)
```

### Issue 2: Sistema de Limpieza Completa
- **Método**: `clear_all_data()`
- **Funcionalidad**: Eliminar completamente tablas vec0 y metadata
- **Validación**: Verificar que no queden residuos
- **Logging**: Registro detallado de operaciones

**Implementación**:
```python
def clear_all_data(self) -> Dict[str, Any]:
    # 1. Backup automático
    # 2. Eliminar tablas vec0 y metadata
    # 3. Verificar limpieza completa
    # 4. Logging detallado
```

### Issue 3: Integración Docling para Preprocesamiento
- **Método**: `_preprocess_with_docling(text, source_info)`
- **Funcionalidad**:
  - Limpieza de texto (remover artefactos de VTT)
  - Estructuración lógica (párrafos, secciones)
  - Extracción de metadatos semánticos
  - Normalización de formato

**Implementación**:
```python
def _preprocess_with_docling(self, text: str, source_info: Dict) -> Dict[str, Any]:
    # 1. Procesar texto con Docling
    # 2. Extraer estructura lógica
    # 3. Limpiar artefactos
    # 4. Generar metadatos enriquecidos
```

### Issue 4: Análisis de Calidad de Texto
- **Método**: `_analyze_text_quality(text)`
- **Métricas**:
  - Densidad de información
  - Coherencia estructural
  - Presencia de artefactos
  - Longitud óptima de chunks

**Implementación**:
```python
def _analyze_text_quality(self, text: str) -> Dict[str, float]:
    # 1. Calcular densidad de información
    # 2. Evaluar coherencia estructural
    # 3. Detectar artefactos
    # 4. Determinar longitud óptima
```

### Issue 5: Sistema de Chunking Mejorado
- **Método**: `_create_enhanced_chunks(text, strategy)`
- **Mejoras**:
  - Detección automática de mejor estrategia
  - Ajuste dinámico de tamaño según contenido
  - Preservación de contexto semántico
  - Metadatos enriquecidos

**Implementación**:
```python
def _create_enhanced_chunks(self, text: str, strategy: str) -> List[Chunk]:
    # 1. Analizar texto para determinar mejor estrategia
    # 2. Ajustar tamaño según contenido
    # 3. Preservar contexto semántico
    # 4. Enriquecer metadatos
```

### Issue 6: Validación de Calidad de Chunks
- **Método**: `_validate_chunks(chunks)`
- **Validaciones**:
  - Longitud apropiada (200-1200 caracteres)
  - Coherencia semántica
  - Superposición óptima
  - Ausencia de fragmentos inútiles

**Implementación**:
```python
def _validate_chunks(self, chunks: List[Chunk]) -> Dict[str, Any]:
    # 1. Validar longitud de chunks
    # 2. Evaluar coherencia semántica
    # 3. Verificar superposición
    # 4. Filtrar chunks inútiles
```

### Issue 7: Sistema de Regeneración de Embeddings
- **Método**: `regenerate_embeddings(model_name=None)`
- **Funcionalidad**:
  - Soporte para múltiples modelos
  - Procesamiento por lotes
  - Reanudación de procesos interrumpidos
  - Comparación de rendimientos

**Implementación**:
```python
def regenerate_embeddings(self, model_name: str = None) -> Dict[str, Any]:
    # 1. Configurar modelo de embeddings
    # 2. Procesar por lotes
    # 3. Guardar progreso
    # 4. Métricas de rendimiento
```

### Issue 8: Pipeline Completo de Reconstrucción
- **Método**: `rebuild_database(source_files, strategy, model)`
- **Flujo**:
  1. Backup de base de datos actual
  2. Limpieza completa
  3. Procesamiento con Docling
  4. Chunking mejorado
  5. Generación de embeddings
  6. Validación final
  7. Reporte de resultados

**Implementación**:
```python
def rebuild_database(self, source_files: str, strategy: str, model: str) -> Dict[str, Any]:
    # 1. Backup automático
    # 2. Limpieza completa
    # 3. Procesamiento con Docling
    # 4. Chunking mejorado
    # 5. Generación de embeddings
    # 6. Validación final
    # 7. Reporte detallado
```

### Issue 9: Sistema de Experimentación Controlada
- **Métodos**: `create_experiment()`, `compare_experiments()`
- **Funcionalidad**:
  - Crear bases de datos de prueba
  - Comparar diferentes estrategias
  - Métricas de rendimiento
  - Selección automática de mejor configuración

**Implementación**:
```python
def create_experiment(self, experiment_name: str, config: Dict) -> str:
    # 1. Crear base de datos experimental
    # 2. Aplicar configuración específica
    # 3. Generar reporte de experimento

def compare_experiments(self, experiment_names: List[str]) -> Dict[str, Any]:
    # 1. Comparar métricas entre experimentos
    # 2. Generar reporte comparativo
    # 3. Recomendar mejor configuración
```

### Issue 10: Monitoreo y Reportes
- **Métodos**: `get_rebuild_status()`, `generate_quality_report()`
- **Métricas**:
  - Estadísticas de chunks generados
  - Tiempos de procesamiento
  - Calidad de embeddings
  - Comparaciones antes/después

**Implementación**:
```python
def get_rebuild_status(self) -> Dict[str, Any]:
    # 1. Estado actual del proceso
    # 2. Progreso completado
    # 3. Tiempos estimados

def generate_quality_report(self) -> Dict[str, Any]:
    # 1. Estadísticas de calidad
    # 2. Comparación antes/después
    # 3. Recomendaciones
```

### Issue 11: Integración con GUI Streamlit
- **Modificar**: `rag_interface.py`
- **Añadir**: métodos para usar `RAGDatabaseManager`
- **Funcionalidad**:
  - Botón de reconstrucción en GUI
  - Indicadores de progreso
  - Selección de estrategias
  - Visualización de resultados

**Implementación**:
```python
# En rag_interface.py
class RAGInterface:
    def __init__(self):
        # ... código existente ...
        self.db_manager = RAGDatabaseManager()

    def rebuild_rag_database(self, strategy: str, model: str) -> Dict[str, Any]:
        # Interfaz para GUI
        return self.db_manager.rebuild_database(...)
```

### Issue 12: Testing Completo
- **Crear**: `tests/test_database_manager.py`
- **Tests unitarios**: cada método individual
- **Tests de integración**: flujo completo
- **Tests de rendimiento**: tiempo y calidad
- **Tests de rollback**: recuperación de errores

**Implementación**:
```python
# tests/test_database_manager.py
class TestRAGDatabaseManager:
    def test_backup_and_restore(self):
        # Test de backup y restauración

    def test_docling_preprocessing(self):
        # Test de preprocesamiento con Docling

    def test_chunking_quality(self):
        # Test de calidad de chunking

    # ... más tests ...
```

## Dependencias entre Issues

```
1 (Estructura) → 2 (Limpieza) → 3 (Docling) → 4 (Análisis) →
5-6 (Chunking y Validación) → 7 (Embeddings) → 8 (Pipeline) →
9 (Experimentación) → 10 (Monitoreo) → 11 (GUI) → 12 (Testing)
```

## Flujo Principal de Uso

```python
# Uso típico para reconstrucción completa
manager = RAGDatabaseManager()

# Opción 1: Reconstrucción simple
result = manager.rebuild_database(
    source_files="transcripts_for_rag/",
    strategy="semantic_enhanced",
    model="all-MiniLM-L6-v2"
)

# Opción 2: Experimentación controlada
exp_id = manager.create_experiment(
    "test_docling_semantic",
    {
        "strategy": "semantic_enhanced",
        "model": "all-MiniLM-L6-v2",
        "docling_enabled": True,
        "chunk_size": 800,
        "overlap": 150
    }
)

# Opción 3: Comparación de estrategias
comparison = manager.compare_experiments([
    "test_character_basic",
    "test_semantic_enhanced",
    "test_docling_optimized"
])
```

## Configuraciones de Chunking Propuestas

### 1. `character_basic` (Baseline)
- Estrategia: Caracteres simple
- Chunk size: 1000
- Overlap: 200
- Docling: No

### 2. `semantic_enhanced` (Mejorado)
- Estrategia: Semántico mejorado
- Chunk size: 800 (ajuste dinámico)
- Overlap: 150
- Docling: Sí

### 3. `docling_optimized` (Óptimo)
- Estrategia: Semántico + Docling
- Chunk size: 600-1200 (dinámico)
- Overlap: 100-200 (según contenido)
- Docling: Sí, configuración completa

## Métricas de Calidad Propuestas

### Métricas de Texto
- **Densidad de información**: palabras únicas / palabras totales
- **Coherencia estructural**: puntuación de estructura lógica
- **Limpieza**: porcentaje de texto libre de artefactos

### Métricas de Chunks
- **Longitud promedio**: caracteres por chunk
- **Superposición efectiva**: cantidad de contexto compartido
- **Cohesión semántica**: similitud entre partes del chunk

### Métricas de Embeddings
- **Cobertura**: % del texto original representado
- **Calidad de recuperación**: precisión en búsquedas
- **Rendimiento**: tiempo de generación y consulta

## Integración con GUI Streamlit

### Nueva Pestaña: "Gestión RAG"

**Secciones**:
1. **Estado Actual**: Estadísticas de la base de datos
2. **Reconstrucción**: Configurar y ejecutar reconstrucción
3. **Experimentación**: Probar diferentes configuraciones
4. **Comparación**: Visualizar resultados de experimentos
5. **Reportes**: Análisis detallado de calidad

**Controles**:
- Selector de estrategia de chunking
- Selector de modelo de embeddings
- Configuración de Docling
- Indicadores de progreso
- Visualización de resultados

## Plan de Implementación

### Fase 1: Fundación (Issues 1-4)
- Estructura básica de la clase
- Sistema de backup y limpieza
- Integración con Docling
- Análisis de calidad

### Fase 2: Procesamiento (Issues 5-8)
- Chunking mejorado
- Validación de calidad
- Regeneración de embeddings
- Pipeline completo

### Fase 3: Experimentación (Issues 9-10)
- Sistema de experimentos
- Monitoreo y reportes
- Comparación de resultados

### Fase 4: Integración (Issues 11-12)
- Integración con GUI
- Testing completo
- Documentación

## Riesgos y Mitigaciones

### Riesgo 1: Pérdida de Datos
- **Mitigación**: Backup automático antes de cualquier operación
- **Recuperación**: Sistema de restauración completo

### Riesgo 2: Tiempo de Procesamiento
- **Mitigación**: Procesamiento por lotes y reanudación
- **Optimización**: Paralelización donde sea posible

### Riesgo 3: Calidad Inferior
- **Mitigación**: Validación en cada etapa
- **Recuperación**: Rollback automático si la calidad es insuficiente

### Riesgo 4: Complejidad de Uso
- **Mitigación**: Interfaz simplificada en GUI
- **Documentación**: Guías detalladas y ejemplos

## Success Criteria

1. **Calidad de Chunks**: Aumentar la coherencia semántica en un 50%
2. **Precisión de Búsqueda**: Mejorar la relevancia en un 30%
3. **Tiempo de Procesamiento**: Mantener o mejorar el rendimiento actual
4. **Facilidad de Uso**: Reducir la complejidad para el usuario final
5. **Experimentación**: Permitir pruebas sin riesgo de pérdida de datos

## Timeline Estimado

- **Fase 1**: 2-3 días
- **Fase 2**: 3-4 días
- **Fase 3**: 2-3 días
- **Fase 4**: 2 días
- **Total**: 9-12 días

## Entregables

1. **Código Fuente**: `rag_engine/database_manager.py`
2. **Tests**: `tests/test_database_manager.py`
3. **GUI**: Modificaciones en `rag_interface.py` y `gui_streamlit.py`
4. **Documentación**: Guías de uso y API reference
5. **Reportes**: Sistema de métricas y análisis

---

**Nota**: Este plan está diseñado para ser implementado de forma incremental, con cada issue entregando valor funcional de forma independiente.