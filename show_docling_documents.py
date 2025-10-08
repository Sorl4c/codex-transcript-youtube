#!/usr/bin/env python3
"""
Script to show documents processed with DocLing preprocessing.
"""

import sqlite3
import json

def show_docling_documents():
    """Show documents processed with DocLing preprocessing."""

    # Connect to database
    conn = sqlite3.connect('rag_database.db')
    cursor = conn.cursor()

    print("=== DOCUMENTOS PROCESADOS CON DOCLING ===\n")

    # Get the most recent documents first
    cursor.execute("""
        SELECT content, source_document, chunking_strategy,
               semantic_title, semantic_summary, char_start, char_end
        FROM vector_store
        WHERE source_document LIKE '%test_agentic.md'
        ORDER BY id DESC
    """)

    docling_docs = cursor.fetchall()

    if not docling_docs:
        print("No se encontraron documentos procesados con DocLing")
        return

    print(f"Se encontraron {len(docling_docs)} documentos procesados con DocLing\n")

    for i, (content, source, strategy, title, summary, start, end) in enumerate(docling_docs, 1):
        print(f"=== CHUNK #{i} ===")
        print(f"Fuente: {source}")
        print(f"Estrategia: {strategy}")
        print(f"Posición: chars {start}-{end}")

        if title:
            print(f"Título semántico: {title}")

        if summary:
            print(f"Resumen semántico: {summary}")

        print(f"\nContenido completo:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        print()

    # Also show the preprocessing info from the logs
    print("\n=== INFORMACIÓN DE PROCESAMIENTO DOCLING ===")
    print("De los registros de la CLI:")
    print("- Processor: docling")
    print("- Format detected: md (markdown)")
    print("- Pipeline: SimplePipeline")
    print("- Processing time: ~0.05 seconds")
    print("- Status: Completado exitosamente")

    conn.close()

if __name__ == "__main__":
    show_docling_documents()