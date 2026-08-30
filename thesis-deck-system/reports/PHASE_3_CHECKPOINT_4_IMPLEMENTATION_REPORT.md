# Phase 3 Checkpoint 4 — Implementation Report

## 1. Objective completed

Implemented Checkpoint 4 only: the sanitized-domain Scientific Figure Control
Plane and schema-versioned repository-local Skill routing. It creates plans,
specifications, routing evidence, a complete A01–A18 routing matrix, and
execution-owned QA. It does not render or generate any figure/PPTX/PDF/PNG,
does not calibrate archetype geometry, and does not access private exemplars.

## 2. Architecture decisions

- Scientific authority stays in the existing canonical ledger/materialized
  state. CP4 plans preserve source, Claim, Evidence, Layer, Block, Stage, and
  cursor bindings but cannot create scientific content.
- CP3 artifacts are the sole visual input. The current partial structural
  calibration is retained: governed use may be recurring, provisional,
  fallback, or unresolved; material-semantic colors remain blocked.
- Routing is one deterministic class-to-specialist map. Fabrication is a
  distinct route and cannot be absorbed by mechanism or experiment schematic.
- Structured diagram routes default to vector. With no measured native-shape
  threshold, the plan records `insufficient_evidence` rather than enabling a
  convenient native route.
- FigureCritic is a mandatory later gate. Layout Director accepts only an
  `APPROVED_FIGURE` with provenance; raw specs and unapproved outputs fail.

## 3. Files changed

Added:

- `packages/thesis-deck-system/src/thesis_deck_system/phase3_checkpoint4.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py`
- CP4 schemas for archetype routing, execution evidence, and QA.
- 13 bounded repo-local specialist Skill contracts.
- five CP4 generated JSON artifacts under `thesis-deck-system/artifacts/phase3/`.
- this report.

Modified:

- Phase 3 schema registry and compatible Figure Plan/Figure Spec/Skill Routing
  contracts.
- `thesis-deck-system/skill-routing.yaml`.
- four existing local Skill contracts: thesis-deck-router, fishbone-director,
  layout-director, and professor-qa.

Deleted: none.

## 4. Behavior implemented

### CP4-1 — FigureProductionPlan

`FigureProductionPlan` is a closed v4 contract with explicit visual class,
scientific purpose, evidence/claim status, canonical source bindings, selected
specialist, renderer/output policy, native-shape eligibility, CP3 style policy,
required QA, handoff, status, and typed specialist payload. The legacy v3
contract remains schema-compatible for approved CP1 regression fixtures.

### CP4-2 — ScientificFigureSpec

Added strongly typed v4 Figure Specs emitted only for CP4's deterministic
synthetic routing acceptance set. Specs contain cursor/scientific bindings,
canvas, typed empty component collections (no free-form fields), provenance,
output targets, QA requirements, and specialist payload. They are contracts,
not rendered figures.

### CP4-3 / CP4-4 — specialist and renderer routing

The router handles quantitative plots, real photos, literature figures,
mechanisms, experiment schematics, fabrication processes, Fishbone history,
comparisons, matrices, and non-evidence concepts. Quantitative, real, and
literature sources reject AI generation. Structured diagrams route to
deterministic SVG/vector while native eligibility remains insufficient.

### CP4-B1 — actual style identity and route readiness

The router consumes the approved CP3 `visual-style-profile.json` and binds its
actual `style_profile_id` (`VSP003`) to every plan/spec. Route-specific category
records retain CP3 readiness, consumption mode, profile provenance, and any
blocking state; material semantic colors remain explicitly unresolved.

### CP4-B2 / CP4-B3 — discriminated, 10-class acceptance

The deterministic acceptance set exercises all ten supported visual classes.
Each plan/spec uses its route-consistent FigureSpec type, specialist, renderer,
canonical output, evidence/source requirement, AI policy, and native threshold
state. No empirical, literature, photo, or concept route is represented as a
generic vector diagram.

### CP4-B4 / CP4-B5 — graph and Observation boundaries

Registry routes now enter `scientific-figure-router`; specialists pass through
the future output-manifest stage before FigureCritic, and no scientific route
can reach Layout directly. `FigureRoutingRequest` is closed: organic concepts
must have non-evidence status with empty claim/evidence/empirical slots.

### CP4-B6 — candidate-bound disposable regression

`CP4-DISPOSABLE-REGRESSION` binds the exact composite candidate hash to the
disposable-worktree suite identity and pass/fail counts. The component map
includes all six CP3 inputs, CP4 source, `contracts.py`, all CP4 schemas,
routing YAML, and all 17 local Skill contracts; source, schema, routing, skill,
or CP3-input changes invalidate prior evidence.

### CP4-5 / CP4-6 — style and Observation boundaries

Plans reference the consumed `VSP003`, preserve CP3's partial/provisional/fallback state,
and block unresolved material-semantic colors. Concepts require
`non_evidence`, forbidden claim support, and zero evidence bindings; therefore
they cannot satisfy Observation or any empirical reference.

### CP4-7 / CP4-8 — Skill registry and handoff graph

The local registry contains exactly the 17 authorized identities and each
local Skill declares trigger, exclusion, input/context, workflow, bounded
downstream authority, forbidden actions, output/provenance/failure/blocked
contracts, handoff, and QA owner. The graph is persisted as:

`scientific_state → FigureProductionPlan → selected_specialist_director →
future_renderer_output_manifest → figure-critic → APPROVED_FIGURE →
layout-director`.

### CP4-9 — A01–A18 routing matrix

All 18 archetypes have routing-only records. A03 binds Fishbone; A04 is a real
empirical route; A05 pairs literature/mechanism; A06/A07/A09 expose separate
fabrication routing; A10/A11/A13 include result/plot routes; A12 matrix;
A16 deterministic transition/mechanism; all geometry statuses are `not_run`.

### CP4-10 / CP4-11 / CP4-12 — owning QA, candidate binding, status truth

Execution-owned checks validate CP3 inputs, private-boundary API absence,
route determinism, registry, no-bypass handoff graph, A01–A18 coverage,
SVG-first rule, AI/evidence boundary, fabrication separation, Fishbone
provenance, CP3 Governor consumption, recursive schema closure, and an actual
repository plus staged-index privacy scan. Candidate state binds six CP3
artifacts, CP4 source, `contracts.py`, six CP4 schemas, routing YAML, and 17
Skill-contract hashes. Independent status
dimensions remain not-run/blocked as required.

## 5. Commands/tests run

- RED: `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py -q` initially failed with the missing CP4 module (17 failures), then with missing local Skill contract sections (1 failure).
- GREEN: `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py -q` — 18 passed, 0 failed.
- `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint1.py -q` — 64 passed, 0 failed after v3/v4 compatibility validation.
- Regenerated CP4 artifacts with `write_checkpoint4_artifacts()` using only committed CP3 JSON inputs.
- SchemaRegistry / Draft 2020-12 FormatChecker validates all CP4 artifacts.
- Full `python -m pytest packages/thesis-deck-system/tests -q` in a disposable
  detached worktree containing the exact CP4 candidate patch — 298 passed,
  0 failed (177.41 seconds).
- The CP4 execution record includes the authoritative repository/staged privacy
  scanner ID/version/configuration hash and executed zero-finding results.

## 6. Test results

- Focused CP4: 18 passed, 0 failed.
- CP1 focused compatibility: 64 passed, 0 failed.
- Full Phase 1–2 + Checkpoint 1–4 disposable regression: 298 passed, 0 failed.

## 7. Artifacts produced

- `thesis-deck-system/artifacts/phase3/figure-production-plans.json`
- `thesis-deck-system/artifacts/phase3/scientific-figure-specs.json`
- `thesis-deck-system/artifacts/phase3/archetype-figure-routing.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json`

## 8. Visual QA evidence

No visual asset is authorized or produced. Production figure rendering and
FigureCritic visual acceptance are `not_run`; no PPTX, render, montage, PDF,
or private render exists in this checkpoint.

## 9. Scientific/provenance QA evidence

The executed CP4 evidence reports private alias resolution/source open/render
attempts of **0 / 0 / 0**. Plans require canonical source/evidence bindings,
reject AI for empirical/literature/plot classes, retain Fishbone revision/focus/
history, preserve fabrication unknown conditions, and require provenance before
future FigureCritic/Layout handoff.

## 10. Known failures / technical debt

- Native-shape eligibility remains `insufficient_evidence` until later measured
  visual calibration establishes a rule; structured diagrams therefore use the
  conservative vector route.
- CP4 intentionally does not execute a FigureCritic visual review because no
  figure renderer/output is authorized.
- Private visual/output stages intentionally remain blocked or not-run; this is
  a control-plane checkpoint, not a rendering or acceptance-deck checkpoint.

## 11. Deviations from reviewer prompt

None. Existing v3 schema variants were preserved solely to avoid regressing the
accepted CP1 contract suite; all new CP4 production records validate against
closed v4 variants.

## 12. Questions requiring reviewer decision

None.

## 13. Recommended next phase

Stop at Checkpoint 4 and await reviewer approval. Do not render a figure,
calibrate A01–A18 geometry, reconstruct templates, create a deck, or start
Phase 4 without the next explicit authorization.

```yaml
codex_report:
  phase: PHASE_3_CHECKPOINT_4
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: null
  files_added:
    - packages/thesis-deck-system/src/thesis_deck_system/phase3_checkpoint4.py
    - packages/thesis-deck-system/tests/unit/test_phase3_checkpoint4.py
    - thesis-deck-system/schemas/archetype-figure-routing.schema.json
    - thesis-deck-system/schemas/checkpoint-4-execution-evidence.schema.json
    - thesis-deck-system/schemas/checkpoint-4-qa.schema.json
    - thesis-deck-system/artifacts/phase3/archetype-figure-routing.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json
    - thesis-deck-system/artifacts/phase3/figure-production-plans.json
    - thesis-deck-system/artifacts/phase3/scientific-figure-specs.json
    - thesis-deck-system/reports/PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md
    - thesis-deck-system/skills/comparison-figure-director/SKILL.md
    - thesis-deck-system/skills/concept-illustration-director/SKILL.md
    - thesis-deck-system/skills/experiment-schematic-director/SKILL.md
    - thesis-deck-system/skills/fabrication-process-director/SKILL.md
    - thesis-deck-system/skills/figure-critic/SKILL.md
    - thesis-deck-system/skills/image-matrix-director/SKILL.md
    - thesis-deck-system/skills/literature-figure-director/SKILL.md
    - thesis-deck-system/skills/mechanism-diagram-director/SKILL.md
    - thesis-deck-system/skills/photo-annotation-director/SKILL.md
    - thesis-deck-system/skills/provenance-qa/SKILL.md
    - thesis-deck-system/skills/scientific-figure-router/SKILL.md
    - thesis-deck-system/skills/scientific-plot-director/SKILL.md
    - thesis-deck-system/skills/vector-figure-builder/SKILL.md
    - thesis-deck-system/skills/visual-style-governor/SKILL.md
  files_modified:
    - packages/thesis-deck-system/src/thesis_deck_system/contracts.py
    - thesis-deck-system/schemas/figure-production-plan.schema.json
    - thesis-deck-system/schemas/scientific-figure-spec.schema.json
    - thesis-deck-system/schemas/skill-routing.schema.json
    - thesis-deck-system/skill-routing.yaml
    - thesis-deck-system/skills/fishbone-director/SKILL.md
    - thesis-deck-system/skills/layout-director/SKILL.md
    - thesis-deck-system/skills/professor-qa/SKILL.md
    - thesis-deck-system/skills/thesis-deck-router/SKILL.md
  files_deleted: []
  artifacts:
    - thesis-deck-system/artifacts/phase3/figure-production-plans.json
    - thesis-deck-system/artifacts/phase3/scientific-figure-specs.json
    - thesis-deck-system/artifacts/phase3/archetype-figure-routing.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-execution-evidence.json
    - thesis-deck-system/artifacts/phase3/checkpoint-4-qa.json
  render_previews: []
  tests_run:
    - focused CP4 RED to GREEN
    - CP1 compatibility regression
    - disposable-worktree complete regression
  tests_passed:
    - 18 focused CP4 tests
    - 64 CP1 tests
    - 298 complete regression tests
  tests_failed: []
  known_failures: []
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```
