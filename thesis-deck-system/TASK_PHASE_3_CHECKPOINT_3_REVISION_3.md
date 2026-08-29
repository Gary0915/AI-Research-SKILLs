# Task — Phase 3 Checkpoint 3 Revision 3

## Status

Checkpoint 3 is **NOT APPROVED**.

Implement only CP3-D1–CP3-D5 from:

`thesis-deck-system/reviews/PHASE_3_CHECKPOINT_3_REVISION_3_REVIEW.md`

Do not start later Phase 3 production/calibration stages.

## CP3-D1 — Explicit candidate→slide binding

Replace the current positional-only candidate/measurement association with a resolver-safe sanitized binding contract.

Required behavior:

- persist one binding record for each of the 13 body candidates;
- each record must identify the bound `slide_id`, family, confidence, binding method/version, and structural binding evidence;
- local `O###` object IDs alone are insufficient identity because they recur across slides;
- candidates with no object evidence must still have a deterministic, validated binding;
- array reordering must never silently change family→slide assignment;
- either normalize independent input order through stable identities or fail closed on ambiguity;
- owning QA must validate all bindings, not merely family preferred-descriptor membership.

Required RED cases include:

1. reverse only measurements;
2. swap two result slides that both contain the same local object ID used by the candidates;
3. swap two insufficient candidates with no object IDs;
4. duplicate/ambiguous structural binding evidence;
5. missing bound slide;
6. 13 persisted bindings reconcile exactly with 13 candidates and 13 measurements.

## CP3-D2 — Real approved repository + staged privacy evidence

The owning privacy check must execute/consume the approved scanner result, not assert staged binding.

Required behavior:

- use the authoritative Phase 3 forbidden basename/config set;
- run repository scan;
- run staged-index scan;
- preserve exact approved legacy exception handling;
- persist scanner identity/version/config hash;
- persist repository finding count, staged finding count, and approved exception count;
- stale/missing staged scan evidence fails;
- `staged_scan_bound: true` may only be derived from actual matching scanner evidence.

Required RED cases include:

- forbidden basename only in staged content fails;
- forbidden basename only in repository content fails unless exact approved exception applies;
- empty/incorrect forbidden-basename configuration fails owning QA;
- fabricated staged-bound boolean without scanner evidence fails.

## CP3-D3 — Conservative category readiness + report consistency

Replace the current `fully_calibrated if recurring_count > 0` rule.

Define a controlled readiness model such as:

- `fully_calibrated`
- `partial_recurring`
- `provisional_only`
- `unresolved`

or an equivalent explicit enum.

Each category must define required sub-capabilities and evaluate them individually.

At minimum:

### shell_geometry

- canvas;
- content title geometry;
- formal shell role coverage;
- safe bounds status must remain visible and must prevent false completeness where required.

### typography_hierarchy

- authorized semantic role coverage;
- measured size hierarchy;
- weight/style consistency;
- unresolved roles visible.

### body_composition

- reusable family coverage;
- provisional/insufficient families visible.

### connector_arrow_grammar

- orientation coverage;
- directed/plain coverage;
- head/tail marker coverage;
- unresolved flip/directional semantics explicitly represented if not calibrated.

### line_style_grammar

- measured line-width grammar;
- evidence support state.

### color_emphasis_grammar

- actual usage-backed colors;
- generic role/emphasis support;
- no theme-palette-only promotion;
- incomplete semantic/emphasis coverage prevents false full calibration.

The report, `visual-style-profile.json`, QA facts, and delivery summary must use the exact same status values and counts.

Add an execution-derived report/artifact consistency check for the governed CP3 facts.

## CP3-D4 — Typography fail-closed role authority + role grammar

Remove `unknown` from professor-derived Exemplar-2 typography authority.

Allowed professor-derived authority remains:

- Primary 1: content/Hypothesis roles authorized by the design;
- Primary 3: cover/divider/footer/page-number/navigation roles;
- Exemplar 2: body/caption/annotation/panel-label.

Unknown role:

- audit-only / insufficient evidence;
- never professor-derived.

Resolve typography into reusable role-level grammar where evidence permits.

Persist at least:

- semantic role;
- script role;
- family/family alternatives;
- size range and robust center;
- weight/style consistency or alternatives;
- role confidence;
- supporting slide/container/measurement IDs;
- independent support count;
- evidence tier;
- resolver rule;
- status.

Do not count repeated runs from the same slide/container as independent recurrence.

Preserve raw sanitized observation references only as provenance/evidence.

Required RED cases include:

- explicit font with `role=unknown` cannot become professor-derived;
- duplicate same-slide runs do not upgrade evidence tier;
- two independent authorized containers can support recurrence;
- size/weight/style mutations are reflected in role grammar;
- cross-authority role mutation remains excluded.

## CP3-D5 — Composite candidate-state regression binding

Strengthen the disposable regression binding.

The candidate-state hash must include at minimum:

- four canonical CP2 input hashes;
- `phase3_checkpoint3.py` hash;
- `professor-template-resolved.schema.json` hash;
- `body-composition-profile.schema.json` hash;
- `professor-visual-grammar-v3.schema.json` hash;
- `visual-style-profile.schema.json` hash;
- `resolver-evidence.schema.json` hash;
- `checkpoint-3-qa.schema.json` hash.

Persist the component hash map and composite candidate hash.

A schema-only mutation after regression must invalidate the prior regression evidence.

A source-only mutation must invalidate it.

A CP2 input mutation must invalidate it.

The owning regression check must fail on any mismatch.

## Preserve

Do not regress:

- sanitized-only CP3 boundary;
- zero private alias/source/render attempts;
- family-conditioned body distributions;
- audit-only global body metrics;
- whole theme palettes reference-only;
- usage-backed color/connector/line evidence;
- material scientific colors unresolved;
- safe-bound honesty;
- shell support/topology/variants;
- Hypothesis/history insufficient without direct evidence;
- `partial_structural_calibration` top-level Governor status;
- disposable-worktree full regression;
- no A01–A18/PPTX/production Figure generation.

## Tests and validation

Run:

1. focused CP3 RED→GREEN suite;
2. CP1 + CP2 + CP3 suite;
3. complete regression in disposable worktree;
4. all four CP2 input schema validations;
5. all six CP3 output schema validations with `FormatChecker`;
6. recursive schema-closure audit;
7. explicit candidate-binding reconciliation audit;
8. privacy repository + staged scanner audit;
9. category-coverage/report consistency audit;
10. composite regression-state binding audit;
11. `git diff --check`;
12. remote SHA/tree/blob verification.

Do not run the complete regression in the active implementation worktree if it mutates Phase 1 artifacts.

## Delivery

Return:

- repository;
- branch;
- commit SHA;
- pushed yes/no;
- remote verification yes/no;
- report path;
- files added/modified/deleted;
- focused CP3 tests passed/failed;
- CP1+CP2+CP3 tests passed/failed;
- full disposable regression passed/failed;
- CP3-D1 binding summary and persisted binding count;
- CP3-D2 repository/staged privacy scanner summary;
- CP3-D3 category readiness table/status summary;
- CP3-D4 typography role-grammar summary;
- CP3-D5 candidate-state component/hash summary;
- owning QA count/status;
- private alias/source/render counters;
- private qualitative review status;
- acceptance deck status;
- archetype calibration status;
- native PowerPoint status;
- production Group Meeting readiness;
- known failures;
- technical debt;
- unresolved questions.

Only after commit, push, and remote verification write:

`READY_FOR_CHECKPOINT_3_REVIEW: yes`

Then stop.
