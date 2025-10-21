#!/usr/bin/env python3
"""
PostgreSQLVectorDatabase para experimentos controlados - Adaptado para Docker
"""
import os
import json
import hashlib
import time
from typing import List, Tuple, Dict, Any, Optional
import psycopg
from psycopg_pool import ConnectionPool
import numpy as np

class PostgreSQLVectorDatabase:
    """Implementación PostgreSQL para experimentos con embedders (Docker version)"""

    def __init__(self):
        """Inicializar conexión PostgreSQL (Docker)"""
        # Cargar configuración desde .env.rag
        env_file = '.env.rag'
        config = {}

        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value.strip()

        self.embedding_dim = int(config.get('EMBEDDING_DIM', '384'))
        self.embedding_model = config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

        # Pool de conexiones para Docker
        self.pool = ConnectionPool(
            conninfo=self._build_connection_string(config),
            min_size=int(config.get('POSTGRES_MIN_CONNECTIONS', '2')),
            max_size=int(config.get('POSTGRES_MAX_CONNECTIONS', '10')),
            timeout=int(config.get('POSTGRES_TIMEOUT', '30'))
        )

        print(f"🔌 PostgreSQLVectorDatabase inicializado (Docker)")
        print(f"📏 Dimensión: {self.embedding_dim}")
        print(f"🤖 Modelo: {self.embedding_model}")
        print(f"🗄️ Base de datos: {config.get('POSTGRES_DB')}")

    def _build_connection_string(self, config: Dict[str, str]) -> str:
        """Construir connection string desde configuración Docker"""
        return (
            f"host={config.get('POSTGRES_HOST', 'localhost')} "
            f"port={config.get('POSTGRES_PORT', '5432')} "
            f"dbname={config.get('POSTGRES_DB', 'rag_experiments')} "
            f"user={config.get('POSTGRES_USER', 'rag_user')} "
            f"password={config.get('POSTGRES_PASSWORD', '')}"
        )

    def add_documents_with_metadata(self, documents: List[Tuple[str, List[float], dict]]):
        """
        Insertar documentos con metadata y embeddings

        Args:
            documents: Lista de (content, embedding, metadata_dict)
        """
        if not documents:
            return

        start_time = time.time()
        print(f"📥 Insertando {len(documents)} documentos...")

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                for i, (content, embedding, metadata) in enumerate(documents):
                    # Validar dimensión
                    if len(embedding) != self.embedding_dim:
                        raise ValueError(
                            f"Dimensión incorrecta: esperado {self.embedding_dim}, "
                            f"recibido {len(embedding)}"
                        )

                    # Generar source_hash si no existe
                    source_hash = metadata.get('source_hash') or hashlib.md5(
                        content.encode('utf-8')
                    ).hexdigest()

                    try:
                        # Insertar documento (con ON CONFLICT para evitar duplicados)
                        cursor.execute("""
                            INSERT INTO documents (
                                content, source_hash, source_document,
                                chunking_strategy, chunk_index, char_start, char_end,
                                semantic_title, semantic_summary, semantic_overlap,
                                embedding_model, metadata_json
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                            ON CONFLICT (source_hash) DO UPDATE SET
                                content = EXCLUDED.content,
                                embedding_model = EXCLUDED.embedding_model
                            RETURNING id
                        """, (
                            content,
                            source_hash,
                            metadata.get('source_document'),
                            metadata.get('chunking_strategy', 'agentic'),
                            metadata.get('chunk_index'),
                            metadata.get('char_start'),
                            metadata.get('char_end'),
                            metadata.get('semantic_title'),
                            metadata.get('semantic_summary'),
                            metadata.get('semantic_overlap'),
                            self.embedding_model,
                            json.dumps(metadata.get('additional_metadata', {}))
                            if metadata.get('additional_metadata') else None
                        ))

                        doc_id = cursor.fetchone()[0]

                        # Convertir embedding a formato PostgreSQL vector
                        embedding_str = f"[{','.join(map(str, embedding))}]"

                        # Insertar embedding
                        cursor.execute("""
                            INSERT INTO document_embeddings (
                                document_id, embedding, embedding_model
                            ) VALUES (%s, %s::vector, %s)
                            ON CONFLICT (document_id) DO UPDATE SET
                                embedding = EXCLUDED.embedding,
                                embedding_model = EXCLUDED.embedding_model
                        """, (doc_id, embedding_str, self.embedding_model))

                        print(f"✅ Documento {i+1}/{len(documents)} insertado (hash: {source_hash[:16]}...)")

                    except Exception as e:
                        print(f"❌ Error insertando documento {i+1}: {e}")
                        continue

            conn.commit()

        elapsed_time = time.time() - start_time
        print(f"🎉 Inserción completada en {elapsed_time:.2f}s")

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Buscar documentos similares usando pgvector

        Args:
            query_embedding: Vector de consulta
            top_k: Número de resultados a devolver

        Returns:
            Lista de (content, similarity_score)
        """
        if len(query_embedding) != self.embedding_dim:
            raise ValueError(
                f"Dimensión incorrecta en query: esperado {self.embedding_dim}, "
                f"recibido {len(query_embedding)}"
            )

        start_time = time.time()

        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        d.content,
                        d.source_hash,
                        1 - (de.embedding <=> %s::vector) as similarity
                    FROM document_embeddings de
                    JOIN documents d ON de.document_id = d.id
                    ORDER BY de.embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, top_k))

                results = cursor.fetchall()

        elapsed_time = time.time() - start_time
        print(f"🔍 Búsqueda completada en {elapsed_time:.3f}s: {len(results)} resultados")

        return [(content, float(similarity)) for content, _, similarity in results]

    def get_document_count(self) -> int:
        """Obtener número total de documentos"""
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM documents")
                return cursor.fetchone()[0]

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        with self.pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM document_embeddings")
                emb_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT embedding_model)
                    FROM documents WHERE embedding_model IS NOT NULL
                """)
                model_count = cursor.fetchone()[0]

                return {
                    'documents': doc_count,
                    'embeddings': emb_count,
                    'models': model_count,
                    'current_model': self.embedding_model,
                    'dimension': self.embedding_dim
                }

    def close(self):
        """Cerrar pool de conexiones"""
        if self.pool:
            self.pool.close()
            print("🔌 Pool de conexiones cerrado")

if __name__ == "__main__":
    # Test básico de la clase (Docker version)
    print("🧪 Test de conexión PostgreSQL (Docker)...")

    try:
        db = PostgreSQLVectorDatabase()
        stats = db.get_stats()
        print(f"📊 Estadísticas: {stats}")

        # Test de búsqueda con embedding de prueba
        test_embedding = [0.1] * int(os.getenv('EMBEDDING_DIM', '384'))
        results = db.search_similar(test_embedding, top_k=1)
        print(f"🔍 Test búsqueda: {len(results)} resultados")

        db.close()
        print("✅ Test completado exitosamente")

    except Exception as e:
        print(f"❌ Error en test: {e}")
        print("💡 Verifica que Docker está corriendo y .env.rag tiene las credenciales correctas")