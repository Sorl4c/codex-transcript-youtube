"""
Main orchestrator for the RAG ingestion pipeline.

This module brings together the chunker, embedder, and database components
to process and store text data for retrieval.
"""

import os
from typing import Dict, Any

from .chunker import TextChunker
from .embedder import Embedder, EmbedderFactory
from .database import VectorDatabase, SQLiteVecDatabase
from .config import INGESTION_SOURCE_DIR

class RAGIngestor:
    """Orchestrates the process of chunking, embedding, and storing text data."""

    def __init__(
        self,
        chunker: TextChunker,
        embedder: Embedder,
        database: VectorDatabase
    ):
        """
        Initializes the RAGIngestor with dependency injection.

        Args:
            chunker (TextChunker): An instance of a text chunker.
            embedder (Embedder): An instance of an embedder.
            database (VectorDatabase): An instance of a vector database.
        """
        self.chunker = chunker
        self.embedder = embedder
        self.database = database

    def ingest_text(self, text: str) -> Dict[str, Any]:
        """
        Processes a single string of text and stores it in the database.

        Args:
            text (str): The text to ingest.

        Returns:
            Dict[str, Any]: A dictionary summarizing the ingestion process.
        """
        print("--- Starting ingestion process for text ---")
        
        # 1. Chunk the text
        chunks = self.chunker.chunk(text)
        if not chunks:
            print("Text is too short or empty, nothing to ingest.")
            return {"status": "No chunks generated", "chunks_processed": 0}
        print(f"Text split into {len(chunks)} chunks.")

        # 2. Extract text content from Chunk objects
        # Chunks can be Chunk objects (with .content) or plain strings
        chunk_texts = []
        for chunk in chunks:
            if hasattr(chunk, 'content'):
                chunk_texts.append(chunk.content)
            else:
                chunk_texts.append(str(chunk))

        # 3. Generate embeddings
        embeddings = self.embedder.embed(chunk_texts)
        print(f"Generated {len(embeddings)} embeddings.")

        # 4. Combine chunk texts with their embeddings
        documents = list(zip(chunk_texts, embeddings))

        # 4. Add to the database
        initial_doc_count = self.database.get_document_count()
        self.database.add_documents(documents)
        final_doc_count = self.database.get_document_count()
        
        summary = {
            "status": "Success",
            "chunks_processed": len(chunks),
            "initial_doc_count": initial_doc_count,
            "final_doc_count": final_doc_count,
            "new_documents_added": final_doc_count - initial_doc_count
        }
        print("--- Ingestion process finished ---")
        print(f"Summary: {summary}")
        return summary

    def ingest_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Reads a text file and ingests its content.

        Args:
            file_path (str): The absolute path to the text file.

        Returns:
            Dict[str, Any]: A summary of the ingestion process.
        """
        print(f"Reading content from file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.ingest_text(content)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return {"status": "Error", "message": "File not found"}
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return {"status": "Error", "message": str(e)}


# --- Example Usage --- 
if __name__ == '__main__':
    print("--- Running RAG Ingestor Standalone Example ---")

    # Create a dummy text file for ingestion
    if not os.path.exists(INGESTION_SOURCE_DIR):
        os.makedirs(INGESTION_SOURCE_DIR)
    
    dummy_file_path = os.path.join(INGESTION_SOURCE_DIR, 'sample_transcript.txt')
    dummy_content = ( 
        "Artificial intelligence (AI) is intelligence demonstrated by machines, "
        "in contrast to the natural intelligence displayed by humans and animals. "
        "Leading AI textbooks define the field as the study of 'intelligent agents': "
        "any device that perceives its environment and takes actions that maximize its "
        "chance of successfully achieving its goals. The term 'artificial intelligence' "
        "was first coined by John McCarthy in 1956. AI research has been through several "
        "cycles of optimism, followed by disappointment and the loss of funding, known as an 'AI winter'. "
        "Funding and interest vastly increased after 2012 when deep learning surpassed all previous "
        "AI techniques. Deep learning is a subfield of machine learning that is based on artificial "
        "neural networks with representation learning. The learning can be supervised, semi-supervised or unsupervised."
    ) * 5 # Make the text long enough to be chunked
    
    with open(dummy_file_path, 'w', encoding='utf-8') as f:
        f.write(dummy_content)

    print(f"Created a dummy transcript at: {dummy_file_path}")

    # 1. Instantiate the components
    # This demonstrates the dependency injection principle
    text_chunker = TextChunker()
    # The factory makes it easy to switch between local and API embeddings
    embedder = EmbedderFactory.create_embedder() 
    vector_db = SQLiteVecDatabase()

    # 2. Instantiate the ingestor
    ingestor = RAGIngestor(
        chunker=text_chunker,
        embedder=embedder,
        database=vector_db
    )

    # 3. Run the ingestion process from the file
    ingestion_summary = ingestor.ingest_from_file(dummy_file_path)

    print("\n--- Example Run Finished --- ")
