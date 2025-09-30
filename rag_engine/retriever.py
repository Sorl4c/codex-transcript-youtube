"""
Retriever module for RAG system.

Provides high-level query interface for semantic search over the vector database.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

from .database import VectorDatabase, SQLiteVecDatabase
from .embedder import Embedder, EmbedderFactory
from .config import DB_PATH


@dataclass
class SearchResult:
    """Represents a single search result with content and similarity score."""
    content: str
    score: float  # Similarity score (lower is better for distance, we'll normalize)

    def __repr__(self):
        preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"SearchResult(score={self.score:.4f}, content='{preview}')"


class SimpleRetriever:
    """
    Simple retriever that performs semantic search over the vector database.

    This is the MVP version - future versions will add hybrid search,
    reranking, and more advanced features.
    """

    def __init__(
        self,
        database: Optional[VectorDatabase] = None,
        embedder: Optional[Embedder] = None
    ):
        """
        Initialize the retriever.

        Args:
            database: Vector database instance. If None, creates SQLiteVecDatabase.
            embedder: Embedder instance. If None, creates default from factory.
        """
        self.database = database or SQLiteVecDatabase(db_path=DB_PATH)
        self.embedder = embedder or EmbedderFactory.create_embedder()

    def query(self, question: str, top_k: int = 5) -> List[SearchResult]:
        """
        Query the vector database with a question.

        Args:
            question: The query string.
            top_k: Number of results to return (default: 5).

        Returns:
            List of SearchResult objects sorted by relevance (most relevant first).
        """
        if not question.strip():
            return []

        # 1. Generate embedding for the question
        question_embedding = self.embedder.embed([question])[0]

        # 2. Search the database
        results = self.database.search_similar(
            query_embedding=question_embedding,
            top_k=top_k
        )

        # 3. Convert to SearchResult objects
        # Note: database returns (content, distance) where lower distance = more similar
        # We'll keep the distance as score for now (could normalize later)
        search_results = [
            SearchResult(content=content, score=distance)
            for content, distance in results
        ]

        return search_results

    def get_stats(self) -> dict:
        """
        Get statistics about the vector database.

        Returns:
            Dictionary with stats like document count.
        """
        return {
            "total_documents": self.database.get_document_count(),
            "embedder_type": type(self.embedder).__name__,
            "database_type": type(self.database).__name__
        }


# Convenience function for quick queries
def query_rag(question: str, top_k: int = 5) -> List[SearchResult]:
    """
    Convenience function to quickly query the RAG system.

    Args:
        question: The query string.
        top_k: Number of results to return.

    Returns:
        List of SearchResult objects.
    """
    retriever = SimpleRetriever()
    return retriever.query(question, top_k=top_k)


if __name__ == "__main__":
    # Quick test
    print("=== Testing SimpleRetriever ===")

    retriever = SimpleRetriever()
    stats = retriever.get_stats()
    print(f"\nDatabase stats: {stats}")

    if stats["total_documents"] > 0:
        test_query = "What is artificial intelligence?"
        print(f"\nTest query: '{test_query}'")

        results = retriever.query(test_query, top_k=3)
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {result.score:.4f}) ---")
            print(result.content[:200] + "..." if len(result.content) > 200 else result.content)
    else:
        print("\nNo documents in database. Run ingestion first:")
        print("  python -m rag_engine.rag_cli ingest transcripts_for_rag/sample_transcript.txt")
