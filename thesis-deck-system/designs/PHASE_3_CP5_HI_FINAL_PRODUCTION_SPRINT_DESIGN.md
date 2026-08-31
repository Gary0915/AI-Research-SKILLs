# Phase 3 CP5-H/I Final Production Sprint Design

## 1. Status and purpose

This design authorizes the final integrated Phase 3 production sprint after the
external approval of CP5-A through CP5-G at commit
`ec9266bcc2497b7a486fe31465e33841f89c211d`.

The sprint is intentionally large and has one external review boundary only:

```text
H0 backend/native preflight
→ H1 Scientific SVG → native-figure compilation plan
→ H2 PythonPptxAssembler integration + native-vector benchmarks
→ I0 fresh sanitized native-template reconstruction
→ I1 Ledger-derived acceptance deck
→ I2 structural/render/native/release QA
→ one external review
```

The purpose is not merely to create a `.pptx`. It is to prove that the complete
scientific presentation control plane can produce a fresh, privacy-safe,
professor-calibrated PowerPoint package while preserving scientific history,
figure approval, provenance, and the single-backend architecture.

## 2. Approved starting state

The following are fixed inputs and are not reopened for redesign during this
sprint:

- CP5-A Scientific SVG language: done.
- CP5-B SVG native-capability registry: done.
- CP5-C FigureOutputManifest/static approval trust chain: done.
- CP5-D structured directors: done.
- CP5-E evidence-bound directors: done with truthful source-blocked routes.
- CP5-F render/review architecture: done; host renderer may remain
  `blocked_environment`, image-capable review may remain `blocked_visual_review`.
- CP5-G A01–A18/figure-family calibration: done with provisional and
  insufficient-evidence states preserved.
- definitive prior regression: `461 passed / 0 failed`.
- prior candidate-state hash:
  `2c846703807a02c1b4b97b8adfb4dbff5e56dd90ff3ef35febe11bd534d30762`.
- prior privacy state: repository/staged findings `0 / 0`, one approved
  historical exception, private alias/source/render counters `0 / 0 / 0`.

CP5-H/I may consume only committed sanitized/public/synthetic artifacts unless a
new private authorization is explicitly supplied. No such authorization is part
of this design.

## 3. Immutable architecture boundaries

The approved control plane remains:

```text
canonical scientific objects
→ append-only Ledger
→ cursor materialization
→ Hypothesis-Layer / Scientific-Method projections
→ Slide Specs
→ FigureProductionPlan
→ ScientificFigureSpec
→ canonical FigureOutputManifest + Static FigureCritic
→ ApprovedFigureHandle
→ Layout Director
→ PythonPptxAssembler
→ PPTX / render / Professor QA
```

The following are hard invariants:

1. `PythonPptxAssembler` is the sole public PPTX backend and the sole component
   permitted to assemble the acceptance deck.
2. The CP5-H compiler is an internal adapter. It may parse SVG and emit an
   immutable native-figure compilation plan or adapter-owned DrawingML
   fragments, but it may not save or export a PPTX independently.
3. Scientific SVG remains the canonical editable figure IR. Native PowerPoint
   objects are derived representations, not a new scientific or figure truth.
4. `ApprovedFigureHandle`, not an arbitrary SVG/path/dictionary, is the Layout
   handoff authority.
5. No silent raster fallback. Any SVG/vector/raster fallback is explicit,
   feature/figure bound, and reported.
6. No external compiler source is copied, vendored, or reused in this sprint.
   PPT Master/open-slide remain reference material only. The default CP5-H
   implementation is thesis-native.
7. Private PPTX files are not opened, copied, patched, rendered, or used as a
   package base.
8. Production Group Meeting readiness is an independent release decision and
   is never inferred from the existence of a PPTX.

## 4. Existing backend reality and H integration boundary

The current `PythonPptxAssembler` already owns:

- template copy/open/save through `python-pptx`;
- semantic layout-role resolution;
- governed slide placement;
- editable text generation;
- image placement;
- speaker notes/source refs;
- exact SVG-to-slide/picture relationship attachment for vector ownership;
- final package save.

CP5-H must extend this path rather than replace it. The recommended structure
is:

```text
ApprovedFigureHandle
+ canonical Scientific SVG
+ CP5-B registry
        ↓
ScientificSvgNativeCompiler
        ↓
NativeFigureCompilationPlan
        ↓
PythonPptxAssembler.add_compiled_figure(...)
        ↓
python-pptx native shapes / narrowly scoped assembler-owned OOXML
        ↓
PPTX
```

`ScientificSvgNativeCompiler` must have no `save_pptx`, `export_pptx`, or
presentation-package writer API.

## 5. CP5-H compilation model

### 5.1 Separate compilation outcome from native-fidelity truth

Do not misuse the CP5-B capability registry. A compiler successfully emitting
DrawingML is not by itself `native_powerpoint_verified`.

Every compiled figure/object records a compilation outcome such as:

- `DRAWINGML_EMITTED`;
- `SVG_VECTOR_FALLBACK`;
- `RASTER_FALLBACK_EXPLICIT` only if already permitted by route/capability;
- `BLOCKED_UNSUPPORTED`;
- `BLOCKED_UNKNOWN_MAPPING`.

The independent CP5-B native capability/evidence state remains authoritative.
`NATIVE_EXACT` or `NATIVE_NORMALIZED` may be claimed only under the evidence
rule already encoded by CP5-B, including native PowerPoint verification where
required.

### 5.2 Native compilation plan

A closed `NativeFigureCompilationPlan` must bind at least:

- plan ID/version;
- figure ID/revision;
- ApprovedFigureHandle identity/hash inputs;
- canonical SVG hash/profile version;
- CP5-B registry ID/version/hash;
- source viewBox and target placement box;
- deterministic coordinate transform;
- ordered native objects;
- stable source SVG object IDs and semantic roles;
- object type and geometry;
- text/runs and CJK/Latin content where applicable;
- fill/stroke/font/line/arrow properties;
- group/parent relation;
- source feature IDs;
- per-object compilation outcome;
- explicit fallback records;
- compilation QA status and plan hash.

The plan is derived visual data and cannot contain Claim/Evidence/Ledger truth.

### 5.3 Minimum feature coverage

The compiler must define an explicit mapping or explicit fallback/block state for
all CP5-B feature IDs, and must natively exercise at least the feature subset
used by the approved CP5-D/E acceptance figures where technically feasible:

- root/viewBox and coordinate normalization;
- `g`;
- `rect`, `circle`, `ellipse`;
- `line`, `polyline`, `polygon`;
- supported simple `path` subset;
- `text` and `tspan`, including mixed CJK/Latin text;
- local marker/arrow semantics;
- image placement for approved image-matrix/source routes;
- translate/scale/rotate/matrix transforms by deterministic flattening or
  declared normalization;
- stroke width/cap/join/dash;
- fill/stroke opacity;
- text anchor/baseline/font attributes;
- same-document references.

`clipPath`, complex paths, or other unimplemented behavior must remain explicit
fallback/block states. They may not disappear silently.

### 5.4 Shape identity and editability

Native PowerPoint objects must retain stable non-scientific identity, for
example through a controlled shape-name convention such as:

`tds-fig:<figure-id>/<svg-object-id>/<semantic-role>`.

The generated native shape must remain editable where the compilation outcome
claims native emission. Text must remain real PowerPoint text, not outlines or
rasterized labels.

### 5.5 OOXML use

Use public `python-pptx` APIs first. Narrowly scoped OOXML edits are permitted
inside the assembler-owned adapter for properties not exposed by python-pptx
(e.g. certain arrowhead/group/native metadata details), provided they are:

- deterministic;
- namespace/schema constrained;
- covered by structural tests;
- unable to save a deck independently;
- audited after package save.

## 6. CP5-H benchmark strategy

CP5-H uses two benchmark layers.

### 6.1 Primitive/native-vector vectors

Consume the CP5-B synthetic vector corpus and create controlled test figures for
all compiler mappings. For each vector, persist:

- source SVG/profile/hash;
- used feature IDs;
- compilation plan/hash;
- emitted native object count/types;
- fallback count/types;
- package slide/object relationships;
- source-object → PowerPoint-object mapping;
- text-preservation facts;
- geometry/style comparison metrics;
- native PowerPoint evidence status.

### 6.2 Real system figure families

Compile approved committed representatives from at least:

- Fishbone;
- mechanism;
- experiment schematic;
- fabrication/process;
- fair comparison;
- scientific plot;
- image matrix;
- concept illustration.

Photo/literature routes remain source-blocked unless a permitted committed
source already exists; they are not replaced by fake evidence.

## 7. Fresh sanitized native-template reconstruction

### 7.1 Fresh-lineage rule

The final template must be generated from committed sanitized descriptors and
independently created primitives. A private PPTX and the older Phase 2
acceptance PPTX may never be used as the output package base.

Allowed inputs include:

- `professor-template-resolved.json`;
- sanitized shell/body descriptors;
- VSP003 and style-category resolution records;
- A01–A18 calibration records;
- Fishbone calibration;
- committed generic/synthetic builder assets;
- program code under the single backend.

No private OOXML bytes, relationships, notes, media, custom XML, document
properties, or package parts may be copied.

### 7.2 Template builder ownership

Template reconstruction is a private internal capability of the approved PPTX
backend subsystem, e.g. `SanitizedNativeTemplateBuilder` invoked through
`PythonPptxAssembler` or its template subsystem. It is not a second general
presentation exporter.

A narrowly scoped fresh OOXML package-part builder is permitted to create
Master/Layout/theme parts that `python-pptx` cannot author directly. It may only
create the sanitized template input; it may not assemble scientific slides or
bypass `PythonPptxAssembler`.

### 7.3 Measured topology target

Reconstruction must consume the measured sanitized topology rather than invent a
single generic content layout. Current resolved evidence includes a 16:9 canvas
and sanitized Master/Layout topology. The builder must attempt the topology and
semantic roles supported by sanitized evidence, including at least:

- formal cover/divider role;
- academic content role;
- Fishbone role;
- comparison/result role;
- summary/decision role;
- recurring footer/page-number regions where supported.

If exact measured topology cannot be reconstructed, report the exact unsupported
portion and downgrade reconstruction status. Do not claim exact professor
fidelity from a generic one-layout template.

### 7.4 Reconstruction manifest

Every ZIP part in the reconstructed template and acceptance deck must have a
manifest classification such as:

- `builder_required`;
- `reconstructed_shell`;
- `generated_slide`;
- `generated_notes`;
- `generated_media`;
- `generated_metadata`.

Forbidden families include copied private media, comments/people, custom XML,
embeddings/OLE, macros, external private links, private chart caches/workbooks,
private thumbnails, and orphan/unreferenced parts.

The final package privacy proof must verify every package member and relationship
against the manifest and show that all construction inputs were committed
sanitized/public/synthetic sources. Raw private-part hash comparison is not
required in this unauthorized-private session; fresh lineage is established by
construction/input closure, not by reopening private exemplars.

## 8. CP5-I acceptance-deck story

### 8.1 Scientific source

The acceptance deck must be derived from the existing committed Phase 2
hypothesis-layered synthetic scientific state and Slide Specs. The older Phase 2
PPTX may be inspected structurally as a regression artifact but may not be used
as a binary/package base.

The committed Phase 2 acceptance story contains H001 and H002. It does **not**
contain H003. CP5-I must therefore preserve H001→H002 and must not invent an
H003 merely to satisfy an old planning shorthand.

### 8.2 Acceptance-deck size and coverage

Build one fresh formal cover from deck metadata plus the existing nineteen
Phase 2 source-derived slides, for an expected acceptance deck of 20 slides
unless a source-driven split rule legitimately adds slides.

The 19 source-derived slides must preserve their semantic order, scientific
bindings, hypothesis-layer history, source cursors, Fishbone revision/focus,
failed/partial history, decisions, actions, and notes/citations.

The deck must exercise, where supported by the existing Slide Specs:

- progress/previous commitments;
- H001 Hypothesis;
- H001 Problem;
- H001 Fishbone/history locator;
- Observation/Problem evidence page;
- literature/mechanism role without fabricated literature evidence;
- experiment schematic/design;
- result/scientific plot;
- integrated discussion;
- layer summary/decision;
- H001→H002 transition;
- H002 Hypothesis;
- H002 Problem;
- H002 Fishbone/history locator;
- H002 observation/problem;
- experiment/result comparison;
- final H002 summary/decision.

The cover is presentation metadata only and cannot introduce scientific claims.

### 8.3 Approved figures only

Every figure slot that uses a CP5 figure must resolve through:

`ApprovedFigureHandle → NativeFigureCompilationPlan or explicit SVG fallback → Layout → PythonPptxAssembler`.

No raw SVG, persisted approval JSON, or unapproved asset may bypass the gate.

### 8.4 Archetype/layout coverage

Map source slide semantic roles to the existing canonical A01–A18 archetypes
where the repository already defines such mappings. Report:

- archetypes exercised;
- archetypes not exercised by this source deck;
- measured/provisional/insufficient calibration used per slide;
- split-rule events;
- fallback geometry/layout roles.

Do not manufacture slides solely to claim 18/18 deck coverage. Library
calibration coverage and acceptance-deck coverage remain separate dimensions.

## 9. QA and acceptance dimensions

The sprint reports independent status dimensions rather than one aggregate
visual PASS:

1. `single_backend_integrity_status`;
2. `drawingml_compiler_contract_status`;
3. `drawingml_structural_compilation_status`;
4. `drawingml_native_fidelity_status`;
5. `fresh_template_lineage_status`;
6. `template_reconstruction_status`;
7. `acceptance_story_preservation_status`;
8. `approved_figure_handoff_status`;
9. `pptx_package_structural_status`;
10. `render_visual_status`;
11. `professor_structural_fidelity_status`;
12. `image_capable_qualitative_review_status`;
13. `native_powerpoint_acceptance_status`;
14. `production_release_status`;
15. `production_group_meeting_ready`.

A blocked native PowerPoint environment does not invalidate the SVG compiler,
template, or deck package. A blocked qualitative visual review does not erase
structural metrics. Conversely, neither blocked dimension may be silently
reported as PASS.

## 10. Native PowerPoint acceptance

Probe native PowerPoint only against generated sanitized/synthetic outputs.
Never open a private exemplar in this gate.

If PowerPoint is available, native acceptance should execute a controlled
open/save/reopen round-trip and verify where feasible:

- file opens through native PowerPoint automation;
- no slide-count loss;
- Master/Layout references remain valid;
- shape/object counts remain consistent within declared normalization;
- native compiled text remains text;
- mixed CJK/Latin text survives;
- stable shape names/semantic identities survive where expected;
- generated notes remain present;
- save/reopen does not corrupt relationships;
- compiler/native-fallback records remain consistent with the reopened package;
- generated slide renders can be produced for visual QA when supported.

If PowerPoint is unavailable or automation cannot be safely proven:
`native_powerpoint_acceptance_status = blocked_environment`.

Do not substitute LibreOffice or package validity for native PowerPoint
acceptance. LibreOffice may provide an independent compatibility/render signal
only.

## 11. Render and image-capable review

Use the existing CP5-F renderer/review architecture.

- If a deterministic host renderer is available, render every acceptance slide
  and generate a full-deck montage plus targeted difficult-slide montages.
- Every render is hash-bound to the exact PPTX/slide/build identity.
- Run render QA for clipping, overflow, margins, blank content, and geometry.
- If an authorized image-capable provider is available for generated
  non-private renders, review **every acceptance slide**, not merely a sample,
  and bind each review to the render hash.
- If unavailable, persist `blocked_visual_review` and do not claim professor
  qualitative acceptance.

## 12. Reconstruction and professor metrics

Compare the fresh generated template/deck only against committed sanitized
professor descriptors and G1 calibration facts. No private render comparison is
allowed in this sprint.

Required metric families where evidence exists:

- canvas and title geometry;
- footer/page-number regions;
- safe bounds and margins;
- typography hierarchy;
- body/figure split;
- panel/matrix/comparison geometry;
- connector/line/style tokens;
- Fishbone placement/spacing/focus;
- figure/text dominance;
- whitespace/density;
- archetype-specific calibrated constraints.

Provisional/insufficient evidence remains explicitly provisional/insufficient.
A numeric match to a provisional token does not create professor qualitative
acceptance.

## 13. Release decision

The final release decision is fail-honest.

`acceptance_deck_build_status` may PASS even when release is blocked.

`production_release_status` and `production_group_meeting_ready` may become
PASS/true only if every release-required gate in the committed release-gate
matrix passes. In particular, no release claim may be inferred from:

- PPTX creation alone;
- OOXML structural validity alone;
- SVG/render calibration alone;
- deterministic test renderer evidence;
- blocked native PowerPoint;
- blocked qualitative review;
- provisional professor visual evidence when the gate requires resolved
  fidelity.

If release remains blocked, CP5-I still completes by producing a truthful
release-gap report identifying the exact remaining blockers and the minimum
next evidence required.

## 14. Test and execution strategy

Use internal gate commits without external reviewer stops:

- H0: backend/capability preflight and contracts;
- H1: compiler + native plan;
- H2: assembler integration + native benchmark deck;
- I0: fresh sanitized native template;
- I1: acceptance deck;
- I2: QA/native/release facts.

Run focused RED→GREEN tests per internal gate. Do not run the entire repository
regression after each gate.

After I2 and all cross-gate acceptance checks are green, freeze one final
candidate, capture its component hash, and run one definitive disposable-worktree
full regression. Long tests must use durable pre-hash/command/stdout/stderr/exit
code/post-hash/completion evidence.

Ordinary in-scope compiler, OOXML, layout, rendering, or QA defects may be
corrected autonomously in bounded correction cycles. Stop only for a genuine
scope/private/single-backend contradiction or an environment gate that the
contract says must block rather than be bypassed.

## 15. Final deliverables

The sprint should produce versioned, schema-backed artifacts for at least:

- native compiler capability/mapping manifest;
- NativeFigureCompilationPlan corpus;
- DrawingML/native compilation audit;
- backend-uniqueness audit;
- native-vector benchmark PPTX and structural audit;
- sanitized native template and template profile;
- template reconstruction manifest and privacy/fresh-lineage proof;
- acceptance Slide Specs/deck manifest;
- final acceptance PPTX;
- render manifests/montages when available;
- native PowerPoint acceptance evidence or truthful blocked record;
- professor reconstruction metrics;
- release-gate facts;
- release-gap report when blocked;
- final Phase 3 CP5-H/I implementation report.

The final external reviewer receives one coherent package and decides whether
Phase 3 can be closed and whether production Group Meeting readiness can be
claimed.