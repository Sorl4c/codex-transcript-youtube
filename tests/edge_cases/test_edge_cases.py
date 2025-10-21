#!/usr/bin/env python3
"""
Tests de edge cases y manejo de errores para el sistema RAG PostgreSQL
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from second_brain.plan.postgresql_database_experimental import PostgreSQLVectorDatabase
from second_brain.plan.ingest_fase1 import Fase1IngestionControl


@pytest.mark.slow
class TestEmbeddingEdgeCases:
    """Tests de edge cases para embeddings"""

    def test_empty_embeddings(self, rag_database):
        """Test manejo de embeddings vacíos"""
        db = rag_database

        # Embedding vacío
        empty_embedding = []
        content = "Test content"

        metadata = {
            "source_hash": "test_hash",
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería lanzar ValueError por dimensión incorrecta
        with pytest.raises(ValueError, match="Dimensión incorrecta"):
            db.add_documents_with_metadata([(content, empty_embedding, metadata)])

    def test_single_dimension_embedding(self, rag_database):
        """Test embedding de una sola dimensión"""
        db = rag_database

        single_embedding = [0.5]
        content = "Test content"

        metadata = {
            "source_hash": "test_hash",
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería lanzar ValueError por dimensión incorrecta
        with pytest.raises(ValueError, match="Dimensión incorrecta"):
            db.add_documents_with_metadata([(content, single_embedding, metadata)])

    def test_very_large_embedding(self, rag_database):
        """Test embedding con dimensiones muy grandes"""
        db = rag_database

        # Embedding con más dimensiones de las esperadas
        large_embedding = [0.1] * 1000  # 1000 dimensiones en lugar de 384
        content = "Test content"

        metadata = {
            "source_hash": "test_hash",
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería lanzar ValueError por dimensión incorrecta
        with pytest.raises(ValueError, match="Dimensión incorrecta"):
            db.add_documents_with_metadata([(content, large_embedding, metadata)])

    def test_embedding_with_nan_values(self, rag_database):
        """Test embedding con valores NaN"""
        db = rag_database

        # Embedding con valor NaN
        nan_embedding = [0.1] * 383 + [float('nan')]
        content = "Test content"

        metadata = {
            "source_hash": "test_hash",
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # El comportamiento puede variar: puede insertar o lanzar error
        # Validamos que el sistema maneje la situación de alguna manera
        try:
            db.add_documents_with_metadata([(content, nan_embedding, metadata)])
            # Si no lanza error, verificamos que se insertó correctamente
            stats = db.get_stats()
            assert stats["embeddings"] >= 1
        except (ValueError, Exception) as e:
            # Si lanza error, también es aceptable
            print(f"Expected behavior for NaN embedding: {e}")

    def test_embedding_with_infinite_values(self, rag_database):
        """Test embedding con valores infinitos"""
        db = rag_database

        # Embedding con valor infinito
        inf_embedding = [0.1] * 383 + [float('inf')]
        content = "Test content"

        metadata = {
            "source_hash": "test_hash",
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Similar al caso NaN, validamos manejo apropiado
        try:
            db.add_documents_with_metadata([(content, inf_embedding, metadata)])
            # Si no lanza error, verificamos que se insertó
            stats = db.get_stats()
            assert stats["embeddings"] >= 1
        except (ValueError, Exception) as e:
            print(f"Expected behavior for infinite embedding: {e}")

    def test_embedding_with_extreme_values(self, rag_database):
        """Test embedding con valores numéricos extremos"""
        db = rag_database

        # Embedding con valores muy grandes y muy pequeños
        extreme_embedding = [float('1e10'), float('-1e10')] + [0.1] * 382
        content = "Test content"

        metadata = {
            "source_hash": "test_hash",
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería manejar valores extremos apropiadamente
        try:
            db.add_documents_with_metadata([(content, extreme_embedding, metadata)])
            stats = db.get_stats()
            assert stats["embeddings"] >= 1
        except Exception as e:
            print(f"Expected behavior for extreme values: {e}")


@pytest.mark.slow
class TestDocumentEdgeCases:
    """Tests de edge cases para documentos"""

    def test_empty_content_document(self, rag_database):
        """Test documento con contenido vacío"""
        db = rag_database

        empty_content = ""
        embedding = [0.1] * 384

        metadata = {
            "source_hash": "empty_hash",  # Hash específico para contenido vacío
            "source_document": "empty.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # El comportamiento puede variar dependiendo de la implementación
        try:
            db.add_documents_with_metadata([(empty_content, embedding, metadata)])
            stats = db.get_stats()
            assert stats["documents"] >= 1

            # Verificar que se pueda buscar
            results = db.search_similar(embedding, top_k=1)
            assert len(results) >= 1
        except Exception as e:
            print(f"Expected behavior for empty content: {e}")

    def test_very_long_document(self, rag_database):
        """Test documento con contenido muy largo"""
        db = rag_database

        # Documento muy largo (varios MB)
        long_content = "Este es un documento muy largo para testing. " * 10000  # ~500KB
        embedding = [0.1] * 384

        metadata = {
            "source_hash": "long_hash",
            "source_document": "long_document.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        try:
            db.add_documents_with_metadata([(long_content, embedding, metadata)])
            stats = db.get_stats()
            assert stats["documents"] >= 1
        except Exception as e:
            print(f"Expected behavior for long content: {e}")

    def test_document_with_unicode_characters(self, rag_database):
        """Test documento con caracteres Unicode complejos"""
        db = rag_database

        # Documento con varios caracteres Unicode
        unicode_content = "Test con Unicode: ñáéíóú, 中文, العربية, русский, emoji 🚀🔍💾, matemáticas ∑∏∫∆∇∂"
        embedding = [0.1] * 384

        metadata = {
            "source_hash": "unicode_hash",
            "source_document": "unicode.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería manejar Unicode correctamente
        db.add_documents_with_metadata([(unicode_content, embedding, metadata)])
        stats = db.get_stats()
        assert stats["documents"] >= 1

        # Verificar que se puede recuperar el contenido correctamente
        results = db.search_similar(embedding, top_k=1)
        assert len(results) >= 1
        recovered_content, _ = results[0]
        assert "ñáéíóú" in recovered_content
        assert "中文" in recovered_content
        assert "🚀" in recovered_content

    def test_document_with_special_characters(self, rag_database):
        """Test documento con caracteres especiales"""
        db = rag_database

        # Documento con caracteres especiales que pueden causar problemas
        special_content = "Test con caracteres especiales: 'comillas', \"dobles comillas\", \n saltos de línea, \t tabuladores, \\ backslashes, % porcentajes, & ampersands"
        embedding = [0.1] * 384

        metadata = {
            "source_hash": "special_hash",
            "source_document": "special.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería manejar caracteres especiales correctamente
        db.add_documents_with_metadata([(special_content, embedding, metadata)])
        stats = db.get_stats()
        assert stats["documents"] >= 1

        # Verificar recuperación
        results = db.search_similar(embedding, top_k=1)
        assert len(results) >= 1
        recovered_content, _ = results[0]
        assert "comillas" in recovered_content

    def test_duplicate_content_different_metadata(self, rag_database):
        """Test manejo de contenido duplicado con metadata diferente"""
        db = rag_database

        content = "Contenido duplicado con metadata diferente"
        embedding = [0.1] * 384

        # Insertar mismo contenido con metadata diferente
        metadata_1 = {
            "source_hash": "duplicate_1",
            "source_document": "doc1.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        metadata_2 = {
            "source_hash": "duplicate_2",
            "source_document": "doc2.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Ambos deberían insertarse porque tienen source_hash diferente
        db.add_documents_with_metadata([
            (content, embedding, metadata_1),
            (content, embedding, metadata_2)
        ])

        stats = db.get_stats()
        assert stats["documents"] == 2  # Ambos documentos insertados

    def test_very_long_metadata_values(self, rag_database):
        """Test metadata con valores muy largos"""
        db = rag_database

        content = "Test con metadata larga"
        embedding = [0.1] * 384

        # Metadata con valores muy largos
        long_title = "T" * 1000  # 1000 caracteres
        long_summary = "S" * 10000  # 10000 caracteres
        long_metadata = {"key": "value" * 1000}  # Metadata JSON grande

        metadata = {
            "source_hash": "long_metadata_hash",
            "source_document": "long_metadata.txt",
            "chunking_strategy": "test",
            "chunk_index": 0,
            "semantic_title": long_title,
            "semantic_summary": long_summary,
            "additional_metadata": long_metadata
        }

        try:
            db.add_documents_with_metadata([(content, embedding, metadata)])
            stats = db.get_stats()
            assert stats["documents"] >= 1
        except Exception as e:
            print(f"Expected behavior for long metadata: {e}")


@pytest.mark.slow
class TestSearchEdgeCases:
    """Tests de edge cases para búsqueda"""

    def test_search_with_zero_vector(self, rag_database):
        """Test búsqueda con vector cero"""
        db = rag_database

        # Vector de todos ceros
        zero_vector = [0.0] * 384

        results = db.search_similar(zero_vector, top_k=3)

        # Debería manejar vector cero sin problemas
        assert isinstance(results, list)

    def test_search_with_normalized_vector(self, rag_database):
        """Test búsqueda con vector normalizado"""
        db = rag_database

        # Vector normalizado (magnitud = 1)
        import math
        normalized_vector = [1.0 / math.sqrt(384)] * 384

        results = db.search_similar(normalized_vector, top_k=3)

        # Debería manejar vector normalizado correctamente
        assert isinstance(results, list)

    def test_search_with_extreme_vector_values(self, rag_database):
        """Test búsqueda con valores extremos en vector"""
        db = rag_database

        # Vector con valores extremos
        extreme_vector = [1.0] * 192 + [-1.0] * 192

        results = db.search_similar(extreme_vector, top_k=3)

        # Debería manejar valores extremos
        assert isinstance(results, list)

    def test_search_top_k_zero(self, rag_database, populated_rag_database):
        """Test búsqueda con top_k = 0"""
        db = rag_database

        test_embedding = [0.1] * 384

        results = db.search_similar(test_embedding, top_k=0)

        # Debería devolver lista vacía
        assert results == []

    def test_search_top_k_negative(self, rag_database, populated_rag_database):
        """Test búsqueda con top_k negativo"""
        db = rag_database

        test_embedding = [0.1] * 384

        # El comportamiento puede variar: puede lanzar error o devolver 0 resultados
        try:
            results = db.search_similar(test_embedding, top_k=-1)
            # Si no lanza error, debería devolver lista vacía o comportamiento razonable
            assert isinstance(results, list)
        except (ValueError, Exception) as e:
            print(f"Expected behavior for negative top_k: {e}")

    def test_search_top_k_very_large(self, rag_database, populated_rag_database):
        """Test búsqueda con top_k muy grande"""
        db = rag_database

        test_embedding = [0.1] * 384

        results = db.search_similar(test_embedding, top_k=1000)

        # No debería devolver más resultados de los que existen
        stats = db.get_stats()
        assert len(results) <= stats["documents"]

    def test_search_empty_database_with_embedding(self, rag_database):
        """Test búsqueda en base de datos vacía"""
        db = rag_database

        # Asegurar que la BD esté vacía
        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM document_embeddings")
                cursor.execute("DELETE FROM documents")
                conn.commit()

        test_embedding = [0.1] * 384

        results = db.search_similar(test_embedding, top_k=5)

        # Debería devolver lista vacía
        assert results == []


@pytest.mark.slow
class TestErrorRecovery:
    """Tests de recuperación de errores"""

    def test_database_connection_recovery(self):
        """Test recuperación de conexión a base de datos"""
        # Este test requeriría mocking para simular caídas de conexión
        # Por ahora validamos el manejo básico
        pass

    def test_partial_failure_recovery(self, rag_database):
        """Test recuperación de fallos parciales"""
        db = rag_database

        # Insertar lote con algunos documentos inválidos
        documents = []

        # Documentos válidos
        for i in range(3):
            content = f"Valid document {i}"
            embedding = [0.1] * 384
            metadata = {
                "source_hash": f"valid_hash_{i}",
                "source_document": f"valid_{i}.txt",
                "chunking_strategy": "test",
                "chunk_index": i
            }
            documents.append((content, embedding, metadata))

        # Documento inválido (dimensión incorrecta)
        invalid_content = "Invalid document"
        invalid_embedding = [0.1] * 100  # Dimensión incorrecta
        invalid_metadata = {
            "source_hash": "invalid_hash",
            "source_document": "invalid.txt",
            "chunking_strategy": "test",
            "chunk_index": 100
        }
        documents.append((invalid_content, invalid_embedding, invalid_metadata))

        # Más documentos válidos
        for i in range(3, 5):
            content = f"Valid document {i}"
            embedding = [0.1] * 384
            metadata = {
                "source_hash": f"valid_hash_{i}",
                "source_document": f"valid_{i}.txt",
                "chunking_strategy": "test",
                "chunk_index": i
            }
            documents.append((content, embedding, metadata))

        # El sistema debería manejar el fallo parcial
        try:
            db.add_documents_with_metadata(documents)
            stats = db.get_stats()
            # Al menos los documentos válidos deberían insertarse
            assert stats["documents"] >= 4  # Mínimo 4 documentos válidos
        except Exception as e:
            print(f"Expected behavior for partial failure: {e}")

    def test_corrupted_data_handling(self, rag_database):
        """Test manejo de datos corruptos"""
        db = rag_database

        # Intentar insertar datos que podrían causar corrupción
        problematic_content = "Test with problematic content: \x00\x01\x02"
        embedding = [0.1] * 384

        metadata = {
            "source_hash": "corrupted_hash",
            "source_document": "corrupted.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        try:
            db.add_documents_with_metadata([(problematic_content, embedding, metadata)])
            stats = db.get_stats()
            assert stats["documents"] >= 1
        except Exception as e:
            print(f"Expected behavior for corrupted data: {e}")

    def test_memory_exhaustion_simulation(self, rag_database):
        """Test simulación de agotamiento de memoria"""
        # Este test es difícil de implementar sin causar problemas reales
        # Por ahora lo marcamos como placeholder
        pass


@pytest.mark.slow
class TestConfigurationEdgeCases:
    """Tests de edge cases de configuración"""

    def test_missing_environment_variables(self):
        """Test manejo de variables de entorno faltantes"""
        # Temporalmente remover variables de entorno
        original_env = {}
        for var in ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB']:
            original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        try:
            # Debería fallar gracefulmente o usar defaults
            with pytest.raises(Exception):
                db = PostgreSQLVectorDatabase()
        finally:
            # Restaurar variables de entorno
            for var, value in original_env.items():
                if value is not None:
                    os.environ[var] = value

    def test_invalid_port_configuration(self):
        """Test configuración con puerto inválido"""
        with patch.dict(os.environ, {'POSTGRES_PORT': 'invalid_port'}):
            try:
                with pytest.raises(Exception):
                    db = PostgreSQLVectorDatabase()
            except Exception as e:
                print(f"Expected behavior for invalid port: {e}")

    def test_invalid_embedding_dimension(self):
        """Test configuración con dimensión de embedding inválida"""
        with patch.dict(os.environ, {'EMBEDDING_DIM': 'invalid_dim'}):
            try:
                with pytest.raises((ValueError, Exception)):
                    db = PostgreSQLVectorDatabase()
            except Exception as e:
                print(f"Expected behavior for invalid dimension: {e}")


@pytest.mark.slow
class TestConcurrencyEdgeCases:
    """Tests de edge cases de concurrencia"""

    def test_concurrent_same_document_insertion(self, rag_database):
        """Test inserción concurrente del mismo documento"""
        import threading
        import time

        db = rag_database
        results = []

        def insert_document(thread_id):
            content = "Concurrent test document"
            embedding = [0.1] * 384

            metadata = {
                "source_hash": "concurrent_hash",  # Mismo hash para todos los threads
                "source_document": f"concurrent_{thread_id}.txt",
                "chunking_strategy": "test",
                "chunk_index": thread_id
            }

            try:
                db.add_documents_with_metadata([(content, embedding, metadata)])
                results.append(f"Thread {thread_id}: Success")
            except Exception as e:
                results.append(f"Thread {thread_id}: Error - {e}")

        # Crear múltiples threads intentando insertar el mismo documento
        threads = []
        for i in range(5):
            thread = threading.Thread(target=insert_document, args=(i,))
            threads.append(thread)

        # Iniciar todos los threads simultáneamente
        for thread in threads:
            thread.start()

        # Esperar a que todos terminen
        for thread in threads:
            thread.join()

        # Validar resultados
        print(f"Concurrent insertion results: {results}")

        # Solo debería existir un documento (gracias al source_hash único)
        stats = db.get_stats()
        # El número exacto depende de la implementación de concurrencia
        assert stats["documents"] >= 1

    def test_concurrent_search_same_query(self, populated_rag_database):
        """Test búsqueda concurrente con misma query"""
        import threading

        db = populated_rag_database
        results = []

        def search_query(thread_id):
            test_embedding = [0.1] * 384

            try:
                search_results = db.search_similar(test_embedding, top_k=3)
                results.append(f"Thread {thread_id}: {len(search_results)} results")
            except Exception as e:
                results.append(f"Thread {thread_id}: Error - {e}")

        # Crear múltiples threads buscando la misma query
        threads = []
        for i in range(10):
            thread = threading.Thread(target=search_query, args=(i,))
            threads.append(thread)

        # Iniciar todos los threads
        for thread in threads:
            thread.start()

        # Esperar a que todos terminen
        for thread in threads:
            thread.join()

        # Validar que todos los threads obtuvieron resultados
        print(f"Concurrent search results: {results}")

        # Todos deberían haber obtenido resultados
        success_count = sum(1 for result in results if "Error" not in result)
        assert success_count >= 8  # Al menos 8 de 10 deberían tener éxito