# Thesis Deck System — Phase 2 Task

## Authorization

Phase 1 is APPROVED in:

`thesis-deck-system/reviews/PHASE_1_FINAL_REVIEW.md`

This task authorizes **Phase 2 only**.

Phase 2 goal: move from a synthetic proof-of-mechanics to a professor-specific presentation production architecture centered on the user's real template/exemplar grammar, without yet claiming production Group Meeting release readiness.

Public skill registration and production release remain unauthorized.

## Required reading

Synchronize `origin/codex/thesis-deck-system`, then read completely:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/reviews/PHASE_1_FINAL_REVIEW.md`
3. `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`
4. `thesis-deck-system/TASK_PHASE_1.md`
5. `thesis-deck-system/TASK_PHASE_1_REVISION_4.md`
6. this file

Also inspect the current package, schemas, Phase 1 artifacts, professor profile, and any existing skill inventory relevant to slides, diagrams, scientific figures, literature, and citation verification.

## Professor presentation requirements to preserve

These are not optional style suggestions. They are project constraints:

### Scientific Method narrative

Every research block must remain traceable as:

Observation
→ Literature
→ Mechanism
→ Solution / Strategy
→ Experiment
→ Result
→ Discussion / Decision
→ Next Step / Timing

Do not compress this into a generic business-storytelling model.

### Cumulative history

The professor prefers research reports to accumulate layer by layer. Failed experiments, superseded hypotheses, discussion history, and prior commitments remain reachable from the Master Deck history. Meeting views are projections; they do not rewrite the research ledger.

### Visual preference hierarchy

Use the project convention:

- **Template / Master language:** first + third exemplar decks.
- **Content layout and scientific figure composition:** second exemplar deck is the primary reference.
- **Scientific narrative:** professor profile + Scientific Method.

The desired style is white-background, formal academic/research, structured high information density, figures dominant, Traditional Chinese as primary language with English technical terms retained where appropriate.

### Fishbone / research map

Fishbone/research-map is a core recurring page, not decoration. Its stable skeleton must show the thesis problem, strategy branches, experiment/characterization branches, current branch highlight, completed work, and final deliverables.

## Phase 2 mission

Build the professor-specific **template / visual-grammar / layout-director layer** on top of the Phase 1 scientific control plane.

The system must support private local PowerPoint exemplar/template files without requiring them to be committed to Git.

If the real private fixture files are unavailable in the runtime, implement the complete ingestion and validation path and finish all synthetic/sanitized tests, but report the real-fixture acceptance section as `blocked_fixture`. Do not fabricate template findings.

## P2-R1 — Resolve Phase 1 private-ingestion technical debt

Before accepting private PPTX files:

1. Replace fixed-depth repository-root logic such as `template_path.parents[n]` with an explicit path resolver/context object.
2. Add a private-fixture locator abstraction supporting at least:
   - environment variable root;
   - local config path;
   - explicit CLI/API argument.
3. Canonical committed records must use repository-relative paths or stable private aliases such as `private://template-primary-1`; never commit machine-specific absolute paths.
4. Exact private source paths may exist only in ignored/local runtime configuration and local logs that are not committed.
5. Fix SVG bridge targeting: attach Office SVG metadata to the exact generated slide/placement that owns the SVG asset. Do not infer the target from "last slide" ordering.
6. Add negative tests for multiple SVG-bearing generated slides and reordered generated slides.

## P2-R2 — Private fixture policy and ingestion manifest

Create a local/private fixture contract with explicit roles:

- `template_primary_1` — first exemplar/template role;
- `layout_exemplar_2` — second exemplar/content-layout role;
- `template_primary_3` — third exemplar/template role;
- optional `real_sanitized_fixture` — real thesis scientific-content acceptance fixture.

Requirements:

- private files are NOT committed by default;
- add `.gitignore` rules for the private fixture root and private generated artifacts;
- create a committed example config with aliases only, no local paths;
- create a runtime validation command that reports which aliases are resolved, source SHA-256, file type, slide count, and whether ingestion is blocked;
- never silently substitute a synthetic template for a missing private alias when running a real-fixture acceptance command;
- synthetic fallback is allowed only when the caller explicitly requests synthetic mode.

## P2-R3 — Upgrade Template Profile for real academic decks

Extend Template Profile beyond Phase 1's minimal layout identity.

Profile at minimum:

- slide size/aspect ratio;
- all slide masters;
- all layouts in runtime order;
- layout → master identity;
- layout names;
- placeholder types/indices/geometry;
- theme fonts;
- theme colors;
- background/fill information where inspectable;
- recurring master-level/footer/header/logo/slide-number objects where inspectable;
- fixed navigation zones;
- section-divider layouts;
- title-zone geometry;
- body safe-area geometry;
- content placeholders versus decorative/master objects;
- native notes/master relationships required for round-trip acceptance.

Do not infer semantic roles solely from layout names. Semantic-role assignment must be explicit and reviewable.

Persist a sanitized profile that does not copy private slide text/content beyond minimal structural labels needed for layout identity.

## P2-R4 — Exemplar visual-grammar extractor

Implement a profiler for the second exemplar deck that extracts **composition grammar**, not proprietary/research content.

For each exemplar slide, record structural descriptors such as:

- slide index;
- title geometry;
- text-box geometry;
- image/figure geometry;
- table geometry;
- relative visual/text area ratio;
- left/right or top/bottom comparison structure;
- repeated caption bands;
- callout/red-box geometry;
- image-matrix structure;
- arrows/connector density;
- dominant content region;
- whether the slide is comparison-driven, process-driven, result-driven, or observation-driven;
- estimated information-density class.

Do not commit extracted private scientific text, unpublished data, or embedded literature figures unless explicitly permitted.

Create a sanitized `visual-grammar.json` / schema that can drive layout selection.

## P2-R5 — Professor-specific layout archetype library

Implement a first production-oriented layout archetype library. Do not let the model invent arbitrary layouts when a matching archetype exists.

At minimum support:

1. `cover`
2. `progress_todo`
3. `fishbone_research_map`
4. `observation_problem`
5. `photo_schematic_pair`
6. `literature_mechanism`
7. `control_vs_treatment`
8. `experiment_setup`
9. `hero_plot_discussion`
10. `image_matrix`
11. `go_partial_no_go`
12. `next_step_schedule`

Each archetype must define:

- semantic purpose;
- allowed Scientific Method stages;
- required bindings;
- minimum/maximum visual assets;
- title/take-home requirements;
- text budget;
- citation zone;
- layout role or composition recipe;
- failure policy (`split`, `block`, or alternate archetype);
- professor-profile rules it satisfies;
- Traditional Chinese typography behavior;
- expected visual QA checks.

The existing Phase 1 recipes should migrate into this library rather than remain special-case hard-coded behavior.

## P2-R6 — Layout Director

Implement a deterministic `layout_director` that selects an archetype from structured scientific content and available assets.

Inputs must include:

- Research Block / Stage data;
- Claim/Evidence/Asset bindings;
- professor profile;
- template profile;
- visual grammar;
- requested deck kind (`master`, `meeting`, `defense`);
- target language;
- current/history emphasis.

Selection must be explainable. Persist a decision record containing:

- selected archetype;
- candidate alternatives;
- rejection reasons;
- required missing asset/content warnings;
- density estimate;
- split recommendation if over budget.

Do not use a generic LLM-only free-form layout decision as the authoritative output. A model may advise, but deterministic constraints must validate the decision.

## P2-R7 — Scientific Method story compiler

Add a compiler that converts one Research Block into an ordered page sequence while preserving professor logic.

For a full block, default sequence:

1. Observation / Problem
2. Literature synthesis
3. Mechanism / Hypothesis
4. Solution / Strategy
5. Experiment Design
6. Result / Discussion / Decision
7. Next Step / Timing

Small blocks may combine adjacent stages only when the compiler records why the combination remains scientifically clear.

The compiler must:

- keep `research_question` visible before the relevant data section;
- preserve literature → mechanism implication;
- preserve falsifiable hypothesis / predicted result;
- show Control / Proposed or control/baseline structure when applicable;
- show Result, interpretation, Decision, and Next Step together when using a result-focused archetype;
- preserve prior failed/superseded layers in Master history;
- support Meeting projection that highlights the current layer while keeping prior commitments reachable.

## P2-R8 — Fishbone / research-map engine

Implement a stable fishbone/research-map source model and renderer.

Requirements:

- editable vector final source (SVG or Draw.io-compatible representation);
- stable node IDs across meetings;
- branches linked to Research Block IDs / strategy IDs;
- statuses such as planned / active / completed / failed_but_informative / superseded;
- current branch highlight without rebuilding the whole graph;
- failed/superseded branches remain available in history;
- output fits the primary template content safe area;
- deterministic text wrapping and connector routing;
- figure source/provenance recorded as an Asset Manifest.

Do not use generative-image output as the canonical fishbone source.

## P2-R9 — Internal Skill layer (not public registration)

Create internal repo-local skill specifications that wrap the now-stable control-plane capabilities. Do not register/install them globally yet.

At minimum create:

- `thesis-deck-router`
- `scientific-method-planner`
- `master-deck-ledger`
- `layout-director`
- `professor-qa`

Each Skill specification must define:

- trigger conditions;
- required inputs;
- outputs;
- allowed tool/backend calls;
- prohibited shortcuts;
- failure/blocked behavior;
- handoff to the next Skill;
- artifacts that must be persisted;
- QA gates required before handoff.

The router must make explicit when to invoke:

- literature/citation tools;
- scientific plotting;
- vector mechanism/diagram tooling;
- image generation for contextual/decorative imagery only;
- PPTX assembly;
- render/montage QA;
- professor QA.

Do not let image generation create experimental data, literature figures, or quantitative evidence.

## P2-R10 — First professor-style multi-page acceptance deck

Using synthetic or sanitized scientific content, generate a review deck that exercises the new grammar.

Minimum generated pages, excluding any inherited exemplar/template pages:

1. Progress / To-do
2. Fishbone / current-position map
3. Observation / Problem
4. Literature + Mechanism
5. Control vs Proposed / Experiment Design
6. Hero Result + Discussion + Decision + Next Step

Preferred: add a 7th page for Schedule / dependency / parallel work if not already clear.

The deck must use:

- the primary-template semantic language when private fixtures are available;
- the second exemplar's structural content grammar;
- Traditional Chinese primary text;
- English technical terms where appropriate;
- real structured scientific bindings from the synthetic/sanitized fixture;
- editable text and vector scientific assets;
- Slide-Spec-derived notes/citations.

If private fixtures are unavailable, generate the same deck with the synthetic template but mark template acceptance as `blocked_fixture`. Do not claim professor visual fidelity is accepted.

## P2-R11 — Visual QA upgraded for professor layout

Add programmatic and persisted visual checks for the generated professor-style acceptance deck:

- slide dimensions/aspect ratio;
- nonblank render;
- text overflow;
- object overlap except intentional overlays;
- title-zone occupancy;
- footer/nav safe-area violations;
- minimum font sizes by element role;
- figure/text ratio;
- citation legibility;
- comparison symmetry where archetype requires it;
- image-matrix alignment where applicable;
- fishbone connector collisions;
- page-level take-home presence;
- excessive text density warning;
- slide-to-archetype geometry conformance.

Persist per-slide findings with severity and repair suggestions.

Visual QA PASS must not be a self-authored sentence with no measurable evidence.

## P2-R12 — Professor QA expanded beyond Phase 1 smoke checks

Professor QA must consume the versioned professor profile and evaluate at minimum:

- question before data;
- Observation → Literature → Mechanism → Solution chain;
- literature synthesis rather than paper listing;
- falsifiable mechanism/hypothesis;
- experiment answers a stated question;
- control/baseline visibility;
- N / replicate / metric / units visibility where relevant;
- Result versus interpretation separation;
- Decision strength calibrated to evidence;
- prior commitment carry-forward;
- Next Step with owner/timing/dependency;
- failed/superseded history preservation;
- fishbone current-location consistency;
- high information density without loss of hierarchy.

Persist rule-level evidence and repair advice.

## Real/private fixture acceptance behavior

If real template/exemplar files are available locally:

- profile them;
- record private source hashes and aliases in local/private records;
- generate sanitized structural profiles;
- run the Phase 2 acceptance deck against the real primary template;
- render every slide;
- produce montage;
- run structural QA;
- run professor QA;
- do not commit private source binaries unless explicitly authorized.

If they are unavailable:

- do not ask the reviewer to infer their structure;
- mark `private_fixture_acceptance: blocked_fixture`;
- report the exact expected aliases/configuration mechanism;
- complete all non-private Phase 2 implementation/tests.

## Native PowerPoint

Native Microsoft PowerPoint round-trip remains a production release gate.

Phase 2 may still be reviewed with Stage 8 `blocked_environment`, but must not claim production readiness.

If a real Windows PowerPoint environment is available, run native acceptance and preserve evidence; otherwise report it honestly.

## Required tests

Add positive and negative tests covering at least:

1. private fixture alias resolution;
2. missing private fixture does not silently fall back;
3. no committed absolute private paths;
4. exact SVG-bearing slide targeting with multiple/reordered SVG slides;
5. Template Profile role/path/master consistency on multi-layout fixtures;
6. visual-grammar extraction sanitization;
7. archetype validation;
8. layout-director deterministic selection;
9. over-budget content causes split/block rather than font crushing;
10. Scientific Method compiler preserves stage ordering;
11. failed/superseded history remains reachable;
12. fishbone stable IDs/status highlighting;
13. professor QA catches missing Literature→Mechanism implication;
14. professor QA catches missing control / timing / prior commitment;
15. visual QA catches deliberate geometry/overflow/density violations;
16. no generated context accepted as scientific evidence;
17. no private source text copied into sanitized grammar/profile outputs;
18. existing Phase 1 regression suite remains green.

## Required artifacts

At minimum persist reviewable non-private artifacts:

- upgraded schemas/contracts;
- example private-fixture alias config;
- sanitized template profile fixture;
- sanitized visual grammar fixture;
- archetype registry;
- layout-director decision records;
- fishbone source + SVG preview;
- 6+ page acceptance Slide Specs;
- acceptance Deck Manifest;
- acceptance PPTX;
- structural audit;
- professor QA report;
- visual QA report;
- rendered slide PNGs;
- full montage;
- implementation report.

Private artifacts remain local/ignored unless explicitly permitted.

## Phase 2 implementation report

Write:

`thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`

Follow `REVIEW_PROTOCOL.md` and include explicit traceability for P2-R1 through P2-R12.

Report must explicitly state:

- private fixture mode: real / synthetic / blocked_fixture;
- resolved private aliases without revealing forbidden absolute paths;
- template profile IDs/hashes/roles;
- visual grammar version;
- archetypes implemented;
- layout-director decisions for every generated slide;
- Scientific Method page sequence;
- fishbone asset/source IDs;
- professor QA results;
- visual QA results;
- PPTX structural status;
- native PowerPoint status;
- known failures;
- unresolved fixture/privacy questions.

## Delivery

Commit and push Phase 2 work to:

`origin/codex/thesis-deck-system`

Verify remote state.

Final Codex response must include:

- repository
- branch
- commit SHA
- pushed
- remote verification
- Phase 2 report path
- files added/modified/deleted
- tests/checks run
- tests passed/failed
- P2-R1–P2-R12 traceability
- private fixture status
- template profile status
- visual grammar status
- archetype registry path
- fishbone source/render paths
- acceptance PPTX path/status
- render/montage paths
- professor QA path/status
- visual QA path/status
- native PowerPoint status
- known failures
- unresolved questions

Only then write:

`READY_FOR_REVIEW: yes`

Then STOP.

Do not begin Phase 3 or public skill registration until reviewer approval.
