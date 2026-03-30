# Contributing Guide

This project follows a strict **"Self-Validating AI Development Ecosystem"**.

## Roles & Workflow

1.  **Architect:** Defines requirements in `REQUIREMENT.md`.
2.  **Manager:** Manages Issues and reviews PRs.
3.  **Engineer:** Implements features using strict TDD.

## For Human Operators

- **Do not** copy-paste code between chats. Use `gh` commands or file reads.
- **Do not** bypass CI. If CI fails, the PR is invalid.
- **Follow the Signs:** Look for `::: action` blocks in AI responses.

## Branching & Closure Rules

- Start every delivery branch from `origin/main`.
- Open every implementation or recovery PR against `main`.
- Do not use stacked PRs for normal delivery work.
- Keep the linked Issue open until the implementation is visible on `main`.

## Verification Example

Use one of these checks before closing the linked Issue:

- `git merge-base --is-ancestor <commit-on-main-path> origin/main`
- `git diff --stat origin/main...<recovery-branch>`
- Review the merged PR diff against `main`

## For AI Agents

- **Read Rules First:** Always reference `.cursor/rules/*.mdc`.
- **Isolation:** You are disposable. Do not rely on conversation history from other tasks.
- **TDD:** `make test` (Red) -> Code -> `make test` (Green) is MANDATORY.
- **Configuration:** Tech stack details are in `tech-stack.mdc` (Dynamic). Do not assume specific languages unless defined there.