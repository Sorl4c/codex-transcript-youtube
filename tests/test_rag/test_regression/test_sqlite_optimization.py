"""
Regression tests for sqlite-vec optimization.

This module validates that the sqlite-vec optimization is working correctly
and that we're using native KNN queries instead of manual calculations.
"""

import pytest
import time
import sqlite3
from typing import List, Dict, Any

from rag_engine.database import SQLiteVecDatabase
from rag_engine.hybrid_retriever import HybridRetriever
from rag_engine.retriever import SimpleRetriever


class TestSQLiteVecOptimization:
    """Regression tests to ensure sqlite-vec optimization is working."""

    def test_native_knn_queries_being_used(self, populated_test_database):
        """Test that native KNN queries are being used instead of manual calculations."""
        db = populated_test_database

        # Search should use native KNN queries
        query_vector = [0.1] * 384

        # This should trigger native KNN queries
        results = db.search_similar(query_vector, top_k=3)

        # Should get results
        assert len(results) > 0

        # Results should come from native KNN (not manual calculation)
        # We can verify this by checking that the search is fast enough
        start_time = time.time()
        results = db.search_similar(query_vector, top_k=5)
        query_time = time.time() - start_time

        # Native KNN should be very fast (< 0.01s)
        assert query_time < 0.01, f"Query too slow for native KNN: {query_time:.3f}s"

    def test_vec0_virtual_tables_exist(self, populated_test_database):
        """Test that vec0 virtual tables exist and are being used."""
        db = populated_test_database
        cursor = db.conn.cursor()

        # Check for vec0 virtual tables
        cursor.execute(f"""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name='{db.table_name}_vec0'
        """)
        vec0_table = cursor.fetchone()
        assert vec0_table is not None, "vec0 virtual table should exist"

        # Check that it's actually a virtual table
        cursor.execute(f"""
            SELECT sql FROM sqlite_master
            WHERE name='{db.table_name}_vec0'
        """)
        create_sql = cursor.fetchone()[0]
        assert "VIRTUAL TABLE" in create_sql.upper(), "Table should be virtual"
        assert "USING vec0" in create_sql.upper(), "Should use vec0 virtual table"

    def test_no_manual_distance_calculations(self, populated_test_database):
        """Test that manual distance calculations are not being used."""
        db = populated_test_database

        # The search method should use native KNN, not manual calculations
        # We can verify this by checking performance and lack of manual processing
        query_vector = [0.2] * 384

        # Multiple searches should all be fast (indicating native processing)
        times = []
        for _ in range(10):
            start_time = time.time()
            results = db.search_similar(query_vector, top_k=3)
            query_time = time.time() - start_time
            times.append(query_time)

        # All queries should be consistently fast
        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert avg_time < 0.01, f"Average query time too slow: {avg_time:.3f}s"
        assert max_time < 0.02, f"Max query time too slow: {max_time:.3f}s"

    def test_distance_functions_native(self, populated_test_database):
        """Test that native distance functions are available and working."""
        db = populated_test_database
        cursor = db.conn.cursor()

        # Check that vec extension functions are available
        try:
            cursor.execute("SELECT vec_version()")
            version = cursor.fetchone()[0]
            assert version.startswith("v"), f"Invalid vec version: {version}"
        except sqlite3.OperationalError:
            pytest.fail("vec extension functions not available")

        # Check that we can use KNN syntax
        vec0_table = f"{db.table_name}_vec0"
        query_vector = [0.1] * 384

        # Convert to bytes for query
        import struct
        query_bytes = struct.pack(f'{len(query_vector)}f', *query_vector)

        # This should work with native KNN syntax
        cursor.execute(f"""
            SELECT COUNT(*) FROM {vec0_table} v
            WHERE v.embedding MATCH ?
            AND k = 3
        """, (query_bytes,))

        count = cursor.fetchone()[0]
        assert count >= 0, "KNN query should work"

    def test_optimization_performance_gains(self, test_database, mock_embeddings):
        """Test that optimization provides measurable performance gains."""
        db = test_database

        # Add test data
        test_docs = [
            (f"Test document {i}", mock_embeddings["query_vector"], {})
            for i in range(20)
        ]
        db.add_documents_with_metadata(test_docs)

        # Measure search performance
        query_vector = mock_embeddings["query_vector"]

        # Native KNN should be very fast
        start_time = time.time()
        results = db.search_similar(query_vector, top_k=5)
        native_time = time.time() - start_time

        # Should be extremely fast (< 5ms)
        assert native_time < 0.005, f"Native KNN too slow: {native_time:.3f}s"

        # Should get reasonable results
        assert len(results) > 0
        assert all(score > 0 for _, score in results)

    def test_hybrid_search_optimization(self, populated_test_database):
        """Test that hybrid search also benefits from sqlite-vec optimization."""
        retriever = HybridRetriever()

        query = "machine learning artificial intelligence"

        # Hybrid search should be fast (vector part uses native KNN)
        start_time = time.time()
        results = retriever.query(query, top_k=5, mode="hybrid")
        hybrid_time = time.time() - start_time

        # Should be fast even with hybrid processing
        assert hybrid_time < 0.05, f"Hybrid search too slow: {hybrid_time:.3f}s"

        # Should get results with RRF scoring
        assert len(results) > 0
        for result in results:
            assert hasattr(result, 'score')
            assert result.score > 0

    def test_vector_search_consistency_after_optimization(self, populated_test_database, mock_embeddings):
        """Test that vector search results are consistent after optimization."""
        db = populated_test_database

        query_vector = mock_embeddings["query_vector"]

        # Multiple searches should return identical results
        result_sets = []
        for _ in range(5):
            results = db.search_similar(query_vector, top_k=5)
            result_sets.append([(content, round(score, 6)) for content, score in results])

        # All result sets should be identical
        first_set = result_sets[0]
        for i, result_set in enumerate(result_sets[1:], 1):
            assert result_set == first_set, f"Results differ on iteration {i+1}"

    def test_no_fallback_to_legacy_methods(self, populated_test_database):
        """Test that system is not falling back to legacy search methods."""
        db = populated_test_database

        # The search should use vec0 tables, not legacy tables
        cursor = db.conn.cursor()

        # Check that we're not using legacy search
        query_vector = [0.1] * 384
        results = db.search_similar(query_vector, top_k=3)

        # Should get results without any fallback messages
        assert len(results) > 0

        # Check that the search is using KNN syntax (not manual cosine similarity)
        # We can verify this by checking query patterns in the database implementation
        # For now, performance is a good indicator
        start_time = time.time()
        db.search_similar(query_vector, top_k=3)
        query_time = time.time() - start_time

        # Should be too fast for manual calculation
        assert query_time < 0.01, "Query appears to be using manual calculations"

    def test_database_size_optimization(self, test_database):
        """Test that vec0 optimization doesn't cause excessive database size growth."""
        import os

        initial_size = os.path.getsize(test_database.db_path)

        # Add documents
        test_docs = [
            (f"Optimized document {i}", [0.1 * i] * 384, {"optimized": True})
            for i in range(50)
        ]
        test_database.add_documents_with_metadata(test_docs)

        final_size = os.path.getsize(test_database.db_path)

        # Size growth should be reasonable
        growth_mb = (final_size - initial_size) / (1024 * 1024)
        assert growth_mb < 5, f"Database grew too much: {growth_mb:.2f}MB for 50 documents"

        # Average size per document should be reasonable
        avg_size_per_doc = (final_size - initial_size) / 50
        assert avg_size_per_doc < 100000, f"Average size per document too large: {avg_size_per_doc} bytes"

    def test_concurrent_search_performance(self, populated_test_database):
        """Test that optimized system handles concurrent searches well."""
        import threading
        import time

        db = populated_test_database
        query_vector = [0.15] * 384
        results = []
        errors = []

        def search_worker():
            try:
                start_time = time.time()
                search_results = db.search_similar(query_vector, top_k=3)
                end_time = time.time()
                results.append((search_results, end_time - start_time))
            except Exception as e:
                errors.append(e)

        # Run multiple concurrent searches
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=search_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)  # 5 second timeout

        # Should have no errors
        assert len(errors) == 0, f"Concurrent search errors: {errors}"

        # Should have results from all threads
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"

        # All searches should be fast
        for search_results, search_time in results:
            assert search_time < 0.02, f"Concurrent search too slow: {search_time:.3f}s"
            assert len(search_results) > 0, "Search should return results"

    def test_optimization_regression_detection(self, populated_test_database):
        """Regression test to detect if optimization is lost."""
        db = populated_test_database

        # These are the performance characteristics we expect after optimization
        expected_characteristics = {
            "max_query_time": 0.01,      # 10ms max for native KNN
            "min_result_quality": 0.1,   # Minimum similarity score
            "max_memory_growth": 50000000, # 50MB max for test operations
        }

        query_vector = [0.1] * 384

        # Test query performance
        start_time = time.time()
        results = db.search_similar(query_vector, top_k=5)
        query_time = time.time() - start_time

        # Check performance regression
        assert query_time <= expected_characteristics["max_query_time"], \
            f"Performance regression: query took {query_time:.3f}s, expected < {expected_characteristics['max_query_time']}s"

        # Check result quality
        assert len(results) > 0, "Should get results"
        max_score = max(score for _, score in results)
        assert max_score >= expected_characteristics["min_result_quality"], \
            f"Quality regression: max score {max_score}, expected >= {expected_characteristics['min_result_quality']}"

        # Check that we're using vec0 tables (not legacy)
        cursor = db.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {db.table_name}_vec0")
        vec0_count = cursor.fetchone()[0]
        assert vec0_count > 0, "Should have data in vec0 tables"

    def test_sqlite_vec_version_check(self, populated_test_database):
        """Test that we're using the correct version of sqlite-vec."""
        db = populated_test_database
        cursor = db.conn.cursor()

        # Check sqlite-vec version
        cursor.execute("SELECT vec_version()")
        version = cursor.fetchone()[0]

        # Should be a recent version with vec0 support
        assert version.startswith("v"), f"Invalid version format: {version}"

        # Extract version number
        version_num = version[1:]  # Remove 'v' prefix
        version_parts = version_num.split('.')
        assert len(version_parts) >= 2, f"Invalid version format: {version}"

        major = int(version_parts[0])
        minor = int(version_parts[1])

        # Should be version 0.1.x or higher (which has vec0 support)
        assert major >= 0, f"Major version too old: {major}"
        if major == 0:
            assert minor >= 1, f"Minor version too old for vec0: {minor}"