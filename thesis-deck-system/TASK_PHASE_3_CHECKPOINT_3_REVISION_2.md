# TASK — Phase 3 Checkpoint 3 Revision 2

## Status

Authorized correction only after review of commit:

`6498c60506ab04c7219006cdc3138c1ee20e71ed`

Read completely before implementation:

1. `thesis-deck-system/reviews/PHASE_3_CHECKPOINT_3_REVISION_2_REVIEW.md`
2. `thesis-deck-system/TASK_PHASE_3_CHECKPOINT_3_REVISION.md`
3. `thesis-deck-system/TASK_PHASE_3_IMPLEMENTATION_CHECKPOINT_3.md`
4. `thesis-deck-system/designs/PHASE_3_VISUAL_FIDELITY_DESIGN.md`
5. `thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`
6. `thesis-deck-system/REVIEW_PROTOCOL.md`

This revision is limited to **CP3-C1–CP3-C5**.

Checkpoint 3 remains sanitized-domain-only. Production private alias resolution, private PPTX opening/hashing, raw-profile access, private rendering, screenshot review, or private text/media access is forbidden.

---

# CP3-C1 — Authority-safe typography grammar

Implement the fixed authority matrix for typography before any observation becomes professor-derived.

Required authority:

- `P3-TEMPLATE-PRIMARY-1`: content-page / Hypothesis-history typography roles only;
- `P3-TEMPLATE-PRIMARY-3`: cover / divider / footer / page-number / navigation typography roles only;
- `P3-LAYOUT-EXEMPLAR-2`: body / caption / annotation / panel-label scientific-body typography evidence only.

Do not accept an explicit font merely because it exists in an authorized descriptor.

Preserve, where CP2 supplies safe structural evidence:

- family;
- script role;
- size_pt;
- weight;
- style;
- role;
- role confidence;
- source scope;
- supporting IDs;
- evidence state;
- evidence tier;
- resolver rule ID.

Do not emit `size_pt: null` when measured size is available.

When repeated compatible observations support one role, produce a role-level distribution / controlled preferred value with range and evidence tier rather than treating every run as an independent professor preference.

Unknown / unspecified / inherited-unresolved remain excluded.

Fallback rendering fonts remain implementation fallback only.

Required RED tests include:

1. Primary-1 footer typography cannot become active footer preference when Primary-3 is authoritative.
2. Primary-3 content typography cannot replace Primary-1 content typography.
3. Exemplar-2 body typography cannot become formal-shell typography.
4. measured size/weight/style survive into resolved grammar/governor.
5. unknown/inherited typography remains excluded.
6. role-level recurrence cannot be inferred from duplicate records inside one source container only.

---

# CP3-C2 — Usage-backed color / line / connector grammar

Do not promote entire active Office theme palettes.

However, do not discard actual measured style usage.

Consume sanitized CP2 structural evidence from authorized fields such as:

- shell `style_roles`;
- body measurement `style_roles`;
- object style evidence;
- connector records;
- geometry-eligible line/connector objects.

Resolve generic structural style grammar only when directly supported.

## Colors

Eligible evidence may include:

- direct RGB actually used by a measured shell/body style;
- theme-role color actually referenced by a measured style with a resolvable bound active theme;
- neutral/accent/emphasis role recurrence.

Persist:

- semantic visual role;
- resolved/direct RGB when safe;
- source profile/scope;
- supporting IDs;
- support count;
- evidence tier;
- authority family;
- resolver rule.

Do not infer hydrogel/electrode/heater/sensor/interface semantics.

## Lines / connectors

Where sufficient sanitized evidence exists, resolve generic distributions/classes for:

- line width;
- connector orientation;
- directed/plain;
- head marker;
- tail marker;
- common marker/direction class;
- flip-normalized directional form where defensible.

Rotation-ineligible records must remain excluded.

Do not invent a connector class when support is insufficient.

## Emphasis

A red/emphasis token may be professor-derived only from actual measured use and proper source authority. Theme palette existence alone is insufficient.

Required RED tests include:

1. referenced theme palette alone does not create color preference;
2. measured direct shell color may create usage-backed style evidence;
3. unused theme accent does not become active style;
4. measured directed triangle-tail connector contributes to generic connector grammar;
5. connector marker absence does not become arrow preference;
6. rotated/geometry-ineligible connector is excluded;
7. Exemplar-2 style cannot become formal-shell palette authority;
8. no material-specific semantic color is inferred.

---

# CP3-C3 — Resolver-safe body binding and representative selection

Current parallel arrays must not silently misbind candidate families and measurements.

Implement an explicit normalized binding layer.

Each resolved body evidence record must have a stable `source_descriptor_id` / slide ID and the family classification bound to that same record.

If the CP2 representation requires parallel arrays, validate their alignment through a fail-closed invariant and persist the normalized binding before aggregation.

Independent source reordering must either:

- produce the same normalized mapping; or
- fail explicitly.

It must never silently assign one slide's measurements to another slide's family.

## Preferred representative

Replace raw unscaled sum-of-absolute-deviations selection.

Use a documented deterministic method such as:

- pairwise medoid over normalized comparable metrics; or
- normalized robust-distance-to-center with explicit missing-data penalty.

Requirements:

- heterogeneous metric scales must not dominate accidentally;
- missing metrics must not reward a candidate;
- distance is calculated only over documented comparable dimensions;
- tie break is deterministic;
- persist distance method/version;
- persist comparable metric count;
- persist preferred descriptor ID;
- persist outlier method/version and outlier IDs.

Required RED tests include:

1. candidate-array reorder cannot silently relabel slides;
2. measurement-array reorder cannot silently relabel slides;
3. same logical input under allowed order changes gives same result;
4. descriptor with many missing metrics cannot win merely because fewer distances were summed;
5. changing metric units/scales under normalized transformation does not arbitrarily change medoid;
6. tie break is deterministic;
7. preferred descriptor is always a supporting descriptor.

---

# CP3-C4 — Complete owning QA and execution evidence

Extend persisted execution-derived QA. Do not rely only on unit-test existence.

Owning QA must include actual checks/evidence for at least:

- CP2 input schema validation;
- CP2 aggregate QA status;
- canonical input identity/profile closure;
- computed input hashes;
- no private access;
- fixed exemplar authority;
- shell contamination prevention;
- conflict completeness;
- hard-conflict behavior evidence;
- evidence tiers;
- recurring support rule;
- theme metadata vs style-token separation;
- typography authority and unresolved exclusion;
- supplemental/reference-only font exclusion;
- family binding integrity;
- family distribution/representative reconciliation;
- unavailable metric preservation;
- connector/color semantic non-invention;
- Visual Style Governor provenance and category coverage;
- fallback separation;
- resolver determinism;
- nested schema closure;
- approved repository/staged privacy scan result;
- disposable-worktree regression result bound to the tested candidate state.

`CP3-PRIVACY-SCAN` must consume/bind the approved repository/staged privacy scanner result; do not replace that with a weaker substring-only scan over only some artifacts.

The full regression execution evidence must record at least:

- candidate commit/tree/patch identity or equivalent deterministic candidate hash;
- test command/class;
- passed/failed counts;
- disposable-worktree status.

A failed owning check must make aggregate status fail.

---

# CP3-C5 — Coverage dimensions for later archetype/Figure routing

Visual Style Governor coverage must become decision-useful.

At minimum separate coverage for:

- shell geometry;
- typography hierarchy;
- body composition;
- scientific figure metric grammar;
- connector/arrow grammar;
- line/style grammar;
- color/emphasis grammar;
- unresolved/fallback/reference-only evidence.

For each category report equivalent counts/status for:

- recurring professor-derived;
- provisional professor-derived;
- fallback;
- unresolved;
- reference-only metadata;
- reusable coverage status.

A category with only provisional evidence must not be represented as fully calibrated.

A category with no usage-backed style evidence remains unresolved even if an active theme exists.

Preserve global summary counts only as convenience; they may not replace category coverage.

---

# Schemas

Update CP3 schemas for all new structures.

All nested core objects must remain typed and fail closed with `additionalProperties: false`.

Add mutation tests for every new nested contract.

---

# Preserve all accepted behavior

Do not regress:

- sanitized-only CP3 execution;
- zero production private alias/source/render attempts;
- asymmetric exemplar authority;
- safe-content-bounds honesty;
- CP2 shell support/topology retention;
- body-family-local ranges;
- audit-only global body statistics;
- active theme metadata separated from style tokens;
- material semantic colors unresolved;
- no color blending;
- unavailable metrics remain unavailable;
- source-order deterministic shell resolution;
- incompatible canvas hard block;
- unresolved font exclusion;
- unreferenced theme exclusion;
- partial structural governor status;
- no A01–A18;
- no PPTX/template reconstruction;
- no production Figure Skills;
- no benchmark/acceptance deck;
- production readiness false;
- disposable-worktree full regression;
- regression artifact cleanup discipline.

---

# Validation

Run at minimum:

1. focused CP3 Revision-2 tests;
2. CP1 + CP2 + CP3 tests;
3. complete Phase 1–2 + CP1 + CP2 + CP3 regression in disposable worktree;
4. four canonical CP2 input schema validations;
5. all CP3 artifact schemas + FormatChecker;
6. recursive schema closure audit;
7. typography authority/fidelity QA;
8. usage-backed color/line/connector QA;
9. family binding and medoid mutation QA;
10. execution-owned determinism QA;
11. governor category-coverage QA;
12. repository/staged privacy scan;
13. `git diff --check`;
14. remote branch/artifact/report verification.

Do not run the complete regression in the active implementation worktree if it dirties Phase 1 artifacts.

---

# Required report

Update:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_3_IMPLEMENTATION_REPORT.md`

Add explicit traceability for:

- CP3-C1
- CP3-C2
- CP3-C3
- CP3-C4
- CP3-C5

Report actual counts for:

- typography tokens by authority/role/tier;
- usage-backed color roles;
- connector classes and support;
- line-width distributions;
- body binding records;
- representative method and family medoids;
- owning checks;
- governor category coverage.

Continue to report:

- private qualitative visual review = `blocked_visual_review`;
- acceptance deck visual fidelity = `not_run`;
- archetype calibration coverage = `not_run`;
- native PowerPoint acceptance = `not_run`;
- production Group Meeting ready = `false`.

---

# Not authorized

Do NOT start:

- A01–A18 production calibration;
- reconstructed professor template;
- PPTX output;
- production Figure Skills/renderers;
- production SVG figures;
- reconstruction benchmarks;
- acceptance deck;
- Phase 4;
- public/global Skill registration.

---

# Delivery

Return:

- repository;
- branch;
- commit SHA;
- pushed status;
- remote verification;
- report path;
- files added/modified/deleted;
- focused CP3 test count;
- CP1+CP2+CP3 count;
- full regression count;
- CP3-C1–C5 traceability;
- typography authority/fidelity summary;
- usage-backed color/connector/line summary;
- family binding/representative summary;
- owning QA count/summary;
- category coverage summary;
- private-access counters;
- blocked/not-run status dimensions;
- known failures;
- technical debt;
- unresolved questions.

Only after commit, push, and remote verification write:

`READY_FOR_CHECKPOINT_3_REVIEW: yes`

Then STOP.
