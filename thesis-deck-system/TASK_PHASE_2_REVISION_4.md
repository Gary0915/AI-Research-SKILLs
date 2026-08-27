# TASK — Phase 2 Revision 4

## Scope

Correct Phase 2 only.

Do **not** start Phase 3.

Do **not** globally/publicly register Skills.

Do **not** claim production Group Meeting readiness.

Authoritative reviewer verdict:

`thesis-deck-system/reviews/PHASE_2_REVISION_4_REVIEW.md`

Required blockers:

- P2-E1 — generic N-layer story/projection
- P2-E2 — causal layer lifecycle + generic temporal dependency QA
- P2-E3 — field-level presentation contracts
- P2-E4 — honest semantic/report QA

Preserve every previously accepted Phase 1 and Phase 2 correction.

---

# P2-E1 — Generic N-layer story / Master projection

## Problem

The current production story driver still treats the deck as:

`first layer + first transition + current layer`

and contains literal H001/H002/B101/B201/ST-RESxxx logic.

That is incompatible with the professor's required persistent history:

`H01 full layer → H02 full layer → H03 full layer → H04 ...`

## Required architecture

Implement a reusable layer projection engine that:

1. discovers every Hypothesis Layer from persisted/replayed Ledger state;
2. orders layers by actual creation/history cursor;
3. compiles every layer in order;
4. resolves each layer's own:
   - block refs;
   - experiment stage refs;
   - result stage refs;
   - discussion ref;
   - decision/summary refs;
   - fishbone snapshot;
   - transition(s);
5. emits the transition between the correct predecessor/successor layers;
6. never skips a middle historical layer;
7. does not depend on literal H001/H002/B101/B201/RES101/RES201 IDs in reusable production code.

Fixture/test builders may contain concrete IDs. Reusable projection/cursor logic may not.

## Master projection requirement

A three-layer history must produce conceptually:

H001
- Hypothesis
- Problem
- historical Fishbone
- scientific content
- Experiments
- Results
- Integrated Discussion
- Summary / Decision
- Transition

H002
- full retained layer
- Transition

H003
- full current layer

Do not compact by dropping H002 because H003 is current.

## Meeting projection

Meeting projection may focus the current layer, but Master history must still retain every layer.

## Required acceptance proof

Add a real H001→H002→H003 projection/build fixture or deterministic extension that runs through:

Ledger.load
→ Master story projection
→ Slide Specs
→ Layout Plans
→ PPTX/structural QA where practical.

At minimum prove:

- all three layers appear;
- H002 appears between H001 and H003;
- each layer retains separate Hypothesis and Problem;
- each layer retains its historical Fishbone ref;
- transitions bind the correct predecessor/successor pair;
- no production story function depends on literal H001/H002 IDs.

Required artifact:

`artifacts/phase2/n-layer-projection-qa.json`

Include:

- ordered_layer_ids
- emitted_layer_ids
- emitted_transition_ids
- per-layer slide counts/roles
- skipped_layers
- literal_id_dependency_scan
- status

---

# P2-E2 — Causal successor-layer lifecycle and generic temporal QA

## Part A — Layer lifecycle

The research Ledger must express the causal story, not merely hide future data from Slide Specs.

For a successor layer H(n+1), enforce the intended causal sequence:

prior-layer Results
→ prior-layer Integrated Discussion
→ prior-layer Decision/Summary
→ true precursor Observation/uncertainty
→ Hypothesis Transition
→ successor Hypothesis Layer opened
→ successor Problem/Fishbone/Scientific Method state
→ successor Experiment Design
→ successor Result Evidence
→ successor Result
→ successor Integrated Discussion
→ successor Decision/Summary

The new hypothesis Claim required by the Transition may exist immediately before the Transition.

Do not append successor Experiment, pending Result, pending Discussion, Decision or Action before the Transition/Layer opening unless they are explicitly modeled as a separate planning artifact whose semantics cannot be mistaken for executed successor-layer research.

For the synthetic fixture, reorder H002 history accordingly.

## Part B — Generic result-evidence discovery

Remove synthetic hard-coding such as:

`result_evidence = {E101, E201}`

Derive experiment-result evidence from canonical data, using:

- result-stage `evidence_refs`;
- Evidence `causal_role`;
- Evidence `origin.experiment_stage_ref`;
- block/layer ownership;
- event cursors.

## Part C — True cursor dependency bounds

For each Slide Spec calculate:

`earliest_required_cursor`

as the maximum cursor at which every required presented dependency is available.

Dependencies may include:

- Hypothesis Layer revision
- Claim
- Problem
- Fishbone revision
- Stage revision(s)
- Evidence
- Asset
- Decision
- Action
- Discussion
- Summary
- Transition

For opening Hypothesis/Problem/Fishbone slides:

if the layer has a first experiment-result evidence cursor R,

require:

`source_cursor < R`

not `<= R`.

`latest_allowed_cursor` should therefore be `R - 1` in an integer cursor model, or represented as an explicit strict bound.

For Result slides:

`earliest_required_cursor` must be at/after the actual result stage/evidence/asset dependencies.

For Integrated Discussion:

`earliest_required_cursor` must be after the complete required Result set and Discussion object/stage.

For Summary/Decision:

it must be after Discussion and Decision/Summary dependencies.

For Transition:

it must be after prior-layer Result/Discussion/Decision + precursor evidence and before successor experiment-result evidence.

## Required genericity tests

Add tests with IDs that are not E101/E201/H001/H002, for example H003 / E777 / EXP777 / RES777.

The temporal validator must still:

- classify result evidence correctly;
- reject opening slides at/after result evidence;
- reject future bindings;
- calculate correct earliest dependency cursor;
- calculate correct transition bounds.

## Required artifact

Regenerate:

`artifacts/phase2/presentation-temporal-snapshot-qa.json`

Per slide include:

- slide_id
- layer_id
- semantic_role
- source_cursor
- stage_source_cursors
- dependency_refs with dependency cursor/type
- earliest_required_cursor
- latest_allowed_cursor or strict boundary representation
- bound refs
- future/causal findings
- status

Also produce:

`artifacts/phase2/layer-lifecycle-qa.json`

with per-layer lifecycle events/cursors and ordering findings.

---

# P2-E3 — Field-level audience-visible presentation contracts

## Principle

A physical textbox being non-empty does not prove the professor-required scientific information is visible.

Move from slot-level completeness to field-level semantic completeness.

## Required field contracts

### Hypothesis

At least:

- hypothesis statement
- falsifiable prediction / falsifier
- research question

### Problem

- previous finding
- unresolved conflict/problem
- research question
- scope where required

### Literature

- consensus
- disagreement/alternative explanation
- research gap
- implication for the current hypothesis/strategy

### Mechanism / Strategy

- mechanism
- evidence/claim link represented in provenance
- strategy
- success criterion

### Experiment Design

Individually verify audience-visible:

- independent variables
- controlled variables
- control/baseline
- sample plan
- N / replicates
- measured outputs
- units
- instrumentation/method
- predicted outcomes
- decision rule

### Result

- result identity
- result statement
- metric/value/uncertainty where applicable
- bound figure/asset if required

### Integrated Discussion

Individually verify:

- supporting results
- contradicting results and/or explicit none
- non-discriminating results and/or explicit none where applicable
- cross-experiment pattern
- mechanism assessment
- alternative explanations
- remaining uncertainty

### Summary / Decision

- answered question
- hypothesis status
- decision
- unresolved item(s)
- next question
- next step

### Transition

- prior hypothesis
- key prior result(s)
- unresolved point
- precursor observation/uncertainty
- derivation/rationale
- new hypothesis

## Representation

You may preserve aggregate physical slots for layout efficiency, but the Slide Spec must carry machine-addressable semantic field bindings so QA can prove each field appears in extracted PPTX text or a governed asset/annotation.

Example concept:

```json
{
  "slot": "experiment_matrix",
  "semantic_fields": {
    "independent_variables": "...",
    "controlled_variables": "...",
    "sample_plan": "...",
    "replicates": "...",
    "method": "..."
  }
}
```

The exact schema may differ.

## Required negative tests

Keep a parent slot physically present and non-empty, but remove only one subfield.

Required failures include at least:

- Experiment page missing N/replicates;
- Experiment page missing method;
- Literature page missing research gap;
- Integrated Discussion missing mechanism assessment;
- Integrated Discussion missing alternatives;
- Summary missing hypothesis status;
- Summary missing next question.

`combined-role-content-qa.json` must report field-level coverage.

---

# P2-E4 — Honest presentation semantic gate and report truth

## Part A — Executed semantic checks must be real

`run_presentation_semantic_fidelity_qa()` may list a check in `executed_checks` only if it actually executes an owning assertion and persists evidence.

Implement explicit checks for at least:

1. temporal snapshot correctness;
2. combined-role field completeness;
3. physical text/asset fidelity;
4. Hypothesis/Problem separation;
5. all professor-required Scientific Method stages audience-visible;
6. Result before Integrated Discussion;
7. all required Results before Integrated Discussion;
8. Integrated Discussion before Summary/Decision;
9. historical Fishbone revision/focus binding;
10. visible Result distinction;
11. transition location/provenance between layers.

Persist per-check evidence.

## Part B — Result distinction must be generic and render-grounded

Do not compare only the first two Result records.

For every pair/set of Result objects that are expected to convey different scientific statements:

- compare expected semantic result identity/text;
- compare extracted PPTX text;
- ensure the appropriate slide contains the correct result text;
- use final render hashes / image review evidence when claiming visible distinction.

If render evidence is not available yet, presentation-semantic status must be provisional/blocked for render-dependent checks.

Final PASS occurs only after the render step.

Add a test with 3+ Result objects where Result 2 and Result 3 are accidentally identical in the final presentation; the semantic gate must fail even if Result 1 differs.

## Part C — Report-evidence consistency

Current committed evidence shows:

- E104 precursor cursor = **52**

The previous implementation report incorrectly states cursor 32.

Fix the report.

Create one canonical report-facts object generated from committed artifacts.

Required fields include at least:

- h01_opening_cursor
- h01_experiment_cursors
- h01_result_cursors
- h01_discussion_cursor
- h01_summary_cursor
- precursor_evidence_id
- precursor_evidence_cursor
- transition_cursor
- h02_opening_cursor
- h02_experiment_cursor
- h02_result_evidence_cursor
- h02_result_slide_cursor(s)
- h02_discussion_cursor
- h02_summary_cursor
- generated_slide_spec_count
- physical_pptx_page_count
- required_governed_slot_count
- instantiated_governed_slot_count
- intentionally_empty_slot_count
- missing_governed_slot_count
- qa_report_id
- native PowerPoint status
- private fixture status

`report-evidence-consistency.json` must be generated from these facts and verify the report's corresponding machine-readable footer/facts section.

Its status may not be based only on overall QA status + transition cursor equality.

Add negative tests for:

- stale precursor cursor;
- omitted H01 experiment cursor;
- wrong physical page count;
- wrong missing-slot count.

Any mismatch must fail consistency QA.

---

# Preserve accepted corrections

Do not regress:

- Phase 1 temporal/provenance contracts.
- H002 Hypothesis/Problem/Fishbone do not bind E201.
- E104 is a true precursor, not H02 Result data.
- E201 is downstream of its Experiment.
- Hypothesis and Problem are separate.
- historical/versioned/hierarchical Fishbone.
- H001 Result slides preserve distinct annotations and renders.
- asset + annotation composition.
- exact SVG owning-slide OpenXML relationships.
- governed physical slot identities.
- no synthetic reviewer split override.
- state-derived story/layout after Ledger.load().
- H003-generic Professor QA.
- render-pixel QA and image-capable hash-bound qualitative review.
- repo-local Skills remain unregistered globally.
- private fixture status remains honest.
- native PowerPoint remains blocked if unavailable.

---

# Required tests

Run the complete Phase 1 + Phase 2 test suite.

Add Revision-4 tests including at least:

1. production N-layer projection H001→H002→H003 includes all three layers;
2. middle-layer omission negative test;
3. no literal H001/H002 dependency in reusable N-layer story/cursor driver;
4. transition precedes successor-layer experiment/result/discussion work;
5. generic result-evidence discovery with renamed IDs;
6. true earliest Result cursor calculation;
7. strict opening latest-bound test;
8. transition earliest/latest dependency test;
9. experiment field-level missing-replicates negative;
10. experiment field-level missing-method negative;
11. literature missing-gap negative;
12. discussion missing-mechanism-assessment negative;
13. discussion missing-alternatives negative;
14. summary missing-status negative;
15. summary missing-next-question negative;
16. semantic gate story-order negative;
17. semantic gate historical-fishbone negative;
18. 3-result visible-distinction negative;
19. report stale-E104-cursor negative;
20. report wrong-page/slot-count negative;
21. all existing Phase 2 D1–D4 tests remain green.

---

# Required artifacts

Regenerate all Phase 2 artifacts from a clean output root.

Add/update at least:

- `artifacts/phase2/n-layer-projection-qa.json`
- `artifacts/phase2/layer-lifecycle-qa.json`
- `artifacts/phase2/presentation-temporal-snapshot-qa.json`
- `artifacts/phase2/combined-role-content-qa.json`
- `artifacts/phase2/physical-content-fidelity-qa.json`
- `artifacts/phase2/presentation-semantic-fidelity-qa.json`
- `artifacts/phase2/report-evidence-consistency.json`
- `artifacts/phase2/qa-report.json`
- Slide Specs / Layout Plans / Manifest
- acceptance PPTX
- renders and montages
- H003/N-layer evidence as required

Run:

- schema validation
- Ledger serialize/load/hash/replay/materialization
- lifecycle causal validation
- generic temporal dependency validation
- evidence causal-role validation
- N-layer projection QA
- field-level combined-role QA
- physical-content fidelity QA
- presentation-semantic fidelity QA
- Professor QA
- structural PPTX/SVG/slot audit
- render-pixel QA
- image-capable qualitative review
- report-evidence consistency
- LibreOffice rendering
- montages
- absolute-path scan
- `git diff --check`
- remote Git verification

Native PowerPoint remains `blocked_environment` if unavailable.

---

# Implementation report

Update:

`thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`

Add explicit traceability:

- P2-E1
- P2-E2
- P2-E3
- P2-E4

Do not hand-type factual cursor/count values independently from canonical report facts.

Include exact tests, artifact paths, known limitations and status.

---

# Final Codex delivery format

Return:

```text
repository:
branch:
commit SHA:
pushed:
remote verification:

report path:

files added:
files modified:
files deleted:

tests/checks run:
tests passed:
tests failed:

P2-E1–P2-E4 traceability:

N-layer projection:
- ordered layers:
- emitted layers:
- emitted transitions:
- skipped layers:
- literal reusable H001/H002 dependencies:

layer lifecycle:
- H01 summary cursor:
- precursor evidence cursor:
- transition cursor:
- H02 layer-open cursor:
- first H02 scientific-stage cursor:
- H02 experiment cursor:
- H02 result-evidence cursor:
- lifecycle status:

temporal QA:
- result evidence discovery method:
- opening bound strictness:
- earliest cursor validation:
- renamed-ID generic test:

field-level presentation QA:
- fields required:
- fields physically represented:
- missing:
- negative subfield tests:

presentation semantic fidelity:
- actual executed checks:
- result objects checked:
- render-grounded distinction status:

report facts:
- H01 opening:
- H01 experiment cursors:
- H01 result cursors:
- H01 discussion:
- H01 summary:
- precursor evidence ID/cursor:
- transition:
- H02 opening:
- H02 experiment:
- H02 result evidence:
- H02 result slide:
- H02 discussion:
- H02 summary:
- Slide Specs count:
- physical PPTX pages:
- slots required/instantiated/intentionally-empty/missing:

report-evidence consistency:
Professor QA:
render-pixel QA:
qualitative visual review:

acceptance PPTX:
render paths:
montage paths:

private fixture status:
native PowerPoint status:

known failures:
technical debt:
unresolved questions:

READY_FOR_REVIEW: yes
```

Only write `READY_FOR_REVIEW: yes` after the implementation and required artifacts are pushed and remotely verified.

Then STOP.

Do not begin Phase 3.
