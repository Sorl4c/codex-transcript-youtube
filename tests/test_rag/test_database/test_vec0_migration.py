"""
Tests for vec0 virtual table migration functionality.

This module tests the migration from traditional SQLite tables
to modern vec0 virtual tables with native distance functions.
"""

import pytest
import sqlite3
import tempfile
import os
from typing import List, Dict, Any

from rag_engine.database import SQLiteVecDatabase


class TestVec0Migration:
    """Test migration to vec0 virtual tables."""

    def test_vec0_table_creation(self, test_database):
        """Test that vec0 virtual tables are created correctly."""
        db = test_database

        # Add some test data to trigger table creation
        test_docs = [
            ("Test document 1", [0.1, 0.2, 0.3], {}),
            ("Test document 2", [0.4, 0.5, 0.6], {}),
        ]
        db.add_documents_with_metadata(test_docs)

        cursor = db.conn.cursor()

        # Check that vec0 table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{db.table_name}_vec0'")
        vec0_table = cursor.fetchone()
        assert vec0_table is not None
        assert f"{db.table_name}_vec0" in vec0_table[0]

        # Check that metadata table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{db.table_name}_metadata'")
        metadata_table = cursor.fetchone()
        assert metadata_table is not None
        assert f"{db.table_name}_metadata" in metadata_table[0]

        # Check that vec0 info tables exist (created by sqlite-vec)
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{db.table_name}_vec0_%'")
        info_tables = cursor.fetchall()
        assert len(info_tables) > 0  # Should have info tables

    def test_metadata_table_structure(self, test_database):
        """Test that metadata table has the correct structure."""
        db = test_database

        # Add test data to create tables
        test_docs = [("Test content", [0.1, 0.2, 0.3], {"test": "metadata"})]
        db.add_documents_with_metadata(test_docs)

        cursor = db.conn.cursor()
        metadata_table_name = f"{db.table_name}_metadata"

        # Get table structure
        cursor.execute(f"PRAGMA table_info({metadata_table_name})")
        columns = cursor.fetchall()

        # Check for required columns
        column_names = [col[1] for col in columns]
        required_columns = [
            'id', 'content', 'source_document', 'source_hash',
            'chunking_strategy', 'chunk_index', 'char_start', 'char_end',
            'semantic_title', 'semantic_summary', 'semantic_overlap',
            'created_at', 'metadata_json'
        ]

        for required_col in required_columns:
            assert required_col in column_names, f"Missing column: {required_col}"

        # Check that data was inserted correctly
        cursor.execute(f"SELECT COUNT(*) FROM {metadata_table_name}")
        count = cursor.fetchone()[0]
        assert count == 1

        cursor.execute(f"SELECT content, metadata_json FROM {metadata_table_name}")
        content, metadata_json = cursor.fetchone()
        assert content == "Test content"
        assert "test" in metadata_json

    def test_vec0_table_structure(self, test_database):
        """Test that vec0 table has the correct structure."""
        db = test_database

        # Add test data with 3-dimensional vectors
        test_docs = [("Test content", [0.1, 0.2, 0.3], {})]
        db.add_documents_with_metadata(test_docs)

        cursor = db.conn.cursor()
        vec0_table_name = f"{db.table_name}_vec0"

        # Check table structure
        cursor.execute(f"PRAGMA table_info({vec0_table_name})")
        columns = cursor.fetchall()

        # Vec0 tables should have embedding and metadata_id columns
        column_names = [col[1] for col in columns]
        assert 'embedding' in column_names
        assert 'metadata_id' in column_names

        # Check that data was inserted
        cursor.execute(f"SELECT COUNT(*) FROM {vec0_table_name}")
        count = cursor.fetchone()[0]
        assert count == 1

        # Verify relationship between tables
        cursor.execute(f"""
            SELECT m.content, v.metadata_id
            FROM {vec0_table_name} v
            JOIN {db.table_name}_metadata m ON v.metadata_id = m.id
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "Test content"

    def test_data_consistency_between_tables(self, test_database):
        """Test that data remains consistent between metadata and vec0 tables."""
        db = test_database

        # Add multiple test documents
        test_docs = [
            ("Document 1", [0.1, 0.1, 0.1], {"source": "test1"}),
            ("Document 2", [0.2, 0.2, 0.2], {"source": "test2"}),
            ("Document 3", [0.3, 0.3, 0.3], {"source": "test3"}),
        ]
        db.add_documents_with_metadata(test_docs)

        cursor = db.conn.cursor()
        metadata_table = f"{db.table_name}_metadata"
        vec0_table = f"{db.table_name}_vec0"

        # Check counts match
        cursor.execute(f"SELECT COUNT(*) FROM {metadata_table}")
        metadata_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {vec0_table}")
        vec0_count = cursor.fetchone()[0]

        assert metadata_count == vec0_count == len(test_docs)

        # Check that all metadata_ids are valid
        cursor.execute(f"""
            SELECT COUNT(*) FROM {vec0_table} v
            WHERE NOT EXISTS (SELECT 1 FROM {metadata_table} m WHERE m.id = v.metadata_id)
        """)
        orphaned_vectors = cursor.fetchone()[0]
        assert orphaned_vectors == 0

        # Verify content matches
        cursor.execute(f"""
            SELECT m.content, v.metadata_id
            FROM {vec0_table} v
            JOIN {metadata_table} m ON v.metadata_id = m.id
            ORDER BY v.metadata_id
        """)
        results = cursor.fetchall()

        expected_contents = ["Document 1", "Document 2", "Document 3"]
        actual_contents = [result[0] for result in results]
        assert actual_contents == expected_contents

    def test_vector_storage_format(self, test_database):
        """Test that vectors are stored in the correct binary format."""
        db = test_database

        # Test with known vector
        test_vector = [0.1, -0.2, 0.3, -0.4, 0.5]
        test_docs = [("Test vector storage", test_vector, {})]
        db.add_documents_with_metadata(test_docs)

        cursor = db.conn.cursor()
        vec0_table = f"{db.table_name}_vec0"

        # Retrieve stored vector
        cursor.execute(f"SELECT embedding FROM {vec0_table}")
        stored_bytes = cursor.fetchone()[0]

        # Convert back to float and verify
        import struct
        unpacked_vector = struct.unpack(f'{len(test_vector)}f', stored_bytes)

        # Compare with tolerance for floating point precision
        for original, stored in zip(test_vector, unpacked_vector):
            assert abs(original - stored) < 1e-6

    def test_multiple_vector_dimensions(self, test_database):
        """Test that vec0 tables handle different vector dimensions correctly."""
        db = test_database

        # This should create a table with the dimension of the first document
        test_docs_3d = [("3D vector", [0.1, 0.2, 0.3], {})]
        db.add_documents_with_metadata(test_docs_3d)

        # Try to add a document with the same dimension (should work)
        test_docs_3d_more = [("Another 3D", [0.4, 0.5, 0.6], {})]
        db.add_documents_with_metadata(test_docs_3d_more)

        cursor = db.conn.cursor()
        metadata_table = f"{db.table_name}_metadata"
        cursor.execute(f"SELECT COUNT(*) FROM {metadata_table}")
        count = cursor.fetchone()[0]
        assert count == 2

    def test_indices_created(self, test_database):
        """Test that appropriate indices are created on metadata table."""
        db = test_database

        # Add test data to trigger table and index creation
        test_docs = [("Test content", [0.1, 0.2, 0.3], {"source": "test_file"})]
        db.add_documents_with_metadata(test_docs)

        cursor = db.conn.cursor()
        metadata_table = f"{db.table_name}_metadata"

        # Check that indices exist
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{metadata_table}'")
        indices = cursor.fetchall()

        # Should have indices on key columns
        index_names = [idx[0] for idx in indices]
        expected_patterns = ["content", "strategy", "source", "hash"]

        for pattern in expected_patterns:
            assert any(pattern in idx_name.lower() for idx_name in index_names), \
                f"Missing index for pattern: {pattern}"

    def test_migration_from_legacy_format(self):
        """Test migration from legacy table format to vec0."""
        # Create a temporary database with legacy format
        temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db', prefix='rag_legacy_test_')
        os.close(temp_db_fd)

        try:
            # Create legacy database
            legacy_conn = sqlite3.connect(temp_db_path)
            cursor = legacy_conn.cursor()

            # Create legacy table structure
            cursor.execute("""
                CREATE TABLE legacy_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    source_document TEXT,
                    chunking_strategy TEXT DEFAULT 'unknown'
                )
            """)

            # Insert some legacy data
            import json
            cursor.execute("""
                INSERT INTO legacy_test (content, embedding, source_document, chunking_strategy)
                VALUES (?, ?, ?, ?)
            """, ("Legacy content", json.dumps([0.1, 0.2, 0.3]), "legacy_file.txt", "legacy"))

            legacy_conn.commit()
            legacy_conn.close()

            # Now create SQLiteVecDatabase with same path (should trigger migration)
            db = SQLiteVecDatabase(db_path=temp_db_path, table_name="legacy_test")

            # Check that new tables were created
            cursor = db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%vec0%'")
            vec0_tables = cursor.fetchall()
            assert len(vec0_tables) > 0

            # Check that legacy table was renamed
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='legacy_test_backup'")
            backup_table = cursor.fetchone()
            assert backup_table is not None

            # Check that data was migrated
            cursor.execute("SELECT COUNT(*) FROM legacy_test_metadata")
            migrated_count = cursor.fetchone()[0]
            assert migrated_count == 1

            # Clean up
            del db

        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    def test_database_size_growth(self, test_database):
        """Test that database size grows appropriately with data."""
        import os

        db = test_database
        initial_size = os.path.getsize(db.db_path)

        # Add test data
        test_docs = [
            ("Document with longer content " * 50, [0.1] * 384, {"test": "data"}),
            ("Another document with content " * 50, [0.2] * 384, {"test": "data2"}),
        ]
        db.add_documents_with_metadata(test_docs)

        final_size = os.path.getsize(db.db_path)

        # Database should have grown
        assert final_size > initial_size

        # Growth should be reasonable (not too large, indicating inefficient storage)
        growth_ratio = final_size / initial_size
        assert growth_ratio < 10  # Shouldn't grow more than 10x for 2 documents