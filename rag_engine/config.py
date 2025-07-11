"""
Configuration for the RAG engine.

Centralizes all key parameters for easy modification and testing.
"""

import os

# --- General Settings ---
# Determine the root directory of the project
# This assumes the script is run from within the project structure
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Database Settings ---
# Using an absolute path is more robust
DB_PATH = os.path.join(PROJECT_ROOT, 'rag_database.db')
DB_TABLE_NAME = "vector_store"

# --- Embedder Settings ---
# Options: 'local', 'api'
EMBEDDER_TYPE = 'local'

# Local sentence-transformer model
LOCAL_EMBEDDER_MODEL = 'all-MiniLM-L6-v2'

# API settings (compatible with OpenAI standard)
# This leverages the existing llm_service
API_EMBEDDER_URL = "http://localhost:8000/v1/embeddings"
API_EMBEDDER_MODEL = "local_model" # The model name served by the local API

# --- Chunker Settings ---
CHUNK_SIZE = 1000  # Target size in characters
CHUNK_OVERLAP = 200 # Characters to overlap between chunks

# --- Ingestor Settings ---
# Directory to store raw text files for ingestion
INGESTION_SOURCE_DIR = os.path.join(PROJECT_ROOT, 'transcripts_for_rag')