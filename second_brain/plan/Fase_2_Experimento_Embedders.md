# Fase 2: Experimento con Embedders Candidatos

## Objetivo del Día

Comparar rendimiento y calidad entre diferentes embedders usando un corpus sintético multitemático con 3 categorías.

**Duración estimada:** 4-5 horas
**Resultado esperado:** Matriz de ingestión completada para 3 embedders con métricas objetivas de rendimiento usando dataset con tres dominios (tecnología, aprendizaje/productividad, deporte/bienestar) y chunks sintéticos.

## Checklist Completo

### ✅ Paso 1: Preparación y Cache Invalidation (30 minutos)

#### Checklist:
- [ ] Validar que Fase 1 completó exitosamente
- [ ] Limpiar cache de sentence-transformers
- [ ] Limpiar base de datos PostgreSQL
- [ ] Configurar variables de entorno para embedder #2
- [ ] Validar que todo está limpio

#### Comandos:
```bash
# 1.1 Validar que Fase 1 completó
if [ ! -f "second_brain/plan/logs/fase_1_metrics.json" ]; then
    echo "❌ Fase 1 no completada. Ejecutar Fase 1 primero."
    exit 1
fi
echo "✅ Fase 1 completada detectada"

# 1.2 Limpiar cache de sentence-transformers (CRÍTICO)
echo "🧹 Limpiando cache de sentence-transformers..."
rm -rf ~/.cache/torch/sentence_transformers/
rm -rf ~/.cache/huggingface/
echo "✅ Cache limpiada"

# 1.3 Limpiar completamente base de datos PostgreSQL
echo "🗑️ Limpiando base de datos PostgreSQL..."
psql -d rag_experiments -c "
DROP TABLE IF EXISTS document_embeddings CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
"
echo "✅ Tablas eliminadas"

# 1.4 Validar que la BD está vacía
psql -d rag_experiments -c "
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE '%document%';
"
# Esperado: 0 filas

# 1.5 Configurar variables para embedder #2 (MPNet)
echo "⚙️ Configurando para embedder #2: all-mpnet-base-v2"
cat > .env.fase2 << EOF
# PostgreSQL Configuration
DATABASE_BACKEND=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_experiments
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password

# Embedding Configuration - Fase 2 (MPNet)
EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DIM=768

# Experiment Configuration
EXPERIMENT_MODE=true
SAVE_RAW_OUTPUTS=true
LOG_LEVEL=DEBUG
PHASE=fase_2
EOF

# Usar variables de Fase 2
export $(cat .env.fase2 | xargs)
echo "✅ Variables configuradas:"
echo "   EMBEDDING_MODEL: $EMBEDDING_MODEL"
echo "   EMBEDDING_DIM: $EMBEDDING_DIM"
```

### ✅ Paso 2: Setup Schema para Nueva Dimensión (30 minutos)

#### Checklist:
- [ ] Modificar script de schema para nueva dimensión
- [ ] Recrear tablas con EMBEDDING_DIM=768
- [ ] Validar que la nueva dimensión funciona
- [ ] Verificar constraints de dimensión
- [ ] Test básico de inserción

#### Comandos:
```bash
# 2.1 Recrear schema con nueva dimensión
echo "🔧 Creando schema para dimensión 768..."
python setup_schema.py
# Esperado: 🔧 Creando schema... ✅ Schema creado exitosamente

# 2.2 Validar nueva dimensión en schema
psql -d rag_experiments -c "
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'document_embeddings' AND column_name = 'embedding';
"
# Esperado: embedding | vector | 768

# 2.3 Validar constraint de dimensión
psql -d rag_experiments -c "
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'document_embeddings'::regclass;
"
# Esperado: Constraint CHECK array_length(embedding, 1) = 768
```

### ✅ Paso 3: Ingestión con Embedder #2 (MPNet - 768d) (90 minutos)

#### Checklist:
- [ ] Descargar modelo all-mpnet-base-v2
- [ ] Cargar dataset experimental de Fase 1
- [ ] Generar embeddings de 768 dimensiones
- [ ] Insertar en PostgreSQL validando nueva dimensión
- [ ] Registrar métricas detalladas
- [ ] Validar que no hay duplicados

#### Archivo: `ingest_fase2_mpnet.py`
```python
#!/usr/bin/env python3
"""
Ingestión Fase 2a: Modelo all-mpnet-base-v2 (768 dimensiones)
"""
import os
import json
import time
import psutil
import hashlib
from sentence_transformers import SentenceTransformer
import numpy as np

from postgresql_database_experimental import PostgreSQLVectorDatabase

def clear_model_cache():
    """Limpiar cache de modelos completamente"""
    import torch
    import gc

    # Limpiar cache de PyTorch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Forzar garbage collection
    gc.collect()

    print("🧹 Cache de modelos limpiada")

def ingest_mpnet_model():
    """Ingestar dataset con modelo MPNet (768 dimensiones)"""

    print("🚀 Iniciando ingestión Fase 2a: Modelo MPNet (768d)")
    print(f"🤖 Modelo: {os.getenv('EMBEDDING_MODEL')}")
    print(f"📏 Dimensión: {os.getenv('EMBEDDING_DIM')}")

    # Limpiar cache completamente
    clear_model_cache()

    # Cargar corpus sintético multitemático
    print("\n📂 Cargando corpus sintético multitemático...")
    with open("second_brain/plan/data/corpus_multitematico.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    print(f"✅ Corpus cargado: {len(dataset)} chunks (3 categorías: tecnología, aprendizaje/productividad, deporte/bienestar)")
    print(f"🎯 Objetivo: Medir relevancia cruzada entre dominios")

    # Registrar uso de recursos antes de cargar modelo
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    print(f"💾 Memoria inicial: {initial_memory:.1f} MB")

    # Inicializar modelo MPNet
    print(f"\n🤖 Cargando modelo {os.getenv('EMBEDDING_MODEL')}...")
    model_start = time.time()

    try:
        model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'))
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        print("💡 Intentando descarga manual...")
        # Forzar descarga
        model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'), cache_folder='./cache')

    model_load_time = time.time() - model_start
    print(f"✅ Modelo cargado en {model_load_time:.2f}s")

    # Registrar memoria después de cargar modelo
    after_model_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    model_memory = after_model_memory - initial_memory
    print(f"💾 Memoria usada por modelo: {model_memory:.1f} MB")

    # Validar dimensión del modelo
    test_embedding = model.encode(["test"])
    actual_dim = len(test_embedding[0])
    expected_dim = int(os.getenv('EMBEDDING_DIM'))

    if actual_dim != expected_dim:
        raise ValueError(
            f"❌ Dimensión incorrecta: modelo genera {actual_dim}, "
            f"configurado para {expected_dim}"
        )
    print(f"✅ Dimensión validada: {actual_dim}")

    # Inicializar base de datos
    print("\n🔌 Inicializando PostgreSQL...")
    db = PostgreSQLVectorDatabase()

    # Preparar documentos (mismo formato que Fase 1)
    print("\n📋 Preparando documentos para ingestión...")
    documents_to_ingest = []

    for i, chunk_data in enumerate(dataset):
        content = chunk_data['content']

        metadata = {
            'source_document': chunk_data['source_document'],
            'source_hash': chunk_data['source_hash'],
            'chunking_strategy': 'synthetic',
            'chunk_index': chunk_data['chunk_index'],
            'semantic_title': chunk_data.get('titulo', f"MPNet chunk {i+1}"),
            'semantic_summary': chunk_data.get('resumen', content[:100] + "..."),
            'additional_metadata': {
                'phase': 'fase_2a',
                'model': os.getenv('EMBEDDING_MODEL'),
                'dimension': actual_dim,
                'dataset_type': 'synthetic_multitematic',
                'categoria': chunk_data.get('categoria', 'tecnologia'),
                'fuente': chunk_data.get('fuente', 'sintetico'),
                'cross_domain_relevance': True
            }
        }

        documents_to_ingest.append((content, None, metadata))

    print(f"✅ {len(documents_to_ingest)} documentos preparados")

    # Generar embeddings en batch (monitorear recursos)
    print(f"\n🧮 Generando embeddings {actual_dim}D para {len(documents_to_ingest)} chunks...")
    embedding_start = time.time()

    # Medir recursos durante generación
    peak_memory = initial_memory

    texts = [doc[0] for doc in documents_to_ingest]

    # Generar en batches más pequeños para controlar memoria
    batch_size = 5
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        print(f"   Procesando batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch_texts)} chunks)")

        batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
        all_embeddings.extend(batch_embeddings)

        # Monitorear uso de memoria
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        peak_memory = max(peak_memory, current_memory)
        print(f"   Memoria actual: {current_memory:.1f} MB (pico: {peak_memory:.1f} MB)")

    embeddings = np.array(all_embeddings)
    embedding_time = time.time() - embedding_start
    embedding_per_chunk = embedding_time / len(embeddings)

    print(f"✅ Embeddings generados en {embedding_time:.2f}s")
    print(f"⏱️ Tiempo por chunk: {embedding_per_chunk:.3f}s")
    print(f"💾 Pico de memoria: {peak_memory:.1f} MB")

    # Preparar para ingestión
    documents_with_embeddings = []
    for (content, _, metadata), embedding in zip(documents_to_ingest, embeddings):
        documents_with_embeddings.append((content, embedding.tolist(), metadata))

    # Ingestar en base de datos
    print(f"\n📥 Ingestando {len(documents_with_embeddings)} documentos en PostgreSQL...")
    ingestion_start = time.time()

    try:
        db.add_documents_with_metadata(documents_with_embeddings)
        ingestion_time = time.time() - ingestion_start
        print(f"✅ Ingestión completada en {ingestion_time:.2f}s")
    except Exception as e:
        print(f"❌ Error en ingestión: {e}")
        raise

    # Validar resultados
    print(f"\n📊 Validando resultados...")
    stats = db.get_stats()
    print(f"📈 Estadísticas finales:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Validar no duplicados
    print(f"\n🔍 Verificando duplicados...")
    with db.pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT source_hash, COUNT(*) as count
                FROM documents
                GROUP BY source_hash
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()

            if duplicates:
                print(f"⚠️ Se encontraron {len(duplicates)} hashes duplicados:")
                for hash_val, count in duplicates:
                    print(f"   {hash_val[:16]}...: {count} veces")
            else:
                print("✅ No se encontraron duplicados")

    # Validar dimensión guardada
    print(f"\n🔍 Validando dimensión guardada...")
    with db.pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT array_length(embedding, 1) as dim, COUNT(*) as count
                FROM document_embeddings
                GROUP BY array_length(embedding, 1)
            """)
            dimensions = cursor.fetchall()

            for dim, count in dimensions:
                print(f"   {dim} dimensiones: {count} embeddings")

    # Guardar métricas detalladas
    metrics = {
        'phase': 'fase_2a',
        'model': os.getenv('EMBEDDING_MODEL'),
        'dimension': actual_dim,
        'dataset_size': len(dataset),
        'model_load_time': model_load_time,
        'model_memory_mb': model_memory,
        'peak_memory_mb': peak_memory,
        'embedding_time': embedding_time,
        'embedding_per_chunk': embedding_per_chunk,
        'ingestion_time': ingestion_time,
        'ingestion_per_chunk': ingestion_time / len(documents_with_embeddings),
        'final_stats': stats,
        'duplicates_found': len(duplicates),
        'dimensions_found': dimensions,
        'batch_size': batch_size,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    metrics_file = "second_brain/plan/logs/fase_2a_mpnet_metrics.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n📄 Métricas guardadas en: {metrics_file}")

    # Test de búsqueda básica
    print(f"\n🔍 Probando búsqueda básica...")
    test_query = "¿Qué es un sistema?"
    test_embedding = model.encode([test_query])[0].tolist()

    results = db.search_similar(test_embedding, top_k=3)
    print(f"✅ Búsqueda test: {len(results)} resultados")
    for i, (content, similarity) in enumerate(results):
        print(f"   Resultado {i+1}: similarity={similarity:.3f}, content='{content[:50]}...'")

    db.close()
    clear_model_cache()
    print(f"\n🎉 Fase 2a (MPNet) completada exitosamente!")

if __name__ == "__main__":
    ingest_mpnet_model()
```

#### Comandos:
```bash
# 3.1 Crear script de ingestión MPNet
# (Crear el archivo ingest_fase2_mpnet.py con el contenido de arriba)

# 3.2 Ejecutar ingestión MPNet
python ingest_fase2_mpnet.py
# Esperado: 🚀 Ingestión completada con métricas de 768 dimensiones
```

### ✅ Paso 4: Cache Invalidation y Preparación Embedder #3 (30 minutos)

#### Checklist:
- [ ] Validar que MPNet completó exitosamente
- [ ] Limpiar cache de sentence-transformers
- [ ] Limpiar base de datos PostgreSQL
- [ ] Configurar variables para embedder #3 (Multilingüe)
- [ ] Validar configuración para 384 dimensiones

#### Comandos:
```bash
# 4.1 Validar MPNet completado
if [ ! -f "second_brain/plan/logs/fase_2a_mpnet_metrics.json" ]; then
    echo "❌ Fase 2a (MPNet) no completó exitosamente"
    exit 1
fi
echo "✅ Fase 2a (MPNet) completada detectada"

# 4.2 Limpiar cache (CRÍTICO para cambiar de modelo)
echo "🧹 Limpiando cache para embedder #3..."
rm -rf ~/.cache/torch/sentence_transformers/
rm -rf ~/.cache/huggingface/
rm -rf ./cache/
echo "✅ Cache limpiada"

# 4.3 Limpiar base de datos
echo "🗑️ Limpiando base de datos para embedder #3..."
psql -d rag_experiments -c "
DROP TABLE IF EXISTS document_embeddings CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
"

# 4.4 Configurar para embedder #3 (Multilingüe)
echo "⚙️ Configurando para embedder #3: multilingual-MiniLM"
cat > .env.fase2b << EOF
# PostgreSQL Configuration
DATABASE_BACKEND=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_experiments
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password

# Embedding Configuration - Fase 2b (Multilingual)
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIM=384

# Experiment Configuration
EXPERIMENT_MODE=true
SAVE_RAW_OUTPUTS=true
LOG_LEVEL=DEBUG
PHASE=fase_2b
EOF

# Usar variables de Fase 2b
export $(cat .env.fase2b | xargs)
echo "✅ Variables configuradas:"
echo "   EMBEDDING_MODEL: $EMBEDDING_MODEL"
echo "   EMBEDDING_DIM: $EMBEDDING_DIM"
```

### ✅ Paso 5: Ingestión con Embedder #3 (Multilingüe - 384d) (60 minutos)

#### Checklist:
- [ ] Descargar modelo multilingüe
- [ ] Cargar mismo dataset experimental
- [ ] Generar embeddings de 384 dimensiones
- [ ] Insertar en PostgreSQL
- [ ] Registrar métricas comparativas
- [ ] Validar mejora en español

#### Archivo: `ingest_fase2_multilingual.py`
```python
#!/usr/bin/env python3
"""
Ingestión Fase 2b: Modelo Multilingüe (384 dimensiones)
"""
import os
import json
import time
import psutil
from sentence_transformers import SentenceTransformer
import numpy as np

from postgresql_database_experimental import PostgreSQLVectorDatabase

def clear_model_cache():
    """Limpiar cache de modelos completamente"""
    import torch
    import gc

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    gc.collect()
    print("🧹 Cache de modelos limpiada")

def ingest_multilingual_model():
    """Ingestar dataset con modelo multilingüe (384 dimensiones)"""

    print("🚀 Iniciando ingestión Fase 2b: Modelo Multilingüe (384d)")
    print(f"🤖 Modelo: {os.getenv('EMBEDDING_MODEL')}")
    print(f"📏 Dimensión: {os.getenv('EMBEDDING_DIM')}")

    clear_model_cache()

    # Cargar corpus sintético multitemático
    print("\n📂 Cargando corpus sintético multitemático...")
    with open("second_brain/plan/data/corpus_multitematico.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    print(f"✅ Corpus cargado: {len(dataset)} chunks (3 categorías: tecnología, aprendizaje/productividad, deporte/bienestar)")
    print(f"🎯 Objetivo: Medir relevancia cruzada entre dominios")

    # Recursos iniciales
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
    print(f"💾 Memoria inicial: {initial_memory:.1f} MB")

    # Cargar modelo multilingüe
    print(f"\n🤖 Cargando modelo {os.getenv('EMBEDDING_MODEL')}...")
    model_start = time.time()

    try:
        model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'))
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        print("💡 Intentando con descarga explícita...")
        model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'), cache_folder='./cache_multilingual')

    model_load_time = time.time() - model_start
    print(f"✅ Modelo cargado en {model_load_time:.2f}s")

    after_model_memory = psutil.Process().memory_info().rss / 1024 / 1024
    model_memory = after_model_memory - initial_memory
    print(f"💾 Memoria usada por modelo: {model_memory:.1f} MB")

    # Validar dimensión
    test_embedding = model.encode(["test"])
    actual_dim = len(test_embedding[0])
    expected_dim = int(os.getenv('EMBEDDING_DIM'))

    if actual_dim != expected_dim:
        raise ValueError(
            f"❌ Dimensión incorrecta: modelo genera {actual_dim}, "
            f"configurado para {expected_dim}"
        )
    print(f"✅ Dimensión validada: {actual_dim}")

    # Test de calidad en español (importante para modelo multilingüe)
    print(f"\n🌍 Probando calidad en español...")
    spanish_queries = [
        "¿Qué es la inteligencia artificial?",
        "Cómo funciona el aprendizaje automático",
        "Sistemas de bases de datos relacionales"
    ]

    spanish_embeddings = model.encode(spanish_queries)
    print(f"✅ {len(spanish_queries)} queries españoles procesadas")

    # Inicializar base de datos
    print("\n🔌 Inicializando PostgreSQL...")
    db = PostgreSQLVectorDatabase()

    # Preparar documentos
    print("\n📋 Preparando documentos para ingestión...")
    documents_to_ingest = []

    for i, chunk_data in enumerate(dataset):
        content = chunk_data['content']

        metadata = {
            'source_document': chunk_data['source_document'],
            'source_hash': chunk_data['source_hash'],
            'chunking_strategy': 'synthetic',
            'chunk_index': chunk_data['chunk_index'],
            'semantic_title': chunk_data.get('titulo', f"Multilingual chunk {i+1}"),
            'semantic_summary': chunk_data.get('resumen', content[:100] + "..."),
            'additional_metadata': {
                'phase': 'fase_2b',
                'model': os.getenv('EMBEDDING_MODEL'),
                'dimension': actual_dim,
                'language_support': 'multilingual',
                'dataset_type': 'synthetic_multitematic',
                'categoria': chunk_data.get('categoria', 'tecnologia'),
                'fuente': chunk_data.get('fuente', 'sintetico'),
                'cross_domain_relevance': True
            }
        }

        documents_to_ingest.append((content, None, metadata))

    print(f"✅ {len(documents_to_ingest)} documentos preparados")

    # Generar embeddings
    print(f"\n🧮 Generando embeddings {actual_dim}D para {len(documents_to_ingest)} chunks...")
    embedding_start = time.time()

    texts = [doc[0] for doc in documents_to_ingest]
    embeddings = model.encode(texts, convert_to_numpy=True)

    embedding_time = time.time() - embedding_start
    embedding_per_chunk = embedding_time / len(embeddings)

    print(f"✅ Embeddings generados en {embedding_time:.2f}s")
    print(f"⏱️ Tiempo por chunk: {embedding_per_chunk:.3f}s")

    # Preparar para ingestión
    documents_with_embeddings = []
    for (content, _, metadata), embedding in zip(documents_to_ingest, embeddings):
        documents_with_embeddings.append((content, embedding.tolist(), metadata))

    # Ingestar
    print(f"\n📥 Ingestando {len(documents_with_embeddings)} documentos en PostgreSQL...")
    ingestion_start = time.time()

    db.add_documents_with_metadata(documents_with_embeddings)
    ingestion_time = time.time() - ingestion_start
    print(f"✅ Ingestión completada en {ingestion_time:.2f}s")

    # Validar resultados
    print(f"\n📊 Validando resultados...")
    stats = db.get_stats()
    print(f"📈 Estadísticas finales:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Validar no duplicados
    print(f"\n🔍 Verificando duplicados...")
    with db.pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT source_hash, COUNT(*) as count
                FROM documents
                GROUP BY source_hash
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            print(f"✅ Duplicados encontrados: {len(duplicates)}")

    # Guardar métricas
    metrics = {
        'phase': 'fase_2b',
        'model': os.getenv('EMBEDDING_MODEL'),
        'dimension': actual_dim,
        'dataset_size': len(dataset),
        'model_load_time': model_load_time,
        'model_memory_mb': model_memory,
        'embedding_time': embedding_time,
        'embedding_per_chunk': embedding_per_chunk,
        'ingestion_time': ingestion_time,
        'ingestion_per_chunk': ingestion_time / len(documents_with_embeddings),
        'final_stats': stats,
        'duplicates_found': len(duplicates),
        'spanish_queries_tested': len(spanish_queries),
        'language_support': 'multilingual',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    metrics_file = "second_brain/plan/logs/fase_2b_multilingual_metrics.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n📄 Métricas guardadas en: {metrics_file}")

    # Test de búsqueda en español
    print(f"\n🔍 Probando búsqueda en español...")
    test_query = "¿Qué es un sistema de bases de datos?"
    test_embedding = model.encode([test_query])[0].tolist()

    results = db.search_similar(test_embedding, top_k=3)
    print(f"✅ Búsqueda test español: {len(results)} resultados")
    for i, (content, similarity) in enumerate(results):
        print(f"   Resultado {i+1}: similarity={similarity:.3f}, content='{content[:50]}...'")

    db.close()
    clear_model_cache()
    print(f"\n🎉 Fase 2b (Multilingüe) completada exitosamente!")

if __name__ == "__main__":
    ingest_multilingual_model()
```

#### Comandos:
```bash
# 5.1 Crear script de ingestión multilingüe
# (Crear el archivo ingest_fase2_multilingual.py con el contenido de arriba)

# 5.2 Ejecutar ingestión multilingüe
python ingest_fase2_multilingual.py
# Esperado: 🚀 Ingestión completada con soporte multilingüe
```

### ✅ Paso 6: Crear Matriz de Ingestión (45 minutos)

#### Checklist:
- [ ] Recopilar métricas de los 3 embedders
- [ ] Crear matriz comparativa de rendimiento
- [ ] Analizar diferencias significativas
- [ ] Identificar patrones de rendimiento
- [ ] Preparar recomendaciones iniciales

#### Archivo: `create_ingestion_matrix.py`
```python
#!/usr/bin/env python3
"""
Crear matriz comparativa de ingestión para los 3 embedders
"""
import json
import os
from datetime import datetime

def create_ingestion_matrix():
    """Crear matriz comparativa de rendimiento de ingestión"""

    print("📊 Creando matriz comparativa de ingestión...")

    # Cargar métricas de las 3 fases
    metrics_files = {
        'MiniLM (Control)': 'second_brain/plan/logs/fase_1_metrics.json',
        'MPNet (Alta Calidad)': 'second_brain/plan/logs/fase_2a_mpnet_metrics.json',
        'Multilingual (Español)': 'second_brain/plan/logs/fase_2b_multilingual_metrics.json'
    }

    all_metrics = {}
    missing_files = []

    for name, file_path in metrics_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                all_metrics[name] = json.load(f)
            print(f"✅ Cargado: {name}")
        else:
            missing_files.append(file_path)
            print(f"❌ No encontrado: {file_path}")

    if missing_files:
        print(f"\n⚠️ Archivos faltantes: {missing_files}")
        print("Asegúrate de haber completado todas las fases de ingestión.")
        return

    # Crear matriz de ingestión
    print(f"\n📋 Creando matriz de ingestión...")

    matrix_data = []
    for name, metrics in all_metrics.items():
        # Extraer métricas clave
        ingestion_performance = {
            'Embedder': name,
            'Model': metrics.get('model', 'N/A'),
            'Dimension': metrics.get('dimension', 'N/A'),
            'Dataset_Size': metrics.get('dataset_size', 'N/A'),
            'Model_Load_Time_s': round(metrics.get('model_load_time', 0), 2),
            'Model_Memory_MB': round(metrics.get('model_memory_mb', 0), 1),
            'Embedding_Time_s': round(metrics.get('embedding_time', 0), 2),
            'Embedding_Per_Chunk_s': round(metrics.get('embedding_per_chunk', 0), 3),
            'Ingestion_Time_s': round(metrics.get('ingestion_time', 0), 2),
            'Ingestion_Per_Chunk_s': round(metrics.get('ingestion_per_chunk', 0), 3),
            'Peak_Memory_MB': round(metrics.get('peak_memory_mb', 0), 1),
            'Duplicates_Found': metrics.get('duplicates_found', 'N/A'),
            'Success_Rate_%': 100 if metrics.get('duplicates_found', 0) == 0 else 0,
            'Timestamp': metrics.get('timestamp', 'N/A')
        }

        matrix_data.append(ingestion_performance)

    # Mostrar matriz en consola
    print(f"\n📈 MATRIZ DE INGESTIÓN COMPARATIVA")
    print("="*120)

    # Header
    header = [
        "Embedder",
        "Dim",
        "Model_Load",
        "Embed_Time",
        "Ingest_Time",
        "Mem_MB",
        "Duplicates",
        "Success_%"
    ]
    print(f"{header[0]:<20} {header[1]:<6} {header[2]:<12} {header[3]:<12} {header[4]:<12} {header[5]:<8} {header[6]:<10} {header[7]:<9}")
    print("-"*120)

    # Data rows
    for row in matrix_data:
        print(f"{row['Embedder']:<20} {row['Dimension']:<6} {row['Model_Load_Time_s']:<12} "
              f"{row['Embedding_Time_s']:<12} {row['Ingestion_Time_s']:<12} "
              f"{row['Model_Memory_MB']:<8} {row['Duplicates_Found']:<10} {row['Success_Rate_%']:<9}")

    print("="*120)

    # Análisis comparativo
    print(f"\n🔍 ANÁLISIS COMPARATIVO")

    # Tiempos
    fastest_model = min(matrix_data, key=lambda x: x['Embedding_Per_Chunk_s'])
    slowest_model = max(matrix_data, key=lambda x: x['Embedding_Per_Chunk_s'])

    print(f"⚡ Embedding más rápido: {fastest_model['Embedder']} "
          f"({fastest_model['Embedding_Per_Chunk_s']}s por chunk)")
    print(f"🐌 Embedding más lento: {slowest_model['Embedder']} "
          f"({slowest_model['Embedding_Per_Chunk_s']}s por chunk)")

    # Memoria
    lightest_model = min(matrix_data, key=lambda x: x['Model_Memory_MB'])
    heaviest_model = max(matrix_data, key=lambda x: x['Model_Memory_MB'])

    print(f"💾 Modelo más ligero: {lightest_model['Embedder']} "
          f"({lightest_model['Model_Memory_MB']} MB)")
    print(f"🏋️ Modelo más pesado: {heaviest_model['Embedder']} "
          f"({heaviest_model['Model_Memory_MB']} MB)")

    # Duplicados (problema que queremos resolver)
    successful_models = [m for m in matrix_data if m['Success_Rate_%'] == 100]
    print(f"✅ Modelos sin duplicados: {len(successful_models)}/{len(matrix_data)}")
    for model in successful_models:
        print(f"   - {model['Embedder']}")

    # Calcular scores de rendimiento (ponderado)
    print(f"\n📊 PUNTUACIONES DE RENDIMIENTO")

    def calculate_performance_score(row):
        """Calcular score de rendimiento 0-100"""
        # Factores (menos es mejor para tiempos y memoria)
        time_score = max(0, 100 - (row['Embedding_Per_Chunk_s'] * 100))  # 0.01s = 99, 0.1s = 90
        memory_score = max(0, 100 - (row['Model_Memory_MB'] / 10))  # 100MB = 90, 500MB = 50
        success_score = row['Success_Rate_%']

        # Ponderación: 40% tiempo, 30% memoria, 30% éxito
        total_score = (time_score * 0.4) + (memory_score * 0.3) + (success_score * 0.3)
        return round(total_score, 1)

    for row in matrix_data:
        row['Performance_Score'] = calculate_performance_score(row)
        print(f"   {row['Embedder']}: {row['Performance_Score']}/100")

    # Recomendación basada en rendimiento puro
    best_performance = max(matrix_data, key=lambda x: x['Performance_Score'])
    print(f"\n🏆 Mejor rendimiento (tiempo + memoria + éxito): {best_performance['Embedder']}")

    # Guardar matriz completa
    matrix_complete = {
        'generated_at': datetime.now().isoformat(),
        'analysis': {
            'fastest_embedding': fastest_model['Embedder'],
            'slowest_embedding': slowest_model['Embedder'],
            'lightest_model': lightest_model['Embedder'],
            'heaviest_model': heaviest_model['Embedder'],
            'successful_models_count': len(successful_models),
            'best_performance': best_performance['Embedder']
        },
        'matrix_data': matrix_data,
        'raw_metrics': all_metrics
    }

    matrix_file = "second_brain/plan/results/ingestion_matrix.json"
    with open(matrix_file, 'w', encoding='utf-8') as f:
        json.dump(matrix_complete, f, indent=2)

    print(f"\n📄 Matriz completa guardada en: {matrix_file}")

    # Crear resumen para Fase 3
    summary = {
        'experiment_completed': True,
        'models_tested': len(matrix_data),
        'all_successful': len(successful_models) == len(matrix_data),
        'recommendations': {
            'proceed_to_phase_3': len(successful_models) >= 2,  # Al menos 2 modelos funcionan
            'best_performance': best_performance['Embedder'],
            'consider_language': any('multilingual' in m['Embedder'].lower() for m in matrix_data),
            'memory_constraints': heaviest_model['Model_Memory_MB'] > 500
        }
    }

    summary_file = "second_brain/plan/results/fase_2_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"📄 Resumen para Fase 3 guardado en: {summary_file}")

    return matrix_complete

if __name__ == "__main__":
    create_ingestion_matrix()
```

#### Comandos:
```bash
# 6.1 Crear script de matriz
# (Crear el archivo create_ingestion_matrix.py con el contenido de arriba)

# 6.2 Ejecutar análisis de matriz
python create_ingestion_matrix.py
# Esperado: 📊 Matriz comparativa con análisis completo
```

### ✅ Paso 7: Validación Final y Preparación Fase 3 (15 minutos)

#### Checklist:
- [ ] Verificar que los 3 embedders completaron exitosamente
- [ ] Confirmar que la matriz de ingestión está creada
- [ ] Validar que no hay duplicados en ningún caso
- [ ] Preparar resumen para Fase 3
- [ ] Documentar aprendizajes

#### Comandos:
```bash
# 7.1 Validar archivos de métricas
echo "🔍 Validando archivos de métricas..."
ls -la second_brain/plan/logs/fase_*_metrics.json
# Esperado: 3 archivos (fase_1, fase_2a_mpnet, fase_2b_multilingual)

# 7.2 Validar matriz de ingestión
echo "📊 Validando matriz de ingestión..."
if [ -f "second_brain/plan/results/ingestion_matrix.json" ]; then
    echo "✅ Matriz creada exitosamente"
    python -c "
    import json
    with open('second_brain/plan/results/ingestion_matrix.json', 'r') as f:
        matrix = json.load(f)
    print(f'📈 Modelos analizados: {len(matrix[\"matrix_data\"])}')
    best = matrix['analysis']['best_performance']
    print(f'🏆 Mejor rendimiento: {best}')
    "
else
    echo "❌ Matriz no encontrada"
fi

# 7.3 Validar estado final de PostgreSQL
echo "🔍 Validando estado final de PostgreSQL..."
psql -d rag_experiments -c "
SELECT
    COUNT(*) as total_docs,
    COUNT(DISTINCT embedding_model) as models,
    COUNT(DISTINCT source_hash) as unique_hashes
FROM documents;
"

# 7.4 Resumen preparación Fase 3
echo "📋 Preparación para Fase 3..."
python -c "
import json
with open('second_brain/plan/results/fase_2_summary.json', 'r') as f:
    summary = json.load(f)

print('🎯 Estado Fase 2:')
print(f'   ✅ Experimento completado: {summary[\"experiment_completed\"]}')
print(f'   ✅ Modelos probados: {summary[\"models_tested\"]}')
print(f'   ✅ Todos exitosos: {summary[\"all_successful\"]}')
print(f'   ✅ Recomendar Fase 3: {summary[\"recommendations\"][\"proceed_to_phase_3\"]}')
print(f'   🏆 Mejor rendimiento: {summary[\"recommendations\"][\"best_performance\"]}')
"
```

## Criterios de Éxito de Fase 2

### ✅ Éxito si:
- Los 3 embedders se probaron exitosamente
- Matriz de ingestión creada con métricas comparativas
- 0 duplicados en al menos 2 de los 3 embedders
- Tiempos de ingestión medidos y comparados
- Uso de memoria medido y documentado
- Recomendaciones claras para Fase 3

### ❌ Fracaso si:
- Menos de 2 embedders completan exitosamente
- Todos los embedders generan duplicados
- Tiempos de ingestión no se pueden medir
- Matriz comparativa no se puede crear
- Errores críticos sin resolución

## Entregables de Fase 2

1. **Métricas de MPNet** (768 dimensiones) - `fase_2a_mpnet_metrics.json`
2. **Métricas de Multilingüe** (384 dimensiones) - `fase_2b_multilingual_metrics.json`
3. **Matriz de ingestión comparativa** - `ingestion_matrix.json`
4. **Resumen y recomendaciones** - `fase_2_summary.json`
5. **Análisis de rendimiento** con scores ponderados
6. **Validación de cache invalidation** exitosa

## Aprendizajes Clave Esperados

1. **Impacto de dimensión**: 384 vs 768 en rendimiento y memoria
2. **Cache invalidation**: Importancia crítica al cambiar modelos
3. **Rendimiento relativo**: Cuál embedder es más eficiente
4. **Soporte multilingüe**: Beneficios para contenido en español
5. **Patrones de duplicación**: Si el problema es del modelo o del sistema

## Preparación para Fase 3

Al completar Fase 2 exitosamente, tendrás:
- **3 embedders probados** con el mismo dataset
- **Métricas objetivas** de rendimiento y recursos
- **Matriz comparativa** para toma de decisiones
- **Base de datos PostgreSQL** funcionando con el mejor modelo
- **Pipeline validado** para experimentos controlados

**Siguiente paso:** Proceder a `Fase_3_Validacion_Decision.md` para comparar calidad de búsqueda y tomar decisión final.