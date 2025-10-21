# Fase 3: Validación Comparativa y Decisión Final

## Objetivo del Día

Ejecutar queries de prueba para cada embedder, comparar calidad de retrieval y tomar decisión final sobre el embedder a utilizar.

**Duración estimada:** 4-5 horas
**Resultado esperado:** Matriz de decisión completa con embedder final seleccionado y justificación objetiva.

## Checklist Completo

### ✅ Paso 1: Preparación y Configuración (30 minutos)

#### Checklist:
- [ ] Validar que Fase 2 completó exitosamente
- [ ] Cargar matriz de ingestión de Fase 2
- [ ] Seleccionar embedder con mejor rendimiento de Fase 2
- [ ] Configurar base de datos con el embedder seleccionado
- [ ] Preparar 5 queries de referencia

#### Comandos:
```bash
# 1.1 Validar que Fase 2 completó
if [ ! -f "second_brain/plan/results/fase_2_summary.json" ]; then
    echo "❌ Fase 2 no completó. Ejecutar Fase 2 primero."
    exit 1
fi

# 1.2 Analizar resultados de Fase 2
echo "📊 Analizando resultados de Fase 2..."
python -c "
import json
with open('second_brain/plan/results/ingestion_matrix.json', 'r') as f:
    matrix = json.load(f)

print('🏆 Embedders por rendimiento:')
for row in sorted(matrix['matrix_data'], key=lambda x: x['Performance_Score'], reverse=True):
    print(f'   {row[\"Performance_Score\"]:>3}/100 {row[\"Embedder\"]}')

best = max(matrix['matrix_data'], key=lambda x: x['Performance_Score'])
print(f'\\n🎯 Mejor performer: {best[\"Embedder\"]} ({best[\"Performance_Score\"]}/100)')
print(f'   Modelo: {best[\"Model\"]}')
print(f'   Dimensión: {best[\"Dimension\"]}')
"

# 1.3 Configurar variables para el mejor embedder
echo "⚙️ Configurando para el mejor embedder de Fase 2..."
python -c "
import json
with open('second_brain/plan/results/ingestion_matrix.json', 'r') as f:
    matrix = json.load(f)

best = max(matrix['matrix_data'], key=lambda x: x['Performance_Score'])

# Crear configuración para el mejor embedder
config = f'''# PostgreSQL Configuration
DATABASE_BACKEND=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_experiments
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password

# Embedding Configuration - Fase 3 (Best Performer)
EMBEDDING_MODEL={best['Model']}
EMBEDDING_DIM={best['Dimension']}

# Experiment Configuration
EXPERIMENT_MODE=true
SAVE_RAW_OUTPUTS=true
LOG_LEVEL=DEBUG
PHASE=fase_3
BEST_PERFORMER={best['Embedder']}
'''

with open('.env.fase3', 'w') as f:
    f.write(config)

print(f'✅ Configuración creada para: {best[\"Embedder\"]}')
print(f'   Modelo: {best[\"Model\"]}')
print(f'   Dimensión: {best[\"Dimension\"]}')
"

# 1.4 Usar configuración de Fase 3
export $(cat .env.fase3 | xargs)
echo "✅ Variables configuradas:"
echo "   EMBEDDING_MODEL: $EMBEDDING_MODEL"
echo "   EMBEDDING_DIM: $EMBEDDING_DIM"
echo "   BEST_PERFORMER: $BEST_PERFORMER"
```

### ✅ Paso 2: Definir Queries de Referencia (30 minutos)

#### Checklist:
- [ ] Crear archivo con 5 queries estandarizadas
- [ ] Definir expected results para cada query
- [ ] Validar que los conceptos existen en el dataset
- [ ] Preparar sistema de evaluación
- [ ] Crear plantilla para guardar resultados

#### Archivo: `queries_referencia.py`
```python
#!/usr/bin/env python3
"""
Queries de referencia para validación de retrieval
"""

QUERIES_REFERENCIA = [
    {
        "id": 1,
        "query": "¿Qué es Docker y cómo funciona?",
        "category": "tecnologia_definicion",
        "expected_concepts": ["docker", "contenedores", "virtualización"],
        "expected_min_chunks": 1,
        "expected_max_chunks": 5,
        "language": "español",
        "difficulty": "básico"
    },
    {
        "id": 2,
        "query": "¿Cómo se instala PostgreSQL?",
        "category": "proceso_instalacion",
        "expected_concepts": ["postgresql", "instalación", "base de datos"],
        "expected_min_chunks": 1,
        "expected_max_chunks": 4,
        "language": "español",
        "difficulty": "básico"
    },
    {
        "id": 3,
        "query": "¿Qué son los embeddings?",
        "category": "concepto_tecnico",
        "expected_concepts": ["embeddings", "vectores", "representación"],
        "expected_min_chunks": 1,
        "expected_max_chunks": 5,
        "language": "español",
        "difficulty": "intermedio"
    },
    {
        "id": 4,
        "query": "¿Para qué sirve el chunking?",
        "category": "aplicacion_practica",
        "expected_concepts": ["chunking", "trozos", "procesamiento"],
        "expected_min_chunks": 1,
        "expected_max_chunks": 4,
        "language": "español",
        "difficulty": "intermedio"
    },
    {
        "id": 5,
        "query": "Sistemas de bases de datos",
        "category": "tema_general",
        "expected_concepts": ["base de datos", "sistemas", "almacenamiento"],
        "expected_min_chunks": 2,
        "expected_max_chunks": 6,
        "language": "español",
        "difficulty": "variable"
    }
]

def save_queries():
    """Guardar queries en archivo JSON"""
    import json
    with open("second_brain/plan/queries_referencia.json", "w", encoding="utf-8") as f:
        json.dump(QUERIES_REFERENCIA, f, indent=2, ensure_ascii=False)
    print("✅ Queries de referencia guardadas")

def load_queries():
    """Cargar queries desde archivo"""
    import json
    with open("second_brain/plan/queries_referencia.json", "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    save_queries()
    print(f"\n📋 Queries de referencia preparadas:")
    for query in QUERIES_REFERENCIA:
        print(f"   {query['id']}. {query['query']}")
        print(f"      Categoría: {query['category']}")
        print(f"      Conceptos esperados: {', '.join(query['expected_concepts'])}")
```

#### Comandos:
```bash
# 2.1 Crear y guardar queries
python queries_referencia.py
# Esperado: ✅ Queries de referencia guardadas

# 2.2 Validar que las queries están listas
cat second_brain/plan/queries_referencia.json | python -m json.tool | head -20
```

### ✅ Paso 3: Ejecutar Queries con Cada Embedder (90 minutos)

#### Checklist:
- [ ] Para cada embedder (MiniLM, MPNet, Multilingüe):
  - [ ] Cargar modelo y configurar BD
  - [ ] Ejecutar las 5 queries
  - [ ] Guardar resultados crudos
  - [ ] Medir tiempos de respuesta
  - [ ] Evaluar relevancia subjetiva

#### Archivo: `execute_validation.py`
```python
#!/usr/bin/env python3
"""
Ejecutar validación de queries para todos los embedders
"""
import os
import json
import time
import psutil
from sentence_transformers import SentenceTransformer
import numpy as np

from postgresql_database_experimental import PostgreSQLVectorDatabase
from queries_referencia import load_queries

def clear_model_cache():
    """Limpiar cache de modelos"""
    import torch
    import gc
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def configure_for_embedder(embedder_name):
    """Configurar variables de entorno para un embedder específico"""
    embedder_configs = {
        'MiniLM (Control)': {
            'model': 'all-MiniLM-L6-v2',
            'dim': 384,
            'phase': 'fase_3_minilm'
        },
        'MPNet (Alta Calidad)': {
            'model': 'all-mpnet-base-v2',
            'dim': 768,
            'phase': 'fase_3_mpnet'
        },
        'Multilingual (Español)': {
            'model': 'paraphrase-multilingual-MiniLM-L12-v2',
            'dim': 384,
            'phase': 'fase_3_multilingual'
        }
    }

    config = embedder_configs.get(embedder_name)
    if not config:
        raise ValueError(f"Embedder no reconocido: {embedder_name}")

    # Configurar variables de entorno
    os.environ['EMBEDDING_MODEL'] = config['model']
    os.environ['EMBEDDING_DIM'] = str(config['dim'])
    os.environ['PHASE'] = config['phase']

    return config

def setup_database_for_embedder(embedder_name, config):
    """Configurar base de datos para un embedder específico"""
    print(f"🔌 Configurando BD para: {embedder_name}")

    # Limpiar tablas existentes
    from postgresql_database_experimental import PostgreSQLVectorDatabase
    temp_db = PostgreSQLVectorDatabase()

    with temp_db.pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS document_embeddings CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS documents CASCADE;")

    # Recrear schema con dimensión correcta
    os.system(f"EMBEDDING_DIM={config['dim']} python setup_schema.py")

    # Cargar datos para este embedder desde logs de Fase 2
    phase_files = {
        'MiniLM (Control)': 'fase_1_metrics.json',
        'MPNet (Alta Calidad)': 'fase_2a_mpnet_metrics.json',
        'Multilingual (Español)': 'fase_2b_multilingual_metrics.json'
    }

    phase_file = phase_files.get(embedder_name)
    if not phase_file:
        raise ValueError(f"No se encontraron datos para {embedder_name}")

    # Cargar dataset original
    with open("second_brain/plan/experimental_dataset.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Cargar modelo
    print(f"🤖 Cargando modelo: {config['model']}")
    model = SentenceTransformer(config['model'])

    # Preparar documentos
    documents = []
    for i, chunk_data in enumerate(dataset):
        content = chunk_data['content']
        metadata = {
            'source_document': chunk_data['source_document'],
            'source_hash': chunk_data['source_hash'],
            'chunking_strategy': 'experimental',
            'chunk_index': chunk_data['chunk_index'],
            'semantic_title': f"{embedder_name} chunk {i+1}",
            'semantic_summary': content[:100] + "..." if len(content) > 100 else content,
            'additional_metadata': {
                'phase': config['phase'],
                'model': config['model'],
                'dimension': config['dim'],
                'validation_phase': True
            }
        }
        documents.append((content, None, metadata))

    # Generar embeddings
    print(f"🧮 Generando embeddings para {len(documents)} chunks...")
    texts = [doc[0] for doc in documents]
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Insertar en BD
    documents_with_embeddings = []
    for (content, _, metadata), embedding in zip(documents, embeddings):
        documents_with_embeddings.append((content, embedding.tolist(), metadata))

    db = PostgreSQLVectorDatabase()
    db.add_documents_with_metadata(documents_with_embeddings)

    stats = db.get_stats()
    print(f"✅ BD configurada: {stats}")

    return db, model

def evaluate_relevance(query_text, results, expected_concepts):
    """Evaluar relevancia subjetiva de los resultados"""
    if not results:
        return 0, "No results"

    score = 0
    feedback = []

    # Verificar si los resultados contienen conceptos esperados
    concept_matches = 0
    for content, similarity in results[:3]:  # Evaluar top 3
        content_lower = content.lower()
        found_concepts = [concept for concept in expected_concepts if concept.lower() in content_lower]
        if found_concepts:
            concept_matches += len(found_concepts)
            score += 2  # 2 puntos por concepto encontrado
            feedback.append(f"✅ Conceptos encontrados: {found_concepts}")

    # Bonus por similitud alta
    if results and results[0][1] > 0.7:
        score += 1
        feedback.append(f"✅ Alta similitud: {results[0][1]:.3f}")

    # Penalizar si no hay conceptos esperados
    if concept_matches == 0:
        score -= 2
        feedback.append("❌ No se encontraron conceptos esperados")

    # Normalizar score (0-5)
    score = max(0, min(5, score))

    return score, "; ".join(feedback)

def execute_validation_for_embedder(embedder_name):
    """Ejecutar validación completa para un embedder"""
    print(f"\n🚀 Iniciando validación para: {embedder_name}")
    print("="*60)

    start_time = time.time()

    # Configurar para este embedder
    config = configure_for_embedder(embedder_name)

    # Limpiar cache antes de cargar modelo
    clear_model_cache()

    # Configurar base de datos
    db, model = setup_database_for_embedder(embedder_name, config)

    # Cargar queries de referencia
    queries = load_queries()
    print(f"📋 Cargadas {len(queries)} queries de referencia")

    # Ejecutar queries
    results = {}
    total_query_time = 0

    for query_info in queries:
        query_id = query_info['id']
        query_text = query_info['query']

        print(f"\n🔍 Ejecutando query {query_id}: {query_text}")

        # Medir tiempo de query
        query_start = time.time()

        # Generar embedding de la query
        query_embedding = model.encode([query_text])[0].tolist()

        # Ejecutar búsqueda
        search_results = db.search_similar(query_embedding, top_k=5)

        query_time = time.time() - query_start
        total_query_time += query_time

        # Evaluar relevancia
        relevance_score, feedback = evaluate_relevance(
            query_text, search_results, query_info['expected_concepts']
        )

        # Guardar resultados
        results[f"query_{query_id}"] = {
            'query': query_text,
            'category': query_info['category'],
            'expected_concepts': query_info['expected_concepts'],
            'expected_range': (query_info['expected_min_chunks'], query_info['expected_max_chunks']),
            'results_count': len(search_results),
            'query_time_ms': int(query_time * 1000),
            'relevance_score': relevance_score,
            'relevance_feedback': feedback,
            'top_results': [
                {
                    'content': content[:200] + "...",
                    'similarity': float(similarity),
                    'length': len(content)
                }
                for content, similarity in search_results[:3]
            ]
        }

        print(f"   ⏱️ Tiempo: {query_time*1000:.0f}ms")
        print(f"   📊 Resultados: {len(search_results)} chunks")
        print(f"   🎯 Relevancia: {relevance_score}/5 - {feedback}")

    # Calcular métricas agregadas
    avg_relevance = np.mean([r['relevance_score'] for r in results.values()])
    avg_query_time = total_query_time / len(queries)
    total_time = time.time() - start_time

    validation_results = {
        'embedder': embedder_name,
        'model': config['model'],
        'dimension': config['dim'],
        'total_time_s': round(total_time, 2),
        'avg_query_time_ms': round(avg_query_time * 1000, 1),
        'avg_relevance_score': round(avg_relevance, 2),
        'total_queries': len(queries),
        'successful_queries': len([r for r in results.values() if r['relevance_score'] > 0]),
        'results': results,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Guardar resultados
    phase_name = config['phase']
    results_file = f"second_brain/plan/logs/{phase_name}_validation.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Resumen para {embedder_name}:")
    print(f"   Tiempo total: {total_time:.2f}s")
    print(f"   Tiempo promedio por query: {avg_query_time*1000:.1f}ms")
    print(f"   Relevancia promedio: {avg_relevance:.2f}/5")
    print(f"   Queries exitosas: {validation_results['successful_queries']}/{len(queries)}")
    print(f"   📄 Resultados guardados en: {results_file}")

    db.close()
    clear_model_cache()

    return validation_results

def run_all_validations():
    """Ejecutar validaciones para todos los embedders"""
    print("🎯 Iniciando validación completa para todos los embedders")
    print("="*80)

    embedders = [
        'MiniLM (Control)',
        'MPNet (Alta Calidad)',
        'Multilingual (Español)'
    ]

    all_results = {}

    for embedder in embedders:
        try:
            result = execute_validation_for_embedder(embedder)
            all_results[embedder] = result
            print(f"✅ Validación completada: {embedder}")
        except Exception as e:
            print(f"❌ Error en validación {embedder}: {e}")
            all_results[embedder] = {'error': str(e)}

    return all_results

if __name__ == "__main__":
    results = run_all_validations()
    print(f"\n🎉 Todas las validaciones completadas!")
```

#### Comandos:
```bash
# 3.1 Crear script de validación
# (Crear el archivo execute_validation.py con el contenido de arriba)

# 3.2 Ejecutar validación completa
python execute_validation.py
# Esperado: 🎯 Validación completada para los 3 embedders con métricas detalladas
```

### ✅ Paso 4: Crear Matriz de Decisión (60 minutos)

#### Checklist:
- [ ] Cargar resultados de los 3 embedders
- [ ] Calcular scores de decisión ponderados
- [ ] Crear matriz comparativa final
- [ ] Analizar trade-offs entre calidad y rendimiento
- [ ] Generar recomendación final

#### Archivo: `create_decision_matrix.py`
```python
#!/usr/bin/env python3
"""
Crear matriz de decisión final basada en resultados de validación
"""
import json
import os
import numpy as np
from datetime import datetime

def load_validation_results():
    """Cargar resultados de validación de todos los embedders"""
    results = {}

    validation_files = {
        'MiniLM (Control)': 'second_brain/plan/logs/fase_3_minilm_validation.json',
        'MPNet (Alta Calidad)': 'second_brain/plan/logs/fase_3_mpnet_validation.json',
        'Multilingual (Español)': 'second_brain/plan/logs/fase_3_multilingual_validation.json'
    }

    for embedder, file_path in validation_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                results[embedder] = json.load(f)
            print(f"✅ Cargado: {embedder}")
        else:
            print(f"❌ No encontrado: {file_path}")

    return results

def load_ingestion_metrics():
    """Cargar métricas de ingestión de Fase 2"""
    with open('second_brain/plan/results/ingestion_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)

    ingestion_metrics = {}
    for row in matrix['matrix_data']:
        ingestion_metrics[row['Embedder']] = row

    return ingestion_metrics

def calculate_decision_scores(validation_results, ingestion_metrics):
    """Calcular scores de decisión ponderados"""

    # Definir ponderaciones (total = 100%)
    weights = {
        'relevance': 0.35,      # 35% - Calidad de resultados
        'response_time': 0.25, # 25% - Velocidad de respuesta
        'resource_usage': 0.15, # 15% - Uso de memoria/CPU
        'spanish_support': 0.15, # 15% - Soporte para español
        'stability': 0.10       # 10% - Consistencia y errores
    }

    decision_matrix = []

    for embedder, validation_data in validation_results.items():
        if 'error' in validation_data:
            print(f"⚠️ Omitiendo {embedder} por errores")
            continue

        ingestion_data = ingestion_metrics.get(embedder, {})

        # Calcular scores normalizados (0-100)

        # 1. Relevancia (35%)
        relevance_score = validation_data.get('avg_relevance_score', 0) * 20  # 0-5 -> 0-100

        # 2. Tiempo de respuesta (25%) - menor es mejor
        avg_time_ms = validation_data.get('avg_query_time_ms', 1000)
        # Normalizar: 100ms = 100 puntos, 1000ms = 0 puntos
        time_score = max(0, 100 - (avg_time_ms - 100) * 100 / 900)

        # 3. Uso de recursos (15%) - menor es mejor
        memory_mb = ingestion_data.get('Model_Memory_MB', 100)
        # Normalizar: 100MB = 100 puntos, 1000MB = 0 puntos
        resource_score = max(0, 100 - (memory_mb - 100) * 100 / 900)

        # 4. Soporte español (15%)
        if 'multilingual' in embedder.lower():
            spanish_score = 100
        elif 'mpnet' in embedder.lower():
            spanish_score = 70  # Bueno pero no especializado
        else:
            spanish_score = 50  # Básico

        # 5. Estabilidad (10%) - queries exitosas
        successful_queries = validation_data.get('successful_queries', 0)
        total_queries = validation_data.get('total_queries', 5)
        stability_score = (successful_queries / total_queries) * 100

        # Calcular score total ponderado
        total_score = (
            relevance_score * weights['relevance'] +
            time_score * weights['response_time'] +
            resource_score * weights['resource_usage'] +
            spanish_score * weights['spanish_support'] +
            stability_score * weights['stability']
        )

        # Redondear a 1 decimal
        total_score = round(total_score, 1)

        decision_matrix.append({
            'Embedder': embedder,
            'Model': ingestion_data.get('Model', 'N/A'),
            'Dimension': ingestion_data.get('Dimension', 'N/A'),

            # Métricas individuales (normalizadas 0-100)
            'Relevance_Score': round(relevance_score, 1),
            'Response_Time_Score': round(time_score, 1),
            'Resource_Score': round(resource_score, 1),
            'Spanish_Support_Score': spanish_score,
            'Stability_Score': round(stability_score, 1),

            # Score total
            'Total_Score': total_score,

            # Métricas originales para referencia
            'Original_Relevance': round(validation_data.get('avg_relevance_score', 0), 2),
            'Original_Time_ms': round(avg_time_ms, 1),
            'Original_Memory_MB': round(memory_mb, 1),
            'Successful_Queries': f"{successful_queries}/{total_queries}",

            # Metadata
            'Weights': weights
        })

    return decision_matrix

def create_final_decision_matrix(decision_matrix):
    """Crear matriz de decisión final con análisis"""

    print("📊 CREANDO MATRIZ DE DECISIÓN FINAL")
    print("="*100)

    # Ordenar por score total
    decision_matrix.sort(key=lambda x: x['Total_Score'], reverse=True)

    # Mostrar matriz
    header = [
        "Embedder",
        "Relevance",
        "Time",
        "Resource",
        "Spanish",
        "Stability",
        "TOTAL"
    ]

    print(f"{header[0]:<25} {header[1]:<10} {header[2]:<8} {header[3]:<10} {header[4]:<10} {header[5]:<10} {header[6]:<8}")
    print("-"*100)

    for row in decision_matrix:
        print(f"{row['Embedder']:<25} {row['Relevance_Score']:<10} "
              f"{row['Response_Time_Score']:<8} {row['Resource_Score']:<10} "
              f"{row['Spanish_Support_Score']:<10} {row['Stability_Score']:<10} {row['Total_Score']:<8}")

    print("="*100)

    # Análisis detallado
    print(f"\n🔍 ANÁLISIS DETALLADO")

    winner = decision_matrix[0]
    print(f"🏆 GANADOR: {winner['Embedder']}")
    print(f"   Score Total: {winner['Total_Score']}/100")
    print(f"   Modelo: {winner['Model']}")
    print(f"   Dimensión: {winner['Dimension']}")

    print(f"\n📈 PUNTUACIONES DETALLADAS:")
    print(f"   Relevancia: {winner['Relevance_Score']}/100 "
          f"(original: {winner['Original_Relevance']}/5)")
    print(f"   Tiempo Respuesta: {winner['Response_Time_Score']}/100 "
          f"(original: {winner['Original_Time_ms']}ms)")
    print(f"   Uso Recursos: {winner['Resource_Score']}/100 "
          f"(original: {winner['Original_Memory_MB']}MB)")
    print(f"   Soporte Español: {winner['Spanish_Support_Score']}/100")
    print(f"   Estabilidad: {winner['Stability_Score']}/100 "
          f"(original: {winner['Successful_Queries']})")

    # Comparación con otros
    print(f"\n🔄 COMPARACIÓN CON ALTERNATIVAS:")
    for i, row in enumerate(decision_matrix[1:], 1):
        diff = row['Total_Score'] - winner['Total_Score']
        print(f"   {i}. {row['Embedder']}: {row['Total_Score']} "
              f"({diff:+.1f} vs ganador)")

    # Recomendaciones basadas en uso
    print(f"\n💡 RECOMENDACIONES POR CASO DE USO:")

    # Mejor relevancia
    best_relevance = max(decision_matrix, key=lambda x: x['Relevance_Score'])
    print(f"   🎯 Mejor Relevancia: {best_relevance['Embedder']} "
          f"({best_relevance['Relevance_Score']}/100)")

    # Más rápido
    fastest = max(decision_matrix, key=lambda x: x['Response_Time_Score'])
    print(f"   ⚡ Más Rápido: {fastest['Embedder']} "
          f"({fastest['Response_Time_Score']}/100)")

    # Mejor para español
    best_spanish = max(decision_matrix, key=lambda x: x['Spanish_Support_Score'])
    print(f"   🌍 Mejor para Español: {best_spanish['Embedder']} "
          f"({best_spanish['Spanish_Support_Score']}/100)")

    # Más ligero
    lightest = max(decision_matrix, key=lambda x: x['Resource_Score'])
    print(f"   💾 Más Ligero: {lightest['Embedder']} "
          f"({lightest['Resource_Score']}/100)")

    return decision_matrix

def generate_final_report(decision_matrix, validation_results, ingestion_metrics):
    """Generar reporte final completo"""

    winner = decision_matrix[0]

    report = {
        'experiment_completed': True,
        'generated_at': datetime.now().isoformat(),
        'final_decision': {
            'selected_embedder': winner['Embedder'],
            'model': winner['Model'],
            'dimension': winner['Dimension'],
            'total_score': winner['Total_Score'],
            'recommendation_strength': 'ALTA' if winner['Total_Score'] > 75 else 'MEDIA',
            'confidence': 'ALTO' if winner['Stability_Score'] > 80 else 'MEDIO'
        },
        'decision_matrix': decision_matrix,
        'weights_used': {
            'relevance': 0.35,
            'response_time': 0.25,
            'resource_usage': 0.15,
            'spanish_support': 0.15,
            'stability': 0.10
        },
        'validation_summary': validation_results,
        'ingestion_summary': ingestion_metrics,
        'next_steps': {
            'implement_selected_embedder': True,
            'proceed_to_refactor': winner['Total_Score'] > 70,
            'monitor_performance': True,
            'document_learnings': True
        }
    }

    # Guardar reporte final
    report_file = "second_brain/plan/results/final_decision_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Reporte final guardado en: {report_file}")

    # Crear resumen ejecutivo
    executive_summary = f"""
# 🎯 DECISIÓN FINAL - EMBEDDER SELECCIONADO

## Ganador: {winner['Embedder']}

### Configuración Recomendada:
- **Modelo:** {winner['Model']}
- **Dimensión:** {winner['Dimension']}
- **Score Total:** {winner['Total_Score']}/100
- **Confianza:** {report['final_decision']['confidence']}

### Métricas Clave:
- **Relevancia:** {winner['Original_Relevance']}/5 ⭐
- **Tiempo Respuesta:** {winner['Original_Time_ms']}ms ⚡
- **Memoria:** {winner['Original_Memory_MB']}MB 💾
- **Queries Exitosas:** {winner['Successful_Queries']} ✅

### Justificación:
Este embedder obtuvo el mejor balance entre calidad de resultados, rendimiento y uso de recursos según la ponderación definida.

### Recomendación:
Implementar este embedder como backend definitivo del sistema RAG.
"""

    summary_file = "second_brain/plan/results/executive_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(executive_summary)

    print(f"📄 Resumen ejecutivo guardado en: {summary_file}")

    return report

def main():
    """Función principal de creación de matriz de decisión"""
    print("🚀 Iniciando creación de matriz de decisión final...")

    # Cargar resultados
    validation_results = load_validation_results()
    ingestion_metrics = load_ingestion_metrics()

    if len(validation_results) < 2:
        print("❌ Se necesitan resultados de al menos 2 embedders para comparar")
        return

    # Calcular matriz de decisión
    decision_matrix = calculate_decision_scores(validation_results, ingestion_metrics)

    # Crear matriz final
    final_matrix = create_final_decision_matrix(decision_matrix)

    # Generar reporte final
    final_report = generate_final_report(final_matrix, validation_results, ingestion_metrics)

    print(f"\n🎉 Matriz de decisión completada exitosamente!")

    return final_report

if __name__ == "__main__":
    main()
```

#### Comandos:
```bash
# 4.1 Crear script de decisión
# (Crear el archivo create_decision_matrix.py con el contenido de arriba)

# 4.2 Ejecutar análisis de decisión
python create_decision_matrix.py
# Esperado: 📊 Matriz de decisión final con embedder ganador
```

### ✅ Paso 5: Validación y Documentación (30 minutos)

#### Checklist:
- [ ] Verificar que la matriz de decisión se creó
- [ ] Validar que hay un ganador claro
- [ ] Revisar que todos los archivos están guardados
- [ ] Crear documentación final
- [ ] Preparar recomendaciones para Fase 4

#### Comandos:
```bash
# 5.1 Validar archivos finales
echo "🔍 Validando archivos finales del experimento..."
echo "Métricas de ingestión:"
ls -la second_brain/plan/results/ingestion_matrix.json

echo -e "\nMétricas de validación:"
ls -la second_brain/plan/logs/fase_*_validation.json

echo -e "\nDecisión final:"
ls -la second_brain/plan/results/final_decision_report.json

# 5.2 Validar que hay un ganador claro
echo -e "\n🏆 Validando ganador..."
python -c "
import json
with open('second_brain/plan/results/final_decision_report.json', 'r') as f:
    report = json.load(f)

winner = report['final_decision']['selected_embedder']
score = report['final_decision']['total_score']
confidence = report['final_decision']['confidence']

print(f'✅ Ganador: {winner}')
print(f'✅ Score: {score}/100')
print(f'✅ Confianza: {confidence}')

if score > 75:
    print('🎯 DECISIÓN CLARA: Ganador con score alto')
elif score > 60:
    print('⚖️ DECISIÓN MODERADA: Ganador con score medio')
else:
    print('❓ DECISIÓN DUDOSA: Ningún embedder claramente superior')
"

# 5.3 Resumen de todo el experimento
echo -e "\n📊 RESUMEN COMPLETO DEL EXPERIMENTO"
python -c "
import json
import os

# Contar archivos generados
logs = len([f for f in os.listdir('second_brain/plan/logs') if f.endswith('.json')])
results = len([f for f in os.listdir('second_brain/plan/results') if f.endswith('.json')])

print(f'📁 Archivos de logs generados: {logs}')
print(f'📁 Archivos de resultados: {results}')

# Cargar decisión final
with open('second_brain/plan/results/final_decision_report.json', 'r') as f:
    final = json.load(f)

print(f'\\n🎯 ESTADO FINAL:')
print(f'   ✅ Experimento completado: {final[\"experiment_completed\"]}')
print(f'   ✅ Embedder seleccionado: {final[\"final_decision\"][\"selected_embedder\"]}')
print(f'   ✅ Proceder a refactor: {final[\"next_steps\"][\"proceed_to_refactor\"]}')
"

# 5.4 Crear resumen para documentación
cat > second_brain/plan/EXPERIMENTO_COMPLETO.md << EOF
# 🎯 Experimento RAG PostgreSQL - Resumen Completo

## Objetivo Alcanzado
✅ Evaluar 3 embedders diferentes para seleccionar el mejor para el sistema RAG

## Embedders Probados
1. **all-MiniLM-L6-v2** (Control - 384 dimensiones)
2. **all-mpnet-base-v2** (Alta calidad - 768 dimensiones)
3. **paraphrase-multilingual-MiniLM-L12-v2** (Multilingüe - 384 dimensiones)

## Métricas Evaluadas
- **Calidad de retrieval** (relevancia de resultados)
- **Tiempo de respuesta** (latencia)
- **Uso de recursos** (memoria/CPU)
- **Soporte para español** (cobertura lingüística)
- **Estabilidad** (consistencia de resultados)

## Dataset
- **15 chunks** seleccionados de transcripts_for_rag
- **5 queries** de referencia estandarizadas
- **Evaluación subjetiva** 0-5 puntos por query

## Decision Key
Ponderación: Relevancia(35%) + Tiempo(25%) + Recursos(15%) + Español(15%) + Estabilidad(10%)

## Resultados
Consultar el archivo \`final_decision_report.json\` para detalles completos.

## Próximos Pasos
1. Implementar embedder ganador en producción
2. Refactorizar sistema RAG actual
3. Monitorear rendimiento en producción
4. Documentar aprendizajes

---

*Experimento completado en $(date)*
EOF

echo "📄 Resumen del experimento guardado en: second_brain/plan/EXPERIMENTO_COMPLETO.md"
```

## Criterios de Éxito de Fase 3

### ✅ Éxito si:
- Las 5 queries se ejecutan para cada embedder
- Matriz de decisión creada con scores ponderados
- Hay un ganador claro con score > 60/100
- Métricas de calidad y rendimiento documentadas
- Recomendación final justificada
- Todos los archivos de resultados guardados

### ❌ Fracaso si:
- Menos de 2 embedders completan validación
- No hay un ganador claro (scores muy similares)
- Las métricas de calidad no son fiables
- Errores en las queries de prueba
- No se puede tomar decisión informada

## Entregables de Fase 3

1. **Resultados de validación** por embedder - `fase_*_validation.json`
2. **Matriz de decisión** con scores ponderados - `final_decision_report.json`
3. **Resumen ejecutivo** con recomendación - `executive_summary.md`
4. **Análisis comparativo** detallado - incluido en reporte final
5. **Documentación completa** del experimento - `EXPERIMENTO_COMPLETO.md`

## Decisión Final Esperada

Basado en el análisis, el embedder seleccionado debería tener:

### Score > 75/100 (Decisión Clara)
- **Mejor balance** entre calidad y rendimiento
- **Relevancia** > 3.0/5 en promedio
- **Tiempo respuesta** < 500ms promedio
- **Estabilidad** > 80% (queries exitosas)

### Score 60-75/100 (Decisión Moderada)
- **Trade-offs identificados** claramente
- **Ventajas específicas** para ciertos casos de uso
- **Recomendaciones condicionales** según prioridades

### Score < 60/100 (Decisión Dudosa)
- **Ningún embedder claramente superior**
- **Problemas fundamentales** en retrieval
- **Necesita más investigación** o ajustes

## Preparación para Fase 4 (Opcional)

Al completar Fase 3 exitosamente, tendrás:
- **Embedder ganador** seleccionado objetivamente
- **Configuración óptima** definida y probada
- **Métricas baseline** para comparación futura
- **Confianza** en la decisión técnica
- **Roadmap claro** para implementación

**Siguiente paso:** Si se decide proceder, implementar `PostgreSQLVectorDatabase` definitiva con el embedder ganador y refactorizar el sistema actual.

## Impacto del Experimento

Este experimento proporciona:
1. **Base objetiva** para decisiones técnicas
2. **Experiencia práctica** con diferentes embedders
3. **Métricas reales** de rendimiento y calidad
4. **Proceso reproducible** para futuras evaluaciones
5. **Confianza** en la arquitectura seleccionada

El conocimiento adquirido es directamente aplicable al proyecto RAG del ERP en tu trabajo.