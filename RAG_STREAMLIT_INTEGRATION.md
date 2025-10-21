# RAG + Streamlit Integration Guide

## Overview

This guide documents the integration of the RAG (Retrieval-Augmented Generation) system with the Streamlit GUI, providing users with semantic search capabilities across their video transcripts.

## Features

### 🔍 Semantic Search
- **Vector Search**: Find content based on semantic similarity using sentence transformers
- **Keyword Search**: Traditional BM25 keyword matching for exact terms
- **Hybrid Search**: Combines vector and keyword search using Reciprocal Rank Fusion (RRF)

### 📊 Real-time Statistics
- Track number of documents in the RAG database
- Monitor database size and type
- View embedder information
- System availability status

### 🚀 Automatic Ingestion
- Option to automatically ingest transcripts during video processing
- Support for both Local and API processing modes
- DocLing preprocessing for enhanced document understanding

## Usage

### 1. Access the RAG Interface

1. Run the Streamlit application:
   ```bash
   streamlit run gui_streamlit.py
   ```

2. Navigate to the **"Búsqueda RAG"** tab in the sidebar

### 2. Configure Search Parameters

- **Question**: Enter your search query in natural language
- **Search Mode**: Choose between:
  - `vector`: Semantic search using embeddings
  - `keyword`: BM25 keyword search
  - `hybrid`: Combined vector + keyword search (recommended)
- **Results**: Number of results to return (1-10)

### 3. View Results

Each result includes:
- **Content**: The relevant transcript segment
- **Score**: Relevance score (higher = more relevant)
- **Metadata**: Additional information about the match
- **Copy Button**: Quick copy to clipboard functionality

### 4. Automatic Ingestion

When processing new videos in the **"Agregar Vídeos"** tab:

1. Check the **"Ingestar en RAG"** option
2. Select your processing mode (Local or API)
3. Process URLs as usual
4. Transcripts will be automatically ingested into the RAG system

## Technical Details

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│   RAGInterface   │───▶│   RAG Engine    │
│     GUI         │    │   (rag_interface.py) │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  SQLite Vec DB   │
                       │  (rag_database.db)│
                       └──────────────────┘
```

### Key Components

1. **RAGInterface** (`rag_interface.py`)
   - Wrapper for the RAG system
   - Handles ingestion and querying
   - Provides statistics and status information

2. **YouTubeProcessor** (modified)
   - Integrated with RAG interface
   - Automatic transcript ingestion
   - Error handling and user feedback

3. **StreamlitApp** (modified)
   - New "Búsqueda RAG" page
   - Integration with existing GUI architecture
   - Real-time statistics display

### Dependencies

Required packages (already in `requirements.txt`):
```
sentence-transformers>=5.1.0  # Local embeddings
sqlite-vec>=0.1.6              # Vector database
scikit-learn>=1.7.0           # ML utilities
rank-bm25>=0.2.0              # BM25 search
docling>=2.0.0                # Document preprocessing
```

## Troubleshooting

### RAG System Not Available

If you see "Sistema RAG no disponible":

1. **Check Dependencies**: Ensure all RAG packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Virtual Environment**: Make sure you're using the correct venv:
   ```bash
   # Windows
   .venv\Scripts\activate

   # WSL/Linux
   source .venv/Scripts/activate
   ```

3. **Check RAG Engine**: Verify the RAG engine is accessible:
   ```bash
   python -m rag_engine.rag_cli stats
   ```

### No Search Results

If searches return no results:

1. **Ingest Transcripts**: Make sure you have ingested content:
   - Use the "Ingestar en RAG" option when processing videos
   - Or ingest manually via CLI:
     ```bash
     python -m rag_engine.rag_cli ingest transcript.txt
     ```

2. **Check Database**: Verify database has content:
   ```bash
   python -m rag_engine.rag_cli stats
   ```

3. **Try Different Queries**: Experiment with different question phrasing

### Performance Issues

For optimal performance:

1. **Use Hybrid Search**: Recommended for best results
2. **Limit Results**: Start with 3-5 results
3. **Clear Database**: If needed, reset the database:
   ```python
   from rag_interface import get_rag_interface
   rag = get_rag_interface()
   rag.clear_database()
   ```

## API Reference

### RAGInterface Class

#### Methods

- `is_available()`: Check if RAG system is available
- `get_stats()`: Get database statistics
- `ingest_transcript(video_id, title, transcript, strategy, use_docling)`: Ingest transcript
- `query(question, mode, top_k)`: Search the RAG database
- `get_available_strategies()`: Get chunking strategies
- `get_available_modes()`: Get search modes
- `clear_database()`: Clear all data

#### Data Classes

- `RAGResult`: Search result with content, score, and metadata
- `RAGStats`: Database statistics and system information

## Examples

### Sample Queries

Try these sample queries to test the system:

- "¿Qué ejercicios recomiendan para principiantes?"
- "machine learning basics"
- "cómo mejorar la productividad"
- "tips para estudiar mejor"

### Programmatic Usage

```python
from rag_interface import get_rag_interface

# Get RAG interface
rag = get_rag_interface()

# Check availability
if rag.is_available():
    # Search
    results, error = rag.query("machine learning", mode="hybrid", top_k=5)

    # Get stats
    stats = rag.get_stats()
    print(f"Documents: {stats.total_documents}")
```

## Future Enhancements

Planned improvements:

1. **Advanced Filtering**: Filter by date, channel, or video metadata
2. **Export Results**: Export search results to various formats
3. **Search History**: Save and revisit previous searches
4. **Batch Ingestion**: Ingest multiple existing transcripts
5. **Performance Monitoring**: Detailed performance metrics
6. **Custom Embeddings**: Support for custom embedding models

## Contributing

To contribute to the RAG integration:

1. Test changes with the integration test suite:
   ```bash
   python tests/test_rag_streamlit_integration.py
   ```

2. Follow the existing code patterns in `rag_interface.py` and `gui_streamlit.py`

3. Update documentation for new features

4. Ensure backward compatibility with existing functionality