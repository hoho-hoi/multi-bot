# Multi-Bot Bootstrap Baseline

This repository provides the initial Python 3.12 monorepo baseline for the multi-bot
development workflow. The setup focuses on clear package boundaries so future
implementation issues can evolve `control_plane`, `worker_runtime`, and
`shared_contracts` independently.

## Repository Structure

- `src/control_plane/`: orchestration-facing entrypoints.
- `src/worker_runtime/`: execution-facing entrypoints.
- `src/shared_contracts/`: shared DTOs and contracts used across boundaries.
- `tests/`: bootstrap validation tests.

## Local Setup

The project uses `uv` as the source of truth for Python package management, dependency
locking, and command execution. The committed `uv.lock` file is used for both local
development and CI so the same dependency set is resolved everywhere.

```bash
make setup
```

The `make setup` target runs the equivalent `uv` command directly:

```bash
uv sync --frozen --group dev
```

## Usage Examples

Run static checks with the locked environment:

```bash
make lint
```

Run the same test suite command directly through `uv`:

```bash
uv run --frozen pytest
```

Or use the Make target wrapper:

```bash
make test
```

Apply formatting through `uv`:

```bash
make format
```

Refresh the lock file after dependency changes:

```bash
uv lock
uv sync --frozen --group dev
```

List available commands:

```bash
make help
```
