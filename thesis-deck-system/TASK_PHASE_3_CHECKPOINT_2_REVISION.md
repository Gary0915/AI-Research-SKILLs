# Task — Phase 3 Checkpoint 2 Revision

## Scope

Correct only the remaining Checkpoint 2 blockers from `reviews/PHASE_3_CHECKPOINT_2_REVIEW.md`.

Do **not** begin the Professor Visual Grammar resolver/calibration checkpoint. Do not calibrate A01–A18, reconstruct a template, build production figures, build reconstruction benchmarks, assemble an acceptance deck, start Phase 4, or globally register Skills.

The three already-authorized production aliases may be reopened only through the existing Checkpoint 2 guarded local/private flow after all CP2 pre-open gates pass.

## CP2-B1 — Measured structural profiling sufficient for later calibration

Upgrade the shell/body profiler without extracting private scientific content.

### Shell descriptors — Exemplar 1 + Exemplar 3

Collect sanitized measured/derived evidence where structurally available for at least:

- slide dimensions;
- master count / layout count;
- sanitized master IDs / layout IDs;
- layout→master relationship topology;
- slide→layout relationship topology where needed;
- title-region geometry;
- recurring header/footer/page-number/navigation region geometry;
- recurring shell-object geometry/classes;
- measured/derived safe content bounds;
- margins/gutters where derivable;
- font family/size/weight/style role measurements using approved bounded font fields;
- fill/stroke/theme/color-role measurements permitted by sanitizer;
- shell primitive classes and recurrence counts.

Do not export text values, private layout/master names, raw XML, relationship XML, media names, or package-part hashes.

Do not use fixed constants such as a universal safe-content rectangle and label them as measured exemplar evidence.

Every descriptor field that is not directly measured must identify its evidence basis as one of:

- `measured`
- `derived`
- `not_observable_structurally`

Do not invent missing values.

### Body / figure descriptors — Exemplar 2

Collect data-minimized structural evidence for later Figure Skill and VisualStyleGovernor calibration, including where structurally observable:

- object/region normalized x/y/w/h;
- object class: text, picture, table, chart, native shape, connector/line, group;
- native primitive type / geometry class;
- group membership/structure using sanitized local IDs;
- connector/arrow orientation and endpoint geometry;
- line/fill/stroke/color/style roles;
- permitted font-role measurements;
- panel count / panel geometry;
- matrix row/column candidate geometry;
- comparison symmetry metrics;
- red/emphasis callout candidate geometry using style-role evidence, without private text;
- caption-region candidate geometry without caption text;
- annotation-region/count/density metrics;
- dominant-figure ratio;
- figure/text ratio;
- picture/schematic geometry relationship;
- whitespace/gutter measurements;
- recurring geometry/style counts.

Do not claim semantic certainty from structure alone. Each classification needs a confidence/evidence state such as:

- `structurally_supported`
- `provisional`
- `insufficient_structural_evidence`

Candidate-family vocabulary should support the approved families when evidence exists:

- formal_shell_divider
- hypothesis_problem
- photo_schematic
- control_proposed_comparison
- experiment_schematic
- result_single
- result_comparison
- result_discussion
- image_matrix
- fishbone_research_map
- fabrication_process_flow
- other_insufficient_structural_evidence

Do not force a family when structural evidence is insufficient.

## CP2-B2 — Fully typed fail-closed nested sanitizer boundary

Strengthen schemas and runtime sanitizer.

Requirements:

1. Every committed nested object/array item is fully typed.
2. Core nested objects use `additionalProperties:false`.
3. Arbitrary free text is forbidden from structural descriptors.
4. Strings must be controlled enums, sanitized IDs, approved font values, role IDs, or other explicitly bounded structural tokens.
5. Normalized geometry is bounded appropriately.
6. Runtime sanitizer constructs/validates a new sanitized object, not a deep copy of unchecked nested raw values.
7. Before write, validate the complete sanitized descriptor using the canonical schema + FormatChecker where applicable.

Negative tests must reject:

- arbitrary nested private text;
- note-like strings;
- unexpected nested keys;
- Windows/UNC/WSL paths;
- source basenames;
- URLs/DOIs;
- raw XML/relationship fragments;
- package-part identifiers/paths;
- media names;
- untyped free-form dictionaries;
- out-of-range normalized geometry.

## CP2-B3 — Structured private source-session lifecycle evidence

Replace the current informal `open:<alias>` event with a typed source-session lifecycle.

Before source file access record:

- sanitized session ID;
- stable alias;
- `started=true`;
- start event/order.

After each step record sanitized results for:

- regular-file validation;
- OOXML package validation;
- source hashing;
- structural profiling;
- sanitizer handoff;
- session closed/outcome.

Do not persist the path/basename.

Malformed/failed authorized source sessions must remain visible in execution evidence.

Final QA must distinguish:

- source session attempts;
- successful authorized closed sessions;
- failed sessions;
- unauthorized attempts.

Add consistency tests proving the final QA cannot hide a failed/partial session.

## CP2-B4 — No fabricated private render review

Provider capability/preflight alone must never increment render/review/delete counters or produce `reviewed_ephemerally`.

If actual render + hash-bound image-capable review + deletion is not implemented and authorized in this checkpoint:

- keep render counters at zero;
- set `private_qualitative_review_status` to `blocked_visual_review` or `not_run` as appropriate.

Add negative tests proving an approved provider object alone cannot synthesize a completed visual-review lifecycle.

No production private render is required by this revision.

## CP2-B5 — Descriptor-quality owning QA

Extend Checkpoint 2 execution-derived QA with owning checks/evidence for:

- shell descriptor structural completeness;
- body descriptor structural completeness;
- measurement-basis validity (`measured` / `derived` / `not_observable_structurally`);
- nested schema/sanitizer closure;
- shell/body authority separation;
- source slide count ↔ sanitized descriptor coverage consistency;
- zero prohibited fields after sanitization.

Aggregate Checkpoint PASS requires all these owning checks.

The QA artifact must not simply infer descriptor quality from the existence of output files.

## Privacy and data minimization

Preserve the exact legacy exception mechanism.

Raw profiler output remains ignored/local-only.

Do not collect/export slide text, speaker notes, comments, private URLs/citations/titles, author/company metadata, media filenames/bytes, chart caches, raw XML, relationship dumps, or package-part hashes.

Use only stable aliases in committed artifacts.

## Tests / checks

Use RED → GREEN.

Run at minimum:

- focused Checkpoint 1–2 tests;
- full Phase 1–2 + CP1 + CP2 regression suite;
- all Phase 3 schema validation;
- nested primitive/additionalProperties audit;
- production-private bounded rebuild of sanitized CP2 descriptors through the guarded aliases;
- descriptor-quality QA;
- Checkpoint 2 QA consistency validation;
- repository/staged privacy scan;
- raw-root ignored/untracked verification;
- `git diff --check`;
- remote branch/artifact verification.

## Artifacts

Regenerate only Checkpoint 2 artifacts as required:

- `thesis-deck-system/artifacts/phase3/sanitized-exemplar-manifest.json`
- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

Update:

`thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

with explicit CP2-B1 through CP2-B5 traceability.

## Delivery

Commit and push the correction to `origin/codex/thesis-deck-system`.

Verify remote head and required artifacts.

Return:

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

CP2-B1:
CP2-B2:
CP2-B3:
CP2-B4:
CP2-B5:

shell profiling summary:
- master/layout topology records:
- measured shell regions:
- typography/style records:
- fixed/default measurements presented as exemplar-derived: 0

body profiling summary:
- structural object records:
- connector/arrow records:
- group records:
- panel/matrix/comparison metrics:
- style/font/color-role records:
- candidate family counts by class/confidence:

nested schema/sanitizer negative tests:
source-session attempts/successes/failures:
private renders created/deleted/retained:
private qualitative review status:
descriptor-quality QA:
repository/staged privacy scan:
checkpoint aggregate status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_2_REVIEW: yes

Then STOP.

Do not begin the Professor Visual Grammar resolver/calibration checkpoint.
