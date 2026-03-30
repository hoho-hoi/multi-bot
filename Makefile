.PHONY: setup test lint format clean help check-virtual-environment

PYTHON_VERSION ?= 3.12
UV ?= uv
VIRTUAL_ENVIRONMENT_DIRECTORY := .venv
VIRTUAL_ENVIRONMENT_BIN := $(VIRTUAL_ENVIRONMENT_DIRECTORY)/bin
PYTEST_EXECUTABLE := $(VIRTUAL_ENVIRONMENT_BIN)/pytest
RUFF_EXECUTABLE := $(VIRTUAL_ENVIRONMENT_BIN)/ruff
MYPY_EXECUTABLE := $(VIRTUAL_ENVIRONMENT_BIN)/mypy

setup:
	$(UV) venv --python $(PYTHON_VERSION) $(VIRTUAL_ENVIRONMENT_DIRECTORY)
	$(UV) pip install --python $(VIRTUAL_ENVIRONMENT_BIN)/python -e ".[dev]"

check-virtual-environment:
	@test -x "$(VIRTUAL_ENVIRONMENT_BIN)/python" || (echo "Run 'make setup' first." && exit 1)

test: check-virtual-environment
	$(PYTEST_EXECUTABLE)

lint: check-virtual-environment
	$(RUFF_EXECUTABLE) check .
	$(RUFF_EXECUTABLE) format --check .
	$(MYPY_EXECUTABLE) --strict src

format: check-virtual-environment
	$(RUFF_EXECUTABLE) check --fix .
	$(RUFF_EXECUTABLE) format .

clean:
	rm -rf "$(VIRTUAL_ENVIRONMENT_DIRECTORY)" .mypy_cache .pytest_cache .ruff_cache
	rm -rf scratch/*

help:
	@echo "Available commands:"
	@echo "  make setup   - Create a Python 3.12 virtual environment and install dev dependencies"
	@echo "  make test    - Run the pytest suite"
	@echo "  make lint    - Run Ruff checks and mypy strict type checking"
	@echo "  make format  - Apply Ruff fixes and formatting"
	@echo "  make clean   - Remove caches and the local virtual environment"