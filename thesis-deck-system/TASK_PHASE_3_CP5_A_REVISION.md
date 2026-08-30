# TASK — Phase 3 CP5-A Revision

## Authorization

Implement **CP5-A revision only**. Do not begin CP5-B or any later checkpoint.

Reviewed implementation commit: `4dd7b2574c7f28d397685f8e22f3a2e34033758a`.

Authoritative review: `reviews/PHASE_3_CP5_A_REVIEW.md`.

## Required corrections

Implement all:

- CP5A-B1 — profile-owned executable SVG language authority;
- CP5A-B2 — namespace + semantic role / visual-class / child-policy enforcement;
- CP5A-B3 — deterministic path / transform / points grammar;
- CP5A-B4 — fully execution-derived QA and full CP4 freeze validation;
- CP5A-B5 — significant text whitespace + namespace-safe canonicalization.

## Required RED / mutation coverage

At minimum prove:

1. profile element-attribute mutation changes behavior or fails profile/code compatibility;
2. profile cannot omit executable grammar identity silently;
3. foreign child element namespace fails;
4. foreign attribute namespace fails;
5. namespace canonicalization cannot collapse foreign attributes/elements into approved SVG names;
6. root visual class mismatch with Figure Spec fails;
7. `control`/`proposed` outside `fair_comparison` fails;
8. `matrix_cell` outside `image_matrix` fails;
9. plot-only roles outside quantitative visual class fail;
10. role with `children_allowed=false` rejects children;
11. registry addressability policy is enforced;
12. synthetic corpus bindings are deterministic and visual-class correct;
13. malformed path with excess unmatched parameters fails;
14. missing path parameter group fails;
15. malformed arc parameter count fails if `A/a` remains allowed;
16. invalid arc flags fail if `A/a` remains allowed;
17. `matrix()` with other than six values fails;
18. invalid `rotate()`/`translate()`/`scale()` arity fails;
19. polyline with fewer than two coordinate pairs fails;
20. polygon with fewer than three coordinate pairs fails;
21. meaningful inter-`tspan` whitespace survives canonicalization;
22. formatting-only whitespace remains deterministically normalizable;
23. missing private-access execution evidence fails QA;
24. nonzero private access counter fails QA;
25. resource/CJK/canonicalization/corpus status dimensions cannot PASS if their owning check fails;
26. all consumed CP4 FigureProductionPlans validate;
27. all consumed CP4 ScientificFigureSpecs validate;
28. CP4 consumed identity/hash mutation invalidates candidate acceptance;
29. candidate hash changes when any new revision dependency changes;
30. full disposable regression tested/current hashes remain independently equal.

Do not target an arbitrary test count; cover the contract.

## Profile requirements

The persisted `scientific-svg-profile.json` must be the authoritative declared language contract. It must include or reference strongly typed, versioned definitions for:

- per-element allowed attributes;
- approved element namespace(s);
- approved attribute namespace/local-name pairs;
- semantic attribute placement;
- path grammar ID/version;
- points grammar ID/version;
- transform grammar ID/version;
- coordinate/numeric rules;
- resource modes;
- canonicalization rules.

Parser implementation may remain in Python, but the selected grammar/version must be explicitly bound to the profile. Unknown/stale profile grammar IDs fail closed.

## Visual-class and role binding

Use the schema-valid ScientificFigureSpec as the authoritative effective visual class.

If SVG root `data-visual-class` is present:

`root_visual_class == figure_spec.visual_class`

is required.

Every semantic role must satisfy its registry `allowed_visual_classes` and `allowed_elements` rules.

Enforce `children_allowed` and addressability semantics.

The ten-fixture synthetic corpus must have explicit deterministic Figure Spec/visual-class binding. Do not reuse the first quantitative Spec for unrelated comparison/Fishbone/mechanism fixtures merely to make language tests pass.

## Geometry grammar

Prefer a small exact grammar over permissive pseudo-parsing.

If supported, SVG path commands must obey exact parameter-group rules. If supporting elliptical arc is disproportionately complex, reduce the CP5-A allowed path subset and document the deferred command rather than accepting malformed paths.

Transform grammar must use exact allowed function arities and finite values.

## QA requirements

No literal owning PASS.

Persist execution-derived facts for the core CP5-A gates. Missing execution evidence fails closed.

Private access evidence must not be fabricated by hard-coded zeros. Bind an execution-owned counter record or equivalent approved session evidence.

`checkpoint-5a-qa.json` status dimensions must be projected from owning checks.

The CP4 freeze check must cover the full consumed plan/spec collections and their current schema/identity bindings.

## Candidate state

Include every execution-affecting revision component, including new/changed:

- source;
- contracts/schema registry source;
- tests where acceptance is test-bound;
- profile;
- role registry;
- synthetic corpus/spec bindings;
- schemas;
- technical Skills;
- privacy scanner/configuration sources used;
- consumed CP4 contracts/artifacts.

Capture TESTED hash from the disposable candidate independently from CURRENT hash.

## Privacy and scope

Required final counters: `0 / 0 / 0`.

No private PPTX/source/render.

No production SVG figure.

No PPTX.

No external code vendoring.

Do not modify CP4 scientific routing semantics.

## Required validation

Run at minimum:

- focused CP5-A revision tests;
- CP1+CP2+CP3+CP4+CP5-A regression;
- full disposable-worktree regression;
- all CP5-A JSON schemas + FormatChecker;
- recursive schema closure;
- profile/code grammar compatibility audit;
- namespace mutation suite;
- role/visual-class/child-policy suite;
- geometry grammar mutation suite;
- CJK/significant-whitespace suite;
- synthetic corpus binding audit;
- execution-owned QA consistency audit;
- full CP4 consumed collection validation;
- candidate-state mutation audit;
- tested/current hash equality;
- repository privacy scan;
- staged privacy scan;
- absolute private-path scan;
- `git diff --check`;
- exact scope audit;
- remote SHA/tree/blob verification.

## Report

Update `reports/PHASE_3_CP5_A_IMPLEMENTATION_REPORT.md` with explicit CP5A-B1–B5 traceability and actual final test counts.

Use a truthful non-self-referential report-footer convention for the implementation commit identity.

## Delivery

Return:

repository:
branch:
commit SHA:
pushed:
remote verification:
report path:
files added/modified/deleted:
focused/full regression pass/fail counts:
CP5A-B1–B5 traceability:
profile-owned attribute/grammar summary:
namespace policy summary:
role/visual-class/children/addressability summary:
synthetic fixture/spec binding summary:
path/transform/points grammar summary:
CJK/significant-whitespace summary:
execution-owned QA count/status:
CP4 freeze validation summary:
candidate-state component count/current/tested hash/equality:
privacy scanner summary:
private alias/source/render counters:
later checkpoint statuses:
known failures:
blocked conditions:
technical debt:
unresolved questions:

Only after commit, push and remote verification write:

`READY_FOR_CP5_A_REVIEW: yes`

Then STOP.
