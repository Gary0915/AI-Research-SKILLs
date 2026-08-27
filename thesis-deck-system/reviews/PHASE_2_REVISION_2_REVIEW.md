# Phase 2 Revision 2 Reviewer Verdict

## Verdict

**REVISE**

Reviewed implementation commit: `1eaddc807de902df6d79263fcf84878f7882c7c9`

Phase 3 remains blocked. Public/global Skill registration remains blocked. Production Group Meeting readiness remains blocked.

## What is now accepted

The previous P2-B1–P2-B8 correction materially improved the system and the following pieces are accepted as directionally correct:

- H01 first materialization no longer sees a future transition.
- persisted causal ordering now places experiment/result before Discussion/Decision/Summary;
- B101/B201 are materialized as canonical graph boundaries and Slide/Manifest unresolved-ref count is zero;
- Slide prose has a state-derived compiler path backed by persisted ledger materialization;
- Hypothesis and Problem remain separate;
- H01 and H02 retain distinct historical fishbone revisions;
- fishbone `parent_ref` now affects connector geometry;
- A01–A18 have distinct governed geometry definitions;
- seven required repo-local orchestration Skills and a routing map now exist;
- private fixture and native PowerPoint limitations are still reported honestly.

These corrections must be preserved.

## Remaining blockers

### P2-C1 — Transition provenance still leaks the H02 discriminating experiment data backward

`E201` is constructed from `phase2/contact-pressure.csv`. That CSV contains the pressure/CV/contact-resistance measurements later used as H02's discriminating experiment/result evidence. However `TR-H001-H002` also uses `E201` as its `observation_or_uncertainty_refs` before `ST-EXP201` and `ST-RES201` are appended.

This passes the current cursor validator only because the Evidence Card is appended earlier than the Experiment/Result stages. Scientifically, it still gives the H01→H02 transition access to the data that H02 is supposed to generate.

Required correction:

- separate **precursor observation/uncertainty evidence** from **H02 experimental result evidence**;
- the transition may reference only evidence that genuinely exists before H02 experiment execution;
- H02 result evidence must be downstream of the H02 experiment declaration/execution boundary;
- add a negative test that rejects reusing a downstream discriminating-result evidence object as transition precursor evidence merely by appending the Evidence Card early;
- causal QA must validate evidence role/origin, not cursor order alone.

### P2-C2 — Layout Plans declare multi-slot archetypes, but the PPTX does not instantiate all governed slots

The new `ROLE_GEOMETRY` is useful, but the assembler still creates one generic body textbox for most roles and only materializes extra boxes when an asset placement exists.

Examples:

- `problem_definition` declares `previous_finding`, `unresolved_conflict`, and `research_question`, but the assembler places the entire body in only `research_question`;
- `progress_todo` declares `commitment_table`, `current_position`, and `parallel_work`, but the assembler places the entire body in only `commitment_table`;
- `layer_integrated_discussion` declares three distinct regions but generic assembly uses only one body slot;
- `layer_summary_decision` and `hypothesis_transition` have the same problem.

The structural audit currently checks only a reduced `expected_slots` list (`body_slot + asset slots`), so `governed_geometry_match: true` can be reported even when required plan slots have no corresponding shape.

Required correction:

- every required Layout Plan slot must be instantiated by an actual PPTX shape or explicitly marked `intentionally_empty` with a justified contract rule;
- Slide Spec content must become structured slot content rather than a single newline-delimited `content.body` for multi-panel archetypes;
- the assembler must map structured content to the corresponding governed slot;
- structural audit must compare **all required plan slots** against actual generated shapes, not a reduced subset;
- tag generated shapes with stable slot identity so the audit proves slot→shape conformance;
- add negative tests where a three-slot plan with only one physical shape fails structural QA.

### P2-C3 — Over-budget layout overrides are automatically self-approved

When `LayoutDirector` recommends a split, the build automatically writes a `reviewed_split_override`, changes `split_recommendation` to false, and labels it as approved by `Phase 2 synthetic acceptance review`. The justification is the same boilerplate for every override and cites `visual-inspection.json` before render/inspection exists.

This is a certification bypass, not a real resolution.

Required correction:

Choose one of these governed outcomes:

1. split the slide; or
2. perform a measurable automated fit/legibility proof and persist it as an **automated fit exception**, not a human/reviewer approval; or
3. require an explicit external reviewer/user approval artifact.

The build itself may not fabricate reviewer approval.

No override may cite evidence that has not yet been generated.

Add negative tests proving that an unresolved split or synthetic/self-approved review cannot pass Stage 7.

### P2-C4 — Visual inspection is still inferred from Slide Specs, not actual rendered pixels

`run_visual_qa_v2()` performs some real raster checks (existence, dimensions, variance), but the persisted per-slide observations such as `dominant_visual`, `question_visibility`, `comparison_balance`, and `density` are generated from semantic role and Slide Spec metadata rather than from the rendered image.

Therefore `18 slide-specific inspections` does not yet prove actual visual inspection of the 18 renders.

Required correction:

- separate **automated geometric/spec QA** from **render-pixel QA** and **visual review**;
- link every inspection to the exact render SHA-256;
- pixel-derived checks should operate on the rendered image where technically measurable (nonblank regions, approximate occupied regions, clipping to canvas, figure/text balance proxies, contrast/readability proxies, etc.);
- qualitative claims such as 'current fishbone focus is obvious' or 'comparison is visually balanced' must come from an actual image-capable inspection step; if unavailable, mark that check `blocked_visual_review` rather than auto-pass;
- persisted observations must describe the actual rendered slide, not restate role metadata;
- add tests proving that changing the rendered image while keeping the same Slide Spec changes/fails visual evidence.

### P2-C5 — Professor QA is hard-coded to H001/H002 and TR-H001-H002

`run_professor_qa_v2()` contains fixture-specific logic:

- transition provenance is checked only when `layer_id == "H001"`;
- it fetches the literal transition ID `TR-H001-H002`;
- history reachability accepts only `{H001, H002}`.

The professor's required architecture is H01 → H02 → H03 → ... and cannot stop at two layers.

Required correction:

- production QA must discover predecessor/successor relations and transitions from the materialized state/projection;
- no production professor/history validator may hard-code H001/H002 or a literal transition ID;
- add a synthetic H003 fixture/test proving H002→H003 transition validation, fishbone revision history, history reachability, and summary/decision checks work generically;
- fixture-specific IDs may remain only inside acceptance-fixture setup/tests, not reusable production validators.

### P2-C6 — Downstream Layout Director inputs still read the seed fixture after the ledger exists

Scientific prose is now rebuilt from persisted state, but Phase 2 layout planning still obtains `plan_layer` from `fixture["hypothesis_layers"]` to derive experiment/result counts.

This leaves a second source of truth in the post-ledger pipeline. The current fixture-mutation regression explicitly excludes `layout_plan_ref` and `placement_plan`, so it does not prove layout decisions are state-derived.

Required correction:

- after ledger persistence, all story, projection, layout, manifest, PPTX, and QA inputs must come from cursor materialization/projection only;
- the seed fixture may be used only to seed canonical ledger events;
- extend mutation tests so mutating the source fixture after ledger persistence cannot alter Slide Specs **or Layout Plans / Layout Director decisions** rebuilt from the persisted ledger;
- document the exact boundary after which fixture reads are forbidden.

## Acceptance conditions for the next review

The next submission must demonstrate all P2-C1–P2-C6 items with positive and negative tests, regenerated acceptance artifacts, and explicit report traceability.

The reviewer will specifically inspect:

1. transition precursor evidence is genuinely pre-H02 and not the later H02 result dataset;
2. Problem/Progress/Discussion/Summary/Transition slides physically instantiate all governed slots;
3. structural audit fails if a required physical slot is missing;
4. no automatically fabricated `approved_by` review overrides exist;
5. qualitative visual claims are backed by actual render inspection or honestly blocked;
6. Professor QA passes an H003 generic-history fixture without H001/H002 hard-coding;
7. layout decisions can be rebuilt from persisted ledger state after the seed fixture is mutated.

## Phase status

Phase 2 remains **open / revise**.

Do not begin Phase 3.
