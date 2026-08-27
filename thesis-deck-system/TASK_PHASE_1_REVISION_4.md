# Thesis Deck System — Phase 1 Revision 4 Task

## Authorization

Reviewer verdict is `REVISE` in:

`thesis-deck-system/reviews/PHASE_1_REVISION_3_REVIEW.md`

This task authorizes **Phase 1 correction only**. Phase 2, public skill registration, private-template production acceptance, and production Group Meeting use remain unauthorized.

## Required reading

Synchronize `origin/codex/thesis-deck-system`, then read completely:

1. `thesis-deck-system/REVIEW_PROTOCOL.md`
2. `thesis-deck-system/TASK_PHASE_1.md`
3. `thesis-deck-system/TASK_PHASE_1_REVISION.md`
4. `thesis-deck-system/TASK_PHASE_1_REVISION_2.md`
5. `thesis-deck-system/TASK_PHASE_1_REVISION_3.md`
6. `thesis-deck-system/reviews/PHASE_1_REVISION_3_REVIEW.md`
7. `thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`
8. this file

## Mission

Correct remaining blockers `P1-D1` through `P1-D6` without expanding scope.

The goal is temporal truth: an earlier deck must never contain or reference a future research revision, and every immutable deck build must have provenance that resolves to the exact research state and QA scope that existed at its source cursor.

## P1-D1 — Implement real B001 revision history

The first materialized state must contain B001 revision 1, not revision 2.

Required implementation:

- Commit or deterministically construct a canonical B001 revision 1 scientific record.
- `block_created` must create B001 revision 1.
- After the first-build cursor, append a real `block_revised` event that creates/materializes B001 revision 2.
- `Ledger.materialize(until_cursor)` must reconstruct B001 rev1 at the first cursor and rev2 at the revised cursor.
- The revised block event must carry enough normalized content to replay from zero; do not mutate the historical block object in place outside the ledger.

The committed first/revised materializations must prove this transition.

## P1-D2 — Make each Research Block revision graph-closed

Define/document what the direct ref arrays on a Research Block revision mean. Use that meaning consistently.

At minimum validate the refs needed by the current bounded fixture:

- Claim refs
- Evidence refs
- Asset refs
- Action refs
- Decision refs
- Scientific Stage refs

B001 rev1 must resolve the scientific objects used by the first build. B001 rev2 must resolve those used by the revised build.

The observation source A002/E002 and result/literature source E003 may not remain invisible from the relevant block revision graph. Discussion v2's D002 must be reachable from B001 rev2.

If a revised NS001 is considered bound to B001 rev2, update its linked block revision consistently. If the contract intentionally preserves its originating block revision, document that rule and add semantic validation so the distinction is unambiguous.

## P1-D3 — Finish primitive typing across all twelve schemas

Audit all files under:

`thesis-deck-system/schemas/`

for the twelve Phase 1 contracts.

Requirements:

- every field using `pattern` has an explicit compatible `type`;
- every `format: date` / `date-time` field has `type: string`;
- every ID/reference field has explicit string typing;
- nested arrays specify item types;
- nested objects used by the bounded Phase 1 contracts specify object types and required fields where semantically necessary;
- keep Draft 2020-12 + `FormatChecker`.

Do not limit this audit to Slide Spec / Deck Manifest / Asset Manifest / Template Profile.

Add negative tests across multiple schemas, including at minimum:

- numeric B001 `block_id` rejected;
- numeric/invalid research question ID rejected;
- numeric `created_at` rejected;
- numeric Claim / Evidence / Action / Decision ID rejected where applicable;
- non-string date-time value rejected.

## P1-D4 — Add revision-aware temporal semantic validation

Implement a deterministic validator over persisted ledger history/materializations and generated bindings.

For every first/revised Slide Spec and Manifest slide entry:

- resolve `source_cursor`;
- materialize the ledger at that cursor;
- prove the referenced block exists;
- prove the referenced block revision is the valid revision at that cursor;
- prove referenced Claim/Evidence/Asset/Action/Decision IDs used by the slide/manifest are valid according to the block/temporal contract;
- reject references to a later/future revision.

Stage 1 must execute this validator and report check IDs/evidence.

Required negative tests:

- first Slide Spec changed to B001 rev2 must fail if rev2 did not yet exist at first cursor;
- revised Slide Spec changed to wrong block revision must fail;
- manifest block revision mismatch must fail;
- future decision/action binding at an earlier cursor must fail.

## P1-D5 — Correct immutable build ↔ QA provenance

The first Deck Manifest may not reference a revised-only QA report.

Implement an explicit valid design. Preferred bounded Phase 1 design:

- generate `QA-MASTER-PHASE1-FIRST` scoped to `BUILD-MASTER-PHASE1-FIRST` / `MASTER-PHASE1-FIRST`;
- generate `QA-MASTER-PHASE1-REVISED` scoped to the revised build;
- bind each manifest to its matching QA report.

If native PowerPoint is unavailable, both QA reports may be blocked at Stage 8; that does not prevent their earlier gates from being independently recorded.

Add semantic validation:

`manifest.qa_report_refs` must resolve to a QA record whose deck/build scope matches that manifest.

Persist both QA artifacts in reviewable files, or introduce a clearly schema-defined multi-report container if preferred.

## P1-D6 — Remove synthetic QA PASS bypass

The `critical_findings` compatibility branch in `run_pipeline()` may not create Stage 1–7 `pass` statuses without executing their checks.

Required implementation:

- remove the branch, or redesign it so skipped gates are `not_run`/`blocked`;
- all production/runtime PASS values must come from owning gate execution;
- tests that need synthetic findings should inject failures through normal gate inputs or a test-only helper outside the production QA certification path.

Add a test proving that providing a synthetic finding list cannot produce a valid Stage 1–7 certified QA report without normal inputs/check execution.

## Preserve prior accepted corrections

All P1-C1–P1-C7 behavior must remain green, including:

- stable runtime layout index/path/master identity;
- slide → layout → master → semantic role audit;
- revised D002 resolution;
- nested schema contracts;
- complete A001 provenance-chain verification;
- ledger-derived meeting projection;
- Slide-Spec-derived PowerPoint notes;
- visual evidence checks;
- true source-template immutability evidence;
- actual result-slide SVG relationship.

## Non-blocking future hardening

Do not expand scope, but record as Phase 2 technical debt:

- SVG bridge must eventually target the exact SVG-bearing generated slide instead of relying on `sorted(slide*.xml)[-1]`;
- repository-root resolution must not depend on fixed template path depth when private templates are introduced.

## Required clean artifacts

Regenerate from a clean Phase 1 artifact directory:

- ledger stream with B001 rev1 → rev2 history;
- materialized-first and materialized-revised;
- first/revised Slide Specs;
- first/revised Deck Manifests;
- first/revised QA report artifacts;
- meeting delta;
- canonical/revised PPTX artifacts;
- structural audit;
- render/montage/visual inspection evidence;
- implementation report.

## Required tests/evidence

Before submission:

1. full pytest suite;
2. clean end-to-end rebuild;
3. verify first materialization B001 rev1 and revised materialization B001 rev2;
4. verify a real `block_revised` event occurs after first cursor;
5. exact schema validation for all schema-backed committed/generated objects;
6. primitive-type negative tests across all twelve schemas;
7. temporal binding positive/negative tests;
8. per-build QA-scope binding validation;
9. no synthetic PASS bypass regression;
10. provenance/hash validation;
11. structural PPTX audit;
12. render/montage/inspection validation;
13. canonical absolute-path scan;
14. `git diff --check`;
15. remote verification.

## Report update

Update:

`thesis-deck-system/reports/PHASE_1_IMPLEMENTATION_REPORT.md`

Add explicit `P1-D1`–`P1-D6` traceability with exact files, tests, cursors, revision IDs, and QA report IDs.

The report must explicitly state:

- first cursor and B001 revision at that cursor;
- revised cursor and B001 revision at that cursor;
- cursor of the B001 `block_revised` event;
- first/revised QA report IDs and build/deck IDs;
- result of a full 12-schema primitive typing audit;
- result of temporal binding validation.

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
- P1-D1–P1-D6 traceability
- first cursor / B001 revision
- block_revised cursor
- revised cursor / B001 revision
- first/revised QA IDs and scope
- 12-schema typing audit summary
- temporal-binding validation summary
- PPTX/structural/render artifact paths
- native PowerPoint status
- known failures
- unresolved questions

Only then write:

`READY_FOR_REVIEW: yes`

and STOP. Do not begin Phase 2.
