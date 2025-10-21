"""
Tests for RAG CLI commands.

This module tests the command-line interface for the RAG system,
including ingest, query, and stats commands.
"""

import pytest
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any

from rag_engine.rag_cli import cmd_ingest, cmd_query, cmd_stats, main
import argparse


class TestRAGCLICommands:
    """Test RAG CLI command functionality."""

    @pytest.fixture
    def cli_args_namespace(self):
        """Create argparse.Namespace objects for testing CLI commands."""
        class Args:
            def __init__(self):
                pass

        return Args()

    def test_cmd_stats_function(self, populated_test_database, capsys):
        """Test the stats command function directly."""
        # Create a mock args object for stats
        args = argparse.Namespace()

        # Capture output
        result = cmd_stats(args)

        # Should return success code
        assert result == 0

        # Check captured output
        captured = capsys.readouterr()
        assert "Database Statistics" in captured.out
        assert "Total documents:" in captured.out
        assert "Embedder type:" in captured.out
        assert "Database type:" in captured.out

    def test_cmd_query_function_basic(self, populated_test_database, capsys):
        """Test the query command function directly."""
        # Create mock args for query
        args = argparse.Namespace()
        args.question = "What is artificial intelligence?"
        args.top_k = 3
        args.mode = "vector"

        # Capture output
        result = cmd_query(args)

        # Should return success code
        assert result == 0

        # Check captured output
        captured = capsys.readouterr()
        assert "Found" in captured.out
        assert "results:" in captured.out

    def test_cmd_query_function_hybrid(self, populated_test_database, capsys):
        """Test the query command with hybrid mode."""
        args = argparse.Namespace()
        args.question = "machine learning database"
        args.top_k = 5
        args.mode = "hybrid"

        result = cmd_query(args)
        assert result == 0

        captured = capsys.readouterr()
        assert "Found" in captured.out
        # Should show hybrid search results with RRF scoring
        assert "Result #" in captured.out

    def test_cmd_query_function_keyword(self, populated_test_database, capsys):
        """Test the query command with keyword mode."""
        args = argparse.Namespace()
        args.question = "sqlite database"
        args.top_k = 3
        args.mode = "keyword"

        result = cmd_query(args)
        assert result == 0

        captured = capsys.readouterr()
        assert "Found" in captured.out

    def test_cmd_ingest_function(self, temp_rag_files, capsys):
        """Test the ingest command function directly."""
        # Create mock args for ingest
        args = argparse.Namespace()
        args.file = str(temp_rag_files["transcript"])
        args.mock = True  # Use mock mode for fast testing
        args.no_docling = False
        args.strategy = None

        result = cmd_ingest(args)
        assert result == 0

        captured = capsys.readouterr()
        assert "SUCCESS" in captured.out
        assert "Ingestion completed" in captured.out

    def test_cmd_ingest_nonexistent_file(self, capsys):
        """Test ingest command with non-existent file."""
        args = argparse.Namespace()
        args.file = "/nonexistent/path/file.txt"
        args.mock = True
        args.no_docling = False
        args.strategy = None

        result = cmd_ingest(args)
        assert result == 1  # Should return error code

        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "File not found" in captured.out

    def test_main_function_with_stats(self, populated_test_database, capsys):
        """Test main function with stats command."""
        # Mock sys.argv for main function
        original_argv = sys.argv
        try:
            sys.argv = ["rag_cli.py", "stats"]
            result = main()
            assert result == 0

            captured = capsys.readouterr()
            assert "Database Statistics" in captured.out
        finally:
            sys.argv = original_argv

    def test_main_function_with_query(self, populated_test_database, capsys):
        """Test main function with query command."""
        original_argv = sys.argv
        try:
            sys.argv = ["rag_cli.py", "query", "What is AI?", "--top-k", "3"]
            result = main()
            assert result == 0

            captured = capsys.readouterr()
            assert "Found" in captured.out
        finally:
            sys.argv = original_argv

    def test_main_function_help(self, capsys):
        """Test main function help output."""
        original_argv = sys.argv
        try:
            sys.argv = ["rag_cli.py", "--help"]
            result = main()
            assert result == 1  # Help exits with code 1

            captured = capsys.readouterr()
            assert "RAG CLI" in captured.out
            assert "Commands:" in captured.out
        except SystemExit as e:
            # argparse calls sys.exit() on help
            assert e.code == 1
        finally:
            sys.argv = original_argv

    @pytest.mark.slow
    def test_cli_integration_via_subprocess(self, temp_rag_files):
        """Test CLI via subprocess (integration test)."""
        # Test stats command
        result = subprocess.run(
            [sys.executable, "-m", "rag_engine.rag_cli", "stats"],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should succeed
        assert result.returncode == 0
        assert "Database Statistics" in result.stdout

    @pytest.mark.slow
    def test_cli_ingest_via_subprocess(self, temp_rag_files):
        """Test CLI ingest via subprocess."""
        result = subprocess.run(
            [
                sys.executable, "-m", "rag_engine.rag_cli", "ingest",
                str(temp_rag_files["transcript"]), "--mock"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        assert result.returncode == 0
        assert "SUCCESS" in result.stdout
        assert "Ingestion completed" in result.stdout

    @pytest.mark.slow
    def test_cli_query_via_subprocess(self, populated_test_database):
        """Test CLI query via subprocess."""
        result = subprocess.run(
            [
                sys.executable, "-m", "rag_engine.rag_cli", "query",
                "What is artificial intelligence?", "--mode", "vector"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0
        assert "Found" in result.stdout

    def test_query_command_different_modes(self, populated_test_database, capsys):
        """Test query command with different modes."""
        test_cases = [
            ("vector", "What is machine learning?"),
            ("keyword", "sqlite database"),
            ("hybrid", "AI neural networks"),
        ]

        for mode, question in test_cases:
            args = argparse.Namespace()
            args.question = question
            args.top_k = 3
            args.mode = mode

            result = cmd_query(args)
            assert result == 0

            captured = capsys.readouterr()
            assert "Found" in captured.out
            assert f"Mode: {mode}" in captured.out

    def test_query_command_with_different_top_k(self, populated_test_database, capsys):
        """Test query command with different top_k values."""
        args = argparse.Namespace()
        args.question = "database systems"
        args.mode = "vector"

        for top_k in [1, 3, 5, 10]:
            args.top_k = top_k
            result = cmd_query(args)
            assert result == 0

            captured = capsys.readouterr()
            assert f"top {top_k} results" in captured.out

    def test_ingest_command_different_strategies(self, temp_rag_files, capsys):
        """Test ingest command with different chunking strategies."""
        strategies = ["caracteres", "palabras", "semantico"]

        for strategy in strategies:
            args = argparse.Namespace()
            args.file = str(temp_rag_files["transcript"])
            args.mock = True
            args.no_docling = True  # Disable DocLing for faster testing
            args.strategy = strategy

            result = cmd_ingest(args)
            assert result == 0

            captured = capsys.readouterr()
            assert "SUCCESS" in captured.out
            assert strategy in captured.out

    def test_ingest_command_with_docling_options(self, temp_rag_files, capsys):
        """Test ingest command with DocLing enabled/disabled."""
        base_args = argparse.Namespace()
        base_args.file = str(temp_rag_files["transcript"])
        base_args.mock = True
        base_args.strategy = "caracteres"

        # Test with DocLing enabled (default)
        args_with_docling = argparse.Namespace(**vars(base_args))
        args_with_docling.no_docling = False

        result1 = cmd_ingest(args_with_docling)
        assert result1 == 0
        captured1 = capsys.readouterr()
        assert "DocLing preprocessing: Enabled" in captured1.out

        # Test with DocLing disabled
        args_without_docling = argparse.Namespace(**vars(base_args))
        args_without_docling.no_docling = True

        result2 = cmd_ingest(args_without_docling)
        assert result2 == 0
        captured2 = capsys.readouterr()
        assert "DocLing preprocessing: Disabled" in captured2.out

    def test_error_handling_invalid_mode(self, capsys):
        """Test error handling for invalid query mode."""
        # This would be caught by argparse validation in normal operation,
        # but we test the function's error handling
        args = argparse.Namespace()
        args.question = "test question"
        args.top_k = 3
        args.mode = "invalid_mode"

        # This should raise an exception
        with pytest.raises(Exception):
            cmd_query(args)

    def test_empty_database_stats(self, test_database, capsys):
        """Test stats command with empty database."""
        # The test_database fixture should be empty initially
        args = argparse.Namespace()

        result = cmd_stats(args)
        assert result == 0

        captured = capsys.readouterr()
        assert "Total documents: 0" in captured.out

    def test_query_empty_database(self, test_database, capsys):
        """Test query command on empty database."""
        args = argparse.Namespace()
        args.question = "What is AI?"
        args.top_k = 3
        args.mode = "vector"

        result = cmd_query(args)
        assert result == 1  # Should return error for empty database

        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "No results found" in captured.out
        assert "ingested documents first" in captured.out

    def test_large_query_handling(self, populated_test_database, capsys):
        """Test handling of large/complex queries."""
        large_query = " ".join(["artificial intelligence"] * 50)  # Very long query

        args = argparse.Namespace()
        args.question = large_query
        args.top_k = 3
        args.mode = "vector"

        result = cmd_query(args)
        assert result == 0

        captured = capsys.readouterr()
        assert "Found" in captured.out

    def test_special_characters_in_query(self, populated_test_database, capsys):
        """Test queries with special characters."""
        special_queries = [
            "machine learning & AI",
            "database? systems!",
            "natural language processing (NLP)",
            "vector search \"similarity\"",
            "test@example.com query",
        ]

        for query in special_queries:
            args = argparse.Namespace()
            args.question = query
            args.top_k = 3
            args.mode = "vector"

            result = cmd_query(args)
            assert result == 0

            captured = capsys.readouterr()
            assert query in captured.out or "Found" in captured.out