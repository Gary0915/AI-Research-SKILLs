# Task — Phase 3 Implementation Checkpoint 4

## Status

Checkpoint 3 is **APPROVED**.

Implement **Checkpoint 4 only: Scientific Figure Control Plane + Repo-local Skill Routing**.

Do not start visual production, archetype calibration, template reconstruction, benchmarks, acceptance deck, or Phase 4.

## Objective

Turn the approved Professor Visual Grammar and Visual Style Governor into a deterministic control plane that decides **which specialist Skill must handle each visual request, which renderer class is permitted, what evidence/provenance is required, and what must remain blocked/unresolved**.

Checkpoint 4 produces contracts, routing decisions, Skill specifications, and execution-owned QA only.

It must produce **no production figure asset, no SVG output, no PPTX, no private render, and no reconstructed template**.

## Canonical authorities

Scientific truth remains exclusively in the approved Phase 1–2 control plane:

`Ledger → materialized scientific state → Hypothesis/Research Block/Stage/Claim/Evidence/Decision/Action objects → Slide Specs`.

Professor visual influence comes only from approved CP3 artifacts:

- `professor-template-resolved.json`
- `body-composition-profile.json`
- `professor-visual-grammar-v3.json`
- `visual-style-profile.json`
- `resolver-evidence.json`
- `checkpoint-3-qa.json`

Private exemplars are **not** inputs to Checkpoint 4.

## CP4-1 — FigureProductionPlan contract

Implement/strengthen a closed, schema-backed `FigureProductionPlan`.

Each plan must contain at least:

- `figure_plan_id`;
- `visual_class`;
- `scientific_purpose`;
- `evidence_status`;
- `scientific_claim_support`;
- `source_refs`;
- `claim_refs`;
- `evidence_refs`;
- `hypothesis_layer_ref`;
- `research_block_refs`;
- `stage_ref` / cursor binding where required;
- `selected_specialist_skill`;
- `renderer_class`;
- `canonical_output_kind`;
- `source_asset_required`;
- `ai_generation_allowed`;
- `native_shape_eligibility`;
- `style_profile_ref`;
- `required_style_categories`;
- `required_qa`;
- `handoff_target`;
- `status`;
- provenance / resolver rule IDs.

Every nested object must be strongly typed with `additionalProperties:false`.

No scientific prose or claim may be invented by the router.

## CP4-2 — ScientificFigureSpec contract

Implement/strengthen a schema-backed `ScientificFigureSpec` sufficient for later specialist directors.

Required common fields include:

- figure/spec identity;
- figure type;
- scientific purpose;
- evidence status;
- source/claim/evidence refs;
- Hypothesis Layer / Research Block / Stage refs;
- selected director Skill;
- renderer;
- style profile reference;
- canvas;
- components;
- connections;
- annotations;
- labels;
- visual states;
- provenance;
- output targets;
- QA requirements.

Use discriminated specialist payloads where needed. Do not use a single giant untyped free-form object.

Checkpoint 4 may create specs for synthetic/canonical test fixtures but must not render them.

## CP4-3 — Deterministic scientific-figure-router

Implement a deterministic router with fail-closed classification.

Required routes:

### Quantitative measured result

`scientific-plot-director`

- source data/evidence required;
- reproducible plot route;
- generated imagery forbidden;
- canonical later output must be vector-capable.

### Real experiment / photo / microscopy / instrument output

`photo-annotation-director`

- immutable real source evidence required;
- source image cannot be replaced by generated imagery;
- annotations must be separate overlays.

### Literature figure

`literature-figure-director`

- extraction from real literature source required;
- citation/provenance required;
- AI recreation forbidden.

### Mechanism / causal concept / material-interface explanation

`mechanism-diagram-director`

- deterministic vector/native-plan route;
- unknown/uncertain edges remain explicit;
- cannot silently become experiment/fabrication evidence.

### Experimental setup / sample stack / measurement path

`experiment-schematic-director`

- instrumentation, inputs, outputs, measurement points, controls, variables;
- deterministic vector/native-plan route.

### Fabrication / preparation / curing / assembly chronology

`fabrication-process-director`

- chronology and material/state references preserved;
- known conditions preserved;
- missing conditions remain unknown;
- cannot be silently absorbed by mechanism or measurement schematic.

### Fishbone / research-map history

`fishbone-director`

- versioned Fishbone identity/revision/focus preserved;
- visual styling only;
- scientific branches/history remain canonical Phase 2 state.

### Control / Proposed or other fair comparison

`comparison-figure-director`

- comparable panel treatment;
- no unfair scale/area manipulation;
- source/evidence identity preserved.

### Image matrix / ordered multi-panel evidence

`image-matrix-director`

- panel order, identity, captions, scales, and source refs preserved;
- generated replacement forbidden for empirical evidence.

### Organic conceptual illustration only

`concept-illustration-director`

- only when `evidence_status=non_evidence`;
- `scientific_claim_support=forbidden`;
- cannot satisfy Observation or empirical Evidence bindings.

## CP4-4 — Renderer policy

Implement the approved hierarchy:

1. editable native PPTX-shape plan for genuinely simple primitives only;
2. deterministic SVG/vector for structured diagrams/flows/layers/mechanisms;
3. reproducible scientific plot;
4. real evidence source;
5. extracted literature figure;
6. generated concept substrate only for non-evidence organic concepts.

### SVG-first rule

Boxes, circles, arrows, layers, interfaces, process flows, mechanisms, Fishbone, and multi-edge scientific diagrams default to SVG/vector unless native-shape eligibility is explicitly established.

Do **not** invent the primitive-count threshold `N` if CP3 does not support it.

Until a measured eligibility threshold is available:

- native shape may be permitted only for a strict controlled trivial case with explicit reason;
- otherwise choose SVG/vector;
- persist `native_shape_eligibility = insufficient_evidence | eligible | ineligible` plus rule evidence.

No renderer may be selected only because it is convenient.

## CP4-5 — Visual Style Governor consumption policy

The router must consume category-specific CP3 readiness honestly.

Current partial/provisional grammar must not be treated as fully calibrated.

For each plan persist style usage policy such as:

- `professor_recurring_allowed`;
- `professor_provisional_allowed_with_flag`;
- `fallback_required`;
- `blocked_unresolved`.

At minimum evaluate:

- shell geometry when relevant;
- typography hierarchy;
- body composition;
- scientific figure metrics;
- connector/arrow grammar;
- line style;
- color/emphasis grammar.

Material semantic colors remain unresolved and must not be invented.

Directors must not hard-code arbitrary visual tokens when a governed token exists.

## CP4-6 — Observation / evidence boundary

Preserve the Scientific Method evidence boundary.

Generated or conceptual imagery must never satisfy:

- Observation empirical evidence;
- `observation_evidence_ref`;
- empirical `evidence_refs`;
- experimental image slots;
- quantitative result evidence;
- literature-figure evidence.

An auxiliary concept may coexist only as separately bound `non_evidence` support.

Add fail-closed tests for masquerading generated images.

## CP4-7 — Skill routing registry

Create or update the schema-versioned repo-local Skill routing registry.

Do not duplicate an existing Skill under a second name. Inspect current repo-local Skills first and extend them.

Required specialist identities:

- `thesis-deck-router`
- `scientific-figure-router`
- `fishbone-director`
- `mechanism-diagram-director`
- `experiment-schematic-director`
- `fabrication-process-director`
- `scientific-plot-director`
- `photo-annotation-director`
- `literature-figure-director`
- `comparison-figure-director`
- `image-matrix-director`
- `concept-illustration-director`
- `vector-figure-builder`
- `visual-style-governor`
- `figure-critic`
- `layout-director`
- `provenance-qa`

Every repo-local Skill specification must state at least:

- trigger;
- do-not-trigger conditions;
- inputs;
- required context;
- workflow;
- allowed downstream Skills/tools;
- forbidden actions;
- output contract;
- provenance behavior;
- failure modes;
- blocked states;
- handoff target;
- QA owner.

Skills remain repository-local and unregistered.

## CP4-8 — Handoff and no-bypass rules

Persist an explicit handoff graph.

Required invariant:

`scientific state → FigureProductionPlan → specialist director → future renderer/output manifest → FigureCritic → APPROVED_FIGURE → Layout Director`.

Checkpoint 4 stops before rendering, but the contracts must enforce the later gate.

Layout Director must reject:

- raw Figure Specs;
- unreviewed generated images;
- unapproved SVG/native plans;
- arbitrary scientific drawing instructions;
- assets without provenance.

There must be no `router → layout` bypass for scientific figures.

## CP4-9 — Archetype routing matrix, not calibration

Persist the required visual route for A01–A18 without changing archetype geometry.

Use the approved Phase 3 plan mapping.

Examples:

- A03 → Fishbone Director;
- A04 → real empirical route; concept only auxiliary non-evidence;
- A05 → literature extraction + mechanism;
- A06 → mechanism or fabrication-process according to scientific role;
- A07 → real photo + experiment schematic, with fabrication process when preparation transitions are shown;
- A08 → comparison;
- A09 → experiment schematic, fabrication separately when applicable;
- A10/A11/A13 → plot / result routes;
- A12 → image matrix;
- A16 → deterministic transition diagram.

This is a routing matrix only.

Do **not** calibrate A01–A18 layout geometry in CP4.

## CP4-10 — Execution-owned QA

Produce a Checkpoint 4 execution-evidence artifact and final QA.

No literal PASS fields.

Owning checks must include at least:

- canonical CP3 input schema/status/hash validation;
- no private source access;
- routing determinism;
- visual-class coverage;
- specialist exclusivity where required;
- source/evidence requirements;
- Observation empirical boundary;
- AI-generation prohibition for empirical/literature/plot classes;
- fabrication/mechanism/measurement separation;
- Fishbone identity/history preservation;
- SVG-first policy;
- native-shape fail-closed threshold behavior;
- Visual Style Governor readiness consumption;
- material-semantic-color non-invention;
- Skill registry completeness;
- handoff/no-bypass graph;
- A01–A18 routing-matrix completeness;
- schema closure;
- deterministic mutation tests;
- repository/staged privacy scan;
- full regression bound to candidate state.

## CP4-11 — Candidate-state regression binding

Bind disposable regression evidence to:

- all canonical CP3 input artifacts consumed by CP4;
- CP4 router/control-plane source files;
- all CP4 schemas/contracts;
- repo-local Skill routing registry/spec hashes that affect execution.

Persist component hashes and composite hash.

Source/schema/routing-registry mutation must invalidate old regression evidence.

## CP4-12 — Honest status model

Report independently:

- CP3 Professor Visual Grammar input status;
- figure control-plane status;
- figure routing coverage;
- Skill registry coverage;
- style-governor consumption status;
- empirical-evidence boundary status;
- production figure rendering: `not_run`;
- FigureCritic visual acceptance: `not_run`;
- A01–A18 calibration: `not_run`;
- template reconstruction: `not_run`;
- acceptance deck: `not_run`;
- private qualitative review: `blocked_visual_review`;
- native PowerPoint: `not_run`;
- production Group Meeting readiness: `false`.

Do not call routing-contract completion a visual-fidelity PASS.

## TDD required negative cases

At minimum prove:

1. quantitative evidence cannot route to concept generation;
2. real photo cannot be replaced by generated substrate;
3. literature figure cannot route to AI recreation;
4. generated concept cannot satisfy Observation evidence;
5. mechanism cannot silently absorb fabrication chronology;
6. experiment schematic cannot silently absorb fabrication chronology;
7. fabrication process with unknown condition preserves unknown;
8. Fishbone route preserves revision/focus/history refs;
9. Exemplar-2 body grammar cannot become shell authority;
10. unresolved material color cannot be invented;
11. unavailable native-shape threshold cannot produce an unrestricted native route;
12. structured multi-edge diagram defaults SVG;
13. layout cannot accept an unapproved figure;
14. router output is independent of source-list order;
15. missing provenance ref fails;
16. A01–A18 routing matrix has no missing archetype;
17. unexpected Skill route fails closed;
18. changed Skill registry invalidates regression evidence.

## Required artifacts

Produce schema-backed artifacts equivalent to:

- `figure-production-plans.json` or deterministic synthetic acceptance set;
- `skill-routing.yaml` / schema-versioned routing registry;
- `archetype-figure-routing.json`;
- `checkpoint-4-execution-evidence.json`;
- `checkpoint-4-qa.json`.

Use only sanitized/canonical repository data. No private paths or content.

## Required report

Create:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md`

Include CP4-1 through CP4-12 traceability.

## Validation

Run:

1. focused CP4 RED→GREEN tests;
2. CP1 + CP2 + CP3 + CP4 focused regression;
3. full package regression in a disposable worktree;
4. all consumed CP3 input schema/status/hash checks;
5. all CP4 schemas with Draft 2020-12 `FormatChecker`;
6. recursive schema-closure audit;
7. routing determinism/mutation suite;
8. empirical-evidence/AI-prohibition suite;
9. Skill-registry and handoff-graph audit;
10. A01–A18 route-coverage audit;
11. repository + staged privacy scan;
12. `git diff --check`;
13. remote SHA/tree/blob verification.

Do not run full regression in the active implementation worktree if it dirties generated Phase 1 artifacts.

## Not authorized

Do not:

- render/generate a production scientific figure;
- create production SVG/PDF/PNG figure assets;
- call a concept-image generator;
- create private exemplar renders;
- calibrate A01–A18 geometry;
- reconstruct the professor template;
- create a PPTX;
- run reconstruction benchmarks;
- build the acceptance deck;
- begin Phase 4;
- publicly/globally register Skills.

## Delivery

Return:

- repository;
- branch;
- commit SHA;
- pushed yes/no;
- remote verification yes/no;
- report path;
- files added/modified/deleted;
- focused CP4 tests passed/failed;
- CP1+CP2+CP3+CP4 tests passed/failed;
- full disposable regression passed/failed;
- CP4-1–CP4-12 traceability;
- FigureProductionPlan routing summary;
- specialist Skill registry summary;
- A01–A18 routing coverage summary;
- evidence/AI boundary summary;
- SVG/native routing policy summary;
- Visual Style Governor consumption summary;
- owning QA count/status;
- private alias/source/render counters;
- production figure rendering status;
- FigureCritic status;
- archetype calibration status;
- template reconstruction status;
- acceptance deck status;
- native PowerPoint status;
- production Group Meeting readiness;
- known failures;
- technical debt;
- unresolved questions.

Only after commit, push, and remote verification write:

`READY_FOR_CHECKPOINT_4_REVIEW: yes`

Then stop.
