# Task — Phase 3 Checkpoint 4 Revision

## Status

Checkpoint 4 is **NOT APPROVED**.

Implement only CP4-B1 through CP4-B6 from:

`thesis-deck-system/reviews/PHASE_3_CHECKPOINT_4_REVIEW.md`

Do not start production Figure rendering, A01–A18 geometry calibration, template reconstruction, benchmarks, acceptance deck, or Phase 4.

---

## CP4-B1 — Bind the actual CP3 Visual Style Governor identity and route-specific readiness

The current approved CP3 style artifact is the authority. Do not hard-code a stale profile ID.

Required behavior:

- derive `style_profile_ref` from consumed `visual-style-profile.json`;
- require plan/spec profile reference to equal the consumed artifact ID;
- remove stale schema constants that contradict the consumed CP3 identity;
- derive `required_style_categories` by visual class;
- persist per-category consumption records with:
  - category ID;
  - CP3 readiness status;
  - consumption mode;
  - provenance/source profile ref;
  - blocking/unresolved reason where applicable;
- use recurring evidence directly only when permitted;
- provisional evidence must remain flagged;
- unresolved required evidence must block or explicitly invoke approved fallback policy;
- material semantic colors remain blocked and may never be invented.

Required RED cases:

1. stale/wrong `style_profile_ref` fails;
2. CP3 profile ID mutation invalidates plan/spec;
3. mechanism/Fishbone require connector-arrow grammar;
4. visual classes receive different relevant style-category sets;
5. unresolved required category cannot be silently treated as calibrated;
6. provisional category remains flagged provisional.

---

## CP4-B2 — Add route-consistent ScientificFigureSpec discrimination

Create an explicit mapping between:

- `visual_class`;
- Figure Spec `figure_type`;
- director Skill;
- renderer class;
- canonical output target;
- evidence status/source requirement.

At minimum enforce:

- quantitative measured result → `scientific_plot`;
- real experiment/photo → `real_photo`;
- literature figure → `literature_figure`;
- organic concept → `concept_illustration`;
- mechanism / experiment schematic / fabrication / Fishbone / comparison / matrix composition → documented structured diagram variants.

The v4 schema must reject mismatches.

Do not create real/photo/literature/concept specs as generic `vector_diagram` merely because no rendering occurs yet.

Required RED cases:

1. real photo + `vector_diagram` fails;
2. literature route + `vector_diagram` fails;
3. concept route + non-concept type fails;
4. quantitative route + non-plot type fails;
5. director mismatch fails;
6. renderer/output mismatch fails.

---

## CP4-B3 — Make execution acceptance cover all ten visual classes

Build a deterministic sanitized acceptance request/plan/spec set containing exactly one or more controlled cases for every supported visual class:

1. quantitative measured result;
2. real experiment/photo;
3. literature figure;
4. mechanism explanation;
5. experiment setup;
6. fabrication process;
7. Fishbone history;
8. fair comparison;
9. image matrix;
10. organic concept.

The committed routing artifacts must expose truthful coverage. No class may be absent while a check claims full visual-class coverage.

Execution-owned QA must persist at least:

- supported visual class count = 10;
- exercised visual class count = 10;
- missing class count = 0;
- per-class selected Skill;
- per-class Figure Spec type;
- per-class renderer class;
- per-class AI allowance;
- per-class source/evidence requirement status;
- per-class native-shape status;
- failed/mismatched class count.

Do not use a blanket expression such as “all non-quantitative must use deterministic SVG” because real-photo, literature-source, and concept routes have different renderer semantics.

Required RED cases must mutate each family independently and prove the owning QA fails.

---

## CP4-B4 — Normalize actual routing graph; eliminate persisted bypasses

The registry's executable/user routes, per-Skill contracts, and declared handoff graph must agree.

Required invariant for scientific visuals:

`scientific state → FigureProductionPlan → specialist director → renderer/builder/output manifest → FigureCritic → APPROVED_FIGURE → Layout Director`

Required behavior:

- all user routes that create or place scientific visuals enter `scientific-figure-router`;
- no scientific user route may hand directly to `layout-director` before FigureCritic approval;
- no director may hand a raw/spec-level output directly to FigureCritic when FigureCritic declares an output manifest input;
- vector directors may hand to `vector-figure-builder`, then future output manifest, then FigureCritic;
- plot/photo/literature/concept routes must explicitly include their future renderer/output-manifest stage before FigureCritic;
- Layout accepts only `APPROVED_FIGURE` with provenance;
- non-figure workflows may bypass Figure routing only when explicitly tagged/classified as non-figure paths.

Add graph validation over:

- `routes`;
- `skills[].allowed_downstream`;
- `skills[].handoff_target`;
- declared `handoff_graph`;
- output/input contract compatibility.

Required RED cases:

1. result-page route directly to Layout fails;
2. literature/mechanism route directly to Layout fails;
3. Fishbone route bypassing FigureCritic fails;
4. specialist spec handed directly to FigureCritic fails when manifest is required;
5. unknown downstream target fails;
6. output/input contract mismatch fails.

---

## CP4-B5 — Add a closed, fail-closed Figure routing request boundary

Introduce a schema-backed `FigureRoutingRequest` or an equivalent closed validator before routing.

Unknown evidence-semantic fields must not be silently ignored.

The request boundary must explicitly represent or explicitly reject empirical slot bindings, including at least:

- `observation_evidence_ref` or equivalent Observation empirical binding;
- empirical evidence refs;
- experimental image/evidence slot refs;
- quantitative result evidence slot refs;
- literature figure evidence slot refs.

For `organic_concept`:

- `evidence_status = non_evidence`;
- `scientific_claim_support = forbidden`;
- claim refs empty;
- evidence refs empty;
- all empirical slot bindings absent/empty;
- no Observation slot may be satisfied;
- no literature/experimental/quantitative evidence slot may be satisfied.

For real empirical/literature routes, required source/evidence fields must remain mandatory.

Required RED cases:

1. concept + `observation_evidence_ref` fails;
2. concept + experimental image slot fails;
3. concept + quantitative result slot fails;
4. concept + literature evidence slot fails;
5. unknown request key affecting evidence semantics fails;
6. empirical route missing source/evidence fails;
7. valid auxiliary concept remains routable only as non-evidence.

---

## CP4-B6 — Bind disposable regression to the complete execution-affecting candidate state

Persist execution-owned full-regression evidence.

Required candidate component coverage includes at minimum:

- all six consumed CP3 artifacts;
- CP4 router/control-plane source;
- `contracts.py` if its schema registration affects CP4 execution;
- all CP4 schemas/contracts;
- `skill-routing.yaml`;
- all 17 repo-local Skill `SKILL.md` files;
- any additional source dependency whose mutation changes routing/privacy/schema semantics used by CP4.

Persist:

- component hash map;
- composite candidate-state hash;
- regression candidate-state hash;
- disposable-worktree = true;
- passed count;
- failed count;
- regression status;
- exact command/suite identifier or controlled equivalent.

Add a real owning check:

`CP4-DISPOSABLE-REGRESSION`

PASS only when the regression evidence binds the exact current candidate state.

Required RED cases:

1. CP4 source mutation invalidates old regression evidence;
2. schema mutation invalidates it;
3. `skill-routing.yaml` mutation invalidates it;
4. any `SKILL.md` mutation invalidates it;
5. `contracts.py` mutation invalidates it where execution-affecting;
6. changed CP3 input invalidates it;
7. wrong regression candidate hash fails;
8. non-disposable regression evidence fails;
9. failed test count > 0 fails.

---

## Execution-owned QA requirements

Do not solve this by cosmetically increasing check count.

The final owning evidence must explicitly cover the required control dimensions, including:

- canonical CP3 schema/status/hash validation;
- exact CP3 style profile identity;
- no private source access;
- 10/10 visual-class execution coverage;
- deterministic routing;
- route/spec semantic discrimination;
- specialist exclusivity;
- source/evidence requirements;
- Observation empirical boundary;
- AI-generation prohibitions;
- fabrication/mechanism/measurement separation;
- Fishbone identity/history;
- SVG/native policy;
- route-specific Governor readiness;
- material-color non-invention;
- 17/17 Skill registry completeness;
- actual no-bypass graph validation;
- 18/18 archetype routing completeness;
- recursive schema closure;
- repository/staged privacy;
- candidate-bound disposable full regression.

Evidence should persist counts, controlled IDs, and hashes where those are the real proof; do not reduce every owning check to one opaque boolean.

---

## Schemas

Add/strengthen schemas as needed, including a routing-request contract if selected.

All v4 nested objects must be closed and strongly typed.

Preserve legacy v3 compatibility only where genuinely required by accepted regression fixtures. Legacy compatibility must not weaken v4 semantics.

---

## Artifacts

Regenerate all authorized CP4 artifacts, including:

- figure-production-plans;
- scientific-figure-specs;
- archetype routing;
- execution evidence;
- final QA;
- routing registry;
- any new schema-backed routing acceptance/coverage artifact required by the correction.

Do not generate any production visual asset.

---

## Report

Update:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md`

Add explicit traceability for:

- CP4-B1;
- CP4-B2;
- CP4-B3;
- CP4-B4;
- CP4-B5;
- CP4-B6.

Correct the stale `VSP001` statement.

Report the actual exercised visual class count, actual Skill graph audit, actual style-profile ID, and actual candidate-bound regression evidence.

---

## Preserve

Do not regress:

- CP3 approved status;
- CP4 sanitized-only boundary;
- private alias/source/render counters = `0 / 0 / 0`;
- no private PPTX/profile/render access;
- no production SVG/PDF/PNG/plot/generated image/PPTX;
- generated concepts remain non-evidence only;
- fabrication remains distinct;
- unknown fabrication conditions remain unknown;
- Fishbone revision/focus/history preserved;
- native-shape threshold remains unresolved unless measured evidence exists;
- structured diagrams remain conservative SVG-first;
- material semantic colors remain unresolved;
- FigureCritic mandatory before Layout;
- A01–A18 geometry calibration = `not_run`;
- template reconstruction = `not_run`;
- acceptance deck = `not_run`;
- native PowerPoint = `not_run`;
- private qualitative review = `blocked_visual_review`;
- production Group Meeting readiness = `false`.

---

## Validation

Run:

1. focused CP4 revision RED→GREEN tests;
2. CP1 + CP2 + CP3 + CP4 focused suite;
3. complete package regression in disposable worktree;
4. all six CP3 input schema/status/hash validations;
5. all CP4 schema validations with Draft 2020-12 FormatChecker;
6. recursive schema closure;
7. 10/10 visual-class acceptance coverage audit;
8. route/spec discriminator audit;
9. empirical-slot / Observation-boundary mutation suite;
10. Skill registry + actual graph/no-bypass audit;
11. A01–A18 route coverage audit;
12. style-profile identity/readiness audit;
13. candidate-state component/hash audit;
14. candidate-bound disposable regression audit;
15. repository + staged privacy scan;
16. `git diff --check`;
17. remote SHA/tree/blob verification.

Do not run the complete regression in the active implementation worktree if it mutates unrelated generated artifacts.

---

## Not authorized

Do not begin:

- production vector/SVG generation;
- scientific plot rendering;
- real-photo rendering/annotation output;
- literature figure extraction output;
- concept image generation;
- production Fishbone output;
- production mechanism/experiment/fabrication output;
- A01–A18 geometry calibration;
- template reconstruction;
- reconstruction benchmarks;
- acceptance deck;
- PPTX generation;
- native PowerPoint acceptance;
- Phase 4;
- public/global Skill registration.

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
- focused CP4 revision tests passed/failed;
- CP1+CP2+CP3+CP4 tests passed/failed;
- full disposable regression passed/failed;
- CP4-B1 style identity/readiness summary;
- CP4-B2 route/spec discriminator summary;
- CP4-B3 10-class acceptance coverage summary;
- CP4-B4 actual no-bypass graph audit summary;
- CP4-B5 Observation/empirical-slot boundary summary;
- CP4-B6 candidate-state/regression binding summary;
- owning QA count/status;
- actual consumed style profile ID;
- specialist Skill registry count;
- A01–A18 route coverage;
- private alias/source/render counters;
- production figure rendering status;
- FigureCritic visual acceptance status;
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
