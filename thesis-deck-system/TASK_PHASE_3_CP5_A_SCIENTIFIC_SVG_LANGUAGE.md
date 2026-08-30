# TASK — Phase 3 CP5-A: Scientific SVG Language and Static SVG QA

## Authorization

Implement **CP5-A only**. Do not begin CP5-B or later checkpoints.

The external architecture gate is approved at reviewed commit `b8124fb838170aed420ce5820b20a1d84ba5bce0` and reviewer approval file `reviews/PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_APPROVAL.md`.

## Purpose

Create a thesis-owned, closed, deterministic **Scientific SVG intermediate representation** that every future scientific figure director must use. CP5-A establishes the language, semantic metadata boundary, canonicalization, synthetic fixtures, static validator, technical Skills, execution-owned QA, and candidate-bound regression evidence. It does **not** create production scientific figures.

The Scientific SVG IR is visual authoring state only. Scientific truth remains in Ledger/materialization/ScientificFigureSpec/FigureOutputManifest.

## Non-negotiable scientific authority

Preserve the professor-required Scientific Method:

Observation → Literature → Mechanism → Solution → Experiment → Result → Discussion → Decision → Next Step.

Preserve N-layer history, separate Hypothesis and Problem pages, required Fishbone page per layer, immutable Fishbone revisions, failed/negative experiment history, all-results-before-summary ordering, asymmetric exemplar authority, and structured high-information-density composition.

No external presentation convention may override these rules.

## CP5-A boundaries

### Allowed

- CP4 read-only contract/freeze validation.
- New CP5-A source modules.
- New schemas/contracts/profile artifacts.
- New synthetic fixtures only.
- New repository-local technical Skills for Scientific SVG authoring/governance.
- Static XML/SVG validation and canonicalization.
- Hash/candidate-state evidence.
- Disposable-worktree regression.

### Forbidden

Do not implement or produce:

- production Fishbone SVG;
- production mechanism diagram;
- production experiment schematic;
- production fabrication/process diagram;
- production comparison/image matrix;
- production plot;
- real-photo annotation;
- literature extraction/rendering;
- concept image generation;
- FigureOutputManifest/static FigureCritic production gate (CP5-C);
- CurrentSlideContext/ReviewAction/live editor (CP5-F);
- A01–A18 calibration (CP5-G);
- DrawingML compiler (CP5-H);
- template reconstruction, PPTX, acceptance deck (CP5-I);
- private exemplar access;
- native PowerPoint acceptance claims;
- direct reuse/vendoring of PPT Master/open-slide code.

## CP5-A1 — Versioned Scientific SVG profile

Implement a schema-backed, versioned profile artifact, for example:

`scientific-svg-profile.json`

with a stable profile ID/version and explicit policies for:

- SVG root contract;
- allowed elements;
- allowed attributes by element;
- allowed namespaced attributes;
- semantic metadata allowlist;
- ID rules;
- coordinate/unit rules;
- transform policy;
- text/CJK policy;
- resource-reference policy;
- styling policy;
- forbidden executable/browser features;
- canonicalization version;
- hashing rules;
- validation severity/status vocabulary.

All nested objects must be strongly typed and `additionalProperties: false` where applicable.

No permissive catch-all SVG browser compatibility mode.

## CP5-A2 — Conservative element allowlist

Start with the smallest practical structured-scientific subset needed by the known future figure families. The exact final list must be evidence/rationale-backed, but should consider only controlled forms of:

- `svg`
- `g`
- `defs`
- `rect`
- `circle`
- `ellipse`
- `line`
- `polyline`
- `polygon`
- `path`
- `text`
- `tspan`
- `image`
- `marker`
- `clipPath`

Do not automatically allow arbitrary SVG elements.

Explicitly reject unless later reviewed:

- `script`
- `foreignObject`
- animation elements
- event-handler attributes
- embedded executable content
- external CSS
- uncontrolled filters/effects
- arbitrary HTML
- remote network resources
- XML external entities / DTD expansion.

If a future needed feature is not in CP5-A, it should fail closed and require profile revision rather than silently pass.

## CP5-A3 — Attribute allowlist and style discipline

Implement element-specific attribute validation.

Support only the controlled attributes needed for scientific vector structure, such as applicable subsets of:

- geometry: `x`, `y`, `width`, `height`, `cx`, `cy`, `r`, `rx`, `ry`, `x1`, `y1`, `x2`, `y2`, `points`, `d`;
- coordinate system: `viewBox`, `preserveAspectRatio`;
- transforms: `transform` under controlled grammar;
- paint: `fill`, `fill-opacity`, `stroke`, `stroke-width`, `stroke-opacity`, `stroke-linecap`, `stroke-linejoin`, `stroke-dasharray`, `opacity`;
- text: `font-family`, `font-size`, `font-weight`, `font-style`, `text-anchor`, `dominant-baseline`, `dx`, `dy`;
- references: `marker-start`, `marker-end`, `clip-path`, `href` under safe-reference rules;
- stable IDs and approved semantic attributes.

Prefer presentation attributes / explicit local attributes over unrestricted `<style>` blocks or external stylesheets so static validation remains deterministic.

Do not use professor material-semantic colors in CP5-A synthetic fixtures as if they were established style truth.

## CP5-A4 — Minimal rendering-neutral semantic metadata

Mandatory metadata must remain minimal:

- root Scientific SVG profile/version;
- root figure ID;
- stable addressable object ID;
- local semantic role on addressable scientific objects.

Optional:

- visual class where needed for static rules.

Do not encode authoritative scientific provenance in SVG:

- Hypothesis Layer;
- Research Block;
- Stage;
- Claim;
- Evidence;
- source cursor;
- source hash;
- Decision;
- Action;
- scientific provenance chain.

If a future non-authoritative mirror is ever supported, CP5-A must not enable it as scientific truth.

Semantic metadata must be rendering-neutral. Removing approved semantic metadata must not alter the visible/presentation AST.

## CP5-A5 — Stable object identity

Define deterministic object-identity requirements.

At minimum:

- every addressable object has a unique stable ID within one figure;
- duplicate IDs fail;
- IDs must match a controlled pattern;
- IDs must not be generated from mutable pixel geometry, display text, or z-order alone;
- object IDs should remain stable across revisions when the same conceptual visual object changes geometry/style/text;
- object IDs may change when the object is semantically replaced;
- XML child order remains meaningful because SVG source order controls z-order.

Canonicalization must never reorder child elements merely to obtain a stable hash.

## CP5-A6 — Semantic-role registry

Create a versioned, schema-backed semantic-role registry.

The registry must be local-visual semantics, not research provenance.

It should cover reusable role families needed by known future visuals without overclaiming material-specific professor styling. Candidate role families include:

- structure: `container`, `panel`, `group`, `node`;
- text: `title`, `label`, `caption`, `annotation`, `callout`;
- connections: `connector`, `arrow`, `flow`, `branch`, `spine`;
- emphasis: `highlight`, `focus`;
- scientific schematic: `sample`, `electrode`, `instrument`, `interface`, `input`, `output`, `process_step`, `material_state`;
- comparison/matrix: `control`, `proposed`, `matrix_cell`, `panel_label`;
- plot-local: `plot_area`, `axis`, `data_series`, `legend`;
- image-local: `image`, `overlay`.

If specialized roles such as `heat_flow` or `ion_transport` are included, treat them as local visual semantics only and do not infer color/style from the role.

Unknown semantic role must fail closed unless the role is first added through a versioned registry change.

Persist for each role where useful:

- role ID;
- category;
- allowed visual classes;
- allowed element families;
- addressability requirement;
- whether children are permitted;
- whether role is reusable or specialized;
- description.

## CP5-A7 — Coordinate and numeric policy

Define deterministic numeric/geometry rules.

At minimum:

- root `viewBox` is required;
- finite numeric values only;
- no NaN/Infinity;
- no percentage-based geometry unless explicitly justified;
- no absolute OS-dependent measurements;
- negative widths/heights/radii fail;
- path data must parse under the allowed path grammar;
- transforms must parse under the controlled transform grammar;
- canonical numeric formatting is deterministic;
- z-order follows source order and is preserved.

Do not hard-code one figure aspect ratio for every visual class. Figure geometry belongs to future specs/layout/calibration.

## CP5-A8 — Text and CJK policy

Scientific SVG must preserve editable Unicode text.

Requirements:

- UTF-8;
- Chinese/English mixed text supported;
- text remains `<text>/<tspan>` rather than being converted to paths in canonical SVG;
- no bundled/private font files;
- no fabricated font availability claim;
- explicit font family/size/style may be used only under the resolved style input in later checkpoints;
- CP5-A synthetic fixtures may use safe generic test fonts and must label them synthetic/fallback, not professor preference;
- XML escaping and Unicode normalization policy must be deterministic;
- no lossy ASCII transliteration.

Add synthetic mixed CJK/English fixtures and round-trip/static canonicalization tests.

## CP5-A9 — Resource-reference policy

Canonical SVG must be portable and privacy-safe.

Reject:

- `http://`
- `https://`
- `file://`
- Windows absolute paths
- UNC paths
- WSL-mounted private paths
- parent traversal outside the figure bundle
- uncontrolled external entities.

Define explicit permitted image/reference forms. Prefer a portable controlled policy such as:

- safe relative package-local asset references; and/or
- bounded data URI only for synthetic/test assets where explicitly allowed.

Any later real photo/literature evidence identity remains outside SVG in Figure Spec/Manifest. CP5-A must not turn image `href` into evidence authority.

Add path traversal and private-path negative tests.

## CP5-A10 — Static validator

Implement a deterministic validator owned by thesis-deck-system.

The validator must execute real checks, not literal PASS fields.

At minimum validate:

1. XML well-formedness;
2. root element/profile/version;
3. namespace policy;
4. element allowlist;
5. per-element attribute allowlist;
6. forbidden executable/browser content;
7. object-ID uniqueness/pattern;
8. semantic-role registry membership;
9. semantic-role/element compatibility;
10. viewBox/numeric geometry rules;
11. transform grammar;
12. path/points grammar;
13. safe references/resources;
14. CJK/UTF-8 preservation;
15. forbidden scientific-provenance metadata;
16. metadata rendering-neutrality at static AST level;
17. deterministic canonicalization;
18. canonical SVG/spec figure-ID binding for synthetic specs;
19. no silent raster fallback marker;
20. no private path/basename leakage.

Persist structured findings with:

- check ID;
- severity;
- object ID/path where applicable;
- rule ID;
- finding message;
- pass/fail/block status.

Aggregate PASS only from executed checks.

## CP5-A11 — Canonicalization and hashing

Create a documented deterministic canonicalization algorithm.

Requirements:

- preserve child/source order;
- normalize XML declaration/encoding policy;
- normalize namespace declarations deterministically;
- sort attributes only where XML semantics/rendering are unaffected;
- normalize numeric serialization according to a versioned rule;
- normalize insignificant whitespace without changing visible text;
- preserve text node content and significant whitespace;
- no automatic geometry simplification;
- no path reordering;
- no z-order changes;
- no semantic metadata removal in the canonical source hash.

Persist at least:

- exact source SHA-256;
- canonical SVG SHA-256;
- profile/canonicalization version.

Optionally define a separate presentation-structure hash for metadata-invisibility tests, but do not confuse it with the canonical asset identity.

Identical semantic source under irrelevant formatting changes should canonicalize identically when safe; visible text/order/geometry mutations must change the appropriate hash.

## CP5-A12 — Metadata invisibility QA

Because CP5-A does not yet own render-based FigureCritic, prove metadata invisibility statically.

Recommended approach:

- parse canonical SVG;
- create a copy with only approved `data-thesis-*` / semantic attributes removed;
- compare the presentation-relevant AST/tree after normalization;
- require geometry, paint, text, transforms, references and source order to remain identical.

Do not claim pixel-equivalent render evidence from this static test.

Persist status as static metadata-invisibility evidence only.

## CP5-A13 — Synthetic fixture corpus

Create a sanitized synthetic CP5-A fixture corpus exercising the language, not professor visuals.

At minimum include valid fixtures for:

- simple shapes + text;
- connector + marker arrow;
- grouped mechanism-like blocks;
- experiment-like schematic primitives;
- Fishbone-like spine/branches;
- comparison panels;
- path/polyline geometry;
- clipPath/image-safe-reference example;
- mixed Chinese/English text;
- transforms/rotation under allowed grammar.

Also create negative fixtures/mutations for all major RED cases.

Synthetic fixtures must not be called production figures or professor-calibrated outputs.

## CP5-A14 — Technical repository-local Skills

Create/update repository-local technical Skills as needed, without globally/publicly registering them.

At minimum evaluate and normally implement:

### `scientific-svg-authoring`

Owns:

- CP5-A SVG language;
- allowed elements/attributes;
- object IDs;
- coordinates;
- text/CJK rules;
- resource references;
- canonicalization expectations;
- handoff to validation.

It must NOT own scientific truth, figure routing, professor style selection, Layout, or PPTX assembly.

### `semantic-svg-governor`

Owns:

- semantic metadata allowlist;
- semantic-role registry;
- local role validation;
- non-authoritative boundary;
- metadata invisibility rule.

It must NOT store Ledger provenance or infer scientific claims.

If existing Skills already cover these exact responsibilities, extend them instead of duplicating.

Update the repository-local Skill routing/registry only if required by the CP5-A technical-Skill registration contract; do not modify CP4 scientific routing semantics.

## CP5-A15 — Closed schemas/contracts

Add schema-backed contracts for every persisted CP5-A artifact.

Likely classes include:

- Scientific SVG Profile;
- Semantic Role Registry;
- Static SVG QA Report;
- Scientific SVG identity/canonicalization record;
- CP5-A execution evidence/report facts.

Use Draft 2020-12 / existing repository convention.

Nested objects must be strongly typed.

Add schema-closure negative tests.

Do not attempt to schema-validate raw SVG using an overly permissive JSON abstraction; raw SVG must be parsed/validated by the Scientific SVG validator.

## CP5-A16 — Input/freeze authority

CP5-A must bind to the approved CP4 control-plane state without modifying it.

At minimum verify/have candidate-state component hashes for the relevant CP4 contracts/artifacts that define:

- FigureProductionPlan;
- ScientificFigureSpec;
- visual class/routing authority;
- current approved Visual Style Profile identity where referenced.

CP5-A synthetic specs may be used for tests, but they must conform to approved CP4 contracts.

No private exemplar artifact is an input.

## CP5-A17 — Candidate-bound regression and QA

Create execution-derived CP5-A QA.

Candidate state must include all execution-affecting CP5-A components, including:

- CP4 consumed input contracts/artifacts;
- CP5-A source modules;
- CP5-A schemas;
- profile/role-registry artifacts;
- CP5-A technical Skill files;
- any routing/registry file modified by CP5-A;
- synthetic fixture definitions used as canonical acceptance inputs.

Full regression must run in a disposable worktree if the existing suite mutates generated artifacts.

Persist tested candidate hash independently from the recomputed current candidate hash.

PASS only when equal and all required tests pass.

## CP5-A18 — Required RED tests

Implement direct negative tests at minimum for:

1. unknown SVG element;
2. unknown attribute;
3. `script`;
4. `foreignObject`;
5. event-handler attribute;
6. DTD/external entity;
7. remote HTTP image/resource;
8. absolute Windows path;
9. parent path traversal;
10. duplicate object ID;
11. malformed object ID;
12. unknown semantic role;
13. semantic role on incompatible element;
14. missing root profile version;
15. missing figure ID;
16. wrong SVG/spec figure ID;
17. embedded Claim/Evidence/source-cursor metadata;
18. visible styling dependent on semantic metadata;
19. invalid `viewBox`;
20. NaN/Infinity;
21. invalid/negative dimensions;
22. malformed path;
23. malformed points;
24. forbidden transform;
25. lossy CJK mutation;
26. text converted to path when text semantics are required;
27. canonicalization changes z-order;
28. formatting-only canonicalization nondeterminism;
29. visible geometry mutation not changing canonical hash;
30. silent raster-fallback marker;
31. unregistered profile version;
32. stale semantic-role registry version;
33. fixture containing private basename/path;
34. Skill contract bypassing validator;
35. candidate-state source/schema/Skill mutation invalidates regression evidence.

Also include positive tests for all supported element families and mixed CJK/English.

## CP5-A19 — Status dimensions

At CP5-A end, report truthfully:

- Scientific SVG language status;
- static SVG validator status;
- semantic metadata governance status;
- CJK/static text status;
- resource-policy status;
- canonicalization/hash status;
- synthetic fixture status.

And keep later dimensions:

- native capability registry = `not_run`;
- static FigureCritic = `not_run` (CP5-C; CP5-A validator is not the final critic);
- production figure rendering = `not_run`;
- render critic = `not_run`;
- image-capable qualitative review = `not_run` or existing environment status, not CP5-A PASS;
- A01–A18 calibration = `not_run`;
- DrawingML compiler = `not_run`;
- template reconstruction = `not_run`;
- acceptance deck = `not_run`;
- native PowerPoint = `not_run`/`blocked_environment` only if actually checked;
- production Group Meeting ready = `false`.

Do not call CP5-A success `professor_visual_fidelity = pass`.

## Privacy

Private alias/source/render counters must remain `0 / 0 / 0`.

Do not resolve/open private PPTX exemplars.

Do not access ignored CP2 raw profiles.

Do not create private renders.

Repository/staged privacy scans remain required with the approved historical exception behavior.

## Required artifacts/report

Use repository naming conventions and create a CP5-A implementation report, recommended:

`thesis-deck-system/reports/PHASE_3_CP5_A_IMPLEMENTATION_REPORT.md`

Persist machine-readable CP5-A execution evidence and profile/role-registry/QA artifacts under the Phase 3 artifact area.

The report must include CP5-A1–CP5-A19 traceability.

## Validation

Before delivery run at minimum:

1. focused CP5-A tests;
2. CP1+CP2+CP3+CP4+CP5-A regression;
3. complete disposable-worktree regression;
4. CP4 consumed-input validation/hash checks;
5. all CP5-A JSON schemas + FormatChecker;
6. recursive schema closure;
7. Scientific SVG valid-fixture corpus;
8. Scientific SVG negative/mutation corpus;
9. CJK/static text tests;
10. resource/private-path tests;
11. canonicalization determinism/hash tests;
12. semantic metadata invisibility static QA;
13. Skill contract/registry audit;
14. candidate-state mutation audit;
15. independent tested/current candidate hash equality;
16. repository privacy scan;
17. staged privacy scan;
18. absolute private-path scan;
19. `git diff --check`;
20. exact scope check;
21. commit;
22. push;
23. remote SHA/tree/blob verification.

Do not fabricate unavailable execution evidence.

## Delivery format

Return:

- repository
- branch
- commit SHA
- pushed
- remote verification
- report path
- files added/modified/deleted
- focused/full regression pass/fail counts
- CP5-A1–CP5-A19 traceability
- Scientific SVG profile ID/version
- allowed element count/list
- forbidden element/security summary
- allowed semantic-role count/categories
- valid synthetic fixture count
- negative/mutation test count
- CJK test summary
- resource-reference policy summary
- canonicalization version/hash summary
- metadata invisibility QA summary
- technical Skills added/updated
- candidate-state component count/current hash/tested hash/equality
- owning QA count/status
- privacy scanner summary
- private alias/source/render counters
- all later checkpoint statuses
- known failures
- blocked conditions
- technical debt
- unresolved questions

Only after commit, push and remote verification write:

`READY_FOR_CP5_A_REVIEW: yes`

Then STOP.
