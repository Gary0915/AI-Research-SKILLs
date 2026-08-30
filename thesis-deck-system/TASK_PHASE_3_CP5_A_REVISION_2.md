# TASK — Phase 3 CP5-A Revision 2

## Authorization

Implement **CP5-A Revision 2 only**. Do not begin CP5-B or any later checkpoint.

Reviewed implementation commit: `e8a8b6da76aa33193b832a83c0263ac6e3e4c726`.

Authoritative review: `reviews/PHASE_3_CP5_A_REVISION_2_REVIEW.md`.

## Required corrections

Implement all:

- CP5A-C1 — complete profile/code language authority;
- CP5A-C2 — consuming exact path/points/transform lexical grammar;
- CP5A-C3 — schema-valid ScientificFigureSpec authoring handoff;
- CP5A-C4 — execution-owned private-access evidence;
- CP5A-C5 — complete execution-owned owning-check coverage;
- CP5A-C6 — exact and resolved local SVG reference semantics.

## CP5A-C1 — Complete profile/code authority

The persisted Scientific SVG profile is the authoritative declared language contract.

Every language-affecting profile field must either:

1. directly control execution behavior; or
2. be checked against a registered implementation capability and fail validator construction when unsupported/mismatched.

At minimum reconcile:

- `root_contract`;
- `element_attribute_contract`;
- `namespace_policy`;
- `semantic_attribute_placement`;
- `grammar_bindings`;
- `id_policy`;
- `coordinate_policy`;
- `transform_policy`;
- `text_policy` where executable;
- `resource_policy`;
- `style_policy` / forbidden executable features;
- canonicalization version/rules where executable.

Do not allow arbitrary per-element attribute strings to introduce an uncontrolled attribute without schema or compatibility rejection.

Required mutations include:

- change object-ID pattern and prove behavior changes or compatibility fails;
- remove `rotate` from allowed transforms and prove rotate no longer silently passes;
- remove synthetic data URI mode and prove it cannot silently remain allowed;
- introduce an approved attribute namespace unsupported by code and prove construction fails closed;
- mutate root required attributes and prove behavior changes or compatibility fails;
- add an uncontrolled attribute such as `style` to a profile contract and prove profile/schema/compatibility rejection.

## CP5A-C2 — Exact consuming geometry grammar

Replace regex-search/token-skipping behavior with a tokenizer/parser that consumes the entire controlled grammar.

### Path

Require:

- first drawable command is `M` or `m`;
- complete lexical consumption;
- no skipped characters;
- exact command parameter groups;
- valid repeated groups;
- finite numbers;
- valid closepath behavior;
- current arc rules and exact flags if `A/a` remains supported.

Reject at minimum:

- `L 0 0` as the first command;
- incomplete exponent forms such as a numeric token ending in `e`/`E`;
- adjacent malformed numeric lexemes;
- unmatched/excess groups;
- invalid arc radii/flags/counts if arcs remain supported.

### Points

Require exact separators and full lexical consumption.

Reject repeated/empty separators such as double commas rather than collapsing them.

Maintain:

- polyline >= 2 pairs;
- polygon >= 3 pairs;
- finite values.

### Transform

Require exact full-string consumption and exact function arity.

Reject malformed repeated separators and token gaps.

Supported arity remains explicitly controlled by the profile/registered grammar.

## CP5A-C3 — Validate ScientificFigureSpec at authoring handoff

Before `author_svg_for_spec()` or equivalent can return canonical Scientific SVG:

- validate the supplied FigureSpec against the approved CP4 `scientific-figure-spec` schema;
- run the registered cross-field route/discriminator validation;
- then bind figure ID / visual class and validate SVG.

A fake dict containing only `figure_id` and `visual_class` must fail.

Add negative tests for:

- missing required FigureSpec fields;
- invalid route discriminator;
- unsupported source/evidence combination;
- invalid schema version;
- SVG otherwise valid but supplied Spec invalid.

## CP5A-C4 — Execution-owned private-access evidence

A caller-provided zero-count dictionary is not sufficient evidence.

Bind the final CP5-A private-access counters to an instrumented execution/session record or another canonical sealed evidence type that records guarded entrypoint attempts.

Requirements:

- counters derive from the execution object;
- manual/spoofed dictionaries cannot be promoted to canonical PASS;
- missing record fails;
- unsealed/unexecuted record fails;
- any nonzero alias/source/render attempt fails;
- record identity/hash is persisted in checkpoint evidence where appropriate;
- candidate state binds any source/schema used by the counter mechanism.

Reuse an existing reviewed checkpoint execution-evidence mechanism if appropriate instead of inventing a weaker duplicate.

## CP5A-C5 — Complete owning-check evidence

Persist explicit execution-derived owning checks for at least:

- profile/code authority across executable policy fields;
- namespace policy;
- element/attribute allowlist;
- semantic role registry;
- visual-class incompatibility rejection;
- role child-policy rejection;
- addressability rejection;
- path/points/transform exact grammar;
- CJK/editable text;
- significant inter-`tspan` whitespace;
- resource/path policy;
- local-reference resolution;
- canonicalization determinism;
- metadata invisibility;
- synthetic corpus + exact fixture/spec bindings;
- full CP4 FigureProductionPlan collection validation;
- full CP4 ScientificFigureSpec collection validation;
- canonical authoring handoff rejects invalid FigureSpec;
- repository/staged privacy;
- sealed private-access execution evidence;
- candidate-bound disposable regression.

`checkpoint-5a-qa.json` must remain projected from owning checks. No literal PASS dimensions.

## CP5A-C6 — Exact local reference grammar and resolution

For `marker-start`, `marker-end`, and `clip-path`:

- accept only exact `url(#<object-id>)` syntax;
- reject prefix matches with trailing junk;
- referenced ID must exist in the same canonical SVG;
- marker references must target a `marker` element;
- clip-path references must target a `clipPath` element.

For any direct local `href` mode that remains allowed:

- define exact syntax in the profile/grammar;
- resolve same-document IDs when applicable;
- reject dangling references.

Bundle-relative and synthetic-data image resources remain governed by the existing safe resource policy.

Add negative tests for:

- `url(#obj-x)junk`;
- missing marker target;
- marker reference targeting a non-marker;
- missing clip target;
- clip reference targeting a non-clipPath.

## Preserve

Do not regress:

- Scientific SVG = visual authoring IR only;
- no Ledger/Claim/Evidence provenance in SVG;
- minimal rendering-neutral semantic metadata;
- editable UTF-8 CJK text;
- child/source order and z-order preservation;
- no private exemplar/source/render access;
- no production figure generation;
- no PPTX;
- CP5-B through CP5-I remain `not_run`;
- production Group Meeting ready remains `false`.

## Candidate state and regression

Candidate state must include every changed execution-affecting component, including any reused execution-evidence mechanism and its tests/schema.

Run:

- focused CP5-A Revision 2 tests;
- full CP1+CP2+CP3+CP4+CP5-A regression;
- full disposable-worktree regression;
- all CP5-A schemas + FormatChecker;
- recursive schema closure;
- profile/code compatibility mutation suite;
- exact geometry tokenizer/parser mutation suite;
- FigureSpec authoring-handoff suite;
- private execution-evidence spoofing suite;
- owning-check/status projection consistency audit;
- local reference grammar/resolution suite;
- CJK/significant-whitespace suite;
- full CP4 consumed collection validation;
- candidate-state mutation audit;
- independently captured tested/current candidate hash equality;
- repository privacy scan;
- staged privacy scan;
- absolute private-path scan;
- `git diff --check`;
- exact scope audit;
- remote SHA/tree/blob verification.

## Report

Update `reports/PHASE_3_CP5_A_IMPLEMENTATION_REPORT.md` with explicit CP5A-C1 through CP5A-C6 traceability and final evidence.

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
CP5A-C1–C6 traceability:
profile/code authority summary:
exact path/points/transform grammar summary:
ScientificFigureSpec handoff validation summary:
private-access execution evidence summary:
owning QA count/status:
local reference validation summary:
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
