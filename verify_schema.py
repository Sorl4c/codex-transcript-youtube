#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script temporal para verificar schema v2 y metadata tracking"""

import sqlite3
import os
import sys

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 >nul 2>&1')

def main():
    db_path = 'rag_database.db'

    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        return 1

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar schema
    print("\n" + "=" * 80)
    print("SCHEMA VERIFICATION - vector_store table")
    print("=" * 80)

    cursor.execute("PRAGMA table_info(vector_store)")
    columns = cursor.fetchall()

    print(f"\nTotal columns: {len(columns)}")
    print("\nColumn details:")
    print("-" * 80)
    for col in columns:
        col_id, name, col_type, not_null, default, pk = col
        nullable = "NOT NULL" if not_null else "NULLABLE"
        primary = "PRIMARY KEY" if pk else ""
        print(f"  {name:25s} {col_type:15s} {nullable:10s} {primary}")

    # Verificar metadata tracking
    print("\n" + "=" * 80)
    print("METADATA TRACKING VERIFICATION")
    print("=" * 80)

    cursor.execute("""
        SELECT
            source_document,
            source_hash,
            chunking_strategy,
            chunk_index,
            char_start,
            char_end
        FROM vector_store
        ORDER BY source_document, chunk_index
        LIMIT 10
    """)

    rows = cursor.fetchall()
    print(f"\nSample metadata (first 10 chunks):")
    print("-" * 80)

    for i, row in enumerate(rows, 1):
        source_doc, source_hash, strategy, idx, char_start, char_end = row
        filename = os.path.basename(source_doc) if source_doc else "N/A"
        hash_short = source_hash[:12] if source_hash else "N/A"
        print(f"{i:2d}. {filename:30s} | {strategy:12s} | idx={idx} | chars={char_start}-{char_end} | hash={hash_short}...")

    # Verificar estrategias únicas
    cursor.execute("SELECT DISTINCT chunking_strategy FROM vector_store")
    strategies = [row[0] for row in cursor.fetchall()]

    print("\n" + "=" * 80)
    print("CHUNKING STRATEGIES IN DATABASE")
    print("=" * 80)
    print(f"Strategies found: {', '.join(strategies)}")

    # Verificar source documents únicos
    cursor.execute("SELECT DISTINCT source_document FROM vector_store")
    sources = [os.path.basename(row[0]) if row[0] else "N/A" for row in cursor.fetchall()]

    print("\n" + "=" * 80)
    print("SOURCE DOCUMENTS IN DATABASE")
    print("=" * 80)
    print(f"Unique sources: {len(sources)}")
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source}")

    conn.close()

    print("\n" + "=" * 80)
    print("[SUCCESS] Schema v2 verification completed!")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
