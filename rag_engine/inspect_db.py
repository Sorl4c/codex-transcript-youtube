#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspect_db.py - Herramienta para inspeccionar el contenido de rag_database.db

Muestra estadísticas detalladas, metadata de chunking strategies, y permite
detectar duplicados y analizar la diversidad del corpus.
"""

import sys
import os
import json
import sqlite3
from collections import Counter
from typing import Dict, List, Tuple

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 >nul 2>&1')  # UTF-8

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.config import DB_PATH


def get_db_connection():
    """Conecta a la base de datos RAG."""
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found: {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)


def get_basic_stats(conn: sqlite3.Connection) -> Dict:
    """Obtiene estadísticas básicas de la BD."""
    cursor = conn.cursor()

    # Total documentos
    cursor.execute("SELECT COUNT(*) FROM vector_store")
    total_docs = cursor.fetchone()[0]

    # Estadísticas por strategy
    cursor.execute("""
        SELECT chunking_strategy, COUNT(*)
        FROM vector_store
        GROUP BY chunking_strategy
    """)
    strategy_stats = dict(cursor.fetchall())

    # Source documents únicos
    cursor.execute("SELECT COUNT(DISTINCT source_document) FROM vector_store")
    unique_sources = cursor.fetchone()[0]

    # Source hashes únicos
    cursor.execute("SELECT COUNT(DISTINCT source_hash) FROM vector_store")
    unique_hashes = cursor.fetchone()[0]

    return {
        "total_documents": total_docs,
        "strategy_breakdown": strategy_stats,
        "unique_source_documents": unique_sources,
        "unique_source_hashes": unique_hashes
    }


def get_source_documents(conn: sqlite3.Connection) -> List[Tuple[str, int, str]]:
    """Lista todos los source documents con sus estadísticas."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            source_document,
            COUNT(*) as chunk_count,
            chunking_strategy
        FROM vector_store
        WHERE source_document IS NOT NULL
        GROUP BY source_document, chunking_strategy
        ORDER BY source_document, chunking_strategy
    """)
    return cursor.fetchall()


def detect_duplicates(conn: sqlite3.Connection) -> List[Tuple[str, int]]:
    """Detecta posibles duplicados por source_hash."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source_hash, COUNT(*) as count
        FROM vector_store
        WHERE source_hash IS NOT NULL
        GROUP BY source_hash
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    return cursor.fetchall()


def get_agentic_metadata_samples(conn: sqlite3.Connection, limit: int = 5) -> List[Dict]:
    """Obtiene muestras de chunks con metadata agentic."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            SUBSTR(content, 1, 100) as content_preview,
            semantic_title,
            semantic_summary,
            metadata_json,
            chunking_strategy,
            source_document
        FROM vector_store
        WHERE chunking_strategy = 'agentic' AND semantic_title IS NOT NULL
        LIMIT ?
    """, (limit,))

    samples = []
    for row in cursor.fetchall():
        doc_id, content, title, summary, metadata_json, strategy, source = row

        # Parse keywords from metadata_json
        keywords = []
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
                keywords = metadata.get('keywords', [])
            except json.JSONDecodeError:
                pass

        samples.append({
            "id": doc_id,
            "content_preview": content + "...",
            "title": title,
            "summary": summary,
            "keywords": keywords,
            "source": os.path.basename(source) if source else "N/A"
        })

    return samples


def analyze_content_diversity(conn: sqlite3.Connection) -> Dict:
    """Analiza la diversidad del contenido usando palabras frecuentes."""
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM vector_store")

    all_text = " ".join(row[0].lower() for row in cursor.fetchall())

    # Palabras más frecuentes (excluyendo stopwords comunes)
    stopwords = {"de", "la", "el", "en", "y", "a", "los", "las", "del", "que", "es", "se", "por",
                 "con", "para", "un", "una", "al", "lo", "como", "más", "su", "sus", "o", "no"}

    words = [w for w in all_text.split() if len(w) > 3 and w not in stopwords]
    word_counts = Counter(words)

    return {
        "total_words": len(words),
        "unique_words": len(set(words)),
        "top_20_words": word_counts.most_common(20)
    }


def print_report(stats: Dict, sources: List, duplicates: List, agentic_samples: List, diversity: Dict):
    """Imprime un reporte completo."""
    print("\n" + "=" * 80)
    print("RAG DATABASE INSPECTION REPORT")
    print("=" * 80)

    # Estadísticas básicas
    print("\n[1] BASIC STATISTICS")
    print("-" * 80)
    print(f"Database path: {DB_PATH}")
    print(f"Total chunks: {stats['total_documents']}")
    print(f"Unique source documents: {stats['unique_source_documents']}")
    print(f"Unique source hashes: {stats['unique_source_hashes']}")

    if os.path.exists(DB_PATH):
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        print(f"Database size: {size_mb:.2f} MB")

    # Breakdown por strategy
    print("\n[2] CHUNKING STRATEGY BREAKDOWN")
    print("-" * 80)
    for strategy, count in stats['strategy_breakdown'].items():
        percentage = (count / stats['total_documents']) * 100 if stats['total_documents'] > 0 else 0
        print(f"  {strategy:15s}: {count:5d} chunks ({percentage:5.1f}%)")

    # Source documents
    print("\n[3] SOURCE DOCUMENTS")
    print("-" * 80)
    if sources:
        for source, chunk_count, strategy in sources:
            source_name = os.path.basename(source) if source else "N/A"
            print(f"  {source_name:40s} | {strategy:12s} | {chunk_count:3d} chunks")
    else:
        print("  No source documents found")

    # Duplicados
    print("\n[4] DUPLICATE DETECTION")
    print("-" * 80)
    if duplicates:
        print(f"  Found {len(duplicates)} potential duplicates:")
        for source_hash, count in duplicates[:10]:
            print(f"    Hash {source_hash[:16]}... appears {count} times")
    else:
        print("  [OK] No duplicates detected")

    # Muestras de metadata agentic
    print("\n[5] AGENTIC METADATA SAMPLES")
    print("-" * 80)
    if agentic_samples:
        for i, sample in enumerate(agentic_samples, 1):
            print(f"\n  Sample #{i} (ID: {sample['id']}, Source: {sample['source']})")
            print(f"  Title: {sample['title']}")
            print(f"  Summary: {sample['summary']}")
            if sample['keywords']:
                print(f"  Keywords: {', '.join(sample['keywords'])}")
            print(f"  Content: {sample['content_preview']}")
    else:
        print("  No agentic chunks with metadata found")

    # Diversidad de contenido
    print("\n[6] CONTENT DIVERSITY ANALYSIS")
    print("-" * 80)
    print(f"Total words: {diversity['total_words']}")
    print(f"Unique words: {diversity['unique_words']}")
    print(f"Vocabulary richness: {(diversity['unique_words'] / diversity['total_words'] * 100):.1f}%")
    print("\nTop 20 most frequent words:")
    for word, count in diversity['top_20_words']:
        print(f"  {word:20s}: {count:5d}")

    print("\n" + "=" * 80)


def main():
    """Punto de entrada principal."""
    print("\n[INSPECT] Inspecting RAG Database...")

    conn = get_db_connection()
    if not conn:
        return 1

    try:
        stats = get_basic_stats(conn)
        sources = get_source_documents(conn)
        duplicates = detect_duplicates(conn)
        agentic_samples = get_agentic_metadata_samples(conn, limit=5)
        diversity = analyze_content_diversity(conn)

        print_report(stats, sources, duplicates, agentic_samples, diversity)

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
