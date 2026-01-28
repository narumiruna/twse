# Repository Guidelines

## Project Structure & Module Organization
- `src/twse/` contains the package implementation (e.g., `stock_info.py`, `utils.py`) and `py.typed` for type hints.
- `tests/` holds pytest suites (e.g., `tests/test_stock_info.py`) and fixtures under `tests/testdata/`.
- `example.py` provides a runnable usage example.
- `pyproject.toml` defines dependencies, tooling, and lint/type settings.
 - Public API entry points: `get_stock_info_sync` (sync) and `get_stock_info` (async).

## Build, Test, and Development Commands
Use `uv`-backed Make targets to ensure consistent environments:
- `make format`: Run Ruff formatter.
- `make lint`: Run Ruff lint checks.
- `make type`: Run Ty type checks.
- `make test`: Run pytest with coverage on `src/`.
- `make publish`: Build and publish the wheel (requires `PYPI_TOKEN`).

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints for public interfaces, and concise docstrings where behavior is non-obvious.
- Ruff enforces formatting and lint rules; max line length is 120.
- Module/function names: `snake_case`. Classes: `CapWords`. Constants: `UPPER_SNAKE_CASE`.
- Keep imports sorted and single-line per Ruff isort settings.

## Testing Guidelines
- Framework: `pytest` with `pytest-cov`.
- Naming: tests live in `tests/` and follow `test_*.py` and `test_*` function names.
- Run locally with `make test` or `uv run pytest -v -s --cov=src tests`.

## Commit & Pull Request Guidelines
- Use short, imperative commit subjects (e.g., "add retry for TWSE requests").
- Conventional Commits are acceptable but optional (e.g., `chore: update deps`).
- PRs should include: a brief summary, testing evidence (`make test` output), and any API or behavior changes.

## Security & Configuration Tips
- Avoid committing credentials; publishing requires `PYPI_TOKEN`.
- Treat network responses as untrusted input and validate fields before use.
