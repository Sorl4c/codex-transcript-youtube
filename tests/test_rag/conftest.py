"""
RAG-specific pytest configuration and fixtures.

This file contains fixtures and configuration specific to the RAG system tests.
These fixtures are available to all RAG test modules.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
from typing import Generator, List, Dict, Any
import hashlib

import pytest

from rag_engine.config import DB_PATH, DB_TABLE_NAME
from rag_engine.database import SQLiteVecDatabase
from rag_engine.embedder import LocalEmbedder
from rag_engine.chunker import TextChunker


@pytest.fixture(scope="function")
def test_database() -> Generator[SQLiteVecDatabase, None, None]:
    """
    Create a temporary SQLite database with vec0 extension for testing.

    This fixture creates a fresh database for each test function,
    ensuring test isolation and preventing test data pollution.
    """
    # Create temporary database file
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db', prefix='rag_test_')

    try:
        # Close the file descriptor so SQLite can use the file
        os.close(temp_db_fd)

        # Create SQLiteVecDatabase with temporary path
        db = SQLiteVecDatabase(db_path=temp_db_path, table_name="test_vector_store")

        yield db

    finally:
        # Cleanup: close database connection and remove temp file
        if 'db' in locals():
            del db  # This will trigger the destructor and close connection

        # Remove the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


@pytest.fixture(scope="session")
def sample_documents() -> List[Dict[str, Any]]:
    """
    Sample documents for testing RAG ingestion and retrieval.

    Returns a list of dictionaries containing test documents with metadata.
    These documents are designed to test various aspects of the RAG system.
    """
    return [
        {
            "id": 1,
            "content": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.",
            "source": "test_ai_document.txt",
            "title": "Introduction to Artificial Intelligence",
            "category": "technology"
        },
        {
            "id": 2,
            "content": "Machine learning is a subfield of artificial intelligence that is based on artificial neural networks with representation learning. The learning can be supervised, semi-supervised or unsupervised. Deep learning architectures have been applied to fields including computer vision, speech recognition, and natural language processing.",
            "source": "test_ml_document.txt",
            "title": "Machine Learning Fundamentals",
            "category": "technology"
        },
        {
            "id": 3,
            "content": "SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine. SQLite is the most used database engine in the world. SQLite is built into all mobile phones and most computers and comes bundled inside countless other applications that people use every day.",
            "source": "test_sqlite_document.txt",
            "title": "SQLite Database Overview",
            "category": "database"
        },
        {
            "id": 4,
            "content": "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They are essential for applications involving similarity search, recommendation systems, and machine learning embeddings. Vector databases use specialized indexing structures like HNSW, IVF, or LSH to enable fast approximate nearest neighbor searches.",
            "source": "test_vector_db_document.txt",
            "title": "Vector Database Concepts",
            "category": "database"
        },
        {
            "id": 5,
            "content": "Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language. It focuses on how to program computers to process and analyze large amounts of natural language data.",
            "source": "test_nlp_document.txt",
            "title": "Natural Language Processing",
            "category": "technology"
        }
    ]


@pytest.fixture(scope="session")
def sample_queries() -> Dict[str, str]:
    """
    Sample queries for testing RAG retrieval functionality.

    Returns a dictionary of categorized queries designed to test different
    aspects of semantic search and retrieval.
    """
    return {
        "ai_basic": "What is artificial intelligence?",
        "ml_concepts": "Explain machine learning and neural networks",
        "database_basics": "What are vector databases?",
        "sqlite_features": "Tell me about SQLite database",
        "nlp_applications": "How is natural language processing used?",
        "similarity_search": "Find information about similarity search",
        "hybrid_query": "machine learning database applications",
        "fuzzy_query": "artifical intelignce misspelled query"
    }


@pytest.fixture(scope="session")
def mock_embeddings() -> Dict[str, List[float]]:
    """
    Mock embedding vectors for testing without actual embedding generation.

    These are pre-computed normalized vectors that simulate embeddings
    from a sentence-transformer model (384 dimensions).
    """
    import random

    # Set seed for reproducible tests
    random.seed(42)

    def generate_normalized_vector(dim: int = 384) -> List[float]:
        """Generate a normalized random vector."""
        vector = [random.gauss(0, 1) for _ in range(dim)]
        magnitude = sum(x * x for x in vector) ** 0.5
        return [x / magnitude for x in vector]

    return {
        "ai_vector": generate_normalized_vector(),
        "ml_vector": generate_normalized_vector(),
        "database_vector": generate_normalized_vector(),
        "sqlite_vector": generate_normalized_vector(),
        "nlp_vector": generate_normalized_vector(),
        "query_vector": generate_normalized_vector(),
    }


@pytest.fixture(scope="function")
def populated_test_database(test_database: SQLiteVecDatabase,
                          sample_documents: List[Dict[str, Any]],
                          mock_embeddings: Dict[str, List[float]]) -> SQLiteVecDatabase:
    """
    Create a test database populated with sample documents and embeddings.

    This fixture sets up a database with test data, making it convenient
    for tests that require pre-populated data.
    """
    # Map documents to embeddings (simulate embedding generation)
    embedding_map = {
        1: mock_embeddings["ai_vector"],
        2: mock_embeddings["ml_vector"],
        3: mock_embeddings["sqlite_vector"],
        4: mock_embeddings["database_vector"],
        5: mock_embeddings["nlp_vector"]
    }

    # Prepare documents with metadata for insertion
    documents_with_metadata = []
    for doc in sample_documents:
        embedding = embedding_map.get(doc["id"], mock_embeddings["query_vector"])

        metadata = {
            "source_document": doc["source"],
            "chunking_strategy": "test",
            "chunk_index": doc["id"] - 1,
            "semantic_title": doc["title"],
            "semantic_summary": f"Test document about {doc['category']}",
            "metadata_json": f'{{"category": "{doc["category"]}", "title": "{doc["title"]}"}}'
        }

        documents_with_metadata.append((doc["content"], embedding, metadata))

    # Add documents to database
    test_database.add_documents_with_metadata(documents_with_metadata)

    return test_database


@pytest.fixture(scope="session")
def test_embedder() -> LocalEmbedder:
    """
    Create a test embedder instance for generating embeddings.

    Returns a LocalEmbedder instance configured for testing.
    """
    return LocalEmbedder()


@pytest.fixture(scope="session")
def test_chunker() -> TextChunker:
    """
    Create a test chunker instance for text chunking.

    Returns a TextChunker instance with small chunks for faster testing.
    """
    return TextChunker(chunk_size=200, chunk_overlap=50, strategy="caracteres")


@pytest.fixture(scope="session")
def rag_performance_thresholds() -> Dict[str, float]:
    """
    Performance thresholds specifically for RAG system tests.

    These thresholds define acceptable performance limits for RAG operations.
    """
    return {
        "max_embedding_generation_time": 0.1,    # seconds
        "max_chunking_time": 0.01,               # seconds per document
        "max_database_insertion_time": 0.05,     # seconds per document
        "max_vector_search_time": 0.01,          # seconds
        "max_hybrid_search_time": 0.05,          # seconds
        "max_knn_query_time": 0.005,             # seconds
        "min_similarity_threshold": 0.3,         # minimum similarity score
        "max_memory_usage_mb": 100,              # MB for test operations
    }


@pytest.fixture
def temp_rag_files(temp_dir: Path) -> Dict[str, Path]:
    """
    Create temporary RAG-related files for testing.

    Returns a dictionary containing paths to temporary files
    used in RAG system testing.
    """
    files = {}

    # Create sample transcript file
    transcript_file = temp_dir / "test_transcript.txt"
    transcript_file.write_text("""This is a test transcript file for RAG ingestion testing.

Machine learning algorithms are designed to find patterns in data. These algorithms can be
supervised, unsupervised, or semi-supervised. Deep learning, a subset of machine learning,
uses neural networks with multiple layers to progressively extract higher-level features
from raw input.

Natural language processing enables computers to understand and generate human language.
Modern NLP systems use transformer architectures and large language models to achieve
impressive results in tasks like translation, summarization, and question answering.
""")
    files["transcript"] = transcript_file

    # Create VTT file for testing
    vtt_file = temp_dir / "test_transcript.vtt"
    vtt_file.write_text("""WEBVTT

00:00:00.000 --> 00:00:05.000
This is the first subtitle for testing purposes.

00:00:05.000 --> 00:00:10.000
This is the second subtitle containing information about machine learning.

00:00:10.000 --> 00:00:15.000
The third subtitle discusses natural language processing concepts.
""")
    files["vtt"] = vtt_file

    # Create empty file for edge case testing
    empty_file = temp_dir / "empty.txt"
    empty_file.write_text("")
    files["empty"] = empty_file

    return files


@pytest.fixture
def rag_test_config() -> Dict[str, Any]:
    """
    Test configuration for RAG system components.

    Returns a dictionary containing configuration values
    specifically for testing RAG components.
    """
    return {
        "test_table_name": "test_vector_store",
        "test_chunk_size": 200,
        "test_chunk_overlap": 50,
        "test_top_k": 3,
        "test_similarity_threshold": 0.5,
        "test_embedding_dim": 384,  # all-MiniLM-L6-v2 dimension
        "test_batch_size": 10,
    }


# Helper function for generating test file hashes
def generate_file_hash(file_path: Path) -> str:
    """
    Generate a consistent hash for a test file.

    Used in tests to verify file tracking and change detection.
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()