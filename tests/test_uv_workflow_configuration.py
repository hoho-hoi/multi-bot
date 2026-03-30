import tomllib
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def read_repository_file(relative_path: str) -> str:
    """Reads a repository file as UTF-8 text."""

    return (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")


def test_pyproject_uses_uv_dependency_groups_for_development_tools() -> None:
    pyproject_data = tomllib.loads(read_repository_file("pyproject.toml"))

    dependency_groups = pyproject_data.get("dependency-groups")

    assert dependency_groups == {"dev": ["mypy", "pytest", "ruff"]}
    assert pyproject_data["tool"]["uv"]["default-groups"] == ["dev"]

    project_table = pyproject_data["project"]
    assert "optional-dependencies" not in project_table


def test_makefile_uses_uv_sync_and_uv_run_commands() -> None:
    makefile_content = read_repository_file("Makefile")

    assert "$(UV) sync --frozen --group dev --python $(PYTHON_VERSION)" in makefile_content
    assert "$(UV) run --frozen --python $(PYTHON_VERSION) pytest" in makefile_content
    assert "$(UV) run --frozen --python $(PYTHON_VERSION) ruff check ." in makefile_content
    assert "$(UV) run --frozen --python $(PYTHON_VERSION) ruff format --check ." in makefile_content
    assert "$(UV) run --frozen --python $(PYTHON_VERSION) mypy --strict src" in makefile_content
    assert "pip install" not in makefile_content
    assert ".venv/bin" not in makefile_content


def test_readme_documents_uv_sync_and_reproducible_lock_file_workflow() -> None:
    readme_content = read_repository_file("README.md")

    assert "uv sync --frozen --group dev" in readme_content
    assert "uv.lock" in readme_content
    assert "make setup" in readme_content
    assert "uv run --frozen pytest" in readme_content


def test_ci_uses_frozen_uv_sync_with_committed_lock_file() -> None:
    ci_workflow_content = read_repository_file(".github/workflows/ci.yml")

    assert "astral-sh/setup-uv" in ci_workflow_content
    assert "uv sync --frozen --group dev" in ci_workflow_content
    assert "python -m pip install uv" not in ci_workflow_content


def test_uv_lock_file_is_committed_for_python_312() -> None:
    uv_lock_path = REPOSITORY_ROOT / "uv.lock"

    assert uv_lock_path.exists()
    assert 'requires-python = "==3.12.*"' in uv_lock_path.read_text(encoding="utf-8")
