# Thesis Deck System — Phase 1 Revision 2 Task

## Authorization

Reviewer verdict is `REVISE` in:

`thesis-deck-system/reviews/PHASE_1_REVISION_REVIEW.md`

This task authorizes **Phase 1 correction only**. Phase 2, public skill registration, and production Group Meeting acceptance remain unauthorized.

## Required reading

Synchronize remote branch first, then read completely in this order:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/TASK_PHASE_1.md`
3. `thesis-deck-system/TASK_PHASE_1_REVISION.md`
4. `thesis-deck-system/reviews/PHASE_1_REVIEW.md`
5. `thesis-deck-system/reviews/PHASE_1_REVISION_REVIEW.md`
6. `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`
7. this file

## Mission

Repair blocking findings `P1-B1` through `P1-B9` without expanding scope. The goal is not more files; the goal is one internally consistent vertical slice in which committed scientific records, ledger history, Slide Specs, PPTX relationships and QA evidence all agree.

## Non-negotiable correction requirements

### C1 — Real SVG relationship, not detached package storage

Replace the current detached `ppt/media/plot-canonical.svg` workaround.

The result slide must have an actual slide relationship to the canonical SVG and the slide XML must reference that relationship.

Implement the smallest OpenXML bridge needed after python-pptx assembly.

Requirements:

- canonical plot remains SVG;
- PNG is compatibility preview/fallback only and must not be the sole scientific image used by the result slide;
- `[Content_Types].xml` contains SVG content type support as needed;
- result slide `.rels` contains the SVG relationship;
- result slide XML references the SVG relationship ID;
- structural audit reports `slide_id -> relationship_id -> ppt/media/...svg`;
- test fails if an SVG merely exists in the ZIP but is not referenced by the result slide.

If modern PowerPoint-compatible SVG insertion truly cannot be implemented, STOP and report the exact blocker. Do not claim P1-B1 resolved by packaging an unreferenced SVG.

### C2 — Actually strengthen the schemas

Update the canonical schemas, not only validator code.

At minimum:

- every patterned ID/path/date field has explicit type;
- Slide Spec schema defines `content`, semantic placement objects, bindings, profile refs, story visibility and repository-relative asset paths;
- Deck Manifest schema defines each slide entry including ordinal, spec path/hash, block ref, Claim/Evidence/Asset/Action refs, profile refs, cursor and visibility;
- Template Profile schema defines semantic role mapping to stable layout identity;
- Asset Manifest schema defines input/output/script/hash structures used by A001/A002;
- Evidence Card schema constrains source URI/hash and verification fields used in Phase 1;
- nested objects use `additionalProperties: false` where appropriate;
- canonical paths reject drive-letter / absolute machine-specific forms;
- semantic validation rejects duplicate/non-sequential manifest ordinals and dangling bindings.

Then validate the **exact committed/generated** Slide Specs, manifests, Asset Manifests, Evidence Cards and Template Profile through `SchemaRegistry`.

Add negative tests proving the old shallow schemas would no longer pass invalid values.

### C3 — Remove canonical absolute paths

No canonical YAML/JSON under the Phase 1 fixture/artifacts may contain local absolute paths.

Fix at least:

- `slide-specs-*.json` content fields;
- A001 top-level `path` / `preview_path`;
- any generated or fixture paths introduced elsewhere.

Use repository-relative POSIX paths in canonical records.

Implement one reusable path validator/resolver:

- canonical record stores repo-relative POSIX path;
- runtime resolves it against repository root only when accessing the filesystem.

Add a recursive test scanning canonical Phase 1 YAML/JSON and fail on Windows drive paths, UNC paths, or Unix absolute paths.

### C4 — Fix Evidence/Asset provenance and observation asset identity

Create a distinct committed observation Asset Manifest, e.g. `A002`, for the synthetic observation visual.

Bind:

- `photo_observation` -> A002 + E002;
- `hero_plot_discussion` -> A001 + E001/E003 as appropriate.

Replace all-zero Evidence hashes with actual hashes:

- E001 -> committed measurements CSV;
- E002 -> committed synthetic observation source;
- E003 -> create/use a separate committed synthetic literature source/note and hash that file. Do not self-hash E003.

Stage 3 must verify file existence and SHA-256 agreement for Evidence and Assets.

A001 provenance must verify:

- CSV path/hash;
- real plot script path/hash;
- SVG path/hash;
- PNG preview path/hash;
- generator/version;
- plot parameters;
- sample-SD policy;
- source Evidence refs.

### C5 — Make the ledger/materialized state the scientific source for slide compilation

Remove hard-coded `obs`, `res`, `res2` scientific truth from `build.py`.

After ledger serialization/reload:

- first build content must be derived from first materialized/replayed state;
- revised build content must be derived from revised materialized/replayed state;
- Discussion/Decision/Next Step strings shown on slides must come from the corresponding Stage/Decision/Action objects;
- Observation/problem content must come from committed Stage/Block/Evidence/Asset records.

If a presentation-specific summary is needed, implement a deterministic compiler/selector from the materialized objects. Do not duplicate the scientific meaning in build-local literals.

Also append the complete B001 record (or equivalent reconstructable events) so materialization can reconstruct normalized B001 rather than only a minimal block stub.

### C6 — Make meeting projection fully ledger-derived

Remove the manual `md.update(...)` patch that injects previous/current action truth.

`meeting_delta()` or a dedicated projection must derive from ledger history:

- previous commitment at/before `since_cursor`;
- current action state;
- owner;
- original target timing;
- revised target timing;
- blocker/closure evidence;
- source decision;
- parallelizable/workstream;
- changed block IDs.

Fix `stage_revised` block detection using `payload.block_ref.block_id` when appropriate.

For this scenario `changed_block_ids` must contain `B001` after Discussion v2.

Add a test that fails if B001 disappears from the delta despite a revised Stage after the cursor.

### C7 — Resolve semantic layout roles without fallback ambiguity

Template Profile must store a stable layout identity that the assembler can actually resolve, for example:

- layout index + OpenXML partname/path; and optionally
- human PowerPoint layout name.

Assembler must resolve `native_layout_role` using that stable identity.

Do not compare OpenXML part stems such as `slideLayout2` against unrelated human `SlideLayout.name` strings.

Do not silently fall back to `prs.slide_layouts[1]` if a required role cannot be resolved. Missing role/layout mapping is a blocking error.

Structural audit must report for each generated slide:

`slide -> layout part -> master part -> expected semantic role`

Add a test that deliberately breaks the role mapping and expects assembly/QA failure.

### C8 — Make structural PPTX QA relationship-aware

Expand `audit_pptx()` to produce explicit relationship evidence, not package-level booleans.

At minimum return:

- source template SHA-256 before assembly;
- generated PPTX SHA-256 separately;
- presentation slide ID/order;
- generated slide part paths;
- generated slide -> layout relationship target;
- layout -> master relationship target;
- expected semantic role per generated slide;
- generated slide -> media relationship IDs/targets/content types;
- notes relationship targets;
- internal relationship target validation;
- orphan/broken part list;
- editable text presence per generated slide;
- full-slide raster substitution check;
- result slide actual SVG relationship proof.

Rename/remove misleading fields. `source_template_hash` may not be the output deck hash.

Stage 6 PASS must depend on this relationship-aware evidence.

### C9 — Make QA gates truly execute their owning checks

Refactor Stage 1–7 so each PASS is backed by actual results.

Minimum ownership:

#### Stage 1 — schema/ledger integrity

Execute:

- SchemaRegistry validation of all canonical Phase 1 objects, including generated Slide Specs/manifests/assets/profile;
- referential checks;
- persisted `Ledger.load().replay()` hash/cursor validation;
- first/revised materialization consistency.

The `ledger` input must be used.

#### Stage 2 — scientific reasoning

Execute Scientific Method semantic checks on the committed/materialized B001 state, including Literature/Experiment/Discussion/Next Step.

#### Stage 3 — citation/evidence provenance

Execute Evidence/Asset path existence + hash verification and generated-context restrictions.

#### Stage 4 — professor style logic

Consume the referenced Professor Profile version and verify at minimum:

- actual research question exists before data;
- Literature synthesis exists;
- Discussion has decision + canonical Next Step;
- prior unfinished commitment appears in meeting view;
- owner/timing exist;
- failed-history reachability rule;
- `photo_observation` has observation visual with A002/E002 binding;
- `hero_plot_discussion` has actual plot + Discussion + decision + Next Step.

Use stable profile-derived finding IDs/paths.

#### Stage 5 — compile/assemble

Verify validated Slide Specs were assembled and the generated deck exists with expected generated slide IDs/count.

#### Stage 6 — structural PPTX

Use corrected relationship-aware audit, including result-slide SVG linkage and semantic layout mapping.

#### Stage 7 — render/montage visual

Do not accept an injected hard-coded `status: pass`.

Create persisted visual QA evidence that verifies:

- expected render files exist;
- slide count matches deck;
- image dimensions are nonzero/expected;
- montage files exist;
- no blank-render heuristic triggers;
- a human-inspection record exists with concrete notes for generated slides 3 and 4.

Stage 7 must consume that record.

### C10 — Persist QA evidence in reviewable form

`qa-report.json` should contain per-stage check details sufficient for reviewer inspection, not only generic strings such as `scientific validators`.

For each Stage 1–7 include, as appropriate:

- check IDs;
- paths/artifacts inspected;
- hashes/counts;
- result status;
- findings.

Native PowerPoint Stage 8 may remain `blocked_environment`; Stage 9 `not_run`; Stage 10 `blocked`.

## Required regression tests

In addition to all existing tests, add explicit tests for:

1. committed/generated Slide Specs validate against Slide Spec schema;
2. generated manifests validate against Deck Manifest schema;
3. generated A001/A002 validate against Asset Manifest schema;
4. evidence hashes match actual files and tampering fails;
5. recursive canonical path scan rejects absolute paths;
6. observation slide binds A002/E002, not A001;
7. broken semantic layout mapping blocks assembly;
8. generated slides report expected slide->layout->master relationships;
9. result slide `.rels` actually targets the SVG and slide XML references that relationship;
10. detached SVG without slide relationship fails Stage 6;
11. source template hash and output deck hash are distinct named audit fields;
12. first/revised slide content is derived from materialized history;
13. changed B001 appears in meeting delta;
14. manual/hard-coded meeting projection augmentation is unnecessary;
15. Stage 1 fails on invalid schema or tampered ledger;
16. Stage 3 fails on bad Evidence/Asset hash;
17. Stage 4 fails when the professor-required hero content field is removed;
18. Stage 7 fails when a render or inspection record is missing;
19. all previous 11 required negative tests still pass at expected gates.

## Visual QA

Rebuild and rerender after all source corrections. The reviewer is still not requiring final private NCKU styling in Phase 1, but generated slides must remain coherent and readable.

Persist a human-inspection JSON/YAML record for every generated content slide with at least:

- slide ID;
- render path;
- checked_by;
- checks performed;
- observations;
- status.

Do not fabricate native PowerPoint acceptance.

## Required regenerated artifacts

Regenerate from a clean Phase 1 artifact directory:

- complete fixture and any new synthetic source note;
- A001/A002 manifests;
- plot SVG/PNG;
- persisted ledger;
- materialized first/revised states;
- Slide Specs;
- first/revised PPTX;
- first/revised manifests;
- meeting delta;
- structural audit artifact;
- visual QA inspection record;
- QA report;
- individual renders/montages;
- implementation report.

## Report update

Update:

`thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`

Add a traceability table for `P1-B1` through `P1-B9` and explicitly state how each blocker was verified.

Do not merely repeat that tests pass. Give exact artifact paths and relationship/hash evidence.

## Delivery

Before saying ready:

1. run full test suite;
2. run clean end-to-end rebuild;
3. validate every generated schema-backed artifact;
4. reload/replay persisted ledger;
5. run Stage 1–7 gate execution;
6. run relationship-aware structural audit;
7. render/rerender;
8. generate/consume persisted visual inspection record;
9. run recursive absolute-path scan;
10. run `git diff --check`;
11. commit and push;
12. verify remote head and key artifacts.

Final response must contain:

- repository
- branch
- commit SHA
- pushed
- remote verification
- report path
- files added/modified/deleted
- tests/checks run
- tests passed/failed
- P1-B1–P1-B9 traceability
- schema validation summary for generated artifacts
- Evidence/Asset hash verification summary
- actual result-slide SVG relationship target
- generated slide layout/master mapping summary
- PPTX artifact paths
- Slide Spec/Manifest paths
- ledger/materialization paths
- meeting delta path/status
- structural audit path/status
- visual inspection record path/status
- render/montage paths
- QA report path/status
- native PowerPoint status
- known failures
- unresolved questions

Only then write:

`READY_FOR_REVIEW: yes`

and STOP. Do not begin Phase 2.
