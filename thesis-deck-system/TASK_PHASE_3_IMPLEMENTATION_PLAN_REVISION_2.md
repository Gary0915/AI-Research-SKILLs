# Task — Phase 3 TDD Implementation Plan Revision 2

## Authorization

Plan revision only. Production Phase 3 implementation is NOT authorized.

Revise:

`thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`

using:

`thesis-deck-system/reviews/PHASE_3_IMPLEMENTATION_PLAN_REVISION_2_REVIEW.md`

as the authoritative correction specification.

## Required corrections

Address all:

- P3-PLAN-C1 — artifact-type-aware Figure Output Manifest;
- P3-PLAN-C2 — Observation evidence vs conceptual-image separation;
- P3-PLAN-C3 — privacy-authorized ImageReviewProvider;
- P3-PLAN-C4 — fabrication/process-flow specialist.

### C1 acceptance

Plan a discriminated figure-output contract so every visual class preserves its true canonical source/output lineage rather than universally requiring SVG. Add RED tests for each variant and cross-class masquerading failures.

### C2 acceptance

Observation evidence must derive from actual evidence/source data. Conceptual imagery may be auxiliary non-evidence only and cannot satisfy Observation evidence bindings. Add routing and semantic-negative tests.

### C3 acceptance

Private-reference review requires an image-capable AND private-content-authorized provider. Add provider privacy fields, preflight behavior, blocked states, and negative tests for capable-but-unauthorized providers.

### C4 acceptance

Add a bounded `fabrication-process-director` (or equivalent explicit name) for preparation/process chronology. Do not merge it into causal mechanism or measurement setup. Plan its contract, routing, vector outputs, provenance, tests, and relevant archetype handoffs.

## Preserve

Preserve all previous approved design constraints and all P3-PLAN-B1–B6 corrections. Keep the plan-only boundary. Do not add code, schemas, Skills, private profiles, renders, templates, benchmarks, or implementation artifacts.

## Test plan update

Add RED cases for C1–C4 and recalculate the total test count; do not preserve 285 if the correct count changes.

## Self-check

Before push verify:

1. all 22 design sections remain mapped;
2. P3P-1–P3P-8 remain mapped;
3. P3-PLAN-B1–B6 remain mapped;
4. P3-PLAN-C1–C4 are mapped;
5. figure artifact variants are explicit;
6. Observation cannot use generated imagery as evidence;
7. private provider authorization is explicit;
8. fabrication/process route is explicit;
9. Skill routing includes the new specialist;
10. RED arithmetic is correct;
11. no production file changed;
12. no private path/content introduced;
13. `git diff --check` passes;
14. remote plan blob matches the pushed commit.

## Delivery

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

P3-PLAN-C1:
P3-PLAN-C2:
P3-PLAN-C3:
P3-PLAN-C4:

figure output variants planned:
Observation evidence rule:
private image-review provider rule:
fabrication/process Skill:

planned RED tests count:
test-count arithmetic:

known planning risks:
unresolved planning questions:

READY_FOR_PLAN_REVIEW: yes

Then STOP and wait for reviewer approval before production Phase 3 implementation.