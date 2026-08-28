# Task — Phase 3 Checkpoint 2 Revision 3

## Objective

Close the final resolver-safety gaps identified in `reviews/PHASE_3_CHECKPOINT_2_REVISION_3_REVIEW.md` before Professor Visual Grammar resolution is authorized.

## Authorized scope

Correct only CP2-D1 through CP2-D4.

Do **not** begin:

- Professor Visual Grammar resolver;
- VisualStyleGovernor calibration;
- A01–A18 calibration;
- production Figure Skills;
- sanitized template reconstruction;
- reconstruction benchmarks;
- acceptance deck generation;
- Phase 4;
- public/global Skill registration.

## CP2-D1 — Semantic shell-region recurrence

Replace ambiguous raw-shape recurrence semantics with resolver-safe evidence.

Required:

- prefer placeholder semantics for `title`, `ctrTitle`, `ftr`, `sldNum`, `hdr`, etc.;
- use geometry-only role inference only as a documented fallback;
- prevent accidental role overlap from positional predicates;
- persist `occurrence_count` separately from `source_container_count`;
- persist eligible-container count and/or coverage ratio;
- persist supporting source IDs and source scope;
- ensure resolver-facing recurrence is based on distinct Master/Layout containers, not number of matching shapes.

Negative tests:

- one header-like shape cannot inflate recurrence across multiple containers;
- one shape matching title+header positional rules is not silently counted as both without explicit evidence;
- raw occurrence count cannot masquerade as source-container recurrence.

## CP2-D2 — Reconstructable color/font evidence

Extend sanitized style evidence sufficiently for fresh-template reconstruction while preserving privacy.

Required color evidence where observable:

- direct RGB;
- scheme/theme token;
- resolved sanitized RGB when deterministically resolvable;
- supported tint/shade/lumMod/lumOff transforms;
- explicit unsupported/unresolved transform state;
- source scope and measurement basis.

Do not flatten unresolved theme-backed color to `none` or coarse `accent` only.

Required font evidence where observable:

- exact safe font family;
- theme major/minor role where applicable;
- size/weight/style;
- source scope;
- evidence basis.

Do not collapse valid professor fonts to `other_approved` when the exact safe name can be preserved through an explicit safe-font policy.

Negative tests:

- two distinct direct accent RGBs remain distinguishable;
- theme accent token retains resolved palette evidence;
- unsupported color transform does not silently PASS as exact color;
- safe non-default font name survives sanitizer;
- arbitrary unsafe string cannot cross as a font name.

## CP2-D3 — Rotation truth

Detect DrawingML `rot` on groups and child shapes/connectors.

Choose one truthful implementation:

1. correctly compose rotation into absolute geometry; or
2. mark affected geometry unsupported/not-observable and exclude it from geometry-dependent metrics and structurally-supported family confidence.

Required tests:

- rotated group;
- rotated child inside group;
- nested rotated group if supported;
- unsupported-rotation path cannot emit ordinary `basis=measured` absolute geometry.

Preserve existing off/ext/chOff/chExt, nested scaling/translation, flip and connector marker behavior.

## CP2-D4 — Body typography evidence

Add privacy-safe typography observations for `private://layout_exemplar_2`.

No private slide text may cross.

Resolver-facing observations should support, when inferable:

- title;
- body;
- caption;
- annotation;
- panel label;
- unknown/provisional role.

Persist:

- safe font family or theme font role;
- size;
- weight;
- style;
- source scope;
- role confidence/evidence basis.

If a role is not structurally inferable, preserve the measurement with role `unknown`/provisional rather than inventing semantics.

## Owning QA

Extend execution-derived descriptor QA. Aggregate PASS must require all new owning checks.

At minimum add checks for:

- shell-region semantic recurrence consistency;
- occurrence/container-count separation;
- color reconstruction evidence integrity;
- font evidence integrity;
- rotation truth/exclusion;
- body typography coverage/availability;
- privacy scan over new nested fields;
- complete schema closure.

No new check may be literal PASS.

## Private access

The same three stable aliases may be reopened only through the already-approved guarded CP2 flow after CP2-PRE-1 and CP2-PRE-2 pass.

No new private source is authorized.

No private render is required. `blocked_visual_review` remains acceptable and truthful.

## Artifacts

Regenerate as necessary:

- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

Update:

- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

## Required validation

Run:

- focused CP2 tests;
- CP1+CP2 tests;
- full Phase 1–2 + CP1 + CP2 regression in disposable worktree;
- guarded bounded production-private CP2 rebuild;
- all Phase 3 schemas with `FormatChecker`;
- recursive `additionalProperties: false` audit;
- shell recurrence QA;
- color/font fidelity QA;
- rotation truth QA;
- body typography QA;
- repository/staged privacy scans;
- raw-root ignored/untracked verification;
- `git diff --check`;
- remote branch/artifact verification.

If full regression regenerates unrelated Phase 1 artifacts, preserve the existing exact-path cleanup discipline; do not silently expand a restore allowlist.

## Delivery

Return:

- repository
- branch
- commit SHA
- pushed
- remote verification
- report path
- files added/modified/deleted
- tests/checks run and pass/fail counts
- CP2-D1 through CP2-D4 traceability
- shell region recurrence summary
- theme/direct color preservation summary
- font preservation summary
- rotation handling summary
- body typography summary
- source-session attempts/success/failure
- private render counts/status
- descriptor-quality QA
- privacy scan status
- aggregate checkpoint status
- known failures
- technical debt
- unresolved questions

Only after push and remote verification write:

`READY_FOR_CHECKPOINT_2_REVIEW: yes`

Then STOP. Do not begin Professor Visual Grammar resolution.
