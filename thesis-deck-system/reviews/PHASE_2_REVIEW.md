# Phase 2 Reviewer Verdict — REVISE

Reviewed implementation commit: `f56ab7476bcb5cfec1041715b620e6299b7273e2`.

## Verdict

**REVISE. Phase 3 is not authorized. Production Group Meeting readiness is not authorized.**

The Phase 2 submission establishes several correct foundations: separate Hypothesis/Problem pages, versioned fishbone records, H01→H02 transition objects, a governed archetype registry, private-fixture blocking, exact SVG-to-slide OpenXML relationships, and a larger 18-generated-slide acceptance deck. Those directions are accepted.

However, the current vertical slice regresses some approved Phase 1 provenance guarantees and substantially overstates what the Layout Director, Professor QA, Visual QA, and repo-local Skills actually execute. These defects must be corrected before Phase 2 can close.

## Accepted foundations to preserve

- Hypothesis and Problem are modeled separately and compiled to separate slides.
- H01 and H02 bind different fishbone revisions.
- Fishbone branch IDs are stable across revisions where semantics persist.
- H02 contains explicit derivation metadata from H01.
- Private fixture lookup returns `blocked_fixture` instead of silently substituting a real-template claim.
- Native PowerPoint remains honestly `blocked_environment`.
- Canonical PPTX retains actual SVG relationships to the owning generated slide.
- A01–A18 archetype metadata is a useful registry and should be preserved.
- zh-TW is treated as the primary presentation language.

## Blocking findings

### P2-B1 — Phase 1 temporal/provenance invariants are not preserved end-to-end

Phase 2 Slide Specs bind `B101` / `B201`, but the Phase 2 ledger never materializes corresponding Research Block records. The new Phase 2 history instead appends fishbone, claims, problems, evidence, discussions, decisions, actions, experiment/result stages, and hypothesis layers directly.

In addition, the Phase 2 claim/evidence/action/decision payloads are lightweight ad-hoc records rather than validated instances of the approved Phase 1 canonical contracts. Phase 2 therefore has two levels of provenance semantics: strong Phase 1 contracts and weaker Phase 2 synthetic payloads.

Required correction:

- Every `block_ref`, Claim, Evidence, Asset, Action, Decision, and Scientific Stage referenced by a Phase 2 Slide Spec must resolve from the materialized ledger at that slide's source cursor.
- Reuse or explicitly version/extend the approved Phase 1 contracts; do not create a weaker parallel object system.
- Stage 1 must execute cursor-aware binding validation over all Phase 2 Slide Specs / Manifest entries, not only Hypothesis/Fishbone history.

### P2-B2 — The event chronology contains future references and inverted scientific causality

The current synthetic history records H01 `layer_discussion_recorded`, D101, NS101, and the layer summary before EXP101/EXP102 and RES101/RES102 are appended. H02 similarly records its integrated discussion, decision, action, and summary before EXP201/RES201.

Also, H001 is created at cursor 14 with `transition_ref: TR-H001-H002`, but the transition event does not exist until cursor 19. All H01 Slide Specs are then forced to source cursor 14, including the H01→H02 transition slide. This leaks future research state into an earlier historical snapshot.

Required correction:

- No event may reference an object that is not materialized at that event/cursor unless the contract explicitly defines a non-binding future intent field.
- Experiment/result evidence must exist before the integrated Discussion/Decision/Summary that claims to interpret it.
- A transition slide must use the transition object's actual source cursor; it may not inherit the earlier H01 layer cursor if the transition was created later.
- Add a causal-temporal validator and negative tests for discussion-before-result and transition-before-new-hypothesis/evidence.

### P2-B3 — Slide scientific content is still compiled from the raw fixture / hard-coded prose, not from materialized ledger state

`phase2_build.py` calls `compile_hypothesis_layer()` on `fixture["hypothesis_layers"]`, then `_hydrate(..., fixture, ...)`; `_content_text()` reads the fixture and also contains hard-coded presentation prose. The Progress slide similarly hard-codes NS101 / H02 / NS201 text rather than compiling the actual meeting projection.

The ledger is persisted and replayed, but it is not the canonical input to the story/content compiler.

Required correction:

`persisted ledger -> materialize(cursor) -> projection -> story/content compiler -> Slide Specs` must be the only scientific-content path.

- Historical H01 slides must be reproducible from their own cursor states.
- Transition content must resolve from the transition record at its cursor.
- Progress/previous-commitment content must resolve from `meeting_projection`, not fixture literals.
- Add mutation tests: changing fixture data after the ledger is serialized must not change rebuilt Slide Specs unless new ledger events are appended.

### P2-B4 — The Layout Director is currently a semantic label mapper, not a real layout engine

Although A01–A18 metadata is useful, `LayoutDirector.select()` returns the same single full-width `content` placement for every archetype. The generated `layout-plans.json` confirms essentially identical placement geometry across Hypothesis, Problem, Fishbone, Experiment, Result, Discussion, and Progress pages. All archetypes also resolve to the same synthetic `content_academic` native layout.

The PPTX assembler does not consume the archetype placement plan as a general geometry contract; most recipes fall through to one generic text box plus a generic right-side image placement. Therefore the acceptance deck does not yet prove the professor-style body composition system requested for Exemplar 2.

Required correction:

Implement actual governed geometry for the core archetypes and make the assembler consume it. At minimum demonstrate distinct geometry for:

- A01 Hypothesis
- A02 Problem
- A03 Fishbone locator
- A04 Observation / Problem
- A05 Literature + Mechanism
- A06 Mechanism + Strategy
- A08 Control vs Proposed
- A09 Experiment Design
- A10/A11 Result
- A14 Integrated Discussion
- A15 Summary / Decision
- A16 Transition
- A17 Progress / To-do
- A18 Next Step / Schedule

The same native PowerPoint layout may be used when appropriate, but body geometry, hierarchy, slots, and constraints must differ by archetype.

Also resolve `split_recommendation` / over-budget warnings before assembly; final acceptance Slide Specs may not silently ignore a required split.

### P2-B5 — Professor QA V2 reports checks that it does not actually execute

`run_professor_qa_v2()` lists `fishbone_history`, `integrated_discussion`, and `summary_decision` as executed checks, but the implementation only verifies a subset: Hypothesis/Problem separation, fishbone existence/focus, presence of a summary slide, and owner/timing on current commitments.

It does not actually prove the professor rules specified for Phase 2, including:

- historical fishbone revision equality at the layer cursor;
- Scientific Method order;
- Literature synthesis rather than source listing;
- Mechanism -> Solution causality;
- Experiment variables/control/N/metrics/decision rule;
- all required Results before Integrated Discussion;
- cross-experiment synthesis;
- Summary hypothesis status + decision + remaining uncertainty;
- transition provenance to the next Hypothesis;
- failed/partial historical-layer reachability;
- prior meeting commitment carry-forward.

Required correction:

Implement owning checks for each claimed Professor QA rule. `executed_checks` must list only checks that ran. Add corrupted-input negative tests for every critical rule.

Professor QA must consume a persisted/versioned professor profile, not a small inline synthetic dict that omits most project rules.

### P2-B6 — Visual QA V2 also reports checks that it does not execute

`run_visual_qa_v2()` declares checks for overlap, title hierarchy, zh-TW readability, density, and archetype geometry, but the actual implementation only checks render existence, exact dimensions, nonblank variance, placement canvas bounds, and minimum font size.

`visual-inspection.json` then repeats the same generic sentence for every slide and marks all slides PASS. That is not evidence of slide-by-slide visual inspection.

Required correction:

Implement or stop claiming each check. Phase 2 acceptance should execute, at minimum:

- geometry overlap/collision detection from PPTX/Slide Spec coordinates;
- title-vs-body hierarchy;
- minimum body/title font rules;
- zh-TW wrapping/line-count/overflow checks;
- density budget and unresolved split warnings;
- archetype-specific required slot geometry;
- fishbone current-focus visibility;
- fair comparison symmetry for Control/Result comparison pages;
- Result vs Discussion visual distinction where applicable.

Persist specific, non-boilerplate observations for each acceptance slide. If a check is human/vision-only, mark it separately and provide concrete inspection notes rather than auto-generating PASS text.

### P2-B7 — The repo-local Skill layer does not satisfy the requested orchestration system

Only seven very small SKILL.md files were added. For example, `hypothesis-layer-compiler/SKILL.md` is only frontmatter plus one sentence. The required orchestration roles from the specification are missing or renamed without equivalent coverage, especially:

- `thesis-deck-router`
- `scientific-method-planner`
- `hypothesis-layer-planner`
- `master-deck-ledger`
- `fishbone-director`
- `layout-director`
- `professor-qa`

The current Skill set also lacks detailed trigger rules, input/output contracts, tool routing, failure modes, stop conditions, and handoff semantics. It cannot yet reliably choose the right tool at the right time.

Required correction:

Create/expand the repo-local Skill layer so the seven required orchestration responsibilities exist explicitly. Additional specialist Skills may remain.

Each required SKILL.md must define at least:

- trigger / when to use;
- non-trigger / when not to use;
- required inputs;
- ordered workflow;
- tool/skill routing;
- output contract;
- provenance requirements;
- failure/block conditions;
- handoff / next skill;
- professor-specific invariants.

Also persist a machine-readable routing map and test its deterministic routes for representative user requests.

### P2-B8 — Fishbone parent hierarchy is stored but not rendered

`fishbone-revision.schema.json` contains `parent_ref`, but `render_fishbone_svg()` separates roots and children and then connects every branch directly to the main spine. Parent/child topology is therefore visually lost.

The professor's total fishbone is intended to show the research hierarchy, not merely a flat list of branch cards.

Required correction:

- Render child branches as children of their declared parent branch (or another deterministic hierarchy-preserving fishbone geometry).
- Validate parent refs, cycles, duplicate IDs, and orphan parents.
- Add collision/overflow handling for growing fishbone revisions.
- Preserve stable branch placement where possible across revisions so the research map remains visually learnable over time.
- Add a test proving a child added in rev2 appears under the same parent without moving unrelated stable branches unnecessarily.

## Additional reviewer notes

### Private fixture status

`blocked_fixture` is acceptable for this revision and is **not** a blocker. Do not fabricate professor-template fidelity. Real Exemplar 1/2/3 profiling remains required before production acceptance.

### Native PowerPoint

`blocked_environment` is acceptable for Stage 8 and is **not** a blocker. Do not substitute LibreOffice as native acceptance.

### Binary render review limitation

The reviewer can audit committed render metadata, QA code, Slide Specs, and OpenXML artifacts through the repository connector, but the connector does not expose binary PNG bytes for direct reviewer vision inspection. This increases—not reduces—the requirement that Codex persist concrete and truthful slide-specific visual inspection evidence.

## Required verdict after correction

Phase 2 may be approved only when the synthetic vertical slice proves:

`canonical contracts -> causally ordered ledger -> cursor materialization -> projections -> state-derived Hypothesis Layer story -> real archetype geometry -> PPTX -> structural QA -> executed Professor QA -> executed Visual QA`

without future-state leakage or claimed-but-unexecuted checks.
