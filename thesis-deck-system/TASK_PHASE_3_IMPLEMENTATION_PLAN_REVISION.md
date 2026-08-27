# Task — Phase 3 TDD Implementation Plan Revision

## Status

Reviewer verdict on `plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`: **REVISE**.

Production Phase 3 implementation remains unauthorized.

The authoritative review is:

`thesis-deck-system/reviews/PHASE_3_IMPLEMENTATION_PLAN_REVIEW.md`

Revise the existing plan in place. Do not create production code, schemas, tests, profiles, templates, renders, or Phase 3 implementation artifacts in this task.

## Required corrections

Address every blocker from the review:

- P3-PLAN-B1 image-capable provider abstraction and preflight;
- P3-PLAN-B2 calibration evidence tiers and separation of deck fidelity from reusable-library coverage;
- P3-PLAN-B3 representative + stress reconstruction benchmark selection;
- P3-PLAN-B4 fresh-lineage/package non-reuse proof replacing universal zero-hash-equality logic;
- P3-PLAN-B5 data-minimized private-render lifecycle;
- P3-PLAN-B6 scope-separated visual-fidelity statuses.

## Concrete plan changes

### 1. Image review provider

Replace durable reliance on the literal `functions.view_image` symbol with a provider/capability contract.

Plan:

- provider preflight before qualitative private-slide classification;
- provider ID and capability evidence;
- Codex view-image use only as one runtime adapter when available;
- `blocked_visual_review` when unavailable;
- tests for absent/non-image/stale/hash-unbound providers.

### 2. Calibration evidence tiers

For A01–A18 define evidence/confidence status distinct from calibration output.

Plan at least:

- recurring direct evidence;
- single-example provisional evidence;
- indirect support;
- insufficient evidence.

One descriptor must not silently establish recurring professor grammar.

Define how reviewer waivers are represented and prohibit builder-generated waivers.

### 3. Benchmark family sampling

Replace complexity-only selection with a dual selection strategy where evidence permits:

- representative/medoid reference;
- difficult/stress reference.

Single-descriptor families must be labeled as such.

Define sanitized feature vector/distance logic and deterministic tie-breaking.

### 4. Template lineage / non-reuse

Revise package reconstruction proof:

- reconstruction entrypoint accepts sanitized descriptors only;
- output package has a part lineage manifest;
- prohibited content-bearing private-part equality is hard failure;
- generic independently generated boilerplate equality is classified as benign equivalence, not copying;
- private media/notes/comments/customXML/embedded content can never cross;
- local comparison remains private and committed evidence contains aggregate/sanitized statuses only.

### 5. Private render minimization

Plan structural-first and streaming visual inspection.

Retain only benchmark/reference renders required for the active review.
Delete temporary non-selected private renders immediately after classification.

Define local retention manifest and cleanup behavior.

### 6. Scope-separated final statuses

Add explicit plan/contracts for:

- private exemplar ingestion;
- shell fidelity;
- body-composition fidelity;
- acceptance-deck visual fidelity;
- Fishbone visual fidelity;
- archetype library calibration coverage;
- native PowerPoint acceptance;
- production Group Meeting readiness.

Do not allow acceptance-deck PASS to imply full A01–A18 reusable-library calibration.

### 7. TDD inventory

Add RED tests covering each correction.

Recompute the total planned test count. Do not keep 116 merely for consistency.

Update task-by-task execution order so capability preflight and privacy protections occur before private visual classification.

## Files allowed

Modify only:

`thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`

plus minimal planning/index documentation if strictly required.

Do not add implementation code or implementation artifacts.

## Required checks

Before commit:

- all P3-PLAN-B1–B6 mapped to concrete modules/tests/evidence/gates;
- all approved design sections still mapped;
- all P3P-1–P3P-8 remain covered;
- no private paths/content appear;
- no production implementation files changed;
- test inventory arithmetic is consistent;
- `git diff --check` passes.

Commit and push to `origin/codex/thesis-deck-system`.

Verify the remote plan blob.

## Final response

Return:

repository:
branch:
commit SHA:
pushed:
remote verification:

plan path:

files added:
files modified:
files deleted:

P3-PLAN-B1–B6 coverage:

image-review provider/preflight summary:
calibration evidence-tier summary:
representative/stress benchmark summary:
package lineage/non-reuse summary:
private-render minimization summary:
scoped fidelity-status summary:

revised RED test count:
Design-section coverage:
P3P-1–P3P-8 coverage:

known planning risks:
unresolved planning questions:

READY_FOR_PLAN_REVIEW: yes

Then STOP. Wait for reviewer approval before production Phase 3 implementation.
