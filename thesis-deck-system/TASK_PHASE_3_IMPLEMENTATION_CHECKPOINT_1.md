# Phase 3 Implementation Checkpoint 1 — Contracts / Privacy / Provider Boundary

## Authorization

This task authorizes **Checkpoint 1 only** of the approved Phase 3 TDD implementation plan.

Authoritative plan:

`thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`

Authoritative final plan review:

`thesis-deck-system/reviews/PHASE_3_IMPLEMENTATION_PLAN_FINAL_REVIEW.md`

Do not implement later Phase 3 checkpoints until reviewer approval.

## Purpose

Establish the complete safety/control boundary **before any production private exemplar is opened or profiled**.

The checkpoint must implement the Phase A contract/privacy/provider foundations required by the approved plan and enough typed contracts to prevent later phases from creating ambiguous or unsafe outputs.

## Hard stop

During this checkpoint:

- do **not** open/read/profile any production private exemplar PPTX;
- do **not** resolve production private local paths;
- do **not** render private slides;
- do **not** emit sanitized professor profiles from the real exemplars;
- do **not** reconstruct the native template;
- do **not** calibrate A01–A18;
- do **not** generate scientific figures or the Phase 3 acceptance deck;
- do **not** begin Phase 4;
- do **not** globally/publicly register Skills.

Only redistributable synthetic/canary fixtures may exercise privacy/contracts/provider behavior.

## Required implementation areas

### CP1-1 — Privacy root and pre-open guard

Implement the ignored/local-only private profile storage guard specified by the plan.

It must prove, before a future private alias can be opened, that the raw-profile root is:

- outside committed artifact directories;
- ignored/untracked;
- not staged;
- not a symlink/redirect into a committable directory;
- writable only as intended;
- subject to cleanup/retention policy.

Negative tests must reject unsafe roots before source open.

### CP1-2 — Fail-closed sanitizer/scanner foundation

Implement the allowlist-based sanitizer foundation and repository privacy scanner.

Unknown/untyped fields must fail closed.

Scanner test corpus must detect at least:

- absolute Windows/private paths;
- private basenames/canaries;
- URLs/DOIs where prohibited;
- speaker notes/private text canaries;
- author/company metadata canaries;
- media/embedded filenames;
- raw OOXML/package fragments;
- staged private PPTX/render candidates.

Do not include real private values in committed tests; use synthetic canaries.

### CP1-3 — Provider abstractions

Implement typed provider boundaries for:

- `ImageReviewProvider`
- `ConceptImageProvider`

No repository contract may depend on a literal runtime tool/vendor name.

Image-review capability must include at least:

- provider_id;
- image_capable;
- hash_binding_supported;
- private_content_allowed;
- approved_for_private_exemplars;
- egress_mode;
- retention_class;
- supported input/path form if applicable.

Private-reference preflight must fail/return blocked when any required privacy capability is absent.

A provider that is image-capable but private-unauthorized may review sanitized renders only; it cannot certify private-reference visual fidelity.

### CP1-4 — Figure routing and output contracts

Implement schemas/contracts only for the Phase 3 figure control plane, without production figure generation.

At minimum:

- FigureProductionPlan;
- ScientificFigureSpec;
- discriminated FigureOutputManifest;
- FigureCriticReport;
- VisualStyleProfile;
- SkillRouting contract/schema.

The FigureOutputManifest must support the approved primary-artifact variants:

- vector_diagram;
- scientific_plot;
- real_photo;
- literature_figure;
- concept_illustration;
- native_shape_figure.

Cross-class masquerading must fail validation.

Generated conceptual content must require `evidence_status=non_evidence` and must not support scientific claims.

### CP1-5 — Observation evidence contract

Implement the contract-level rule that empirical Observation evidence cannot be satisfied by generated conceptual imagery.

Synthetic negative tests must prove:

- concept illustration cannot satisfy Observation evidence refs;
- empirical Observation requiring Evidence fails without valid empirical source;
- concept illustration may coexist only as separately bound auxiliary non-evidence visual.

Do not alter approved Phase 2 story semantics.

### CP1-6 — Fabrication/process contract boundary

Implement the typed contract boundary required for the future `fabrication-process-director` without implementing the renderer/director logic yet.

It must distinguish fabrication/process chronology from:

- mechanism explanation;
- measurement/experiment schematic.

The contract must preserve:

- ordered steps;
- material/state refs;
- known conditions;
- timing/temperature when known;
- state transitions;
- provenance;
- explicit unknown values rather than invented parameters.

### CP1-7 — Skill contract/routing schema foundation

Define the machine-readable structure that later repo-local Skills must conform to.

Do not globally register or publish Skills.

Checkpoint 1 may add schema/contracts and synthetic routing fixtures/tests, but should not implement all Phase 3 Skill files yet unless strictly necessary to validate the contract shape.

## RED/GREEN requirement

Follow TDD.

Checkpoint 1 should implement the approved Phase A RED inventory and any additional contract-level RED cases necessary for CP1-1 through CP1-7.

The final report must state the exact tests added rather than claiming the planned count automatically.

Do not weaken a failing contract to make tests green.

## Regression requirement

Run all existing Phase 1–2 tests plus the new Checkpoint 1 tests.

Approved Phase 1–2 artifacts/contracts must remain backward compatible unless the Phase 3 plan explicitly introduces an additive versioned contract.

## Required evidence/artifacts

Committed outputs may include only non-private implementation/test evidence, for example:

- new/updated schemas;
- provider-capability synthetic fixtures;
- privacy scanner synthetic canary fixtures;
- contract/routing synthetic fixtures;
- Checkpoint 1 QA JSON;
- Checkpoint 1 implementation report.

Do not commit raw/private profiler artifacts.

## Checkpoint QA

Produce a machine-readable checkpoint QA record proving at least:

- private_source_open_attempts = 0;
- real_private_alias_resolution_attempts = 0;
- provider private-authorization negatives pass;
- sanitizer/scanner negatives pass;
- discriminated figure variants validate/reject correctly;
- Observation evidence negatives pass;
- fabrication contract negatives pass;
- Phase 1–2 regression status.

## Report

Create:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_1_IMPLEMENTATION_REPORT.md`

Include explicit traceability:

- CP1-1 Privacy root/pre-open guard
- CP1-2 Sanitizer/scanner
- CP1-3 Provider abstractions
- CP1-4 Figure contracts
- CP1-5 Observation evidence boundary
- CP1-6 Fabrication contract boundary
- CP1-7 Skill/routing contract foundation

## Final delivery

Commit and push all Checkpoint 1 work to:

`origin/codex/thesis-deck-system`

Verify remote head and required artifacts.

Return:

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

CP1-1 through CP1-7 traceability:

private source open attempts:
real private alias resolution attempts:
privacy scanner status:
provider authorization status:
figure contract status:
Observation evidence status:
fabrication contract status:
Phase 1–2 regression status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_1_REVIEW: yes

Only write `READY_FOR_CHECKPOINT_1_REVIEW: yes` after the checkpoint is pushed and remotely verified.

Then STOP.

Do not begin Checkpoint 2 or any private exemplar production profiling.
