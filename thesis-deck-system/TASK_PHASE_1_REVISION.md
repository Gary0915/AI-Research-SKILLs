# Thesis Deck System — Phase 1 Revision Task

## Authorization

Phase 1 reviewer verdict is `REVISE` in:

`thesis-deck-system/reviews/PHASE_1_REVIEW.md`

This task authorizes **Phase 1 correction only**. Phase 2 remains unauthorized.

## Required reading

Synchronize `origin/codex/thesis-deck-system`, then read completely:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/TASK_PHASE_1.md`
3. `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`
4. `thesis-deck-system/reviews/PHASE_1_REVIEW.md`
5. this file

Do not rely on your prior local state without syncing the remote reviewer commits first.

## Mission

Correct every blocking requirement `P1-R1` through `P1-R12` while preserving the approved Phase 0 architecture and the useful parts of the existing Phase 1 implementation.

This is **not** a rewrite from scratch and is **not** an invitation to expand scope. Fix the vertical slice so that the committed artifacts themselves prove the architecture end-to-end.

## Required corrected vertical slice

### 1. Committed complete B001 project bundle

The committed synthetic fixture must now include schema-valid records for:

- Research Block B001
- Observation Stage
- Literature Stage
- Mechanism Stage
- Solution Stage
- Experiment Stage
- Result Stage
- Discussion v1
- Discussion v2 / revised Discussion state
- Claims C001/C002/C003 and any additional required Claim
- Evidence Cards including E001/E002 as actually referenced
- Action Item / Next Step NS001 and revised state/revision where applicable
- Decision D001
- Professor Profile

Use a clear directory structure such as `stages/`, `evidence/`, `decisions/`, or equivalent. The exact structure may differ, but every reference in B001 must resolve to a committed object.

Create a fixture loader that reads the committed files, builds one bundle, runs SchemaRegistry + semantic validators, and fails on missing referenced files/IDs.

### 2. Use the real Ledger implementation for the build scenario

Do not manually construct a simplified event list in `build.py`.

The build must:

1. initialize/load Ledger,
2. append events through `Ledger.append()`,
3. serialize full Event records,
4. reload persisted events from disk,
5. verify hash/cursor continuity,
6. materialize state from zero,
7. prove prior revisions remain addressable,
8. use that materialized state/projection as input to the deck build.

Persist `timestamp`, `previous_hash`, and `event_hash`.

A persisted `stage_revised` event must contain the stage identity/content/revision required to replay it.

### 3. Make QA an execution pipeline, not a status template

Implement gate runners for the ten canonical stages. For Phase 1 they may remain bounded/simple, but each PASS must come from actual execution evidence.

Required minimum gate evidence:

- Stage 1: full committed fixture + persisted-ledger validation
- Stage 2: Scientific Method/Claim/Experiment/Literature/Discussion/Next-Step checks on committed B001
- Stage 3: Evidence Card + Asset provenance checks
- Stage 4: Professor Profile evaluator results
- Stage 5: Slide Spec compile + PPTX assembly results
- Stage 6: structural audit result
- Stage 7: render/montage automated checks + human-inspection record
- Stage 8: `blocked_environment` if native PowerPoint unavailable
- Stage 9: not run when Stage 8 blocks
- Stage 10: blocked when Stage 8 blocks

Do not pre-fill stages 1–7 as pass.

### 4. Consume Professor Profile

Create a deterministic `professor_qa` or equivalent that loads the exact profile version referenced by the build and emits stable findings.

For Phase 1 verify at least:

- question before data,
- Literature synthesis exists,
- Discussion contains decision + Next Step,
- prior unfinished commitment is carried into meeting view,
- owner/timing are present,
- failed-history reachability rule is enabled,
- `photo_observation` requires an observation visual,
- `hero_plot_discussion` requires plot + discussion/decision/next-step content.

Record profile rule IDs/paths in findings.

### 5. Implement the two recipes for real

`photo_observation` must include:

- a committed synthetic observation/photo-like asset (clearly synthetic),
- the visual in the expected semantic visual slot,
- observation/problem content,
- provenance/source binding.

`hero_plot_discussion` must include:

- scientific plot,
- Result/Discussion interpretation,
- decision state,
- canonical Next Step/timing summary,
- evidence/claim binding.

Recipe compilation must emit semantic slots. PPTX assembly must resolve `native_layout_role` via Template Profile rather than hard-code `slide_layouts[1]`.

### 6. Preserve vector scientific plot in PPTX

Prefer embedding the registered SVG in the PPTX. If python-pptx does not support the required SVG media path directly, implement the smallest OpenXML bridge needed.

Requirements:

- committed SVG remains the canonical plot asset,
- PNG remains preview/fallback only,
- PPTX structural audit identifies which media part the result slide uses,
- Stage 6 fails if the result slide silently uses only the PNG when vector media is required by the Phase 1 contract.

If this proves technically impossible in the chosen backend, stop and report the exact technical blocker before claiming acceptance; do not silently downgrade.

### 7. Persist Slide Specs and strengthen Deck Manifest

Persist reviewable Slide Spec files for first and revised builds.

Fix Manifest records:

- unique ordinal sequence,
- slide ID,
- Slide Spec revision/path/hash,
- Block ID + revision,
- Claim refs,
- Evidence refs,
- Asset refs,
- Action refs,
- Professor Profile ID/version,
- Template Profile ID/version,
- source cursor,
- story visibility.

Add semantic validation for duplicate ordinals and dangling Slide Spec/source bindings.

### 8. Expand structural PPTX audit

At minimum inspect and report:

- package content types,
- all internal relationship targets,
- presentation slide IDs/order,
- generated slide → layout relationship,
- layout → master relationship,
- expected semantic layout role,
- media refs/types per generated slide,
- notes refs,
- source-template hash before/after copy/assembly,
- no orphan parts,
- no full-slide screenshot substitution,
- editable text presence,
- vector media use for the plot.

Update integration tests accordingly.

### 9. Fix plot provenance

Use a real repository-relative script source path and hash.

Asset manifest must record at minimum:

- input CSV path/hash,
- plot script path/hash,
- SVG path/hash,
- PNG preview path/hash,
- Matplotlib version,
- plot parameters,
- sample-SD/error-bar policy,
- transform description,
- source Evidence Card binding.

The provenance test must fail if the recorded script is missing or changed.

### 10. Normalize canonical paths

Canonical YAML/JSON manifests must use repository-relative `/` paths.

Reject Windows drive-letter absolute paths and other machine-specific absolute paths in canonical records.

Runtime logs may separately record local paths if necessary.

### 11. Make the revision scientifically meaningful

The first and revised states must differ in actual scientific state, not only revision numbers.

Required demonstration:

- Discussion v1 contains an interpretation/decision.
- A later event creates Discussion v2 with a changed/updated interpretation, evidence gap, or decision.
- The canonical Next Step is revised or newly selected as a consequence.
- The revised `hero_plot_discussion` slide visibly contains the new interpretation/decision/next-step state.
- Meeting delta identifies prior commitment, current status, revised/new next action, owner, timing, blocker/closure evidence, decision binding and parallel workstream.

### 12. Strengthen schemas/validation

Correct shallow schema behavior found by the reviewer:

- use explicit `type: string` for IDs/patterned strings,
- use explicit types for date/time fields,
- use `FormatChecker` when validating formats,
- constrain nested Slide Spec/Deck Manifest bindings,
- constrain Template Profile semantic-role/layout structures,
- constrain evidence/asset provenance structures used in Phase 1,
- reject duplicate/invalid ordinal/binding scenarios through schema or semantic validation.

Add targeted negative tests for these corrections.

## Visual QA requirement

After rebuilding:

- regenerate individual slide PNGs,
- regenerate full montage,
- regenerate changed-slide montage,
- inspect all revised slides,
- report concrete findings per generated content slide.

The reviewer is not asking for final NCKU/AMPL styling yet. The reviewer is asking that the two Phase 1 recipes be real, internally coherent research layouts rather than placeholders.

Do not expand to the full recipe library.

## Required tests/evidence before submission

In addition to the existing suite, add tests proving:

- committed fixture loader resolves every B001 reference,
- persisted ledger reload/replay/materialize passes,
- persisted stage revision is replayable,
- Professor Profile actually changes/enables Professor QA behavior,
- recipe → semantic layout resolution works,
- `photo_observation` contains an observation visual,
- result slide uses SVG/vector plot media,
- Manifest ordinals are unique/sequential,
- Manifest per-slide scientific bindings resolve,
- canonical paths are repository-relative,
- structural audit validates generated slide layout/master/media/notes,
- plot script hash is real and verified,
- revised Discussion/Next Step content differs meaningfully,
- QA Stage 1–7 statuses are generated by actual gate results,
- existing eleven required negative cases still pass at the expected gate.

## Artifacts to regenerate

Regenerate, do not patch in place by hand:

- synthetic template/profile if needed,
- complete synthetic fixture,
- plot SVG/PNG + manifest,
- ledger event stream,
- materialized state snapshot if used,
- persisted Slide Specs,
- first Master PPTX + manifest,
- revised Master PPTX + manifest,
- meeting delta,
- QA report,
- render directories/montages,
- Phase 1 implementation report.

## Report update

Update/replace:

`thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`

Add a traceability table:

`P1-R1` through `P1-R12` → implementation files/tests/artifacts that prove each correction.

Do not claim `READY_FOR_REVIEW: yes` unless every correction is committed and remotely verified.

## Delivery gate

After implementation:

1. run full Phase 1 test suite,
2. run fixture/ledger replay checks,
3. regenerate artifacts from a clean Phase 1 artifact directory,
4. run structural QA,
5. render/rerender and inspect,
6. validate report/footer,
7. run `git diff --check`,
8. commit/push,
9. verify remote branch head,
10. verify key text/binary paths exist remotely.

Final Codex response must include:

- repository
- branch
- commit SHA
- pushed
- remote verification
- report path
- files added/modified/deleted
- tests/checks run
- tests passed/failed summary
- P1-R1–P1-R12 traceability
- PPTX artifact paths/status
- Slide Spec paths
- ledger/replay artifact paths
- render/montage paths
- QA report path/status
- native PowerPoint status
- known failures
- unresolved questions

Then:

`READY_FOR_REVIEW: yes`

and stop. Do not begin Phase 2.
