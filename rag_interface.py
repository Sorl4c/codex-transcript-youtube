#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Interface - Wrapper para el sistema RAG que integra con Streamlit GUI.

Este módulo proporciona una interfaz simplificada para las operaciones RAG
dentro de la aplicación Streamlit, encapsulando la complejidad del sistema
RAG subyacente.
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio padre al path para importar módulos RAG
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rag_engine.ingestor import RAGIngestor
    from rag_engine.chunker import TextChunker
    from rag_engine.embedder import EmbedderFactory
    from rag_engine.database import SQLiteVecDatabase
    from rag_engine.retriever import SimpleRetriever
    from rag_engine.hybrid_retriever import HybridRetriever
    from rag_engine.config import DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP
    RAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RAG engine not available: {e}")
    RAG_AVAILABLE = False


@dataclass
class RAGResult:
    """Resultado de una consulta RAG."""
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    vector_rank: Optional[int] = None
    vector_score: Optional[float] = None
    bm25_rank: Optional[int] = None
    bm25_score: Optional[float] = None


@dataclass
class RAGStats:
    """Estadísticas del sistema RAG."""
    total_documents: int
    embedder_type: str
    database_type: str
    database_path: str
    database_size_mb: float
    available: bool


class RAGInterface:
    """
    Interfaz simplificada para operaciones RAG en la aplicación Streamlit.

    Esta clase encapsula toda la complejidad del sistema RAG y proporciona
    métodos simples para ingestión y consulta de documentos.
    """

    def __init__(self):
        """Inicializar la interfaz RAG."""
        self.available = RAG_AVAILABLE
        self._retriever = None
        self._ingestor = None
        self._hybrid_retriever = None
        self._chunker = None
        self._embedder = None
        self._database = None

    def _ensure_database(self):
        """Crear la base de datos bajo demanda."""
        try:
            if self._database is None and self.available:
                logger.info("Initializing RAG vector database on demand")
                self._database = SQLiteVecDatabase(db_path=DB_PATH)
        except Exception as e:
            logger.error(f"Error initializing RAG database: {e}")
            self.available = False

    def _ensure_embedder(self):
        """Crear el embedder cuando sea necesario."""
        try:
            if self._embedder is None and self.available:
                logger.info("Initializing sentence-transformer embedder on demand")
                self._embedder = EmbedderFactory.create_embedder()
        except Exception as e:
            logger.error(f"Error initializing embedder: {e}")
            self.available = False

    def _ensure_chunker(self, strategy: str):
        """Crear el chunker cuando se requiera."""
        if not self.available:
            return

        recreate = (
            self._chunker is None or
            getattr(self._chunker, 'strategy', None) != strategy
        )

        if recreate:
            self._chunker = TextChunker(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                strategy=strategy
            )

    def _get_database(self):
        """Obtener la base de datos inicializada."""
        if not self.available:
            raise RuntimeError("RAG system not available")
        self._ensure_database()
        if self._database is None:
            raise RuntimeError("RAG database could not be initialized")
        return self._database

    def _get_embedder(self):
        """Obtener el embedder inicializado."""
        if not self.available:
            raise RuntimeError("RAG system not available")
        self._ensure_embedder()
        if self._embedder is None:
            raise RuntimeError("RAG embedder could not be initialized")
        return self._embedder

    def _get_vector_retriever(self):
        """Obtener el retriever vectorial reutilizando recursos."""
        if self._retriever is None:
            self._retriever = SimpleRetriever(
                database=self._get_database(),
                embedder=self._get_embedder()
            )
        return self._retriever

    def _get_hybrid_retriever(self):
        """Obtener el retriever híbrido reutilizando recursos."""
        if self._hybrid_retriever is None:
            self._hybrid_retriever = HybridRetriever(
                database=self._get_database(),
                embedder=self._get_embedder()
            )
        return self._hybrid_retriever

    def is_available(self) -> bool:
        """Verificar si el sistema RAG está disponible."""
        return self.available

    def get_stats(self) -> RAGStats:
        """Obtener estadísticas del sistema RAG."""
        if not self.available:
            return RAGStats(
                total_documents=0,
                embedder_type="N/A",
                database_type="N/A",
                database_path="N/A",
                database_size_mb=0.0,
                available=False
            )

        try:
            database = self._get_database()
            total_documents = database.get_document_count()
            embedder_type = type(self._embedder).__name__ if self._embedder else "uninitialized"
            database_type = type(database).__name__

            # Obtener tamaño de la base de datos
            db_size = 0.0
            if os.path.exists(DB_PATH):
                db_size = os.path.getsize(DB_PATH) / (1024 * 1024)

            return RAGStats(
                total_documents=total_documents,
                embedder_type=embedder_type,
                database_type=database_type,
                database_path=DB_PATH,
                database_size_mb=db_size,
                available=True
            )

        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return RAGStats(
                total_documents=0,
                embedder_type="Error",
                database_type="Error",
                database_path=DB_PATH,
                database_size_mb=0.0,
                available=False
            )

    def ingest_transcript(self, video_id: str, title: str, transcript: str,
                         strategy: str = 'semantico', use_docling: bool = True) -> Dict[str, Any]:
        """
        Ingestar una transcripción en el sistema RAG.

        Args:
            video_id: ID del vídeo
            title: Título del vídeo
            transcript: Texto de la transcripción
            strategy: Estrategia de chunking ('caracteres', 'palabras', 'semantico', 'agentic')
            use_docling: Usar preprocesamiento DocLing

        Returns:
            Diccionario con resultado de la operación
        """
        if not self.available:
            return {
                'status': 'error',
                'message': 'RAG system not available'
            }

        try:
            # Crear un documento temporal con la transcripción
            temp_dir = os.path.join(os.path.dirname(DB_PATH), 'temp_transcripts')
            os.makedirs(temp_dir, exist_ok=True)

            database = self._get_database()
            embedder = self._get_embedder()
            self._ensure_chunker(strategy)

            # Generar nombre de archivo único
            filename = f"{video_id}_{hashlib.md5(title.encode()).hexdigest()[:8]}.txt"
            temp_file = os.path.join(temp_dir, filename)

            # Escribir transcripción a archivo temporal
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n{transcript}")

            # Actualizar chunker con la estrategia especificada
            # Crear ingestor
            self._ingestor = RAGIngestor(
                chunker=self._chunker,
                embedder=embedder,
                database=database,
                source_document=f"video:{video_id}",
                use_docling=use_docling
            )

            # Ingestar documento
            if use_docling:
                summary = self._ingestor.ingest_from_file_enhanced(temp_file)
            else:
                summary = self._ingestor.ingest_from_file(temp_file)

            # Limpiar archivo temporal
            try:
                os.remove(temp_file)
            except:
                pass

            return {
                'status': 'success',
                'message': f'Successfully ingested transcript for video: {title}',
                'chunks_processed': summary.get('chunks_processed', 0),
                'strategy': strategy,
                'use_docling': use_docling,
                'video_id': video_id
            }

        except Exception as e:
            logger.error(f"Error ingesting transcript: {e}")
            return {
                'status': 'error',
                'message': f'Error ingesting transcript: {str(e)}',
                'video_id': video_id
            }

    def query(self, question: str, mode: str = 'hybrid', top_k: int = 5) -> Tuple[List[RAGResult], Optional[str]]:
        """
        Realizar una consulta al sistema RAG.

        Args:
            question: Pregunta a consultar
            mode: Modo de búsqueda ('vector', 'keyword', 'hybrid')
            top_k: Número de resultados a recuperar

        Returns:
            Tupla con (lista de resultados, mensaje de error si existe)
        """
        if not self.available:
            return [], "RAG system not available"

        if not question or not question.strip():
            return [], "Please enter a question"

        try:
            # Crear retriever apropiado según el modo
            if mode == 'vector':
                retriever = self._get_vector_retriever()
                results = retriever.query(question, top_k=top_k)
            else:
                retriever = self._get_hybrid_retriever()
                results = retriever.query(question, top_k=top_k, mode=mode)

            if not results:
                return [], "No results found. Try ingesting some transcripts first."

            # Convertir resultados a RAGResult
            rag_results = []
            for result in results:
                rag_result = RAGResult(
                    content=result.content,
                    score=result.score,
                    metadata=getattr(result, 'metadata', None),
                    vector_rank=getattr(result, 'vector_rank', None),
                    vector_score=getattr(result, 'vector_score', None),
                    bm25_rank=getattr(result, 'bm25_rank', None),
                    bm25_score=getattr(result, 'bm25_score', None)
                )
                rag_results.append(rag_result)

            return rag_results, None

        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return [], f"Error querying RAG system: {str(e)}"

    def get_available_strategies(self) -> List[str]:
        """Obtener estrategias de chunking disponibles."""
        return ['caracteres', 'palabras', 'semantico', 'agentic']

    def get_available_modes(self) -> List[str]:
        """Obtener modos de búsqueda disponibles."""
        return ['vector', 'keyword', 'hybrid']

    def clear_database(self) -> Dict[str, Any]:
        """Limpiar la base de datos RAG."""
        if not self.available:
            return {
                'status': 'error',
                'message': 'RAG system not available'
            }

        try:
            if self._database is not None:
                try:
                    self._database.conn.close()
                except Exception:
                    pass
            self._database = None
            self._retriever = None
            self._hybrid_retriever = None
            self._chunker = None
            self._ingestor = None

            # Eliminar archivo de base de datos
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)

            return {
                'status': 'success',
                'message': 'RAG database cleared successfully'
            }

        except Exception as e:
            logger.error(f"Error clearing RAG database: {e}")
            return {
                'status': 'error',
                'message': f'Error clearing RAG database: {str(e)}'
            }


# Instancia global de la interfaz RAG
_rag_interface = None

def get_rag_interface() -> RAGInterface:
    """Obtener la instancia global de la interfaz RAG."""
    global _rag_interface
    if _rag_interface is None:
        _rag_interface = RAGInterface()
    return _rag_interface
