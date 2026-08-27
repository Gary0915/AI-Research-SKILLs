# Phase 3 Professor Visual Fidelity TDD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved private-exemplar sanitized calibration pipeline, reconstruct a non-private professor-style native template, calibrate A01–A18 and Fishbone appearance, and generate a ledger-derived Phase 3 acceptance deck with honest privacy, reconstruction, visual, Professor, and native-PowerPoint gates.

**Architecture:** Private PPTX inspection is confined to a data-minimized ignored local domain. A fail-closed allowlist sanitizer produces the only contracts visible to shell/body resolvers, calibration, the existing `PythonPptxAssembler`, benchmarks, and QA. The approved Phase 1–2 Ledger, temporal, scientific, provenance, N-layer, Fishbone-history, and field-level presentation contracts remain the sole scientific control plane.

**Tech Stack:** Python 3.11+, pytest, jsonschema Draft 2020-12, python-pptx behind `PythonPptxAssembler`, lxml/zipfile for read-only OOXML inspection and adapter-owned package QA, Pillow/LibreOffice/Poppler for rendering evidence, and Codex `functions.view_image(detail=original)` for image-capable qualitative review.

---

## 1. Scope and invariants

This plan implements
`designs/PHASE_3_VISUAL_FIDELITY_DESIGN.md` and P3P-1–P3P-8 from
`reviews/PHASE_3_DESIGN_FINAL_REVIEW.md`. Production implementation may start
only after this plan is approved.

Implementation must not change these approved invariants:

- the Ledger is append-only, persisted, hash-verified, reloaded, replayed, and
  cursor-materialized before story or scientific presentation decisions;
- Master projection contains every Hypothesis Layer in causal creation order;
- Hypothesis and Problem remain separate audience-visible roles;
- every layer binds an immutable historical Fishbone revision and focus;
- every Slide Spec uses a stage-aware source cursor and graph-closed bindings;
- field-level scientific contracts remain audience-visible and QA-owned;
- Evidence/Asset/notes/decision/action provenance remains intact;
- `PythonPptxAssembler` is the only PPTX assembly backend;
- direct OOXML code is read-only profiling/QA or adapter-internal package
  construction, never an independent assembler;
- missing private evidence never triggers synthetic fallback presented as
  professor fidelity;
- generated imagery never masquerades as experimental or literature evidence;
- native PowerPoint Stage 8 and production readiness remain independent;
- no Phase 4 or global/public Skill registration occurs.

The implementation changes visual calibration only. Private exemplars are not
scientific inputs and may not influence Claims, Evidence, Research Blocks,
Stages, Decisions, Actions, Hypothesis transitions, or source cursors.

## 2. Phase 3 implementation dependency graph

```text
P1 contracts/privacy boundary
 └─hard→ P2 private profiler
          ├─hard→ P3a shell profile/resolver (Exemplar 1/3)
          └─hard→ P3b body profile/resolver (Exemplar 2)
                    P3a + P3b
                       └─hard→ P4 calibration + template reconstruction
                                  ├─hard→ P5 reconstruction benchmarks
                                  └─hard→ P6 ledger-derived acceptance deck
                                               P5 + P6
                                                  └─hard→ P7 complete QA/report
```

Parallelization:

- P3a and P3b may run in parallel after P2 has produced separately sanitized
  shell and body inputs.
- In P4, A01–A18 token calibration and Fishbone style calibration may run in
  parallel after the resolved grammar exists; reconstructed-template assembly
  waits for shell calibration.
- P5 benchmark metric computation and P6 scientific projection preparation may
  run in parallel, but PPTX assembly in P6 waits for the reconstructed template
  and calibrated archetypes.
- P7 waits for every required P5/P6 artifact and never upgrades a blocked
  prerequisite.

Hard prerequisites:

- the ignored-storage guard must pass before a private PPTX is opened;
- sanitizer tests and repository privacy scan must pass before a sanitized
  profile is written under a tracked path;
- shell resolver must have no hard conflict before template reconstruction;
- all used archetypes must be calibrated before acceptance assembly;
- benchmark and rendered-image evidence must exist before professor visual
  fidelity can pass.

## 3. File/module plan

### 3.1 Source modules

| Path | Change | Domain | Responsibility | Owning tests | Consumers |
| --- | --- | --- | --- | --- | --- |
| `packages/thesis-deck-system/src/thesis_deck_system/contracts.py` | modify | sanitized | register Phase 3 schemas without altering Phase 1–2 validation | `test_phase3_contracts.py` | all Phase 3 producers |
| `packages/thesis-deck-system/src/thesis_deck_system/private_fixtures.py` | modify | private boundary | stricter alias/package validation and stable alias/hash record | `test_phase3_profiler.py` | profiler |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_privacy.py` | new | boundary | ignored-root guard, canaries, allowlist construction, lexical/binary/repository scans | `test_phase3_privacy.py` | profiler, build, report |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_profiler.py` | new | private | data-minimized OOXML/style/geometry profiler and local raw store | `test_phase3_profiler.py` | profile sanitizer |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_profiles.py` | new | sanitized | shell/body sanitization, authority resolver, conflict evidence, visual grammar | `test_phase3_resolvers.py` | calibration, QA |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_metrics.py` | new | sanitized/local comparator | exact geometry, typography, color, pixel, and Fishbone metric formulas | `test_phase3_metrics.py` | benchmark, visual QA |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_calibration.py` | new | sanitized | A01–A18 and Fishbone token calibration with immutable contract hashes | `test_phase3_calibration.py` | Layout Director, Fishbone renderer |
| `packages/thesis-deck-system/src/thesis_deck_system/layout.py` | modify | sanitized | consume calibrated registry/grammar without changing semantic role mapping | `test_phase3_calibration.py`, Phase 2 tests | Layout Plans |
| `packages/thesis-deck-system/src/thesis_deck_system/fishbone.py` | modify | sanitized | accept style tokens while preserving canonical graph/history | `test_phase3_calibration.py` | SVG renderer |
| `packages/thesis-deck-system/src/thesis_deck_system/pptx.py` | modify | sanitized adapter | add adapter-owned reconstruction/assembly entrypoints and package audit | `test_phase3_reconstruction.py` | Phase 3 build |
| `packages/thesis-deck-system/src/thesis_deck_system/pptx_reconstruction.py` | new, private to adapter | sanitized adapter | construct fresh master/layout/theme/docProps parts only when called by `PythonPptxAssembler` | `test_phase3_reconstruction.py` | `pptx.py` only |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_benchmark.py` | new | split local/sanitized | select difficult families and emit sanitized metric records | `test_phase3_benchmarks.py` | QA/report |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_build.py` | new | sanitized | orchestrate Ledger.load→projection→calibration→single-backend PPTX | `test_phase3_acceptance_build.py` | CLI/report |
| `packages/thesis-deck-system/src/thesis_deck_system/phase3_render.py` | new | sanitized/local | render, montage, pixel evidence, review-request and review finalization | `test_phase3_visual_review.py` | QA/report |
| `packages/thesis-deck-system/src/thesis_deck_system/qa3.py` | new | sanitized | owning Phase 3 gates and report facts | `test_phase3_qa.py` | final pipeline |
| `packages/thesis-deck-system/src/thesis_deck_system/cli.py` | modify | boundary | explicit Phase 3 profile/build/verify commands; no implicit fallback | integration tests | operator |

`pptx_reconstruction.py` has no public CLI or assembler class. Its functions
require a `PythonPptxAssembler`-owned call token/context, and a dependency scan
test fails if another module imports it directly.

### 3.2 Schemas

Create under `thesis-deck-system/schemas/`:

- `sanitized-exemplar-manifest.schema.json`
- `shell-profile.schema.json`
- `body-composition-profile.schema.json`
- `professor-visual-grammar-v3.schema.json`
- `fishbone-style-profile.schema.json`
- `archetype-calibration.schema.json`
- `reconstruction-benchmark.schema.json`
- `reconstruction-manifest.schema.json`
- `image-capable-visual-review.schema.json`
- `phase3-report-facts.schema.json`

### 3.3 Tests and non-private fixtures

Create:

- `packages/thesis-deck-system/tests/unit/test_phase3_contracts.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_privacy.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_profiler.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_resolvers.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_metrics.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_calibration.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_reconstruction.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_benchmarks.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_visual_review.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_qa.py`
- `packages/thesis-deck-system/tests/integration/test_phase3_private_pipeline.py`
- `packages/thesis-deck-system/tests/integration/test_phase3_acceptance_build.py`
- `packages/thesis-deck-system/tests/integration/test_phase3_regressions.py`
- `packages/thesis-deck-system/tests/fixtures/phase3/` containing only generated,
  redistributable OOXML fixtures and explicit privacy canaries.

### 3.4 Repo-local Skill routing

Modify only after calibrated profiles exist:

- `thesis-deck-system/skills/thesis-deck-router/SKILL.md`
- `thesis-deck-system/skills/hypothesis-layer-planner/SKILL.md`
- `thesis-deck-system/skills/fishbone-director/SKILL.md`
- `thesis-deck-system/skills/layout-director/SKILL.md`
- `thesis-deck-system/skills/professor-qa/SKILL.md`
- `thesis-deck-system/skill-routing.yaml`

These remain repository-local and unregistered.

## 4. TDD red-green-refactor matrix

The plan adds **116 new RED test cases**, including parameterized cases. Each
production change begins only after its owning test is observed failing for the
expected missing behavior.

### Phase 1 — Contracts and privacy boundary: 22 RED cases

**RED first**

- schema registration and nested-type failures for all ten schemas;
- `.private/` missing/trackable/outside-root guards;
- unknown sanitizer key and unbounded string rejection;
- path, text, notes, metadata, URL/DOI, media-name, binary, screenshot, PPTX,
  and staged/tracked leakage cases;
- stable alias/SHA/profile-ID positive boundary.

Representative test API:

```python
def test_sanitizer_rejects_unknown_nested_field():
    raw = synthetic_raw_profile()
    raw["canvas"]["unexpected"] = "must-not-cross"
    with pytest.raises(PrivacyBoundaryError, match="unknown_field"):
        sanitize_profile(raw, policy=phase3_policy(), canaries=CanarySet.empty())

def test_private_root_must_be_git_ignored(repo_root, tmp_path):
    store = PrivateProfileStore(repo_root / ".private" / "phase3", repo_root)
    with pytest.raises(PrivacyBoundaryError, match="private_root_not_ignored"):
        store.assert_safe_before_open()
```

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/unit/test_phase3_contracts.py packages/thesis-deck-system/tests/unit/test_phase3_privacy.py
```

Expected: collection errors for missing Phase 3 schemas/modules, not syntax or
fixture errors.

**GREEN minimum**

- add ten valid Draft 2020-12 schemas and Phase 3 registry opt-in;
- implement `PrivateProfileStore.assert_safe_before_open()`;
- implement typed allowlist construction, `CanarySet`, lexical/binary scans,
  and staged/tracked scan with redacted findings;
- add `.private/` ignore rule only after its failing test exists.

**REFACTOR constraints**

- no generic recursive copy/delete sanitizer;
- no leaked value in exceptions or committed findings;
- Phase 1–2 registry behavior unchanged unless `include_phase3=True`.

**Exit evidence:** synthetic `privacy-qa.json` fixture passes; a mutation corpus
shows every forbidden class fails. No private file is opened in this phase.

**Checkpoint commit:** `feat: add Phase 3 privacy contracts and fail-closed boundary`.

### Phase 2 — Data-minimized private profiler: 12 RED cases

**RED first**

- missing alias, unreadable/zero-byte/not-PPTX/invalid-ZIP/macro package;
- required-part and CRC failures;
- ignored-store guard runs before file open;
- profile persists no full text/notes/URL/media bytes;
- one-way canary generation and local cleanup;
- structural/theme/geometry extraction from redistributable synthetic PPTX.

Representative test:

```python
def test_profiler_does_not_persist_slide_text(synthetic_private_pptx, safe_store):
    result = profile_private_exemplar(
        fixture_record("template_primary_1", synthetic_private_pptx), safe_store
    )
    persisted = safe_store.read_summary(result.run_id, result.alias)
    assert "synthetic private canary sentence" not in json.dumps(persisted)
    assert persisted["content_presence"]["text_shape_count"] > 0
```

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/unit/test_phase3_profiler.py
```

**GREEN minimum**

- validate package and hash before measurement;
- inspect text/notes/URLs only ephemerally to create salted one-way n-gram
  canaries; persist counts/presence flags, not values;
- persist normalized geometry/style, raw private part hashes, and local render
  references only in the ignored store;
- render private reference slides directly to the ignored store without
  extracting media;
- remove ephemeral extraction directories in `finally` blocks; retain raw
  summaries/renders only for the current reviewed run.

**REFACTOR constraints:** no text dump, media extraction, notes dump, or anydoc
Markdown retention; no private path in returned committable objects.

**Exit evidence:** local-only ingestion record for all aliases and synthetic
profiler tests. No sanitized profile is committed yet.

**Checkpoint commit:** `feat: add data-minimized private exemplar profiler`.

### Phase 3 — Sanitized profiles and resolvers: 14 RED cases

**RED first**

- separate shell/body schema conformance;
- Exemplar 2 provenance rejected from every shell token family;
- Exemplar 1/3 conflict records retain winner, loser, rule, classification;
- canvas/safe-bound/title hard conflicts fail;
- soft authority rules select content/cover/footer token owners;
- no three-deck averaging;
- body descriptor grouping retains preferred/range/outliers;
- missing body evidence yields `insufficient_evidence`.

Representative contamination test:

```python
@pytest.mark.parametrize("family", SHELL_TOKEN_FAMILIES)
def test_layout_exemplar_2_cannot_supply_shell_tokens(family):
    p1, p3 = synthetic_shell_profiles()
    body = synthetic_body_profile(shell_injection={family: {"value": 0.4}})
    resolved = resolve_professor_profiles(p1, body, p3)
    assert all(
        source["alias"] != "private://layout_exemplar_2"
        for source in resolved["formal_shell_rules"][family]["source_evidence"]
    )
```

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/unit/test_phase3_resolvers.py
```

**GREEN minimum:** build sanitized shell/body objects only from explicit
selectors; implement token-family authority, conflict records, hard-conflict
classification, body range selection, and V3 grammar.

**REFACTOR constraints:** source authority is table-driven and exhaustive;
adding a shell family without an authority rule fails tests.

**Exit evidence:** sanitized manifest, two shell profiles, one body profile,
resolved professor-template profile, visual grammar, resolver/conflict QA.

**Checkpoint commit:** `feat: resolve asymmetric professor exemplar grammar`.

### Phase 4 — A01–A18, Fishbone, and template reconstruction: 24 RED cases

**RED first**

- 18 parameterized archetype semantic-contract hash preservation cases;
- insufficient-evidence blocking and used-archetype failure;
- Fishbone stable positions/history/state meanings;
- fresh package manifest coverage;
- private-part hash non-reuse, orphan/external relation, metadata audit;
- second-backend/import dependency scan.

Representative archetype test:

```python
@pytest.mark.parametrize("archetype_id", [f"A{i:02d}" for i in range(1, 19)])
def test_calibration_preserves_semantic_contract(archetype_id, phase2_registry):
    calibrated = calibrate_archetype(
        phase2_registry[archetype_id], evidence_for(archetype_id), grammar_v3()
    )
    assert calibrated["semantic_contract_sha256"] == semantic_contract_hash(
        phase2_registry[archetype_id]
    )
```

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/unit/test_phase3_calibration.py packages/thesis-deck-system/tests/unit/test_phase3_reconstruction.py
```

**GREEN minimum**

- calibrate mutable tokens and persist immutable semantic-contract hashes;
- style Fishbone without mutating graph data;
- add `PythonPptxAssembler.reconstruct_sanitized_template(profile, manifest,
  output_path)`;
- build every package part afresh inside the adapter boundary;
- audit canonical part hashes against local private part hashes and commit only
  aggregate counts/status.

**REFACTOR constraints:** no import/copy of private PPTX; no public constructor
in `pptx_reconstruction.py`; canonical package digest ignores ZIP timestamps but
not part bytes or relationship graphs.

**Exit evidence:** calibrated registry, calibration coverage QA, Fishbone style
profile/QA, reconstructed template, reconstruction manifest, package privacy QA.

**Checkpoint commit:** `feat: calibrate archetypes and reconstruct sanitized template`.

### Phase 5 — Reconstruction benchmarks: 18 RED cases

**RED first**

- exact formula fixtures for bbox edges, IoU, ratios, gutter, symmetry,
  caption/callout, whitespace, line/font, CIEDE2000, Fishbone position/focus;
- difficult-family selector coverage and no easy-only set;
- unsupported family produces `insufficient_evidence`;
- committed record cannot contain private render path/hash;
- threshold failure blocks benchmark status.

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/unit/test_phase3_metrics.py packages/thesis-deck-system/tests/unit/test_phase3_benchmarks.py
```

**GREEN minimum:** implement formulas in section 13, local comparator, required
family selector, sanitized benchmark records, and committed reconstruction
renders only.

**REFACTOR constraints:** no global pixel-similarity shortcut; every required
metric has independent evidence and threshold.

**Exit evidence:** benchmark selection QA, per-family benchmark JSON, sanitized
reconstruction renders, benchmark summary.

**Checkpoint commit:** `feat: add professor reconstruction benchmarks`.

### Phase 6 — Ledger-derived acceptance deck: 12 RED cases

**RED first**

- build reads scientific/story content only from `Ledger.load()` materialized
  state after persistence;
- fixture mutation after persistence leaves Slide Specs/Layout Plans/Manifest
  scientific bindings unchanged;
- H001→transition→H002→transition→H003 history retained;
- Hypothesis/Problem and historical Fishbone retained per layer;
- every used archetype calibrated;
- real slide→layout→master and SVG ownership relationships;
- Traditional Chinese wrap/overflow;
- speaker notes provenance;
- second-backend scan and private-source non-use.

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/integration/test_phase3_acceptance_build.py packages/thesis-deck-system/tests/integration/test_phase3_regressions.py
```

**GREEN minimum:** orchestrate existing Phase 2 ledger/projections through the
calibrated Layout Director and reconstructed template, then assemble solely via
`PythonPptxAssembler`.

**REFACTOR constraints:** no Phase 3 scientific fixture dictionaries after
Ledger reload; no dropped middle layer or future cursor binding.

**Exit evidence:** Phase 3 ledger copy/hash proof, materialized snapshots,
Slide Specs, Layout Plans, Deck Manifest, acceptance PPTX, structural audit.

**Checkpoint commit:** `feat: build ledger-derived Phase 3 acceptance deck`.

### Phase 7 — Complete QA, review, report, and delivery: 14 RED cases

**RED first**

- each owning QA gate rejects missing/stale evidence;
- visual review rejects missing render, hash mismatch, non-image method,
  boilerplate findings, and absent private-reference review;
- `blocked_visual_review` propagation;
- Professor QA rejects missing presentation-semantic/calibration evidence;
- report-facts stale count/hash/status rejection;
- native Stage 8 blocked behavior and production false;
- repository privacy scan and remote artifact consistency.

Run RED:

```text
python -m pytest -q packages/thesis-deck-system/tests/unit/test_phase3_visual_review.py packages/thesis-deck-system/tests/unit/test_phase3_qa.py packages/thesis-deck-system/tests/integration/test_phase3_private_pipeline.py
```

**GREEN minimum:** run/persist every owning QA check, render every slide,
perform hash-bound image review, write report facts and implementation report,
then run full regression/clean rebuild/remote verification.

**REFACTOR constraints:** no gate may set another gate PASS; report facts are
generated from canonical artifacts, not retyped.

**Exit evidence:** complete Phase 3 QA artifact set and implementation report.

**Checkpoint commit:** `test: complete Phase 3 fidelity acceptance evidence`.

## 5. Contracts and schemas

All schemas use Draft 2020-12, `additionalProperties: false` at every object,
explicit primitive types, bounded arrays/strings, and `FormatChecker` where
applicable.

| Schema | Required nested fields and bounded strings |
| --- | --- |
| sanitized-exemplar-manifest | `manifest_id`, `version`, exactly three `sources[]` with alias enum, status enum, 64-hex SHA, profile-ID pattern, role enum, sanitizer version, QA ref |
| shell-profile | profile/version/alias/SHA; canvas; sanitized masters/layouts; placeholder class enum; normalized bbox; motif enum; typography roles; theme roles; recurrence; measurement provenance IDs |
| body-composition-profile | descriptor ID, alias/SHA, source ordinal integer, composition-class enum, controlled shape-role bboxes, area/gap/symmetry/density metrics, rule-ID enums, evidence status |
| professor-visual-grammar-v3 | separate `formal_shell_rules` and `body_composition_rules`; token source evidence; conflict records; typography/spacing/highlight/caption/comparison/annotation/matrix/density/Fishbone/do-not-use tokens |
| fishbone-style-profile | numeric spine/branch/label/focus/state tokens; state-role enum; source measurement IDs; no scientific labels |
| archetype-calibration | A01–A18 ID; semantic role; immutable contract SHA; mutable tokens; descriptor refs; minimum evidence; native layout role; status enum; rationale rule IDs |
| reconstruction-benchmark | benchmark/family/descriptor IDs; reconstruction slide/render SHA; metrics[] with name enum, target/actual/delta/tolerance/formula-version/status; private evidence availability enum |
| reconstruction-manifest | package ID; profile refs; `parts[]` with normalized package path pattern, origin enum, content type, expected rel owners; forbidden families; canonical digest |
| image-capable-visual-review | slide ID; repository-relative render path; SHA; dimensions; image-capable reviewer method enum/ID/time; bounded finding objects; status enum |
| phase3-report-facts | alias statuses/hashes/profile IDs; counts; QA IDs/statuses; artifact relative paths/hashes; Stage 8 and production status; no narrative free text |

Allowed free strings are limited to:

- font-family names: 1–96 Unicode characters, control/path/URL characters
  rejected;
- repository-relative paths: anchored schema patterns under approved Phase 3
  directories, with `..`, drive, UNC, and URI schemes forbidden;
- findings/repair advice: generated only from controlled rule-ID message maps,
  maximum 240 characters;
- IDs: explicit regexes and maximum lengths;
- SHA-256: exactly 64 lowercase hex characters.

No schema accepts generic `object`, unconstrained `string`, or raw extension
fields.

## 6. Privacy boundary implementation plan

### 6.1 Data minimization (P3P-1)

`RawProfileSummary` persists only:

- alias, source hash, package-validation status;
- slide/master/layout counts and sanitized in-run identities;
- normalized geometry and numeric style values;
- placeholder/shape-type counts and content-presence booleans;
- per-run salted HMAC-SHA256 canaries for normalized private 5-grams;
- local private-part hashes for package non-reuse comparison;
- local render references and controlled local classifier labels.

It never persists full text, notes, comments, URLs, author values, media names,
media bytes, extracted tables, or OOXML dumps. These values are inspected in
memory only. Notes/URLs/metadata produce presence/count flags and canaries,
then are discarded. Private images remain inside the original PPTX; the
profiler renders complete slides locally without extracting media.

Canary salt is generated per run and stored only in the ignored run directory.
Canaries and private part hashes are deleted after final privacy/package QA or
on explicit cleanup. Private renders may remain only until the reviewer closes
the Phase 3 review; the final local manifest records the cleanup deadline.

### 6.2 Storage guard

Before opening a private alias:

```python
store = PrivateProfileStore(private_root, repo_root)
store.assert_safe_before_open()
```

The guard resolves both paths, requires the private root not to be a tracked
path, verifies `git check-ignore`, forbids committable artifact/profile roots,
creates a run directory with restrictive permissions where supported, and
records only a redacted local diagnostic on failure.

### 6.3 Alias/hash boundary (P3P-2)

Only alias URI, approved source SHA-256, sanitized profile ID, and status cross
the boundary. Repository-wide scans cover tracked files, staged files, PPTX ZIP
members, JSON/YAML/Markdown, speaker notes, renders, and artifact manifests.
The scan uses local forbidden basenames/path fragments/canaries but emits only
rule ID and repository-relative finding path.

### 6.4 Whitelist construction

Each sanitizer has a typed constructor such as:

```python
def sanitize_shell_profile(raw: RawProfileSummary, policy: SanitizerPolicy) -> dict:
    return {
        "schema_version": policy.schema_version,
        "profile_id": policy.profile_id_for(raw.alias, raw.source_sha256),
        "source": policy.allowed_source(raw.alias, raw.source_sha256),
        "canvas": policy.canvas(raw.canvas),
        "masters": [policy.master(item) for item in raw.masters],
        "layouts": [policy.layout(item) for item in raw.layouts],
        "tokens": policy.shell_tokens(raw.measurements),
    }
```

Every selector accepts exact keys/types. Input extras cause complete rejection
before output is written. The output is schema-validated, lexically scanned,
binary-signature scanned, serialized to a temporary ignored staging file,
rescanned, then atomically moved to a committable path.

## 7. Private profiler plan

### 7.1 OOXML structural profiling

- `zipfile` validates signature, CRC, required parts, content types, macros,
  encryption indicators, external relationships, and package topology.
- `lxml` reads presentation size, master/layout/slide relationships,
  placeholders, transforms, theme/style references, docProps presence, and
  notes/comments presence.
- raw relationship targets and docProps values remain ephemeral.

### 7.2 Geometry/style extraction

- coordinates are converted to normalized canvas fractions at read time;
- theme fonts/colors, explicit fill/line/text styles, paragraph spacing,
  bullet indentation, and placeholder classes are reduced to typed numeric or
  controlled-role records;
- raw text is used only to distinguish empty/nonempty and build local canaries;
- shape names and alt text are not persisted.

### 7.3 Rendering and local classification

- LibreOffice/Poppler renders every private source slide into the ignored run
  directory;
- the implementation executor uses `functions.view_image` at original detail
  for local role classification;
- local annotations store only controlled composition classes and anonymized
  shape-role assignments tied to local in-run IDs;
- no private screenshot/contact sheet leaves the ignored directory.

### 7.4 Cleanup

Ephemeral XML/text/media buffers are released after each slide. Failed runs
delete staging directories while retaining only a redacted diagnostic. Final
cleanup deletes canary salts, local canaries, private part hashes, private
renders, and raw summaries after review closure; committed outputs remain
self-contained sanitized records.

## 8. Exemplar authority/resolver plan

### 8.1 Authority table

`SHELL_AUTHORITY` is exhaustive:

- Exemplar 1: canvas, content master topology, content title grid,
  Hypothesis/history motifs;
- Exemplar 3: cover/divider, footer, page number, navigation, formal closure;
- Exemplar 1 then Exemplar 3 fallback: missing token only, never averaging;
- Exemplar 2: no shell families.

`BODY_AUTHORITY` allows only composition, figure/text ratio, comparison,
matrix, annotation, caption, callout, density, and split-signal families from
Exemplar 2.

### 8.2 Shell contamination prevention (P3P-3)

Exemplar 2 cannot influence unauthorized shell token families. Its authority is
limited to the body-composition families enumerated in section 8.1.

Tests parameterize every shell family and inject Exemplar 2 values/provenance.
The resolver must either ignore the injection and retain an authorized shell
source or fail with `unauthorized_shell_source`. A final provenance walk fails
if `private://layout_exemplar_2` occurs under `formal_shell_rules`.

### 8.3 Conflict evidence (P3P-4)

Each competing token emits:

```json
{
  "token_path": "title.content.bbox",
  "selected_value": {},
  "winning_source_role": "template_primary_1",
  "losing_alternative": {"descriptor_id": "SP3-MEAS-...", "value": {}},
  "rule_id": "SHELL-CONTENT-TITLE-P1",
  "classification": "non_blocking",
  "status": "resolved"
}
```

Hard conflicts use `classification: blocking` and `status: unresolved`; they
stop reconstruction. Tests cover aspect-ratio mismatch, empty safe-bound
intersection, recurring-object overlap, missing title zone, and missing
authority rule.

## 9. A01–A18 calibration plan

| ID | Required descriptor class | Mutable families | Immutable contract | Minimum evidence | Fallback |
| --- | --- | --- | --- | --- | --- |
| A01 | hypothesis/history shell | title/assertion/chapter geometry | question+hypothesis+falsifier, Problem separate | 1 shell descriptor | insufficient_evidence |
| A02 | observation/problem | three regions, question emphasis | finding/conflict/question/scope | 1 body + shell | insufficient_evidence |
| A03 | history/Fishbone | figure/focus shell placement | revision/focus bindings | 1 history shell + Fishbone | blocked Fishbone fidelity |
| A04 | observation/photo | figure/text/caption/question | observation/problem/question/evidence | 1 body descriptor | insufficient_evidence |
| A05 | literature/mechanism | columns/caption/density | consensus/disagreement/gap/implication | 1 body descriptor | insufficient_evidence |
| A06 | mechanism/solution | diagram/strategy/arrows | mechanism/provenance/strategy/criterion | 1 body descriptor | insufficient_evidence |
| A07 | photo/schematic | dominant/inset/annotation | asset and text bindings | 1 body descriptor | insufficient_evidence |
| A08 | horizontal comparison | panels/gutter/symmetry | control/proposed distinction | 1 comparison descriptor | insufficient_evidence |
| A09 | experiment/table/schematic | matrix/table/diagram/density | all experiment fields and rule | 1 setup descriptor | insufficient_evidence |
| A10 | result single | hero/annotation/take-home | result/metric/uncertainty/asset | 1 result descriptor | insufficient_evidence |
| A11 | result comparison | panel/gutter/caption | distinct Results and assets | 1 comparison descriptor | insufficient_evidence |
| A12 | image matrix | grid/gaps/main-secondary | matrix identities/annotations | 1 matrix descriptor | insufficient_evidence |
| A13 | result+discussion | hero/interpretation/callout | Result/Discussion/Decision/Next Step | 1 result-discussion | insufficient_evidence |
| A14 | integrated discussion | support/contradiction/uncertainty | all discussion fields/order | 1 discussion descriptor | insufficient_evidence |
| A15 | summary/decision | decision/callout/next-step | answer/status/decision/uncertainty/next | 1 closure/body descriptor | insufficient_evidence |
| A16 | transition/history | nodes/derivation strip | causal predecessor/successor provenance | 1 history descriptor | insufficient_evidence |
| A17 | progress/todo | table/current/parallel | prior commitment/owner/time/status | 1 progress descriptor | insufficient_evidence |
| A18 | schedule/next step | timeline/dependencies | owner/time/dependencies/decision | 1 schedule descriptor | insufficient_evidence |

The Phase 2 semantic contract is canonicalized and SHA-256 hashed before and
after calibration. Eighteen parameterized tests require equality. Calibration
coverage artifact records descriptor count/class, mutable tokens changed,
semantic hash, status, and used-in-acceptance flag. Any used insufficient
archetype blocks fidelity PASS.

## 10. Fishbone calibration plan

Calibrated visual tokens are spine/branch thickness, root/child angle, branch
spacing, label bbox/offset/wrap, node fill/border, CURRENT prominence, and
completed/partial/failed/superseded/future state styles.

Tests clone canonical revisions, apply styles, and assert byte-equivalent
canonical graph JSON before/after. Unchanged branch IDs must remain within
0.020 normalized Euclidean position delta across revisions. CURRENT stroke
ratio and contrast use section 13 formulas, and `functions.view_image` review
owns the 3–5 second focus judgment.

Evidence:

- `profiles/fishbone-style-profile.json`
- `artifacts/phase3/fishbone-style-qa.json`
- sanitized revision SVGs and comparison montage;
- canonical graph/history hash parity.

## 11. Sanitized native-template reconstruction plan

### 11.1 One-backend entrypoint

```python
PythonPptxAssembler().reconstruct_sanitized_template(
    resolved_profile=profile,
    reconstruction_manifest=manifest,
    output_path=output_path,
)
```

Only this method may invoke `pptx_reconstruction.py`. Assembly of acceptance
slides continues through `PythonPptxAssembler.assemble(...)`.

### 11.2 Fresh-package sequence

1. validate resolved shell and manifest schemas;
2. create a new empty presentation/package;
3. generate generic core/app properties;
4. generate theme from sanitized semantic color/font tokens;
5. construct fresh masters and layouts from sanitized geometry;
6. construct internal relationships from manifest identities;
7. save through the adapter;
8. normalize ZIP entry order/timestamps inside the same adapter-owned save
   operation for deterministic canonical package digest;
9. reopen and audit every part/relationship.

No private PPTX is an input to this entrypoint.

### 11.3 Package non-reuse proof (P3P-5)

Local QA computes SHA-256 for every private source part and every output part.
Committed evidence contains only source-part count, output-part count,
comparison count, equal-hash count, and status. Equal-hash count must be zero.

The reconstruction manifest must cover 100% of output parts. Allowed families
are content types/root rels, generic docProps, presentation/view/pres/table
styles, generated themes, masters/layouts/slides/notes, internal rels, and
repository-provenanced synthetic media. Forbidden families include macros,
custom XML, comments/people, external links, embeddings/OLE, private charts or
cached workbooks, thumbnails, unmanifested media, and orphan parts.

Audit fails on external relationships, unresolved targets, orphan parts,
private canaries/basenames/metadata, forbidden content types, non-generic
docProps, unmanifested parts, or any private-part hash reuse.

## 12. Reconstruction benchmark plan

### 12.1 Required difficult families (P3P-6)

Selector must attempt:

1. formal shell/content page;
2. Hypothesis/Problem shell;
3. photo+schematic or equivalent figure-first layout;
4. Control vs Proposed/comparison;
5. Result+Discussion;
6. image matrix when direct evidence exists;
7. Fishbone/research-history when direct evidence exists.

For each family, choose the descriptor with the greatest required-slot count,
then highest annotation density, then lowest sanitized source ordinal for
determinism. This prevents selecting only sparse/easy slides. Missing direct
evidence emits `insufficient_evidence`, never a fabricated target.

### 12.2 Evidence separation

Private render paths, hashes, and side-by-side images remain local. Committed
records contain descriptor ID, family, sanitized reconstruction render path and
hash, numeric metric records, and status. The sanitizer rejects any private
render path/hash field.

### 12.3 Benchmark exit

Every supported required family must pass all required metrics and image review.
An unsupported family is visible as `insufficient_evidence`; if used by the
acceptance deck it blocks professor fidelity.

## 13. Quantitative fidelity metric definitions

### 13.1 Coordinate domain

For canvas width `W`, height `H`, convert EMU/pixels to:

```text
x_n=x/W, y_n=y/H, w_n=w/W, h_n=h/H
left=x_n, top=y_n, right=x_n+w_n, bottom=y_n+h_n
```

All bboxes are clipped to `[0,1]²`. Invalid negative sizes fail measurement.

### 13.2 Geometry metrics (P3P-7)

- **per-edge error:** absolute difference of reference and candidate left,
  top, right, bottom; bbox edge error is their maximum.
- **x/y/w/h error:** componentwise absolute differences in normalized values.
- **IoU:** intersection area divided by union area; zero when union is zero.
- **dominant-figure area ratio:** union area of shapes classified
  `primary_figure` divided by safe-content area; delta is absolute reference
  minus candidate ratio.
- **text/figure ratio:** union area of visible governed text regions divided by
  union area of governed figure regions, both clipped to safe bounds. Zero
  figure area is invalid for figure-required roles.
- **gutter:** for x-ordered nonoverlapping panels, `(next.left-current.right)`;
  compare each normalized gap and the median.
- **comparison symmetry:** first re-normalize panel edges to the safe-content
  bbox so its left/top is `(0,0)` and right/bottom is `(1,1)`, then take the maximum of
  `abs(A_left-A_right)/(A_left+A_right)` and mirrored-edge error
  `max(abs(left.left-(1-right.right)), abs(left.right-(1-right.left)))`.
- **caption/callout error:** maximum bbox edge error plus absolute height delta;
  both component findings persist.
- **image-matrix gap:** maximum row/column normalized gap delta after stable
  row/column ordering.
- **table/diagram proportion:** `A_table/(A_table+A_diagram)` absolute delta.
- **footer/navigation alignment:** maximum baseline and bbox edge error.
- **whitespace fraction:** in rendered safe-area pixels, estimate background as
  the median sRGB of four 5% corner patches; convert to Lab as below; normalize
  grayscale Sobel magnitude to `[0,1]`; a pixel is whitespace when ΔE00≤3 and
  Sobel magnitude≤0.02. Fraction is whitespace pixels divided by safe-area
  pixels.
- **line-width delta:** absolute point-width difference; missing required line
  is failure, not width zero.
- **font delta:** record absolute point delta and
  `abs(candidate-reference)/reference`; both must pass (`≤2 pt` and `≤8%`).

### 13.3 CIEDE2000 assumptions

Inputs are 8-bit sRGB after alpha compositing over the measured slide
background. Convert sRGB to linear RGB with IEC 61966-2-1 transfer function,
then to XYZ using the standard sRGB D65 matrix. Convert XYZ to CIELAB using D65
2° reference white `(Xn,Yn,Zn)=(95.047,100.000,108.883)`. Compute CIEDE2000
with `kL=kC=kH=1` using the Sharma/Wu/Dalal equations. Persist reference RGB,
candidate RGB, Lab values rounded to 6 decimals, ΔE00, formula version
`cie2000-srgb-d65-2deg-v1`, and threshold 6. Alpha/transparency or theme colors
are resolved to rendered sRGB before comparison.

### 13.4 Fishbone metrics

- **branch-position delta:** Euclidean distance
  `sqrt((x2_n-x1_n)^2+(y2_n-y1_n)^2)` for the center of the same stable branch
  ID across revisions; required maximum ≤0.020.
- **focus stroke ratio:** current-branch stroke width divided by median
  noncurrent branch stroke width; required ≥1.5.
- **focus contrast:** WCAG relative-luminance contrast ratio between CURRENT
  stroke/fill emphasis and its adjacent background; required ≥3:1.
- **focus qualitative status:** image-capable reviewer judgment; pixel metrics
  cannot replace it.

Unit tests use hand-calculated fixtures, identity cases, threshold boundaries,
and known published CIEDE2000 sample pairs.

## 14. Image-capable review execution plan

### 14.1 Actual mechanism (P3P-8)

The implementation environment exposes Codex `functions.view_image`. The
executor will open every local image with `detail="original"`:

- private reference render from ignored storage;
- corresponding sanitized reconstruction render;
- every final acceptance slide render;
- full and family-specific montages for flow only.

Controlled reviewer ID is `codex-view-image-original-v1`; review method records
`kind=image_capable`, tool ID, detail level, timestamp, render dimensions, and
SHA-256. Slide-level review remains authoritative; montage review cannot replace
it.

### 14.2 Private comparison handling

Private and sanitized images are opened locally in separate tool calls. No
side-by-side private montage is committed. Findings reference sanitized
descriptor/family IDs only and contain no private text. Local review record may
bind the private render hash; the committed record stores only
`private_reference_reviewed: true` and local evidence status.

### 14.3 Blocking behavior

If `functions.view_image` is unavailable, cannot open a render, or the executor
cannot inspect every required image, records use `status=blocked_visual_review`.
Professor visual review and professor visual fidelity become blocked; render
pixel QA may still report its independent status. Metadata, Layout Plans, or
pixel heuristics cannot create qualitative PASS.

## 15. Acceptance deck plan

The accepted Phase 2 path remains:

```text
persisted ledger-events.json
→ Ledger.load() + hash/replay verification
→ cursor materialization
→ compile_master_story_from_ledger()
→ stage-aware Slide Specs and field bindings
→ calibrated LayoutDirector
→ calibrated Layout Plans
→ reconstructed sanitized native template
→ PythonPptxAssembler.assemble()
→ structural/render/semantic/Professor QA
```

After `Ledger.load()`, no scientific/story source may read private exemplars or
seed fixture dictionaries. Private-derived sanitized profiles influence only
visual tokens/layout geometry.

The acceptance deck includes Progress/commitments; H001 Hypothesis, Problem,
Fishbone, scientific stages, experiments, distinct Results, Discussion,
Summary/Decision; H001→H002 transition; complete H002 layer; H002→H003
transition; sufficient H003 layer; and dedicated examples of photo+schematic,
Control vs Proposed, image matrix, Result+Discussion, and Next Step/Schedule.
Traditional Chinese is primary with English technical terms where appropriate.

Required mutations prove seed/private profile scientific changes after ledger
persistence do not alter scientific bindings, cursors, story order, or notes.

## 16. Phase 3 QA pipeline

| Owning gate | Executed checks | Evidence artifact |
| --- | --- | --- |
| ingestion QA | alias resolution, SHA, type, ZIP/CRC/required parts, atomic three-alias status | `artifacts/phase3/exemplar-ingestion-qa.json` |
| sanitizer/privacy QA | allowlist/schema/lexical/binary/tracked/staged/PPTX package scans | `artifacts/phase3/sanitizer-privacy-qa.json` |
| profile QA | separate profile schemas, metric completeness, no raw content | `artifacts/phase3/template-profile-qa.json`, `body-profile-qa.json` |
| resolver/conflict QA | authority, contamination, conflicts, hard blockers | `artifacts/phase3/resolver-conflict-qa.json` |
| archetype QA | A01–A18 evidence, token changes, semantic hashes | `artifacts/phase3/archetype-calibration-qa.json` |
| Fishbone QA | style tokens, stable graph/history/positions, focus metrics | `artifacts/phase3/fishbone-style-qa.json` |
| package QA | manifest coverage, part families, rels, metadata, hash non-reuse | `artifacts/phase3/reconstruction-package-qa.json` |
| benchmark QA | required families, formulas, thresholds, insufficient evidence | `artifacts/phase3/reconstruction-benchmark-qa.json` |
| structural PPTX QA | slide→layout→master, governed shapes, geometry, notes, SVG relationships | `artifacts/phase3/structural-audit.json` |
| scientific/presentation QA | Phase 2 temporal, field, role, distinction, history invariants | `artifacts/phase3/presentation-semantic-fidelity-qa.json` |
| render-pixel QA | nonblank, clipping, bounds, ratios, symmetry, whitespace, density | `artifacts/phase3/render-pixel-qa.json` |
| image-capable review | hash-bound slide-specific reference/reconstruction/final review | `artifacts/phase3/professor-visual-review.json` |
| Professor QA | calibrated profile plus ledger/presentation evidence | `artifacts/phase3/professor-qa.json` |
| report consistency QA | canonical counts/hashes/statuses/report footer | `artifacts/phase3/report-evidence-consistency.json` |
| native Stage 8 | real PowerPoint round-trip only | `artifacts/phase3/native-powerpoint-qa.json` or blocked record |

The canonical release order remains schema/ledger → scientific reasoning →
citation/provenance → Professor logic → PPTX assembly → structural QA →
render/montage QA → native PowerPoint → final audit → release. Phase 3 sub-gates
feed their owning canonical stages; they do not reorder or self-certify them.

## 17. Acceptance thresholds and stop/go gates

| Phase entry/exit | GO evidence | STOP behavior |
| --- | --- | --- |
| open private alias | private root ignored, untracked, outside committed roots | fail before opening file |
| finish ingestion | all three valid aliases/hashes/packages | `blocked_fixture`/`fail`; no profile claim |
| write sanitized profile | allowlist, schema, lexical, binary scans pass | discard staging output; local redacted diagnostic |
| resolve shell | complete authority and no hard conflicts | no template reconstruction |
| resolve body | required descriptors classified or explicit insufficiency | affected archetype insufficient |
| calibrate archetype | minimum evidence and unchanged semantic hash | fallback Phase 2 geometry, block fidelity if used |
| reconstruct template | resolved shell and manifest pass | no PPTX output accepted |
| accept package | 100% manifest coverage, zero forbidden/orphan/external/reused parts | package QA fail |
| accept benchmark | every supported required metric within section 13/design thresholds | benchmark fail; no fidelity PASS |
| assemble deck | all used archetypes calibrated and Ledger replay valid | build blocked/fail |
| visual review | every required actual render inspected and hash-bound | `blocked_visual_review` or fail |
| Professor fidelity | every requirement in design section 17 passes | fail/blocked, never partial PASS |
| native Stage 8 | actual Microsoft PowerPoint round-trip evidence | `blocked_environment` |
| production readiness | professor fidelity + native + permitted real scientific fixture | always false until all exist |

## 18. Negative-test inventory

The 116 planned cases include these explicit negative boundaries:

### Privacy and ingestion

- drive, UNC, POSIX-home, traversal, and URI path leakage;
- private basename, slide text/canary, notes, comments, citation/title, URL,
  DOI, e-mail, author/company/editor, media name/alt text, raw XML, base64,
  ZIP/image/PPTX signature leakage;
- private PPTX, screenshot, media, side-by-side render, or matching private hash
  staged/tracked;
- unknown nested sanitizer field and unconstrained string;
- raw root not ignored, inside artifact root, or tracked;
- missing/unreadable/empty/wrong-extension/invalid-ZIP/CRC/required-part/macro
  source;
- diagnostics echoing the rejected private value;
- full private text/notes/media persisted by profiler.

### Authority and conflict

- Exemplar 2 supplies canvas, title, master, footer, page number, navigation,
  chapter marker, or shell typography;
- all-three-deck average token;
- conflict missing winner, loser, rule ID, or classification;
- canvas ratio, safe-bound, shell-overlap, missing-title hard conflict ignored;
- body descriptor outlier silently discarded;
- missing evidence reported as calibrated.

### Calibration, Fishbone, and reconstruction

- each A01–A18 semantic hash changes;
- used insufficient archetype allowed to pass;
- Hypothesis/Problem merged or field contract weakened;
- Fishbone branch ID/parent/status/revision/layer binding changes;
- unstable unchanged Fishbone branch or weak CURRENT focus;
- private package copied/cleaned, output part hash reused, manifest incomplete,
  forbidden/orphan/external part, non-generic metadata, unresolved relation;
- another module imports reconstruction helper or introduces an assembler.

### Benchmark and visual review

- easy-only benchmark selection;
- missing formal, Hypothesis/Problem, figure-first, comparison, or
  Result+Discussion family;
- unsupported matrix/Fishbone fabricated instead of insufficient evidence;
- bad bbox/IoU/ratio/gutter/symmetry/caption/callout/whitespace/font/line/color
  metric accepted;
- global pixel similarity overrides a failed required metric;
- private render path/hash in committed benchmark;
- blank/cropped/misaligned render does not change pixel QA;
- qualitative PASS from metadata, missing render, hash mismatch, non-image
  method, montage-only review, boilerplate findings, or missing local reference
  inspection.

### Phase 1–2 regressions and release honesty

- fixture/private scientific mutation changes ledger-derived story;
- future evidence appears on opening slides;
- middle Hypothesis Layer or historical Fishbone disappears;
- result distinction or SVG relationship is lost;
- prior commitment, owner, timing, dependency, or decision binding disappears;
- Professor QA passes without presentation/calibration evidence;
- native blocked environment reported as pass;
- production readiness true without native and real scientific fixture gates;
- stale report facts or missing artifact hashes accepted.

## 19. Generated artifact plan

### 19.1 Committed sanitized artifacts

| Artifact | Producer | Consumer | Schema/classification | Acceptance role |
| --- | --- | --- | --- | --- |
| `profiles/sanitized-exemplar-manifest.json` | sanitizer | all | sanitized manifest | alias/hash/profile proof |
| `profiles/template-primary-1.sanitized.json` | sanitizer | shell resolver | shell profile | Exemplar 1 evidence |
| `profiles/template-primary-3.sanitized.json` | sanitizer | shell resolver | shell profile | Exemplar 3 evidence |
| `profiles/layout-exemplar-2.sanitized.json` | sanitizer | body resolver | body profile | Exemplar 2 evidence |
| `profiles/professor-template-resolved.json` | shell resolver | reconstruction/Layout Director | resolved shell | shell authority/conflicts |
| `profiles/professor-visual-grammar-v3.json` | resolvers | calibration/QA | V3 grammar | source-role grammar |
| `profiles/fishbone-style-profile.json` | calibrator | renderer/QA | Fishbone style | appearance calibration |
| `profiles/archetype-calibrations.json` | calibrator | Layout Director | calibration array | A01–A18 coverage |
| `artifacts/phase3/reconstruction-manifest.json` | adapter | package QA | reconstruction manifest | fresh-package proof |
| `artifacts/phase3/reconstructed-template.pptx` | adapter | acceptance build | sanitized PPTX | native shell |
| `artifacts/phase3/reconstruction-benchmarks/*.json` | benchmark | QA/report | sanitized metrics | family fidelity |
| `artifacts/phase3/reconstruction-renders/*.png` | benchmark | image review | sanitized render | review evidence |
| `artifacts/phase3/slide-specs.json` | build | Layout/QA | existing schema | scientific presentation |
| `artifacts/phase3/layout-plans.json` | Layout Director | assembler/QA | existing schema | calibrated geometry |
| `artifacts/phase3/MASTER-PHASE3.manifest.json` | build | audit/report | deck manifest | binding/provenance |
| `artifacts/phase3/acceptance-deck.pptx` | assembler | render/review | sanitized PPTX | acceptance output |
| `artifacts/phase3/render/*.png` and montages | renderer | pixel/image QA | sanitized render | visual evidence |
| `artifacts/phase3/*-qa.json` | owning gates | report | QA schemas | inspectable PASS/fail |
| `artifacts/phase3/report-facts.json` | QA3 | report consistency | report facts | delivery truth |
| `reports/PHASE_3_IMPLEMENTATION_REPORT.md` | report step | reviewer | protocol report | final traceability |

### 19.2 Local-only artifacts

Under `.private/thesis-deck-system/phase3/<run-id>/`:

- alias-to-path map and exact diagnostics;
- data-minimized raw profile summaries;
- per-run canary salt/HMAC set;
- private source package-part hashes;
- private source slide renders/contact sheets;
- local classifier annotations;
- local private-vs-sanitized comparison records;
- any temporary Office conversion output;
- cleanup manifest.

No committed artifact refers to a local-only path or private render hash.

## 20. Implementation commits/checkpoints

1. `feat: add Phase 3 privacy contracts and fail-closed boundary`
2. `feat: add data-minimized private exemplar profiler`
3. `feat: resolve asymmetric professor exemplar grammar`
4. `feat: calibrate archetypes and reconstruct sanitized template`
5. `feat: add professor reconstruction benchmarks`
6. `feat: build ledger-derived Phase 3 acceptance deck`
7. `test: complete Phase 3 fidelity acceptance evidence`
8. `docs: report Phase 3 professor visual fidelity implementation`

At every checkpoint:

- run the new focused test module RED, implement GREEN, rerun focused and full
  prior suites, then refactor while green;
- inspect staged paths and privacy scan before commit;
- commit no local/private artifacts;
- record generated evidence needed by the next checkpoint;
- stop at any hard gate rather than committing a claimed PASS.

## 21. Final Phase 3 implementation delivery contract

The final implementation response/report must provide:

- repository, branch, commit SHA, pushed status, remote head/artifact proof;
- files added/modified/deleted;
- exact test/QA commands and pass/fail counts;
- P3-R1–P3-R12 traceability;
- three private aliases with resolved status, approved SHA-256, and sanitized
  profile ID only;
- raw local storage and cleanup status;
- sanitizer/privacy scan status and forbidden finding count;
- Exemplar 1/3 shell token/conflict evidence;
- Exemplar 2 body-composition evidence and shell-contamination result;
- A01–A18 evidence/calibration/semantic-hash coverage;
- Fishbone style, stable-history, and focus evidence;
- reconstructed-template path/hash, manifest coverage, forbidden/orphan/
  external counts, private-part equality count;
- benchmark families, metric pass/fail/insufficient counts, deviations;
- acceptance PPTX, Slide Specs, Layout Plans, Manifest, render and montage paths;
- render-pixel and hash-bound image-capable review results;
- Professor QA and presentation-semantic results;
- Traditional Chinese QA;
- native PowerPoint Stage 8 status;
- production Group Meeting readiness, which remains false unless every
  independent gate passes;
- known failures, technical debt, deviations, and unresolved questions;
- protocol `codex_report` footer with `status: awaiting_review`.

## 22. Design-section and reviewer-condition coverage

| Design section | Implementation phase | Tests | Evidence |
| --- | --- | --- | --- |
| 1 scope/invariants | all | Phase 1–2 regression module | semantic/provenance QA |
| 2 two-domain architecture | P1–P3 | privacy boundary/integration | sanitizer/privacy QA |
| 3 ingestion | P2 | package/alias negatives | ingestion QA |
| 4 raw model | P1–P2 | minimization/cleanup | local raw manifest |
| 5 sanitizer | P1 | allowlist/leakage negatives | sanitizer QA |
| 6 contracts | P1/P3/P5/P7 | schema tests | committed profiles/metrics/facts |
| 7 role separation | P3 | authority/averaging tests | resolver QA |
| 8 shell resolver | P3 | conflict/hard-stop tests | resolved shell/conflicts |
| 9 body resolver | P3 | grouping/outlier tests | body grammar |
| 10 A01–A18 | P4 | 18 semantic-hash cases | coverage matrix |
| 11 template reconstruction | P4 | package/non-reuse tests | manifest/package QA |
| 12 benchmark | P5 | formulas/families | benchmark QA |
| 13 Fishbone | P4 | graph/history/focus tests | Fishbone QA |
| 14 backend | P4/P6 | dependency scan | backend audit |
| 15 image review | P7 | hash/method/block tests | visual review JSON |
| 16 privacy negatives | P1–P7 | inventory section 18 | privacy QA |
| 17 acceptance gates | P7 | missing/stale evidence tests | QA report |
| 18 native/readiness | P7 | blocked/native tests | Stage 8 record |
| 19 QA ownership | P7 | cross-gate PASS rejection | owning QA artifacts |
| 20 D3 traceability | all | coverage self-check | implementation report |
| 21 TDD phases | all | 116 cases | checkpoint artifacts |
| 22 risks/questions | relevant phase | insufficiency/block tests | known-failure report |

| Condition | Explicit coverage |
| --- | --- |
| P3P-1 | Sections 6–7: ephemeral inspection, HMAC canaries, no persisted full content, retention/cleanup |
| P3P-2 | Section 6.3 and repository-wide privacy scan; alias/SHA/profile only |
| P3P-3 | Section 8.2 parameterized shell-family contamination tests |
| P3P-4 | Section 8.3 complete conflict record plus hard-conflict tests |
| P3P-5 | Section 11 fresh package, manifest, relationships, metadata, local hash non-reuse |
| P3P-6 | Section 12 difficult benchmark families and insufficiency behavior |
| P3P-7 | Section 13 exact formulas and CIEDE2000 assumptions |
| P3P-8 | Section 14 `functions.view_image(detail=original)` and blocked behavior |

## 23. Planning self-check and execution stop

Before plan delivery, verify:

- every approved design section appears in section 22;
- P3P-1–P3P-8 appear in section 22 and their owning sections;
- planned test counts sum to 116 (`22+12+14+24+18+12+14`);
- all source/schema/test/artifact paths are repository-relative;
- the plan contains no private path, private basename, private content, or raw
  diagnostic;
- no Phase 3 implementation file was created or modified;
- only this plan is staged;
- `git diff --check` passes;
- remote plan blob matches the pushed commit.

STOP after pushing this plan. Wait for reviewer approval before creating tests,
schemas, production modules, profiles, templates, benchmarks, decks, renders,
QA artifacts, or the Phase 3 implementation report.

## 24. Task-by-task execution checklist after approval

### Task 1: Contracts and privacy boundary

- [ ] Add the 22 Phase 1 RED cases named in section 4 to
  `test_phase3_contracts.py` and `test_phase3_privacy.py`; run the exact focused
  command from section 4 and confirm failures are missing schemas/APIs.
- [ ] Create the ten Draft 2020-12 schemas and the `phase3_privacy.py` APIs
  specified in sections 3, 5, and 6; add the `.private/` ignore rule only after
  its guard test fails.
- [ ] Rerun the focused tests and require 22/22 GREEN, then run the existing
  complete test suite and require no Phase 1–2 regression.
- [ ] Generate only the synthetic privacy mutation evidence, run the repository
  privacy scan and `git diff --check`, inspect staged paths, and create
  checkpoint commit 1.

### Task 2: Data-minimized private profiler

- [ ] Add the 12 profiler RED cases from section 4 with redistributable synthetic
  OOXML fixtures and verify the focused command fails because profiler behavior
  is absent.
- [ ] Implement package validation, ephemeral content inspection, HMAC canaries,
  normalized geometry/style summaries, local rendering, and cleanup exactly as
  sections 6–7 define.
- [ ] Rerun profiler tests to 12/12 GREEN, then rerun Task 1 and the complete
  Phase 1–2 suite.
- [ ] Execute a local-only three-alias ingestion dry run only when implementation
  authorization permits private reads; verify no tracked file changes, then
  create checkpoint commit 2 containing code/tests only.

### Task 3: Sanitized profiles and asymmetric resolvers

- [ ] Add the 14 resolver RED cases, including the parameterized unauthorized
  Exemplar-2 shell-family injection and incomplete conflict-record mutations.
- [ ] Implement typed profile constructors, authority tables, conflict records,
  hard-stop rules, body descriptor grouping, and grammar V3.
- [ ] Require 14/14 focused GREEN plus all previous suites, then run schema and
  repository privacy scans against generated sanitized candidates.
- [ ] Persist only allowlisted sanitized profiles/resolver evidence and create
  checkpoint commit 3.

### Task 4: A01–A18, Fishbone, and fresh template reconstruction

- [ ] Add the 24 RED cases, including 18 semantic-contract hashes, Fishbone
  immutability, package non-reuse, and single-backend dependency scans.
- [ ] Implement calibrated token records, Fishbone style application, and
  `PythonPptxAssembler.reconstruct_sanitized_template()` with its private helper.
- [ ] Require 24/24 focused GREEN, full Phase 1–3 regression GREEN, zero private
  part-hash equality, complete reconstruction manifest coverage, and clean
  relationship audit.
- [ ] Inspect the reconstructed package and sanitized artifact diff, run privacy
  scan/`git diff --check`, and create checkpoint commit 4.

### Task 5: Difficult-family reconstruction benchmarks

- [ ] Add the 18 metric/family RED cases, including published CIEDE2000 pairs,
  threshold boundaries, difficult-family selection, and insufficiency behavior.
- [ ] Implement section 13 formulas and section 12 selection/comparison logic;
  keep private renders and hashes local.
- [ ] Require 18/18 focused GREEN, all prior suites GREEN, and each supported
  required family within its independent thresholds.
- [ ] Inspect every sanitized reconstruction render through the mechanism in
  section 14, persist sanitized findings/metrics only, and create checkpoint
  commit 5.

### Task 6: Ledger-derived acceptance deck

- [ ] Add the 12 acceptance RED cases for persisted-ledger reproducibility,
  N-layer history, semantic roles, calibrated archetypes, native relationships,
  Traditional Chinese, notes, and single-backend use.
- [ ] Implement `phase3_build.py` orchestration without reading seed/private
  scientific facts after `Ledger.load()`.
- [ ] Require 12/12 focused GREEN and the complete suite GREEN; clean-build the
  acceptance artifact directory and replay/materialize from zero.
- [ ] Run structural audit and privacy scan on PPTX/notes/media, then create
  checkpoint commit 6.

### Task 7: Complete owning QA, image review, and report

- [ ] Add the 14 QA RED cases for missing/stale evidence, image-review blocking,
  Professor evidence, report facts, native Stage 8, and remote consistency.
- [ ] Implement `qa3.py`, render/review finalization, report facts, and canonical
  pipeline ownership without synthetic PASS paths.
- [ ] Render every slide, use `functions.view_image(detail=original)` on every
  required private/local comparison and sanitized final render, bind hashes,
  and persist slide-specific findings.
- [ ] Require 14/14 focused GREEN, all 116 new cases GREEN, the complete existing
  suite GREEN, all available QA gates evidenced, and blocked native/production
  status when prerequisites remain unavailable.
- [ ] Write `PHASE_3_IMPLEMENTATION_REPORT.md`, run report consistency, privacy
  scan, absolute-path scan, `git diff --check`, checkpoint commits 7–8, push,
  and verify remote head and artifact blobs.
