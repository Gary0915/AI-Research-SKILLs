# Phase 3 Professor Visual Fidelity — TDD Implementation Plan (Revision 2)

**Status:** plan-only. Production Phase 3 work remains unauthorized.

**Goal:** implement the approved private-exemplar calibration pipeline without
introducing another scientific source of truth. It will produce a fresh,
sanitized native template and ledger-derived acceptance deck, and route every
scientific visual to a provenance-governed specialist before layout.

**This revision changes no production code, schemas, Skills, profiles, figures,
private fixtures, templates, renders, benchmarks, QA artifacts, acceptance deck,
or report.** Only this plan is authorized.

## 1. Invariants and control plane

The approved Phase 1–2 chain remains the sole scientific control plane:

```text
canonical scientific objects
→ causally ordered append-only Ledger
→ Ledger.load() / hash verification / replay / cursor materialization
→ hypothesis and meeting projections
→ stage-aware Slide Specs
→ FigureProductionPlans and approved figures
→ calibrated Layout Plans
→ PythonPptxAssembler
→ structural / render / qualitative / Professor QA
```

Private exemplars may affect visual descriptors only. They may never modify
Claims, Evidence, Research Blocks, Stages, Decisions, Actions, source cursors,
Hypothesis Layers, Fishbone history, or scientific prose. The single assembly
backend remains `PythonPptxAssembler`; direct OOXML is read-only profiling/QA or
adapter-owned reconstruction support, never a second assembler.

Exemplar authority is fixed and asymmetric:

```text
template_primary_1 + template_primary_3 → formal shell/master grammar
layout_exemplar_2                     → body composition + figure grammar
persisted scientific ledger           → scientific story and claims
```

No component mathematically averages the three exemplars. Missing private
evidence is `blocked_fixture`; synthetic substitutes cannot claim professor
fidelity. Phase 4 and public/global Skill registration remain prohibited.

## 2. Two-domain privacy and render minimization

Before an alias is opened, the future `PrivateProfileStore` must prove an
ignored, untracked local root outside all committable directories. A local-only
run may use a structure such as:

```text
.private/thesis-deck-system/phase3/<run-id>/
  raw/ diagnostics/ classifier/ private-renders/ retention-manifest.json
```

It may contain resolved paths, OS diagnostics, ephemeral raw text/notes/URLs,
private package comparison data, and review inputs. It is never committed or a
production input after sanitization.

### 2.1 Structural-first streaming lifecycle

1. Scan all private slides structurally for style/geometry without rendering.
2. Select candidates using sanitized structural descriptors.
3. Capability-preflight `ImageReviewProvider` before qualitative work.
4. Render only the candidate currently requiring classification/review.
5. Inspect it; persist only controlled local class/measurement and a
   hash-bound local review record.
6. Delete its render immediately unless it is selected as a current benchmark
   or reference; retain only that minimal selected set.
7. Delete retained references at review close and record retained/deleted
   counts locally. Only aggregate sanitized counts/statuses may be committed.

If full-deck classification is genuinely necessary, it must process one slide
at a time under the same deletion rule. No private screenshot, media extraction,
notes, source basename, private render path, or private render hash crosses the
sanitizer boundary.

### 2.2 Fail-closed sanitizer

Sanitization builds a new typed object from explicit allowlisted selectors; it
never copies raw objects or recursively deletes “obvious” fields. Every schema
uses Draft 2020-12, explicit primitive types, bounded values, and
`additionalProperties: false` at every level. Unknown keys, wrong types,
paths/URLs/private canaries, binaries, or package signatures reject the whole
output before it is written.

Allowed committed values: stable aliases, source SHA-256, sanitized IDs,
controlled enums, numeric geometry/style measurements, bounded permitted font
names, and rule/metric IDs. Forbidden values: absolute paths/basenames, slide
text, notes/comments, citations/titles, URLs/DOIs, author/company metadata,
media names/bytes, raw XML/relationships, chart caches, private renders, and
private package hashes. Local diagnostics contain rule ID/location only, never
the rejected private value.

## 3. Scientific visual-asset architecture

### 3.1 Deterministic renderer hierarchy

The future `scientific-figure-router` emits an immutable
`FigureProductionPlan` before selecting a renderer. Its priority hierarchy is:

1. editable native PPTX shapes for genuinely very simple primitives;
2. structured SVG/vector for diagrams, flows, layers, and mechanisms;
3. reproducible scientific plots from canonical data;
4. real experimental image/microscopy/instrument output;
5. literature figure extracted from its source; and
6. generated conceptual illustration only when organic and non-evidence.

Generation is never the default. The router rejects a requested renderer that
conflicts with evidence role/origin.

| Visual class | Required route | Canonical output | Generation rule |
| --- | --- | --- | --- |
| quantitative result | `scientific-plot-director` → reproducible plotter | SVG/PDF/vector; PNG compatibility fallback only | forbidden |
| real experiment/photo/microscopy | `photo-annotation-director` | source evidence plus separate overlay | cannot replace evidence |
| literature figure | `literature-figure-director` | actual extraction plus citation/provenance | recreation forbidden |
| mechanism/process/stack/flow | relevant director → `vector-figure-builder` | deterministic SVG or native plan | not applicable |
| comparison/matrix | comparison/matrix director | governed SVG/native composition | forbidden for evidence |
| organic concept | concept director → `ConceptImageProvider` + overlay | generated substrate plus deterministic overlay | only non-evidence |

**SVG-first:** boxes, circles, arrows, layers, interfaces, flows, mechanisms,
and process diagrams default to editable deterministic SVG. Native shapes are
allowed only when an evidence-backed measurable rule says the primitive count
is at/below threshold `N`, all primitives are shared-library primitives, there
are no complex paths/dense motifs/clipping/multi-edge routing, and a native
shape plan preserves all bindings. `N` is deliberately not hard-coded before
measurement. Everything else is SVG canonical.

### 3.2 Shared primitive library

Future `VisualPrimitiveLibrary` contains `rectangle`, `rounded_rectangle`,
`circle`, `ellipse`, `line`, `arrow`, `curved_arrow`, `bracket`, `callout`,
`label`, `caption`, `panel_frame`, `red_highlight_box`, `material_layer`,
`measurement_marker`, `interface_marker`, `dimension_line`, `heat_flow_arrow`,
`pressure_arrow`, `electrical_signal_arrow`, `dashed_unknown_arrow`, and
`legend_key`. Primitives are not micro-Skills: scientific directors specify
meaning; the vector builder composes deterministic primitives.

### 3.3 Provider abstractions

`ConceptImageProvider` is an abstract runtime capability, not a durable literal
tool. It may be used only for an organic concept with
`evidence_status=non_evidence` and `scientific_claim_support=forbidden`; it
records generation manifest/hash and creates a separate deterministic SVG/native
overlay. It is forbidden for experimental photos, microscopy, instrument
output, measured samples, quantitative plots, literature figures, and
pseudo-evidence.

`ImageReviewProvider` is also abstract. Capability preflight records provider
ID, capability level, supported input/path form, and render-SHA binding support.
A Codex image viewer may be an adapter at runtime, but contracts cannot name it
as a repository invariant. If unavailable, non-image-capable, stale, or unable
to bind hashes, `qualitative_visual_review=blocked_visual_review`; metadata or
pixel heuristics never create a qualitative PASS.

## 4. Future contracts and evidence

New future schemas under `thesis-deck-system/schemas/`:

- sanitized exemplar manifest; shell profile; body-composition profile;
  professor visual grammar V3; Fishbone style; archetype calibration;
  reconstruction benchmark; reconstruction manifest; image-capable review; and
  Phase 3 report facts;
- `figure-production-plan.schema.json`;
- `scientific-figure-spec.schema.json`;
- `figure-output-manifest.schema.json`;
- `figure-critic-report.schema.json`;
- `visual-style-profile.schema.json`; and
- `skill-routing.schema.json`.

### 4.1 FigureProductionPlan and Figure Spec

`FigureProductionPlan` proves routing: figure ID, visual class, scientific
purpose, evidence status, source/claim/layer/block refs, selected specialist,
renderer, AI allowance, source requirement, canonical output kind, native-shape
eligibility evidence, required QA, and handoff cursor. It is derived from
cursor-materialized state only.

`scientific-figure-spec.schema.json` requires `figure_id`, `figure_type`,
`scientific_purpose`, `evidence_status`, `source_refs`, `claim_refs`,
`hypothesis_layer_ref`, `research_block_refs`, `director_skill`, `renderer`,
`style_profile_ref`, `canvas`, `components`, `connections`, `annotations`,
`labels`, `visual_states`, `provenance`, `output_targets`, and
`qa_requirements`. Mechanism specs have typed nodes/edges, causal semantics,
confidence, unknowns, and alternatives. Experiment specs have sample stack,
instrumentation, inputs/outputs, measurement points, controls, and variables.

### 4.2 Output, critic, and style contracts

`figure-output-manifest` requires figure/spec refs, renderer, source-spec hash,
canonical SVG path/hash, optional PNG path/hash, optional native-shape-plan ref,
provenance refs, style grammar ref, critic status, privacy status, evidence
status, and output-part lineage. PNG cannot be the sole canonical output where
SVG/vector is required.

`figure-critic-report` binds output hashes to executed checks, findings,
correction refs, and `APPROVED_FIGURE|FAIL|BLOCKED`.

```text
ScientificFigureSpec → renderer → output manifest → FigureCritic
→ correction loop or APPROVED_FIGURE → Layout Director
```

Layout accepts only approved assets/native plans and never illustrates or
repairs scientific figures.

`visual-style-profile` maps measured grammar to material
(`hydrogel`, `electrode`, `substrate`, `heater`, `sensor`, `contact_interface`),
arrow (`mechanism`, `measurement`, `heat_flow`, `pressure`, `electrical`,
`unknown`), emphasis (`current_focus`, `critical_result`, `red_callout`,
`warning`, `failed_but_informative`), and annotation tokens. Tokens contain
fill/stroke/width/dash/arrowhead/font/text-size/radius/padding/opacity/spacing
and descriptor provenance. Directors cannot hard-code arbitrary visual language.

## 5. Private profile, grammar, and evidence tiers

Exemplars 1/3 yield shell profiles: canvas, master/layout topology, safe bounds,
title/footer/navigation/page-number geometry, typography, and theme roles.
Exemplar 2 yields body descriptors for photo/schematic, comparison, matrix,
table/schematic, literature/mechanism, result/discussion, callout, annotation,
and density. It must measure figure grammar: primitive type/count, arrows and
orientation, label-target proximity, red-box recurrence/location, panel framing,
annotation density, photo/schematic and text/figure ratios, caption relation,
dominant visual ratio, matrix structure, comparison symmetry, take-home
placement, and whitespace.

Grammar keeps separate `shell_grammar`, `body_composition_grammar`, and
`figure_grammar`. Every rule records `evidence_tier`, `descriptor_count`,
`source_exemplar_role`, `supporting_descriptor_refs`, confidence, and status:

- `recurring_pattern`: ≥2 independent compatible direct descriptors;
- `single_example_provisional`: exactly one direct descriptor;
- `indirect_supported`: explicit related-family support only;
- `insufficient_evidence`: no defensible evidence.

One descriptor cannot establish recurring professor grammar. A reviewer waiver,
if later provided, must be an external scoped approval with expiry; a builder
must never invent it. Shell conflict records retain selected value, winner,
losing alternative, rule ID, and blocking classification. Exemplar 2 is
forbidden from every shell token family.

## 6. A01–A18 and figure routing matrix

Phase 2 semantic contracts, cursors, provenance, visible fields, split policy,
Hypothesis/Problem separation, and Fishbone bindings remain immutable. Only
geometry, hierarchy, typography/style, and layout mapping may change.

| Archetype(s) | Measured influence | Required figure route | Immutable obligation |
| --- | --- | --- | --- |
| A01/A02 | shell 1/3; body 2 problem balance | native governed text/layout | question/hypothesis/falsifier; Problem separate |
| A03 | shell 1/3 + figure grammar | fishbone director → SVG builder | revision/focus/branch history |
| A04 | body 2 observation grammar | real photo annotation or approved concept | observation/question/evidence binding |
| A05 | body 2 | literature extraction + mechanism director | synthesis/citation provenance |
| A06 | body 2 | mechanism director → SVG/native decision | mechanism/strategy/criterion |
| A07 | body 2 | photo annotation + experiment schematic | photo and annotations co-exist |
| A08 | body 2 | comparison director | fair Control/Proposed distinction |
| A09 | body 2 | experiment schematic + native table | IV/controls/N/method/prediction/rule |
| A10 | body 2 | plot director or real photo | evidence/metric/uncertainty/units |
| A11 | body 2 | plot + comparison director | distinct results/fair scales |
| A12 | body 2 | image-matrix director | order/identity/captions/scales |
| A13 | body 2 | plot + FigureCritic annotation | result/discussion/decision/next step |
| A14/A15 | body 2 + closure shell | native field-level regions | discussion/summary field completeness |
| A16 | shell 1/3 + derivation grammar | transition SVG | causal predecessor/successor |
| A17 | body 2 | native table + simple diagram | commitment/owner/time/dependencies |
| A18 | schedule evidence | native timeline or SVG | owner/time/decision/dependency |

Each calibration records evidence tier, changed token families, layout role,
immutable semantic-contract hash, and fallback. Insufficient evidence retains
Phase 2 geometry but blocks recurring grammar claims. Acceptance-deck fidelity
and reusable-library coverage are separate statuses.

## 7. Repo-local Skill contracts and routing map

All future Skills remain local and unregistered. Every future `SKILL.md` must
state name, trigger, do-not-trigger-when, inputs, required context, workflow,
allowed downstream Skills/tools, forbidden actions, output contract, provenance
behavior, failure modes, blocked states, handoff target, and QA owner.

| Skill | Trigger/output | Forbidden action | Handoff / QA owner |
| --- | --- | --- | --- |
| `thesis-deck-router` | routes ledger-derived request | draw figures | planners/router; provenance QA |
| `scientific-method-planner` | experiment/stage requirements | invent data | figure router; Professor QA |
| `hypothesis-layer-planner` | N-layer history | flatten layers/merge Problem | method planner; Professor QA |
| `scientific-figure-router` | FigureProductionPlan | default AI/bypass specialist | selected director; provenance QA |
| `fishbone-director` | versioned Fishbone spec | alter graph/history | vector builder; Fishbone QA |
| `mechanism-diagram-director` | causal mechanism spec | imply certainty for unknowns | vector builder; critic |
| `experiment-schematic-director` | stack/instrument spec | omit controls/replace photos | vector builder; critic |
| `scientific-plot-director` | data plot spec | AI/raster-only plot | plotter; provenance QA |
| `photo-annotation-director` | source photo overlay plan | replace source image | overlay; provenance QA |
| `literature-figure-director` | extracted/cited figure plan | AI recreation | critic; provenance QA |
| `comparison-figure-director` | comparison spec | alter scale/side binding | renderer; critic |
| `image-matrix-director` | ordered matrix spec | lose labels/scales/order | renderer; critic |
| `concept-illustration-director` | non-evidence concept plan | claim evidence | provider/overlay; provenance QA |
| `vector-figure-builder` | deterministic SVG/native plan | invent science/style | critic; structural QA |
| `visual-style-governor` | descriptor-derived tokens | arbitrary cross-slide drift | directors; style QA |
| `figure-critic` | evidence-backed figure decision | approve missing evidence | layout; critic QA |
| `layout-director` | place approved assets | create/repair figures | assembler; structural QA |
| `professor-qa` | science/presentation/calibration checks | qualitative visual certification | release; Professor QA |
| `visual-qa` | pixel/review coordination | PASS without provider | report QA |
| `provenance-qa` | source/asset lineage | create visual asset | critic/release QA |

Future `skill-routing.yaml` is schema-versioned and records input predicates,
allowed transitions, required plan/spec/output artifacts, and owner QA.

```text
experiment request → thesis-deck-router → hypothesis-layer-planner
→ scientific-method-planner → scientific-figure-router
→ experiment-schematic-director → vector-figure-builder → figure-critic
→ layout-director → PythonPptxAssembler → visual-qa → professor-qa

result plot → scientific-figure-router → scientific-plot-director
→ figure-critic → layout-director

real experimental photo → scientific-figure-router → photo-annotation-director
→ figure-critic → layout-director

organic conceptual illustration → scientific-figure-router
→ concept-illustration-director → ConceptImageProvider → deterministic overlay
→ figure-critic → layout-director
```

Routing tests reject giant all-purpose bypasses, unauthorized generation, and
Layout-created evidence figures.

### 7.1 Concrete future module, schema, and test locations

The future production changes are bounded to the following locations; this
planning revision creates none of them.

| Future path | Responsibility | Owning RED suites |
| --- | --- | --- |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_privacy.py` | ignored-root guard, allowlist, scans, retention policy | `test_phase3_privacy.py` |
| `private_fixtures.py`, `phase3_profiler.py`, `phase3_profiles.py` | alias/OOXML validation, minimal local profile, sanitizer/resolvers | `test_phase3_profiler.py`, `test_phase3_resolvers.py` |
| `image_review.py`, `concept_images.py` | provider preflight and provider boundaries | `test_phase3_visual_review.py`, `test_phase3_concept_images.py` |
| `figure_routing.py`, `figure_contracts.py` | FigureProductionPlan, Figure Spec, routing policy | `test_phase3_figure_router.py`, `test_phase3_figure_contracts.py` |
| `visual_primitives.py`, `visual_style.py`, `vector_figures.py` | shared primitives, governed tokens, deterministic SVG/native plans | `test_phase3_vector_figures.py`, `test_phase3_style_governor.py` |
| `mechanism_diagrams.py`, `experiment_schematics.py`, `comparison_figures.py`, `image_matrices.py` | specialist scientific figure specs | dedicated director test modules |
| `scientific_plots.py`, `photo_annotation.py`, `literature_figures.py` | plot/photo/literature source workflows | `test_phase3_plot.py`, `test_phase3_photo.py`, `test_phase3_literature.py` |
| `figure_critic.py` | pre-layout FigureCritic decision/evidence | `test_phase3_figure_critic.py` |
| `phase3_calibration.py`, `fishbone.py`, `layout.py` | calibrated A01–A18/Fishbone/Layout consumption | `test_phase3_calibration.py` |
| `pptx.py`, adapter-private `pptx_reconstruction.py` | sole-backend reconstruction/assembly | `test_phase3_reconstruction.py` |
| `phase3_metrics.py`, `phase3_benchmark.py` | metric formulas and dual benchmark selection | `test_phase3_metrics.py`, `test_phase3_benchmarks.py` |
| `phase3_build.py`, `qa3.py`, `phase3_render.py` | ledger-derived build and owning gates | integration build/regression/QA suites |
| `thesis-deck-system/skill-routing.yaml` and local `skills/*/SKILL.md` | only the defined repo-local routing/Skill contracts | `test_phase3_skill_routing.py` |

All future schemas listed in §4 are registered in `contracts.py` with existing
Phase 1–2 contracts untouched. Future tests live under
`packages/thesis-deck-system/tests/unit/` or `tests/integration/` and use only
redistributable synthetic fixtures unless a future implementation checkpoint is
explicitly authorized to read an alias within the ignored private domain.

### 7.2 Full contract fields for each future Skill

The table below is the implementation-ready completion of the common contract
format stated above. `ctx` is required cursor-materialized context; `flow` is
the bounded workflow; `allow` is the only downstream authority; `fail` includes
both failure mode and blocked state. Every output includes an ID, hash-bound
input refs, source cursor, and provenance chain.

| Skill | Trigger / do-not-trigger | ctx / flow | allow / forbidden | output / provenance / fail / handoff / QA |
| --- | --- | --- | --- | --- |
| thesis-deck-router | ledger-derived slide request; not raw fixture/private style request | block/layer/stage cursor → route | planners/router only; no figure drawing | route record; ledger refs; unresolved route blocks → planner; provenance QA |
| scientific-method-planner | experiment/method stage; not result-art rendering | question/hypothesis/experiment fields → method requirements | figure router; no data invention | method plan; stage refs; missing field blocks → router; Professor QA |
| hypothesis-layer-planner | layer/history request; not one-off visual edit | ordered materialized layers → predecessor/current/successor context | method planner; no flattening/Problem merge | layer projection; event refs; missing transition blocks → router; Professor QA |
| scientific-figure-router | approved scientific visual request; not arbitrary decoration | FigureProductionPlan predicates → deterministic specialist selection | named director; no default AI/bypass | plan; source/claim refs; conflict blocks → router; provenance QA |
| fishbone-director | historical Fishbone role; not unversioned map | canonical Fishbone revision/focus → style-applied spec | vector builder; no graph/history mutation | Fishbone spec; revision hash; missing revision blocks → critic; Fishbone QA |
| mechanism-diagram-director | mechanism/alternative/unknown visual; not data plot | causal nodes/edges/confidence → typed spec | vector builder; no certainty invention | mechanism spec; claim/evidence refs; missing unknown/label fails → critic; FigureCritic |
| experiment-schematic-director | experiment design/stack; not photo replacement | variables/controls/method/instrumentation → schematic spec | vector builder; no omitted controls | schematic spec; stage refs; incomplete stack blocks → critic; FigureCritic |
| scientific-plot-director | quantitative data result; not conceptual request | verified dataset/units/replicates → reproducible plot spec | plotting adapter; no AI/raster-only canonical | plot spec+SVG manifest; missing data blocks → critic; provenance QA |
| photo-annotation-director | real experimental image; not synthetic substitute | source asset/physical interfaces → overlay plan | vector overlay; no source replacement/AI | source+overlay manifest; source mismatch blocks → critic; provenance QA |
| literature-figure-director | cited literature figure; not mechanism recreation | citation/source extraction rights → extraction plan | extractor/critic; no AI recreation | extracted source manifest; missing citation/source blocks → critic; provenance QA |
| comparison-figure-director | control/proposed or result comparison; not single result | left/right bindings/scales → comparison spec | vector/native renderer; no scale/side swap | comparison spec; field refs; unfair scale fails → critic; FigureCritic |
| image-matrix-director | multi-panel image evidence; not arbitrary collage | row/column semantics/scales → ordered matrix spec | renderer; no panel reorder/caption loss | matrix spec; asset refs; missing scale blocks → critic; FigureCritic |
| concept-illustration-director | organic non-evidence concept; not real/lit/plot | non-evidence purpose → provider request + overlay spec | ConceptImageProvider/overlay; no claim support | generation plan; non-evidence manifest; provider block → critic; provenance QA |
| vector-figure-builder | approved vector/native spec; not untyped prose | spec+style tokens → deterministic SVG/native plan | FigureCritic; no scientific invention/style drift | output manifest+geometry; non-determinism blocks → critic; structural QA |
| visual-style-governor | director token resolution; not standalone art creation | measured grammar/token evidence → token set | directors; no arbitrary hard-code | token resolution; descriptor refs; insufficient tier blocks rule → director; style QA |
| figure-critic | completed output manifest; not incomplete spec | spec+output+render/provenance → executed findings | correction route/layout only when approved; no self-generation | critic report; hash refs; FAIL/BLOCKED stops layout → layout; critic QA |
| layout-director | approved figures + Slide Spec; not FigureCritic failure | calibrated archetype/slots → physical placement | assembler; no figure creation/repair | Layout Plan; approved figure refs; missing slot/approval blocks → assembler; structural QA |
| professor-qa | complete presentation evidence; not metadata-only review | ledger projection+semantic/fidelity evidence → rubric check | release gate; no qualitative inference | professor report; QA refs; missing owning evidence blocks → release; Professor QA |
| visual-qa | rendered slide and provider capability; not absent/stale render | render hash/pixels/review record → pixel + qualitative coordination | report gate; no PASS without provider | visual QA; hash/provider refs; blocked review propagates → report; visual QA |
| provenance-qa | FigurePlan/spec/output request; not asset creation | source/claim/evidence lineage → chain validation | critic/release; no source fabrication | provenance report; all refs; unresolved/AI misuse fails → critic; provenance QA |

## 8. Reconstruction lineage and benchmark architecture

### 8.1 Fresh package proof

`PythonPptxAssembler.reconstruct_sanitized_template()` will accept sanitized
descriptors and a reconstruction manifest only—not alias paths, private files,
raw profiles, or source bytes. It builds a fresh package and gives every output
part lineage: `reconstructed_shell`, `builder_required`, `sanitized_metadata`,
or `generated_scientific_asset`.

Local comparisons classify private/output equality as:

- `prohibited_content_bearing`: media, notes, comments, custom XML, private
  slides, OLE, embeddings, macros, charts/cache, thumbnails, or private text;
  any equality/reuse hard-fails;
- `source_specific_style_or_structure`: requires generated descriptor lineage
  and privacy scan; unexplained equality fails;
- `generic_deterministic_boilerplate`: equality is recorded as
  `benign_equivalence`, not copying.

Package QA proves manifest coverage, allowed families, no external/orphan
relationships, generic metadata, and zero prohibited reuse. This replaces the
unsound “all package hashes must differ” rule.

### 8.2 Representative + stress benchmarks

For each family with ≥2 descriptors, choose both
`representative_reference` (nearest the medoid in sanitized feature space) and
`stress_reference` (highest deterministic complexity/density). With one
descriptor use `single_example`, never recurring grammar. Tie-break by
sanitized descriptor ID and persist vector, distance, complexity, and rationale.

Families: formal shell/content, Hypothesis/Problem, photo+schematic,
Control/Proposed, experiment schematic, Result single, Result comparison,
Result+Discussion, image matrix where supported, and Fishbone/history where
supported. Missing evidence is `insufficient_evidence`, never fabricated.

### 8.3 Metric formulas

Geometry uses `(x/W,y/H,w/W,h/H)`. Edge error is max absolute
left/top/right/bottom delta; IoU is intersection/union (zero union invalid).
Area metrics use union area clipped to safe bounds. Measure title/caption/callout
error, figure/text and photo/schematic ratios, gutters, panel symmetry,
matrix gap, table/diagram ratio, footer alignment, whitespace, font/line delta,
and Fishbone branch position.

Figure metrics additionally cover primitive-count match, primitive-role coverage
`matched_required_roles/required_roles`, normalized component geometry, arrow
endpoint Euclidean/direction-angle error, label-target distance normalized by
canvas diagonal, annotation density, red-callout location, graph topology exact
edge/parent match, experiment stack order as LCS/required length, and caption
spacing. CIEDE2000 is sRGB D65 → linear RGB → XYZ D65 → CIELAB using white
`(0.95047,1,1.08883)` and Sharma 2005 ΔE00 with `kL=kC=kH=1`; fixtures use
published reference pairs. Pixel whitespace requires ΔE00≤3 from corner-patch
background and normalized Sobel≤0.02. No global pixel similarity can pass a
failed required metric.

## 9. TDD phases and RED inventory

Every phase begins RED, reaches focused GREEN, runs earlier focused suites plus
all Phase 1–2 regression, then refactors only while green. A failed gate stops
progress; requirements are never weakened.

| Phase | Future work | RED cases | Stop/go evidence |
| --- | --- | ---: | --- |
| A | contracts, privacy, provider preflight | 32 | sanitizer/provider QA; no private open |
| B | minimized profiler + streaming classification | 17 | ingestion/retention QA |
| C | shell/body/figure grammar, conflicts, tiers | 24 | resolver QA; conflict stop |
| D | style governor + figure router | 30 | routing/plan QA |
| E | vector stack: mechanism/experiment/fishbone/comparison/matrix | 42 | SVG/native plans + critic QA |
| F | plot, real-photo, literature workflows | 27 | provenance/output QA |
| G | ConceptImageProvider boundary | 12 | non-evidence QA |
| H | A01–A18/Fishbone calibration + template reconstruction | 31 | package-lineage QA |
| I | representative/stress and figure benchmarks | 29 | benchmark QA |
| J | ledger-derived acceptance deck | 17 | replay/structural/SVG QA |
| K | FigureCritic integration, visual/Professor/report gates | 24 | owning QA/status truth |
| **Total** |  | **285** | `32+17+24+30+42+27+12+31+29+17+24=285` |

### Phase A — contracts, privacy, providers (32)

RED: all schema/type/format failures; ignored-root and scanner corpus;
absent/non-image/hash-unbound/stale `ImageReviewProvider`; wrong path form;
preflight evidence; blocked review propagation. GREEN adds only typed contracts,
scanners, and provider interfaces. No alias opens.

### Phase B — profiler and minimized classification (17)

RED: alias/OOXML failures, guard-before-open, ephemeral text/notes/URL handling,
all-slide structural scan, candidate-only rendering, immediate deletion,
retained/deleted accounting/cleanup, and blocked qualitative classification.
GREEN supports streaming local review only.

### Phase C — profiles, roles, evidence tiers (24)

RED: separate profile schemas; every Exemplar-2 shell injection; authority and
conflict winner/loser/rule/classification; hard conflicts; no averaging;
descriptor grouping/outlier retention; all four tiers; one-descriptor non-
recurrence; external-waiver-only validation; scoped statuses. GREEN has no
scientific mutations.

### Phase D — governor and router (30)

RED: quantitative→plot, photo→annotation, literature→extraction,
mechanism→SVG/native decision, experiment→schematic, organic→concept; AI
rejection for experimental/literature/plot evidence; SVG-first/native rule;
Figure Spec requirements; token consistency/drift; source provenance; no giant
bypass; Layout's finished-assets-only rule. GREEN produces routing contracts.

### Phase E — vector figure stack (42)

RED: deterministic SVG/geometry manifest/no invention/style tokens; mechanism
causal direction, unknowns, observation/hypothesis distinction, labels;
experiment stack, locations, I/O, controls, variables; Fishbone history/stable
positions; fair comparison and labels; matrix ordering/scales/captions; critic
tests for misleading arrow, missing uncertainty, unreadable labels, excess
decor, and failed figure blocking Layout. GREEN implements specialist directors
and vector builder only after routes exist.

### Phase F — plot/photo/literature (27)

RED: data provenance, SVG canonical/PNG fallback, units, replicate/error;
source-photo preservation/separate overlay/interface binding/no AI replacement;
literature citation/extraction/AI-recreation rejection; output hashes and
failure propagation. GREEN uses reproducible plots and genuine sources.

### Phase G — concepts (12)

RED: mandatory `non_evidence`, forbidden claim support, generation manifest,
deterministic overlay, output hash, prohibited source classes, provider failures,
and refusal where a real-evidence route exists. GREEN implements only the
abstract capability boundary.

### Phase H — calibration and reconstruction (31)

RED: 18 immutable semantic hashes; insufficient-used-archetype block; Fishbone
visual-only application; sanitized-only reconstruction API/private-argument
rejection; per-part lineage; prohibited reuse; unexplained source-style equality;
benign boilerplate equivalence; relation/orphan/external/metadata checks; sole
backend dependency scan. GREEN stays adapter-owned.

### Phase I — reconstruction benchmarks (29)

RED: representative medoid + stress selection, deterministic ties,
single-example state, all families, privacy-safe records, formula boundaries
(including CIEDE2000 and figure metrics), failed-metric block, and no global
similarity override. GREEN emits only sanitized metrics.

### Phase J — ledger acceptance deck (17)

RED: `Ledger.load()`-only materialization, fixture/private visual mutation
reproducibility, N-layer/cursor retention, all used archetypes, FigureCritic
approval, physical slots, template/SVG relationships, notes, Chinese wrapping,
and no second backend. GREEN uses only the approved assembler.

### Phase K — owning QA and report (24)

RED: critic-to-layout block, stale/missing evidence, review hash mismatch,
render mutation, slide-specific findings, blocked qualitative review, Professor
QA fidelity consumption, status independence, report truth, privacy scan,
native block, and release honesty. GREEN executes owning checks; no gate may
synthesize another gate's PASS.

## 10. Artifacts, QA ownership, and final status

Future committed artifacts are sanitized profiles/grammar/style/calibration,
Figure Plans/Specs/Output Manifests/Critic reports, reconstructed template,
benchmarks/sanitized renders, ledger-derived Slide Specs/Layout Plans/Manifest/
acceptance PPTX, and owning QA records. Raw profiles, aliases, private package
comparisons, and minimally retained private reference renders stay local.

Owners: ingestion QA validates alias/hash/OOXML; privacy QA validates boundary;
resolver QA validates authority/tier/conflict; provenance QA validates figure
sources; FigureCritic validates figure truth; structural QA validates PPTX;
render QA validates pixels; ImageReviewProvider owns qualitative review;
Professor QA consumes science and fidelity evidence; report QA validates facts.

The report-facts schema records independent dimensions:

- `private_exemplar_ingestion`
- `shell_fidelity`
- `body_composition_fidelity`
- `figure_grammar_fidelity`
- `figure_grammar_calibration_coverage`
- `fishbone_visual_fidelity`
- `acceptance_deck_visual_fidelity`
- `archetype_library_calibration_coverage`
- `figure_skill_routing_coverage`
- `reconstruction_benchmark_status`
- `qualitative_visual_review`
- `native_powerpoint_acceptance`
- `production_group_meeting_ready`

A specific acceptance deck can pass while unused archetypes remain provisional;
that does not claim library-wide calibration. Production readiness remains false
unless all private, scientific, visual, native, and permitted real-fixture gates
pass. Native PowerPoint unavailable means `blocked_environment`.

## 11. Traceability

| Requirement | Coverage |
| --- | --- |
| Design §1 scope/invariants | §§1, 9J/K | Phase 1–2 regression and semantic QA |
| Design §2 two domains | §2, 9A/B | privacy boundary and retention QA |
| Design §3 ingestion | §§2, 9B | exemplar-ingestion QA |
| Design §4 raw private model | §§2, 9A/B | local-only retention/cleanup manifest |
| Design §5 whitelist sanitizer | §2.2, 9A | sanitizer/privacy QA |
| Design §6 sanitized contracts | §4, 9A/C/H/I/K | schema validation and profiles/metrics/facts |
| Design §7 role separation | §5, 9C | resolver-conflict QA |
| Design §8 shell resolver | §5, 9C/H | resolved shell/conflict evidence |
| Design §9 body resolver | §5, 9C/D | body and figure-grammar profile QA |
| Design §10 A01–A18 calibration | §6, 9H/J | archetype calibration and layout QA |
| Design §11 native reconstruction | §8.1, 9H | reconstruction manifest/package QA |
| Design §12 benchmark architecture | §§8.2–8.3, 9I | sanitized benchmark metrics QA |
| Design §13 Fishbone calibration | §§6, 9E/H | Fishbone style/history QA |
| Design §14 backend boundary | §§1, 8.1, 9H/J | import/dependency and assembly audit |
| Design §15 image review | §3.3, 9A/B/K | provider preflight/review records |
| Design §16 privacy negatives | §§2, 9A/B/I/K | repository/privacy mutation QA |
| Design §17 acceptance gates | §10, 9K | owning QA and status artifact |
| Design §18 native/readiness | §10, 9K | Stage 8/production-readiness evidence |
| Design §19 QA ownership | §10, 9K | gate ownership/anti-synthesis tests |
| Design §20 D3 traceability | §11, 9A–K | implementation report facts check |
| Design §21 next TDD phases | §9 | checkpoint sequence and RED arithmetic |
| Design §22 risks/questions | §12 | insufficiency/block behavior tests |

| Condition | Concrete plan location |
| --- | --- |
| P3P-1 | §§2, 9A/B minimal private storage/cleanup |
| P3P-2 | §2.2 scanner and sanitized alias/hash boundary |
| P3P-3 | §5/9C exhaustive shell-contamination tests |
| P3P-4 | §5/9C conflict evidence and hard stops |
| P3P-5 | §8.1/9H lineage and prohibited-reuse proof |
| P3P-6 | §8.2/9I representative and stress selection |
| P3P-7 | §8.3/9I formula fixtures |
| P3P-8 | §3.3/9A/B/K provider preflight/blocking |
| P3-PLAN-B1 | §3.3, 9A/K provider abstraction |
| P3-PLAN-B2 | §§5–6, 9C/H evidence tiers/scoped coverage |
| P3-PLAN-B3 | §8.2, 9I dual benchmark roles |
| P3-PLAN-B4 | §8.1, 9H fresh lineage/non-reuse |
| P3-PLAN-B5 | §2.1, 9B streaming retention |
| P3-PLAN-B6 | §10, 9C/K independent statuses |

## 12. Risks and stop conditions

- The native-shape threshold `N` must be measured; until then SVG is the safe
  default.
- Weak direct evidence yields provisional/insufficient status, not fabricated
  recurring grammar.
- Font metrics may differ across profiling, LibreOffice, and native PowerPoint.
- Image review may be unavailable/hash-unbound; qualitative review then blocks.
- `python-pptx` master/layout limitations may require adapter-owned OOXML, but
  a second backend is prohibited.
- Native PowerPoint and a permitted real scientific fixture may remain blocked;
  production readiness must remain false.

Before delivery, verify every design section, P3P-1–P3P-8, P3-PLAN-B1–B6, all
twenty Skill contracts, deterministic routing, SVG-first policy, narrow
generation boundary, FigureCritic-before-Layout, render minimization, status
separation, and RED arithmetic. Confirm no private path/content or production
file changed, run `git diff --check`, push, verify the remote plan blob, then
stop for reviewer approval.
