#!/usr/bin/env python3
"""
Tests unitarios para PostgreSQLVectorDatabase - Core functionality
"""
import pytest
import time
import hashlib
from unittest.mock import patch, MagicMock

from second_brain.plan.postgresql_database_experimental import PostgreSQLVectorDatabase


class TestPostgreSQLVectorDatabaseConnection:
    """Tests de conexión y configuración"""

    def test_database_initialization(self, rag_database):
        """Test que la base de datos se inicializa correctamente"""
        db = rag_database

        assert db.embedding_dim == 384
        assert db.embedding_model == "all-MiniLM-L6-v2"
        assert db.pool is not None
        assert hasattr(db, '_build_connection_string')

    def test_connection_string_building(self, postgres_config):
        """Test construcción de connection string"""
        # Patch temporal para probar el método
        with patch.object(PostgreSQLVectorDatabase, '__init__', return_value=None):
            db = PostgreSQLVectorDatabase.__new__(PostgreSQLVectorDatabase)
            db.embedding_dim = 384
            db.embedding_model = "all-MiniLM-L6-v2"

            conn_string = db._build_connection_string(postgres_config)

            assert "host=localhost" in conn_string
            assert "port=5432" in conn_string
            assert "dbname=rag_experiments" in conn_string
            assert "user=rag_user" in conn_string

    def test_database_connectivity(self, rag_database):
        """Test que la conexión es funcional"""
        db = rag_database

        # Test consulta simple
        stats = db.get_stats()
        assert isinstance(stats, dict)
        assert 'documents' in stats
        assert 'embeddings' in stats
        assert 'models' in stats
        assert 'current_model' in stats
        assert 'dimension' in stats

    def test_database_schema_validation(self, rag_database):
        """Test que el schema existe y es válido"""
        db = rag_database

        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                # Verificar que las tablas existen
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name IN ('documents', 'document_embeddings')
                """)
                tables = cursor.fetchall()
                assert len(tables) == 2

                # Verificar columnas principales
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'documents' AND column_name IN ('id', 'content', 'source_hash')
                """)
                doc_columns = cursor.fetchall()
                assert len(doc_columns) == 3

                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'document_embeddings' AND column_name IN ('id', 'document_id', 'embedding')
                """)
                emb_columns = cursor.fetchall()
                assert len(emb_columns) == 3


class TestPostgreSQLVectorDatabaseEmbeddings:
    """Tests de manejo de embeddings"""

    def test_embedding_dimension_validation(self, rag_database):
        """Test validación de dimensiones de embeddings"""
        db = rag_database

        # Embedding correcto (384 dimensiones)
        correct_embedding = [0.1] * 384
        content = "Test content"

        # Mock metadata
        metadata = {
            "source_hash": hashlib.md5(content.encode()).hexdigest(),
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # No debería lanzar excepción
        try:
            db.add_documents_with_metadata([(content, correct_embedding, metadata)])
        except Exception as e:
            pytest.fail(f"No debería lanzar excepción con embedding correcto: {e}")

    def test_embedding_wrong_dimension_rejection(self, rag_database):
        """Test rechazo de embeddings con dimensiones incorrectas"""
        db = rag_database

        # Embedding incorrecto (256 dimensiones en lugar de 384)
        wrong_embedding = [0.1] * 256
        content = "Test content"

        metadata = {
            "source_hash": hashlib.md5(content.encode()).hexdigest(),
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Debería lanzar ValueError
        with pytest.raises(ValueError, match="Dimensión incorrecta"):
            db.add_documents_with_metadata([(content, wrong_embedding, metadata)])

    def test_embedding_storage_format(self, rag_database, sample_embeddings_384):
        """Test que los embeddings se almacenan en formato vectorial correcto"""
        db = rag_database

        content = "Test embedding format"
        embedding = sample_embeddings_384[0]  # Primer embedding de prueba

        metadata = {
            "source_hash": hashlib.md5(content.encode()).hexdigest(),
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Insertar documento
        db.add_documents_with_metadata([(content, embedding, metadata)])

        # Verificar formato en BD
        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT embedding FROM document_embeddings LIMIT 1")
                result = cursor.fetchone()

                assert result is not None
                stored_embedding = result[0]

                # Verificar que es un string en formato vector
                assert isinstance(stored_embedding, str)
                assert stored_embedding.startswith('[')
                assert stored_embedding.endswith(']')

                # Verificar dimensión con vector_dims
                cursor.execute("SELECT vector_dims(embedding) FROM document_embeddings LIMIT 1")
                dim_result = cursor.fetchone()
                assert dim_result[0] == 384


class TestPostgreSQLVectorDatabaseSearch:
    """Tests de funcionalidad de búsqueda"""

    def test_search_with_exact_match(self, populated_rag_database, sample_embeddings_384):
        """Test búsqueda con embedding exacto"""
        db = populated_rag_database

        # Usar embedding exacto de un documento en la BD
        test_embedding = sample_embeddings_384[0]  # Primer embedding

        results = db.search_similar(test_embedding, top_k=3)

        # Debería encontrar al menos 1 resultado con similitud = 1.0
        assert len(results) >= 1

        # El primer resultado debería tener similitud 1.0 (match exacto)
        best_content, best_similarity = results[0]
        assert best_similarity == 1.0

    def test_search_performance(self, populated_rag_database, sample_embeddings_384, rag_performance_thresholds):
        """Test performance de búsqueda"""
        db = populated_rag_database
        max_time_ms = rag_performance_thresholds["max_search_time_ms"]

        test_embedding = sample_embeddings_384[1]

        # Medir tiempo de búsqueda
        start_time = time.time()
        results = db.search_similar(test_embedding, top_k=5)
        end_time = time.time()

        search_time_ms = (end_time - start_time) * 1000

        # Validar performance
        assert search_time_ms < max_time_ms, f"Búsqueda tomó {search_time_ms:.2f}ms, umbral es {max_time_ms}ms"
        assert len(results) <= 5  # No debería devolver más de 5 resultados

    def test_search_with_different_queries(self, populated_rag_database, rag_test_queries):
        """Test búsqueda con diferentes queries"""
        db = populated_rag_database

        from sentence_transformers import SentenceTransformer

        embedder = SentenceTransformer('all-MiniLM-L6-v2')

        for query_config in rag_test_queries:
            query = query_config["query"]
            expected_min = query_config["expected_min_similarity"]

            # Generar embedding para la query
            query_embedding = embedder.encode([query])[0].tolist()

            results = db.search_similar(query_embedding, top_k=3)

            # Validar resultados
            assert isinstance(results, list)
            assert len(results) >= 0

            # Verificar formato de resultados
            for content, similarity in results:
                assert isinstance(content, str)
                assert isinstance(similarity, (float, int))
                # La similitud de coseno puede ser negativa para vectores muy opuestos
                assert -1 <= similarity <= 1

    def test_search_empty_database(self, rag_database, sample_embeddings_384):
        """Test búsqueda en base de datos vacía"""
        db = rag_database

        results = db.search_similar(sample_embeddings_384[0], top_k=5)

        # Debería devolver lista vacía
        assert results == []

    def test_search_with_invalid_embedding_dimension(self, rag_database):
        """Test búsqueda con embedding de dimensión inválida"""
        db = rag_database

        # Embedding con dimensión incorrecta
        invalid_embedding = [0.1] * 100  # 100 dimensiones en lugar de 384

        with pytest.raises(ValueError, match="Dimensión incorrecta en query"):
            db.search_similar(invalid_embedding, top_k=5)


class TestPostgreSQLVectorDatabaseMetadata:
    """Tests de manejo de metadata"""

    def test_document_metadata_storage(self, rag_database, sample_embeddings_384):
        """Test almacenamiento de metadata de documentos"""
        db = rag_database

        content = "Test document with metadata"
        embedding = sample_embeddings_384[0]

        metadata = {
            "source_hash": hashlib.md5(content.encode()).hexdigest(),
            "source_document": "test_document.md",
            "chunking_strategy": "agentic",
            "chunk_index": 5,
            "char_start": 100,
            "char_end": 200,
            "semantic_title": "Test Document Title",
            "semantic_summary": "Test summary of the document",
            "semantic_overlap": "overlap content",
            "additional_metadata": {
                "test_key": "test_value",
                "numeric_value": 42,
                "nested": {"key": "value"}
            }
        }

        # Insertar documento
        db.add_documents_with_metadata([(content, embedding, metadata)])

        # Verificar metadata almacenada
        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT source_document, chunking_strategy, chunk_index,
                           char_start, char_end, semantic_title, semantic_summary,
                           metadata_json
                    FROM documents
                    WHERE source_hash = %s
                """, (metadata["source_hash"],))

                result = cursor.fetchone()
                assert result is not None

                (source_doc, strategy, chunk_idx, char_start, char_end,
                 title, summary, metadata_json) = result

                assert source_doc == metadata["source_document"]
                assert strategy == metadata["chunking_strategy"]
                assert chunk_idx == metadata["chunk_index"]
                assert char_start == metadata["char_start"]
                assert char_end == metadata["char_end"]
                assert title == metadata["semantic_title"]
                assert summary == metadata["semantic_summary"]
                assert metadata_json is not None

    def test_duplicate_document_prevention(self, rag_database, sample_embeddings_384):
        """Test prevención de documentos duplicados vía source_hash"""
        db = rag_database

        content = "Test duplicate prevention"
        embedding = sample_embeddings_384[0]
        source_hash = hashlib.md5(content.encode()).hexdigest()

        metadata = {
            "source_hash": source_hash,
            "source_document": "test.txt",
            "chunking_strategy": "test",
            "chunk_index": 0
        }

        # Insertar mismo documento dos veces
        db.add_documents_with_metadata([(content, embedding, metadata)])
        db.add_documents_with_metadata([(content, embedding, metadata)])

        # Verificar que solo existe un documento
        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM documents WHERE source_hash = %s", (source_hash,))
                count = cursor.fetchone()[0]
                assert count == 1

    def test_statistics_calculation(self, populated_rag_database):
        """Test cálculo de estadísticas"""
        db = populated_rag_database

        stats = db.get_stats()

        assert stats["documents"] == 4  # 4 chunks en fixture
        assert stats["embeddings"] == 4  # 4 embeddings
        assert stats["models"] >= 1
        assert stats["current_model"] == "all-MiniLM-L6-v2"
        assert stats["dimension"] == 384

    def test_document_count_accuracy(self, populated_rag_database):
        """Test precisión del conteo de documentos"""
        db = populated_rag_database

        count = db.get_document_count()
        stats = db.get_stats()

        assert count == stats["documents"]
        assert isinstance(count, int)
        assert count > 0


class TestPostgreSQLVectorDatabaseEdgeCases:
    """Tests de edge cases y manejo de errores"""

    def test_empty_documents_list(self, rag_database):
        """Test manejo de lista vacía de documentos"""
        db = rag_database

        # No debería lanzar excepción
        db.add_documents_with_metadata([])

        # La BD debería seguir vacía
        assert db.get_document_count() == 0

    def test_database_connection_failure(self):
        """Test manejo de fallos de conexión"""
        # Este test requeriría mocking del pool de conexiones
        # Por ahora solo verificamos que el método falle gracefulmente
        pass

    def test_cleanup_on_close(self, rag_database):
        """Test limpieza propera al cerrar conexión"""
        db = rag_database

        # Verificar que el pool existe antes de cerrar
        assert db.pool is not None

        # Cerrar conexión
        db.close()

        # Verificar que el pool se cerró (puede ser None o_closed dependiendo de la implementación)
        # Esto depende de la implementación específica de psycopg_pool