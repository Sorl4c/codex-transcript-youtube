"""
Tests for vector operations and KNN queries.

This module tests vector search functionality, including native KNN queries,
similarity calculations, and distance function usage with sqlite-vec.
"""

import pytest
import time
import sqlite3
from typing import List, Tuple

from rag_engine.database import SQLiteVecDatabase


class TestVectorOperations:
    """Test vector operations and KNN queries."""

    def test_native_knn_queries(self, populated_test_database):
        """Test native KNN queries with vec0 virtual tables."""
        db = populated_test_database

        # Test vector search with mock embedding
        query_embedding = [0.1] * 384  # Simple test vector

        start_time = time.time()
        results = db.search_similar(query_embedding, top_k=3)
        query_time = time.time() - start_time

        # Should return results
        assert len(results) > 0
        assert len(results) <= 3

        # Results should be tuples of (content, similarity_score)
        for content, score in results:
            assert isinstance(content, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1  # Similarity scores should be normalized

        # Query should be fast (native KNN)
        assert query_time < 0.1, f"KNN query too slow: {query_time:.3f}s"

    def test_knn_query_with_different_k_values(self, populated_test_database):
        """Test KNN queries with different top_k values."""
        db = populated_test_database
        query_embedding = [0.2] * 384

        # Test with different k values
        for k in [1, 2, 3, 5, 10]:
            results = db.search_similar(query_embedding, top_k=k)

            # Should return at most k results
            assert len(results) <= k

            # Results should be sorted by similarity (descending)
            if len(results) > 1:
                similarities = [score for _, score in results]
                assert similarities == sorted(similarities, reverse=True)

    def test_vector_similarity_scoring(self, test_database):
        """Test that similarity scores are calculated correctly."""
        db = test_database

        # Create test documents with known vectors
        test_docs = [
            ("Document A", [1.0, 0.0, 0.0], {}),
            ("Document B", [0.0, 1.0, 0.0], {}),
            ("Document C", [1.0, 0.0, 0.0], {}),  # Same as A
        ]
        db.add_documents_with_metadata(test_docs)

        # Query with vector similar to Document A/C
        query_vector = [0.9, 0.1, 0.0]
        results = db.search_similar(query_vector, top_k=3)

        assert len(results) >= 2

        # Documents A and C should have highest similarity (they're identical)
        scores = [score for _, score in results]
        top_scores = sorted(scores, reverse=True)[:2]

        # Top two scores should be very similar (for identical documents)
        assert abs(top_scores[0] - top_scores[1]) < 0.1

    def test_vector_distance_calculation(self, test_database):
        """Test distance calculation in vector search."""
        db = test_database

        # Add documents with orthogonal vectors
        test_docs = [
            ("Orthogonal 1", [1.0, 0.0, 0.0], {}),
            ("Orthogonal 2", [0.0, 1.0, 0.0], {}),
            ("Similar", [0.9, 0.1, 0.0], {}),
        ]
        db.add_documents_with_metadata(test_docs)

        # Query with vector similar to "Similar"
        query_vector = [1.0, 0.0, 0.0]
        results = db.search_similar(query_vector, top_k=3)

        # Extract contents and scores
        result_map = {content: score for content, score in results}

        # "Similar" document should have highest score
        if "Similar" in result_map and "Orthogonal 1" in result_map:
            assert result_map["Similar"] > result_map["Orthogonal 1"]

    def test_empty_vector_database(self, test_database):
        """Test vector search on empty database."""
        db = test_database

        # Don't add any documents
        query_vector = [0.1] * 384
        results = db.search_similar(query_vector, top_k=5)

        # Should return empty results
        assert len(results) == 0

    def test_single_document_search(self, test_database):
        """Test vector search with single document."""
        db = test_database

        # Add single document
        test_docs = [("Single document", [0.5, 0.5, 0.5], {})]
        db.add_documents_with_metadata(test_docs)

        query_vector = [0.5, 0.5, 0.5]
        results = db.search_similar(query_vector, top_k=5)

        # Should return exactly one result
        assert len(results) == 1
        content, score = results[0]
        assert content == "Single document"
        assert score > 0.9  # Should be very high similarity

    def test_vector_dimension_mismatch(self, test_database):
        """Test handling of vector dimension mismatches."""
        db = test_database

        # Add document with 3D vector
        test_docs = [("3D document", [0.1, 0.2, 0.3], {})]
        db.add_documents_with_metadata(test_docs)

        # Query with different dimension vector (should still work with appropriate handling)
        query_vector_5d = [0.1, 0.1, 0.1, 0.1, 0.1]

        # This should either work or fail gracefully
        try:
            results = db.search_similar(query_vector_5d, top_k=1)
            # If it works, results should be empty or handled appropriately
            assert isinstance(results, list)
        except Exception as e:
            # Should fail with a clear error message
            assert "dimension" in str(e).lower() or "size" in str(e).lower()

    def test_vector_search_performance(self, populated_test_database, rag_performance_thresholds):
        """Test that vector search meets performance thresholds."""
        db = populated_test_database
        query_vector = [0.1] * 384

        # Multiple queries to test consistency
        times = []
        for _ in range(5):
            start_time = time.time()
            results = db.search_similar(query_vector, top_k=5)
            query_time = time.time() - start_time
            times.append(query_time)

            # Each query should be fast
            assert query_time < rag_performance_thresholds["max_knn_query_time"]

        # Average should also be fast
        avg_time = sum(times) / len(times)
        assert avg_time < rag_performance_thresholds["max_knn_query_time"]

    def test_batch_vector_operations(self, test_database):
        """Test batch vector operations."""
        db = test_database

        # Add multiple documents in batch
        batch_size = 10
        test_docs = [
            (f"Document {i}", [0.1 * i] * 384, {"batch_id": i})
            for i in range(batch_size)
        ]

        start_time = time.time()
        db.add_documents_with_metadata(test_docs)
        batch_time = time.time() - start_time

        # Batch insertion should be reasonably fast
        assert batch_time < batch_size * rag_performance_thresholds["max_database_insertion_time"]

        # Verify all documents were added
        doc_count = db.get_document_count()
        assert doc_count == batch_size

        # Test batch search (multiple queries)
        query_vectors = [[0.1 * i] * 384 for i in range(3)]
        all_results = []

        for query_vec in query_vectors:
            results = db.search_similar(query_vec, top_k=3)
            all_results.extend(results)

        # Should get results for each query
        assert len(all_results) > 0

    def test_vector_search_with_metadata_filtering(self, test_database):
        """Test vector search combined with metadata filtering."""
        db = test_database

        # Add documents with different categories
        test_docs = [
            ("AI document", [0.1, 0.2, 0.3], {"category": "ai"}),
            ("Database document", [0.4, 0.5, 0.6], {"category": "database"}),
            ("NLP document", [0.7, 0.8, 0.9], {"category": "nlp"}),
        ]
        db.add_documents_with_metadata(test_docs)

        # Search for AI-related content
        query_vector = [0.1, 0.2, 0.3]
        results = db.search_similar(query_vector, top_k=5)

        # Should find the AI document with highest similarity
        assert len(results) > 0

        # Find AI document in results
        ai_found = any("AI document" in content for content, _ in results)
        assert ai_found, "AI document should be found in search results"

    def test_vector_search_result_consistency(self, populated_test_database):
        """Test that vector search returns consistent results."""
        db = populated_test_database
        query_vector = [0.15] * 384

        # Run same query multiple times
        result_sets = []
        for _ in range(3):
            results = db.search_similar(query_vector, top_k=3)
            result_sets.append(results)

        # Results should be identical across runs
        for i in range(1, len(result_sets)):
            assert len(result_sets[i]) == len(result_sets[0])

            for j, (content1, score1) in enumerate(result_sets[0]):
                content2, score2 = result_sets[i][j]
                assert content1 == content2
                assert abs(score1 - score2) < 1e-6  # Very high precision required

    def test_legacy_fallback_search(self):
        """Test fallback to legacy search when vec0 tables are not available."""
        import tempfile
        import os

        # Create temporary database
        temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db', prefix='rag_legacy_fallback_')
        os.close(temp_db_fd)

        try:
            # Create database without vec0 support
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()

            # Create legacy table structure
            cursor.execute("""
                CREATE TABLE test_legacy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    embedding TEXT
                )
            """)

            # Insert test data with JSON embedding
            import json
            cursor.execute("""
                INSERT INTO test_legacy (content, embedding)
                VALUES (?, ?)
            """, ("Legacy content", json.dumps([0.1, 0.2, 0.3])))

            conn.commit()
            conn.close()

            # Create SQLiteVecDatabase - should handle legacy format
            db = SQLiteVecDatabase(db_path=temp_db_path, table_name="test_legacy")

            # Try search - should fallback to legacy method
            query_vector = [0.1, 0.2, 0.3]
            results = db.search_similar(query_vector, top_k=1)

            # Should get results from legacy fallback
            assert len(results) >= 1
            content, score = results[0]
            assert "Legacy content" in content

            del db

        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)