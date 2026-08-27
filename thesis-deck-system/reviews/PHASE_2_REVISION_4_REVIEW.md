# Phase 2 Revision 4 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`830add3f0b1571ad5f0e7d497b85e728514c90d3`

Phase 3 remains blocked.

This revision materially improves presentation fidelity: early H002 slides no longer bind E201, result annotations survive beside SVG assets, RES101/RES102 render differently, governed slot count is 52/52, and the post-render Professor QA consumes presentation-semantic evidence. Those corrections are accepted and must not regress.

However, the reviewer found four remaining architecture blockers that are important for the professor's required **layer-by-layer research history** and for using this system beyond the bounded H001/H002 synthetic fixture.

---

# P2-E1 — Production story projection is still H001/H002-specific and skips middle layers

The reusable scientific objects and Professor QA are becoming generic, but the actual deck story driver is not.

`_story_specs_from_ledger()` currently:

- takes only `ordered[0]` and `ordered[-1]` as `first_layer_id` and `current_layer_id`;
- emits the first layer, a transition from the first layer, and the current layer;
- hard-codes `ST-RES101`, `ST-RES102`, `B101`, `DISC-H001`, `SUM-H001`;
- hard-codes `ST-RES201`, `B201`, `ST-EXP201`, `DISC-H002`, `SUM-H002`.

Therefore an actual H001 → H002 → H003 Master history would not prove that H002 is preserved in the generated story. The existing H003 acceptance is only a Professor-QA fixture; it does not prove the production Story/Slide-Spec/Layout/PPTX projection for three layers.

This violates the professor's central requirement:

`H01 full layer → H02 full layer → H03 full layer → ...`

with every prior discussion, failed experiment, decision and fishbone snapshot retained.

### Required correction

Create a generic N-layer projection driver that iterates every hypothesis layer in temporal order and compiles every layer plus its actual transition(s), without literal H001/H002/B101/B201/ST-RESxxx dependencies in reusable production code.

Add a real 3-layer projection acceptance test proving H001, H002 and H003 all appear in order and the middle layer is not skipped.

---

# P2-E2 — Ledger lifecycle and temporal QA are not yet truly causal/generic

Revision 3 improved slide cursors, but the underlying ledger still constructs substantial H002 work **before** the H001→H002 transition is recorded.

Before the transition event, the build appends H002:

- Observation/Literature/Mechanism/Solution stages;
- Experiment stage;
- pending Result;
- pending Discussion;
- pending Decision;
- Action;
- fishbone asset / block state.

Only later is `E104` appended and `TR-H001-H002` recorded, followed by `hypothesis_layer_created(H002)`.

This means the slide projection hides future successor-layer objects correctly, but the research ledger itself still says much of H002 existed before the transition that is supposed to explain why H002 exists.

For the professor's layer-by-layer record, the successor-layer lifecycle must be causally ordered. A valid pattern is conceptually:

`H001 results/discussion/decision + precursor observation → transition → H002 layer opening → H002 observation/literature/mechanism/strategy → H002 experiment → H002 result → discussion → summary`.

Claims needed to express the new hypothesis may exist immediately before the transition, but successor experiment/result/discussion/decision work must not predate the transition/layer opening unless explicitly modeled as a separate planning object with honest provenance.

There are also two temporal-QA defects:

1. `run_presentation_temporal_snapshot_qa()` still hard-codes result evidence IDs `{E101, E201}` instead of deriving experiment-result evidence generically from stage/evidence origin metadata.
2. `earliest_required_cursor` in the committed artifact is currently the layer creation cursor even for Result and Transition slides. For example the H001 Result rows report earliest cursor 23 and the Transition reports earliest cursor 23, although their required content does not exist at cursor 23. Likewise `latest_allowed_cursor` equals the first result-evidence cursor while the rule says opening pages must **precede** result evidence; the boundary must be strict.

### Required correction

- Reorder or explicitly model successor-layer lifecycle events so Transition precedes successor scientific work.
- Derive result-evidence sets, role dependencies, and stage cursors from canonical refs/events rather than synthetic IDs.
- Compute `earliest_required_cursor` as the maximum cursor of the actual required objects/bindings for that slide.
- For opening Hypothesis/Problem/Fishbone, enforce `source_cursor < first_result_evidence_cursor` when a result boundary exists.
- Compute transition earliest/latest bounds from prior results/discussion/decision/precursor evidence and successor result boundary.
- Add renamed-ID/generic H003 temporal tests so no E101/E201/H001/H002 literal is required by the validator.

---

# P2-E3 — Combined-role presentation contracts are still slot-level, not scientific-field-level

The current combined-role QA is a useful improvement, but `PRESENTATION_ROLE_CONTRACTS` is too coarse for professor acceptance.

Examples:

- Experiment Design requires only non-empty `experiment_matrix` + `decision_rule`.
- Literature/Mechanism requires only non-empty `literature_evidence` + `mechanism_diagram`.
- Integrated Discussion requires only non-empty `supporting_results`, `contradicting_results`, `uncertainty` (plus one aggregate `discussion_synthesis` in the merged case).

A slide could therefore remove `N/replicates`, method, measured outputs, cross-experiment pattern, mechanism assessment, or alternatives while leaving the parent textbox non-empty, and the presentation-content contract could still pass.

The professor requirement is semantic, not merely geometric.

### Required correction

Define field-level audience-visible contracts and validate the fields individually, including at least:

Experiment Design:
- independent variables;
- controlled variables;
- control/baseline;
- sample plan / N / replicates;
- measured outputs + units;
- method/instrumentation;
- prediction;
- decision rule.

Literature / Mechanism / Strategy:
- consensus;
- alternatives/disagreement;
- gap;
- implication;
- mechanism;
- strategy;
- success criterion where applicable.

Integrated Discussion:
- supporting results;
- contradicting/non-discriminating results;
- cross-experiment pattern;
- mechanism assessment;
- alternative explanations;
- remaining uncertainty.

Summary / Decision:
- answered question;
- hypothesis status;
- decision;
- unresolved uncertainty;
- next question;
- next step.

A non-empty aggregate textbox must not be sufficient proof.

Add negative tests that remove one semantic subfield while keeping the parent physical slot present and non-empty.

---

# P2-E4 — Presentation-semantic and report-consistency gates still over-claim

## 1. Presentation-semantic gate

`run_presentation_semantic_fidelity_qa()` returns an `executed_checks` list containing:

- `hypothesis_problem_separation`
- `discussion_after_results`
- `summary_after_discussion`
- `historical_fishbone`

but the function does not actually execute explicit owning checks for all of those claims. It mainly consumes the temporal/combined/physical statuses, validates layout/geometry/notes, checks a role set, and compares only the first two result extracted-text records.

The gate must never claim a check that it did not execute.

Result distinction must also be generic: compare every distinct Result object that requires visible differentiation, not only `results[0]` versus `results[1]`, and use final render evidence when claiming **visible** distinction.

## 2. Report consistency is still incorrect

The implementation report states:

`E104 is the pre-H02 uncertainty/transition precursor (cursor 32)`.

The committed causal-role artifact correctly reports:

`E104 cursor = 52`.

So Revision 3 still contains a stale factual inconsistency.

The committed `report-evidence-consistency.json` also omits several facts explicitly required by the Revision-3 task, including:

- H01 Experiment cursor(s);
- precursor Evidence cursor;
- physical PPTX page count;
- governed required / instantiated / missing slot counts.

Its `status: pass` currently depends primarily on overall QA not failing and transition-cursor equality; it does not prove all report facts are mutually consistent.

### Required correction

- Implement every semantic check that is declared as executed, each with persisted evidence.
- Validate Hypothesis/Problem separation, result-before-discussion ordering, discussion-before-summary ordering, historical fishbone revision/focus, and all required professor stages inside the owning semantic gate.
- Validate visible result distinction across all relevant Result objects using physical text and final render hashes.
- Do not finalize semantic-fidelity PASS before the render-dependent checks exist.
- Generate one canonical `report_facts` object from artifacts and use it to populate/verify the implementation report.
- Include every required cursor/count field from the task.
- Correct E104 from 32 to its actual cursor 52.
- Add a negative test where a stale or omitted report fact causes report-evidence consistency to fail.

---

# Preserve accepted Revision-3 corrections

Do not regress:

- H002 Hypothesis/Problem/Fishbone do not bind E201.
- RES101 and RES102 retain distinct editable annotations and distinct renders.
- asset + annotation composition and SVG ownership.
- 52 governed physical slots currently instantiated.
- combined-role physical slot coverage.
- E104 precursor role and E201 downstream experiment-result role.
- Hypothesis and Problem separation.
- versioned/hierarchical fishbone.
- H003-generic Professor QA behavior.
- persisted-ledger source-of-truth boundary.
- split governance with no synthetic approval.
- private-fixture honesty.
- native PowerPoint blocked-environment honesty.
- no Phase 3 and no global/public Skill registration.

---

# Reviewer approval conditions

Phase 2 can close when all of the following are demonstrated remotely:

1. Production Master/Meeting story projection supports at least H001→H002→H003 without skipping H002 and without literal H001/H002 cursor logic.
2. Successor-layer lifecycle is causally ordered around Transition and Layer opening.
3. Temporal QA derives dependencies generically and reports true earliest/latest cursor bounds.
4. Combined-role contracts validate scientific subfields, not only non-empty aggregate slots.
5. Presentation-semantic QA executes exactly what it claims and uses render evidence for visible-result distinction.
6. Report facts are generated/verified from canonical artifacts; E104 and all required cursor/count facts agree.
7. All previously accepted Phase 1 / Phase 2 tests remain green.
8. Native PowerPoint and private-fixture limitations remain honestly blocked if unavailable.

Until then:

**Phase 2 = REVISE**

**Phase 3 = NOT AUTHORIZED**
