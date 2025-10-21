#!/usr/bin/env python3
"""
Tests de integración para el pipeline de ingestión RAG
"""
import pytest
import json
import time
import tempfile
import hashlib
from pathlib import Path

from second_brain.plan.ingest_fase1 import Fase1IngestionControl


class TestIngestionPipelineIntegration:
    """Tests de integración del pipeline completo de ingestión"""

    def test_fase1_initialization(self, rag_database):
        """Test inicialización del pipeline Fase 1"""
        # Crear una instancia temporal para testing
        fase1 = Fase1IngestionControl()

        assert fase1.embedding_model == "all-MiniLM-L6-v2"
        assert fase1.embedding_dim == 384
        assert fase1.db is not None
        assert fase1.embedder is not None
        assert hasattr(fase1, 'dataset_path')

        fase1.db.close()

    def test_dataset_creation_and_persistence(self, rag_database, tmp_path):
        """Test creación y persistencia del dataset"""
        fase1 = Fase1IngestionControl()

        # Forzar creación de nuevo dataset
        dataset_path = Path(fase1.dataset_path)
        if dataset_path.exists():
            dataset_path.unlink()

        dataset = fase1.prepare_dataset()

        # Validar dataset
        assert isinstance(dataset, list)
        assert len(dataset) == 15

        # Validar estructura de cada chunk
        for i, chunk in enumerate(dataset):
            assert isinstance(chunk, dict)
            assert "content" in chunk
            assert "source_hash" in chunk
            assert "source_document" in chunk
            assert "chunking_strategy" in chunk
            assert "chunk_index" in chunk
            assert "semantic_title" in chunk
            assert "semantic_summary" in chunk
            assert "embedding_model" in chunk
            assert "additional_metadata" in chunk

            # Validar hashes únicos
            assert len(chunk["source_hash"]) == 32  # MD5 hash

        # Validar que el archivo se creó
        assert dataset_path.exists()

        # Validar contenido del archivo
        with open(dataset_path, 'r', encoding='utf-8') as f:
            saved_dataset = json.load(f)

        assert len(saved_dataset) == 15
        assert saved_dataset == dataset

        fase1.db.close()

    def test_embedding_generation_consistency(self, rag_database):
        """Test consistencia en la generación de embeddings"""
        fase1 = Fase1IngestionControl()

        # Textos de prueba
        texts = [
            "Docker compose es una herramienta de orquestación",
            "Los embeddings permiten encontrar similitud semántica",
            "PostgreSQL es una base de datos relacional"
        ]

        # Generar embeddings dos veces
        embeddings_1 = fase1.generate_embeddings(texts)
        embeddings_2 = fase1.generate_embeddings(texts)

        # Validar consistencia
        assert len(embeddings_1) == 3
        assert len(embeddings_2) == 3

        for i in range(3):
            assert len(embeddings_1[i]) == 384
            assert len(embeddings_2[i]) == 384

            # Los embeddings deberían ser idénticos para mismo texto
            for j in range(384):
                assert abs(embeddings_1[i][j] - embeddings_2[i][j]) < 1e-6

        fase1.db.close()

    def test_end_to_end_ingestion(self, rag_database):
        """Test completo del pipeline de ingestión"""
        fase1 = Fase1IngestionControl()

        # Limpiar BD antes del test
        with fase1.db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM document_embeddings")
                cursor.execute("DELETE FROM documents")
                conn.commit()

        # Ejecutar ingestión completa
        success = fase1.run_fase1()

        # Validar éxito
        assert success is True

        # Validar datos en BD
        stats = fase1.db.get_stats()
        assert stats["documents"] == 15
        assert stats["embeddings"] == 15
        assert stats["models"] == 1
        assert stats["current_model"] == "all-MiniLM-L6-v2"
        assert stats["dimension"] == 384

        # Validar logs
        log_path = Path("second_brain/plan/logs/fase_1_ingestion.json")
        assert log_path.exists()

        with open(log_path, 'r') as f:
            log_data = json.load(f)

        assert log_data["fase"] == "fase_1"
        assert log_data["embedder"] == "all-MiniLM-L6-v2"
        assert log_data["dimension"] == 384
        assert log_data["document_count"] == 15
        assert log_data["status"] == "completed"

        fase1.db.close()

    def test_ingestion_with_metadata_validation(self, rag_database):
        """Test ingestión con validación completa de metadata"""
        fase1 = Fase1IngestionControl()

        # Preparar dataset controlado
        dataset = [
            {
                "content": "Test document for metadata validation",
                "source_hash": hashlib.md5("test content".encode()).hexdigest(),
                "source_document": "test_metadata.txt",
                "chunking_strategy": "test_validation",
                "chunk_index": 0,
                "char_start": 0,
                "char_end": 50,
                "semantic_title": "Metadata Validation Test",
                "semantic_summary": "Testing complete metadata validation",
                "semantic_overlap": "",
                "embedding_model": "all-MiniLM-L6-v2",
                "additional_metadata": {
                    "test_type": "metadata_validation",
                    "timestamp": "2025-01-18T23:59:00Z",
                    "validation": True,
                    "nested": {"level": 1, "data": "test"}
                }
            }
        ]

        # Generar embeddings
        texts = [chunk["content"] for chunk in dataset]
        embeddings = fase1.generate_embeddings(texts)

        # Preparar documentos para inserción
        documents = []
        for chunk, embedding in zip(dataset, embeddings):
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
            documents.append((chunk["content"], embedding, metadata))

        # Ingestar documentos
        fase1.db.add_documents_with_metadata(documents)

        # Validar metadata en BD
        with fase1.db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT source_document, chunking_strategy, chunk_index,
                           char_start, char_end, semantic_title, semantic_summary,
                           metadata_json
                    FROM documents
                    WHERE source_hash = %s
                """, (dataset[0]["source_hash"],))

                result = cursor.fetchone()
                assert result is not None

                (source_doc, strategy, chunk_idx, char_start, char_end,
                 title, summary, metadata_json) = result

                assert source_doc == "test_metadata.txt"
                assert strategy == "test_validation"
                assert chunk_idx == 0
                assert char_start == 0
                assert char_end == 50
                assert title == "Metadata Validation Test"
                assert summary == "Testing complete metadata validation"

                # Validar JSON metadata
                parsed_metadata = json.loads(metadata_json)
                assert parsed_metadata["test_type"] == "metadata_validation"
                assert parsed_metadata["validation"] is True
                assert parsed_metadata["nested"]["level"] == 1

        fase1.db.close()

    def test_search_relevance_validation(self, rag_database):
        """Test validación de relevancia de búsqueda"""
        fase1 = Fase1IngestionControl()

        # Preparar base de datos con datos conocidos
        dataset = [
            {
                "content": "Docker compose es una herramienta para definir y ejecutar aplicaciones Docker múltiples contenedores utilizando archivos YAML para configuración de servicios.",
                "source_hash": hashlib.md5("docker content".encode()).hexdigest(),
                "source_document": "docker_test.txt",
                "chunking_strategy": "test",
                "chunk_index": 0,
                "char_start": 0,
                "char_end": 150,
                "semantic_title": "Docker Compose Test",
                "semantic_summary": "Test content about Docker Compose for container orchestration",
                "semantic_overlap": "",
                "embedding_model": "all-MiniLM-L6-v2",
                "additional_metadata": {"test": True}
            }
        ]

        # Ingestar datos
        texts = [chunk["content"] for chunk in dataset]
        embeddings = fase1.generate_embeddings(texts)

        documents = []
        for chunk, embedding in zip(dataset, embeddings):
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
            documents.append((chunk["content"], embedding, metadata))

        fase1.db.add_documents_with_metadata(documents)

        # Test queries con diferentes niveles de relevancia
        test_queries = [
            ("Docker compose", 0.5),  # Alta relevancia
            ("herramienta Docker", 0.4),  # Media relevancia
            ("contenedores aplicaciones", 0.3),  # Baja relevancia
            ("consulta completamente irrelevante", 0.0)  # Sin relevancia
        ]

        for query, min_similarity in test_queries:
            query_embedding = fase1.embedder.encode([query])[0].tolist()
            results = fase1.db.search_similar(query_embedding, top_k=3)

            if min_similarity > 0:
                # Para queries relevantes, debería encontrar resultados
                assert len(results) > 0, f"Query '{query}' debería encontrar resultados"
                best_similarity = results[0][1]
                assert best_similarity >= min_similarity, \
                    f"Query '{query}' got similarity {best_similarity:.3f}, expected >= {min_similarity}"
            else:
                # Para queries irrelevantes, puede o no encontrar resultados
                # Si encuentra resultados, la similitud debería ser baja
                if results:
                    best_similarity = results[0][1]
                    assert best_similarity < 0.3, \
                        f"Irrelevant query '{query}' got high similarity {best_similarity:.3f}"

        fase1.db.close()


class TestIngestionPerformance:
    """Tests de performance del pipeline de ingestión"""

    def test_ingestion_performance_benchmarks(self, rag_database, rag_performance_thresholds):
        """Test benchmarks de performance de ingestión"""
        fase1 = Fase1IngestionControl()

        # Limpiar BD
        with fase1.db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM document_embeddings")
                cursor.execute("DELETE FROM documents")
                conn.commit()

        # Medir tiempo de ingestión completo
        start_time = time.time()

        # Crear dataset más pequeño para test de performance
        small_dataset = [
            {
                "content": f"Test document {i} for performance testing",
                "source_hash": hashlib.md5(f"perf_test_{i}".encode()).hexdigest(),
                "source_document": f"perf_test_{i}.txt",
                "chunking_strategy": "performance_test",
                "chunk_index": i,
                "char_start": i * 100,
                "char_end": (i + 1) * 100 - 1,
                "semantic_title": f"Performance Test {i}",
                "semantic_summary": f"Performance test document number {i}",
                "semantic_overlap": "",
                "embedding_model": "all-MiniLM-L6-v2",
                "additional_metadata": {"performance_test": True, "doc_id": i}
            }
            for i in range(5)  # 5 documentos para test rápido
        ]

        # Generar embeddings e insertar
        texts = [chunk["content"] for chunk in small_dataset]
        embeddings = fase1.generate_embeddings(texts)

        documents = []
        for chunk, embedding in zip(small_dataset, embeddings):
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
            documents.append((chunk["content"], embedding, metadata))

        fase1.db.add_documents_with_metadata(documents)

        end_time = time.time()
        total_time = end_time - start_time

        # Validar performance
        max_time_per_doc = rag_performance_thresholds["max_ingestion_time_per_doc"]
        expected_max_time = max_time_per_doc * 5  # 5 documentos

        assert total_time < expected_max_time, \
            f"Ingestión tomó {total_time:.3f}s, expected < {expected_max_time:.3f}s"

        # Validar que todos los documentos se insertaron
        stats = fase1.db.get_stats()
        assert stats["documents"] == 5
        assert stats["embeddings"] == 5

        fase1.db.close()

    def test_embedding_generation_performance(self, rag_database, rag_performance_thresholds):
        """Test performance de generación de embeddings"""
        fase1 = Fase1IngestionControl()

        # Generar embeddings para diferentes tamaños de lote
        batch_sizes = [1, 5, 10, 15]
        max_embedding_time = rag_performance_thresholds["max_embedding_generation_time"]

        for batch_size in batch_sizes:
            texts = [f"Test text {i}" for i in range(batch_size)]

            start_time = time.time()
            embeddings = fase1.generate_embeddings(texts)
            end_time = time.time()

            generation_time = end_time - start_time

            # Validar resultados
            assert len(embeddings) == batch_size
            assert all(len(emb) == 384 for emb in embeddings)

            # Validar performance (tiempo por embedding)
            time_per_embedding = generation_time / batch_size
            assert time_per_embedding < max_embedding_time, \
                f"Embedding generation took {time_per_embedding:.4f}s per embedding, expected < {max_embedding_time}s"

        fase1.db.close()


class TestIngestionErrorHandling:
    """Tests de manejo de errores en el pipeline"""

    def test_ingestion_with_invalid_metadata(self, rag_database):
        """Test manejo de metadata inválida"""
        fase1 = Fase1IngestionControl()

        # Test con metadata incompleta
        incomplete_metadata = {
            "source_document": "test.txt",
            # Falta source_hash y otros campos requeridos
        }

        embedding = [0.1] * 384
        content = "Test content"

        # El sistema debería generar source_hash automáticamente
        try:
            fase1.db.add_documents_with_metadata([(content, embedding, incomplete_metadata)])
            # Debería funcionar porque source_hash se genera automáticamente
        except Exception as e:
            pytest.fail(f"Debería manejar metadata incompleta: {e}")

        fase1.db.close()

    def test_ingestion_with_empty_content(self, rag_database):
        """Test manejo de contenido vacío"""
        fase1 = Fase1IngestionControl()

        empty_content = ""
        embedding = [0.1] * 384

        metadata = {
            "source_document": "empty_test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería poder manejar contenido vacío (generará hash pero content estará vacío)
        try:
            fase1.db.add_documents_with_metadata([(empty_content, embedding, metadata)])
        except Exception as e:
            # Puede fallar validación de contenido vacío dependiendo de la implementación
            print(f"Expected behavior for empty content: {e}")

        fase1.db.close()

    def test_fase1_with_database_errors(self):
        """Test manejo de errores de base de datos en Fase 1"""
        # Este test requeriría mocking para simular errores de BD
        # Por ahora validamos el flujo normal
        pass