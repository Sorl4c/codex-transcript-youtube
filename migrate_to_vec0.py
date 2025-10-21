#!/usr/bin/env python3
"""
Script para migrar la base de datos RAG al nuevo formato vec0.
"""

import os
import sys
import sqlite3

# Añadir directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.database import SQLiteVecDatabase, init_sqlite_vec

def migrate_database():
    """Migrate database to vec0 format."""
    db_path = "rag_database.db"

    print(f"Iniciando migración de {db_path} al formato vec0...")

    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)

    try:
        # Inicializar sqlite-vec
        init_sqlite_vec(conn)

        cursor = conn.cursor()

        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tablas existentes: {tables}")

        # Verificar si ya existen tablas vec0
        vec0_exists = "vector_store_vec0" in tables
        metadata_exists = "vector_store_metadata" in tables

        if vec0_exists and metadata_exists:
            print("Las tablas vec0 ya existen. No se necesita migración.")
            return

        # Verificar si existe tabla antigua
        old_table_exists = "vector_store" in tables

        if not old_table_exists:
            print("No existe tabla antigua para migrar.")
            return

        print("Iniciando migración de datos...")

        # Crear tablas nuevas
        vector_dim = 384  # Dimensión de all-MiniLM-L6-v2

        # Crear tabla de metadatos
        cursor.execute("""
            CREATE TABLE vector_store_metadata (
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

        # Crear índices
        cursor.execute("CREATE INDEX idx_vector_store_metadata_content ON vector_store_metadata(content)")
        cursor.execute("CREATE INDEX idx_vector_store_metadata_strategy ON vector_store_metadata(chunking_strategy)")
        cursor.execute("CREATE INDEX idx_vector_store_metadata_source ON vector_store_metadata(source_document)")
        cursor.execute("CREATE INDEX idx_vector_store_metadata_hash ON vector_store_metadata(source_hash)")

        # Crear tabla vec0 virtual
        cursor.execute(f"""
            CREATE VIRTUAL TABLE vector_store_vec0 USING vec0(
                embedding float32[{vector_dim}],
                metadata_id INTEGER
            )
        """)

        # Migrar datos
        cursor.execute("SELECT * FROM vector_store")
        old_data = cursor.fetchall()

        # Obtener nombres de columnas
        cursor.execute("PRAGMA table_info(vector_store)")
        columns = [row[1] for row in cursor.fetchall()]

        migrated_count = 0
        for row in old_data:
            old_record = dict(zip(columns, row))

            # Insertar en tabla de metadatos
            cursor.execute("""
                INSERT INTO vector_store_metadata
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

            # Procesar embedding
            embedding_str = old_record.get('embedding', '[]')
            if isinstance(embedding_str, str):
                import json
                embedding = json.loads(embedding_str)
            else:
                import struct
                embedding = list(struct.unpack(f'{len(embedding_str)//4}f', embedding_str))

            # Convertir a bytes para vec0
            import struct
            embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)

            # Insertar en tabla vec0
            cursor.execute("""
                INSERT INTO vector_store_vec0 (embedding, metadata_id)
                VALUES (?, ?)
            """, (embedding_bytes, metadata_id))

            migrated_count += 1

        # Hacer backup de tabla antigua
        cursor.execute("ALTER TABLE vector_store RENAME TO vector_store_backup")

        # Confirmar cambios
        conn.commit()

        print(f"✅ Migración completada exitosamente!")
        print(f"   - Registros migrados: {migrated_count}")
        print(f"   - Tabla antigua renombrada a: vector_store_backup")
        print(f"   - Nuevas tablas: vector_store_metadata, vector_store_vec0")

    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()