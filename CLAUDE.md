# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a YouTube subtitle downloader and AI-powered video management system. It downloads YouTube transcripts, processes them with local or cloud-based LLMs, and provides a video library interface. The project supports both local GGUF models (via llama-cpp-python) and Google Gemini API for transcript summarization.

**Main Repository**: https://github.com/Sorl4c/codex-transcript-youtube

## Activación Rápida

**Windows PowerShell:** `.venv\Scripts\activate.ps1`
**WSL/Linux:** `source .venv/Scripts/activate`

## Key Commands

**Always activate venv first:**

📖 **Referencia rápida**: Ver `ACTIVATION_COMMANDS.md` para todos los comandos de activación por sistema operativo.

### Windows (CMD)
```cmd
.venv\Scripts\activate.bat
```

### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

### WSL/Git Bash
```bash
source .venv/Scripts/activate
```

*Tip: Usa `cat ACTIVATION_COMMANDS.md` para ver todos los comandos disponibles*

### Running the Application

```bash
# Run the Streamlit web interface (recommended)
streamlit run gui_streamlit.py

# RAG CLI (Sesión 1 - MVP)
python -m rag_engine.rag_cli stats
python -m rag_engine.rag_cli query "Your question here" --top-k 5
python -m rag_engine.rag_cli ingest transcripts_for_rag/sample.txt --mock

# RAG CLI with DocLing (enhanced preprocessing)
python -m rag_engine.rag_cli ingest transcripts_for_rag/sample.txt  # DocLing enabled by default
python -m rag_engine.rag_cli ingest transcripts_for_rag/sample.txt --no-docling  # Traditional parsing

# Run CLI for single video processing
python main.py <youtube_url>

# Run CLI with output file
python main.py <youtube_url> -o output.txt

# Run CLI with language selection
python main.py <youtube_url> -l es

# Process local VTT file
python main.py path/to/subtitle.vtt -o output.txt

# Start the LLM microservice (FastAPI)
cd llm_service
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Testing

No automated test framework is configured. Tests exist in:
- `ia/tests/` - AI module tests
- Individual test files like `test_parser.py`, `test_db.py`

Run individual tests manually:
```bash
python test_parser.py
python ia/tests/test_core.py
```

### Dependencies

**IMPORTANT: Always use the virtual environment!**

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Install LLM service dependencies (optional)
pip install -r requirements_service.txt
```

**Note:** The venv was recreated in September 2025 to fix broken symlinks and add RAG dependencies (sentence-transformers, sqlite-vec, scikit-learn). Now uses standard `.venv/` naming convention.

## Architecture

### Core Processing Flow

1. **URL Input** → `downloader.py` → Downloads VTT subtitles using yt-dlp
2. **VTT Processing** → `parser.py` → Converts VTT to plain text
3. **Database Storage** → `db.py` → Stores in SQLite (`subtitles.db`)
4. **AI Processing** → `ia/` module → Generates summaries via local LLM or Gemini API

### Module Structure

**Main Entry Points:**
- `main.py` - CLI interface
- `gui_streamlit.py` - Streamlit web interface (recommended UI)
- `gui_unified.py` - Legacy tkinter interface (minimal maintenance)
- `gui.py` - Original GUI (deprecated)

**Core Modules:**
- `downloader.py` - YouTube subtitle download via yt-dlp
- `parser.py` - VTT to plain text conversion
- `db.py` - SQLite database operations
- `batch_processor.py` - Batch URL processing
- `utils.py` - Utility functions

**AI Module (`ia/`):**
- `core.py` - LLM initialization and core utilities
- `gemini_api.py` - Google Gemini API integration with cost calculation
- `native_pipeline.py` - Direct llama-cpp-python inference (optimized)
- `langchain_pipeline.py` - LangChain-based processing
- `summarize_transcript.py` - Main transcript summarization logic
- `prompts/` - Prompt templates (summary.txt, map_summary.txt, reduce_summary.txt)

**LLM Service (`llm_service/`):**
- FastAPI microservice providing OpenAI-compatible API for local GGUF models
- `main.py` - FastAPI application
- `model_loader.py` - Model management
- `schemas.py` - Pydantic models (OpenAI compatible)
- `config.py` - Service configuration

**RAG System:**
- **Enhanced RAG pipeline** with DocLing preprocessing (IBM Research)
- **Hybrid search** with vector + BM25 keyword search
- **Multiple chunking strategies**: characters, words, semantic, agentic
- **Local embeddings** using sentence-transformers
- **SQLite vector database** with sqlite-vec extension
- **DocLing integration** for intelligent document preprocessing
- **CLI interface** with flexible options

### Database Schema

SQLite database (`subtitles.db`) stores:
- `id` - Video ID
- `url` - YouTube URL
- `video_id` - YouTube video identifier
- `channel` - Channel name
- `title` - Video title
- `upload_date` - Upload date
- `transcript` - Full formatted transcript
- `summary` - AI-generated summary
- `key_ideas` - Key ideas (optional)
- `ai_categorization` - AI categorization (optional)

### AI Processing Modes

**Local Processing:**
- Uses GGUF models from `C:\local\modelos\` (Windows) or `/mnt/c/local/modelos/` (WSL)
- Supported models: TinyLlama, Mistral-7B, Qwen2-7B
- GPU acceleration via CUDA when available
- Two pipelines: native (faster) and langchain (structured)

**API Processing (Gemini):**
- Google Gemini API for cloud-based summarization
- Requires `GEMINI_API_KEY` in `.env` file
- Generates: summary, key ideas, optimized title
- Includes cost calculation and tracking

### Streamlit GUI Architecture

The `gui_streamlit.py` follows OOP design:

**Data Classes:**
- `Video` - Video data encapsulation

**Business Logic:**
- `DatabaseManager` - All DB operations with caching
- `YouTubeProcessor` - URL processing and local/API modes
- `VideoLibraryView` - Video table display and management
- `AnalysisView` - Detailed video analysis with filtering

**Key Features:**
- Two processing modes: Local (transcript only) and API (with AI summary)
- Interactive video library with search and sorting
- Channel-based filtering in analysis view
- Copy-to-clipboard functionality for transcripts/summaries
- Video deletion

## Environment Configuration

**Required `.env` file:**
```
GEMINI_API_KEY="your_api_key_here"
```

**Model paths:**
- Default local models directory: `C:\local\modelos\` (Windows)
- WSL path: `/mnt/c/local/modelos/`
- Configured in `ia/core.py` as `DEFAULT_MODEL_PATH`

## Important Notes

### Console Encoding (Windows)

The `main.py` automatically handles Windows console encoding to prevent Unicode errors. This is critical for displaying Spanish characters and other UTF-8 content.

### URL Pattern Recognition

The `YouTubeProcessor.get_video_id_from_url()` method in `gui_streamlit.py:82-91` handles multiple YouTube URL formats:
- Standard: `youtube.com/watch?v=`
- Short: `youtu.be/`
- Shorts: `youtube.com/shorts/`
- Live: `youtube.com/live/`
- Embed: `youtube.com/embed/`

### Processing Limitations

The `ia/summarize_transcript.py` script is experimental and processes **one transcript at a time only** (not batch processing).

### Model Management

Models are NOT included in the repository. They must be downloaded separately to the configured model directory. The project uses symlinks to `C:\local\modelos\` for model access.

### Git Configuration

The project tracks:
- Python source files
- Documentation in `docs/`
- Requirements files
- Configuration files

Excluded from git (`.gitignore`):
- `*.db` files
- Virtual environments (`venv/`)
- Model files (`*.gguf`)
- API keys (`.env`)
- Temporary files
- `__pycache__/`

## Development Workflow

1. **Activate virtual environment:**
- Ver `ACTIVATION_COMMANDS.md` para comandos específicos por sistema
- Comandos principales: `.venv\Scripts\activate.bat` (Windows) o `source .venv/Scripts/activate` (WSL)
2. Make changes to relevant module
3. Test using Streamlit interface or CLI
4. Check database with SQLite browser if needed
5. Update `docs/CHANGELOG.md` for significant changes
6. Update version in relevant files

## Architecture Diagrams

Project includes Mermaid diagrams in `docs/PROJECT_MAP.md` showing the complete module structure and data flow. View these in VS Code with "Markdown Preview Mermaid Support" extension or on GitHub.

## Common Issues

**Import Errors:** Ensure you're running from project root, not from subdirectories.

**Model Not Found:** Check that model path in `ia/core.py` matches your actual model location.

**Database Locked:** Only one process can write to SQLite at a time. Close other connections.

**Gemini API Errors:** Verify API key in `.env` and check internet connectivity.

**Streaming Response Handling:** The LLM service supports both streaming and non-streaming modes. For streaming, handle Server-Sent Events (SSE) properly.

**Virtual Environment Issues:** Ver `ACTIVATION_COMMANDS.md` para los comandos correctos:
- Windows (CMD): `.venv\Scripts\activate.bat`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- WSL/Git Bash: `source .venv/Scripts/activate`
