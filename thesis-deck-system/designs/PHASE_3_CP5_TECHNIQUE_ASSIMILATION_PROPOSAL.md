# Phase 3 — CP5 Technique-Assimilation Roadmap

## 1. Decision, scope, and fixed boundaries

This is the final **design-only** CP5 roadmap. It assimilates selected public
engineering ideas while preserving the thesis system as the sole authority for
science, history, provenance, and presentation policy. It authorizes neither
CP5 implementation nor external-code reuse.

The approved control plane remains:

```text
canonical scientific objects → append-only Ledger → cursor materialization
→ Hypothesis-Layer / Scientific-Method projections → Slide Spec
→ FigureProductionPlan → ScientificFigureSpec → governed figure pipeline
→ Layout Director → PythonPptxAssembler → PPTX/render/Professor QA
```

The following are immutable constraints:

- Ledger, not SVG, browser state, PPTX, or a preview, owns scientific truth.
- Hypothesis and Problem stay separate; failed work and historical Fishbone
  revisions remain recoverable and immutable.
- `PythonPptxAssembler` remains the one public PPTX backend.
- External source is not vendored. Any later reuse needs separate approval,
  pinned SHA, MIT notice retention, dependency closure, namespace isolation,
  and thesis-owned tests.
- Private aliases, sources, raw profiles, and private renders are out of scope.
- No CP5 checkpoint may claim production Group Meeting readiness.

## 2. Artifact ownership and non-authoritative interaction loop

| Artifact | Owner and authority | What it is not |
| --- | --- | --- |
| `ScientificFigureSpec` | ledger/materialization-derived scientific and visual requirements | an SVG drawing or user-interface state |
| Canonical Scientific SVG | editable visual authoring IR | scientific provenance database |
| `FigureOutputManifest` | source/provenance bindings, SVG hash, capability state, QA bindings | a second scientific source |
| Preview PNG | derived review artifact | canonical visual source |
| `APPROVED_FIGURE` | gated figure identity referring to approved manifest/revision | an uncontrolled duplicate asset |
| Compiled DrawingML object | derived native artifact beneath the assembler | another deck backend |
| PPTX slide / slide render | layout/assembly and visual-evidence artifacts | scientific truth |
| Master Deck | cumulative Ledger-derived presentation product | a substitute ledger |

The later review loop is deliberately non-authoritative:

```text
preview → CurrentSlideContext → immutable ReviewAction
→ source-revision request → canonical source revision → re-approval
```

`CurrentSlideContext` is transient and contains only `deck_id`, `slide_id`,
`slide_revision`, `figure_id`, `svg_object_id`, `semantic_role`,
`selection_bbox`, `updated_at`, and `source_manifest_ref`. A `ReviewAction`
contains a versioned action ID, target revision/object, reviewer, requested
change, status, approval/rejection state, and resulting source-revision ref.
Neither browser state, SVG comments, nor Slide Spec prose holds review
authority or may directly mutate Ledger, Evidence, or Professor Visual Grammar.

## 3. Minimal Scientific SVG policy

Scientific SVG is a closed visual authoring IR. Its required
rendering-neutral metadata is limited to:

- `data-thesis-svg-version` on the root;
- `data-thesis-figure-id` on the root;
- a stable `id` or `data-thesis-object-id` on addressable visual objects; and
- `data-semantic-role` on addressable visual objects.

`data-visual-class` is optional where static validation benefits from it.
Metadata must be invisible: deleting all allowed semantic attributes must not
alter painted pixels, geometry, or accessible visual text.

The following remain authoritative **outside** SVG in `ScientificFigureSpec`,
`FigureOutputManifest`, and the Ledger: Hypothesis Layer, Research Block,
Stage, Claim, Evidence, source cursor/hash, evidence role/mode, Decision,
Action, and the scientific provenance chain. They must not be copied into SVG
as a convenience field.

A later tooling-only mirror is permitted only when all four conditions hold:

1. it is labelled `non_authoritative_mirror`;
2. its manifest path is explicitly declared and validated against the matching
   `FigureOutputManifest`;
3. it is optional and rendering-neutral; and
4. no scientific validation, reuse, or decision is allowed to rely on it.

## 4. Independent readiness and capability truth

CP5 reports these independent dimensions. A blocked state in one dimension
must not be silently promoted or propagated to an unrelated dimension.

| Dimension | What may establish `pass` | Effect of native PowerPoint unavailability |
| --- | --- | --- |
| `svg_visual_fidelity_status` | SVG contract/static critic evidence | does not block SVG work |
| `render_visual_fidelity_status` | hash-bound renders and render critic evidence | does not block it |
| `professor_visual_calibration_status` | professor grammar + SVG/render benchmarks | does not block calibration |
| `drawingml_native_fidelity_status` | thesis-owned compiler/vector evidence | `blocked_environment` or `not_run` |
| `native_powerpoint_acceptance_status` | native round-trip/acceptance evidence | `blocked_environment` or `not_run` |
| `production_release_status` | all scientific, visual, native, privacy, and release gates | blocked; never inferred from SVG success |

`SVGNativeCapabilityRegistry` is two-dimensional:

| Capability state | Evidence level | Meaning |
| --- | --- | --- |
| `NATIVE_EXACT`, `NATIVE_NORMALIZED`, `VECTOR_FALLBACK`, `RASTER_FALLBACK`, `UNSUPPORTED`, `UNKNOWN` | `upstream_declared`, `source_inspected`, `thesis_synthetic_verified`, `native_powerpoint_verified` | capability state is meaningful only with its evidence level |

`UNKNOWN` is the default for unmeasured thesis behavior. Source inspection may
record an upstream-declared mapping, but cannot promote a thesis entry to
`NATIVE_EXACT` or `NATIVE_NORMALIZED`. A raster fallback is always explicit in
the manifest and capability record; silent raster fallback is forbidden.

### 4.1 Separate Scientific SVG IR support from native compilation

These are intentionally independent future contract dimensions:

| Dimension | Owner | Controlled state | Consequence |
| --- | --- | --- | --- |
| `svg_ir_support_state` | CP5-A Scientific SVG contract | `supported`, `unsupported`, `unknown_contract` | A director may author only `supported` IR features. `unsupported` or `unknown_contract` fails the canonical SVG route. |
| `native_compilation_capability_state` | CP5-B capability registry | `NATIVE_EXACT`, `NATIVE_NORMALIZED`, `VECTOR_FALLBACK`, `RASTER_FALLBACK`, `UNSUPPORTED`, `UNKNOWN` | Records only the current DrawingML/native-compilation truth and its evidence level. |

Thus `svg_ir_support_state: supported` together with
`native_compilation_capability_state: UNKNOWN` is a legal canonical SVG. It may
move through CP5-C, CP5-D/E, CP5-F, and CP5-G as SVG/render evidence. Likewise,
legal SVG plus native `UNSUPPORTED` remains a valid SVG but cannot claim native
DrawingML compilation. CP5-H, not the SVG route, owns that native consequence.

CP5-C must fail or block for a missing registry identity/record, illegal or
unknown-contract SVG feature, undeclared fallback, manifest mismatch,
scientific/provenance failure, or failed static QA. A *declared* native state of
`UNKNOWN` is not itself a static-critic failure. Native `UNSUPPORTED` likewise
does not invalidate legal canonical SVG. Neither state permits a silent raster
fallback.

## 5. CP5 dependency DAG

```text
CP5-A → CP5-B → CP5-C ─┬→ CP5-D ─┐
                        │          ├→ CP5-F → CP5-G → CP5-H → CP5-I
                        └→ CP5-E ─┘
```

CP5-F requires outputs from both director tracks. CP5-G requires CP5-F and
calibrates at SVG/render level; CP5-H follows CP5-G, consumes its approved
figures plus the CP5-B capability registry, and is the first native-fidelity
checkpoint. CP5-I requires CP5-G and CP5-H. No checkpoint requires a later
checkpoint output. `cycle_count = 0`.

| Checkpoint | Prerequisites | Input contracts | Output contracts | Blocked dependencies | Reviewer gate |
| --- | --- | --- | --- | --- | --- |
| CP5-A | CP4 freeze | CP4 Figure Plan/Spec authority | closed SVG IR + static SVG QA | none for synthetic contract tests | SVG ownership/metadata gate |
| CP5-B | CP5-A | SVG IR + synthetic vector corpus | capability registry + synthetic vectors | native verification optional | capability-truth gate |
| CP5-C | CP5-A, CP5-B | legal SVG, Spec, source/provenance bindings, registry identity/record | FigureOutputManifest + static critic + `APPROVED_FIGURE` | no render/human review required; declared native `UNKNOWN` is legal | static-gate approval |
| CP5-D | CP5-C | structured CP4 specs + style requirements | structured SVG + manifest + static approval | illegal/unknown-contract SVG feature or missing scientific input blocks route; native `UNKNOWN`/`UNSUPPORTED` does not | director-boundary gate |
| CP5-E | CP5-C | evidence-bound specs/assets | manifest/overlay/output + static approval | illegal/unknown-contract SVG feature or missing real/literature/data source blocks route; native `UNKNOWN`/`UNSUPPORTED` does not | evidence-bound gate |
| CP5-F | CP5-D, CP5-E | approved outputs and safe review provider | render critic, CurrentSlideContext, ReviewAction | image provider may block qualitative review | review-contract gate |
| CP5-G | CP5-F | canonical SVG/renders, professor grammar, sanitized profiles | A01–A18 calibration + SVG/render benchmarks | native PowerPoint is not a prerequisite | visual-calibration gate |
| CP5-H | CP5-G | CP5-B registry vectors + CP5-D/E approved output + CP5-G calibration evidence | assembler-internal DrawingML adapter + native vectors | native environment may block native fidelity | single-backend/native gate |
| CP5-I | CP5-G, CP5-H | reconstructed-template descriptors, calibrated outputs | fresh template, acceptance deck, native release evidence | native acceptance/private fixture may block release | production-release gate |

## 6. Checkpoint roadmap

### CP5-A — Scientific SVG Language

- **Scope:** thesis-owned closed Scientific SVG IR; minimal metadata; stable
  object IDs; visual-IR ownership; static and semantic SVG QA. No production
  figure rendering.
- **Prerequisites / inputs:** CP4 route/spec authority and synthetic fixtures.
- **Outputs:** versioned SVG profile, static-validator report, SVG/spec identity
  binding records.
- **RED tests:** unknown element/attribute; duplicate object ID; invalid local
  role; visible rendering dependent on metadata; SVG/spec ID mismatch;
  embedded Claim/Evidence/source-cursor provenance; undeclared external
  resource; silent raster fallback.
- **Blocked states:** invalid or unsupported IR is `FAIL`; private data is not
  an input.
- **Stop condition / gate:** all contract tests pass and metadata remains
  non-authoritative; reviewer approves IR before CP5-B.
- **Forbidden:** directors, production figures, compiler, PPTX, A01–A18
  calibration, or acceptance deck.

### CP5-B — SVG Native Capability Registry

- **Scope:** `SVGNativeCapabilityRegistry` and versioned synthetic vector
  corpus; capability/evidence-state rules.
- **Prerequisites / inputs:** CP5-A closed IR and synthetic vectors.
- **Outputs:** registry records, vector contracts, explicit unknown/fallback
  decisions.
- **RED tests:** missing registry identity/record; native claim without thesis
  evidence; source-inspected claim promoted to thesis verified; undeclared
  fallback; silent raster; and illegal SVG feature distinguished from legal SVG
  with native `UNKNOWN` or `UNSUPPORTED`.
- **Blocked states:** absent native environment keeps native state `UNKNOWN` or
  `blocked_environment`, not failure of SVG work.
- **Stop condition / gate:** every primitive has an honest registry state;
  reviewer approves evidence taxonomy before CP5-C.
- **Forbidden:** native-fidelity claims from documentation, compiler output, or
  production director work.

### CP5-C — FigureOutputManifest and Static FigureCritic

- **Scope:** canonical `FigureOutputManifest`, hash/provenance/capability
  bindings, deterministic static FigureCritic, and `APPROVED_FIGURE` contract.
  No production scientific figures yet.
- **Prerequisites / inputs:** CP5-A SVG and CP5-B registry.
- **Outputs:** validated manifest, static critic report, approved/failed/blocked
  gated figure identity.
- **RED tests:** mismatched hashes; manifest/SVG ID mismatch; illegal SVG IR
  feature; missing registry identity/record; undeclared fallback; illegal
  provenance binding; critic PASS without executed static checks; raw output
  reaching Layout; unapproved figure reaching Layout. A declared native
  `UNKNOWN` is explicitly non-failing.
- **Blocked states:** missing source/provenance, registry identity/record, or
  static evidence yields `BLOCKED`/`FAIL`; declared native `UNKNOWN` or
  `UNSUPPORTED` alone does not.
- **Stop condition / gate:** static critic exists before any director relies on
  its approval; reviewer approves pre-director gate before CP5-D/E.
- **Forbidden:** image-capable review, live editor, actual scientific figures,
  PPTX assembly.

### CP5-D — Structured Scientific SVG Directors

- **Scope:** Fishbone, mechanism, experiment schematic, fabrication/process,
  fair comparison where structurally appropriate, and vector builder.
- **Prerequisites / inputs:** CP5-C approval contract; cursor-materialized
  structured requirements; resolved style requirements.
- **Outputs:** canonical SVG, FigureOutputManifest, static critic result.
- **RED tests:** Fishbone revision/history/focus mutation; invented fabrication
  condition; mechanism absorbing fabrication chronology; experiment omitting
  controls; comparison side/scale mutation; unregistered SVG feature.
- **Blocked states:** unknown scientific conditions remain `UNKNOWN`; missing
  ordered source requirements or an illegal/unknown-contract SVG IR feature
  blocks output. Native `UNKNOWN`/`UNSUPPORTED` leaves native compilation
  unresolved for CP5-H but does not block canonical SVG production.
- **Stop condition / gate:** each output passes static critic; no slide/PPTX
  is built. Reviewer validates the directors’ scientific boundaries.
- **Forbidden:** plot/photo/literature routes, concept generation, native
  compiler, A01–A18 calibration.

### CP5-E — Evidence-bound Visual Directors

- **Scope:** scientific plot, photo annotation, literature figure, image
  matrix, and strictly non-evidence concept illustration.
- **Prerequisites / inputs:** CP5-C plus canonical data/real evidence/literature
  source selected by the CP4 route.
- **Outputs:** typed output manifests; vector plot outputs; real source plus
  overlay; literature extraction provenance; static critic result.
- **RED tests:** generated concept as Observation; plot without reproducible
  canonical data/vector; photo identity replacement; literature without source
  extraction/citation; image-matrix order loss; concept claim support.
- **Blocked states:** missing real/literature/data source or an
  illegal/unknown-contract SVG IR feature blocks the visual; concept is never
  a substitute for evidence. Native `UNKNOWN`/`UNSUPPORTED` does not block a
  legal SVG route and cannot trigger an undeclared raster fallback.
- **Stop condition / gate:** evidence identity and static critic evidence pass;
  reviewer validates empirical/literature protection.
- **Forbidden:** generative recreation of evidence, live review, compiler,
  template/deck creation.

### CP5-F — Render Review and Deictic Human Review

- **Scope:** render-derived/image-capable FigureCritic, `CurrentSlideContext`,
  immutable `ReviewAction`, temporary visual overrides, and local review loop.
- **Prerequisites / inputs:** CP5-D/E approved figure outputs and an authorized
  image-review provider where qualitative review is requested.
- **Outputs:** four independent status-bearing outputs: `static_figure_critic_status`
  (the CP5-C evidence it consumes), `render_critic_status`,
  `image_capable_qualitative_review_status`, and `human_review_status`; plus
  hash-bound render critic reports, contexts, review actions, and
  source-revision requests.
- **RED tests:** clipping/overlap/legibility render mutation; stale context;
  object not in manifest; browser/comment direct mutation; private-unauthorized
  provider; metadata-only qualitative PASS; temporary override counted as
  calibration.
- **Blocked states:** an unavailable or unauthorized image-capable provider
  yields `image_capable_qualitative_review_status: blocked_visual_review` only.
  It does not change static-critic, SVG-validity, render-critic, native, or
  native-PowerPoint status unless a declared check explicitly depends on it.
  Human review may independently be `not_run` or blocked.
- **Stop condition / gate:** every change is traceable to a source revision;
  reviewer approves review interaction before CP5-G.
- **Forbidden:** direct Ledger/Evidence/grammar mutation; native acceptance;
  production deck.

### CP5-G — A01–A18 Visual Calibration

- **Scope:** A01–A18 geometry/style calibration and professor SVG/render
  benchmarks using canonical SVG, approved directors, professor grammar, and
  sanitized template/body evidence.
- **Prerequisites / inputs:** CP5-F SVG/render evidence and CP2/CP3 sanitized
  artifacts. Image-capable qualitative review is consumed when available, not
  a prerequisite for geometry/composition calibration.
- **Outputs:** calibration records, SVG/render benchmark metrics, visual
  readiness facts.
- **RED tests:** uncalibrated archetype marked calibrated; body source
  contaminating shell; absent evidence changed to zero; historical cursor loss;
  fidelity PASS without render/human evidence.
- **Blocked states:** weak descriptor evidence stays provisional/insufficient;
  native PowerPoint may stay blocked without blocking this checkpoint. A
  blocked qualitative review permits authorized SVG/render, geometry, and
  composition calibration but prevents a professor *qualitative* visual
  acceptance claim.
- **Stop condition / gate:** visual-calibration/benchmark evidence is honest;
  reviewer authorizes CP5-H independently.
- **Forbidden:** native-fidelity PASS, native template reconstruction, PPTX
  release, Group Meeting readiness.

### CP5-H — DrawingML Compiler Integration

- **Scope:** a compiler adapter only inside `PythonPptxAssembler`, driven by
  CP5-B test vectors and approved figures; decide reimplementation, minimal
  MIT reuse, or thesis-native compiler only now.
- **Prerequisites / inputs:** CP5-B registry, CP5-C approvals, native test
  vectors, and a native environment when claiming native fidelity.
- **Outputs:** adapter contract, compilation records, OpenXML relationship
  audit, capability evidence.
- **RED tests:** unapproved figure reaches Layout; undeclared raster fallback;
  missing slide relationship; second exporter invocation; unsupported feature
  claimed native exact.
- **Blocked states:** no native environment means native fidelity/PowerPoint
  acceptance is `blocked_environment`; canonical SVG remains valid.
- **Stop condition / gate:** agreed vector/native checks pass before CP5-I.
- **Forbidden:** public second backend, unauthorised external reuse, production
  release claim.

### CP5-I — Native Template Reconstruction and Acceptance Deck

- **Scope:** fresh sanitized native template, Ledger-derived acceptance deck,
  structural/render/Professor QA, native PowerPoint round-trip, and production
  release decision.
- **Prerequisites / inputs:** CP5-G calibration and CP5-H native adapter
  evidence; existing privacy/provider gates.
- **Outputs:** reconstruction manifest, package privacy proof, acceptance PPTX,
  renders/montages, native acceptance and release facts.
- **RED tests:** private package part reuse; template copied rather than fresh;
  wrong master/layout; failed FigureCritic bypass; failed experiment/history
  disappearance; native release from blocked environment.
- **Blocked states:** private fixture, qualified visual reviewer, or native
  PowerPoint may each independently block their relevant gate and release.
- **Stop condition / gate:** only a passing, reviewer-accepted release package
  can support a Group Meeting readiness decision.
- **Forbidden:** self-certification of production readiness.

## 7. External-technique disposition

PPT Master remains a reference for constrained SVG, static checking,
capability taxonomy, template topology, and later compiler test vectors. Its
source inspection is not thesis-native verification. All B01–B10 remain
`blocked_environment`; no benchmark claim follows from upstream documentation
or tests.

At pinned open-slide commit `90bb86172f7e390c29bbf2f33067c7b05c646b70`,
`packages/core/src/app/lib/export-pptx.ts` renders React slides through
`html-to-image`, captures page PNGs, and inserts each PNG as the PPTX slide
surface. It is therefore **raster/image-slide PPTX export**, not native editable
PowerPoint authoring. It remains rejected as the canonical thesis backend.
Its CurrentSlideContext, element-selection, comment/review-loop, and live
preview interaction concepts remain ADOPT/ADAPT candidates for CP5-F only.

The current decision totals remain reconciled: **ADOPT 6, ADAPT 8, REJECT 5,
DEFER 5**. This roadmap changes sequencing and evidence interpretation, not
those technique dispositions.

## 8. Architecture answers and status

1. Scientific SVG is a thesis-owned closed visual IR, not scientific state.
2. Static FigureCritic exists at CP5-C; render/image-capable critic follows at
   CP5-F; human preference is a separate ReviewAction path.
3. SVG/render professor calibration at CP5-G does not require native PowerPoint.
4. Native compiler work and native fidelity belong at CP5-H; release belongs at
   CP5-I.
5. No professor or scientific authority is weakened by external presentation
   techniques; high-information-density scientific pages remain acceptable when
   hierarchy is clear.

```yaml
codex_report:
  phase: PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL
  status: awaiting_external_architecture_review
  implementation_authorized: false
  cp5_dependency_cycle_count: 0
  private_access_counters: [0, 0, 0]
  next_action_requested: REVIEW
```
