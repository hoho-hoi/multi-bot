.PHONY: setup test lint format clean help

PYTHON_VERSION ?= 3.12
UV ?= uv

setup:
	$(UV) sync --frozen --group dev --python $(PYTHON_VERSION)

test:
	$(UV) run --frozen --python $(PYTHON_VERSION) pytest

lint:
	$(UV) run --frozen --python $(PYTHON_VERSION) ruff check .
	$(UV) run --frozen --python $(PYTHON_VERSION) ruff format --check .
	$(UV) run --frozen --python $(PYTHON_VERSION) mypy --strict src

format:
	$(UV) run --frozen --python $(PYTHON_VERSION) ruff check --fix .
	$(UV) run --frozen --python $(PYTHON_VERSION) ruff format .

clean:
	rm -rf ".venv" .mypy_cache .pytest_cache .ruff_cache
	rm -rf scratch/*

help:
	@echo "Available commands:"
	@echo "  make setup   - Sync the uv-managed Python 3.12 environment from uv.lock"
	@echo "  make test    - Run pytest through uv with the locked environment"
	@echo "  make lint    - Run Ruff and mypy through uv with the locked environment"
	@echo "  make format  - Apply Ruff fixes and formatting through uv"
	@echo "  make clean   - Remove caches and the local virtual environment"