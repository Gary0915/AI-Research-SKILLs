# Phase 3 Checkpoint 4 — Revision 3 Implementation Report

## 1. Objective completed

Corrected CP4-D1 through CP4-D5 only, preserving CP4-C1 through CP4-C6. CP4 remains a sanitized-domain figure
control plane: it routes and validates contracts, but does not open private
sources, render/generate figures, calibrate A01–A18 geometry, create PPTX, or
start a later checkpoint.

## 2. Architecture decisions

- Production routing requires the committed CP3 Visual Style Governor profile;
  there is no `VSP003` default object.
- Ten route variants are registered once and validated cross-field by the
  schema registry: class, figure type, specialist, renderer, output, evidence
  state, and AI permission cannot be cross-wired.
- A closed `FigureRoutingRequest` contract owns nested scientific, empirical,
  fabrication, Fishbone, and style inputs before normalization.
- The single canonical post-render handoff is `FigureOutputManifest`.
  FigureCritic accepts it and Layout accepts only `APPROVED_FIGURE`.
- Disposable regression evidence carries a pre-execution tested-candidate hash;
  finalization recomputes the current hash and fails on inequality.
- The public router validates its final FigureProductionPlan before return;
  route evidence provenance is an explicit class-policy matrix rather than an
  incidental enum coupling.
- v4 ScientificFigureSpec is a deterministic, exact policy projection of one
  FigureProductionPlan. It retains the plan ref, source requirement, AI and
  native policies, styles, material-color block, and scientific bindings.
- Every declared `allowed_downstream` entry is a graph edge. The audit now
  checks all of them for target existence, input/output compatibility, and the
  mandatory FigureCritic gate before Layout.

## 3. Files changed

No files added in Revision 3.

Modified:

- `packages/thesis-deck-system/src/thesis_deck_system/contracts.py`
- `packages/thesis-deck-system/src/thesis_deck_system/phase3_checkpoint4.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py`
- `thesis-deck-system/schemas/figure-production-plan.schema.json`
- `thesis-deck-system/schemas/scientific-figure-spec.schema.json`
- `thesis-deck-system/skill-routing.yaml`
- `thesis-deck-system/artifacts/phase3/figure-production-plans.json`
- `thesis-deck-system/artifacts/phase3/scientific-figure-specs.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json`
- this report

Deleted: none.

## 4. Behavior implemented

### CP4-C1 — fail-closed style consumption

`route_figure_request()` requires an actual schema-valid CP3 profile with an
approved status and category coverage. Missing, malformed, or stale profile
references fail. Every plan/spec binds the consumed profile ID and records
route-specific category readiness. Material semantic colors remain blocked.

### CP4-C2 — route discriminators

The registry enforces the ten bounded visual-class mappings for both v4 plans
and specs. The focused suite mutates figure type, specialist, renderer, output
kind, and evidence state across every class; each mismatch is rejected.

### CP4-C3 — closed routing request

`FigureRoutingRequest` is registered with recursive `additionalProperties:
false` contracts. Its fabrication step, Fishbone binding, scientific refs,
style ref, and empirical slots are typed. Organic concepts require
`non_evidence` and cannot bind observation, experimental, quantitative, or
literature evidence.

### CP4-C4 — compatible graph

All future output-manifest names were normalized to `FigureOutputManifest`.
The graph audit checks node existence, declared downstream targets, output to
consumer-input compatibility, dangling targets, contract mismatches, and
pre-Critic Layout bypasses. The persisted audit reports zero for each failure
counter.

### CP4-C5 — independent regression binding

The disposable harness captured the tested candidate hash before its final
test run. CP4 finalization recomputed the current composite from six CP3
inputs, CP4 source, `contracts.py`, seven CP4 schemas, routing YAML, and all
17 local Skill documents (33 components). The persisted tested/current hashes
are equal; mutation tests prove stale evidence changes aggregate QA to fail.

### CP4-C6 — evidence-rich QA and truth

Each owning check now stores counts, IDs, and/or hashes rather than an opaque
boolean. The execution record reports six CP3 inputs, ten exercised classes,
17 Skills, 18 archetypes, graph counters, schema count, privacy configuration
hash, and regression facts. The authoritative scanner executed both repository
and staged scans with zero unexcepted findings and one reviewed legacy
exception; the prior count was preserved rather than silently reset.

### CP4-D1 — self-validating public router and evidence policy

`route_figure_request()` now executes request validation, route/evidence-policy
resolution, plan construction, and the registered canonical
`figure-production-plan` validation before returning. Strict routes reject
wrong provenance directly at this boundary. Mechanism and fair-comparison
routes retain a controlled empirical-or-literature alternative without changing
their specialist director.

### CP4-D2 — typed source requirement survives

Every v4 plan and spec records one controlled `source_requirement`:
`canonical_data`, `real_evidence`, `literature_source`, `structured_spec`, or
`non_evidence_only`. `source_asset_required` is checked as its derived boolean,
not used as a lossy substitute.

### CP4-D3 — lossless plan-to-spec safety policy

Every spec has exactly one `figure_plan_ref`. The projection copies all
safety-critical policy and source/scientific bindings; owning QA records 10
plans, 10 specs, 10 exact bindings, and zero mismatches or orphans.

### CP4-D4 — all declared graph edges audited

The Skill graph treats each `allowed_downstream` value as a declared edge,
including unselected edges. It rejects unknown targets, contract mismatches,
and pre-Critic Layout paths. The acceptance registry has 21 nodes, 17 declared
edges, 17 handoff edges, and zero dangling/mismatch/bypass counts.

### CP4-D5 — execution-owned final handoff evidence

Final QA includes router self-validation, evidence-policy matrix coverage,
source-requirement reconciliation, plan/spec policy binding, all-edge graph
audit, candidate/hash equality, 17-Skill registry, 18-archetype routing, CP3
style identity/readiness, schema closure, and repository/staged privacy scans.

## 5. Commands/tests run

- RED: `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py -q` — direct new boundary tests failed before their implementation.
- GREEN focused: same command — **36 passed, 0 failed**.
- Full isolated candidate regression: `python -m pytest packages/thesis-deck-system/tests -q` in the disposable worktree — **316 passed, 0 failed**.
- The isolated run was started only after locally capturing its candidate-state
  hash; no CP4 source/schema/routing/Skill component changed before finalization.
- SchemaRegistry with Draft 2020-12 `FormatChecker` validated all CP3 inputs,
  the closed request, CP4 output schemas, and regenerated records.
- Repository/staged privacy scan, graph audit, 17-Skill audit, 18-archetype
  audit, recursive schema closure, and `git diff --check` were run.

## 6. Test results

- Focused CP4 Revision 3: 36 passed, 0 failed.
- CP1+CP2+CP3+CP4 package regression (disposable): 316 passed, 0 failed.
- Full disposable regression: 316 passed, 0 failed.

## 7. Artifacts produced

- `thesis-deck-system/artifacts/phase3/figure-production-plans.json`
- `thesis-deck-system/artifacts/phase3/scientific-figure-specs.json`
- `thesis-deck-system/artifacts/phase3/archetype-figure-routing.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json`

## 8. Visual QA evidence

No rendering is authorized in CP4. Production figure rendering, FigureCritic
visual acceptance, archetype calibration, template reconstruction, acceptance
deck, and native PowerPoint acceptance remain `not_run`. No private render,
PPTX, PNG, SVG, or PDF was produced.

## 9. Scientific/provenance QA evidence

All plans retain canonical source/Claim/Evidence/Layer/Block/Stage/cursor
bindings. Empirical, photo, literature, and quantitative routes reject AI
generation. Concept remains non-evidence. Fishbone preserves revision/focus/
history references; fabrication stays separate and retains `unknown` conditions.
Private alias/source/render counters are `0 / 0 / 0`.

## 10. Known failures / technical debt

- Native-shape eligibility is intentionally `insufficient_evidence`; SVG-first
  remains the conservative structured-diagram policy.
- Future FigureOutputManifest production and FigureCritic visual review remain
  outside the authorization boundary.
- The required disposable worktrees and temporary test logs are local-only
  verification infrastructure, not repository artifacts.

## 11. Deviations from reviewer prompt

None. The report uses a documented self-referential footer convention: the
footer cannot contain its own final Git commit SHA without changing that SHA.
It records `pending_final_commit` and the final delivery provides the verified
commit identity.

## 12. Questions requiring reviewer decision

None.

## 13. Recommended next phase

Stop at Checkpoint 4 and await review. Do not render production figures,
calibrate archetypes, reconstruct templates, create a deck, or begin Phase 4.

```yaml
codex_report:
  phase: PHASE_3_CHECKPOINT_4
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: pending_final_commit
  files_added: []
  files_modified:
    - packages/thesis-deck-system/src/thesis_deck_system/contracts.py
    - packages/thesis-deck-system/src/thesis_deck_system/phase3_checkpoint4.py
    - packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py
    - thesis-deck-system/schemas/figure-production-plan.schema.json
    - thesis-deck-system/schemas/scientific-figure-spec.schema.json
    - thesis-deck-system/skill-routing.yaml
    - thesis-deck-system/artifacts/phase3/figure-production-plans.json
    - thesis-deck-system/artifacts/phase3/scientific-figure-specs.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json
    - thesis-deck-system/reports/PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md
  files_deleted: []
  artifacts:
    - thesis-deck-system/artifacts/phase3/figure-production-plans.json
    - thesis-deck-system/artifacts/phase3/scientific-figure-specs.json
    - thesis-deck-system/artifacts/phase3/archetype-figure-routing.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json
  render_previews: []
  tests_run:
    - focused CP4 Revision 3 RED to GREEN
    - disposable package regression
  tests_passed:
    - 36 focused CP4 Revision 3 tests
    - 316 disposable package regression tests
  tests_failed: []
  known_failures: []
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```
