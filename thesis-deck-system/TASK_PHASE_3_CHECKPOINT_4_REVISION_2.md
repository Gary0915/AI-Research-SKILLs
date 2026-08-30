# Task — Phase 3 Checkpoint 4 Revision 2

## Status

Checkpoint 4 remains **NOT APPROVED**.

Reviewed implementation commit:

`76c7343042dd36b6701df9c92c2d5ddd5e410161`

Implement only the corrections in this task.

Do not begin production figure rendering, A01–A18 calibration, template reconstruction, benchmarks, acceptance deck, PPTX generation, Phase 4, or public/global Skill registration.

## Authorized corrections

Implement exactly:

- CP4-C1 — fail-closed CP3 style-profile consumption;
- CP4-C2 — route-consistent discriminated Plan/Spec contracts;
- CP4-C3 — schema-backed closed FigureRoutingRequest;
- CP4-C4 — contract-compatible no-bypass handoff graph;
- CP4-C5 — independently candidate-bound disposable regression evidence;
- CP4-C6 — evidence-rich owning QA and report/artifact consistency.

---

## CP4-C1 — Fail-closed Visual Style Governor consumption

Remove any production fallback equivalent to:

`style_profile = {... VSP003 ...}`

when no actual CP3 style artifact was supplied.

Production routing must require the consumed approved `visual-style-profile.json` object.

Validate at least:

- schema validity;
- `status = partial_structural_calibration` or the approved successor state;
- exact `style_profile_id`;
- category coverage structure;
- request style ref, if supplied, equals consumed profile identity.

Missing/stale/mismatched profile must fail closed.

A synthetic unit fixture may exist only as an explicitly test-labelled fixture and must never be a silent production default.

For each route persist route-specific style requirements with:

- `category_id`;
- CP3 readiness status;
- consumption mode;
- source profile ID;
- evidence/provenance reference or rule ID;
- blocking state.

Material-semantic colors remain unresolved and may not be invented.

### Required tests

1. missing style profile → FAIL;
2. stale VSP ID → FAIL;
3. malformed profile → FAIL;
4. route categories differ where scientifically appropriate;
5. plan/spec style refs equal the consumed CP3 profile ID;
6. material semantic colors remain blocked.

---

## CP4-C2 — Discriminated route-consistent contracts

The v4 control plane must make invalid cross-route combinations impossible or explicitly fail validation.

Bind, for each visual class:

- visual class;
- Figure type;
- specialist Skill;
- renderer class;
- canonical output kind;
- evidence status rules;
- source/evidence requirements;
- AI-generation rule.

Required canonical mappings include:

- quantitative result → scientific plot → scientific-plot-director → reproducible plot → vector-capable output;
- real experiment photo → real photo → photo-annotation-director → source-preserving overlay;
- literature figure → literature figure → literature-figure-director → source extraction/overlay;
- mechanism → mechanism diagram → mechanism-diagram-director → deterministic vector;
- experiment setup → experiment schematic → experiment-schematic-director → deterministic vector;
- fabrication → fabrication-process diagram → fabrication-process-director → deterministic vector;
- Fishbone → Fishbone diagram → fishbone-director → deterministic vector;
- fair comparison → comparison diagram → comparison-figure-director;
- image matrix → image-matrix figure → image-matrix-director → source evidence matrix;
- organic concept → concept illustration → concept-illustration-director → generated non-evidence only.

Use discriminated JSON Schema variants, an equivalent registered cross-field validator, or both.

A v4 object that swaps only one of these discriminator fields must fail.

### Required mutation tests

For each of the 10 visual classes mutate at least:

- wrong figure type;
- wrong specialist;
- wrong renderer;
- wrong output kind;
- incompatible evidence status/AI policy where applicable.

No mismatch may remain schema-valid/control-plane-valid.

---

## CP4-C3 — Schema-backed FigureRoutingRequest

Create and register a closed v4 `FigureRoutingRequest` contract or equivalent named schema.

It must use `additionalProperties:false` recursively for controlled objects.

Strongly type:

- figure plan ID;
- visual class;
- scientific purpose;
- evidence status;
- scientific claim support;
- source/claim/evidence refs;
- Layer/Block/Stage/cursor refs;
- requested archetype;
- provenance rule IDs;
- AI-generation request;
- style-profile ref;
- empirical slot bindings;
- fabrication-step payload;
- Fishbone binding;
- any structured/native eligibility hint that remains authorized.

Unknown top-level or nested fields must fail rather than being silently dropped.

For organic concepts, all empirical/Observation slots must be absent or empty.

Explicitly cover:

- `observation_evidence_ref`;
- experimental evidence slots;
- quantitative result evidence slots;
- literature figure evidence slots;
- controlled equivalent fields if renamed.

### Required tests

- unknown top-level field → FAIL;
- unknown fabrication-step field → FAIL;
- unknown Fishbone-binding field → FAIL;
- concept + Observation binding → FAIL;
- concept + experimental slot → FAIL;
- concept + quantitative slot → FAIL;
- concept + literature slot → FAIL;
- malformed scientific binding → FAIL;
- valid non-evidence concept → PASS.

Add the new request schema to:

- schema registry;
- recursive closure audit;
- candidate-state component hashes.

---

## CP4-C4 — Actual contract-compatible no-bypass graph

Normalize the output-manifest contract identity.

Do not mix identifiers such as:

- `future_renderer_output_manifest`;
- `future_output_manifest`;

unless one is an explicitly typed node whose conversion is declared and validated.

Represent every non-Skill graph node as a typed contract node, or introduce an authorized repo-local stage only if necessary. Do not add a duplicate scientific director Skill.

Audit all relevant edges:

- user route → top-level router;
- router → specialist;
- specialist → renderer/vector/source-preserving stage;
- renderer/output stage → canonical FigureOutputManifest;
- FigureOutputManifest → FigureCritic;
- FigureCritic → APPROVED_FIGURE;
- APPROVED_FIGURE → Layout Director.

For each edge prove:

- downstream node exists;
- producer output contract matches consumer input contract;
- handoff target matches allowed downstream;
- no scientific route reaches Layout before approval;
- no raw FigureSpec reaches FigureCritic;
- no raw spec is interpreted by Layout.

The graph validator must reject:

- unknown downstream node;
- dangling handoff target;
- producer/consumer contract mismatch;
- direct specialist → FigureCritic when only a spec exists;
- direct router/specialist → Layout;
- output-manifest name mismatch.

Persist graph audit evidence with node/edge counts and mismatch counts.

---

## CP4-C5 — Independently candidate-bound disposable regression

The tested candidate hash must come from the disposable regression execution, not be assigned during finalization.

### Required sequence

1. compute candidate component hashes before running the disposable suite;
2. compute the composite candidate-state hash;
3. create/run the disposable worktree against exactly that candidate state;
4. record the tested candidate hash from that execution;
5. pass the independent regression record into CP4 artifact finalization;
6. recompute current candidate hash during finalization;
7. require:

`tested_candidate_hash == current_candidate_hash`

before regression PASS.

The regression evidence must contain at least:

- `regression_candidate_state_hash`;
- `disposable_worktree`;
- suite/command identity;
- tests passed;
- tests failed;
- execution/session identifier where available;
- regression status.

Do not overwrite the supplied tested hash with the current hash.

### Candidate components

Bind all execution-affecting inputs, including at minimum:

- six consumed CP3 artifacts;
- `phase3_checkpoint4.py`;
- `contracts.py`;
- all CP4 schemas including the new FigureRoutingRequest schema;
- `skill-routing.yaml`;
- all 17 repo-local `SKILL.md` files;
- any new graph-contract file/schema introduced by CP4-C4.

### Required mutation tests

Old regression evidence must fail after mutation of any one of:

- CP3 input;
- router source;
- `contracts.py`;
- schema;
- routing YAML;
- any one Skill contract;
- graph-contract definition.

---

## CP4-C6 — Evidence-rich owning QA and report consistency

Do not use only opaque `{result: true}` facts where the proof has a measurable identity/count/hash.

Owning QA must persist real evidence for at least:

### CP3 inputs

- expected input count = 6;
- actual validated count;
- schema IDs;
- input hashes;
- CP3 aggregate QA status.

### Style

- consumed style profile ID;
- style status;
- route-category readiness counts;
- unresolved material color state.

### Visual classes

- supported class count = 10;
- exercised class count;
- missing class IDs;
- per-class route/spec consistency status.

### Skill registry / graph

- expected Skill count = 17;
- actual Skill count;
- Skill IDs;
- node count;
- edge count;
- dangling edge count;
- contract mismatch count;
- pre-critic Layout bypass count.

### Archetypes

- expected = 18;
- actual = 18;
- missing IDs;
- non-`not_run` geometry count = 0.

### Schema closure

- schema count;
- closure failure count;
- failed schema IDs.

### Privacy

Use the authoritative repository/staged privacy configuration and scanner.

Persist:

- scanner ID/version;
- configuration hash;
- repository scan executed;
- staged scan executed;
- repository findings;
- staged findings;
- approved historical exception count.

The reviewed historical exception count must not silently change. If repository/config state legitimately changed, document the exact sanitized reason/evidence in the report.

### Regression

Persist:

- current candidate hash;
- tested candidate hash;
- equality result;
- disposable-worktree flag;
- suite ID;
- pass/fail counts.

### Report consistency

Add an execution-derived consistency check across:

- implementation report facts;
- checkpoint-4 execution evidence;
- checkpoint-4 QA;
- figure-production plan count;
- scientific Figure Spec count;
- delivery summary.

At minimum reconcile:

- focused CP4 test count;
- full regression count;
- visual-class count;
- Skill count;
- archetype count;
- owning-check count;
- candidate component count;
- style profile ID;
- production/not-run statuses.

Update `PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md` so it no longer carries stale 18/298 values or the initial file accounting.

The final report/footer must reflect the actual revision candidate. Do not leave a misleading `commit_sha: null` after final delivery if the report contract expects the committed identity; if self-hash/commit-cycle constraints require a staged convention, document and validate that convention explicitly.

---

## Preserve

Do not regress:

- CP3 approved state;
- sanitized-domain-only CP4;
- private alias/source/render counters = `0 / 0 / 0`;
- ten bounded visual classes;
- 17 repository-local Skill identities;
- 10/10 acceptance coverage intent;
- route-specific style categories;
- material-semantic color blocking;
- quantitative/photo/literature empirical source protection;
- concept = non-evidence only;
- fabrication separation;
- Fishbone revision/focus/history bindings;
- unknown fabrication conditions remain unknown;
- SVG-first structured diagrams;
- native shape threshold remains insufficient evidence;
- mandatory FigureCritic before Layout;
- A01–A18 routing only;
- A01–A18 geometry `not_run`;
- production rendering `not_run`;
- FigureCritic visual acceptance `not_run`;
- template reconstruction `not_run`;
- acceptance deck `not_run`;
- native PowerPoint `not_run`;
- production Group Meeting readiness `false`.

---

## Not authorized

Do not:

- render/generate production Fishbone SVG;
- render mechanism/experiment/fabrication/comparison/matrix figures;
- render scientific plots;
- render photo annotations;
- extract/render literature figures;
- call an image generator;
- generate concept imagery;
- calibrate A01–A18 geometry;
- reconstruct templates;
- run reconstruction benchmarks;
- create PPTX;
- build acceptance deck;
- begin Phase 4;
- globally/publicly register Skills.

---

## Validation

Run at minimum:

1. focused CP4 Revision 2 RED → GREEN tests;
2. CP1 + CP2 + CP3 + CP4 regression;
3. complete package regression in a disposable worktree;
4. all six consumed CP3 input validations;
5. FigureRoutingRequest schema + FormatChecker;
6. FigureProductionPlan schema + FormatChecker;
7. ScientificFigureSpec schema + FormatChecker;
8. remaining CP4 artifact schemas + FormatChecker;
9. recursive schema-closure audit;
10. 10/10 visual-class route/spec mismatch mutation matrix;
11. Observation/empirical-slot adversarial suite;
12. style-profile fail-closed suite;
13. actual graph node/edge/contract audit;
14. 17/17 Skill registry/document audit;
15. 18/18 A01–A18 routing audit;
16. independent candidate-hash regression-binding mutation suite;
17. repository + staged privacy scan;
18. report/artifact fact consistency audit;
19. `git diff --check`;
20. remote SHA/tree/blob verification.

Full regression must remain isolated from the active implementation worktree if it mutates generated artifacts.

---

## Required report

Update:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md`

Add explicit traceability for CP4-C1 through CP4-C6.

---

## Delivery

Return:

- repository;
- branch;
- commit SHA;
- pushed yes/no;
- remote verification yes/no;
- report path;
- files added/modified/deleted;
- focused CP4 Revision 2 tests passed/failed;
- CP1+CP2+CP3+CP4 tests passed/failed;
- full disposable regression passed/failed;
- CP4-C1–CP4-C6 traceability;
- consumed style profile ID/status;
- supported/exercised/missing visual-class counts;
- route/spec discriminator audit summary;
- FigureRoutingRequest closure summary;
- graph node/edge/dangling/mismatch/bypass summary;
- specialist Skill registry count/status;
- A01–A18 routing count/status;
- candidate-state component count;
- current candidate hash;
- tested regression candidate hash;
- candidate-hash equality status;
- owning QA count/status;
- authoritative privacy scanner summary including approved legacy exception count;
- report/artifact consistency status;
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
