# Task — Phase 3 Checkpoint 2 Revision 4

Status: authorized correction only.

Authoritative review: `thesis-deck-system/reviews/PHASE_3_CHECKPOINT_2_REVISION_4_REVIEW.md`

Do not begin Professor Visual Grammar resolution, VisualStyleGovernor calibration, A01–A18 calibration, production Figure Skills, template reconstruction, reconstruction benchmarks, acceptance-deck generation, Phase 4, or public/global Skill registration.

## Scope

Correct only CP2-E1 through CP2-E4.

### CP2-E1 — Placeholder semantics and scope-aware shell support

Implement and test:

- `dt` -> explicit date/time role, never navigation;
- navigation requires independent evidence;
- mixed Master/Layout support cannot be represented by one arbitrary source scope;
- scope-aware support counts/eligible counts/coverage;
- deterministic provenance and source IDs;
- preserve per-container placeholder measurements.

Required negative tests include:

- date/time placeholder cannot satisfy navigation;
- Master + Layout support does not collapse to a nondeterministic single scope;
- coverage denominator for a scope cannot include ineligible containers from another scope;
- placeholder semantics override positional heuristics.

### CP2-E2 — Per-theme palette identity and binding

Implement and test:

- sanitized theme profile IDs;
- separate sanitized palettes per theme part;
- Master -> theme topology;
- correct theme palette resolution for Master/Layout/slide evidence;
- explicit semantic-equivalence evidence before deduplicating themes;
- no raw theme XML/path leakage.

Required tests include two synthetic masters bound to different synthetic theme palettes with the same `accent1` token; resolved RGB must remain different and correctly bound.

### CP2-E3 — Resolver-facing East-Asian/theme typography

Implement and test privacy-safe typography evidence for:

- Latin script;
- East-Asian script;
- complex-script evidence where present;
- explicit typeface;
- theme major/minor role and script;
- sanitized theme font scheme metadata;
- safe Unicode family names;
- inherited/unresolved state without guessing;
- direct body-slide source scope distinct from recurrence-derived scope.

Required negative/positive tests include:

- safe Unicode font survives sanitizer;
- path/URL/private-like Unicode/ASCII font string fails closed;
- `+mj-lt`, `+mn-lt`, `+mj-ea`, `+mn-ea` or equivalent controlled theme tokens map to controlled theme role/script evidence;
- direct `a:ea` typeface is not lost because `a:latin` is absent;
- unresolved inheritance remains unresolved rather than becoming a fabricated exact family;
- `family=unknown` alone cannot satisfy the font-fidelity owning gate.

### CP2-E4 — Owning QA

Add execution-owned checks for:

- placeholder semantic correctness;
- scope-aware shell coverage;
- theme/master topology closure;
- theme-bound color resolution;
- font evidence coverage by explicit/theme/unresolved states;
- safe Unicode font policy;
- body direct-source vs recurrence-derived source-scope correctness.

No check may be a literal PASS.

## Private access

The same existing guarded CP2 private access is authorized only for:

- `private://template_primary_1`
- `private://layout_exemplar_2`
- `private://template_primary_3`

Both pre-open gates must pass first. No new private source is authorized. No private render is required.

## Rebuild

Regenerate as necessary:

- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

Update:

- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

## Required validation

Run at minimum:

- focused CP2 tests;
- CP1 + CP2 tests;
- complete Phase 1–2 + CP1 + CP2 regression in a disposable clean worktree;
- guarded bounded production-private rebuild;
- Draft 2020-12 schema + FormatChecker validation;
- recursive `additionalProperties:false` audit;
- placeholder/date-time/navigation semantic QA;
- scope-aware recurrence/coverage QA;
- theme topology/binding QA;
- color resolution QA;
- East-Asian/theme-font typography QA;
- Unicode safe-font/privacy negative tests;
- repository/staged privacy scan;
- ignored raw-root verification;
- `git diff --check`;
- final scope audit;
- push and remote blob verification.

If the full regression regenerates unrelated Phase 1 deterministic outputs, retain the existing reviewer-approved cleanup discipline. Do not silently expand cleanup scope.

## Delivery

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

CP2-E1:
CP2-E2:
CP2-E3:
CP2-E4:

shell placeholder/date-time/navigation summary:
shell source-scope/coverage summary:
theme profiles/master-theme topology summary:
color theme-binding summary:
body typography explicit/theme/unresolved counts:
East-Asian/theme-font handling summary:
source-session attempts/success/failure:
private render counts/status:
descriptor-quality QA:
privacy scan status:
checkpoint aggregate status:

known failures:
technical debt:
unresolved questions:

Only after push and remote verification write:

`READY_FOR_CHECKPOINT_2_REVIEW: yes`

Then STOP.
