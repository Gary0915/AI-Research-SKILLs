# TASK — Phase 3 CP5-H/I Final Production Sprint

## Authorization

**PRE-AUTHORIZED FOR CONTINUOUS IMPLEMENTATION.**

This is the final integrated Phase 3 production sprint. Codex is authorized to
implement H0→H1→H2→I0→I1→I2 continuously without stopping for external review
between passing internal gates.

The reviewed implementation baseline is:

`ec9266bcc2497b7a486fe31465e33841f89c211d`

Reviewer-prepared sprint authority was added after that baseline. Before
implementation Codex must synchronize to the current remote branch and read the
new design, baseline, and release-gate matrix completely.

## 1. Normative inputs

Read completely, in this priority order:

1. `thesis-deck-system/TASK_PHASE_3_CP5_HI_FINAL_PRODUCTION_SPRINT.md`
2. `thesis-deck-system/designs/PHASE_3_CP5_HI_FINAL_PRODUCTION_SPRINT_DESIGN.md`
3. `thesis-deck-system/artifacts/phase3/cp5-hi-final-production-sprint-baseline.json`
4. `thesis-deck-system/artifacts/phase3/cp5-hi-release-gate-matrix.json`
5. `thesis-deck-system/designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md`
6. `thesis-deck-system/designs/PHASE_3_VISUAL_FIDELITY_DESIGN.md`
7. `thesis-deck-system/reports/PHASE_3_CP5_C1_D1_E1_F1_G1_CLOSURE_IMPLEMENTATION_REPORT.md`
8. `thesis-deck-system/REVIEW_PROTOCOL.md`
9. current `packages/thesis-deck-system/src/thesis_deck_system/pptx.py`
10. current template/profile/layout/slide/build sources and owning tests
11. CP5-A SVG profile/validator
12. CP5-B registry/vectors
13. CP5-C FigureOutputManifest/static critic/approval implementation
14. CP5-D/E approved outputs
15. CP5-F renderer/review contracts
16. CP5-G archetype/family/Fishbone calibration
17. `professor-template-resolved.json`, VSP003, sanitized shell/body/profile artifacts
18. Phase 2 `MASTER-PHASE2.manifest.json`, `slide-specs.json`, materialized/Ledger/hypothesis/Fishbone artifacts needed to reproduce the acceptance story.

Do not rely on this task alone when an owning contract already exists.

## 2. Continuous execution model

Internal sequence:

```text
H0 backend/native preflight
→ H1 native compiler
→ H2 assembler integration + native benchmarks
→ I0 sanitized native-template reconstruction
→ I1 Ledger-derived acceptance deck
→ I2 QA/native/release decision
→ definitive full regression
→ privacy
→ final report
→ push/remote verify
→ one external review
```

Do not stop after H0/H1/H2/I0/I1 merely because reviewer approval is absent.
Internal checkpoint commits are recovery boundaries, not review boundaries.

Stop early only for a true blocker that cannot be truthfully represented by an
already defined blocked state and whose solution would require violating a hard
scope boundary.

## 3. Workspace and recovery preflight

Before modification:

- fetch/synchronize `origin/codex/thesis-deck-system`;
- verify the reviewed closure SHA is in ancestry;
- run `git rev-parse HEAD`, `git status --short`, `git diff --name-status`,
  `git diff --check`, and a short commit log;
- classify all dirty paths.

Do not broad reset/clean unrelated user content. If unrelated user-authored
changes exist, stop with exact repository-relative paths.

All long tests and native/render operations use durable local-only evidence:

`PRE hash → exact command → stdout → stderr → numeric exit → POST hash → completion marker`.

On session interruption, inspect durable evidence first. Do not rerun completed
expensive work solely because the interactive session ended.

## 4. H0 — backend and native-capability preflight

### H0-1 Single-backend audit

Machine-audit source and call graph so that:

- `PythonPptxAssembler` remains the only public acceptance-deck PPTX writer;
- compiler objects expose no independent `save_pptx`/`export_pptx` path;
- template reconstruction cannot assemble scientific slides independently;
- no external second exporter is invoked.

Persist a backend-uniqueness artifact with source paths, owning APIs, call edges,
and zero bypasses.

### H0-2 Existing backend characterization

Record the existing assembler capabilities actually present at runtime:

- template-based assembly;
- semantic layout-role identity checks;
- governed text/asset placement;
- notes/source refs;
- SVG package relationship bridge;
- structural audit entry points.

Use this as the H integration boundary. Do not rewrite the assembler wholesale.

### H0-3 PowerPoint/native environment probe

Probe, without accessing private files:

- operating system/runtime;
- `python-pptx` version;
- native Microsoft PowerPoint automation availability;
- deterministic SVG/PPTX rendering compatibility tools already installed;
- any required OOXML parser/runtime.

Do not install/download external dependencies silently.

PowerPoint unavailable is `blocked_environment`, not a reason to stop H0.

### H0-4 Compiler decision

Default implementation decision: **thesis-native compiler**.

Do not copy/vend PPT Master/open-slide or another repository. External projects
remain architecture references only. Any source-code reuse would require a
separate authorization and is not authorized by this task.

### H0-5 Contracts

Add closed versioned schemas/contracts for at least:

- native figure compilation plan;
- native compilation object/result;
- compiler capability/mapping manifest;
- backend uniqueness audit;
- native-vector benchmark;
- H execution evidence and QA.

Write RED tests before implementation.

Checkpoint commit H0 and continue.

## 5. H1 — Scientific SVG to native-figure compiler

Implement an internal adapter equivalent to `ScientificSvgNativeCompiler`.

### H1-1 Required input authority

Compiler input must be bound to:

- reverified `ApprovedFigureHandle`;
- canonical Scientific SVG and hash;
- CP5-A profile/version;
- CP5-B registry ID/version/hash;
- target figure placement box;
- compiler version.

A raw SVG path or persisted approval dictionary alone must be rejected.

### H1-2 Compiler output

Compiler returns an immutable `NativeFigureCompilationPlan`. It does **not**
write a PPTX.

The plan binds:

- figure/revision;
- SVG/viewBox/hash;
- registry identity;
- deterministic source→target coordinate transform;
- ordered object plan;
- stable SVG object ID and semantic role;
- native shape kind;
- geometry;
- text/run content;
- fill/stroke/font/line/arrow properties;
- group/parent relation;
- used feature IDs;
- compilation outcome per object/subtree;
- fallback records;
- plan hash.

### H1-3 Compilation outcomes

Keep compilation outcome distinct from CP5-B native-fidelity truth. Support
closed outcomes equivalent to:

- `DRAWINGML_EMITTED`;
- `SVG_VECTOR_FALLBACK`;
- `RASTER_FALLBACK_EXPLICIT` only where an existing route/capability explicitly permits it;
- `BLOCKED_UNSUPPORTED`;
- `BLOCKED_UNKNOWN_MAPPING`.

Do not promote CP5-B records to `NATIVE_EXACT`/`NATIVE_NORMALIZED` merely because
DrawingML was emitted.

### H1-4 Feature coverage

Define explicit compile/fallback/block behavior for every current CP5-B feature
ID. Natively exercise the feature subset used by approved D/E outputs where
technically feasible:

- SVG root/viewBox;
- group;
- rect/circle/ellipse;
- line/polyline/polygon;
- supported simple path commands;
- text/tspan and mixed CJK/Latin;
- markers/arrows/local refs;
- image;
- translate/scale/rotate/matrix via deterministic transform handling;
- stroke width/cap/join/dash;
- fill/stroke opacity;
- text anchor/dominant baseline/font attributes;
- same-document local references.

Unsupported clip/complex-path behavior remains explicit. No silent deletion or
rasterization.

### H1-5 Native object identity

Use deterministic non-authoritative shape identities, e.g.
`tds-fig:<figure-id>/<svg-object-id>/<semantic-role>`, so package audit can map
PowerPoint shapes back to canonical figure objects.

Scientific provenance must not be copied into shape names/custom metadata.

### H1-6 Text

Mixed Chinese/English text must remain text in native plans. Do not convert text
to outlines/images. Preserve significant content and intended line breaks.

### H1-7 Tests

RED→GREEN tests must include at least:

- raw/unapproved SVG rejected;
- wrong SVG hash rejected;
- registry identity mismatch rejected;
- unknown feature has explicit blocked/fallback result;
- silent raster fallback rejected;
- stable object IDs preserved;
- coordinate transform deterministic;
- repeated compile plan hash deterministic;
- CJK/Latin text preserved;
- simple path mapping correct;
- marker/reference target mismatch rejected;
- unsupported clip/complex behavior not claimed native;
- compiler has no PPTX writer API.

Checkpoint commit H1 and continue.

## 6. H2 — assembler integration and native-vector benchmarks

### H2-1 Integration

Extend `PythonPptxAssembler` through a narrow adapter path that consumes
`ApprovedFigureHandle` + `NativeFigureCompilationPlan`.

The assembler, not the compiler, creates PowerPoint shapes and saves the deck.

Prefer public `python-pptx` APIs. Narrowly scoped assembler-owned OOXML is
allowed only for unsupported properties, with deterministic structural tests.

### H2-2 Figure placement

Native figure placement must respect Layout Director target box and source
viewBox. Verify no compiler component independently chooses slide layout.

### H2-3 Explicit fallback

When a figure/subtree cannot be compiled natively:

- use the declared CP5-B/plan outcome;
- if legal, retain canonical SVG vector fallback through the existing SVG bridge;
- never silently use PNG/raster;
- persist fallback reason and exact source hash.

### H2-4 Benchmark deck

Create a synthetic native-vector benchmark PPTX through `PythonPptxAssembler`.
It must exercise:

- CP5-B primitive vectors;
- Fishbone;
- mechanism;
- experiment schematic;
- fabrication/process;
- fair comparison;
- scientific plot;
- image matrix;
- concept illustration.

Do not fabricate photo/literature evidence to fill blocked routes.

### H2-5 Structural benchmark proof

Audit PPTX/OOXML for:

- expected slide count;
- expected compiled shape count/types;
- stable shape names/object mappings;
- text remains text;
- CJK/Latin survives package save/reopen through `python-pptx`;
- slide relationships resolve;
- no undeclared media;
- vector fallback relationship is exact where used;
- no second exporter signature/path;
- no raw scientific SVG metadata promoted to scientific truth.

### H2-6 Native PowerPoint evidence

If native PowerPoint is available, native-vector benchmark slides may be used for
open/save/reopen evidence. If unavailable, structural compilation may PASS but
`drawingml_native_fidelity_status` remains `blocked_environment` or otherwise
unverified according to the release matrix.

Checkpoint commit H2 and continue.

## 7. I0 — fresh sanitized native-template reconstruction

### I0-1 Inputs

Use committed sanitized inputs only, including:

- `professor-template-resolved.json`;
- sanitized shell/body/profile artifacts;
- VSP003/style resolution;
- A01–A18 calibration;
- Fishbone profile;
- generic public/synthetic builder resources.

Do not open private aliases or PPTX.

### I0-2 No binary base reuse

Forbidden as template/package bases:

- all private exemplar PPTX files;
- Phase 2 `acceptance-deck.pptx`;
- Phase 2 render-compat PPTX;
- any copied historical acceptance/template package.

Construct fresh.

### I0-3 Backend ownership

Template reconstruction must live under the approved PPTX backend/template
subsystem. A fresh OOXML Master/Layout/theme builder may be used when
`python-pptx` cannot author required parts, but it must not expose a second
general deck assembler.

### I0-4 Reconstruction targets

Consume measured sanitized topology and roles. Attempt, where evidence supports:

- 16:9 13.333333 × 7.5 canvas;
- measured Master/Layout topology;
- formal cover/divider role;
- academic content role;
- Fishbone role;
- comparison/result role;
- summary/decision role;
- content-title region;
- footer/page-number/navigation regions where supported;
- typography/theme roles where supported;
- safe content bounds where resolved.

If an item is `insufficient_evidence`, preserve that status and use an explicit
fallback. Do not invent professor measurements.

### I0-5 Fresh package manifest

Create a reconstruction manifest for every package part, with controlled part
classes such as:

- builder_required;
- reconstructed_shell;
- generated_slide;
- generated_notes;
- generated_media;
- generated_metadata.

Reject:

- private media;
- comments/people;
- custom XML;
- embeddings/OLE;
- macros;
- external private links;
- private chart/workbook caches;
- private thumbnails;
- orphan/unreferenced parts.

### I0-6 Fresh-lineage proof

Prove by construction/input closure that the generated template uses only
committed sanitized/public/synthetic sources. No private source/hash comparison
requiring a new private open is authorized.

### I0-7 Template profile and reconstruction metrics

Profile the generated template and compare it to sanitized targets. Persist
per-metric target/actual/delta/tolerance/status. Do not collapse all fidelity to
one pixel or numeric score.

Checkpoint commit I0 and continue.

## 8. I1 — Ledger-derived acceptance deck

### I1-1 Canonical story source

Use the committed Phase 2 hypothesis-layered synthetic state, Ledger-derived
Slide Specs, and source cursors. The Phase 2 PPTX is not a build base.

Current committed acceptance source contains **H001 and H002 only**. Do not
invent H003.

### I1-2 Deck size

Create one fresh formal cover from deck metadata, followed by the nineteen
source-derived Phase 2 acceptance slides. Expected base size: **20 slides**.

A legitimate source-driven split policy may increase count. Do not remove or
merge required source semantics merely to hit 20.

### I1-3 Preserve narrative

Preserve:

- slide semantic order;
- H001→H002 chronology;
- Hypothesis and Problem separation;
- Fishbone revision/focus/history;
- failed/partial/future history where source requires it;
- source cursors;
- claim/evidence/action/decision bindings;
- notes/source references;
- layer transition;
- final summary/decision.

### I1-4 Figure modernization

Where a source slide calls for a governed figure, use the appropriate approved
CP5 figure route and H compiler plan/fallback.

At minimum the acceptance package should exercise, where the source story
supports them:

- Fishbone;
- mechanism;
- experiment schematic;
- fabrication/process only if the source slide semantics support preparation/process content;
- scientific plot;
- fair comparison;
- image matrix only if the source slide semantics/asset requirements support it.

Do not insert an unrelated figure family merely to improve benchmark coverage.
H2 already owns broad compiler coverage.

### I1-5 Evidence boundary

Never replace observation/literature evidence with concept imagery. If a source
slide has a committed synthetic evidence asset, retain its explicit synthetic
evidence identity. Missing real/literature evidence remains blocked rather than
fabricated.

### I1-6 Archetype/layout mapping

Use existing A01–A18 mappings where defined. Report exercised/unexercised
archetypes separately from library calibration coverage. Do not manufacture
extra slides for 18/18 deck coverage.

### I1-7 Figure handoff proof

Every CP5-governed figure placement must prove:

`persisted approval evidence → re-verification → ApprovedFigureHandle → NativeFigureCompilationPlan or declared SVG fallback → Layout → PythonPptxAssembler`.

Raw SVG/FOM/approval dictionaries are not accepted by Layout.

Checkpoint commit I1 and continue.

## 9. I2 — package, render, native and release QA

### I2-1 Package structural QA

Audit the generated acceptance PPTX for at least:

- ZIP/content-types integrity;
- slide count/order;
- slide→layout→master relationship closure;
- theme relationships;
- generated template identity;
- notes existence/source markers;
- all media/object relationships;
- stable native figure object identities;
- no orphan parts;
- no forbidden part families;
- expected native/fallback object counts;
- all governed figure hashes consistent with manifests/plans.

### I2-2 Story/semantic QA

Compare acceptance deck manifest/slide specs against Phase 2 source contracts.
Require:

- all 19 source slides represented exactly once unless an explicit split creates
  a controlled one-to-many mapping;
- source cursor monotonic/causal rules preserved;
- H001 and H002 order preserved;
- no H003;
- Hypothesis/Problem separate;
- Fishbone history retained;
- no loss of claim/evidence/action/decision refs;
- no unapproved figure bypass.

### I2-3 Render QA

Use existing renderer architecture. If a deterministic PPTX renderer is
available, render **every acceptance slide** and create:

- per-slide renders;
- full-deck montage;
- difficult-slide montage covering Fishbone, experiment, result/comparison,
  matrix/high-density, discussion/summary.

Bind every render to deck/slide/build hash.

Run clipping/overflow/nonblank/margin/occupancy QA where measurable.

If unavailable, record `blocked_environment`. Do not substitute deterministic
SVG test adapter evidence for PPTX render PASS.

### I2-4 Image-capable qualitative review

If an authorized image-capable review provider is available for generated
non-private renders, review **every acceptance slide**, hash-bound, for:

- hierarchy;
- legibility;
- scientific figure clarity;
- visual balance;
- crowding;
- alignment;
- comparison fairness;
- Fishbone readability;
- obvious professor-style contradictions.

Critical findings require correction/re-render/review.

If unavailable, `blocked_visual_review` and professor qualitative acceptance
cannot PASS.

### I2-5 Native PowerPoint acceptance

If Microsoft PowerPoint automation is available, use generated non-private
outputs only. Perform controlled open/save/reopen and verify where feasible:

- deck opens;
- slide count preserved;
- layout/master references remain valid;
- native compiled shapes remain shapes;
- native text remains editable text;
- CJK/Latin content survives;
- stable object names survive where expected;
- notes survive;
- relationships remain valid after round-trip;
- package re-audit passes;
- native compilation records remain consistent.

If unavailable, set `native_powerpoint_acceptance_status = blocked_environment`.
Do not treat LibreOffice/package validity as native PowerPoint PASS.

### I2-6 Professor structural metrics

Compare generated template/deck to committed sanitized professor descriptors and
G1 calibration. Persist per-metric evidence. Preserve provisional and
insufficient-evidence statuses.

### I2-7 Release gate

Evaluate every dimension in
`cp5-hi-release-gate-matrix.json` independently.

`acceptance_deck_build_status` may pass while production release remains
blocked.

`production_release_status` may pass only when every required release gate
passes.

`production_group_meeting_ready` remains false until production release passes
**and** external reviewer approval exists. Codex may therefore never
self-certify it true in this sprint handoff.

If blocked, create a `release-gap-report.json` identifying exact blockers and
minimum evidence required to clear them.

Checkpoint commit I2.

## 10. Required schemas/artifacts

Create closed schema-backed artifacts as needed. Expected final classes include
at least:

- compiler mapping/capability manifest;
- NativeFigureCompilationPlan corpus;
- native compilation audit;
- backend uniqueness audit;
- H execution evidence/QA;
- native-vector benchmark manifest/PPTX/structural audit;
- reconstructed sanitized template/profile;
- template reconstruction manifest;
- fresh-lineage/package privacy proof;
- reconstruction metrics;
- acceptance Slide Specs/mapping/deck manifest;
- acceptance PPTX;
- acceptance structural/semantic QA;
- render manifests/reports/montages where available;
- qualitative review artifact or blocked record;
- native PowerPoint acceptance artifact or blocked record;
- release-gate facts;
- release-gap report when needed;
- final implementation report.

All JSON schemas use Draft 2020-12/closed nested contracts and semantic tests in
addition to schema validation.

## 11. Native/vector acceptance RED tests

At minimum include tests for:

- second exporter path discovered;
- compiler writes PPTX directly;
- unapproved figure compiled;
- wrong ApprovedFigureHandle binding;
- stale SVG hash;
- missing capability record;
- unsupported feature claimed native;
- unknown feature silently dropped;
- silent raster fallback;
- CJK converted to image/path;
- object ID loss;
- geometry transform nondeterminism;
- missing slide relationship;
- fallback record mismatch;
- native plan hash mutation;
- benchmark package relationship failure.

## 12. Template/release RED tests

At minimum include tests for:

- private/package binary used as template base;
- old Phase 2 acceptance PPTX used as output base;
- unmanifested package part;
- forbidden customXml/OLE/macro/private media;
- unresolved relationship;
- wrong slide→layout→master link;
- missing required semantic layout role;
- professor measurement invented from insufficient evidence;
- source slide missing from acceptance deck;
- source slide duplicated without controlled split;
- H001/H002 order mutation;
- invented H003;
- Hypothesis/Problem merged;
- Fishbone history dropped;
- claim/evidence/action/decision ref loss;
- raw/unapproved figure bypass;
- release PASS with render blocked when render is release-required;
- release PASS with qualitative review blocked;
- release PASS with native PowerPoint blocked;
- Group Meeting ready true before external reviewer approval.

## 13. Checkpoint validation strategy

After each internal gate run focused tests and schema validation only.

Recommended internal commits:

- H0: `phase3: add CP5-H native backend contracts`
- H1: `phase3: add Scientific SVG native compiler`
- H2: `phase3: integrate native figures into PythonPptxAssembler`
- I0: `phase3: reconstruct fresh sanitized native template`
- I1: `phase3: build ledger-derived acceptance deck`
- I2: `phase3: add CP5-I release and native acceptance gates`

Do not run the full repository regression after every gate.

## 14. Cross-gate acceptance before definitive regression

Before freezing the final candidate, prove at least:

1. one public PPTX backend;
2. compiler cannot write PPTX;
3. every H benchmark input is an approved figure or explicit synthetic vector
   contract;
4. every CP5-B feature has a compile/fallback/block decision;
5. required D/E family figures compile or fall back explicitly;
6. native object IDs/text/geometry are deterministic;
7. template has fresh sanitized lineage;
8. required semantic layout roles exist or are explicitly blocked;
9. 19 Phase 2 source slides map into the acceptance story;
10. H001→H002 and all source cursors/bindings are preserved;
11. no H003 appears;
12. every governed figure enters through ApprovedFigureHandle;
13. package manifest covers every ZIP part;
14. no forbidden package family appears;
15. release dimensions are independently evaluated;
16. no blocked dimension is promoted to PASS;
17. private access counters remain zero unless a separately authorized private
    session exists.

Persist execution-backed facts, not only a boolean PASS.

## 15. Bounded correction policy

Ordinary in-scope failures may be corrected autonomously. Allow up to three
bounded correction cycles after cross-gate or definitive regression failures for
issues such as:

- compiler mapping defect;
- OOXML/native relationship defect;
- template topology/build defect;
- slide mapping/layout overflow defect;
- structural/render QA defect;
- schema/test migration;
- deterministic generated-artifact mismatch.

After a correction, rerun affected focused tests and cross-gate acceptance. If
the final candidate changes, freeze a new hash and run a new definitive full
regression.

Stop for reviewer only if the required fix needs:

- opening private exemplars;
- unauthorized external source-code reuse;
- a second PPTX backend;
- inventing scientific truth;
- relaxing the evidence boundary;
- another project phase outside H/I.

An unavailable renderer/PowerPoint/reviewer that has a defined blocked state is
not itself a reason to stop early; persist the blocked state and continue the
remaining independent gates.

## 16. Definitive regression and privacy

After I2 and cross-gate acceptance, freeze the final candidate and calculate
`TESTED` candidate-state hash/component list.

Use a **fresh disposable worktree** containing the exact candidate and run one
definitive complete test collection:

`python -m pytest packages/thesis-deck-system/tests -q`

Persist PRE/POST hashes, stdout/stderr, exit code, counts, completion marker.
Require `failed = 0` and `TESTED == disposable PRE == disposable POST`.

Then independently calculate active `CURRENT` candidate hash and require
`CURRENT == TESTED`.

After regression PASS run authoritative repository/staged privacy scans and
package privacy scans. Expected private access remains `0 / 0 / 0`; do not open
private exemplars to perform the scan.

## 17. Final report

Create:

`thesis-deck-system/reports/PHASE_3_CP5_HI_FINAL_PRODUCTION_SPRINT_IMPLEMENTATION_REPORT.md`

Report at minimum:

- reviewed starting SHA;
- reviewer-prepared design/baseline/matrix SHA identities;
- H0/H1/H2/I0/I1/I2 checkpoint SHAs;
- correction SHAs;
- files added/modified/deleted;
- focused test counts per gate;
- compiler mapping count/distribution;
- per-feature compilation outcomes;
- native plan count;
- backend uniqueness result;
- benchmark figure/slide/native/fallback counts;
- native-vector benchmark PPTX/hash;
- PowerPoint environment status;
- fresh template path/hash;
- generated master/layout/theme topology;
- reconstruction metric summary;
- package part counts/classifications;
- fresh-lineage/privacy proof;
- acceptance slide count;
- source-slide mapping count;
- split count;
- H001/H002 history preservation;
- H003 count = 0;
- ApprovedFigureHandle placement count;
- native/fallback figure count;
- exercised A01–A18 archetypes;
- provisional/insufficient calibration used;
- structural QA status;
- render count/status;
- montage paths/hashes;
- qualitative review count/status;
- native PowerPoint round-trip status;
- release-gate status for RG-01 through RG-16;
- acceptance deck build status;
- production release status;
- production Group Meeting readiness;
- release-gap report path if blocked;
- final full regression;
- TESTED/POST/CURRENT hashes;
- privacy results;
- known failures/corrections/blockers/technical debt/deviations.

Footer:

```yaml
phase: PHASE_3_CP5_HI_FINAL_PRODUCTION_SPRINT
status: awaiting_review
next_action_requested: REVIEW
```

## 18. Final status truth

Maximum status before external review:

- CP5-H: `implemented / awaiting review` or truthful blocked dimensions;
- CP5-I: `implemented / awaiting review` or truthful blocked dimensions;
- acceptance deck build may be `pass`;
- production release may be `pass` only if the release matrix allows it;
- `production_group_meeting_ready` **must remain false before external reviewer
  approval**, even if all technical gates pass.

## 19. Final commit/push/remote verification

After all authorized work and definitive validation:

1. final report/evidence consistency check;
2. `git diff --check` and exact scope audit;
3. final commit;
4. push `codex/thesis-deck-system`;
5. verify remote SHA/tree;
6. verify key source/schema/template/PPTX/artifact/report blobs.

Do not begin another phase after push.

## 20. Required final delivery

Return:

- repository/branch;
- final sprint SHA and remote SHA;
- H0/H1/H2/I0/I1/I2 SHAs;
- correction SHAs;
- test counts per gate;
- definitive full regression pass/fail;
- candidate hash equality;
- backend uniqueness;
- compiler mapping/outcome summary;
- benchmark PPTX/path/hash and audit;
- fresh template path/hash/topology;
- acceptance PPTX/path/hash/slide count;
- source-slide mapping/split count;
- H001/H002 preservation and H003 count;
- approved/native/fallback figure counts;
- render/qualitative/native PowerPoint statuses;
- release-gate RG-01..RG-16 summary;
- acceptance deck build status;
- production release status;
- production Group Meeting ready (`false` before reviewer approval);
- privacy findings and private counters;
- known failures/corrections/blockers/technical debt/deviations;
- recommended external reviewer decision.

Only after final commit, push, and remote verification write exactly:

`READY_FOR_CP5_HI_FINAL_PRODUCTION_REVIEW: yes`

Then STOP.