# Phase 3 External Presentation Architecture — Final Review

## Verdict

**REVISE — narrow roadmap-consistency correction only.**

The revised reconnaissance at `9e51034a18fad42a38223811c1caac86782962ac` correctly closes the major architecture issues from the prior review:

- CP5-A–CP5-I is acyclic (`cycle_count = 0`).
- Static FigureCritic precedes production directors.
- Scientific SVG metadata is reduced to visual identity/local-role metadata; scientific provenance remains Ledger/Spec/Manifest-owned.
- professor SVG/render calibration is independent from native PowerPoint availability.
- native capability state is separated from evidence level and B01–B10 remain honestly `blocked_environment`.
- open-slide PPTX is correctly classified as raster/image-slide export rather than native editable authoring.
- external code remains unvendored and the single `PythonPptxAssembler` backend boundary is preserved.

These decisions are approved and must not be weakened.

## Remaining blockers

### EAR-F1 — Native capability truth must not gate canonical SVG production

The roadmap says that native capability can remain `UNKNOWN` without invalidating a canonical SVG, but later checkpoint wording can still be read as blocking production directors on native capability state. This must be made unambiguous.

The system needs two distinct notions:

1. **Scientific SVG authoring support** — whether a primitive/feature is legal in the CP5-A canonical SVG IR.
2. **PowerPoint native-compilation capability** — `NATIVE_EXACT`, `NATIVE_NORMALIZED`, `VECTOR_FALLBACK`, `RASTER_FALLBACK`, `UNSUPPORTED`, `UNKNOWN` with an evidence level.

A primitive that is legal in the Scientific SVG IR but has native state `UNKNOWN` or `UNSUPPORTED` may still be used by CP5-D/E and statically approved as an SVG figure. Its native compilation remains unresolved/blocked until CP5-H.

Therefore:

- CP5-C must not fail solely because a declared native state is `UNKNOWN`.
- CP5-D/E must not block canonical SVG merely because native capability is `UNKNOWN` or `UNSUPPORTED`.
- CP5-C/D/E must fail only for missing registry identity, illegal SVG IR features, undeclared fallback, scientific/provenance failure, or class-specific contract failure.
- CP5-H owns native editability/compilation consequences.

### EAR-F2 — Technique-assimilation target phases must reconcile with the final roadmap

The machine-readable matrix still assigns several open-slide review-interaction techniques to CP5-E even though the revised roadmap places render/deictic review at CP5-F.

At minimum reconcile:

- OS18 current-element selection → CP5-F
- OS19 comment-to-agent / ReviewAction → CP5-F
- OS20 live design-token override workflow → CP5-F
- OS21 hot-reload/local preview → CP5-F when retained
- OS16 browser-canvas preview convention → CP5-F if retained as review UX rather than evidence-director functionality

PM09 already targets CP5-F and should remain aligned.

No ADOPT/ADAPT/REJECT/DEFER decision count should change merely because of phase reassignment.

### EAR-F3 — CP5-F provider blocking must not create a new dependency block for CP5-G

The roadmap correctly decouples native PowerPoint from visual calibration, but CP5-F currently combines render review, image-capable review and deictic human review.

Clarify status propagation:

- deterministic render generation/review may proceed without a private image-capable provider;
- an unavailable/unauthorized qualitative provider yields `blocked_visual_review` only for that qualitative dimension;
- CP5-G implementation/calibration may proceed using authorized sanitized SVG/render evidence;
- CP5-G must not claim professor qualitative visual acceptance when CP5-F qualitative review is blocked;
- a blocked qualitative provider must not stop geometry/style calibration work that does not require that provider.

### EAR-F4 — Report/footer execution evidence must match the delivered validation

The committed reconnaissance YAML footer currently records empty `tests_run` / `tests_passed`, while the delivery reports JSON validation, repository/staged privacy scans, targeted CP3 privacy scanner tests, traceability/scope audits, absolute-path checks, diff checks and remote verification.

Update the design/research record so the committed validation summary honestly matches what was executed. Do not fabricate commands or results that were not actually run.

Also update any stale open-slide provenance wording that describes only an HTML/PDF boundary now that `export-pptx.ts` was explicitly inspected and classified.

## Approved architecture after correction

Subject to EAR-F1–F4, the approved future sequence is:

`CP5-A Scientific SVG IR/static QA → CP5-B native capability registry → CP5-C FigureOutputManifest/static FigureCritic → CP5-D structured directors + CP5-E evidence-bound directors → CP5-F render/deictic review → CP5-G A01–A18 SVG/render calibration → CP5-H DrawingML adapter/native fidelity → CP5-I template/acceptance/release`.

## Scope

This review does **not** authorize CP5 implementation. Only the four existing reconnaissance/design artifacts may be corrected. CP1–CP4 implementation, schemas, Skills, routing, assembler and private fixtures remain frozen.
