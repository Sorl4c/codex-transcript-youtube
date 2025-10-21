# RAG Test Suite

Test suite automatizado completo para el sistema RAG (Retrieval-Augmented Generation) con optimización sqlite-vec.

## 📁 Estructura de Tests

```
tests/
├── conftest.py                    # Configuración global pytest
├── test_rag/                      # Tests específicos del sistema RAG
│   ├── __init__.py
│   ├── conftest.py               # Fixtures y configuración RAG
│   ├── test_database/            # Tests del módulo database
│   │   ├── __init__.py
│   │   ├── test_sqlite_vec.py   # Tests extensión sqlite-vec
│   │   ├── test_vec0_migration.py # Tests migración a vec0
│   │   └── test_vector_operations.py # Tests KNN nativas
│   ├── test_retriever/           # Tests del módulo retriever
│   │   ├── __init__.py
│   │   └── test_hybrid_retriever.py # Tests búsqueda híbrida RRF
│   ├── test_integration/         # Tests de integración
│   │   ├── __init__.py
│   │   └── test_cli_commands.py # Tests comandos CLI
│   ├── test_performance/         # Tests de rendimiento
│   │   └── # (Por implementar)
│   └── test_regression/          # Tests de regresión
│       ├── __init__.py
│       └── test_sqlite_optimization.py # Tests optimización sqlite-vec
└── legacy/                       # Tests existentes (compatibilidad)
    ├── test_parser.py
    ├── test_db.py
    └── ...
```

## 🚀 Instalación de Dependencias

### 1. Instalar dependencias de testing:
```bash
pip install -r requirements-test.txt
```

### 2. (Opcional) Instalar dependencias adicionales para reporting avanzado:
```bash
pip install pytest-html pytest-json-report pytest-profiling
```

## 🎯 Ejecución de Tests

### Tests Modulares por Componente

#### Tests de Base de Datos (sqlite-vec, vec0, KNN)
```bash
# Todos los tests de database
pytest tests/test_rag/test_database/ -v

# Tests específicos de sqlite-vec
pytest tests/test_rag/test_database/test_sqlite_vec.py -v

# Tests de migración a vec0
pytest tests/test_rag/test_database/test_vec0_migration.py -v

# Tests de operaciones vectoriales KNN
pytest tests/test_rag/test_database/test_vector_operations.py -v
```

#### Tests de Retriever (búsqueda híbrida, RRF)
```bash
# Tests de hybrid retriever
pytest tests/test_rag/test_retriever/test_hybrid_retriever.py -v

# Tests con diferentes modos
pytest tests/test_rag/test_retriever/ -v -k "hybrid"
```

#### Tests de Integración (CLI, end-to-end)
```bash
# Tests de comandos CLI
pytest tests/test_rag/test_integration/test_cli_commands.py -v

# Tests de integración completos
pytest tests/test_rag/test_integration/ -v
```

#### Tests de Regresión (validación optimización)
```bash
# Tests de regresión sqlite-vec
pytest tests/test_rag/test_regression/test_sqlite_optimization.py -v

# Todos los tests de regresión
pytest tests/test_rag/test_regression/ -v -m regression
```

### Script de Ejecución RAG

Usar el script especializado para ejecución de tests RAG:

```bash
# Validación completa del sistema RAG
python scripts/run_rag_tests.py --full-validation

# Con coverage y verbose
python scripts/run_rag_tests.py --full-validation --coverage --verbose

# Tests críticos rápidos
python scripts/run_rag_tests.py --critical-only

# Tests por módulo específico
python scripts/run_rag_tests.py --module database
python scripts/run_rag_tests.py --module retriever
python scripts/run_rag_tests.py --module integration

# Tests de rendimiento
python scripts/run_rag_tests.py --performance-only

# Tests de regresión
python scripts/run_rag_tests.py --regression-only

# Guardar resultados en JSON
python scripts/run_rag_tests.py --full-validation --output results.json
```

### Comandos pytest直接

#### Todos los tests RAG
```bash
# Ejecutar todos los tests RAG
pytest tests/test_rag/ -v

# Con coverage
pytest tests/test_rag/ --cov=rag_engine --cov-report=html

# Tests paralelos (más rápido)
pytest tests/test_rag/ -n auto
```

#### Tests por marcadores (markers)
```bash
# Tests de rendimiento
pytest tests/test_rag/ -m performance -v

# Tests de integración
pytest tests/test_rag/ -m integration -v

# Tests de regresión
pytest tests/test_rag/ -m regression -v

# Tests lentos
pytest tests/test_rag/ -m slow -v

# Tests que requieren LLM
pytest tests/test_rag/ -m requires_llm -v
```

## 📊 Métricas y Umbrales de Rendimiento

### Umbrales Definidos
- **Consultas KNN**: < 10ms (0.01s)
- **Consultas híbridas**: < 50ms (0.05s)
- **Generación embeddings**: < 100ms (0.1s)
- **Ingestión documentos**: < 1s por documento
- **Uso memoria**: < 100MB para operaciones de test

### Validaciones Críticas
- ✅ sqlite-vec extension loaded correctamente
- ✅ Tablas vec0 creadas y funcionando
- ✅ Queries KNN nativas operativas
- ✅ Sistema híbrido RRF funcional
- ✅ Rendimiento dentro de umbrales

## 🔧 Fixtures y Configuración

### Fixtures Globales (conftest.py)
- `temp_dir`: Directorio temporal para tests
- `temp_file`: Archivo temporal para tests
- `sample_text_data`: Datos de texto de muestra
- `performance_thresholds`: Umbrales de rendimiento

### Fixtures RAG (test_rag/conftest.py)
- `test_database`: Base de datos SQLite temporal con vec0
- `sample_documents`: Documentos de prueba consistentes
- `sample_queries`: Queries de prueba categorizadas
- `mock_embeddings`: Embeddings pre-calculadas
- `populated_test_database`: BD pre-poblada con datos
- `rag_performance_thresholds`: Umbrales específicos RAG

## 📋 Tipos de Tests Implementados

### 1. Tests de Base de Datos (`test_database/`)
- **test_sqlite_vec.py**: Instalación y configuración sqlite-vec
- **test_vec0_migration.py**: Migración a tablas vec0 virtuales
- **test_vector_operations.py**: Operaciones KNN nativas y búsquedas vectoriales

### 2. Tests de Retriever (`test_retriever/`)
- **test_hybrid_retriever.py**: Búsqueda híbrida con RRF (Reciprocal Rank Fusion)

### 3. Tests de Integración (`test_integration/`)
- **test_cli_commands.py**: Comandos CLI (ingest, query, stats)

### 4. Tests de Regresión (`test_regression/`)
- **test_sqlite_optimization.py**: Validación de optimización sqlite-vec

## 🎛️ Configuración Avanzada

### Variables de Entorno para Tests
```bash
export TESTING=true
export RAG_TEST_MODE=true
export LOG_LEVEL=DEBUG
```

### Configuración pytest.ini (opcional)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
markers =
    slow: mark test as slow running
    integration: mark test as integration test
    performance: mark test as performance test
    regression: mark test as regression test
    requires_llm: mark test as requiring LLM access
```

## 📈 Reporting y Cobertura

### Generar Reportes de Cobertura
```bash
# Reporte HTML
pytest tests/test_rag/ --cov=rag_engine --cov-report=html

# Reporte en terminal
pytest tests/test_rag/ --cov=rag_engine --cov-report=term-missing

# Reporte JSON
pytest tests/test_rag/ --cov=rag_engine --cov-report=json
```

### Reportes de Performance
```bash
# Benchmarks con pytest-benchmark
pytest tests/test_rag/test_performance/ --benchmark-only

# Guardar resultados de benchmark
pytest tests/test_rag/test_performance/ --benchmark-only --benchmark-json=benchmark.json
```

### Reportes HTML
```bash
# Reporte HTML completo
pytest tests/test_rag/ --html=report.html --self-contained-html

# Reporte con screenshots para GUI tests (si aplica)
pytest tests/test_rag/ --html=report.html --self-contained-html --capture=no
```

## 🐛 Debugging de Tests

### Ejecución en Modo Debug
```bash
# Detenerse en primer fallo
pytest tests/test_rag/ -x

# Modo debug con pdb
pytest tests/test_rag/ --pdb

# Mostrar output de tests (stdout/stderr)
pytest tests/test_rag/ -s

# Ejecutar test específico
pytest tests/test_rag/test_database/test_sqlite_vec.py::TestSQLiteVecExtension::test_sqlite_vec_import -v
```

### Logs y Traces
```bash
# Ver logs completos
pytest tests/test_rag/ --capture=no --log-cli-level=DEBUG

# Logs para módulo específico
pytest tests/test_rag/test_database/ --log-cli-level=DEBUG
```

## 🔄 Integración CI/CD

### GitHub Actions (Ejemplo)
```yaml
name: RAG Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run critical tests
      run: python scripts/run_rag_tests.py --critical-only
    - name: Run full validation
      run: python scripts/run_rag_tests.py --full-validation --coverage
```

### Pre-commit Hooks
```bash
# Instalar pre-commit
pip install pre-commit

# Configurar .pre-commit-config.yaml
# Ejecutar tests antes de commits
pre-commit run --all-files
```

## 📝 Mejores Prácticas

### 1. Escribir Tests
- Usar nombres descriptivos: `test_sqlite_vec_extension_loads_correctly`
- Una afirmación por test cuando sea posible
- Usar fixtures para datos consistentes
- Documentar comportamiento esperado

### 2. Tests de Rendimiento
- Usar `@pytest.mark.performance` para tests lentos
- Definir umbrales claros en fixtures
- Medir tiempos consistentemente
- Considerar variaciones de sistema

### 3. Tests de Integración
- Probar flujos completos del usuario
- Validar integración entre componentes
- Usar datos realistas pero aislados
- Limpiar recursos después de tests

### 4. Tests de Regresión
- Validar optimizaciones críticas (sqlite-vec)
- Verificar que no hay degradación de rendimiento
- Probar casos límite y edge cases
- Mantener tests actualizados con cambios

## 🚨 Solución de Problemas Comunes

### Issues Frecuentes

1. **sqlite-vec no encontrado**
   ```bash
   pip install sqlite-vec --force-reinstall
   ```

2. **Tests de BD fallan con permisos**
   ```bash
   # Asegurarse que no hay conexiones abiertas a BD de test
   pytest tests/test_rag/test_database/ -v --reuse-db
   ```

3. **Tests lentos**
   ```bash
   # Ejecutar solo tests críticos
   python scripts/run_rag_tests.py --critical-only

   # O excluir tests lentos
   pytest tests/test_rag/ -m "not slow"
   ```

4. **Coverage incompleto**
   ```bash
   # Verificar qué código no está cubierto
   pytest tests/test_rag/ --cov=rag_engine --cov-report=term-missing
   ```

5. **Problemas con fixtures**
   ```bash
   # Verificar fixtures disponibles
   pytest tests/test_rag/ --fixtures
   ```

## 🔗 Recursos Adicionales

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [sqlite-vec GitHub](https://github.com/asg017/sqlite-vec)
- [RAG System Documentation](../docs/)