"""
Hybrid retriever combining vector (semantic) and keyword (BM25) search.

This module implements a hybrid search strategy that combines:
1. Vector search (semantic similarity via embeddings)
2. Keyword search (BM25 lexical matching)
3. Reciprocal Rank Fusion (RRF) for score combination
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re

from rank_bm25 import BM25Okapi

from .retriever import SimpleRetriever, SearchResult
from .database import VectorDatabase, SQLiteVecDatabase
from .embedder import Embedder, EmbedderFactory
from .config import DB_PATH


@dataclass
class HybridSearchResult(SearchResult):
    """
    Extended search result with provenance tracking.

    Attributes:
        content: The document content
        score: Final hybrid score (or single-method score)
        vector_score: Score from vector search (None if not used)
        bm25_score: Score from BM25 search (None if not used)
        vector_rank: Rank in vector results (None if not used)
        bm25_rank: Rank in BM25 results (None if not used)
    """
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    vector_rank: Optional[int] = None
    bm25_rank: Optional[int] = None


class HybridRetriever(SimpleRetriever):
    """
    Hybrid retriever combining vector and BM25 keyword search.

    Supports three modes:
    - 'vector': Pure semantic search via embeddings (default SimpleRetriever)
    - 'keyword': Pure BM25 keyword search
    - 'hybrid': Combination of both via Reciprocal Rank Fusion (RRF)
    """

    def __init__(
        self,
        database: Optional[VectorDatabase] = None,
        embedder: Optional[Embedder] = None,
        rrf_k: int = 60
    ):
        """
        Initialize the hybrid retriever.

        Args:
            database: Vector database instance. If None, creates SQLiteVecDatabase.
            embedder: Embedder instance. If None, creates default from factory.
            rrf_k: RRF constant (default 60, from original RRF paper)
        """
        super().__init__(database, embedder)
        self.rrf_k = rrf_k
        self._corpus = None  # Cached corpus for BM25
        self._bm25 = None    # Cached BM25 model
        self._doc_ids = None # Document IDs corresponding to corpus

    def _load_corpus(self):
        """Load all documents from database for BM25 indexing."""
        if self._corpus is not None:
            return  # Already loaded

        # Fetch all documents from the database
        all_docs = self.database.get_all_documents()

        if not all_docs:
            self._corpus = []
            self._bm25 = None
            self._doc_ids = []
            return

        # Tokenize documents for BM25
        self._corpus = []
        self._doc_ids = []

        for doc_id, content in all_docs:
            tokens = self._tokenize(content)
            self._corpus.append(tokens)
            self._doc_ids.append(doc_id)

        # Create BM25 index
        if self._corpus:
            self._bm25 = BM25Okapi(self._corpus)

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization: lowercase + split on non-alphanumeric.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Convert to lowercase and split on non-word characters
        tokens = re.findall(r'\w+', text.lower())
        return tokens

    def _bm25_search(self, query: str, top_k: int = 5) -> List[HybridSearchResult]:
        """
        Perform BM25 keyword search.

        Args:
            query: Query string
            top_k: Number of results to return

        Returns:
            List of HybridSearchResult objects sorted by BM25 score
        """
        self._load_corpus()

        if not self._bm25 or not self._corpus:
            return []

        # Tokenize query
        query_tokens = self._tokenize(query)

        # Get BM25 scores for all documents
        scores = self._bm25.get_scores(query_tokens)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        # Build results
        results = []
        for rank, idx in enumerate(top_indices):
            doc_id = self._doc_ids[idx]
            content = self.database.get_document_by_id(doc_id)
            score = float(scores[idx])

            result = HybridSearchResult(
                content=content,
                score=score,
                bm25_score=score,
                bm25_rank=rank + 1
            )
            results.append(result)

        return results

    def _vector_search(self, query: str, top_k: int = 5) -> List[HybridSearchResult]:
        """
        Perform vector semantic search (wrapper around parent method).

        Args:
            query: Query string
            top_k: Number of results to return

        Returns:
            List of HybridSearchResult objects sorted by vector similarity
        """
        base_results = super().query(query, top_k)

        # Convert to HybridSearchResult with vector scores
        hybrid_results = []
        for rank, result in enumerate(base_results):
            hybrid_result = HybridSearchResult(
                content=result.content,
                score=result.score,
                vector_score=result.score,
                vector_rank=rank + 1
            )
            hybrid_results.append(hybrid_result)

        return hybrid_results

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[HybridSearchResult],
        bm25_results: List[HybridSearchResult],
        top_k: int
    ) -> List[HybridSearchResult]:
        """
        Combine vector and BM25 results using Reciprocal Rank Fusion (RRF).

        RRF formula: score(d) = sum(1 / (k + rank(d)))
        where k is a constant (default 60) and rank(d) is the rank in each result list.

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            top_k: Number of final results to return

        Returns:
            List of HybridSearchResult objects sorted by RRF score
        """
        # Build a dictionary: content -> HybridSearchResult
        result_map: Dict[str, HybridSearchResult] = {}

        # Add vector results
        for rank, result in enumerate(vector_results, start=1):
            rrf_score = 1.0 / (self.rrf_k + rank)
            result_map[result.content] = HybridSearchResult(
                content=result.content,
                score=rrf_score,
                vector_score=result.vector_score,
                vector_rank=rank
            )

        # Add/update with BM25 results
        for rank, result in enumerate(bm25_results, start=1):
            rrf_score = 1.0 / (self.rrf_k + rank)

            if result.content in result_map:
                # Document appears in both results - combine scores
                existing = result_map[result.content]
                existing.score += rrf_score
                existing.bm25_score = result.bm25_score
                existing.bm25_rank = rank
            else:
                # Document only in BM25 results
                result_map[result.content] = HybridSearchResult(
                    content=result.content,
                    score=rrf_score,
                    bm25_score=result.bm25_score,
                    bm25_rank=rank
                )

        # Sort by RRF score and return top-k
        sorted_results = sorted(result_map.values(), key=lambda x: x.score, reverse=True)
        return sorted_results[:top_k]

    def query(
        self,
        question: str,
        top_k: int = 5,
        mode: str = 'hybrid'
    ) -> List[HybridSearchResult]:
        """
        Query with hybrid, vector, or keyword search.

        Args:
            question: Query string
            top_k: Number of results to return
            mode: Search mode - 'hybrid', 'vector', or 'keyword'

        Returns:
            List of HybridSearchResult objects sorted by relevance

        Raises:
            ValueError: If mode is not one of 'hybrid', 'vector', 'keyword'
        """
        if not question.strip():
            return []

        mode = mode.lower()

        if mode == 'vector':
            return self._vector_search(question, top_k)

        elif mode == 'keyword':
            return self._bm25_search(question, top_k)

        elif mode == 'hybrid':
            # Fetch more results from each method for better RRF
            fetch_k = min(top_k * 3, 20)

            vector_results = self._vector_search(question, fetch_k)
            bm25_results = self._bm25_search(question, fetch_k)

            # Combine with RRF
            hybrid_results = self._reciprocal_rank_fusion(
                vector_results,
                bm25_results,
                top_k
            )

            return hybrid_results

        else:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'vector', 'keyword', or 'hybrid'.")


# Convenience function for quick queries
def query_hybrid(
    question: str,
    top_k: int = 5,
    mode: str = 'hybrid',
    rrf_k: int = 60
) -> List[HybridSearchResult]:
    """
    Convenience function to quickly query with hybrid search.

    Args:
        question: Query string
        top_k: Number of results to return
        mode: Search mode - 'hybrid', 'vector', or 'keyword'
        rrf_k: RRF constant (default 60)

    Returns:
        List of HybridSearchResult objects
    """
    retriever = HybridRetriever(rrf_k=rrf_k)
    return retriever.query(question, top_k=top_k, mode=mode)


if __name__ == "__main__":
    # Quick test
    print("=== Testing HybridRetriever ===")

    retriever = HybridRetriever()
    stats = retriever.get_stats()
    print(f"\nDatabase stats: {stats}")

    if stats["total_documents"] > 0:
        test_query = "ejercicios para triceps"
        print(f"\nTest query: '{test_query}'\n")

        for mode in ['vector', 'keyword', 'hybrid']:
            print(f"\n--- Mode: {mode.upper()} ---")
            results = retriever.query(test_query, top_k=3, mode=mode)
            print(f"Found {len(results)} results:\n")

            for i, result in enumerate(results, 1):
                preview = result.content[:150] + "..." if len(result.content) > 150 else result.content
                print(f"Result {i} (score: {result.score:.4f})")

                if result.vector_rank:
                    print(f"  Vector: rank={result.vector_rank}, score={result.vector_score:.4f}")
                if result.bm25_rank:
                    print(f"  BM25: rank={result.bm25_rank}, score={result.bm25_score:.4f}")

                print(f"  Content: {preview}\n")
    else:
        print("\nNo documents in database. Run ingestion first.")
