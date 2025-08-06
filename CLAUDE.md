# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python machine learning project for predicting fouls for players. The repository is currently in its initial state with only basic documentation and project structure.

## Project Status

**Current State**: Newly initialized repository
- Contains only README.md and .gitignore
- No source code, dependencies, or configuration files yet
- Ready for development setup

## Development Setup

Since this is a fresh Python ML project, development setup will likely require:

1. **Virtual Environment**: Create and activate a Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Dependencies**: Install dependencies once requirements are defined
   ```bash
   pip install -r requirements.txt
   # or if using other package managers:
   # pip install -e .
   # poetry install
   # pdm install
   ```

## Expected Project Structure

Based on the .gitignore configuration, this project is set up to support:
- Standard Python development tools (pytest, coverage, mypy, ruff)
- Multiple package managers (pip, poetry, pdm, uv, pixi)
- Jupyter notebooks for experimentation
- Various Python frameworks (Django, Flask, etc.)
- ML/Data science workflows

## Linting and Code Quality

The .gitignore includes Ruff cache (`.ruff_cache/`), suggesting Ruff will likely be used for:
- Code formatting
- Linting
- Import sorting

Once configured, typical commands would be:
```bash
ruff check .
ruff format .
```

## Testing

The .gitignore is configured for pytest and coverage tools. Expected commands:
```bash
pytest
python -m pytest tests/
```

## Important Notes

- This is a defensive security-focused ML project for foul prediction
- The repository supports modern Python package managers and development tools
- IDE support is configured for both VS Code and Cursor
- Environment files (.env) are ignored for security