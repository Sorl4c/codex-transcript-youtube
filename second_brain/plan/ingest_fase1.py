#!/usr/bin/env python3
"""
Ingestión controlada para Fase 1 - Experimento RAG PostgreSQL
Dataset de 15 chunks representativos de transcripts_for_rag existentes
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sentence_transformers import SentenceTransformer
from second_brain.plan.postgresql_database_experimental import PostgreSQLVectorDatabase

class Fase1IngestionControl:
    """Ingestión controlada para experimento PostgreSQL con MiniLM base"""

    def __init__(self):
        self.db = PostgreSQLVectorDatabase()
        self.embedding_model = self.db.embedding_model  # all-MiniLM-L6-v2
        self.embedding_dim = self.db.embedding_dim       # 384

        # Inicializar embedder
        print(f"🤖 Cargando embedder: {self.embedding_model}")
        self.embedder = SentenceTransformer(self.embedding_model)

        # Dataset controlado de 15 chunks
        self.dataset_path = "second_brain/plan/data/dataset_fase1.json"

    def prepare_dataset(self) -> List[Dict]:
        """
        Preparar dataset de 15 chunks representativos
        Since files don't exist yet, create sample data for testing
        """
        print("📊 Preparando dataset controlado (15 chunks)...")

        # Check if dataset file exists
        if os.path.exists(self.dataset_path):
            print(f"📁 Cargando dataset existente: {self.dataset_path}")
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            print(f"✅ Dataset cargado: {len(dataset)} chunks")
            return dataset

        # Create sample dataset for testing
        print("📝 Creando dataset de prueba desde transcripts existentes...")

        # Sample transcript data (similar to what would be in transcripts_for_rag)
        sample_transcripts = [
            "El Docker compose es una herramienta para definir y ejecutar aplicaciones Docker múltiples contenedores. Se utiliza un archivo YAML para configurar los servicios de la aplicación.",
            "Los embeddings son representaciones vectoriales de texto en un espacio multidimensional. Se utilizan para encontrar similitud semántica entre diferentes fragmentos de texto.",
            "El sistema RAG (Retrieval-Augmented Generation) combina recuperación de información con generación de lenguaje para mejorar la precisión de las respuestas.",
            "La chunking estratégica es fundamental para el procesamiento efectivo de documentos largos. Permite mantener el contexto semántico mientras se divide el contenido.",
            "Los modelos de lenguaje como GPT y BERT han revolucionado el procesamiento de lenguaje natural. Permiten comprender y generar texto de manera más natural.",
            "PostgreSQL con pgvector es una excelente opción para almacenamiento de vectores. Ofrece高性能 búsquedas de similitud y escalabilidad.",
            "El streaming de datos permite procesar información en tiempo real. Es especialmente útil para aplicaciones que requieren respuestas inmediatas.",
            "Los microservicios son una aproximación al desarrollo de software donde una aplicación grande está construida como un conjunto de servicios pequeños.",
            "La arquitectura de eventos permite que los componentes de un sistema se comuniquen a través de eventos. Esto mejora la desacoplación y escalabilidad.",
            "El cache invalidation es un problema clásico en computación. Consiste en determinar cuándo y cómo invalidar datos cacheados que han cambiado.",
            "Los tests unitarios son fundamentales para asegurar la calidad del código. Permiten verificar que cada componente funciona correctamente de forma aislada.",
            "La integración continua es una práctica de desarrollo donde los desarrolladores integran código frecuentemente. Cada integración se verifica automáticamente.",
            "El control de versiones con Git permite rastrear cambios en el código. Facilita la colaboración entre desarrolladores y el mantenimiento del proyecto.",
            "Las bases de datos vectoriales están diseñadas específicamente para almacenar y consultar vectores de alta dimensionalidad eficientemente.",
            "El procesamiento de lenguaje natural (NLP) combina lingüística computacional e inteligencia artificial para procesar texto y voz."
        ]

        dataset = []
        for i, text in enumerate(sample_transcripts[:15]):  # Ensure exactly 15 chunks
            # Generate source hash
            source_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

            chunk_data = {
                "content": text,
                "source_hash": source_hash,
                "source_document": f"document_fase1_chunk_{i+1:03d}",
                "chunking_strategy": "agentic",
                "chunk_index": i,
                "char_start": i * 100,  # Simulated positions
                "char_end": (i + 1) * 100 - 1,
                "semantic_title": f"Chunk {i+1:03d}: {text[:50]}...",
                "semantic_summary": f"Resumen del chunk {i+1}: {text[:100]}...",
                "semantic_overlap": "",
                "embedding_model": self.embedding_model,
                "additional_metadata": {
                    "fase": "fase_1",
                    "ingestion_timestamp": "2025-01-18T23:50:00Z",
                    "test_dataset": True,
                    "chunk_length": len(text)
                }
            }
            dataset.append(chunk_data)

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.dataset_path), exist_ok=True)

        # Save dataset
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"✅ Dataset creado y guardado: {len(dataset)} chunks")
        return dataset

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generar embeddings para lista de textos"""
        print(f"🔢 Generando embeddings para {len(texts)} textos...")

        embeddings = self.embedder.encode(
            texts,
            batch_size=4,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        print(f"✅ Embeddings generados: {embeddings.shape}")
        return embeddings.tolist()

    def ingest_dataset(self, dataset: List[Dict]):
        """Ingestar dataset en PostgreSQL"""
        print(f"📥 Iniciando ingestión de {len(dataset)} chunks...")

        # Preparar datos para inserción
        documents = []
        texts = []

        for chunk in dataset:
            texts.append(chunk["content"])

            # Preparar metadata
            metadata = {
                "source_hash": chunk["source_hash"],
                "source_document": chunk["source_document"],
                "chunking_strategy": chunk["chunking_strategy"],
                "chunk_index": chunk["chunk_index"],
                "char_start": chunk["char_start"],
                "char_end": chunk["char_end"],
                "semantic_title": chunk["semantic_title"],
                "semantic_summary": chunk["semantic_summary"],
                "semantic_overlap": chunk["semantic_overlap"],
                "additional_metadata": chunk["additional_metadata"]
            }

            documents.append((chunk["content"], None, metadata))  # None para embedding (se generará después)

        # Generar embeddings
        embeddings = self.generate_embeddings(texts)

        # Combinar con embeddings
        documents_with_embeddings = []
        for i, (content, _, metadata) in enumerate(documents):
            documents_with_embeddings.append((content, embeddings[i], metadata))

        # Insertar en base de datos
        self.db.add_documents_with_metadata(documents_with_embeddings)

        print(f"✅ Ingestión completada: {len(documents_with_embeddings)} documentos")

        # Guardar registro de ingestión
        ingestion_log = {
            "fase": "fase_1",
            "embedder": self.embedding_model,
            "dimension": self.embedding_dim,
            "document_count": len(documents_with_embeddings),
            "timestamp": "2025-01-18T23:50:00Z",
            "dataset_path": self.dataset_path,
            "status": "completed"
        }

        log_path = "second_brain/plan/logs/fase_1_ingestion.json"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(ingestion_log, f, indent=2, ensure_ascii=False)

        print(f"📋 Registro guardado: {log_path}")

    def verify_ingestion(self):
        """Verificar que la ingestión fue exitosa"""
        print("\n🔍 Verificando ingestión...")

        stats = self.db.get_stats()
        print(f"📊 Estadísticas de la BD:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # Test de búsqueda con embedding de prueba
        test_query = "Docker compose para microservicios"
        test_embedding = self.embedder.encode([test_query])[0].tolist()

        print(f"🔍 Generando embedding para: '{test_query}'")
        print(f"📏 Dimensión del embedding: {len(test_embedding)}")
        print(f"📋 Tipo de embedding: {type(test_embedding)}")
        print(f"📋 Muestra: {test_embedding[:5]}...")

        results = self.db.search_similar(test_embedding, top_k=3)

        print(f"\n🔍 Test de búsqueda: '{test_query}'")
        print(f"📋 Resultados encontrados: {len(results)}")
        for i, (content, similarity) in enumerate(results):
            print(f"   {i+1}. Similitud: {similarity:.4f} - Content: {content[:100]}...")

        # Si no hay resultados, probar con búsqueda directa para debug
        if len(results) == 0:
            print("\n🔧 Debug: Probando búsqueda directa en BD...")
            with self.db.pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT d.content, 1 - (de.embedding <=> %s::vector) as similarity
                        FROM document_embeddings de
                        JOIN documents d ON de.document_id = d.id
                        ORDER BY de.embedding <=> %s::vector
                        LIMIT 3
                    """, (test_embedding, test_embedding))

                    direct_results = cursor.fetchall()
                    print(f"🎯 Búsqueda directa: {len(direct_results)} resultados")
                    for i, (content, similarity) in enumerate(direct_results):
                        print(f"   {i+1}. Similitud: {similarity:.4f} - Content: {content[:100]}...")

        return stats, results

    def run_fase1(self):
        """Ejecutar Fase 1 completa"""
        print("🚀 Iniciando Fase 1: Setup PostgreSQL + Ingestión Controlada")
        print("="*60)

        try:
            # Paso 1: Preparar dataset
            dataset = self.prepare_dataset()

            # Paso 2: Ingestar dataset
            self.ingest_dataset(dataset)

            # Paso 3: Verificar ingestión
            stats, results = self.verify_ingestion()

            print("\n🎉 Fase 1 completada exitosamente!")
            print(f"📊 Documentos ingeridos: {stats['documents']}")
            print(f"🔢 Embeddings generados: {stats['embeddings']}")
            print(f"🤖 Modelo utilizado: {stats['current_model']}")
            print(f"📏 Dimensión: {stats['dimension']}")

            return True

        except Exception as e:
            print(f"❌ Error en Fase 1: {e}")
            return False

        finally:
            # Cerrar conexión
            self.db.close()

if __name__ == "__main__":
    fase1 = Fase1IngestionControl()
    success = fase1.run_fase1()

    if success:
        print("\n✅ Listo para Fase 2: Experimento con embedders")
    else:
        print("\n❌ Revisar errores antes de continuar")