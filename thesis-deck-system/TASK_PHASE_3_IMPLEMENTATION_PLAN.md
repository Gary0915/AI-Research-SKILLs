# TASK — Phase 3 TDD Implementation Plan

## Authorization

Phase 3 visual-fidelity design is approved.

Authoritative design:

`thesis-deck-system/designs/PHASE_3_VISUAL_FIDELITY_DESIGN.md`

Authoritative reviewer verdict:

`thesis-deck-system/reviews/PHASE_3_DESIGN_FINAL_REVIEW.md`

Current authorization is **PLAN ONLY**.

Do not implement Phase 3 production code yet.

Do not generate sanitized profiles or acceptance decks yet.

Do not start Phase 4.

Do not globally/publicly register Skills.

---

## Required output

Create exactly:

`thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`

Minimal index/documentation changes are permitted only if strictly necessary.

The plan must be executable by Codex without reinterpretation.

---

# Required plan structure

## 1. Scope and invariants

Restate the approved scientific/provenance boundaries that implementation may not alter:

- append-only Ledger and temporal truth;
- N-layer Hypothesis history;
- Hypothesis/Problem separation;
- versioned Fishbone;
- stage-aware cursors;
- field-level presentation contracts;
- single `PythonPptxAssembler` backend;
- no synthetic/private fallback pretending to be professor fidelity.

## 2. Phase 3 implementation dependency graph

Provide a dependency DAG for the seven approved implementation phases:

1. contracts and privacy boundary;
2. private profiler;
3. sanitized profiles and resolvers;
4. A01–A18/Fishbone/template reconstruction;
5. reconstruction benchmarks;
6. ledger-derived acceptance deck;
7. complete QA/reporting/remote verification.

Identify which phases may be parallelized and which are hard prerequisites.

## 3. File/module plan

List concrete proposed source modules, schemas, tests, profiles and artifact paths.

For each file specify:

- new / modified;
- responsibility;
- private-domain or sanitized-domain status;
- owning tests;
- downstream consumers.

Do not create the files in this planning step.

## 4. TDD red-green-refactor matrix

For every implementation phase provide:

- RED tests written first;
- expected failing behavior;
- GREEN minimum implementation;
- REFACTOR constraints;
- regression suite to rerun;
- evidence artifact produced before the next phase can begin.

No production module should be implemented before its owning red test exists.

## 5. Contracts and schemas

Specify planned Draft 2020-12 schemas and their key nested fields for at least:

- sanitized-exemplar-manifest;
- shell-profile;
- body-composition-profile;
- professor-visual-grammar-v3;
- fishbone-style-profile;
- archetype-calibration;
- reconstruction-benchmark;
- reconstruction-manifest;
- image-capable-visual-review;
- phase3-report-facts / QA evidence as required.

Every free-form or categorical string crossing the privacy boundary must have an explicit bounded rule.

## 6. Privacy boundary implementation plan

Define exact implementation and tests for:

- ignored `.private/` storage guard;
- alias resolver validation;
- data minimization;
- raw local profile lifetime/cleanup;
- whitelist object construction;
- schema validation;
- lexical private-content scan;
- binary/package signature scan;
- staged/tracked repository privacy scan;
- no private PPTX/screenshot/media/package-part staging;
- local-only diagnostics.

Explicitly address P3P-1 and P3P-2.

## 7. Private profiler plan

Specify how private PPTX files will be inspected for geometry/style without committing content.

Separate:

- OOXML structural profiling;
- rendering for local visual classification;
- theme/font/color extraction;
- master/layout/placeholder geometry;
- body-composition measurement;
- local-only role classification;
- data-minimized canary generation.

State what raw values are never persisted unless absolutely necessary.

## 8. Exemplar authority/resolver plan

Define implementation algorithms for:

- Exemplar 1/3 shell token resolution;
- Exemplar 2 body token resolution;
- source-authority enforcement;
- conflict records;
- hard-conflict failures;
- body/shell contamination prevention.

Include explicit tests proving Exemplar 2 cannot influence unauthorized shell token families.

Explicitly address P3P-3 and P3P-4.

## 9. A01–A18 calibration plan

For each A01–A18 identify:

- required real exemplar descriptor class(es);
- calibrated token families;
- immutable Phase 2 semantic contract;
- minimum evidence count/classification;
- fallback/insufficient-evidence behavior;
- tests proving scientific contracts do not change.

Plan a calibration-coverage matrix artifact.

## 10. Fishbone calibration plan

Define:

- visual tokens to calibrate;
- stable branch-position preservation;
- CURRENT/completed/partial/future state measurement;
- historical-revision invariance tests;
- render-grounded focus-prominence QA.

## 11. Sanitized native-template reconstruction plan

Detail how the one approved backend produces a fresh template package from sanitized descriptors.

Specify:

- reconstruction manifest generation;
- master/layout creation inside the adapter boundary;
- generic docProps generation;
- theme/layout/master part creation;
- relationship construction;
- allowed part families;
- forbidden part families;
- source-part hash non-reuse proof;
- orphan/external relation QA;
- package normalization/determinism considerations.

Explicitly address P3P-5.

## 12. Reconstruction benchmark plan

Define representative benchmark families and selection logic.

At minimum include planned coverage for:

- formal content shell;
- Hypothesis/Problem shell;
- photo + schematic or equivalent figure-first page;
- Control vs Proposed/comparison;
- Result + Discussion;
- image matrix if supported;
- Fishbone/history where supported.

If evidence is absent, the plan must emit `insufficient_evidence`.

Explicitly address P3P-6.

## 13. Quantitative fidelity metric definitions

For every metric in the approved design define the exact formula/input domain.

Include:

- normalized coordinate convention;
- x/y/w/h error;
- edge error;
- IoU;
- dominant figure area ratio;
- text/figure area ratio;
- gutter/column measurement;
- symmetry metric;
- caption/callout geometry;
- whitespace fraction;
- line-width delta;
- font delta;
- CIEDE2000 conversion assumptions;
- Fishbone branch-position delta;
- focus stroke/contrast metric.

Explicitly address P3P-7.

## 14. Image-capable review execution plan

Identify the actual intended image-capable review mechanism for Phase 3 execution.

The plan must define:

- how sanitized acceptance renders are provided to the reviewer;
- how local private reference comparisons are reviewed without committing them;
- render SHA-256 binding;
- controlled reviewer ID;
- slide-specific findings;
- fidelity findings;
- failure/blocking behavior.

If no implementation-time image-capable reviewer is available, define the exact `blocked_visual_review` behavior.

Explicitly address P3P-8.

## 15. Acceptance deck plan

Define how the accepted Phase 2 Ledger/materialized N-layer state flows into calibrated Phase 3 output:

Ledger.load
→ materialization
→ Slide Specs
→ calibrated Layout Director
→ reconstructed sanitized template
→ `PythonPptxAssembler`
→ structural/render/visual QA.

No private exemplar may become a scientific source of truth.

Specify representative slide families that must appear in the acceptance deck.

## 16. Phase 3 QA pipeline

Define owning checks and exact evidence artifacts for:

- ingestion QA;
- sanitizer/privacy QA;
- profile QA;
- resolver/conflict QA;
- archetype calibration QA;
- Fishbone style QA;
- reconstruction/package QA;
- benchmark QA;
- structural PPTX QA;
- scientific/presentation semantic QA;
- render-pixel QA;
- image-capable visual review;
- Professor QA;
- report consistency QA;
- native PowerPoint Stage 8.

No gate may synthesize another gate's PASS.

## 17. Acceptance thresholds and stop/go gates

Create an explicit table of phase-entry/phase-exit requirements.

Implementation must STOP when a hard prerequisite fails.

Examples:

- privacy guard failure → profiler not allowed to open private PPTX;
- sanitizer fail → no profile commit;
- shell hard conflict → no template reconstruction;
- insufficient required archetype evidence → no professor-fidelity PASS;
- reconstruction metric fail → no acceptance fidelity PASS;
- missing image-capable review → blocked visual gate;
- native PowerPoint missing → Stage 8 blocked, production false.

## 18. Negative-test inventory

Enumerate concrete negative tests for all privacy, exemplar-authority, reconstruction, visual-fidelity and Phase 1–2 regression boundaries.

Include every negative case from the approved design and P3P-1–P3P-8 conditions.

## 19. Generated artifact plan

List all intended committed Phase 3 artifacts and all local-only artifacts separately.

For every artifact indicate:

- producer;
- consumer;
- privacy classification;
- schema;
- acceptance role.

## 20. Implementation commits/checkpoints

Propose bounded implementation checkpoints/commits.

Each checkpoint should be independently reviewable and should not combine unrelated subsystems.

Recommended scale:

- privacy/contracts;
- profiler;
- resolver/grammar;
- calibration/template;
- benchmarks;
- acceptance deck;
- QA/report.

## 21. Final Phase 3 implementation delivery contract

Define the final Codex delivery fields that will be required after implementation, including:

- private alias/hash verification;
- sanitizer/privacy status;
- shell/body source-role evidence;
- A01–A18 calibration coverage;
- reconstruction benchmark metrics;
- reconstructed-template privacy proof;
- acceptance PPTX/renders/montages;
- image-capable review;
- Professor QA;
- native PowerPoint status;
- known failures/technical debt.

---

## Planning QA requirements

Before committing the plan:

- verify every section of `PHASE_3_VISUAL_FIDELITY_DESIGN.md` maps to at least one implementation phase/test/artifact;
- verify P3P-1–P3P-8 each have explicit plan coverage;
- verify no implementation code was added;
- verify no private path or private slide content is introduced;
- run `git diff --check`;
- verify only the authorized plan/minimal documentation changes are committed.

---

## Final response for this planning step

Return:

```text
repository:
branch:
commit SHA:
pushed:
remote verification:

plan path:

files added:
files modified:
files deleted:

Design-section coverage:
P3P-1–P3P-8 coverage:

planned implementation phases:
planned red tests count:
planned schemas/contracts:
planned committed artifact classes:
planned local-only artifact classes:

image-capable review mechanism planned:
native PowerPoint handling:

known planning risks:
unresolved planning questions:

READY_FOR_PLAN_REVIEW: yes
```

Then STOP.

Wait for reviewer approval before production Phase 3 implementation.
