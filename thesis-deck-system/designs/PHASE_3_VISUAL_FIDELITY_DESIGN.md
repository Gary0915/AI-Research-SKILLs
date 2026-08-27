# Phase 3 Professor Visual Fidelity Design

## 1. Status and scope

This document is the implementation-ready design for Phase 3: professor visual
fidelity calibration, private exemplar integration, and a sanitized acceptance
deck. It implements the approved **Sanitized Calibration Pipeline** direction
and the mandatory D3-1–D3-10 review conditions.

This design does not authorize implementation. The next step, after reviewer
approval, is a separate test-driven implementation plan.

Phase 3 adds a visual-calibration layer to the approved Phase 1–2 control
plane. It does not alter the scientific source of truth:

```text
canonical scientific objects
→ append-only Ledger
→ Ledger.load()
→ cursor materialization
→ N-layer projections
→ stage-aware Slide Specs
→ field-level semantic bindings
→ calibrated Layout Plans
→ PythonPptxAssembler
→ structural/render/semantic/Professor QA
```

The following remain invariant:

- append-only temporal truth and cursor-scoped materialization;
- complete N-layer Hypothesis history;
- separate Hypothesis and Problem pages;
- versioned, historically bound Fishbone revisions;
- field-level scientific presentation contracts;
- evidence, asset, notes, and decision provenance;
- presentation-semantic and Professor QA honesty;
- one PPTX assembly backend;
- no Phase 4 or public/global Skill registration.

## 2. Architecture overview

Phase 3 uses two security domains separated by a fail-closed sanitizer:

```text
PRIVATE LOCAL DOMAIN
private alias
→ PrivateFixtureLocator
→ OOXML package validation
→ source SHA-256
→ local-only raw profile and private reference renders
                         │
                         │ explicit field allowlist only
                         ▼
COMMITTABLE SANITIZED DOMAIN
sanitized exemplar manifest
→ shell/body profile contracts
→ shell and body resolvers
→ professor visual grammar V3
→ A01–A18 and Fishbone calibration
→ reconstructed sanitized native template
→ reconstruction metrics
→ acceptance deck and QA evidence
```

No downstream component may open a private PPTX directly. Only the private
profiler may read private aliases. Resolvers, calibrators, template
reconstruction, layout selection, deck assembly, QA, and reporting consume
sanitized contracts.

## 3. Private exemplar ingestion architecture

### 3.1 Authoritative aliases

The only canonical source identifiers are:

- `private://template_primary_1`
- `private://layout_exemplar_2`
- `private://template_primary_3`

Absolute source paths may exist in process memory, ignored local configuration,
and local diagnostic logs only. They may not appear in committed JSON, YAML,
Markdown, PPTX, notes, render paths, manifests, or test snapshots.

### 3.2 Ingestion sequence

For each alias, the profiler performs:

1. resolve the alias with `PrivateFixtureLocator`;
2. require a readable, nonempty `.pptx` file;
3. verify ZIP signature and CRC integrity;
4. require `[Content_Types].xml`, `ppt/presentation.xml`, and at least one
   slide or slide-master part;
5. reject encrypted, macro-enabled, malformed, or unsupported packages for
   this Phase 3 path;
6. compute SHA-256 before profiling;
7. inspect OOXML and render locally;
8. write a raw private profile under ignored storage;
9. pass the raw profile to the whitelist sanitizer;
10. compare the output hash and source alias with the local ingestion record.

The three aliases are an atomic dependency for professor-fidelity acceptance.
If any alias is missing or invalid, private fixture ingestion becomes
`blocked_fixture` or `fail`, no synthetic source is substituted, and
`professor_visual_fidelity` cannot pass.

### 3.3 Local-only data

The following may exist only in the private local domain:

- resolved absolute paths and operating-system error messages;
- raw slide text, speaker notes, comments, citations, and URLs;
- document core/custom properties and author/company values;
- raw OOXML part names, relationship targets, and external links;
- extracted private media, filenames, thumbnails, and binary hashes;
- private source slide renders and contact sheets;
- shape names that contain private text;
- full raw theme/package dumps;
- local mapping from raw identities to sanitized identities;
- anydoc or equivalent local Office-document extraction output.

## 4. Raw private profile model

The raw profile is intentionally richer than any committed profile because it
supports measurement and local visual classification. It is never a public
contract and is never read after sanitization by the production pipeline.

Conceptual raw model:

```text
RawPrivateProfile
  run_id
  alias
  resolved_path
  source_filename
  source_sha256
  package_validation
  document_properties
  slide_size
  masters[]
  layouts[]
  themes[]
  slides[]
    raw_text
    notes
    comments
    relationships
    shapes[]
      raw_name
      raw_text
      geometry
      style
      media_target
  extracted_media[]
  local_renders[]
  classifier_annotations[]
```

Raw storage root:

```text
<repository>/.private/thesis-deck-system/phase3/<run-id>/
  raw/
  extracted-media/
  private-renders/
  diagnostics/
  sanitizer-staging/
```

The `.private/` root must be ignored before profiler implementation. Runtime
startup must verify that the resolved raw root is ignored by Git and lies
outside every committable artifact directory. Otherwise profiling fails before
opening a private file. Temporary directories outside the repository are also
allowed, but the same no-commit and cleanup rules apply.

Raw files use restrictive local permissions where supported. Successful runs
may retain local evidence for review, but no raw path may be referenced by a
committed artifact.

## 5. Whitelist sanitizer

### 5.1 Fail-closed rule

Sanitization is schema construction, not recursive field deletion. The
sanitizer creates a new output object from explicit typed selectors. It never
copies an input object wholesale. Every output schema uses
`additionalProperties: false`. An unrecognized requested field, invalid type,
unbounded string, or prohibited token causes rejection of the entire profile.

### 5.2 Allowed field families

Only these field families may cross into committed artifacts:

| Family | Allowed values |
| --- | --- |
| Source identity | private alias URI, resolved status, SHA-256, sanitized profile ID, schema/profile version |
| Structure identity | sanitized master/layout/descriptor IDs, integer counts, sanitized relationship graph using those IDs |
| Canvas | dimensions, aspect ratio, normalized safe bounds and margins |
| Placeholders | controlled placeholder class, sanitized index, normalized geometry, alignment and hierarchy role |
| Typography | permitted font-family name, numeric size/weight/spacing/indent, CJK/Latin fallback role |
| Color/style | RGB/ARGB or theme-role color, numeric line width/corner radius/opacity, fill/border role |
| Composition | controlled archetype/composition labels, normalized geometry, area/gap/symmetry/density metrics |
| Shell motifs | controlled motif label, normalized geometry, recurrence count, z-order role |
| Fishbone style | numeric geometry/spacing/line/highlight tokens and controlled state-role labels |
| Benchmark | sanitized descriptor IDs, metric name, numeric target/actual/delta/tolerance, pass/fail |
| Provenance | alias-level source role and sanitized measurement IDs only |

Free-form text is forbidden except for narrowly bounded rationale written by
the implementation from controlled rule identifiers. It may not be copied or
summarized from private slide content. Font-family strings are allowed only in
font fields. All other categorical strings must match controlled enums or
sanitized ID patterns.

### 5.3 Forbidden field and content classes

The sanitizer rejects:

- absolute Windows, UNC, POSIX home, or drive paths;
- source filenames other than stable alias URIs;
- slide text, notes, comments, citations, literature titles, and captions;
- private URLs, e-mail addresses, DOI strings, and external relationship URLs;
- author, company, manager, last-editor, and document-property values;
- media filenames, media bytes, thumbnails, screenshots, or binary blobs;
- raw OOXML/XML, ZIP entries, package parts, relationship IDs/targets, and
  custom XML;
- embedded objects, macros, OLE packages, charts with cached private data, and
  extracted tables;
- unbounded shape names, alt text, image descriptions, and custom tags;
- unknown keys at any nesting depth.

### 5.4 Privacy scanning and rejection

The sanitizer runs three independent checks:

1. **Schema allowlist validation:** rejects unknown keys, types, enums, and
   unconstrained strings.
2. **Lexical privacy scan:** scans serialized output for drive/UNC paths,
   source basenames, URL/DOI/e-mail patterns, private text canaries harvested
   locally, OOXML markup, notes/comments terms, and known private media names.
3. **Binary/package scan:** rejects non-JSON payloads, embedded base64/binary
   strings, ZIP signatures, image/PPTX signatures, and any staged private
   binary or screenshot.

Sanitization produces output only when all checks pass. Rejection writes a
local-only diagnostic containing the field path and classification; the
rejected value is not copied into a committed log.

## 6. Committed sanitized contracts

Phase 3 introduces separate JSON Schemas under
`thesis-deck-system/schemas/` and versioned profiles under
`thesis-deck-system/profiles/`.

### 6.1 Sanitized exemplar manifest

Records exactly one entry per required alias:

- alias URI;
- status;
- source SHA-256;
- sanitized profile ID;
- exemplar role (`formal_shell`, `body_composition`);
- sanitizer version and sanitization QA reference.

It contains no path, filename, slide text, or private render reference.

### 6.2 Shell profile

`shell-profile.schema.json` represents Exemplar 1 and Exemplar 3 separately:

- sanitized canvas/master/layout identities;
- layout-to-master graph;
- placeholder classes and normalized geometry;
- shell motifs, safe bounds, title/footer/navigation/page-number regions;
- typography and theme-role tokens;
- recurrence metrics;
- alias-level provenance per token.

### 6.3 Body-composition profile

`body-composition-profile.schema.json` represents Exemplar 2:

- sanitized composition descriptors;
- controlled composition class;
- normalized shape-role geometry;
- figure/text, matrix, comparison, annotation, density, and whitespace metrics;
- controlled qualitative rules derived by local inspection;
- sanitized source-slide ordinal and measurement IDs.

It cannot contain source slide text, extracted figure identifiers, or media
names.

### 6.4 Professor visual grammar

`professor-visual-grammar-v3.schema.json` separates:

- `formal_shell_rules`, sourced only from Exemplar 1/3;
- `body_composition_rules`, sourced primarily from Exemplar 2;
- typography, spacing, highlight, caption, comparison, annotation, matrix,
  density, Fishbone, and do-not-use tokens;
- archetype-to-composition mappings;
- source-role evidence for every resolved token;
- unresolved conflicts and blocked calibrations.

### 6.5 Fishbone style profile

`fishbone-style-profile.schema.json` contains visual tokens only: branch
geometry, spacing, line weights, label regions, focus prominence, and state
styles. It contains no branch labels, research content, branch IDs from a
private deck, or scientific facts.

### 6.6 Archetype calibration

`archetype-calibration.schema.json` records A01–A18 semantic role, immutable
contract reference, mutable geometry/style tokens, source descriptor IDs,
density and split bounds, preferred reconstructed native layout role,
calibration status, rationale rule IDs, and per-token provenance.

### 6.7 Reconstruction benchmark

`reconstruction-benchmark.schema.json` records sanitized reference descriptor
ID, reconstruction slide ID and render hash, metric targets/actuals/deltas,
tolerances, per-metric status, aggregate status, and local-private-evidence
availability. It never references a private render path or private image hash.

## 7. Exemplar-role separation and conflict resolution

The resolver never pools all three sources or computes a generic average.

### 7.1 Fixed source authority

- **Exemplar 1 (`template_primary_1`)** governs working canvas, content-slide
  master topology, title grid, formal academic content shell, and secondary
  Hypothesis/research-history patterns.
- **Exemplar 3 (`template_primary_3`)** governs formal cover/chapter-divider
  treatment, footer/page-number/navigation grammar, and defense-style formal
  hierarchy.
- **Exemplar 2 (`layout_exemplar_2`)** governs body composition, scientific
  figure dominance, comparisons, matrices, annotations, captions, callouts,
  and density. It cannot override canvas/master/shell identity.

### 7.2 Conflict rules

1. Token authority is selected by token family, never by arithmetic averaging.
2. Shared safe content bounds use the geometric intersection of compatible
   Exemplar 1/3 bounds; an empty or impractically small intersection is a
   blocking conflict.
3. Content-slide title geometry follows Exemplar 1. Cover and section-divider
   title geometry follows Exemplar 3.
4. Footer/page-number/navigation follows Exemplar 3 unless the object is absent
   there; only then may the equivalent Exemplar 1 token be selected.
5. Hypothesis/history shell motifs follow Exemplar 1; body placement inside the
   safe area follows Exemplar 2.
6. Typography uses role-specific selection: content and Hypothesis roles from
   Exemplar 1, cover/divider/footer roles from Exemplar 3, and body/caption
   scale ratios from Exemplar 2 constrained by the shell hierarchy.
7. Theme colors are mapped by semantic role. Conflicting colors remain
   separate role tokens rather than blended colors.
8. Every disagreement is persisted as a sanitized conflict record with chosen
   source, rule ID, and losing alternative. Unmapped conflicts block the
   resolved profile.

## 8. Shell resolver

The shell resolver consumes the two shell profiles and emits
`professor-template-resolved.json`. It resolves:

- slide dimensions and aspect ratio;
- native master/layout role topology for the reconstructed package;
- content, cover, divider, Fishbone, comparison, and summary layout roles;
- title region and baseline;
- Roman-numeral/chapter-marker and angled-label motifs when measured;
- footer, page number, and bottom navigation regions;
- safe content bounds and alignment grid;
- formal typography and mixed CJK/Latin fallback hierarchy;
- white-background, gray, primary-text, accent, and red-emphasis roles;
- recurring shell-object identities and z-order.

Hard conflicts include incompatible canvas ratios, missing required content
safe bounds, overlapping recurring shell regions, or no valid title region.
They produce `fail`, not a guessed compromise. Soft conflicts are resolved by
the token-authority rules in section 7 and remain auditable.

## 9. Body-composition resolver

The Exemplar 2 profiler classifies useful slides locally, then sanitizes each
as a composition descriptor using controlled roles. The resolver groups
descriptors without looking at private text and produces reusable grammar for:

- photo plus schematic;
- horizontal Control versus Proposed/Treatment;
- same-page result comparisons;
- main-image plus small-image matrices;
- table plus schematic;
- literature plus mechanism;
- result plus discussion;
- red take-home callouts;
- arrows and physical-interface annotations;
- figure/text dominance and high-density page structure.

Each descriptor includes normalized regions, alignment axes, gutters, area
ratios, matrix row/column counts, caption/callout geometry, annotation density,
whitespace fraction, and split indicators. Multiple descriptors of the same
class produce a bounded range and a preferred exemplar descriptor; they are not
collapsed into a single unconstrained average. Outliers remain visible.

The resolver selects a composition by semantic role, asset count/type,
comparison requirement, matrix dimensions, required text fields, and density.
If required content cannot fit within the calibrated range, the existing split
governance remains authoritative; the resolver cannot shrink scientific text
or self-approve an exception.

## 10. A01–A18 calibration matrix

All archetypes retain their Phase 2 semantic role, required scientific fields,
stage restrictions, provenance bindings, physical slot identities, and split
policy. Only geometry, typography/style tokens, visual hierarchy, and native
layout mapping may change.

| ID | Measurement influence | Mutable calibration tokens | Immutable semantic contract | Insufficient-evidence fallback |
| --- | --- | --- | --- | --- |
| A01 Hypothesis | Exemplar 1 Hypothesis/history shell; Exemplar 1/3 title system | title/assertion geometry, hierarchy, chapter marker | question, hypothesis, falsifier remain visible; separate from Problem | retain Phase 2 geometry, mark blocked calibration |
| A02 Problem | Exemplar 1 shell + Exemplar 2 observation/problem | three-region balance, title, question emphasis | previous finding, conflict, question, scope | Phase 2 geometry; no fidelity PASS |
| A03 Fishbone | Exemplar 1 history shell + Fishbone style profile | figure bounds, focus annotation, shell placement | historical revision and focus bindings | Phase 2 placement; Fishbone fidelity blocked |
| A04 Observation | Exemplar 2 observation/photo compositions | figure/text ratio, caption, question region | observation, problem, question, evidence refs | Phase 2 geometry; block archetype calibration |
| A05 Literature | Exemplar 2 literature/mechanism | column ratio, mechanism region, caption density | consensus, disagreement, gap, implication | Phase 2 geometry; block calibration |
| A06 Mechanism/Solution | Exemplar 2 phenomenon/mechanism/solution | diagram/strategy ratio, arrow/callout tokens | mechanism, provenance link, strategy, success criterion | Phase 2 geometry; block calibration |
| A07 Photo/Schematic | Exemplar 2 photo plus schematic | dominant photo, schematic inset, annotation geometry | required asset/text bindings | Phase 2 geometry; block calibration |
| A08 Control/Proposed | Exemplar 2 horizontal comparisons | panel widths, gutter, symmetry, labels | control and proposed content remain distinct | Phase 2 symmetric geometry; block fidelity PASS |
| A09 Experiment Design | Exemplar 2 experiment setup and table/schematic | matrix/table/diagram geometry, density | IV, controls, baseline, N, metrics, units, method, prediction, rule | Phase 2 geometry; block calibration |
| A10 Result Single | Exemplar 2 figure-first results | dominant figure, annotation and take-home regions | result identity/text/metric/uncertainty/asset | Phase 2 geometry; block calibration |
| A11 Result Comparison | Exemplar 2 result comparisons | panel symmetry, figure sizes, gutters, captions | each Result remains distinguishable and bound | Phase 2 geometry; block calibration |
| A12 Image Matrix | Exemplar 2 microscopy/mapping matrices | rows, columns, gaps, dominant/secondary ratio | matrix asset identities and annotations | Phase 2 geometry; block calibration |
| A13 Hero Result/Discussion | Exemplar 2 result plus discussion | hero ratio, interpretation strip, red-callout use | Result, interpretation, Decision, Next Step binding | Phase 2 geometry; block calibration |
| A14 Integrated Discussion | Exemplar 2 multi-result discussion + shell | supporting/contradicting/uncertainty proportions | all discussion semantic fields and result order | Phase 2 geometry; block calibration |
| A15 Summary/Decision | Exemplar 2 take-home emphasis + Exemplar 3 formal closure | decision hierarchy, callout, next-step region | answered question, status, decision, uncertainty, next question/step | Phase 2 geometry; block calibration |
| A16 Transition | Exemplar 1 research-history + Exemplar 1/3 shell | transition-node spacing, derivation strip | predecessor/successor provenance and causal cursor | Phase 2 geometry; block calibration |
| A17 Progress/To-do | Exemplar 2 progress composition when present + shell grid | commitment table, current position, parallel work | prior commitment, owner/timing/status/block links | Phase 2 geometry; block calibration |
| A18 Schedule/Next Step | Exemplar 2 schedule pattern when present + shell grid | timeline, dependency lanes, date hierarchy | owner, timing, dependencies, decision binding | Phase 2 geometry; block calibration |

An archetype with insufficient evidence may continue to function using the
approved Phase 2 geometry, but its `calibration_status` is
`insufficient_evidence`. Any such archetype used in the Phase 3 acceptance deck
prevents professor visual fidelity from passing.

## 11. Sanitized native template reconstruction

### 11.1 Reconstruction rule

The sanitized template is built from sanitized descriptors and independently
created primitives. A private PPTX is never copied, imported, edited, or used
as the output package base.

```text
resolved shell descriptors
→ explicit reconstruction manifest
→ PythonPptxAssembler-compatible native master/layout builder
→ sanitized shell primitives
→ sanitized native template PPTX
→ package privacy and structural QA
```

No private OOXML bytes or relationship graph are reused. Font names, colors,
measurements, and motif geometry are data inputs; each OOXML part is generated
afresh.

### 11.2 Package reconstruction manifest

The manifest assigns every output part one of:

- `reconstructed_shell`: generated from sanitized descriptors;
- `builder_required`: produced by the sole approved backend/runtime;
- `sanitized_metadata`: generated generic document properties;
- `generated_scientific_asset`: non-private synthetic acceptance asset with
  repository provenance.

Allowed part families are:

- `[Content_Types].xml` and root relationships;
- sanitized `docProps/core.xml` and `docProps/app.xml` with generic project
  identity and no author/company/private source metadata;
- `ppt/presentation.xml`, presentation relationships, view/presentation
  properties, and table styles;
- freshly generated theme parts;
- freshly generated slide-master and slide-layout parts plus internal
  relationships;
- generated acceptance slide and notes parts;
- generated, provenance-bound, non-private SVG/PNG media;
- package relationship parts required by the listed owners.

Forbidden part families include copied private media, comments, people,
custom XML, embeddings, OLE objects, macros, external links, private charts or
cached workbooks, private thumbnails, and orphan/unreferenced parts.

### 11.3 Package privacy proof

QA must prove:

- every ZIP member matches the reconstruction manifest and allowed family;
- every relationship target resolves and is allowed;
- no external relationship exists;
- no orphan part exists;
- core/app properties contain only generic sanitized values;
- no part hash equals any locally recorded private source-part hash, except a
  separately documented public component explicitly approved by the reviewer;
- no private source basename, text canary, URL, author/company value, or media
  filename occurs in XML or binary strings;
- every embedded media file is repository-provenanced synthetic/public content;
- generated slide → layout → master relationships match the resolved profile.

Any reused private part hash is a hard failure. The default design contains no
exception.

## 12. Reconstruction benchmark architecture

Private reference slide renders and local side-by-side comparisons remain under
the ignored private run directory. Only sanitized reconstruction renders and
numeric metrics may be committed.

```text
private local reference render + raw geometry
                 │ local comparator
sanitized reconstruction render + sanitized geometry
                 ▼
per-metric deltas and findings
                 ▼ whitelist sanitizer
committed benchmark metrics + sanitized reconstruction render
```

The default measurable thresholds are below. Archetype-specific profiles may
tighten them; they may not loosen them without a recorded reviewer-approved
calibration change.

| Metric | Default acceptance threshold |
| --- | --- |
| Normalized x/y/w/h edge error | each edge ≤ 0.025 of canvas |
| Title region edge error | ≤ 0.020; title-region IoU ≥ 0.90 |
| Dominant-figure area-ratio delta | ≤ 0.05 |
| Text-to-figure area-ratio delta | ≤ 0.10 |
| Column/gutter delta | ≤ 0.020 of canvas width |
| Comparison panel asymmetry delta | ≤ 0.030 |
| Caption position/height delta | ≤ 0.025 |
| Callout/red-box edge error | ≤ 0.035 |
| Image-matrix gap delta | ≤ 0.015 |
| Table-to-diagram proportion delta | ≤ 0.08 |
| Footer/navigation alignment delta | ≤ 0.015 |
| Font size delta | ≤ 2 pt and ≤ 8% |
| Recurring line-width delta | ≤ 0.35 pt |
| Semantic color delta | CIEDE2000 ≤ 6 where measurable |
| Whitespace-fraction delta | ≤ 0.06 |
| Fishbone stable-branch position delta | ≤ 0.020 between revisions |
| Fishbone current-focus prominence | stroke ratio ≥ 1.5 and contrast ratio ≥ 3:1 |

No global pixel-similarity score can independently pass a benchmark. Required
metrics for the archetype must each pass, and image-capable review must find no
critical fidelity issue.

## 13. Fishbone calibration

Fishbone calibration consumes sanitized shell tokens and the Fishbone style
profile. It may change:

- spine and branch geometry;
- parent-child angle and spacing;
- line widths and endpoint treatment;
- label placement and wrapping bounds;
- CURRENT label, border, fill, and contrast prominence;
- completed, partial/failed-informative, superseded, and future visual tokens.

It may not change stable branch IDs, parent references, status meanings,
revision numbers, historical snapshot content, Hypothesis Layer bindings,
source cursors, or provenance. The renderer receives canonical Fishbone data
and applies style tokens without rewriting the data.

Position stability QA compares unchanged branch IDs across revisions. CURRENT
focus QA uses render-grounded contrast/prominence evidence and image-capable
review; metadata alone cannot certify 3–5 second discoverability.

## 14. PPTX backend boundary

`PythonPptxAssembler` remains the only deck assembly adapter. Phase 3 may add
methods behind this adapter for reconstructed native masters/layouts, shell
primitives, and calibrated placement, but may not add another assembler or a
parallel deck-generation stack.

Direct ZIP/XML inspection is allowed only for:

- private package validation and local profiling;
- package-part privacy scans;
- slide/layout/master and SVG relationship QA;
- structural extraction used by reconstruction metrics.

Direct OOXML inspection does not create or mutate the acceptance deck. All deck
assembly flows through the approved adapter boundary.

## 15. Image-capable visual review contract

Qualitative review operates on actual rendered images after rendering. A
review record contains:

```json
{
  "slide_id": "S-...",
  "render_path": "thesis-deck-system/artifacts/phase3/render/slide-01.png",
  "render_sha256": "<64 lowercase hex>",
  "dimensions": {"width": 1921, "height": 1080},
  "reviewer_method": {
    "kind": "image_capable",
    "tool_or_reviewer_id": "<controlled identifier>",
    "reviewed_at": "<date-time>"
  },
  "slide_specific_findings": [],
  "visual_fidelity_findings": [],
  "status": "pass|fail|blocked_environment"
}
```

The review verifies hierarchy, exemplar-role resemblance, density, figure
dominance, annotations/callouts, comparison fairness, Fishbone focus,
Traditional Chinese wrapping, and unexpected private/synthetic-template
content. The stored render hash must equal the inspected file hash. Missing or
mismatched renders block the review. A non-image-capable method cannot emit
`pass`.

Private reference reviews use the same local record shape but remain local and
replace committed paths with alias/descriptor identities during sanitization.

## 16. Privacy QA and negative-test design

The TDD plan must create failing tests before implementation for at least:

1. absolute Windows drive, UNC, and POSIX home paths in sanitized output;
2. copied private slide text or locally harvested text canaries;
3. speaker notes, comments, or notes-part content;
4. author/company/last-editor document metadata;
5. private media filenames, alt text, or raw shape names;
6. private/external URLs, e-mail addresses, and DOI strings;
7. copied citation or literature-title text;
8. copied OOXML, ZIP/binary, base64 media, or private package-part hashes;
9. a private source screenshot staged under a tracked path;
10. a private source PPTX or PPTX with a matching source hash staged in Git;
11. unknown fields at any depth of a sanitizer input mapping;
12. a reconstructed template containing an orphan or external relationship;
13. a sanitized profile that embeds a private render path or hash;
14. a committed artifact containing any authoritative source basename.

The pre-commit/release privacy scan examines tracked and staged files, not only
the files generated by the current process. Findings include classification
and repository-relative file location, never the leaked private value itself.

## 17. Reconstruction and visual acceptance gates

`professor_visual_fidelity: pass` requires all of the following:

1. all three required aliases resolve and match the locally verified hashes;
2. all three OOXML packages pass validation;
3. raw profiles remain in ignored local storage;
4. whitelist sanitization and repository-wide privacy QA pass;
5. separate Exemplar 1, Exemplar 2, and Exemplar 3 sanitized evidence exists;
6. shell and body resolvers have no blocking conflict;
7. the resolved grammar records asymmetric source roles;
8. every A01–A18 record is calibrated, or any unused insufficient-evidence
   record is explicitly non-blocking under reviewer-approved scope;
9. every archetype used by the acceptance deck is fully calibrated;
10. reconstructed template package/privacy/relationship QA passes;
11. required reconstruction metrics pass per archetype;
12. Fishbone geometry, state style, and focus evidence pass;
13. structural PPTX, field-level presentation, provenance, and semantic QA pass;
14. render-pixel QA passes for every acceptance slide;
15. hash-bound image-capable visual review passes every acceptance slide and
    the required local private reference comparisons;
16. Professor QA consumes calibrated grammar and presentation-semantic evidence;
17. report-evidence consistency QA passes.

A metadata-only or aggregate-only PASS is invalid. Failure or blocked status in
any required item prevents professor visual fidelity from passing.

## 18. Native PowerPoint and production gates

Native Microsoft PowerPoint acceptance is a separate Stage 8 gate. If native
PowerPoint is unavailable:

- Stage 8 is `blocked_environment`;
- later release/final-version gates remain blocked or not run as defined by the
  canonical pipeline;
- LibreOffice is compatibility/render evidence only;
- `production_group_meeting_ready` remains `false`.

Even if native PowerPoint becomes available, production readiness also requires
the separately required private/sanitized real thesis scientific fixture
acceptance. The Phase 3 sanitized synthetic corpus alone cannot establish
production readiness.

## 19. QA ownership and error handling

Owning checks are distinct:

- ingestion QA owns alias/hash/package validity;
- sanitizer/privacy QA owns the private-to-committable boundary;
- profile QA owns schema and measured evidence completeness;
- reconstruction QA owns metric deltas and template package reconstruction;
- structural QA owns slide/layout/master, governed shapes, notes, and SVG
  relationships;
- render-pixel QA owns pixel-derived clipping, balance, density, and visibility
  proxies;
- image-capable review owns qualitative resemblance and presentation quality;
- Professor QA owns scientific story and professor-profile logic;
- report consistency QA owns delivery facts.

No gate may synthesize another gate's PASS. Every PASS requires an executed
check and inspectable evidence. A private dependency failure produces a blocked
or failed dimension without erasing successful independent checks.

## 20. D3-1–D3-10 traceability

| Condition | Design coverage | Acceptance proof required |
| --- | --- | --- |
| D3-1 reconstructed template | Section 11 | reconstruction manifest, part/hash/privacy scan, no private part reuse |
| D3-2 asymmetric roles | Sections 7–10 | token-level alias-role provenance and conflict records |
| D3-3 local-only raw outputs | Sections 3–5 | ignored-root guard, allowlist sanitizer, negative privacy tests |
| D3-4 benchmark separation | Sections 6.7 and 12 | local private evidence plus committed numeric metrics only |
| D3-5 measurable targets | Sections 12 and 17 | explicit per-metric tolerances and evidence |
| D3-6 semantic preservation | Sections 1 and 10 | immutable contract refs and full Phase 1–2 regression suite |
| D3-7 Fishbone semantics | Section 13 | stable-ID/revision/binding regressions and render evidence |
| D3-8 one backend | Section 14 | backend dependency scan and adapter-level assembly tests |
| D3-9 image-capable review | Section 15 | render-hash-bound per-slide review records |
| D3-10 native/readiness split | Section 18 | Stage 8 status and production readiness evidence |

## 21. Proposed next TDD implementation phases

After this design is approved, create a separate implementation plan with these
bounded phases:

1. **Contracts and privacy boundary:** schemas, ignored local storage guard,
   sanitizer allowlist, staged-file privacy scanner, and negative tests.
2. **Private profiler:** alias/OOXML/hash validation and raw local profile,
   implemented only after privacy tests fail for the expected reasons.
3. **Sanitized profiles and resolvers:** separate Exemplar 1/3 shell profiles,
   Exemplar 2 body profile, conflict rules, and visual grammar V3.
4. **Calibration and reconstructed template:** A01–A18, Fishbone style, package
   reconstruction manifest, and sole-backend template build.
5. **Reconstruction benchmarks:** local private renders, sanitized
   reconstructions, metric QA, and privacy-safe committed evidence.
6. **Acceptance deck:** existing ledger/materialized N-layer state to calibrated
   Slide Specs/Layout Plans/PPTX without a second scientific source of truth.
7. **Full QA and reporting:** privacy, structural, semantic, Professor,
   render-pixel, image-capable review, report facts, implementation report,
   commit/push/remote verification.

Each phase must use red-green-refactor TDD, preserve the full Phase 1–2 suite,
and stop rather than weakening a test or gate to accept existing output.

## 22. Known design risks and unresolved questions

Known risks:

- `python-pptx` has limited public APIs for constructing masters/layouts; the
  implementation may require narrowly scoped adapter-internal OOXML generation.
  This remains one backend because creation is owned by
  `PythonPptxAssembler`, but it requires strong package tests.
- Font availability may differ between the profiling, LibreOffice-render, and
  native PowerPoint environments. Profiles must distinguish requested font
  tokens from resolved-render fonts.
- Local role classification can require human/image-capable judgment. The raw
  decision may be local, but the committed descriptor must use controlled
  classes and numeric evidence.
- Some A01–A18 roles may have weak direct exemplar coverage. The system must
  expose insufficient evidence instead of claiming calibrated fidelity.
- Private source part hashes are sensitive local evidence and cannot be
  committed; package non-reuse QA must persist only aggregate counts/status.

Unresolved design questions requiring later evidence, not a design decision:

- Which exact archetypes lack direct support after all three decks are fully
  profiled?
- Whether native Microsoft PowerPoint is available for Stage 8 at the final
  Phase 3 acceptance run.
- Whether a permitted private/sanitized real thesis scientific fixture will be
  supplied for a later production-readiness gate.

None of these questions blocks implementing the approved pipeline after this
design receives reviewer approval; each has an explicit blocked/fail behavior.
