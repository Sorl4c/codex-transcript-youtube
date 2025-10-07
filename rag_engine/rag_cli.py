#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG CLI - Command line interface for RAG operations.

Usage:
    python -m rag_engine.rag_cli ingest <file> [--mock] [--strategy <strategy>]
    python -m rag_engine.rag_cli query "<question>" [--top-k <k>]
    python -m rag_engine.rag_cli stats
"""

import sys
import os
import argparse
from typing import Optional

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 >nul 2>&1')  # UTF-8

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.ingestor import RAGIngestor
from rag_engine.chunker import TextChunker
from rag_engine.embedder import EmbedderFactory
from rag_engine.database import SQLiteVecDatabase
from rag_engine.retriever import SimpleRetriever
from rag_engine.hybrid_retriever import HybridRetriever
from rag_engine.config import DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP


def cmd_ingest(args):
    """Handle the ingest command."""
    file_path = args.file

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return 1

    # Determine chunking strategy
    strategy = args.strategy
    if args.mock:
        # Mock mode: use simple character-based chunking (no LLM needed)
        strategy = 'caracteres'
        print("[MOCK] Using character-based chunking (no LLM)")
    elif strategy is None:
        # Default to semantic chunking
        strategy = 'semantico'

    # Get absolute path for source tracking
    abs_file_path = os.path.abspath(file_path)

    print(f"[INGEST] File: {abs_file_path}")
    print(f"[INGEST] Chunking strategy: {strategy}")
    print(f"[INGEST] Chunk size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP}")
    print("-" * 60)

    # Create components
    chunker = TextChunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        strategy=strategy
    )
    embedder = EmbedderFactory.create_embedder()
    database = SQLiteVecDatabase(db_path=DB_PATH)

    # Create ingestor and run with source_document tracking
    ingestor = RAGIngestor(
        chunker=chunker,
        embedder=embedder,
        database=database,
        source_document=abs_file_path
    )

    try:
        summary = ingestor.ingest_from_file(file_path)
        print("\n" + "=" * 60)
        print("[SUCCESS] Ingestion completed!")
        print(f"   Status: {summary.get('status')}")
        print(f"   Chunking strategy: {summary.get('chunking_strategy', 'unknown')}")
        print(f"   Source document: {summary.get('source_document', 'N/A')}")
        print(f"   Source hash: {summary.get('source_hash', 'N/A')[:16]}...")
        print(f"   Chunks processed: {summary.get('chunks_processed', 0)}")
        print(f"   Documents in DB: {summary.get('final_doc_count', 0)}")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n[ERROR] Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_query(args):
    """Handle the query command."""
    question = args.question
    top_k = args.top_k
    mode = args.mode

    print(f"[QUERY] {question}")
    print(f"[QUERY] Mode: {mode}")
    print(f"[QUERY] Retrieving top {top_k} results...")
    print("-" * 60)

    try:
        # Use HybridRetriever if mode is not 'vector', otherwise use SimpleRetriever
        if mode == 'vector':
            retriever = SimpleRetriever()
            results = retriever.query(question, top_k=top_k)
        else:
            retriever = HybridRetriever()
            results = retriever.query(question, top_k=top_k, mode=mode)

        if not results:
            print("[ERROR] No results found. Make sure you've ingested documents first.")
            print("\nTry running:")
            print("  python -m rag_engine.rag_cli ingest transcripts_for_rag/sample_transcript.txt --mock")
            return 1

        print(f"\n[SUCCESS] Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"{'=' * 60}")
            print(f"Result #{i} | Score: {result.score:.4f}")

            # Show provenance for hybrid results
            if hasattr(result, 'vector_rank') or hasattr(result, 'bm25_rank'):
                if result.vector_rank:
                    print(f"  Vector: rank={result.vector_rank}, score={result.vector_score:.4f}")
                if result.bm25_rank:
                    print(f"  BM25: rank={result.bm25_rank}, score={result.bm25_score:.4f}")

            print(f"{'=' * 60}")

            # Show content with nice formatting
            content = result.content.strip()
            if len(content) > 500:
                print(content[:500] + "\n\n[... truncated ...]")
            else:
                print(content)
            print()

        return 0

    except Exception as e:
        print(f"\n[ERROR] Error during query: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_stats(args):
    """Handle the stats command."""
    print("[RAG] Database Statistics")
    print("-" * 60)

    try:
        retriever = SimpleRetriever()
        stats = retriever.get_stats()

        print(f"Database path: {DB_PATH}")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Embedder type: {stats['embedder_type']}")
        print(f"Database type: {stats['database_type']}")

        if os.path.exists(DB_PATH):
            size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
            print(f"Database size: {size_mb:.2f} MB")

        print("-" * 60)
        return 0

    except Exception as e:
        print(f"[ERROR] Error retrieving stats: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG CLI - Command line interface for RAG operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a transcript with mock chunking (fast, no LLM)
  python -m rag_engine.rag_cli ingest transcripts_for_rag/sample_transcript.txt --mock

  # Ingest with semantic chunking
  python -m rag_engine.rag_cli ingest transcripts_for_rag/sample_transcript.txt --strategy semantico

  # Query with different modes
  python -m rag_engine.rag_cli query "What is machine learning?" --mode vector
  python -m rag_engine.rag_cli query "ejercicios triceps" --mode keyword
  python -m rag_engine.rag_cli query "ejercicios para triceps" --mode hybrid

  # Get statistics
  python -m rag_engine.rag_cli stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest a text file into the RAG database')
    ingest_parser.add_argument('file', help='Path to the text file to ingest')
    ingest_parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock mode (simple chunking, no LLM) for fast testing'
    )
    ingest_parser.add_argument(
        '--strategy',
        choices=['caracteres', 'palabras', 'semantico', 'agentic'],
        help='Chunking strategy to use (default: semantico, or caracteres if --mock)'
    )

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG database')
    query_parser.add_argument('question', help='The question to ask')
    query_parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to return (default: 5)'
    )
    query_parser.add_argument(
        '--mode',
        choices=['vector', 'keyword', 'hybrid'],
        default='vector',
        help='Search mode: vector (semantic), keyword (BM25), or hybrid (RRF combination) (default: vector)'
    )

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command handler
    if args.command == 'ingest':
        return cmd_ingest(args)
    elif args.command == 'query':
        return cmd_query(args)
    elif args.command == 'stats':
        return cmd_stats(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
