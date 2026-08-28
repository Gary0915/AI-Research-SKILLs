# Task — Phase 3 Checkpoint 2 Revision 2

## Purpose

Close the remaining resolver-readiness blockers in Checkpoint 2 without beginning Professor Visual Grammar resolution or any later Phase 3 work.

Authoritative reviewer findings:

`thesis-deck-system/reviews/PHASE_3_CHECKPOINT_2_REVISION_2_REVIEW.md`

Correct only:

- CP2-C1 — shell evidence source correctness;
- CP2-C2 — grouped geometry and connector semantics;
- CP2-C3 — real body metrics and conservative family classification;
- CP2-C4 — owning descriptor-quality QA and session/sanitizer lifecycle truth;
- CP2-C5 — theme/style observability.

## Scope boundary

Allowed:

- reopen the same three stable production aliases through the existing guarded Checkpoint 2 flow after CP2-PRE-1 and CP2-PRE-2 pass;
- inspect read-only OOXML structure needed to measure Master/Layout/theme/body geometry;
- update CP2 implementation, typed schemas, synthetic tests, sanitized descriptors, QA, and CP2 report.

Not allowed:

- Professor Visual Grammar resolver;
- VisualStyleGovernor calibration;
- A01–A18 calibration;
- production Figure Skill implementation;
- sanitized professor template reconstruction;
- reconstruction benchmark slides;
- acceptance deck;
- Phase 4;
- global/public Skill registration.

## CP2-C1 — shell measurement source scope

Every committed shell measurement must have a controlled source scope.

Minimum enum:

- `slide_master`
- `slide_layout`
- `theme`
- `slide_recurrence_derived`
- `not_observable_structurally`

Profile shell authority primarily from slideMaster and slideLayout parts:

- Master/Layout topology;
- placeholder role/type and geometry;
- recurring Master/Layout shell shapes;
- title/header/footer/page-number/navigation candidate geometry;
- typography and style roles;
- content-region exclusions / safe-area evidence.

Slide-level recurrence may corroborate a shell token, but a one-off slide-body object may not become shell grammar.

Required tests:

- unique body picture does not enter recurring shell primitives;
- unique connector does not enter recurring shell primitives;
- Master-owned footer/page-number primitive does;
- Layout-owned title placeholder does;
- no-evidence safe area is marked not observable rather than defaulted to full-slide or a fixed rectangle;
- shell resolver inputs retain source scope and recurrence evidence.

## CP2-C2 — group transform and connector semantics

Implement proper OOXML transform composition.

For group shapes, apply parent `grpSpPr/a:xfrm` including:

- `off`
- `ext`
- `chOff`
- `chExt`
- nested groups
- flips where applicable

Produce absolute normalized slide geometry after composition.

Connector records must include controlled fields sufficient to identify direction without private text, for example:

- start point
- end point
- orientation
- head arrow type
- tail arrow type
- directedness
- flip state where needed
- basis/source scope

Do not infer direction solely from bounding-box order.

Required synthetic PPTX tests:

- grouped rectangle absolute geometry;
- nested group absolute geometry;
- group scaling/translation;
- flipped connector endpoint semantics;
- head-only arrow;
- tail-only arrow;
- plain line;
- geometry tolerance assertion.

## CP2-C3 — real metric observations

Replace placeholder numeric defaults with typed observations.

A metric that is not actually measured/derived must be represented as unavailable/insufficient rather than numeric zero.

Introduce a metric observation contract or equivalent with:

- value (nullable where appropriate)
- basis
- evidence/status
- supporting object IDs where appropriate

Implement structural derivations where feasible:

### Panel candidates

Cluster repeated picture/shape regions using normalized geometry and spacing.

### Matrix candidates

Estimate row/column candidates only when repeated aligned regions support a grid signature.

### Comparison symmetry

Derive from paired region geometry / relative area / alignment only when a plausible comparison pair exists.

### Caption candidates

Use geometry/proximity of text regions relative to figure/panel regions; do not export text.

### Photo/schematic relationship

Use picture regions versus vector/group/native-shape regions and spatial relation.

### Whitespace / area

Avoid naive summed-area interpretation when overlap materially changes occupied area. Use union/cluster approximation or clearly label the weaker estimator.

### Candidate families

Family classification must have family-specific signatures and persisted supporting features.

Do not use these as sufficient proof by themselves:

- pictures >= 4 => image matrix
- pictures >= 2 => Control/Proposed
- connectors >= 3 => Fishbone

Required negative tests:

- four unrelated pictures are not automatically image matrix;
- two unrelated pictures are not automatically Control/Proposed;
- ordinary flowchart with >=3 connectors is not automatically Fishbone;
- family with weak signature becomes provisional/insufficient;
- structurally supported family must reference the supporting feature IDs/metrics.

## CP2-C4 — executable descriptor-quality QA

Every DQ PASS must be derived from an owning function/result.

Do not append literal PASS for prohibited fields or any other DQ check.

Required owning checks include at least:

- nested privacy/prohibited-value scan over final sanitized payload;
- shell source-scope validation;
- shell recurrence/source correctness;
- body metric observation validity;
- no placeholder-zero masquerading as derived measurement;
- candidate-family evidence/confidence consistency;
- group absolute-geometry validation;
- source-session lifecycle consistency;
- sanitizer handoff/outcome consistency;
- schema closure;
- shell/body authority separation;
- slide/descriptor coverage.

Source-session lifecycle change:

A private source session may be `profiling_complete` before sanitizer handoff, but it must not be closed `outcome=success` until that alias has passed sanitizer handoff.

If sanitizer handoff fails:

- close session as failed;
- preserve sanitized failure evidence;
- aggregate Checkpoint 2 must fail.

Add a negative test proving sanitizer failure cannot coexist with a successful source session.

## CP2-C5 — theme/style role extraction

Enhance structural color/style extraction without exporting private content.

Support, where present:

- direct `srgbClr`;
- `schemeClr` / theme roles;
- explicit no-fill/no-line;
- unresolved/unknown source.

Do not collapse unresolved theme-backed colors into `none`.

Sanitized style observations should distinguish controlled concepts such as:

- `none`
- `neutral`
- `accent`
- `emphasis`
- `background`
- `theme:<controlled-role>` or equivalent controlled token
- `unknown`

Profile theme relationships read-only and keep raw theme XML local-only.

Typography/color/style observations must carry basis/source scope where relevant.

## Privacy preservation

Preserve all existing CP2 privacy boundaries:

- stable aliases only in committed output;
- exact legacy exception;
- repository/staged privacy scanning;
- no paths/basenames/private text/notes/media/URLs/raw XML/package-part hashes in committed descriptors;
- ignored local raw profiles only;
- zero private renders retained;
- private qualitative review may remain `blocked_visual_review`.

## Required artifacts

Regenerate:

- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

Update:

- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

Update canonical schemas as required.

## Tests / checks

Run at minimum:

- focused Checkpoint 2 tests;
- Checkpoint 1 + 2 tests;
- full Phase 1–2 + Phase 3 CP1/CP2 regression suite;
- schema validation with FormatChecker;
- recursive `additionalProperties: false` audit;
- group-transform geometry tests;
- connector-direction tests;
- metric-observation tests;
- family-classification negative tests;
- descriptor-quality owning QA tests;
- session/sanitizer lifecycle negative tests;
- bounded production-private CP2 rebuild;
- repository/staged privacy scan;
- ignored raw-root verification;
- `git diff --check`;
- remote branch/artifact verification.

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

CP2-C1:
CP2-C2:
CP2-C3:
CP2-C4:
CP2-C5:

shell source-scope summary:
master/layout/theme measurements:
slide-recurrence corroborations:
unique body objects excluded from shell:

body metric observations:
panel/matrix/comparison/caption/photo-schematic derivation summary:
family confidence/evidence summary:

group-transform tests:
connector-direction tests:

source-session attempts/successes/failures:
sanitizer handoff failures:
private renders created/deleted/retained:
private qualitative review status:

descriptor-quality QA:
repository/staged privacy scan:
checkpoint aggregate status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_2_REVIEW: yes

Then STOP.

Do not begin Professor Visual Grammar resolution.