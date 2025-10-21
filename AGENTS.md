# Repository Guidelines

This document highlights the expectations for contributors working on the YouTube subtitle management and RAG tooling in this repository.

## Project Structure & Module Organization
- Core ingestion and CLI workflows live in `main.py`, `downloader.py`, `parser.py`, and supporting helpers in `utils.py` and `db.py`.
- Retrieval-Augmented Generation logic is in `rag_engine/` (chunkers, hybrid retrievers, docling parsers, CLI utilities) and `llm_service/` for model configuration and schemas.
- Streamlit and desktop entry points reside in `gui_streamlit.py`, `gui.py`, and `gui_unified.py`; assets and diagrams are under `docs/`.
- Automated validation and legacy coverage live in `tests/` (see `tests/README.md` for the full matrix), and bespoke runners in `scripts/run_rag_tests.py`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`) to isolate dependencies.
- `pip install -r requirements.txt` for core runtime packages; add `-r requirements-test.txt` before executing the suite.
- `streamlit run gui_streamlit.py` launches the primary UI; `python main.py --help` exposes the CLI transcript ingestion workflow.
- `pytest tests -m "not slow"` is the default smoke pass; use `python scripts/run_rag_tests.py --full-validation` for the curated RAG matrix and `--coverage` to mirror CI coverage reports.

## Coding Style & Naming Conventions
- Target Python 3.9+, four-space indentation, and `black` defaults (88 char line length) before each commit; follow with `isort .` and `flake8` to keep imports and lint warnings clean.
- Keep modules and functions in `snake_case`, classes in `CamelCase`, and constants uppercase; align new files with the patterns in `rag_engine`.
- Prefer type hints and docstrings for public functions so `mypy` and IDEs can reason about the pipeline steps.

## Testing Guidelines
- Tests are Pytest-based; scope granular checks under `tests/test_rag/` and fall back to `tests/legacy/` for classic parsing flows.
- Use markers already defined in `conftest.py` (e.g., `-m integration`, `-m regression`, `-m requires_llm`) to target subsets; keep new markers documented.
- Generate coverage with `pytest --cov=rag_engine --cov-report=html` and ensure new features maintain the existing coverage footprint before merge.

## Commit & Pull Request Guidelines
- Follow the conventional commit style used in history (`feat:`, `fix:`, `docs:`, `refactor:`) with concise, present-tense summaries.
- PRs should describe motivation, notable trade-offs, test evidence (`pytest` or `run_rag_tests.py` command output), and reference related issues or documents in `docs/` when relevant; include screenshots for UI-affecting changes.

## Environment & Security Notes
- Keep secrets in `.env` (e.g., `GEMINI_API_KEY`) and never hard-code credentials. Local SQLite databases (`subtitles.db`, `rag_database.db`) are developer-owned—reset or anonymize them before sharing traces.
