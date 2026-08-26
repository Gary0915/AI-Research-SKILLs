# Thesis Deck System — Codex ↔ Reviewer Protocol

## Roles
- **Codex:** implementer. Inspects repository, proposes changes, writes code/assets/tests, runs validation, and reports exact implementation evidence.
- **ChatGPT:** reviewer/spec owner. Defines acceptance criteria, audits Codex reports/diffs/artifacts, and returns `APPROVE`, `REVISE`, or `REJECT` plus the next scoped task.

## Gate rule
Codex must not silently advance across a major phase boundary. Every major phase ends with an implementation report and `status: awaiting_review`.

## What Codex must report after implementation phases
Every implementation report must contain:

1. **Objective completed** — exact scope attempted.
2. **Architecture decisions** — decisions made and why.
3. **Files changed** — exact paths, grouped by added/modified/deleted.
4. **Behavior implemented** — user-visible and internal behavior.
5. **Commands/tests run** — exact commands.
6. **Test results** — pass/fail counts and relevant output.
7. **Artifacts produced** — PPTX, SVG, PNG, JSON/YAML, montage, logs, etc.
8. **Visual QA evidence** — render paths and what was inspected.
9. **Scientific/provenance QA evidence** — citation/data provenance checks where applicable.
10. **Known failures / technical debt** — never hide failures.
11. **Deviations from reviewer prompt** — explicit and justified.
12. **Questions requiring reviewer decision**.
13. **Recommended next phase** — do not execute it until approved.

## Required footer

```yaml
codex_report:
  phase: <PHASE_ID>
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: <sha-or-null>
  files_added: []
  files_modified: []
  files_deleted: []
  artifacts: []
  render_previews: []
  tests_run: []
  tests_passed: []
  tests_failed: []
  known_failures: []
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```

## Reviewer verdict format
ChatGPT reviewer returns one of:

### APPROVE
- acceptance criteria met
- may proceed to the specifically stated next phase

### REVISE
- architecture is acceptable but defects/gaps remain
- Codex receives a bounded correction task

### REJECT
- core approach violates requirements or is not salvageable without redesign
- Codex receives a replacement design/task

## Review priorities
Order of priority:
1. scientific correctness and evidence provenance
2. preservation of cumulative research history
3. editability/reproducibility
4. professor-specific Scientific Method logic
5. visual hierarchy and consistency
6. PowerPoint engineering correctness
7. automation convenience

## Non-negotiable anti-patterns
Reject or require revision if Codex:
- deletes failed experiments/history instead of preserving provenance,
- fabricates citations/data/literature figures,
- treats generated images as experimental evidence,
- flattens the entire presentation to screenshots,
- bypasses the template/master strategy without justification,
- produces a deck without render-based QA,
- claims tests passed without reporting commands/results,
- continues to a major new phase without review.
