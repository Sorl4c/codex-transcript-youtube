"""
Tests for hybrid retriever with RRF (Reciprocal Rank Fusion).

This module tests the hybrid search functionality that combines
vector search and BM25 keyword search using RRF.
"""

import pytest
import time
from typing import List, Dict, Any

from rag_engine.hybrid_retriever import HybridRetriever
from rag_engine.retriever import SimpleRetriever


class TestHybridRetriever:
    """Test hybrid retriever functionality."""

    @pytest.fixture
    def hybrid_retriever(self, populated_test_database):
        """Create a hybrid retriever instance with populated test database."""
        return HybridRetriever()

    @pytest.fixture
    def simple_retriever(self, populated_test_database):
        """Create a simple retriever for comparison."""
        return SimpleRetriever()

    def test_hybrid_retriever_initialization(self, hybrid_retriever):
        """Test that hybrid retriever initializes correctly."""
        assert hybrid_retriever is not None
        assert hasattr(hybrid_retriever, 'query')

    def test_hybrid_search_basic(self, hybrid_retriever, sample_queries):
        """Test basic hybrid search functionality."""
        query = sample_queries["ai_basic"]

        start_time = time.time()
        results = hybrid_retriever.query(query, top_k=3, mode="hybrid")
        query_time = time.time() - start_time

        # Should return results
        assert len(results) > 0
        assert len(results) <= 3

        # Results should have content and scores
        for result in results:
            assert hasattr(result, 'content')
            assert hasattr(result, 'score')
            assert hasattr(result, 'vector_score') or hasattr(result, 'bm25_score')
            assert result.content.strip() != ""

        # Hybrid search should be reasonably fast
        assert query_time < 0.1, f"Hybrid search too slow: {query_time:.3f}s"

    def test_vector_vs_hybrid_vs_keyword(self, hybrid_retriever, simple_retriever, sample_queries):
        """Test differences between vector, hybrid, and keyword search modes."""
        query = sample_queries["ml_concepts"]

        # Vector search
        vector_results = simple_retriever.query(query, top_k=3)

        # Hybrid search
        hybrid_results = hybrid_retriever.query(query, top_k=3, mode="hybrid")

        # Keyword search
        keyword_results = hybrid_retriever.query(query, top_k=3, mode="keyword")

        # All should return results
        assert len(vector_results) > 0
        assert len(hybrid_results) > 0
        assert len(keyword_results) > 0

        # Results should be different (at least somewhat)
        vector_contents = [r.content for r in vector_results]
        hybrid_contents = [r.content for r in hybrid_results]
        keyword_contents = [r.content for r in keyword_results]

        # Hybrid should be different from pure vector or keyword
        # (though there might be some overlap)
        assert len(set(vector_contents) & set(hybrid_contents)) < len(vector_contents)
        assert len(set(keyword_contents) & set(hybrid_contents)) < len(keyword_contents)

    def test_hybrid_search_with_rrf_scoring(self, hybrid_retriever, sample_queries):
        """Test that RRF (Reciprocal Rank Fusion) scoring works correctly."""
        query = sample_queries["hybrid_query"]
        results = hybrid_retriever.query(query, top_k=5, mode="hybrid")

        # Results should have rank information from both vector and BM25
        for result in results:
            if hasattr(result, 'vector_rank'):
                assert isinstance(result.vector_rank, int)
                assert result.vector_rank >= 1
            if hasattr(result, 'bm25_rank'):
                assert isinstance(result.bm25_rank, int)
                assert result.bm25_rank >= 1

        # Results should be sorted by hybrid score (descending)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_hybrid_search_different_top_k(self, hybrid_retriever, sample_queries):
        """Test hybrid search with different top_k values."""
        query = sample_queries["database_basics"]

        for k in [1, 2, 3, 5, 10]:
            results = hybrid_retriever.query(query, top_k=k, mode="hybrid")

            # Should return at most k results
            assert len(results) <= k

            # Results should be properly scored
            for result in results:
                assert 0 <= result.score <= 1  # Scores should be normalized

    def test_empty_query_handling(self, hybrid_retriever):
        """Test handling of empty or whitespace queries."""
        empty_queries = ["", "   ", "\t", "\n"]

        for query in empty_queries:
            # Should handle gracefully (either return empty or raise clear error)
            try:
                results = hybrid_retriever.query(query, top_k=3, mode="hybrid")
                # If it returns results, they should be valid
                for result in results:
                    assert hasattr(result, 'content')
                    assert hasattr(result, 'score')
            except ValueError as e:
                # Should raise a clear error about empty query
                assert "empty" in str(e).lower() or "query" in str(e).lower()

    def test_hybrid_search_performance(self, hybrid_retriever, sample_queries, rag_performance_thresholds):
        """Test hybrid search performance against thresholds."""
        query = sample_queries["nlp_applications"]

        # Measure multiple queries for consistency
        times = []
        for _ in range(3):
            start_time = time.time()
            results = hybrid_retriever.query(query, top_k=5, mode="hybrid")
            query_time = time.time() - start_time
            times.append(query_time)

            # Each query should meet performance threshold
            assert query_time < rag_performance_thresholds["max_hybrid_search_time"]

        # Average should also be within threshold
        avg_time = sum(times) / len(times)
        assert avg_time < rag_performance_thresholds["max_hybrid_search_time"]

    def test_hybrid_search_consistency(self, hybrid_retriever, sample_queries):
        """Test that hybrid search returns consistent results."""
        query = sample_queries["ai_basic"]

        # Run same query multiple times
        result_sets = []
        for _ in range(3):
            results = hybrid_retriever.query(query, top_k=3, mode="hybrid")
            result_sets.append([(r.content, r.score) for r in results])

        # Results should be consistent across runs
        for i in range(1, len(result_sets)):
            assert len(result_sets[i]) == len(result_sets[0])

            for j, (content1, score1) in enumerate(result_sets[0]):
                content2, score2 = result_sets[i][j]
                assert content1 == content2
                # Scores should be very similar (allowing for tiny floating point differences)
                assert abs(score1 - score2) < 1e-6

    def test_hybrid_search_result_attributes(self, hybrid_retriever, sample_queries):
        """Test that hybrid search results have all required attributes."""
        query = sample_queries["sqlite_features"]
        results = hybrid_retriever.query(query, top_k=3, mode="hybrid")

        for result in results:
            # Core attributes
            assert hasattr(result, 'content')
            assert hasattr(result, 'score')

            # Content should be a non-empty string
            assert isinstance(result.content, str)
            assert result.content.strip() != ""

            # Score should be a float in reasonable range
            assert isinstance(result.score, (float, int))
            assert 0 <= result.score <= 1

            # Should have either vector or BM25 scores (or both)
            has_vector = hasattr(result, 'vector_score')
            has_bm25 = hasattr(result, 'bm25_score')
            assert has_vector or has_bm25, "Result should have either vector_score or bm25_score"

            # If present, individual scores should be valid
            if has_vector:
                assert isinstance(result.vector_score, (float, int))
            if has_bm25:
                assert isinstance(result.bm25_score, (float, int))

    def test_keyword_search_mode(self, hybrid_retriever, sample_queries):
        """Test keyword-only search mode."""
        query = sample_queries["similarity_search"]

        results = hybrid_retriever.query(query, top_k=3, mode="keyword")

        # Should return results
        assert len(results) > 0

        # Results should have BM25 scores
        for result in results:
            assert hasattr(result, 'bm25_score')
            assert hasattr(result, 'bm25_rank')
            assert result.bm25_score > 0
            assert result.bm25_rank >= 1

        # Results should be sorted by BM25 score (descending)
        scores = [r.bm25_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_hybrid_search_fallback(self, hybrid_retriever):
        """Test hybrid search fallback behavior."""
        # Test with query that should return minimal results
        obscure_query = "xyz123 nonexistent term"

        results = hybrid_retriever.query(obscure_query, top_k=3, mode="hybrid")

        # Should either return empty results or handle gracefully
        assert isinstance(results, list)
        for result in results:
            assert hasattr(result, 'content')
            assert hasattr(result, 'score')

    def test_query_type_variations(self, hybrid_retriever):
        """Test different types of queries (short, long, misspelled)."""
        query_variations = [
            "AI",                    # Short query
            "artificial intelligence machine learning deep neural networks",  # Long query
            "artifical intelignce",  # Misspelled query
            "machine learning AND database",  # Complex query
            "What is natural language processing?",  # Question format
        ]

        for query in query_variations:
            try:
                results = hybrid_retriever.query(query, top_k=3, mode="hybrid")

                # Should handle different query types gracefully
                assert isinstance(results, list)

                # If results are returned, they should be valid
                for result in results:
                    assert hasattr(result, 'content')
                    assert hasattr(result, 'score')
                    assert result.content.strip() != ""

            except Exception as e:
                # If it fails, it should be a clear, expected error
                assert not isinstance(e, AttributeError), f"Unexpected error for query '{query}': {e}"

    def test_hybrid_vs_pure_vector_comparison(self, hybrid_retriever, simple_retriever, sample_queries):
        """Compare results between hybrid and pure vector search."""
        query = sample_queries["ml_concepts"]

        # Get results from both methods
        vector_results = simple_retriever.query(query, top_k=5)
        hybrid_results = hybrid_retriever.query(query, top_k=5, mode="hybrid")

        # Both should return results
        assert len(vector_results) > 0
        assert len(hybrid_results) > 0

        # Extract content for comparison
        vector_contents = [r.content for r in vector_results]
        hybrid_contents = [r.content for r in hybrid_results]

        # There should be some difference in ranking or content
        # (Hybrid should incorporate BM25 signals)
        if vector_contents == hybrid_contents:
            # If contents are the same, scores should be different
            vector_scores = [r.score for r in vector_results]
            hybrid_scores = [r.score for r in hybrid_results]

            # At least some scores should be different
            score_differences = [abs(v - h) for v, h in zip(vector_scores, hybrid_scores)]
            assert any(diff > 0.01 for diff in score_differences), "Hybrid should produce different scores than pure vector"

    def test_search_mode_parameter_validation(self, hybrid_retriever, sample_queries):
        """Test validation of search mode parameter."""
        query = sample_queries["ai_basic"]

        # Valid modes should work
        valid_modes = ["vector", "keyword", "hybrid"]
        for mode in valid_modes:
            try:
                results = hybrid_retriever.query(query, top_k=3, mode=mode)
                assert isinstance(results, list)
            except Exception as e:
                pytest.fail(f"Valid mode '{mode}' should not raise exception: {e}")

        # Invalid mode should raise appropriate error
        with pytest.raises((ValueError, TypeError)):
            hybrid_retriever.query(query, top_k=3, mode="invalid_mode")