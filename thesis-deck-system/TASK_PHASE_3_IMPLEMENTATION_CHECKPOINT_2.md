# Task — Phase 3 Implementation Checkpoint 2

## Purpose

Authorize the **first bounded production-private access** for Phase 3 after Checkpoint 1 approval.

Checkpoint 2 implements the approved plan's profiler/minimized-classification stage only:

1. finish mandatory pre-open hardening;
2. resolve the three local production aliases under the private guard;
3. validate/read the three PPTX files read-only;
4. extract data-minimized local raw structural profiles;
5. cross the private boundary only through fail-closed sanitized structural descriptors;
6. optionally perform strictly ephemeral candidate-render review only if a private-authorized `ImageReviewProvider` passes preflight;
7. produce sanitized machine-readable evidence proving what was and was not accessed/retained.

Do not reconstruct the professor template, calibrate A01–A18, generate production figures, assemble an acceptance deck, start Phase 4, or globally register Skills.

## Source authority

Use only these stable aliases in committed artifacts:

- `private://template_primary_1`
- `private://layout_exemplar_2`
- `private://template_primary_3`

Actual paths/basenames remain local-only and must never appear in committed files, Git diffs, reports, test fixtures, screenshots, or final delivery text.

Authority remains asymmetric:

- Exemplar 1 + Exemplar 3 → shell/master/template structural evidence;
- Exemplar 2 → body-composition and figure-grammar structural evidence;
- no three-exemplar averaging.

## CP2-PRE-1 — repository-wide committed-text privacy scan

Before resolving any production alias, strengthen and execute the privacy scanner over relevant tracked UTF-8 repository text/code/config/document files, not only artifacts/profiles/reports.

Requirements:

- scan tracked `.py`, `.json`, `.yaml`, `.yml`, `.md`, `.txt`, `.toml`, `.ini`, and other intentionally text-governed project files;
- synthetic-canary source/tests may be excluded only by a narrow documented rule;
- scan current Git index/staged content as already required;
- load local forbidden root/basename signatures without persisting the raw value;
- detect Windows, UNC, WSL `/mnt/<drive>/...`, local configured private roots, and basename-only leakage;
- findings contain only rule ID/classification/location/sanitized ID;
- any finding blocks alias resolution.

Add RED tests proving a tracked ordinary source/config file containing a synthetic private path/basename blocks the pre-open gate.

## CP2-PRE-2 — production empirical Observation policy

Before production alias access, separate fixture empirical kinds from production empirical kinds.

Production empirical Observation must reject:

- `synthetic_measurement`;
- `synthetic_observation`;
- `simulation_output`;
- generated/contextual concept evidence.

Production empirical Observation may use only verified real empirical evidence kinds approved by the canonical Evidence policy, such as real experimental measurement, observation photo, and microscopy/other explicitly real empirical sources.

Synthetic kinds remain legal only under explicit synthetic/test-fixture mode.

Add RED tests proving simulation and synthetic evidence cannot satisfy production empirical Observation while fixture mode continues to support synthetic tests.

## CP2-1 — authorized alias resolution guard

Implement a Checkpoint 2 execution policy/evidence object distinct from Checkpoint 1.

Every alias resolution must:

1. accept a stable alias, never an arbitrary committed path;
2. record the attempt before resolution;
3. confirm CP2-PRE-1 and CP2-PRE-2 passed;
4. resolve only from ignored/local configuration;
5. reject unrecognized aliases;
6. record a sanitized alias-resolution result without persisting the path/basename.

Required production aliases: exactly the three listed above.

Committed QA may report alias IDs, source SHA-256 values, OOXML validity, slide counts, and sanitized descriptor counts. It may not report source paths or basenames.

## CP2-2 — authorized private-source session

After alias resolution and private-root validation, open each PPTX through one controlled read-only source-session API.

Requirements:

- record source-session start before file open;
- verify the source is a regular file and valid OOXML/PPTX package;
- compute whole-source SHA-256;
- perform read-only ZIP/OOXML inspection;
- do not mutate the private PPTX;
- do not use private PPTX as an assembly base;
- do not copy package parts into committed storage;
- do not persist private part hashes across the sanitizer boundary;
- do not extract media/notes/text into committed files.

The controlled source session should expose sanitized structural measurements to the profiler, not a generic unrestricted file handle to downstream production code.

## CP2-3 — data-minimized raw private profiler

Raw profiles remain local-only under the ignored Phase 3 private root.

Profile structurally first. Extract only information required for later visual calibration.

### Exemplar 1 / Exemplar 3 raw shell measurements

May include local raw measurements for:

- slide dimensions;
- master/layout counts and relationship topology;
- normalized title/header/footer/page-number/navigation geometry;
- recurring shell-object geometry;
- safe content bounds;
- margins/gutters;
- font family/size/weight/style roles;
- fill/stroke/theme color roles;
- recurring shell primitive classes;
- layout/master identity relationships using local/sanitized IDs.

Do not export slide text, notes, citations, URLs, author/company metadata, media names/bytes, chart caches, raw XML, raw relationships, or package-part hashes.

### Exemplar 2 raw body/figure measurements

May include local raw measurements for:

- object/region geometry and normalized bounding boxes;
- object type classes: text region, picture region, table, chart region, native shape, line/arrow, grouped object;
- primitive type/count;
- image/figure/text area ratios;
- panel counts and symmetry;
- comparison geometry;
- matrix row/column structure;
- arrow orientation and endpoint geometry;
- red-callout geometry/recurrence;
- caption-region geometry without caption text;
- annotation density;
- dominant-figure ratio;
- photo/schematic spatial relationship;
- whitespace/gutter measurements;
- color/line/font-role measurements permitted by the approved sanitizer.

Do not use Exemplar 2 to establish committed shell token families.

## CP2-4 — sanitized structural descriptor boundary

Introduce typed sanitized descriptor contracts sufficient for later Phase C resolvers, without performing the resolver/calibration itself.

Recommended committed classes:

- `sanitized-exemplar-manifest`;
- `sanitized-shell-structural-descriptors` for Exemplar 1 and Exemplar 3;
- `sanitized-body-structural-descriptors` for Exemplar 2;
- `checkpoint-2-qa`.

Sanitized descriptors may contain only approved values:

- stable alias;
- whole-source SHA-256;
- sanitized descriptor/profile IDs;
- normalized/numeric geometry;
- counts/ratios;
- controlled enums;
- bounded approved font names;
- color/style role measurements;
- sanitized relationship/role IDs;
- evidence-tier precursor counts where structurally derivable.

Explicitly forbidden:

- source paths/basenames;
- slide text;
- speaker notes/comments;
- private URLs/DOIs/citations/titles;
- author/company metadata;
- media filenames/bytes;
- raw XML/relationships;
- chart cached data;
- private render paths/hashes;
- private OOXML package-part hashes.

Unknown sanitizer fields fail closed.

Add a shell-contamination negative test: Exemplar 2 body descriptors cannot emit/override committed shell descriptor families.

## CP2-5 — structural-first slide classification

All slides may be structurally scanned without rendering.

Create sanitized candidate families using geometry/object-type evidence only, for example:

- formal shell/divider;
- Hypothesis/Problem;
- photo + schematic;
- Control vs Proposed/comparison;
- experiment schematic;
- result single;
- result comparison;
- result + discussion;
- image matrix;
- Fishbone/research map;
- fabrication/process flow;
- other/insufficient structural evidence.

Do not claim recurring professor grammar yet. This checkpoint only creates sanitized descriptor/classification evidence for the later resolver.

## CP2-6 — optional private candidate render review

Private rendering is OPTIONAL and capability-gated.

Before any private render:

- run `ImageReviewProvider` preflight;
- require `private_content_allowed=true`;
- require `approved_for_private_exemplars=true`;
- require permitted egress and retention;
- require hash binding and authorized local-private input form.

If the provider cannot satisfy every private gate:

- render no private slide for that provider;
- set private qualitative classification to `blocked_visual_review`;
- structural profiling may still pass.

If approved:

1. select candidate slide from sanitized structural descriptors;
2. render only that slide;
3. inspect/classify;
4. keep only a local hash-bound review record;
5. delete the render immediately;
6. retain zero private screenshots at Checkpoint 2 close unless a later separately authorized benchmark task explicitly requires retention.

No private render, private render hash, source basename, or slide text may be committed.

## CP2-7 — retention and cleanup evidence

Maintain a local-only retention manifest with at least:

- raw profile files created;
- candidate renders created;
- candidate renders deleted;
- candidate renders retained at close;
- private text exports;
- notes exports;
- media exports;
- local raw-profile retention status.

Committed Checkpoint 2 QA may contain aggregate counts only.

Required checkpoint-close conditions:

- private renders retained = 0;
- private screenshots committed = 0;
- private source files committed = 0;
- private text exports committed = 0;
- notes/media exports committed = 0;
- repository/staged privacy scan = pass.

Local raw structural profiles may remain in the ignored private root for the next approved resolver checkpoint, with cleanup required at final Phase 3 close.

## CP2-8 — execution-derived Checkpoint 2 QA

Create:

`thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

Its summary must be derived from Checkpoint 2 owning execution evidence, not literal PASS values.

Include at least:

- checkpoint ID;
- execution evidence ID/hash;
- pre-open gate results;
- alias resolution attempts/successes/failures;
- authorized source-session count;
- unexpected/unauthorized source attempts;
- three stable alias statuses;
- whole-source SHA-256 per alias;
- OOXML validation result per alias;
- slide count per alias;
- sanitized descriptor counts per alias/family;
- private render count;
- private render deleted count;
- private render retained count;
- private qualitative review status;
- forbidden export counts;
- sanitizer/privacy scan status;
- aggregate checkpoint status.

Any unauthorized source attempt, private leak, sanitizer failure, retained render, or incomplete source set must make aggregate status fail.

## Tests

Use RED → GREEN.

Add focused tests for at least:

- pre-open tracked-source privacy leak blocks access;
- production Observation rejects simulation/synthetic kinds;
- three stable aliases resolve only through local configuration;
- arbitrary path input rejected;
- unrecognized alias rejected;
- source attempt recorded before open;
- malformed/non-OOXML package blocked;
- source SHA/slide count derived correctly on synthetic PPTX fixture;
- read-only profiler does not mutate source hash;
- raw private output root remains ignored/untracked;
- sanitizer rejects text/notes/path/basename/URL/media/XML/package-hash fields;
- Exemplar 2 shell contamination rejected;
- structural scan operates without rendering;
- private-unapproved provider causes zero private renders and `blocked_visual_review`;
- approved synthetic private provider follows render→review→delete lifecycle;
- retained private render at checkpoint close fails;
- output descriptor schemas reject unknown/untyped fields;
- Checkpoint 2 QA cannot literalize PASS/counts independently of execution evidence.

Run the entire Phase 1–2 + Checkpoint 1 + Checkpoint 2 regression suite.

## Production-private access rules

This task authorizes access only to the three stable aliases above after all pre-open gates pass.

Do not print or commit actual local paths/basenames.

Do not send private exemplars/renders to a provider that is not explicitly approved for private content.

Do not extract private text/media/notes merely because OOXML access makes it technically possible.

## Not authorized

Do not:

- resolve shell conflicts into final professor grammar;
- produce final shell/body/figure grammar profiles;
- calibrate A01–A18;
- reconstruct a template/master/layout package;
- implement the full Figure director/render stack;
- create benchmark reconstruction slides;
- build the Phase 3 acceptance deck;
- claim professor visual fidelity PASS;
- claim production Group Meeting readiness;
- start Phase 4;
- globally/publicly register Skills.

## Report

Create:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

Include explicit CP2-PRE-1, CP2-PRE-2, and CP2-1 through CP2-8 traceability.

Do not include private paths/basenames, private text, screenshots, source titles, notes, or other forbidden values in the report.

## Delivery

Commit and push authorized Checkpoint 2 code, schemas, sanitized descriptors, QA artifact, tests, and report.

Verify remote state and remote artifact blobs.

Return exactly:

repository:
branch:
commit SHA:
pushed:
remote verification:

report path:

files added:
files modified:
files deleted:

tests/checks run:
tests passed:
tests failed:

CP2-PRE-1:
CP2-PRE-2:
CP2-1 through CP2-8 traceability:

production aliases expected/resolved:
authorized source sessions:
unauthorized private access attempts:

source validation summary by stable alias:
- private://template_primary_1:
- private://layout_exemplar_2:
- private://template_primary_3:

sanitized descriptor counts:
private renders created:
private renders deleted:
private renders retained:
private qualitative review status:
forbidden export counts:
repository/staged privacy scan status:
checkpoint aggregate status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_2_REVIEW: yes

Then STOP.

Do not begin the resolver/calibration checkpoint.
