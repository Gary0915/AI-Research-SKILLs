# Thesis Deck System — Codex Task Phase 1

## Authorization

Phase 0 architecture was approved by the reviewer in:

`thesis-deck-system/reviews/PHASE_0_FINAL_REVIEW.md`

Phase 1 is authorized. This is a bounded vertical-slice implementation only.

Do **not** silently advance to Phase 2, public skill registration, the full recipe catalog, or production Group Meeting use.

## Required reading before implementation

Read these files completely, in this order:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/TASK_PHASE_0.md`
3. `thesis-deck-system/reviews/PHASE_0_ARCHITECTURE_REVIEW.md`
4. `thesis-deck-system/reviews/PHASE_0_FINAL_REVIEW.md`
5. `thesis-deck-system/reports/PHASE_0_IMPLEMENTATION_REPORT.md`
6. this file

Synchronize the remote branch first and confirm:

- repository: `Gary0915/AI-Research-SKILLs`
- branch: `codex/thesis-deck-system`

## Mission

Implement the smallest end-to-end thesis-deck vertical slice that proves the approved architecture with executable contracts, append-only history, one reproducible scientific plot, two slide recipes, a native-layout synthetic PPTX fixture, a two-slide cumulative Master Deck, a meeting-delta rebuild, and structured QA evidence.

The goal is not a flashy demo. The goal is to prove that the system can preserve scientific reasoning and research history while producing an editable PowerPoint through deterministic, auditable contracts.

## Non-negotiable scientific contract

Each research block must support:

`Observation → Literature → Mechanism → Solution/Strategy → Experiment → Result → Discussion → Next Step`

The Phase 1 B001 fixture must explicitly contain:

- exact research question,
- problem statement,
- formal hypothesis Claim,
- formal mechanism Claim,
- formal prediction Claim,
- falsifying observation,
- discriminating evidence requirement,
- structured Literature synthesis,
- structured Experiment design,
- Result with units/uncertainty,
- Discussion with support/not-support, failed assumptions, missing evidence, limitations, decision,
- canonical Next Step/Action Item with owner and timing.

Do not infer canonical QA fields from Markdown prose.

## Phase 1 implementation scope

### P1.1 — Python package/control plane

Create the approved Python package under:

`packages/thesis-deck-system/`

Use a conventional installable/testable structure, including at least:

- `pyproject.toml`
- `src/thesis_deck_system/`
- `tests/unit/`
- `tests/integration/`
- `tests/fixtures/`
- `tests/golden/` where useful

The package must own:

- JSON Schema validation,
- reference resolution,
- append-only ledger append/replay/materialization,
- projections,
- slide-spec compilation,
- Professor Profile loading,
- QA orchestration,
- backend-neutral `PptxAssembler` interface.

Do not create a second JS/TS orchestration runtime in Phase 1.

### P1.2 — versioned schemas

Implement executable JSON Schemas for at least:

1. `research-block.schema.json`
2. `scientific-stage.schema.json`
3. `claim.schema.json`
4. `evidence-card.schema.json`
5. `asset-manifest.schema.json`
6. `next-step.schema.json`
7. `slide-spec.schema.json`
8. `deck-manifest.schema.json`
9. `qa-report.schema.json`
10. `decision-event.schema.json`
11. `professor-profile.schema.json`
12. `template-profile.schema.json`

Schemas must enforce the approved architecture, not merely accept arbitrary dictionaries.

Critical cross-object rules that JSON Schema alone cannot prove must be implemented in semantic validators and tested.

### P1.3 — append-only ledger

Implement the minimal ledger required to prove cumulative research history:

- stable IDs,
- monotonic cursor,
- append events only,
- event hash/canonical serialization strategy,
- replay/materialize from zero,
- revision increment,
- referential integrity,
- legal `research_status` transitions,
- independent legal `story_visibility` transitions,
- Claim revision/supersession,
- Action Item status/closure,
- decision/event binding.

Manual editing of materialized state must not be treated as authoritative history.

At minimum support events equivalent to:

- block created/revised,
- claim created/revised/superseded,
- stage revised,
- evidence linked,
- research status changed,
- story visibility changed,
- action committed/status changed/closed,
- decision recorded,
- slide spec compiled,
- deck built / QA finding / release state as needed for the slice.

### P1.4 — synthetic scientific project fixture

Create one committed synthetic fixture. It must be obviously synthetic and must not imply actual thesis data.

The fixture must contain B001 with:

- all eight structured Scientific Method stages,
- Claims,
- Evidence Cards,
- one prior commitment,
- one current canonical Next Step,
- one Discussion revision after the initial build,
- one meeting cursor before that revision,
- one `zh-TW` Professor Profile,
- no fabricated literature citation presented as real published evidence.

For literature in the synthetic fixture, use clearly synthetic/local evidence records or public-domain/test metadata whose status is explicitly marked. The architecture test is the objective; do not invent real DOIs/authors.

### P1.5 — quantitative CSV + scientific plot

Create a small synthetic CSV with:

- explicit units,
- condition/position labels,
- replicate identifiers,
- enough data to exercise the Experiment decision rule.

Create a saved Matplotlib script that reads the registered CSV and outputs:

- SVG master,
- PNG preview,
- registered asset manifest,
- data/script/output hashes,
- uncertainty/error-bar policy.

The plot values shown must be programmatically cross-checked against the source data.

Do not use image generation for the plot.

### P1.6 — synthetic native PPTX template fixture + profiler

Create a redistributable synthetic 16:9 PPTX template fixture that contains enough native PowerPoint structure to test:

- at least two native layouts or otherwise meaningful layout distinctions,
- native title/content placeholders where appropriate,
- theme fonts/colors,
- slide size,
- slide numbers/footer behavior if feasible,
- representative existing slide(s).

Implement a profiler that inspects the PPTX/OpenXML package and emits `template-profile.json` containing at least:

- presentation size,
- masters/layouts,
- layout IDs/names,
- placeholder types/indexes/geometry,
- theme fonts/colors,
- relevant relationship IDs,
- semantic layout-role mapping,
- hash/version binding.

Do not flatten the template to screenshots.

Screenshots/renders may be generated only as QA evidence.

### P1.7 — one PPTX backend only

Implement exactly one Phase 1 PPTX worker behind a backend-neutral interface such as:

`PptxAssembler.assemble(template_path, slide_specs, output_path) -> AssemblyResult`

The selected implementation is the Python backend approved in Phase 0.

Do not implement or benchmark PptxGenJS in parallel during Phase 1.

Scientific contracts and Slide Specs must not contain backend-specific Python library types.

If the high-level PPTX library cannot preserve a required native relationship, use the smallest documented OpenXML bridge necessary and test it.

### P1.8 — exactly two slide recipes

Implement exactly these two content recipes for Phase 1:

1. `photo_observation`
2. `hero_plot_discussion`

Do not build the full recipe catalog yet.

Each recipe must define:

- native layout semantic role,
- allowed assets,
- semantic slots,
- text budgets,
- citation/provenance zone,
- speaker-note expectations,
- failure/split behavior.

Text overflow must not be fixed by silently shrinking below the profile threshold.

### P1.9 — first Master Deck build

Build a cumulative synthetic Master Deck containing at minimum two content slides:

- an Observation-oriented slide using `photo_observation`,
- a Result/Discussion slide using `hero_plot_discussion`.

Requirements:

- source template is copied, not edited in place,
- slides bind to stable slide IDs,
- slides bind to block revision, Claims, Evidence, Actions, Professor Profile, Template Profile, and ledger cursor,
- text remains editable,
- SVG/vector content remains editable/inspectable as far as the chosen backend supports,
- no full-slide rasterization,
- notes/citations/provenance metadata are carried according to the approved contracts.

### P1.10 — append revision + meeting delta

After the first build:

1. append a new revision/event that changes B001 Discussion,
2. select/revise the canonical Next Step,
3. preserve the previous commitment and its status/closure/blocker state,
4. rebuild the Master Deck,
5. build a meeting projection since the earlier cursor.

The meeting projection must explicitly prove:

- previous commitment did not disappear,
- owner is preserved,
- target window is preserved,
- completion/closure evidence or blocker is shown,
- decision binding is preserved,
- next action/timing is shown,
- parallelizable workstream is shown,
- scientific Claims are selected/referenced rather than rewritten as new truth.

### P1.11 — Professor Profile

Implement a versioned project `professor-profile.yaml` fixture consumed by Professor QA.

It must encode the currently approved project rules at minimum:

- Scientific Method required,
- research question before data,
- Literature synthesis toward mechanism/hypothesis/strategy,
- mechanism context before solution,
- Discussion updates decision,
- failed experiments and changed hypotheses remain traceable,
- cumulative/layer-by-layer story,
- persistent fishbone/research-map orientation requirement for later recipes,
- previous commitments/status in Group Meeting,
- next steps + timing,
- blockers/dependencies/parallel work,
- figures dominate and text interprets,
- structured high information density is allowed,
- primary language `zh-TW`,
- English technical terminology allowed,
- exemplar roles: 1+3 template language; 2 content layout/figure composition,
- fonts unlocked/pending actual private template profiling.

Do not encode professor preferences only as hard-coded Python constants.

### P1.12 — canonical QA pipeline

Implement the exact ordered pipeline:

1. schema/ledger integrity
2. scientific reasoning
3. citation/evidence provenance
4. professor-style logic
5. compile/assemble PPTX
6. structural PPTX engineering QA
7. render/montage visual QA
8. native PowerPoint round-trip acceptance
9. final deck/version audit
10. release

For the committed synthetic environment, Stage 8 may legitimately return `blocked_environment` if native Windows PowerPoint is unavailable.

If Stage 8 is blocked, the synthetic build must **not claim production release**. It may produce a candidate/build artifact with explicit blocked status.

A downstream stage must not be marked passed after an upstream blocking failure unless the pipeline has been rerun from the proper owning stage.

### P1.13 — render/montage QA evidence

Phase 1 must actually render the generated deck using the available renderer and produce:

- individual slide PNGs,
- full-deck montage/contact sheet,
- changed-slide montage for the revised build where meaningful,
- render logs,
- font/substitution information where available.

Automated visual checks must cover at least:

- off-slide/overflow objects,
- collisions/overlap,
- missing images,
- unreadable/cropped labels,
- blank renders,
- expected slide dimensions,
- broken `zh-TW` glyphs where detectable.

Codex must also perform a visual inspection of the render/montage and report specific observations. Do not claim visual QA from code-only checks.

### P1.14 — structural PPTX QA

Unzip/audit the generated PPTX and verify at minimum:

- package content types,
- relationship targets exist,
- generated slides link to expected native layouts/masters,
- unique slide IDs/order,
- media references,
- notes references if used,
- no orphan/broken parts introduced by generation,
- source template was not overwritten,
- full-slide screenshots were not substituted for editable content.

### P1.15 — required negative fixtures/tests

Implement explicit negative cases for at least all of these:

1. dangling `Cxxx` Claim reference,
2. Block without research question,
3. hypothesis/mechanism without falsification/prediction,
4. Literature containing only a source list without synthesis,
5. Next Step missing owner/timing/decision binding,
6. Experiment missing controls/variables/metrics/decision rule,
7. `research_status` incorrectly used as story visibility,
8. meeting projection loses a prior unfinished commitment,
9. generated illustration masquerades as scientific evidence,
10. failed experiment becomes unreachable from history,
11. unresolved critical QA finding attempts release.

Each fixture/test must assert the expected blocking pipeline stage and a stable rule/error identifier where practical.

## Phase 1 acceptance criteria

The reviewer will not approve Phase 1 based only on unit tests or code presence.

All of these must be demonstrated:

- schemas are executable and non-trivial,
- ledger replay reconstructs the same normalized B001 and preserves prior revisions,
- all Claim references resolve,
- Scientific Method fields are machine-addressable,
- Literature synthesis is validated,
- Experiment design is validated without prose inference,
- canonical Next Step is one Action Item object,
- research status and story visibility change independently,
- failed history remains reachable,
- meeting delta preserves commitments and timing,
- scientific plot is reproducible from registered CSV and verified against source values,
- synthetic PPTX native layout/master relationships survive,
- exactly one PPTX backend is implemented,
- Slide Specs are backend-neutral,
- two recipes compile deterministically,
- Master Deck contains editable content and is not flattened,
- rendered slide images and montage exist,
- visual QA was actually inspected,
- structural PPTX QA evidence exists,
- QA report records exact canonical stage order,
- blocked native PowerPoint environment is represented honestly,
- no unresolved critical finding is allowed to claim release,
- all eleven required negative tests fail at the expected gate,
- append/rebuild/meeting-delta scenario passes.

## Out of scope for Phase 1

Do not implement unless strictly necessary for the vertical slice:

- public skill/marketplace registration,
- the complete skill catalog,
- the full slide recipe library,
- real/private NCKU/AMPL template ingestion into Git,
- production Group Meeting acceptance,
- defense curation implementation beyond any minimal contract stub already required,
- automated literature retrieval pipeline,
- full literature-figure extraction workflow,
- image-generation workflow,
- automatic slide repair agents,
- parallel PPTX backends,
- final font calibration from private exemplars.

## Implementation discipline

- Make small logical commits where useful, but the final branch state must be coherent.
- Do not hide corrected failed attempts. Report them under tests/known issues.
- Prefer deterministic scripts over manual steps.
- Keep synthetic assets clearly labeled synthetic.
- Do not fabricate real papers, data, instruments, or experimental provenance.
- Do not modify unrelated repository areas.
- Do not update the existing public skill count/registries in this phase.

## Required Phase 1 implementation report

Write:

`thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`

Follow every section required by `REVIEW_PROTOCOL.md`.

Additionally include these Phase 1-specific sections/evidence:

- schema inventory and semantic validators,
- ledger replay demonstration,
- B001 Scientific Method trace,
- Claim/evidence/action graph summary,
- synthetic fixture inventory,
- template profile summary,
- slide recipe summary,
- generated Deck Manifest,
- generated QA Report summary,
- first-build versus revised-build cursor/manifest diff,
- meeting-delta evidence,
- negative-test matrix,
- exact artifact paths,
- render/montage paths,
- visual inspection findings,
- structural PPTX inspection findings,
- native PowerPoint acceptance status,
- any blocked environment conditions.

The report must not merely say an artifact exists. It must give enough paths, hashes, commands, and test evidence for the reviewer to independently inspect it.

## Required machine-readable footer

```yaml
codex_report:
  phase: PHASE_1
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: <sha-or-null>
  files_added: []
  files_modified: []
  files_deleted: []
  artifacts: []
  render_previews: []
  tests_run: []
  tests_passed: []
  tests_failed: []
  known_failures: []
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```

## Remote-delivery gate

After implementation:

1. commit Phase 1 changes,
2. push to `origin/codex/thesis-deck-system`,
3. verify the remote branch head,
4. verify the Phase 1 report exists remotely,
5. verify key text artifacts/schemas remotely,
6. if binary artifacts are not committed by policy, report their exact local/release-artifact handling and provide all inspectable metadata/previews that are permitted,
7. do not write `READY_FOR_REVIEW: yes` unless the remote implementation/report state is verified.

## Final Codex response format

Return:

- repository:
- branch:
- commit SHA:
- pushed: yes/no
- remote verification: yes/no
- Phase 1 report path:
- files added:
- files modified:
- files deleted:
- tests/checks run:
- tests passed/failed summary:
- PPTX artifact path/status:
- render paths:
- montage paths:
- QA report path/status:
- native PowerPoint acceptance: pass/blocked/not-run
- known failures:
- blocked environment conditions:
- unresolved questions:

Write:

`READY_FOR_REVIEW: yes`

only when the implementation and report are pushed and remotely verified.

Then stop and wait for reviewer approval.
