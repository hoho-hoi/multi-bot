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

The project uses `uv` to provision Python 3.12 and install development dependencies.

```bash
make setup
```

## Usage Examples

Run static checks:

```bash
make lint
```

Run unit tests:

```bash
make test
```

Apply formatting:

```bash
make format
```

List available commands:

```bash
make help
```
