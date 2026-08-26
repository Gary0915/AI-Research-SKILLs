# Phase 1 Thesis Deck Vertical Slice Implementation Plan

> **For agentic workers:** Execute inline in the required `codex/thesis-deck-system` branch. Use test-driven development for production behavior and preserve the reviewer checkpoints in `TASK_PHASE_1.md`.

**Goal:** Prove the approved architecture end to end with executable contracts, append-only history, a reproducible scientific plot, one Python PPTX backend, exactly two slide recipes, rendered QA evidence, and a meeting-delta rebuild.

**Architecture:** A single installable Python package validates versioned JSON/YAML contracts, appends and replays canonical ledger events, projects meeting state, compiles backend-neutral Slide Specs, and orchestrates the ten-stage QA pipeline. A single `python-pptx` worker implements `PptxAssembler`; Matplotlib creates the only quantitative plot; OpenXML inspection verifies template and generated-deck relationships.

**Tech stack:** Python 3.11, pytest, jsonschema, PyYAML, Matplotlib, Pillow, python-pptx, lxml, LibreOffice/PowerPoint environment detection.

---

### Task 1: Package skeleton and contract tests

**Files:**

- Create: `packages/thesis-deck-system/pyproject.toml`
- Create: `packages/thesis-deck-system/src/thesis_deck_system/contracts.py`
- Create: `packages/thesis-deck-system/tests/unit/test_contracts.py`
- Create: `thesis-deck-system/schemas/*.schema.json`

- [ ] Write failing tests that load all twelve schemas and reject each required invalid contract.
- [ ] Run `python -m pytest packages/thesis-deck-system/tests/unit/test_contracts.py -q` and confirm failures are caused by missing schemas/validators.
- [ ] Implement non-trivial JSON Schemas and semantic rules for referential integrity, scientific completeness, evidence roles, and release blocking.
- [ ] Re-run the contract tests and confirm green.

### Task 2: Append-only ledger and projections

**Files:**

- Create: `packages/thesis-deck-system/src/thesis_deck_system/ledger.py`
- Create: `packages/thesis-deck-system/src/thesis_deck_system/projections.py`
- Create: `packages/thesis-deck-system/tests/unit/test_ledger.py`
- Create: `packages/thesis-deck-system/tests/unit/test_projections.py`

- [ ] Write failing tests for canonical event hashes, monotonic cursors, replay from zero, revision preservation, legal independent status/visibility transitions, Claim supersession, Action closure, and commitment carry-forward.
- [ ] Confirm the tests fail because the implementation is missing.
- [ ] Implement minimal append/replay/materialization and meeting-delta behavior.
- [ ] Re-run the tests and confirm green.

### Task 3: Synthetic project and plot lineage

**Files:**

- Create: `thesis-deck-system/examples/synthetic-project/**`
- Create: `packages/thesis-deck-system/src/thesis_deck_system/plotting.py`
- Create: `packages/thesis-deck-system/tests/integration/test_plotting.py`

- [ ] Write a failing integration test for CSV aggregation, units, error bars, output hashes, and manifest bindings.
- [ ] Add clearly synthetic B001 contracts, local synthetic literature evidence, prior/current Actions, two ledger cursors, and the `zh-TW` Professor Profile.
- [ ] Implement the saved Matplotlib plot worker and cross-check values against the CSV.
- [ ] Generate and register SVG/PNG outputs, then confirm the integration test passes.

### Task 4: Synthetic native template and profiler

**Files:**

- Create: `packages/thesis-deck-system/src/thesis_deck_system/template.py`
- Create: `packages/thesis-deck-system/tests/integration/test_template_profile.py`
- Create: `packages/thesis-deck-system/tests/fixtures/synthetic_native_template.pptx`
- Create: `packages/thesis-deck-system/tests/golden/template-profile.json`

- [ ] Write a failing test for 16:9 size, masters/layouts, placeholders, theme fonts/colors, relationship IDs, semantic role mapping, and fixture hash.
- [ ] Generate the redistributable synthetic fixture from the default native PowerPoint package and add representative slides.
- [ ] Implement OpenXML profiling and deterministic normalized output.
- [ ] Run the profiler test and confirm green.

### Task 5: Slide compiler and one assembler backend

**Files:**

- Create: `packages/thesis-deck-system/src/thesis_deck_system/slides.py`
- Create: `packages/thesis-deck-system/src/thesis_deck_system/pptx.py`
- Create: `packages/thesis-deck-system/tests/unit/test_slides.py`
- Create: `packages/thesis-deck-system/tests/integration/test_pptx.py`

- [ ] Write failing tests for exactly `photo_observation` and `hero_plot_discussion`, deterministic Slide Specs, text budgets, allowed assets, stable bindings, and backend neutrality.
- [ ] Write a failing integration test for the `PptxAssembler` protocol and the single Python backend preserving native layout/master relationships, editable text, notes, and non-flattened vector/media content.
- [ ] Implement only the two recipes and only the Python backend.
- [ ] Re-run unit/integration tests and confirm green.

### Task 6: Canonical QA pipeline and negative matrix

**Files:**

- Create: `packages/thesis-deck-system/src/thesis_deck_system/qa.py`
- Create: `packages/thesis-deck-system/tests/unit/test_qa.py`
- Create: `packages/thesis-deck-system/tests/fixtures/invalid/*.yaml`

- [ ] Write failing tests for exact ten-stage order, downstream blocking, `blocked_environment`, critical release refusal, structural package checks, and all eleven required negative rule IDs/gates.
- [ ] Implement the minimal orchestrator and validators without bypassing upstream failures.
- [ ] Run the full negative matrix and confirm every invalid fixture blocks at the expected stage.

### Task 7: End-to-end builds, renders, and report

**Files:**

- Create: `packages/thesis-deck-system/src/thesis_deck_system/cli.py`
- Create: `packages/thesis-deck-system/tests/integration/test_vertical_slice.py`
- Create locally/ignored: `packages/thesis-deck-system/build/phase1/**`
- Create: `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`

- [ ] Write a failing vertical-slice test covering first build, appended Discussion/Action revision, revised Master Deck, and meeting delta.
- [ ] Implement the deterministic build command and run it twice.
- [ ] Render every slide with the available renderer, create full/changed montages, run structural and visual checks, and inspect each PNG plus montages.
- [ ] Run the complete test suite, inventory guard, `git diff --check`, schema/footer validation, and scope checks.
- [ ] Write the Phase 1 implementation report with exact paths, hashes, commands, matrices, blocked conditions, and `codex_report` footer.
- [ ] Commit all canonical Phase 1 files, push to `origin/codex/thesis-deck-system`, and verify the remote head/report/key schemas.
