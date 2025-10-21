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
        Uses modern sqlite-vec vec0 virtual tables for optimal performance.

        Schema v3 uses vec0 virtual tables with native distance functions.

        Args:
            vector_dim (int): The dimension of the vectors to be stored.
        """
        cursor = self.conn.cursor()

        # Check if old table exists and migrate if needed
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'")
        old_table_exists = cursor.fetchone() is not None

        # Check if new vec0 table exists
        vec0_table_name = f"{self.table_name}_vec0"
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{vec0_table_name}'")
        vec0_table_exists = cursor.fetchone() is not None

        if not vec0_table_exists:
            print(f"Creating new vec0 virtual table '{vec0_table_name}' with vector dimension {vector_dim}.")

            # Create metadata table first
            metadata_table_name = f"{self.table_name}_metadata"
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{metadata_table_name}'")
            if cursor.fetchone() is None:
                cursor.execute(f"""
                    CREATE TABLE {metadata_table_name} (
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata_json TEXT
                    )
                """)

                # Create indices for metadata table
                cursor.execute(f"CREATE INDEX idx_{metadata_table_name}_content ON {metadata_table_name}(content)")
                cursor.execute(f"CREATE INDEX idx_{metadata_table_name}_strategy ON {metadata_table_name}(chunking_strategy)")
                cursor.execute(f"CREATE INDEX idx_{metadata_table_name}_source ON {metadata_table_name}(source_document)")
                cursor.execute(f"CREATE INDEX idx_{metadata_table_name}_hash ON {metadata_table_name}(source_hash)")

            # Create vec0 virtual table for vectors
            cursor.execute(f"""
                CREATE VIRTUAL TABLE {vec0_table_name} USING vec0(
                    embedding float32[{vector_dim}],
                    metadata_id INTEGER
                )
            """)

            print(f"Vec0 virtual table '{vec0_table_name}' created successfully.")

            # Migrate data from old table if it exists
            if old_table_exists:
                self._migrate_from_old_table(vec0_table_name, metadata_table_name)

            self.conn.commit()
        else:
            print(f"Vec0 table '{vec0_table_name}' already exists.")

    def _migrate_from_old_table(self, vec0_table_name: str, metadata_table_name: str):
        """
        Migrate data from old table format to new vec0 virtual tables.
        """
        cursor = self.conn.cursor()

        try:
            # Get all data from old table
            cursor.execute(f"SELECT * FROM {self.table_name}")
            old_data = cursor.fetchall()

            if not old_data:
                print("No data to migrate from old table.")
                return

            print(f"Migrating {len(old_data)} records from old table to new vec0 format...")

            # Get column names from old table
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = [row[1] for row in cursor.fetchall()]

            migrated_count = 0
            for row in old_data:
                old_record = dict(zip(columns, row))

                # Insert into metadata table
                cursor.execute(f"""
                    INSERT INTO {metadata_table_name}
                    (content, source_document, source_hash, chunking_strategy, chunk_index,
                     char_start, char_end, semantic_title, semantic_summary, semantic_overlap, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    old_record.get('content'),
                    old_record.get('source_document'),
                    old_record.get('source_hash'),
                    old_record.get('chunking_strategy', 'unknown'),
                    old_record.get('chunk_index'),
                    old_record.get('char_start'),
                    old_record.get('char_end'),
                    old_record.get('semantic_title'),
                    old_record.get('semantic_summary'),
                    old_record.get('semantic_overlap'),
                    old_record.get('metadata_json')
                ))

                metadata_id = cursor.lastrowid

                # Parse embedding and insert into vec0 table
                embedding_str = old_record.get('embedding', '[]')
                if isinstance(embedding_str, str):
                    import json
                    embedding = json.loads(embedding_str)
                else:
                    # Handle bytes format (legacy)
                    import struct
                    embedding = list(struct.unpack(f'{len(embedding_str)//4}f', embedding_str))

                # Convert to float32 bytes for vec0
                import struct
                embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)

                cursor.execute(f"""
                    INSERT INTO {vec0_table_name} (embedding, metadata_id)
                    VALUES (?, ?)
                """, (embedding_bytes, metadata_id))

                migrated_count += 1

            self.conn.commit()
            print(f"Successfully migrated {migrated_count} records to vec0 format.")

            # Optionally backup old table
            cursor.execute(f"ALTER TABLE {self.table_name} RENAME TO {self.table_name}_backup")
            print(f"Old table renamed to {self.table_name}_backup")

        except Exception as e:
            print(f"Error during migration: {e}")
            self.conn.rollback()
            raise

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
        Adds a batch of documents with metadata to the SQLite database using vec0 virtual tables.

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

        # Get table names
        vec0_table_name = f"{self.table_name}_vec0"
        metadata_table_name = f"{self.table_name}_metadata"

        print(f"Inserting {len(documents)} documents with metadata into new vec0 format...")

        for content, embedding, metadata in documents:
            # Insert into metadata table first
            cursor.execute(f"""
                INSERT INTO {metadata_table_name}
                (content, source_document, source_hash, chunking_strategy, chunk_index,
                 char_start, char_end, semantic_title, semantic_summary, semantic_overlap, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content,
                metadata.get('source_document'),
                metadata.get('source_hash'),
                metadata.get('chunking_strategy', 'unknown'),
                metadata.get('chunk_index'),
                metadata.get('char_start'),
                metadata.get('char_end'),
                metadata.get('semantic_title'),
                metadata.get('semantic_summary'),
                metadata.get('semantic_overlap'),
                metadata.get('metadata_json')
            ))

            metadata_id = cursor.lastrowid

            # Convert embedding to float32 bytes for vec0
            import struct
            embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)

            # Insert into vec0 table
            cursor.execute(f"""
                INSERT INTO {vec0_table_name} (embedding, metadata_id)
                VALUES (?, ?)
            """, (embedding_bytes, metadata_id))

        self.conn.commit()
        print("Insertion complete with vec0 virtual tables.")

    def get_document_count(self) -> int:
        """Returns the total number of documents in the database."""
        cursor = self.conn.cursor()
        try:
            # Try new vec0 format first
            metadata_table_name = f"{self.table_name}_metadata"
            cursor.execute(f"SELECT COUNT(*) FROM {metadata_table_name}")
            count = cursor.fetchone()[0]
            return count
        except sqlite3.OperationalError:
            # Fallback to old table format
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
        Uses modern sqlite-vec KNN queries for optimal performance.

        Args:
            query_embedding (List[float]): The query embedding vector.
            top_k (int): Number of top results to return.

        Returns:
            List[Tuple[str, float]]: List of (content, similarity_score) tuples.
        """
        cursor = self.conn.cursor()

        try:
            # Try new vec0 format with KNN queries
            vec0_table_name = f"{self.table_name}_vec0"
            metadata_table_name = f"{self.table_name}_metadata"

            # Convert query embedding to float32 bytes
            import struct
            query_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)

            # Use KNN query with native distance function
            cursor.execute(f"""
                SELECT
                    m.content,
                    v.distance
                FROM {vec0_table_name} v
                JOIN {metadata_table_name} m ON v.metadata_id = m.id
                WHERE v.embedding MATCH ?
                AND k = ?
            """, (query_bytes, top_k))

            results = cursor.fetchall()

            # Convert distance to similarity (lower distance = higher similarity)
            similarities = [(content, 1.0 / (1.0 + distance)) for content, distance in results]
            print(f"Found {len(similarities)} results using native KNN queries")
            return similarities

        except sqlite3.OperationalError as e:
            # Fallback to old table format
            print(f"Vec0 tables not available, falling back to old format: {e}")
            return self._search_similar_legacy(query_embedding, top_k)

    def _search_similar_legacy(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Legacy search method for old table format.
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
            # Fallback: Try backup table
            try:
                backup_table = f"{self.table_name}_backup"
                print(f"Trying backup table: {backup_table}")
                cursor.execute(f"SELECT content, embedding FROM {backup_table}")
                results = cursor.fetchall()

                similarities = []
                for content, embedding_data in results:
                    # Handle both JSON string and bytes formats
                    if isinstance(embedding_data, str):
                        import json
                        stored_embedding = json.loads(embedding_data)
                    else:
                        import struct
                        stored_embedding = list(struct.unpack(f'{len(embedding_data)//4}f', embedding_data))

                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    similarities.append((content, similarity))

                # Sort by similarity (descending) and return top_k
                similarities.sort(key=lambda x: x[1], reverse=True)
                return similarities[:top_k]
            except sqlite3.OperationalError:
                print("No backup table available. Manual search not possible.")
                return []

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
            # Try new vec0 format first
            metadata_table_name = f"{self.table_name}_metadata"
            cursor.execute(f"SELECT id, content FROM {metadata_table_name}")
            return cursor.fetchall()
        except sqlite3.OperationalError:
            # Fallback to old table format
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
            # Try new vec0 format first
            metadata_table_name = f"{self.table_name}_metadata"
            cursor.execute(f"SELECT content FROM {metadata_table_name} WHERE id = ?", (doc_id,))
            result = cursor.fetchone()
            return result[0] if result else ""
        except sqlite3.OperationalError:
            # Fallback to old table format
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
