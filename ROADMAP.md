# Project Roadmap & Status

## Current Status
- **Phase:** Phase 1 (Setup)
- **Status Summary:** Issue `#2` establishes the Python 3.12 monorepo baseline so the
  repository can move from requirements definition into implementation-oriented work.
- **Active Issues:**
  - `#2` Python monorepo baseline, CI, and roadmap alignment
  - Next implementation issues will target shared contracts, control-plane orchestration,
    and worker-runtime execution flows after the setup baseline is merged.

## Milestones

### v0.1 (MVP)
- [x] `Setup`: define Python 3.12 tooling, package boundaries, CI, and local development
  commands.
- [ ] `UC_DEFINE_REQUIREMENTS_WITH_ARCHITECT`: complete the requirement discovery workflow
  from issue conversation to requirement PR closure.
- [ ] `UC_ORCHESTRATE_DELIVERY_WITH_MANAGER`: automate planning, review, and milestone
  orchestration from GitHub events.
- [ ] `UC_IMPLEMENT_ISSUE_WITH_ENGINEER`: automate issue-driven implementation, testing,
  pull request creation, and feedback handling.

### Backlog (Refactoring & Future)
- [ ] Migrate GitHub automation from workflow-driven credentials to a dedicated GitHub App.
- [ ] Add provider adapters beyond the initial Cursor-oriented execution path.
- [ ] Introduce a persistent session store to replace the initial in-memory session model.
- [ ] Split the monorepo into independently deployable services when operational needs justify
  the boundary.

> NOTE: `ROADMAP.md` is maintained by the Manager (or human owner) as the single source of truth for high-level progress.