# TASK — Phase 2 Revision 2

## Authority

This task supersedes any Phase 2 implementation interpretation that conflicts with:

- `thesis-deck-system/reviews/PHASE_2_REVISION_2_REVIEW.md`
- this file

Preserve all previously accepted Phase 1 guarantees and accepted Phase 2 behavior.

Do not start Phase 3.

## Objective

Close the remaining gap between a semantically correct synthetic deck pipeline and a genuinely trustworthy professor-specific deck system.

The system must prove not only that semantic Layout Plans, QA labels, and temporal objects exist, but that:

- scientific evidence cannot leak backward across hypothesis layers;
- every governed layout slot is physically realized in the PPTX;
- split/fit exceptions cannot self-certify;
- visual claims are grounded in rendered pixels or honestly blocked;
- Professor QA works for arbitrary H01 → H02 → H03 → ... history;
- downstream layout decisions have only one source of truth: persisted materialized ledger state.

## P2-C1 — Evidence-role causal integrity

### Required implementation

Separate precursor observation evidence from downstream discriminating experiment evidence.

For the synthetic acceptance fixture:

- create a real precursor observation/uncertainty evidence object for the H01→H02 transition;
- it must originate from information available before H02 Experiment Design/Result;
- do not use the later contact-pressure result CSV as transition precursor evidence;
- keep the H02 pressure experiment/result evidence separate and downstream of the H02 experiment boundary.

Add explicit evidence lifecycle semantics if needed, e.g.:

- observation
- literature
- experiment_input
- experiment_result
- derived_result

Causal validation must reject a transition that references a downstream experiment-result evidence object even if that Evidence Card was artificially appended earlier.

### Tests

Positive:
- transition precursor evidence exists before transition;
- H02 result evidence is downstream of H02 experiment declaration/execution;
- H02 transition rationale uses only precursor evidence + H01 results/decision.

Negative:
- same Evidence ID cannot be both transition precursor and H02 discriminating result when its source provenance belongs to the later experiment;
- appending a result Evidence Card early must not defeat causal QA.

### Required artifact

`artifacts/phase2/evidence-causal-role-qa.json`

It must list precursor and downstream-result Evidence IDs, origins, source cursors, experiment binding, and pass/fail rationale.

## P2-C2 — Physical slot realization

### Required implementation

Upgrade Slide Spec content from one generic `content.body` blob into structured slot-bound content for multi-region archetypes.

At minimum physically realize all governed slots for:

- A02 Problem
  - previous_finding
  - unresolved_conflict
  - research_question
- A03 Fishbone
  - primary_figure
  - fishbone_focus
- A04 Observation
  - primary_figure
  - research_question
  - observation_text
- A05 Literature/Mechanism
  - literature_evidence
  - mechanism_diagram or structured mechanism region
- A09 Experiment
  - experiment_matrix
  - decision_rule
- A11 Result Comparison
  - control_panel
  - proposed_panel
- A14 Integrated Discussion
  - supporting_results
  - contradicting_results
  - uncertainty
- A15 Layer Summary/Decision
  - decision_status
  - uncertainty
  - next_step
- A16 Transition
  - transition_nodes
  - derivation_strip
- A17 Progress/To-do
  - commitment_table
  - current_position
  - parallel_work

The assembler must consume the persisted Layout Plan and create one or more PPTX shapes mapped to those slots.

Each generated scientific shape must carry a stable slot identity suitable for structural audit. Use an OpenXML-compatible mechanism such as shape name/descr/custom metadata that survives save/reload.

### Structural QA

Structural audit must compare every `required_slot` in the Layout Plan with actual PPTX shapes.

A slide passes only if:

- every required slot is physically instantiated; or
- the plan explicitly permits `intentionally_empty` for that slot and the reason is contract-valid.

Do not reduce expected slots to `body_slot + asset slots`.

Persist:

- slot name
- planned geometry
- actual shape identity
- actual geometry
- geometry tolerance result
- content/asset binding result

### Tests

Add a negative test:

A three-slot Problem plan with only one generated textbox MUST fail structural QA.

Add positive tests for A02, A14, A15, A16, A17.

## P2-C3 — Split / fit exception integrity

### Forbidden behavior

The build may not automatically create a record claiming reviewer approval.

Remove automatic:

`approved_by: Phase 2 synthetic acceptance review`

or equivalent self-certification.

### Allowed resolution paths

For every over-budget slide choose exactly one:

1. `split`
   - compiler emits continuation slide(s);

2. `automated_fit_exception`
   - produced only after measurable fit checks;
   - evidence includes actual PPTX/render measurements;
   - no human/reviewer identity is claimed;

3. `external_review_override`
   - only when an actual user/reviewer approval artifact is supplied.

### Ordering requirement

An exception may not cite visual/render evidence before that evidence exists.

If fit validation is post-render, assembly/QA flow must reflect that state honestly.

### Tests

Negative:
- self-approved override fails;
- override referencing future/nonexistent evidence fails;
- unresolved split fails Stage 7.

Positive:
- actual split passes;
- measurable automated fit exception passes only when its measurement evidence passes.

## P2-C4 — Render-grounded visual QA

### Required separation

Persist three distinct classes of evidence:

1. `spec_geometry_qa`
2. `render_pixel_qa`
3. `qualitative_visual_review`

Do not label all three as if they were the same check.

### Render pixel QA

Every generated slide inspection must bind:

- slide_id
- exact render path
- render SHA-256
- dimensions
- nonblank/variance
- occupied-region or equivalent pixel-derived metrics
- canvas-edge proximity / clipping proxy
- figure/text region balance proxy where applicable

Where practical add image-derived checks for:

- fishbone focus contrast/prominence
- comparison left/right balance
- text/figure occupied-area balance
- excessive empty area

### Qualitative visual review

Claims such as:

- 'focus is obvious in 3–5 seconds'
- 'comparison is visually fair'
- 'hierarchy reads correctly'
- 'the slide looks professor-ready'

must come from an image-capable review step that actually inspects the rendered slide.

If no image-capable visual reviewer is available, mark:

`blocked_visual_review`

for those qualitative checks.

Do not infer these claims from semantic role or Slide Spec metadata.

### Mutation test

Add a render mutation test:

- keep the same Slide Spec;
- alter/blank/crop/misbalance the render;
- visual evidence must change or fail.

## P2-C5 — Generic hypothesis-layer Professor QA

Remove production hard-coding of:

- `H001`
- `H002`
- `TR-H001-H002`
- literal allowed history set `{H001, H002}`

Professor QA must derive:

- ordered layers
- predecessor/successor relation
- transition IDs
- current/historical layer set
- fishbone revision bindings

from the materialized state/projection.

### H003 acceptance fixture/test

Add a synthetic H003 extension used for QA testing. It need not expand the main 18-slide acceptance deck unless useful, but must prove generic logic.

Test at least:

H001 → H002 → H003

including:

- H002→H003 transition provenance;
- H003 Problem separate from Hypothesis;
- historical reachability of H001/H002/H003;
- fishbone revision progression;
- Summary/Decision/Next Step checks;
- no hard-coded layer IDs in reusable validators.

Fixture-specific IDs may remain inside acceptance seed builders/tests only.

## P2-C6 — One source of truth after ledger persistence

Define an explicit boundary:

> After `ledger.serialize()` and `Ledger.load()` succeed, no downstream story, layout, manifest, PPTX, or QA decision may read scientific/hypothesis facts from the seed fixture.

Replace post-ledger reads such as:

`fixture["hypothesis_layers"]`

used to calculate Layout Director inputs.

Use the cursor-materialized layer/state instead.

### Extended mutation regression

After persisting the ledger:

1. mutate the source fixture heavily;
2. reload only the ledger;
3. rebuild:
   - story specs
   - Slide Specs
   - Layout Director requests
   - Layout Plans
   - layout decision records
   - manifest scientific bindings
4. compare against the canonical persisted build.

Scientific and layout outputs must remain identical except for explicitly non-deterministic build metadata.

Do not exclude `placement_plan` or `layout_plan_ref` from this test.

## Acceptance artifacts

Regenerate and persist at least:

- `ledger-events.json`
- `materialized-h01.json`
- `materialized-transition.json`
- `materialized-h02.json`
- state-derived `slide-specs.json`
- `layout-plans.json`
- `layout-director-decisions.json`
- split/fit exception records
- `evidence-causal-role-qa.json`
- `phase2-binding-validation.json`
- `structural-audit.json`
- `professor-qa.json`
- render-pixel QA artifact
- qualitative visual review artifact/status
- `visual-inspection.json`
- `qa-report.json`
- acceptance PPTX and compatibility deck
- full/H02/fishbone/transition montages
- H003 generic Professor-QA fixture/artifact

## Required tests

Run the full Phase 1 + Phase 2 suite.

Add tests covering all P2-C1–P2-C6 requirements.

The next report must state:

- total tests passed/failed;
- causal precursor Evidence ID and downstream H02 result Evidence ID;
- physical required-slot conformance count / failure count;
- number of slides actually split;
- number of automated fit exceptions;
- number of external review overrides;
- any qualitative visual checks blocked;
- H003 generic QA status;
- fixture-mutation state/layout reproducibility status;
- private fixture status;
- native PowerPoint status.

## Report traceability

Update:

`thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`

Add explicit P2-C1–P2-C6 traceability with:

- implementation files;
- tests;
- artifacts;
- exact acceptance status;
- known limitations.

## Final delivery

Commit and push all corrections to:

`origin/codex/thesis-deck-system`

Verify the remote branch and key artifacts.

Final response must include:

- repository
- branch
- commit SHA
- pushed
- remote verification
- report path
- files added/modified/deleted
- tests/checks run
- tests passed/failed
- P2-C1–P2-C6 traceability
- precursor vs downstream evidence IDs/cursors
- required physical slot conformance summary
- split / automated fit exception / external override counts
- render-pixel QA status
- qualitative visual review status
- H003 generic QA status
- persisted-ledger fixture-mutation layout reproducibility status
- private fixture status
- native PowerPoint status
- known failures
- technical debt
- unresolved questions

Only write:

`READY_FOR_REVIEW: yes`

when all required corrections are pushed and remotely verified.

Then STOP.

Do not begin Phase 3.
Do not publicly/global register Skills.
Do not claim production Group Meeting readiness.
