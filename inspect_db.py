#!/usr/bin/env python3
"""
Script to inspect the RAG database and show processed documents.
"""

import sqlite3
import json

def inspect_database():
    """Inspect the RAG database and show processed documents."""

    # Connect to database
    conn = sqlite3.connect('rag_database.db')
    cursor = conn.cursor()

    print("=== INSPECCIÓN DE BASE DE DATOS RAG ===\n")

    # Get basic stats
    cursor.execute("SELECT COUNT(*) FROM vector_store")
    total_docs = cursor.fetchone()[0]
    print(f"Total de documentos en la base de datos: {total_docs}\n")

    # Show sample documents with metadata
    cursor.execute("""
        SELECT content, source_document, chunking_strategy, metadata_json
        FROM vector_store
        WHERE metadata_json LIKE '%docling%'
        LIMIT 3
    """)

    docling_docs = cursor.fetchall()
    print("=== DOCUMENTOS PROCESADOS CON DOCLING ===\n")

    for i, (content, source, strategy, metadata_json) in enumerate(docling_docs, 1):
        print(f"Documento #{i}:")
        print(f"  Fuente: {source}")
        print(f"  Strategy: {strategy}")

        # Parse and show metadata
        try:
            metadata = json.loads(metadata_json) if metadata_json else {}
            print(f"  Metadata:")
            for key, value in metadata.items():
                if key != 'preprocessing_metadata':  # Skip nested metadata for clarity
                    print(f"    {key}: {value}")
                else:
                    print(f"    {key}: [preprocessing metadata disponible]")
        except:
            print(f"  Metadata: {metadata_json}")

        print(f"  Contenido (primeros 200 chars): {content[:200]}...")
        print("-" * 60)
        print()

    # Show documents by chunking strategy
    cursor.execute("""
        SELECT chunking_strategy, COUNT(*) as count
        FROM vector_store
        GROUP BY chunking_strategy
        ORDER BY count DESC
    """)

    strategy_stats = cursor.fetchall()
    print("=== ESTADÍSTICAS POR ESTRATEGIA DE CHUNKING ===\n")
    for strategy, count in strategy_stats:
        print(f"{strategy}: {count} documentos")
    print()

    # Show unique source documents
    cursor.execute("""
        SELECT DISTINCT source_document, COUNT(*) as chunk_count
        FROM vector_store
        GROUP BY source_document
        ORDER BY chunk_count DESC
    """)

    sources = cursor.fetchall()
    print("=== DOCUMENTOS FUENTE ===\n")
    for source, count in sources:
        print(f"{source}: {count} chunks")
    print()

    conn.close()

if __name__ == "__main__":
    inspect_database()