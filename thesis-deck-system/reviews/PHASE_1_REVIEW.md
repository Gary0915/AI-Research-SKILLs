# Phase 1 Reviewer Verdict — REVISE

Reviewed remote implementation commit: `de3cf38a8c63d08d6ab573fa367eb25902b45316` on `codex/thesis-deck-system`.

## Verdict

**REVISE. Phase 1 is not approved and Phase 2 is not authorized.**

The implementation establishes a useful skeleton: one Python control plane, twelve JSON Schemas, a single PPTX backend, a synthetic PPTX fixture, reproducible Matplotlib outputs, first/revised PPTX artifacts, render/montage artifacts, a negative-test matrix, and an honest `blocked_environment` native-PowerPoint status. However, several Phase 1 acceptance claims are currently stronger than the implementation actually demonstrates.

The following items are blocking because they affect the core contract, not cosmetic polish.

## What is accepted in principle

- One Python package/control plane was used; no duplicate JS PPTX stack was added.
- Twelve schema files exist and are parsed with Draft 2020-12 validation.
- Claim, research-question, action-item, research-status/story-visibility concepts are present.
- A synthetic CSV is used for a Matplotlib plot; no image generation is used for quantitative evidence.
- The system generates PPTX files from a copied template and preserves editable text.
- Render, montage, PDF and PNG artifacts were committed.
- Native PowerPoint acceptance is correctly reported as blocked rather than falsely passed.
- Required negative rule IDs exist and tests exercise the intended failure categories.

These parts should be preserved while correcting the blocking defects below.

---

## Blocking requirements

### P1-R1 — The committed B001 fixture does not actually contain the eight structured Scientific Method stages

`examples/synthetic-project/block.yaml` references `ST-OBS`, `ST-LIT`, `ST-MECH`, `ST-SOL`, `ST-EXP`, `ST-RES`, and `ST-DISC`, and references `E001`/`E002`, but the committed synthetic-project directory contains only:

- `actions.yaml`
- `block.yaml`
- `claims.yaml`
- `measurements.csv`
- `professor-profile.yaml`

There are no committed Stage records and no Evidence Card records in that fixture.

This means the Phase 1 claim that B001 contains all eight machine-addressable stages is not demonstrated by the committed project fixture. The tests use separate in-memory dictionaries, which does not substitute for the required end-to-end fixture.

**Required correction:**
- Add committed schema-valid Stage records for Observation, Literature, Mechanism, Solution, Experiment, Result, and Discussion.
- Add committed schema-valid Evidence Cards including the synthetic measurement evidence and clearly synthetic literature/observation evidence needed by the stage graph.
- Load the committed fixture as one bundle and validate all Block/Stage/Claim/Evidence/Action/Profile references together.
- The fixture validation test must fail if any referenced Stage/Evidence file is absent.

### P1-R2 — The committed ledger artifact bypasses the implemented append-only Ledger and is not replayable as claimed

`build.py` manually creates `events = [...]` dictionaries instead of generating the committed history through `Ledger.append()`.

The committed `ledger-events.json` has no `timestamp`, `previous_hash`, or `event_hash`. Its `stage_revised` event contains no `stage_id`, while `Ledger.materialize()` requires `payload["stage_id"]` for `stage_revised`.

Therefore the committed artifact is not the serialized output of the implemented Ledger and cannot prove hash-chain replay/materialization from disk.

**Required correction:**
- Build the Phase 1 scenario by calling `Ledger.append()` for every event.
- Serialize the resulting full Event records including cursor, timestamp, previous_hash, and event_hash.
- Implement reload/deserialization from the committed JSON/JSONL event stream.
- Replay the persisted event stream from zero and materialize it without special in-memory state.
- Add a test that loads the committed ledger artifact and reconstructs normalized B001, Claims, Stages, Action Items and Decisions.
- Demonstrate prior revisions remain retrievable/addressable after the revised build.

### P1-R3 — The QA pipeline currently assigns PASS statuses; it does not orchestrate the actual gates

`qa.run_pipeline()` constructs statuses with `["pass"] * 7`. It does not invoke SchemaRegistry, semantic scientific validation, provenance validation, Professor Profile evaluation, assembly, structural audit, render checks, or visual findings.

As a result, `qa-report.json` says Stages 1–7 pass even though the committed fixture is missing its Stage/Evidence objects.

**Required correction:**
- Make the Phase 1 pipeline execute real gate functions and record their evidence/results.
- Stage 1 must validate the persisted fixture/ledger and reference graph.
- Stage 2 must run Scientific Method validators on the actual committed B001.
- Stage 3 must validate Evidence/Asset provenance on actual objects.
- Stage 4 must consume the Professor Profile.
- Stage 5 must compile/assemble actual Slide Specs.
- Stage 6 must consume the structural audit result.
- Stage 7 must consume render/montage checks and visual findings.
- Stage 8 may remain `blocked_environment`.
- Downstream statuses must be derived from execution, not pre-filled.
- QA report findings must include rule ID, severity, path/object/slide, evidence, and repair action where applicable.

### P1-R4 — Professor Profile exists but Professor QA does not consume it

The project-level `professor-profile.yaml` is a good start, but `qa.py` only writes a profile reference into the report. `build.py` does not load the profile and no Professor-QA function evaluates its rules.

This fails the approved requirement that professor-specific logic be project input rather than decorative metadata.

**Required correction:**
- Load and schema-validate the exact Professor Profile version used for the build.
- Implement a bounded Phase 1 Professor-QA evaluator using that profile.
- At minimum check: research question before data, literature synthesis, discussion→decision/next step, prior commitments, owner/timing, failed-history reachability, and the two Phase 1 content recipe requirements.
- Record which profile rule generated each finding.

### P1-R5 — The two slide recipes are declared, but the PPTX assembler does not implement their semantic layout contract

`slides.py` defines `photo_observation` and `hero_plot_discussion`, but `PythonPptxAssembler` always selects `prs.slide_layouts[1]` and ignores `native_layout_role`/`template-profile.json`.

`photo_observation` does not place a photo at all; it produces text saying `Synthetic fixture • photo_observation`. `hero_plot_discussion` uses hard-coded inch coordinates rather than semantic slots derived from the selected recipe/profile.

**Required correction:**
- Resolve `native_layout_role` through the generated Template Profile.
- Instantiate the resolved native layout rather than hard-code layout index 1.
- Implement semantic slots for each recipe.
- `photo_observation` must contain an actual synthetic observation/photo-like fixture asset plus observation/interpretation content.
- `hero_plot_discussion` must contain the plot and an actual discussion/decision/next-step summary, not only `Claim: C001 / Evidence: E001` labels.
- Add tests proving the two recipes resolve to their expected layout/slots.

### P1-R6 — The plot is inserted as PNG, so the deck does not demonstrate the requested vector/editable plot path

`build.py` assigns `plot["png"]` to the slide placement and `pptx.py` inserts that raster image. The SVG is committed separately but is not the asset used in the deck.

**Required correction:**
- Use the SVG/vector asset in the generated PowerPoint if the Python backend can preserve it.
- If the high-level library cannot, implement the smallest reviewed OpenXML bridge needed to embed SVG while keeping a PNG fallback only for compatibility/preview.
- Structural QA must confirm the slide references the vector media part, not only the PNG.
- If an unavoidable backend limitation remains, report it explicitly instead of claiming editable/vector content passed.

### P1-R7 — Deck Manifest does not bind each slide to the required scientific sources, and its ordinals are invalid

`MASTER-PHASE1-REVISED.manifest.json` contains two slide entries that both have `ordinal: 1`.

Per-slide records contain only slide ID, spec revision and visibility. They do not bind each slide to block revision, Claim IDs, Evidence IDs, Action IDs, Professor/Profile versions, Template/Profile version and source cursor as required by the Phase 1 acceptance criteria.

**Required correction:**
- Use unique sequential ordinals.
- Persist Slide Specs (or content-addressed Slide Spec references/hashes) as reviewable artifacts.
- Each manifest slide record must either carry or resolve deterministically to Block revision, Claims, Evidence, Assets, Actions, Professor Profile, Template Profile, and cursor.
- Add semantic validation for unique ordinals and dangling slide/spec bindings.

### P1-R8 — Structural PPTX QA is substantially below P1.14

`audit_pptx()` currently checks counts, some relationship targets, whether any editable text exists, and orphan parts. The integration test only asserts slide count, editable text, and no orphan relationship target.

It does not prove:
- expected layout/master relationship for each generated slide,
- unique slide IDs/order,
- content types,
- notes relationships,
- media relationships,
- vector-vs-raster scientific asset identity,
- unchanged source-template package binding/hash,
- generated-slide semantic layout role.

**Required correction:**
- Expand structural audit to the P1.14 checklist.
- Record generated-slide → layout → master relationships and compare them with Template Profile roles.
- Validate unique slide IDs and order.
- Validate content types and all internal relationship targets.
- Validate notes/media refs used by generated slides.
- Verify source template remains unchanged by hash.
- Detect full-slide raster substitution.
- Verify the scientific plot's media type/path.

### P1-R9 — Plot provenance is incomplete and the recorded script path is not real

`plotting.py` writes `generator.script: "plot.py"`, but no such saved plot script exists in the fixture/artifact set. The manifest does not record a plot-script SHA-256 even though Phase 1 requires data/script/output hashes.

**Required correction:**
- Make the plot generator source path real and repository-relative, or add a dedicated saved plotting script.
- Record input CSV hash, script hash, SVG hash, PNG preview hash, Matplotlib version, parameters, and uncertainty/error-bar policy.
- Add a provenance test that fails if the recorded script does not exist or its hash changes.

### P1-R10 — Committed manifests/QA use developer-machine absolute paths

Committed artifacts contain paths such as `D:/Gary/.../thesis-deck-system/...`.

This violates the architecture's repository-relative path rule and makes committed manifests non-portable/non-reproducible on another machine.

**Required correction:**
- Store canonical artifact/source paths as repository-relative POSIX-style paths.
- If useful, runtime absolute paths may appear only in a non-canonical execution log, not the committed manifest contract.
- Add validation that rejects drive-letter/absolute paths in canonical manifests where a repository-relative path is expected.

### P1-R11 — The revised scenario does not demonstrate a real Discussion revision and revised canonical Next Step

The revised build bumps a Slide Spec revision and changes NS001 status from `planned` to `in_progress`, but the committed event stream does not contain a complete revised Discussion object and does not persist a revised Action Item object/selection. The result slide's generated content remains generic.

**Required correction:**
- Persist Discussion v1 and Discussion v2 (or revisions in the event-backed state) with a meaningful scientific change.
- Persist Action Item/Next Step revision or selection change caused by the revised Discussion.
- The revised result/discussion slide must visibly reflect the changed interpretation/decision/next step.
- Meeting delta must distinguish prior commitment, current status, revised next action, timing, blocker/closure state, and source decision.

### P1-R12 — Several schemas parse but are not strict enough for the claimed contract

Examples: many string fields use `pattern` or `format` without explicit `type: string`; date-time `format` is not enforced because SchemaRegistry does not use a `FormatChecker`; Deck Manifest's slide items are nearly unconstrained, which allowed duplicate ordinals and missing scientific bindings.

**Required correction:**
- Add explicit types to ID/date/path fields.
- Use `FormatChecker` for date/time validation.
- Strengthen Deck Manifest, Slide Spec, Template Profile, Professor Profile, Evidence Card and Asset Manifest nested object definitions enough to reject the defects above.
- Add targeted schema-negative tests, not only `schema != empty object` tests.

---

## Visual/content-layout reviewer note

The current generated slide code is still a mechanical smoke test rather than a credible implementation of the two research-layout recipes. This is acceptable as an intermediate implementation state, but not as Phase 1 acceptance because `photo_observation` contains no photo and the assembler ignores the template-profile semantic role. The revised Phase 1 must demonstrate the content-layout mechanism, even though final professor visual fidelity remains gated on the private exemplar PPTX files.

Do **not** spend Phase 1 revision effort on full NCKU/AMPL visual styling or the complete recipe library. Fix the two approved recipes correctly first.

## Native PowerPoint

`blocked_environment` for native PowerPoint remains accepted for the synthetic revision. Do not attempt to hide or bypass this gate. Production Group Meeting acceptance still requires the later private/template fixture and native Windows PowerPoint environment.

## Phase boundary

- Phase 1 status: **REVISE**
- Phase 2: **NOT AUTHORIZED**
- Public skill registration: **NOT AUTHORIZED**
- Production Group Meeting use: **NOT AUTHORIZED**

Codex must correct P1-R1 through P1-R12, rerun the entire Phase 1 vertical slice, regenerate artifacts/reports, and wait for review again.
