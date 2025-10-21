"""
Tests for sqlite-vec extension functionality.

This module tests the installation, loading, and basic functionality
of the sqlite-vec extension used by the RAG system.
"""

import pytest
import sqlite3
from pathlib import Path

from rag_engine.database import init_sqlite_vec, SQLiteVecDatabase


class TestSQLiteVecExtension:
    """Test sqlite-vec extension installation and basic functionality."""

    def test_sqlite_vec_import(self):
        """Test that sqlite-vec can be imported successfully."""
        try:
            import sqlite_vec
            assert sqlite_vec is not None
        except ImportError as e:
            pytest.skip(f"sqlite-vec not available: {e}")

    def test_sqlite_vec_version(self):
        """Test that sqlite-vec version can be retrieved."""
        try:
            import sqlite_vec
            # Create a temporary connection to test version
            conn = sqlite3.connect(":memory:")
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)

            cursor = conn.cursor()
            cursor.execute("SELECT vec_version()")
            version = cursor.fetchone()[0]

            assert version is not None
            assert isinstance(version, str)
            # Version should be in format like "v0.1.6"
            assert version.startswith("v")
            conn.close()
        except ImportError:
            pytest.skip("sqlite-vec not available")
        except Exception as e:
            pytest.fail(f"Failed to get sqlite-vec version: {e}")

    def test_init_sqlite_vec_function(self, test_database):
        """Test the init_sqlite_vec helper function."""
        db = test_database

        # Check that extension is loaded
        cursor = db.conn.cursor()
        try:
            cursor.execute("SELECT vec_version()")
            version = cursor.fetchone()[0]
            assert version is not None
        except sqlite3.OperationalError:
            pytest.fail("sqlite-vec extension not loaded properly")

    def test_vec_extension_functions_available(self, test_database):
        """Test that vec extension functions are available."""
        db = test_database
        cursor = db.conn.cursor()

        # Test that vec_version function works
        cursor.execute("SELECT vec_version()")
        version = cursor.fetchone()[0]
        assert version.startswith("v")

        # Test that distance function would be available (when vec0 tables exist)
        # This is more of a smoke test since vec0 tables need to exist first
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%vec0%'")
            tables = cursor.fetchall()
            # Should have vec0 tables after database creation
            assert len(tables) > 0
        except sqlite3.OperationalError:
            pytest.fail("vec extension functions not available")

    def test_sqlite_vec_error_handling(self):
        """Test error handling when sqlite-vec is not available."""
        # Test with non-existent extension
        conn = sqlite3.connect(":memory:")
        conn.enable_load_extension(True)

        with pytest.raises(Exception):
            # This should fail gracefully
            conn.load_extension("non_existent_extension")

        conn.close()

    def test_database_connection_with_sqlite_vec(self):
        """Test that SQLiteVecDatabase properly loads sqlite-vec."""
        import tempfile
        import os

        # Create temporary database
        temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db', prefix='rag_test_')
        os.close(temp_db_fd)

        try:
            # This should not raise an exception if sqlite-vec is available
            db = SQLiteVecDatabase(db_path=temp_db_path, table_name="test_vec_store")

            # Check that extension is loaded
            cursor = db.conn.cursor()
            cursor.execute("SELECT vec_version()")
            version = cursor.fetchone()[0]
            assert version.startswith("v")

            # Clean up
            del db

        except Exception as e:
            if "sqlite-vec" in str(e).lower():
                pytest.skip(f"sqlite-vec not properly installed: {e}")
            else:
                raise
        finally:
            # Remove temporary database
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    @pytest.mark.parametrize("test_vector", [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [1.0, 0.0, -1.0, 0.5, -0.5],
        [0.0] * 10,  # Zero vector
        [1.0] * 5,   # Constant vector
    ])
    def test_vector_operations(self, test_database, test_vector):
        """Test basic vector operations with sqlite-vec."""
        db = test_database
        cursor = db.conn.cursor()

        # Create a simple vec0 table for testing
        vector_dim = len(test_vector)
        cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS test_vectors USING vec0(
                embedding float32[{vector_dim}]
            )
        """)

        # Convert vector to bytes for insertion
        import struct
        vector_bytes = struct.pack(f'{len(test_vector)}f', *test_vector)

        # Insert test vector
        cursor.execute("INSERT INTO test_vectors (embedding) VALUES (?)", (vector_bytes,))
        db.conn.commit()

        # Query to verify insertion
        cursor.execute("SELECT COUNT(*) FROM test_vectors")
        count = cursor.fetchone()[0]
        assert count == 1

        # Test similarity search with same vector
        cursor.execute(f"""
            SELECT distance FROM test_vectors
            WHERE embedding MATCH ?
            AND k = 1
        """, (vector_bytes,))

        result = cursor.fetchone()
        assert result is not None
        # Distance should be 0 for identical vectors
        assert abs(result[0]) < 1e-6