# TASK — Phase 2 Revision 3

## Scope

Correct Phase 2 only.

Do **not** start Phase 3.

Do **not** globally/publicly register Skills.

Do **not** claim production Group Meeting readiness.

Authoritative reviewer verdict:

`thesis-deck-system/reviews/PHASE_2_REVISION_3_REVIEW.md`

Required blockers:

- P2-D1 — layer-opening temporal snapshots
- P2-D2 — combined-role presentation completeness
- P2-D3 — asset + text slot composition fidelity
- P2-D4 — presentation semantic QA + report consistency

---

# P2-D1 — Stage-aware temporal presentation snapshots

## Required architecture

A Hypothesis Layer is not a single close-state snapshot.

Represent the research layer as an append-only sequence of temporal states.

At minimum support:

1. layer opened / initial hypothesis state
2. problem + historical fishbone state
3. initial Observation/Literature/Mechanism/Solution state
4. experiment-design state
5. result state(s)
6. integrated-discussion state
7. decision/summary state
8. transition state

You may implement this through explicit events, layer revisions, stage cursors, or another deterministic append-only model, but the scientific meaning must be preserved.

## Slide cursor rules

For every generated Slide Spec assign the earliest valid/reproducible materialized cursor for the content that slide presents.

Hypothesis:
- must precede layer experiment-result evidence;
- may bind only claims/evidence available when the hypothesis was proposed.

Problem:
- must precede layer experiment-result evidence unless the problem is explicitly a later revised Problem object;
- may not inherit final block-wide result evidence.

Fishbone:
- must use the historical revision available when the layer opened.

Observation/Literature/Mechanism/Solution:
- must use evidence available before the experiment result they motivate.

Experiment Design:
- must exist before its result evidence.

Result:
- must be at/after its result/evidence materialization.

Integrated Discussion:
- must be after the complete required result set.

Summary/Decision:
- must be after Discussion and Decision.

Transition:
- must be after prior-layer results/discussion/decision + true precursor evidence;
- must be before successor experiment-result evidence.

## Binding rules

Do not use the final Research Block's entire `evidence_refs` list for every slide.

Implement role/stage-aware binding projection.

Each Slide Spec must bind only scientifically relevant and cursor-reachable:

- claims
- evidence
- assets
- actions
- decisions
- stages

## Required negative tests

Fail if:

- an H002 Hypothesis slide binds E201;
- an H002 Problem slide binds E201;
- an H002 Fishbone slide binds E201;
- an Experiment Design slide uses a cursor after its Result solely because the final layer cursor was reused;
- an early H001/H002 slide changes when later Result evidence is appended without an explicit revision event.

## Required artifact

Produce:

`artifacts/phase2/presentation-temporal-snapshot-qa.json`

It must include per generated slide:

- slide_id
- semantic_role
- source_cursor
- bound claim/evidence/asset/action/decision refs
- earliest_required_cursor
- latest_allowed_cursor if applicable
- future_ref_findings
- status

---

# P2-D2 — Combined-role content completeness

## Problem

`combined_roles` must never be metadata-only.

## Required contract

Create a machine-readable presentation contract for each semantic role.

Example concept:

```yaml
semantic_role: experiment_design
required_presentation_fields:
  - independent_variables
  - controlled_variables
  - sample_plan
  - measured_outputs
  - method
  - prediction
  - decision_rules
```

For every role listed in `combined_roles`, prove that its required presentation content is physically represented.

## H002 correction

The current acceptance compaction must be corrected.

Acceptable option A — preferred for clarity:

- H002 Hypothesis
- H002 Problem
- H002 Fishbone
- H002 Observation
- H002 Literature + Mechanism + Strategy
- H002 Experiment Design
- H002 Result
- H002 Integrated Discussion
- H002 Summary / Decision

Acceptable option B:

Use explicit merged archetypes with unioned required slots/content.

If Observation + Literature + Mechanism + Strategy are combined, the merged slide must visibly contain all four stages.

If Experiment + Result are combined, the slide must visibly retain complete Experiment metadata **and** the Result.

If Integrated Discussion + Summary are combined, the slide must visibly retain:

- supporting/contradicting/non-discriminating results
- cross-experiment pattern
- mechanism assessment
- alternatives
- remaining uncertainty
- hypothesis status
- decision
- next step

## Professor QA

Do not define `has(role)` solely from `combined_roles`.

A combined role counts as present only if its presentation-content contract passes.

## Required negative tests

Fail if:

- `combined_roles` names Literature but no literature synthesis content is physically present;
- `combined_roles` names Experiment but IV/N/method/decision rule are absent;
- `combined_roles` names Integrated Discussion but discussion synthesis fields are absent;
- a state object exists but presentation content for that role is missing.

## Required artifact

Produce:

`artifacts/phase2/combined-role-content-qa.json`

with per-slide, per-role field coverage.

---

# P2-D3 — Asset + text composition fidelity

## Required slot model

A governed slot must explicitly declare how it is composed.

Support at least:

- text_only
- asset_only
- asset_with_caption
- asset_with_annotation
- nested_group

Do not infer `asset OR text` from the existence of an asset placement.

## Physical assembly rules

When the Slide Spec requires both an asset and scientific text:

- create both physical shapes;
- assign stable identities;
- preserve governed geometry;
- preserve editable text;
- preserve asset relationship/provenance.

You may implement nested identities such as:

- `tds-slot:proposed_panel/figure`
- `tds-slot:proposed_panel/annotation`

or explicit separate slots.

## Structural QA

For each slot validate:

- slot identity
- composition type
- expected text
- actual extracted PPTX text
- expected asset ID
- actual media/OpenXML relationship
- geometry
- status

Do not mark content binding true merely because an asset exists when expected text is non-empty.

## Critical regression proof

The current H001 result pages contain distinct result statements:

- RES101 — conductivity +24% ± 5% SD
- RES102 — CV only -4% ± 6% SD / No-Go

They must produce distinguishable physical PPTX text and distinguishable final renders.

Same plot reuse is allowed only if the visible scientific annotation distinguishes the results.

Add a negative test where:

same SVG + different expected result text + text dropped by assembler

MUST fail structural/presentation-semantic QA.

## Required artifact

Produce:

`artifacts/phase2/physical-content-fidelity-qa.json`

including extracted slide/slot text and asset bindings.

---

# P2-D4 — Presentation semantic fidelity QA and report consistency

## New QA gate

Add an owning QA gate named conceptually:

`presentation_semantic_fidelity`

Run it after Slide Specs/Layout Plans/PPTX assembly and before Professor QA can certify the deck.

The gate must validate:

1. temporal presentation snapshot correctness;
2. combined-role required content coverage;
3. structured Slide Spec slot → actual PPTX text/asset fidelity;
4. no scientific text displaced by asset-only placement;
5. Hypothesis/Problem separation;
6. all layer Scientific Method stages required by Professor Profile are audience-visible;
7. Result pages visibly distinguish different Result objects;
8. Integrated Discussion is visibly present after complete Results;
9. Summary/Decision visibly follows Discussion;
10. historical fishbone revision/focus is correct.

Professor QA should consume this gate's evidence rather than treating object-state completeness as presentation completeness.

## Report consistency

Correct stale cursor reporting.

The current report says transition cursor 38 while committed QA/Slide Spec evidence uses 41.

Generate report facts from canonical artifact values or add an automated report-evidence assertion.

At minimum verify/report consistently:

- H01 opening cursor
- H01 Experiment cursors
- H01 Result cursors
- H01 Discussion cursor
- H01 Summary/Decision cursor
- precursor evidence cursor
- transition cursor
- H02 opening cursor
- H02 Experiment cursor
- H02 Result Evidence cursor
- H02 Discussion cursor
- H02 Summary/Decision cursor
- generated Slide Spec count
- physical PPTX page count
- governed required/instantiated/missing slot counts

## Required artifact

Produce:

`artifacts/phase2/report-evidence-consistency.json`

---

# Preserve previous accepted corrections

Do not regress:

- E104 is a true transition precursor and not H02 result data.
- E201 causal_role=experiment_result and is downstream of ST-EXP201.
- evidence causal-role validator and negative test.
- Hypothesis and Problem separate.
- historical/versioned Fishbone with parent hierarchy.
- H01 FB001 rev1 and H02 FB001 rev2.
- actual split governance with no fabricated approval.
- H001 two Experiment Design continuation pages.
- state-derived story/layout after Ledger.load().
- H003 generic traversal.
- stable named physical slots.
- exact SVG ownership relationship.
- render-pixel QA and hash-bound qualitative review.
- private fixture honesty.
- native PowerPoint blocked status.
- no Phase 3.
- no global/public Skill registration.

---

# Required tests

Run the complete Phase 1 + Phase 2 test suite.

Add tests for P2-D1–P2-D4.

At minimum include:

1. stage-aware slide cursor test;
2. future-result citation rejection test;
3. late-result append does not mutate early slide reconstruction;
4. combined-role content completeness positive/negative tests;
5. experiment+result merge retains Experiment metadata;
6. discussion+summary merge retains Integrated Discussion synthesis;
7. asset_with_annotation physical shape test;
8. asset does not replace expected text negative test;
9. two different Result texts produce different physical extracted text;
10. two different Result texts produce different render hashes;
11. Professor QA fails metadata-only combined roles;
12. report cursor consistency test;
13. all existing P2-C1–P2-C6 tests remain green.

---

# Required rebuild / evidence

Regenerate Phase 2 artifacts from a clean output directory.

Run:

- canonical schema validation
- Ledger serialize/load/hash/replay/materialization
- temporal/cursor validation
- evidence causal-role validation
- presentation temporal snapshot QA
- fixture-mutation story/layout reproducibility
- combined-role content QA
- physical content fidelity QA
- Layout Plan validation
- PPTX structural audit
- SVG ownership audit
- Professor QA
- render-pixel QA
- image-capable qualitative review
- presentation semantic fidelity gate
- report-evidence consistency
- LibreOffice render
- montages
- absolute path scan
- `git diff --check`
- remote Git verification

Native PowerPoint remains blocked if unavailable.

---

# Implementation report

Update:

`thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`

Add explicit traceability:

- P2-D1
- P2-D2
- P2-D3
- P2-D4

For each include:

- implementation files
- exact test names/results
- exact artifacts
- cursor facts
- limitations
- status

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

P2-D1–P2-D4 traceability:

stage-aware cursor summary:
- H01 hypothesis/problem/fishbone cursor:
- H01 experiment cursors:
- H01 result cursors:
- H01 discussion cursor:
- H01 summary/decision cursor:
- transition cursor:
- H02 hypothesis/problem/fishbone cursor:
- H02 experiment cursor:
- H02 result evidence cursor:
- H02 discussion cursor:
- H02 summary/decision cursor:

future-result binding test:
late-result immutability test:

combined-role content QA:
- combined roles tested:
- required fields:
- physically represented:
- missing:

physical content fidelity:
- expected text bindings:
- actual text bindings:
- expected asset bindings:
- actual asset bindings:
- missing:

H001 result render hashes:
- RES101 slide:
- RES102 slide:
- distinguishable: yes/no

presentation semantic fidelity QA:
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

Only write `READY_FOR_REVIEW: yes` after the correction commit is pushed and all required remote artifacts are verified.

Then STOP.

Do not begin Phase 3.
