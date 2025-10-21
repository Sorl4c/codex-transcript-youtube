"""
Global pytest configuration for all tests.

This file contains shared fixtures, configuration, and utilities
that are available to all test modules in the project.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Any

import pytest

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp(prefix="rag_test_"))
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for tests."""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("Test content for file operations.")
    try:
        yield file_path
    finally:
        if file_path.exists():
            file_path.unlink()


@pytest.fixture(scope="session")
def test_env_vars() -> dict:
    """Provide test environment variables."""
    return {
        "TESTING": "true",
        "RAG_TEST_MODE": "true",
        "LOG_LEVEL": "DEBUG",
    }


@pytest.fixture(autouse=True)
def setup_test_env(test_env_vars: dict) -> Generator[None, None, None]:
    """Set up test environment variables for all tests."""
    original_env = {}

    # Store original values and set test values
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        yield
    finally:
        # Restore original values
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


@pytest.fixture(scope="session")
def sample_text_data() -> dict[str, str]:
    """Sample text data for testing various components."""
    return {
        "short_text": "This is a short text document for testing purposes.",
        "medium_text": """
        Artificial intelligence (AI) is intelligence demonstrated by machines,
        in contrast to the natural intelligence displayed by humans and animals.
        Leading AI textbooks define the field as the study of 'intelligent agents':
        any device that perceives its environment and takes actions that maximize
        its chance of successfully achieving its goals.

        Machine learning is a subfield of artificial intelligence that is based on
        artificial neural networks with representation learning. The learning can be
        supervised, semi-supervised or unsupervised.
        """.strip(),
        "long_text": """
        Deep learning is a subfield of machine learning that is based on artificial
        neural networks with representation learning. The learning can be supervised,
        semi-supervised or unsupervised. Deep learning architectures such as deep
        neural networks, deep belief networks, recurrent neural networks and
        convolutional neural networks have been applied to fields including computer
        vision, machine vision, speech recognition, natural language processing,
        audio recognition, social network filtering, machine translation, bioinformatics,
        drug design, medical image analysis, material inspection and board games programs,
        where they have produced results comparable to and in some cases superior
        to human experts.

        Artificial neural networks (ANNs) were inspired by information processing and
        distributed communication nodes in biological systems. ANNs have various differences
        from biological brains. Specifically, neural networks tend to be static and symbolic,
        while the biological brain of most living organisms is dynamic (plastic) and analog.
        """.strip(),
    }


@pytest.fixture
def performance_thresholds() -> dict[str, float]:
    """Performance thresholds for benchmarking tests."""
    return {
        "max_embedding_time": 0.1,  # seconds
        "max_query_time": 0.05,     # seconds
        "max_ingestion_time": 1.0,  # seconds per document
        "max_memory_usage": 500,    # MB for 1000 documents
        "min_similarity_score": 0.3, # minimum acceptable similarity
    }


@pytest.fixture
def mock_embedding_vector() -> list[float]:
    """A mock embedding vector for testing."""
    # This is a normalized 384-dimensional vector (same as all-MiniLM-L6-v2)
    import random
    random.seed(42)  # For reproducible tests
    vector = [random.gauss(0, 1) for _ in range(384)]

    # Normalize the vector
    magnitude = sum(x * x for x in vector) ** 0.5
    return [x / magnitude for x in vector]


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "requires_llm: mark test as requiring LLM access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add performance marker to tests in performance directory
        if "test_performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)

        # Add integration marker to tests in integration directory
        elif "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add regression marker to tests in regression directory
        elif "test_regression" in str(item.fspath):
            item.add_marker(pytest.mark.regression)

        # Add integration marker to PostgreSQL tests
        elif "postgresql" in str(item.fspath).lower() or "rag" in str(item.fspath).lower():
            item.add_marker(pytest.mark.integration)


# PostgreSQL RAG Specific Fixtures
@pytest.fixture(scope="session")
def postgres_config():
    """Configuración PostgreSQL para tests"""
    return {
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB", "rag_experiments"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "rag_user"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "rag_password_2025"),
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
        "EMBEDDING_DIM": "384",
        "POSTGRES_MIN_CONNECTIONS": "1",
        "POSTGRES_MAX_CONNECTIONS": "3",
        "POSTGRES_TIMEOUT": "10"
    }


@pytest.fixture(scope="function")
def rag_database(postgres_config):
    """Base de datos PostgreSQL RAG limpia para cada test"""
    try:
        from second_brain.plan.postgresql_database_experimental import PostgreSQLVectorDatabase

        db = PostgreSQLVectorDatabase()

        # Limpiar datos antes de cada test
        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM document_embeddings")
                cursor.execute("DELETE FROM documents")
                conn.commit()

        yield db

        # Limpiar después de cada test
        with db.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM document_embeddings")
                cursor.execute("DELETE FROM documents")
                conn.commit()

        db.close()

    except Exception as e:
        pytest.skip(f"No se puede conectar a PostgreSQL: {e}")


@pytest.fixture(scope="session")
def sample_rag_chunks():
    """Dataset de prueba RAG consistente"""
    import hashlib

    chunks = [
        {
            "content": "El Docker compose es una herramienta para definir y ejecutar aplicaciones Docker múltiples contenedores. Se utiliza un archivo YAML para configurar los servicios de la aplicación.",
            "source_document": "docker_guide.md",
            "chunk_index": 0,
            "semantic_title": "Docker Compose Overview",
            "semantic_summary": "Introducción a Docker Compose para orquestación de contenedores"
        },
        {
            "content": "Los embeddings son representaciones vectoriales de texto en un espacio multidimensional. Se utilizan para encontrar similitud semántica entre diferentes fragmentos de texto mediante cálculo matemático.",
            "source_document": "ml_basics.md",
            "chunk_index": 1,
            "semantic_title": "Vector Embeddings",
            "semantic_summary": "Conceptos fundamentales de embeddings vectoriales para similitud semántica"
        },
        {
            "content": "PostgreSQL con pgvector permite almacenar y consultar vectores de alta dimensionalidad eficientemente. Soporta operaciones de similitud de coseno y distancia euclidiana.",
            "source_document": "database_guide.md",
            "chunk_index": 2,
            "semantic_title": "PostgreSQL Vector Database",
            "semantic_summary": "PostgreSQL con extensión pgvector para almacenamiento y búsqueda vectorial"
        },
        {
            "content": "El sistema RAG (Retrieval-Augmented Generation) combina recuperación de información con generación de lenguaje para mejorar la precisión de las respuestas utilizando contexto relevante.",
            "source_document": "rag_system.md",
            "chunk_index": 3,
            "semantic_title": "RAG System Overview",
            "semantic_summary": "Arquitectura RAG para combinar retrieval y generation en IA"
        }
    ]

    # Agregar source_hash a cada chunk
    for chunk in chunks:
        chunk["source_hash"] = hashlib.md5(chunk["content"].encode('utf-8')).hexdigest()

    return chunks


@pytest.fixture(scope="session")
def sample_embeddings_384():
    """Embeddings de prueba simulados (384 dimensiones)"""
    import random

    random.seed(42)  # Para reproducibilidad
    embeddings = []

    for i in range(4):  # 4 chunks
        # Generar embedding aleatorio pero consistente
        embedding = [random.uniform(-1, 1) for _ in range(384)]
        embeddings.append(embedding)

    return embeddings


@pytest.fixture(scope="function")
def populated_rag_database(rag_database, sample_rag_chunks, sample_embeddings_384):
    """Base de datos RAG con datos de prueba"""
    db = rag_database

    # Insertar datos de prueba
    documents = []
    for i, (chunk, embedding) in enumerate(zip(sample_rag_chunks, sample_embeddings_384)):
        metadata = {
            "source_hash": chunk["source_hash"],
            "source_document": chunk["source_document"],
            "chunking_strategy": "test",
            "chunk_index": chunk["chunk_index"],
            "char_start": i * 100,
            "char_end": (i + 1) * 100 - 1,
            "semantic_title": chunk["semantic_title"],
            "semantic_summary": chunk["semantic_summary"],
            "semantic_overlap": "",
            "additional_metadata": {
                "test_data": True,
                "test_id": i,
                "fixture_generated": True
            }
        }

        documents.append((chunk["content"], embedding, metadata))

    db.add_documents_with_metadata(documents)

    return db


@pytest.fixture(scope="session")
def rag_test_queries():
    """Queries de prueba para validación de búsqueda RAG"""
    return [
        {
            "query": "Docker compose para contenedores",
            "expected_min_similarity": 0.5,
            "should_match": ["docker"]
        },
        {
            "query": "representaciones vectoriales embeddings",
            "expected_min_similarity": 0.5,
            "should_match": ["embed", "vector"]
        },
        {
            "query": "PostgreSQL base de datos vectorial",
            "expected_min_similarity": 0.5,
            "should_match": ["postgresql", "database"]
        },
        {
            "query": "sistema RAG generation",
            "expected_min_similarity": 0.5,
            "should_match": ["rag", "generation"]
        },
        {
            "query": "consulta completamente irrelevante al sistema",
            "expected_min_similarity": 0.0,
            "should_match": []
        }
    ]


@pytest.fixture(scope="session")
def rag_performance_thresholds():
    """Umbrales de performance para tests RAG"""
    return {
        "max_search_time_ms": 50,
        "max_ingestion_time_per_doc": 0.1,
        "min_similarity_threshold": 0.3,
        "max_memory_usage_mb": 200,
        "max_embedding_generation_time": 0.5
    }