# Task — Phase 3 External Architecture Revision

## Authorization

Revise the external-presentation reconnaissance/proposal only. No CP5 implementation is authorized.

Authoritative review: `thesis-deck-system/reviews/PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_REVIEW.md`.

## Required changes

### EAR-1 — Remove CP5 dependency cycle

Revise the CP5 sequence so no director checkpoint requires FigureCritic approval before the FigureCritic implementation/gate exists.

Required conceptual ordering:

1. Scientific SVG contract/static QA;
2. capability registry/test vectors;
3. FigureOutputManifest + deterministic/static FigureCritic approval contract;
4. production directors;
5. render-derived/live review;
6. professor visual calibration;
7. native DrawingML integration;
8. final native/template/deck release.

Equivalent ordering is allowed only if acyclic and explicitly justified.

Persist a dependency DAG/table showing every checkpoint prerequisite and proving zero cycles.

### EAR-2 — Minimize semantic SVG metadata

Revise the SVG metadata recommendation.

Mandatory SVG metadata should be limited to visual/tooling identity, such as:

- schema/profile version;
- figure ID;
- stable object ID;
- local semantic role;
- optional visual class.

Hypothesis/Block/Stage/Claim/Evidence/source-cursor/source-hash/evidence-mode bindings remain authoritative outside SVG.

If any research binding is mirrored for tooling, label it `non_authoritative_mirror`, require manifest validation, and prohibit using it as scientific truth.

### EAR-3 — Split visual and native readiness

Define independent dimensions:

- `svg_visual_fidelity_status`;
- `render_visual_fidelity_status`;
- `professor_visual_calibration_status`;
- `drawingml_native_fidelity_status`;
- `native_powerpoint_acceptance_status`;
- `production_release_status`.

Native PowerPoint being blocked must not prevent SVG/render-level director work or A01–A18 visual calibration.

### EAR-4 — Capability evidence states

Because B01–B10 are blocked, define a capability evidence model that distinguishes:

- upstream_declared;
- source_inspected;
- thesis_synthetic_verified;
- native_powerpoint_verified.

Registry capability states may include:

- NATIVE_EXACT;
- NATIVE_NORMALIZED;
- VECTOR_FALLBACK;
- RASTER_FALLBACK;
- UNSUPPORTED;
- UNKNOWN.

But without thesis execution evidence, no entry may be promoted to thesis-verified `NATIVE_EXACT`/`NATIVE_NORMALIZED` merely from upstream docs/source.

### EAR-5 — Classify open-slide PPTX correctly

At pinned commit `90bb86172f7e390c29bbf2f33067c7b05c646b70`, record that `packages/core/src/app/lib/export-pptx.ts` uses `html-to-image` capture and inserts per-slide PNG images into PPTX.

Classify it explicitly as raster/image-slide PPTX export, unsuitable as the canonical editable thesis backend.

Keep its CurrentSlideContext/selection/comment interaction ideas as useful.

### EAR-6 — Revise CP5 sequence

Produce a final recommended sequence, preferably equivalent to:

- CP5-A — Scientific SVG IR + minimal semantic contract + static QA;
- CP5-B — SVGNativeCapabilityRegistry + synthetic test-vector corpus;
- CP5-C — FigureOutputManifest + static/deterministic FigureCritic gate;
- CP5-D — structured directors: Fishbone, mechanism, experiment, fabrication, comparison where appropriate;
- CP5-E — evidence visual directors: plot, photo, literature, image matrix, plus strict concept non-evidence boundary;
- CP5-F — render/image-capable FigureCritic + CurrentSlideContext + ReviewAction/live review;
- CP5-G — A01–A18 calibration + professor SVG/render benchmarks;
- CP5-H — DrawingML compiler adapter under PythonPptxAssembler + native vectors;
- CP5-I — template reconstruction + acceptance deck + native PowerPoint/release gate.

You may improve the decomposition, but explain every deviation.

For every checkpoint include:

- scope;
- prerequisites;
- inputs;
- outputs/artifacts;
- RED tests;
- blocked states;
- stop condition;
- reviewer gate;
- explicitly forbidden work.

## Files allowed to change

Only:

- `thesis-deck-system/research/PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_RECONNAISSANCE.md`
- `thesis-deck-system/designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md`
- `thesis-deck-system/artifacts/phase3/external-repo-provenance.json` if needed for the open-slide export clarification/evidence
- `thesis-deck-system/artifacts/phase3/external-technique-assimilation-matrix.json` if needed for corrected classification/target phase

Do not modify the reviewer file or this task.

## Prohibited

Do not:

- implement CP5 code;
- add Scientific SVG schemas yet;
- add Skills;
- vendor PPT Master/open-slide code;
- modify CP1–CP4 implementation;
- access private exemplars;
- generate thesis figures;
- generate PPTX;
- calibrate A01–A18.

## Validation

Before delivery:

1. CP4 freeze remains unchanged;
2. dependency graph has zero cycles;
3. semantic SVG policy does not duplicate canonical scientific provenance;
4. native gate no longer blocks SVG/render visual calibration;
5. B01–B10 remain honestly blocked unless actually rerun;
6. open-slide PPTX export classification is source-backed;
7. ADOPT/ADAPT/REJECT/DEFER totals are reconciled after any matrix changes;
8. JSON validates;
9. privacy counters remain 0/0/0;
10. repository/staged privacy scan passes;
11. absolute private-path scan passes;
12. `git diff --check` passes;
13. only allowed files changed;
14. commit and push;
15. remote SHA/tree/blob verification.

## Delivery

Return:

repository:
branch:
commit SHA:
pushed:
remote verification:

files added:
files modified:
files deleted:

EAR-1 through EAR-6 traceability:

CP5 dependency DAG status/cycle count:
minimal semantic SVG decision:
scientific-provenance-in-SVG policy:
visual-vs-native readiness split:
capability evidence model summary:
open-slide PPTX classification:
revised CP5 checkpoint sequence:
ADOPT/ADAPT/REJECT/DEFER counts:
private alias/source/render counters:
known failures:
blocked conditions:
unresolved questions:

Only after push and remote verification write:

`READY_FOR_EXTERNAL_ARCHITECTURE_REVIEW: yes`

Then stop. Do not begin CP5-A.