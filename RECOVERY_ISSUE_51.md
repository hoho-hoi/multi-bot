# Issue #51 Recovery Ledger

This file records the recovery scope for the stacked-PR incident and defines the
verification steps required before closing the linked Issue.

## Unmerged Target Audit

| Issue | Original PR | Source branch | Original implementation commit | In `origin/main` before recovery? | Verification note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `#38` | `#40` | `feature/issue-38-engineer-execution-work-item` | `0aa3135e295cde7ad746324c28c67b9d169e8921` | Yes | `git merge-base --is-ancestor 0aa3135e295cde7ad746324c28c67b9d169e8921 origin/main` |
| `#36` | `#42` | `feature/issue-36-engineer-execution-bootstrap-from-issue-38` | `8f8c48fcd8d6279333ef29ebd90cfdc3a426da10` | Yes | `git merge-base --is-ancestor 8f8c48fcd8d6279333ef29ebd90cfdc3a426da10 origin/main` |
| `#39` | `#43` | `feature/issue-39-engineer-application-entrypoint` | `d6a420ed2c25106baa868ae29556a83b52f7ea87` | Yes | `git merge-base --is-ancestor d6a420ed2c25106baa868ae29556a83b52f7ea87 origin/main` |
| `#37` | `#44` | `feature/issue-37-implementation-pr-open-payload` | `0b72ff2cefe8015b0ef92bcac913adf6ae684f29` | Yes | `git merge-base --is-ancestor 0b72ff2cefe8015b0ef92bcac913adf6ae684f29 origin/main` |
| `#45` | `#49` | `feature/issue-45-manager-implementation-review-input` | `06fb37e65309b229af20d3af99efac92c5928fea` | No | `git merge-base --is-ancestor 06fb37e65309b229af20d3af99efac92c5928fea origin/main` returned non-zero |

## Recovery Actions

1. Start a dedicated recovery branch from `origin/main`.
   - Branch used for this repair: `feature/issue-51-recover-main-workflow`
2. Re-apply the missing implementation from issue `#45`.
   - Recovery method used here: `git cherry-pick -x 06fb37e65309b229af20d3af99efac92c5928fea`
3. Add guardrails that prevent the same stacked-PR pattern.
   - Implementation PR payloads now require `base_branch_name == "main"`.
   - Manager review input now includes `base_branch_name` and a dedicated
     `BASE_BRANCH_POLICY` review target.
   - Issue and PR templates now require `main`-based verification before Issue closure.

## Verification After Merge

Use at least one of the following checks before closing the linked Issue:

```bash
git diff --stat origin/main...feature/issue-51-recover-main-workflow
```

```bash
git log --oneline origin/main..feature/issue-51-recover-main-workflow
```

```bash
rg "BASE_BRANCH_POLICY|base_branch_name" src/shared_contracts tests .github CONTRIBUTING.md
```

## Usage Example

When a future recovery PR is ready, document the proof in the PR body like this:

```text
Verification evidence:
- `git diff --stat origin/main...feature/issue-51-recover-main-workflow`
- `git log --oneline origin/main..feature/issue-51-recover-main-workflow`
```
