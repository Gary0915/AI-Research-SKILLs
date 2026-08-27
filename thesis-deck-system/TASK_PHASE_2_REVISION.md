# Thesis Deck System — Phase 2 Revision Task

## Authorization

Reviewer verdict is `REVISE` in:

`thesis-deck-system/reviews/PHASE_2_REVIEW.md`

This task authorizes **Phase 2 correction only**.

Do not begin Phase 3. Do not globally/publicly register Skills. Do not claim production Group Meeting readiness.

## Required reading

Synchronize `origin/codex/thesis-deck-system`, then read completely:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/reviews/PHASE_1_FINAL_REVIEW.md`
3. `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`
4. `thesis-deck-system/TASK_PHASE_2.md`
5. `thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`
6. `thesis-deck-system/reviews/PHASE_2_REVIEW.md`
7. this file

## Mission

Correct every blocker `P2-B1` through `P2-B8` while preserving the accepted Phase 1 and Phase 2 foundations.

The corrected bounded chain must be:

`canonical scientific objects`
`-> causally ordered append-only ledger`
`-> cursor materialization`
`-> master/meeting projections`
`-> state-derived Hypothesis Layer story`
`-> governed archetype geometry`
`-> PPTX assembly`
`-> structural QA`
`-> Professor QA`
`-> Visual QA`

No step may invent scientific content independently of the previous canonical step.

---

## P2-B1 — Restore full Phase 1 provenance guarantees in Phase 2

Phase 2 must not use unresolved `B101` / `B201` Slide Spec refs or weaker parallel Claim/Evidence/Action/Decision records.

Required implementation:

- Materialize valid Research Block records for every `block_ref` used by Phase 2 Slide Specs.
- Every Claim/Evidence/Asset/Action/Decision/Scientific Stage used by a slide must exist at that slide's source cursor.
- Reuse the approved Phase 1 schemas where possible. If Phase 2 requires an extension, version it explicitly and keep at least the same provenance strength.
- Run cursor-aware binding validation across Phase 2 Slide Specs and Deck Manifest entries.
- A Slide Spec must fail validation if any referenced scientific object is absent, future, outside its block/layer graph, or revision-incompatible.

Required negative tests:

- nonexistent B201 block binding;
- future Claim;
- future Evidence;
- future Action;
- future Decision;
- future Result/Stage;
- object reachable from a different layer/block but not the active one.

---

## P2-B2 — Correct causal event chronology and eliminate future leakage

Rebuild the synthetic event history so scientific causality is real.

Required invariants:

- Experiment metadata exists before its Result.
- Results required by an Integrated Discussion exist before that Discussion.
- Integrated Discussion exists before the Decision/Summary that cites it.
- A Transition exists only after all result/discussion/decision/new-observation/new-hypothesis objects that it cites are materialized.
- No Hypothesis Layer record may bind a future `transition_ref` as if it already exists.
- Each Slide Spec uses the cursor of the state/object that actually supports that slide; not every slide in a historical layer must share one cursor.

The current failure case must become a negative regression test:

- H01 Transition at cursor 14 must fail if `TR-H001-H002` is appended later.

Also add tests rejecting:

- Discussion before its result set;
- Summary before the layer discussion/decision;
- Transition referencing a future new Hypothesis Claim or future observation;
- historical slide source cursor that cannot materialize all its bindings.

Prefer evolving a layer through append-only revisions rather than creating a final layer object containing future refs.

---

## P2-B3 — Compile all slide scientific content from materialized state/projections

Remove raw-fixture/hard-coded scientific-content compilation from the production Phase 2 build path.

Required architecture:

`Ledger.load()`
`-> materialize(slide/source cursor)`
`-> projection / object resolver`
`-> story/content compiler`
`-> Slide Spec`

Do not allow `_hydrate(...fixture...)`, `_content_text(...fixture...)`, or equivalent production code to become a second scientific source of truth.

The raw fixture may be used only to seed ledger events.

Required behavior:

- Hypothesis text resolves from materialized Claim.
- Problem text resolves from materialized Problem.
- Fishbone resolves from the bound historical Fishbone revision.
- Observation/Literature/Mechanism/Solution resolve from materialized Scientific Stage objects.
- Experiment/Result content resolves from the relevant stages/results.
- Discussion/Summary/Decision resolve from layer records at the slide cursor.
- Transition resolves from the transition record at its own cursor.
- Progress/previous commitments resolve only from `meeting_projection`.

Required mutation test:

After ledger serialization, mutate the source fixture file in-memory/on a temporary copy without appending ledger events. Rebuilding Slide Specs from the persisted ledger must produce byte-identical canonical content/spec hashes.

---

## P2-B4 — Turn the archetype registry into a real layout engine

Keep A01–A18 metadata, but implement distinct governed body geometry.

At minimum provide real geometry contracts for:

- A01 Hypothesis
- A02 Problem
- A03 Fishbone Locator
- A04 Observation / Problem
- A05 Literature + Mechanism
- A06 Mechanism + Strategy
- A08 Control vs Proposed
- A09 Experiment Design
- A10/A11 Result
- A14 Integrated Discussion
- A15 Layer Summary / Decision
- A16 Hypothesis Transition
- A17 Progress / To-do
- A18 Next Step / Timing

Each layout plan must define meaningful slots such as:

- hypothesis_statement
- derivation_strip
- previous_finding
- unresolved_conflict
- research_question
- primary_figure
- literature_evidence
- mechanism_diagram
- control_panel
- proposed_panel
- experiment_matrix
- result_plot
- result_annotation
- supporting_results
- contradicting_results
- uncertainty
- decision_status
- transition_nodes
- commitment_table
- timeline

The assembler must consume the Layout Plan coordinates/slot semantics. It may not ignore them and use one generic textbox/image location for most recipes.

At least six acceptance archetypes must have structurally different placement signatures, and core archetypes above must have semantically appropriate geometry.

### Over-budget policy

`split_recommendation: true` is not advisory noise. Before assembly the story/layout compiler must either:

1. split the content using an allowed archetype continuation; or
2. produce an explicit reviewed override with reason and verified visual QA.

No final acceptance Slide Spec may silently ignore an unresolved required split.

Required tests:

- A01 and A03 do not share the same slot signature;
- A08 has symmetric control/proposed regions;
- A14 contains separate evidence-synthesis and uncertainty/interpretation regions;
- A16 contains ordered transition-node regions;
- A17/A18 contain progress/timing geometry;
- assembler output shape positions match the selected plan within tolerance.

---

## P2-B5 — Implement real Professor QA V2

Use a persisted/versioned professor profile that contains the project rules. Do not construct a minimal inline profile solely for the synthetic build.

Professor QA must execute and persist evidence for at least:

1. Hypothesis page exists.
2. Problem page exists separately.
3. Fishbone page exists for every layer.
4. Fishbone revision equals the layer's historical revision at its slide cursor.
5. Current focus branch resolves and is highlighted.
6. Research question precedes deep result interpretation.
7. Literature contains structured synthesis, not only source refs.
8. Mechanism is evidence-linked.
9. Solution/Strategy is derived from the Mechanism.
10. Experiment design contains IV/control/baseline/N/metrics/units/method/prediction/decision rule.
11. All required layer Results precede final Integrated Discussion.
12. Integrated Discussion references the complete result set and contains support/contradiction/alternative/uncertainty synthesis.
13. Layer Summary contains hypothesis status, answered question, decision, remaining uncertainty, next question/step.
14. Transition provenance resolves to prior discussion/decision/results/new observation/new hypothesis.
15. Failed/partial/superseded layers remain historically reachable.
16. Meeting projection carries prior commitment status plus current next steps with owner/timing/dependencies/parallel work.

`executed_checks` must list only checks that actually ran.

Required negative tests must corrupt each critical rule and prove QA fails.

---

## P2-B6 — Implement truthful Visual QA V2

The current visual inspection artifact must be replaced with concrete executed evidence.

Automated checks should include where feasible:

- render exists;
- exact dimensions;
- nonblank;
- slide canvas bounds;
- text/image/shape overlap from PPTX geometry;
- title/body font hierarchy;
- minimum title/body font sizes;
- zh-TW wrapping/line count/overflow risk;
- density budget;
- unresolved split warning;
- required slot presence and archetype geometry;
- comparison symmetry/treatment fairness;
- fishbone current-focus marker exists and has sufficient prominence metadata;
- Result vs Discussion regions are distinct when required.

For render-dependent/manual/vision review, persist a separate inspection status rather than pretending it is the same automated check.

Each acceptance slide must have specific observations, for example:

- what the dominant visual is;
- whether the intended current fishbone branch is immediately visible;
- whether the research question is visually dominant enough;
- whether comparison panels are balanced;
- whether a plot label/annotation is legible;
- whether density is acceptable or requires split.

Do not reuse one generic sentence for all slides.

Required negative tests:

- overlapping placements;
- font below threshold;
- title not larger than body;
- out-of-bounds placement;
- over-budget unsplit slide;
- asymmetric A08/A11 comparison;
- fishbone slide with no current-focus marker;
- required archetype slot missing.

---

## P2-B7 — Build the required repo-local Skill orchestration layer

The following seven orchestration responsibilities are mandatory and should exist with these names unless a reviewer-approved compatibility alias maps exactly to them:

1. `thesis-deck-router`
2. `scientific-method-planner`
3. `hypothesis-layer-planner`
4. `master-deck-ledger`
5. `fishbone-director`
6. `layout-director`
7. `professor-qa`

Existing specialist Skills may remain, including render/provenance helpers.

Each required `SKILL.md` must contain meaningful operational instructions, not only one sentence.

Required sections/semantics:

- purpose;
- triggers;
- do-not-trigger conditions;
- required inputs;
- ordered workflow;
- tool / downstream Skill routing;
- outputs;
- provenance rules;
- professor-specific invariants;
- failure/block conditions;
- handoff conditions.

Create a machine-readable routing contract such as:

`thesis-deck-system/skill-routing.yaml`

It must show routes for at least:

- `更新這週 Group Meeting`
- `新增一個 Hypothesis`
- `整理這批實驗數據成結果頁`
- `畫目前研究魚骨圖`
- `做文獻與機制頁`
- `更新 Master Deck`
- `審核這份簡報`

Required tests verify deterministic top-level routing and mandatory handoffs.

Do not globally install/register these Skills in Phase 2.

---

## P2-B8 — Render a true hierarchical, stable fishbone

The renderer must use `parent_ref` semantics.

Required behavior:

- root branches connect to the thesis spine;
- child branches visually attach to the declared root/parent branch rather than all attaching directly to the main spine;
- branch IDs are stable;
- parent refs resolve;
- cycles are rejected;
- duplicate branch IDs are rejected;
- orphan parents are rejected;
- focus branch remains visually prominent;
- completed/partial/failed/future states remain visible;
- revisions preserve stable branch positions as much as possible so the map is learnable over time;
- growth triggers deterministic collision/overflow handling.

Required acceptance proof:

- FB001 rev1 and rev2 render side by side;
- `FB-ELECTRODE-CONTACT` appears under `FB-ELECTRODE` in rev2;
- stable unrelated branches retain positions within a documented tolerance;
- H01 still uses rev1 and H02 uses rev2;
- current overview uses latest rev2;
- adding a child does not retroactively mutate the H01 SVG/hash.

---

## Scientific Method data for Phase 2

The corrected fixture must actually contain structured scientific objects for each layer, including:

- Observation
- Literature synthesis
- Mechanism
- Solution / Strategy
- Experiment(s)
- Result(s)
- Integrated Discussion
- Layer Summary / Decision
- Next Step / Transition

Use/extend the approved `scientific-stage` contract or introduce an equally strict versioned replacement. Do not store these only as slide prose.

For Literature, preserve:

- consensus;
- disagreement/alternatives;
- known mechanism;
- research gap;
- relevance to observation;
- implication for hypothesis/strategy.

For Experiment, preserve:

- IV;
- controlled variables;
- controls/baselines;
- sample/replicate count;
- metrics;
- units;
- instrumentation/method;
- predicted outcomes;
- Go / Partial-Go / No-Go criteria.

---

## Acceptance deck after correction

Regenerate a professor-style synthetic deck large enough to test real geometry.

Keep the hypothesis-layer structure:

- Progress / previous commitments
- H01 Hypothesis
- H01 Problem
- H01 historical Fishbone
- H01 Scientific Method pages
- H01 Experiment design(s)
- H01 Results
- H01 Integrated Discussion
- H01 Summary / Decision
- H01 Transition
- H02 Hypothesis
- H02 Problem
- H02 historical Fishbone
- H02 Scientific Method / experiment/result content
- H02 Integrated Discussion
- H02 Summary / Decision / Next Step as appropriate

Do not optimize for minimum slide count.

The corrected deck should be rich enough to demonstrate distinct archetype geometry, not merely distinct titles.

---

## Required test plan

Before submission run:

1. full Phase 1 + Phase 2 pytest suite;
2. clean end-to-end Phase 2 rebuild;
3. exact schema validation for all canonical Phase 1/Phase 2 objects;
4. full persisted ledger hash/replay validation;
5. causal-temporal graph validation;
6. per-slide cursor binding validation;
7. fixture-mutation/state-derived-content test;
8. master/meeting projection tests;
9. H01/H02 fishbone immutability/hierarchy tests;
10. Layout Director geometry tests;
11. assembler-plan conformance tests;
12. Professor QA positive/negative tests;
13. Visual QA positive/negative tests;
14. internal Skill routing tests;
15. structural OpenXML audit;
16. exact SVG relationship audit;
17. LibreOffice compatibility render of every slide;
18. full montage + fishbone comparison montage + transition montage;
19. slide-specific visual inspection record;
20. `slides_test.py` / overflow test where available;
21. canonical absolute-path scan;
22. `git diff --check`;
23. remote Git verification.

---

## Private fixture/native status

If the real private exemplars remain unavailable:

`private_fixture_acceptance: blocked_fixture`

This is acceptable. Do not fabricate fidelity results.

If native Microsoft PowerPoint remains unavailable:

- Stage 8 = `blocked_environment`
- Stage 9 = `not_run`
- release = `blocked`

This is acceptable.

---

## Report update

Update:

`thesis-deck-system/reports/PHASE_2_IMPLEMENTATION_REPORT.md`

Add explicit traceability for:

- P2-B1 provenance/Phase1 contract preservation
- P2-B2 causal temporal chronology
- P2-B3 state-derived story/content compilation
- P2-B4 real layout geometry/assembler conformance
- P2-B5 executed Professor QA
- P2-B6 truthful Visual QA
- P2-B7 Skill orchestration
- P2-B8 hierarchical fishbone

For each item include exact files, tests, artifacts, failures, and acceptance status.

The report must explicitly state:

- H01 key cursors: hypothesis/problem/fishbone, experiments/results, discussion/decision/summary, transition;
- H02 key cursors;
- transition slide source cursor;
- result -> discussion causality validation result;
- number of unresolved Slide Spec refs: must be 0;
- number of final over-budget unsplit slides: must be 0 unless an explicit reviewed override artifact exists;
- number of distinct archetype placement signatures in the acceptance deck;
- Professor QA check count and negative-test count;
- Visual QA automated check count and slide-specific inspection count;
- required Skill names and routing-test result;
- fishbone hierarchy validation result.

---

## Delivery

Commit and push to:

`origin/codex/thesis-deck-system`

Verify remote head and key artifacts.

Final response must include:

- repository
- branch
- commit SHA
- pushed
- remote verification
- report path
- files added/modified/deleted
- tests/checks run
- tests passed/failed
- P2-B1–P2-B8 traceability
- key H01/H02/transition cursors
- unresolved scientific refs count
- state-derived content mutation-test status
- distinct archetype geometry count
- Professor QA checks / negative tests
- Visual QA checks / inspection count
- required Skills implemented
- skill-routing test status
- fishbone hierarchy test status
- acceptance PPTX/render/montage paths
- private fixture status
- native PowerPoint status
- known failures
- technical debt
- unresolved questions

Only write:

`READY_FOR_REVIEW: yes`

when all corrected implementation and artifacts are pushed and remotely verified.

Then STOP.

Do not begin Phase 3.
