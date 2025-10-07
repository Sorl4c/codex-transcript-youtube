"""
Module for handling the vector database operations.

Provides an abstraction layer for the database, allowing for different
backend implementations (e.g., SQLite, PostgreSQL).
"""

# First try to import pysqlite3, which generally has better compatibility
# with extensions. Fall back to standard sqlite3 if not available.
try:
    import pysqlite3 as sqlite3
    print("Using pysqlite3 module for better extension compatibility")
except ImportError:
    import sqlite3
    print(f"Using standard sqlite3 module, version {sqlite3.sqlite_version}")
    # Check if the sqlite version is adequate for sqlite-vec
    import pkg_resources
    if pkg_resources.parse_version(sqlite3.sqlite_version) < pkg_resources.parse_version("3.41.0"):
        print("WARNING: Your SQLite version is older than 3.41.0, which may cause issues with sqlite-vec")
        print("Consider installing pysqlite3-binary: pip install pysqlite3-binary")

from abc import ABC, abstractmethod
from typing import List, Tuple
import json
import sys

from .config import DB_PATH, DB_TABLE_NAME

# Attempt to load the sqlite-vec extension
try:
    import sqlite_vec
except ImportError:
    print("sqlite-vec not found. Please install it with: pip install sqlite-vec")
    sqlite_vec = None

class VectorDatabase(ABC):
    """Abstract base class for a vector database."""

    @abstractmethod
    def add_documents(self, documents: List[Tuple[str, List[float]]]):
        """
        Adds documents and their embeddings to the database.

        Args:
            documents (List[Tuple[str, List[float]]]): A list of tuples,
                where each tuple contains the text chunk and its corresponding embedding.
        """
        pass

    @abstractmethod
    def get_document_count(self) -> int:
        """Returns the total number of documents in the database."""
        pass


def init_sqlite_vec(conn: sqlite3.Connection):
    """
    Initializes and registers the sqlite-vec extension for the given connection.
    This is a more robust way to ensure the extension is loaded.
    """
    if not sqlite_vec:
        raise RuntimeError("sqlite-vec extension is not installed or could not be loaded.")
    
    # Enable loading extensions
    try:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        
        # Verify that the extension loaded correctly
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT vec_version()")
            version = cursor.fetchone()[0]
            print(f"sqlite-vec extension loaded successfully, version: {version}")
        except sqlite3.OperationalError:
            print("WARNING: Could not verify sqlite-vec version, but extension loading didn't fail")
            print("This might indicate an incomplete installation")
        finally:
            conn.enable_load_extension(False)
            
    except Exception as e:
        print(f"ERROR: Failed to load sqlite-vec extension: {e}")
        print("This might be due to:")
        if sys.platform == 'darwin':
            print("  - Using macOS system Python (try using Homebrew Python instead)")
        print("  - Insufficient permissions to load extensions")
        print("  - Incompatible SQLite version")
        print("  - Corrupted sqlite-vec installation")
        print("\nTry: pip install pysqlite3-binary sqlite-vec --force-reinstall")
        raise


class SQLiteVecDatabase(VectorDatabase):
    """Vector database implementation using SQLite with the sqlite-vec extension."""

    def __init__(self, db_path: str = DB_PATH, table_name: str = DB_TABLE_NAME):
        """
        Initializes the SQLiteVecDatabase.

        Args:
            db_path (str): The path to the SQLite database file.
            table_name (str): The name of the table to store vectors.
        """
        if not sqlite_vec:
            raise RuntimeError("sqlite-vec extension is not installed or could not be loaded.")
        
        self.db_path = db_path
        self.table_name = table_name
        self.conn = sqlite3.connect(self.db_path)
        # The init function handles loading the extension in a robust way
        init_sqlite_vec(self.conn)
        print(f"Database connection established to {self.db_path}")

    def _create_table_if_not_exists(self, vector_dim: int):
        """
        Creates the vector store table if it doesn't already exist.
        Uses a regular table with BLOB column for vectors instead of virtual tables.

        Schema v2 includes metadata for chunking strategy tracking and agentic metadata.

        Args:
            vector_dim (int): The dimension of the vectors to be stored.
        """
        cursor = self.conn.cursor()
        # Check if the table already exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'")
        if cursor.fetchone() is None:
            print(f"Creating new table '{self.table_name}' (schema v2) with vector dimension {vector_dim}.")

            # Create a regular table with BLOB column for vectors + metadata columns
            cursor.execute(f"""
                CREATE TABLE {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source_document TEXT,
                    source_hash TEXT,
                    chunking_strategy TEXT NOT NULL DEFAULT 'unknown',
                    chunk_index INTEGER,
                    char_start INTEGER,
                    char_end INTEGER,
                    semantic_title TEXT,
                    semantic_summary TEXT,
                    semantic_overlap TEXT,
                    embedding BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata_json TEXT
                )
            """)

            # Create indices for faster searches
            cursor.execute(f"""
                CREATE INDEX idx_{self.table_name}_content ON {self.table_name}(content)
            """)
            cursor.execute(f"""
                CREATE INDEX idx_{self.table_name}_strategy ON {self.table_name}(chunking_strategy)
            """)
            cursor.execute(f"""
                CREATE INDEX idx_{self.table_name}_source ON {self.table_name}(source_document)
            """)
            cursor.execute(f"""
                CREATE INDEX idx_{self.table_name}_hash ON {self.table_name}(source_hash)
            """)

            print(f"Table '{self.table_name}' (schema v2) created successfully with metadata columns.")
            self.conn.commit()
        else:
            print(f"Table '{self.table_name}' already exists.")

    def add_documents(self, documents: List[Tuple[str, List[float]]]):
        """
        Adds a batch of documents to the SQLite database (legacy method).

        This method is for backward compatibility. For new code, use add_documents_with_metadata().
        """
        if not documents:
            return

        # Convert to new format with empty metadata
        documents_with_metadata = [
            (content, embedding, {}) for content, embedding in documents
        ]
        self.add_documents_with_metadata(documents_with_metadata)

    def add_documents_with_metadata(self, documents: List[Tuple[str, List[float], dict]]):
        """
        Adds a batch of documents with metadata to the SQLite database.

        Args:
            documents: List of tuples (content, embedding, metadata_dict)
                      metadata_dict can include:
                      - source_document: str
                      - source_hash: str
                      - chunking_strategy: str
                      - chunk_index: int
                      - char_start: int
                      - char_end: int
                      - semantic_title: str
                      - semantic_summary: str
                      - semantic_overlap: str
                      - metadata_json: str (additional metadata as JSON)
        """
        if not documents:
            return

        # Infer vector dimension from the first document
        vector_dim = len(documents[0][1])
        self._create_table_if_not_exists(vector_dim)

        cursor = self.conn.cursor()

        # Prepare data for bulk insert
        data_to_insert = []
        for content, embedding, metadata in documents:
            embedding_blob = json.dumps(embedding)

            # Extract metadata fields with defaults
            source_document = metadata.get('source_document')
            source_hash = metadata.get('source_hash')
            chunking_strategy = metadata.get('chunking_strategy', 'unknown')
            chunk_index = metadata.get('chunk_index')
            char_start = metadata.get('char_start')
            char_end = metadata.get('char_end')
            semantic_title = metadata.get('semantic_title')
            semantic_summary = metadata.get('semantic_summary')
            semantic_overlap = metadata.get('semantic_overlap')
            metadata_json = metadata.get('metadata_json')

            data_to_insert.append((
                content,
                source_document,
                source_hash,
                chunking_strategy,
                chunk_index,
                char_start,
                char_end,
                semantic_title,
                semantic_summary,
                semantic_overlap,
                embedding_blob,
                metadata_json
            ))

        print(f"Inserting {len(data_to_insert)} documents with metadata into '{self.table_name}'...")
        cursor.executemany(
            f"""INSERT INTO {self.table_name}
                (content, source_document, source_hash, chunking_strategy, chunk_index,
                 char_start, char_end, semantic_title, semantic_summary, semantic_overlap,
                 embedding, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data_to_insert
        )
        self.conn.commit()
        print("Insertion complete.")

    def get_document_count(self) -> int:
        """Returns the total number of documents in the database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = cursor.fetchone()[0]
            return count
        except sqlite3.OperationalError:
            # This can happen if the table doesn't exist yet
            return 0

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Searches for the most similar documents to the query embedding.
        Uses sqlite-vec functions for efficient vector similarity search.

        Args:
            query_embedding (List[float]): The query embedding vector.
            top_k (int): Number of top results to return.

        Returns:
            List[Tuple[str, float]]: List of (content, similarity_score) tuples.
        """
        cursor = self.conn.cursor()
        
        try:
            # Try to use sqlite-vec's vec_distance function for efficient search
            import struct
            query_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
            
            cursor.execute(f"""
                SELECT content, vec_distance(embedding, ?) as distance
                FROM {self.table_name}
                ORDER BY distance
                LIMIT ?
            """, (query_bytes, top_k))
            
            results = cursor.fetchall()
            # Convert distance to similarity (lower distance = higher similarity)
            return [(content, 1.0 / (1.0 + distance)) for content, distance in results]
            
        except sqlite3.OperationalError:
            # Fallback to manual cosine similarity if vec_distance is not available
            print("sqlite-vec distance function not available, using manual similarity calculation")
            cursor.execute(f"SELECT content, embedding FROM {self.table_name}")
            results = cursor.fetchall()
            
            similarities = []
            for content, embedding_data in results:
                # Handle both JSON string and bytes formats
                if isinstance(embedding_data, str):
                    # Embedding stored as JSON string
                    import json
                    stored_embedding = json.loads(embedding_data)
                else:
                    # Embedding stored as bytes (legacy format)
                    import struct
                    stored_embedding = list(struct.unpack(f'{len(embedding_data)//4}f', embedding_data))
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                similarities.append((content, similarity))
            
            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        import math

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def get_all_documents(self) -> List[Tuple[int, str]]:
        """
        Retrieve all documents from the database.

        Returns:
            List[Tuple[int, str]]: List of (id, content) tuples
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT id, content FROM {self.table_name}")
            return cursor.fetchall()
        except sqlite3.OperationalError:
            return []

    def get_document_by_id(self, doc_id: int) -> str:
        """
        Retrieve a specific document by its ID.

        Args:
            doc_id: Document ID

        Returns:
            str: Document content, or empty string if not found
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT content FROM {self.table_name} WHERE id = ?", (doc_id,))
            result = cursor.fetchone()
            return result[0] if result else ""
        except sqlite3.OperationalError:
            return ""

    def __del__(self):
        """Ensures the database connection is closed when the object is destroyed."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
