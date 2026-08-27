# Thesis Deck System — Phase 1 Revision 3 Task

## Authorization

Reviewer verdict is `REVISE` in:

`thesis-deck-system/reviews/PHASE_1_REVISION_2_REVIEW.md`

This task authorizes **Phase 1 correction only**. Phase 2, public skill registration, and production Group Meeting acceptance remain unauthorized.

## Required reading

Synchronize the remote branch, then read completely:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/TASK_PHASE_1.md`
3. `thesis-deck-system/TASK_PHASE_1_REVISION.md`
4. `thesis-deck-system/TASK_PHASE_1_REVISION_2.md`
5. `thesis-deck-system/reviews/PHASE_1_REVIEW.md`
6. `thesis-deck-system/reviews/PHASE_1_REVISION_REVIEW.md`
7. `thesis-deck-system/reviews/PHASE_1_REVISION_2_REVIEW.md`
8. `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`
9. this file

## Mission

Correct every remaining blocker `P1-C1` through `P1-C7` without expanding the Phase 1 feature scope.

The goal is to remove remaining inconsistencies between Template Profile, materialized scientific history, Slide Specs, actual PPTX notes/layout relationships, canonical schemas, and QA evidence.

## Required corrections

### R3-1 — Self-consistent Template Profile layout identity

Refactor template profiling so every `layouts[]` record is derived from the actual runtime `python-pptx` `SlideLayout` object and has a stable pair:

- runtime `layout_index`;
- exact OpenXML `layout_path` / partname.

Do not assign runtime indexes from lexicographically sorted ZIP filenames.

Required invariants:

- for each layout index, the recorded path is the part actually represented by `prs.slide_layouts[index]`;
- each semantic role references one layout record whose `layout_index` and `layout_path` agree;
- assembler validates that the selected runtime layout part equals the role's expected `layout_path`;
- mismatch must raise/block; no fallback.

Add tests that deliberately corrupt either role index or role path and expect failure.

### R3-2 — Complete slide → layout → master → semantic-role audit

Extend `audit_pptx()` to report for every generated slide:

- Slide Spec / generated slide ID;
- actual slide part;
- actual slide → layout relationship ID and target;
- actual layout → master relationship ID and target;
- expected semantic role;
- expected role layout index/path from Template Profile;
- mapping-match boolean;
- notes relationship target;
- media refs.

Stage 6 must fail on any generated-slide mapping mismatch.

Persist the corrected `structural-audit.json`.

### R3-3 — Compile both first and revised slides only from materialized history

Create one deterministic content compiler whose input is a materialized ledger snapshot plus asset/profile lookup data.

Do not read scientific truth directly from fixture/bundle records after materialization for slide content.

Required behavior:

- first Observation comes from first materialized Observation Stage;
- first Discussion comes from first materialized Discussion Stage;
- first decision resolves that Discussion's `decision_ref`;
- first Next Step resolves the referenced Action at first cursor;
- revised Discussion comes from revision 2;
- revised decision resolves D002, not whichever decision was inserted first;
- revised Next Step resolves the current NS001 revision/status/timing;
- all Claim/Evidence refs come from the resolved materialized objects.

Add exact assertions:

- revised Slide Spec decision text equals D002 rationale;
- it must not equal D001 rationale;
- first/revised content matches the corresponding materialized snapshot.

### R3-4 — Finish canonical schema contracts

Strengthen the actual JSON Schemas so generated artifacts are validated for structure, not merely accepted as arbitrary nested objects.

At minimum:

#### Slide Spec

Constrain:

- `speaker_notes.source_refs` as Evidence IDs;
- `speaker_notes.text`;
- `story_visibility.master/meeting/defense` enums;
- `bindings.claim_refs/evidence_refs/asset_refs/action_refs` ID patterns;
- exact Professor/Template profile refs;
- `content` for both Phase 1 recipes using recipe-conditional schemas;
- placement slot and repository-relative path.

#### Deck Manifest

Constrain:

- block ref;
- Claim/Evidence/Asset/Action arrays;
- profile refs;
- story visibility;
- projection and output fields;
- no unvalidated contract-bearing nested object.

#### Asset Manifest

For `data_plot` require and constrain:

- generator kind/version/script/script SHA;
- input path/SHA;
- output SVG path/SHA and PNG path/SHA;
- transform-chain record;
- preview path;
- source Evidence refs.

For A002 constrain its observation source/preview identity appropriately.

#### Template Profile

Constrain layout/master records and semantic-role layout identity structures.

Add negative tests for malformed nested bindings/provenance/paths and role index/path mismatch.

### R3-5 — QA gates own the full required checks

#### Stage 1

Validate both first and revised generated Slide Specs and Deck Manifests, A001/A002, Evidence Cards, Template Profile, fixture contracts, and persisted ledger replay/materializations.

#### Stage 3

Verify the full A001 provenance chain:

- CSV file/hash;
- plot script file/hash;
- canonical SVG file/hash;
- PNG preview file/hash;
- top-level asset file/hash;
- transform-chain input/output hashes.

Verify A002 path/hash and E001–E003 source path/hash.

Tampering with any required provenance element must fail Stage 3.

#### Stage 4

Professor QA must consume the actual ledger-derived meeting projection/delta used for the build, not the static fixture placeholder.

Verify the unfinished prior commitment and current action state from that projection.

#### Stage 5

Verify generated deck exists and generated content slide count/IDs correspond to validated Slide Specs.

#### Stage 6

Depend on the complete R3-2 mapping audit plus SVG linkage, notes provenance, no orphan/broken parts, editable generated text, and no full-slide raster substitution.

#### Stage 7

Load the persisted visual-inspection record and validate:

- all expected generated slide entries exist;
- each entry has `status: pass`;
- referenced render files exist;
- image width/height are nonzero and plausible;
- blank/uniform-image heuristic does not trigger;
- full montage and changed-slide montage exist;
- inspection notes are nonempty.

Do not treat a nonempty inspection-record path as sufficient.

### R3-6 — PPT notes must match Slide Spec provenance

Assembler must generate notes from each Slide Spec's `speaker_notes` object.

Required acceptance:

- Observation generated slide notes contain E002 and do not falsely state E001 as the sole source;
- Result/Discussion notes contain E001 and E003 as specified;
- structural/content audit extracts/records source-note text or source IDs for generated slides;
- Stage 6 fails when PPT notes disagree with Slide Spec source refs.

### R3-7 — Remove or correctly implement `source_template_unchanged`

Do not set `source_template_unchanged = source_hash is not None`.

Either:

- remove the field; or
- record source-template SHA before assembly and verify the source file SHA after assembly is identical.

The generated PPTX SHA must remain a separate named field.

## Required tests

Add regression tests for at least:

1. Template Profile runtime layout index ↔ part path consistency for every layout.
2. Broken semantic-role layout index fails.
3. Broken semantic-role layout path fails.
4. Generated slide actual layout/master mapping matches expected semantic role.
5. Revised slide decision is D002-derived and not D001-derived.
6. First and revised slide scientific content is derived from corresponding materialized snapshots.
7. Malformed Slide Spec nested bindings/content fail schema.
8. Malformed Deck Manifest nested refs fail schema.
9. Broken A001 script/input/output provenance fails Stage 3.
10. Professor QA fails if the real meeting projection loses NS001.
11. Stage 6 fails on notes-source mismatch.
12. Stage 7 fails on missing render, zero/invalid dimensions, blank render, missing montage, missing/failed inspection entry.
13. Source template unchanged check is real or field is absent.
14. All previous required negative tests continue to pass.

## Artifact regeneration

Regenerate from a clean Phase 1 artifact directory:

- template/profile;
- A001/A002 + plot assets;
- ledger/materialized snapshots;
- first/revised Slide Specs;
- first/revised canonical PPTX;
- renderer compatibility PPTX copies if still needed;
- first/revised Deck Manifests;
- meeting delta;
- structural audit;
- visual inspection record;
- QA report;
- renders and montages;
- Phase 1 implementation report.

## Report

Update:

`thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`

Add `P1-C1`–`P1-C7` traceability with exact files/tests/artifacts.

Explicitly report:

- semantic-role index/path consistency evidence;
- generated slide layout/master mapping;
- revised D002 decision text evidence;
- first/revised materialized-state content derivation;
- full A001 provenance verification;
- notes-source extraction/match evidence;
- Stage 7 visual evidence checks.

## Delivery

Before `READY_FOR_REVIEW: yes`:

1. synchronize remote reviewer commits;
2. implement only Phase 1 corrections;
3. run full tests;
4. clean rebuild;
5. validate all schema-backed first/revised artifacts;
6. replay/materialize ledger from disk;
7. run QA Stage 1–7;
8. run relationship-aware slide/layout/master/notes audit;
9. render and inspect;
10. run canonical absolute-path scan;
11. run `git diff --check`;
12. commit/push;
13. verify remote head and key artifacts.

Final response must include the usual repository/branch/commit/delivery fields plus explicit `P1-C1`–`P1-C7` traceability.

Then stop. Do not begin Phase 2.