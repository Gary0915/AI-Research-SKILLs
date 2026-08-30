# Task — Phase 3 External Architecture Final Revision

## Status

External architecture review verdict: **REVISE**.

This is the final narrow design-consistency correction before CP5-A may be authorized.

## Authorized scope

Modify only, as necessary:

- `thesis-deck-system/research/PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_RECONNAISSANCE.md`
- `thesis-deck-system/designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md`
- `thesis-deck-system/artifacts/phase3/external-repo-provenance.json`
- `thesis-deck-system/artifacts/phase3/external-technique-assimilation-matrix.json`

Do not modify CP1–CP4 implementation, schemas, artifacts, Skills, `skill-routing.yaml`, `PythonPptxAssembler`, private fixtures, or any production figure/deck code.

## Required corrections

### EAR-F1 — Separate SVG legality from native compilation capability

Persist an explicit distinction between:

- `svg_ir_support_state` or equivalent — legal/illegal in the canonical Scientific SVG IR;
- `native_compilation_capability_state` — `NATIVE_EXACT`, `NATIVE_NORMALIZED`, `VECTOR_FALLBACK`, `RASTER_FALLBACK`, `UNSUPPORTED`, `UNKNOWN`;
- `native_capability_evidence_level` — `upstream_declared`, `source_inspected`, `thesis_synthetic_verified`, `native_powerpoint_verified`.

Required policy:

- legal SVG + native `UNKNOWN` remains valid canonical SVG;
- legal SVG + native `UNSUPPORTED` remains valid canonical SVG but cannot claim native compilation;
- CP5-C/D/E must not block solely on native `UNKNOWN`/`UNSUPPORTED`;
- missing capability record, illegal SVG IR, undeclared fallback, or contract/provenance failure may block;
- CP5-H owns native-compilation consequences.

Correct CP5-C RED/blocked wording and CP5-D/E blocked wording accordingly.

### EAR-F2 — Reconcile machine-readable target phases

Update the assimilation matrix so review-interaction techniques align with CP5-F:

- OS18 → CP5-F
- OS19 → CP5-F
- OS20 → CP5-F
- OS21 → CP5-F if retained
- OS16 → CP5-F if retained as preview/review UX

Keep PM09 at CP5-F.

Do not change disposition totals unless evidence truly changes the disposition.

Validate final totals remain 24 techniques with reconciled ADOPT/ADAPT/REJECT/DEFER counts.

### EAR-F3 — Make CP5-F qualitative blocking dimension-specific

Clarify in the roadmap:

- render/static review and qualitative image-capable/human review are separate statuses;
- `blocked_visual_review` from an unavailable/unauthorized provider blocks only qualitative acceptance;
- CP5-G implementation and sanitized SVG/render calibration may still proceed;
- CP5-G cannot claim professor qualitative visual acceptance when that evidence is blocked;
- no provider block may be silently promoted into unrelated native or SVG failure.

Persist the relevant readiness/status wording in the human-readable roadmap.

### EAR-F4 — Reconcile committed validation evidence

Update the reconnaissance report/footer so it reflects the actually executed validation described in the delivery, including only checks that were truly run.

At minimum reconcile:

- JSON validation;
- repository/staged privacy scan;
- targeted privacy scanner tests if executed;
- EAR-F/traceability or freeze-scope audits if executed;
- absolute-path scan;
- diff check;
- remote verification.

Do not claim a test count or command not backed by execution.

Update stale provenance wording so open-slide inspection explicitly includes the PPTX export classification rather than describing only HTML/PDF export boundaries.

## Preserve

Do not regress:

- acyclic CP5 DAG;
- minimal SVG semantic metadata;
- scientific provenance outside SVG;
- visual-vs-native readiness separation;
- B01–B10 `blocked_environment` honesty;
- open-slide PPTX = raster/image-slide classification;
- single `PythonPptxAssembler` backend;
- no external code reuse;
- no private access;
- no CP5 implementation.

## Validation

Before commit/push verify:

1. only authorized files changed;
2. CP4 freeze remains untouched;
3. CP5 dependency `cycle_count = 0`;
4. CP5-C/D/E do not treat native `UNKNOWN`/`UNSUPPORTED` as canonical SVG illegality;
5. CP5-H remains the native-compilation/native-fidelity owner;
6. matrix target phases reconcile with roadmap;
7. technique count = 24;
8. ADOPT/ADAPT/REJECT/DEFER counts reconcile;
9. report validation summary matches real execution evidence;
10. B01–B10 remain blocked unless actually rerun;
11. private counters remain 0 / 0 / 0;
12. no external source copied;
13. repository privacy scan passes;
14. staged privacy scan passes;
15. absolute private-path scan passes;
16. `git diff --check` passes;
17. push succeeds;
18. remote SHA/tree/blob verification passes.

## Delivery

Return:

- repository
- branch
- commit SHA
- pushed
- remote verification
- files added/modified/deleted
- EAR-F1–EAR-F4 traceability
- final SVG IR support vs native capability policy
- final CP5-F qualitative blocking policy
- final CP5 target-phase reconciliation
- technique disposition counts
- report/validation consistency status
- CP5 DAG/cycle count
- B01–B10 status
- private alias/source/render counters
- known failures
- blocked conditions
- technical debt
- unresolved questions

Do **not** write `READY_FOR_CP5_IMPLEMENTATION`.

Only after push and remote verification write:

`READY_FOR_EXTERNAL_ARCHITECTURE_REVIEW: yes`

Then stop.
