# Phase 1 Revision 3 Review

Verdict: **REVISE**

Phase 2 remains unauthorized.

The implementation at `6ccd13c9d8a7302b04d6c172bd6b6a97902b3b00` resolves the prior layout-identity, D002 selection, notes-source, provenance-chain, and render-inspection defects. The remaining blockers are now concentrated in temporal/revision integrity and contract closure. These must be corrected before the append-only research model can be considered trustworthy.

## P1-D1 — First snapshot leaks future B001 revision

At ledger cursor 1, `block_created` already contains `B001 revision: 2`. Therefore `materialized-first.json` at the first-build cursor also contains B001 revision 2.

However the first Slide Specs and first Deck Manifest bind `B001 revision: 1`.

This means the first presentation claims it was compiled from block revision 1 even though no B001 revision 1 exists in the materialized ledger state at that cursor. This violates the core append-only / layered-history requirement.

Required correction:

- The first history prefix must materialize B001 revision 1.
- A later `block_revised` (or equivalent reconstructable event) must create B001 revision 2 after the first-build cursor.
- Revised Slide Specs / Manifest may then bind B001 revision 2.
- No future block revision may appear in a prior snapshot.

## P1-D2 — B001 revision graph is not closed over the scientific objects it uses

The current final B001 record is revision 2, but its direct references remain stale/incomplete:

- `asset_refs` contains A001 but not A002, although the observation slide is bound to A002.
- `evidence_refs` omits E003 although the result/discussion slide and literature reasoning use E003.
- `decision_refs` contains D001 but not D002 although Discussion v2 resolves D002.
- Claims/stages/actions contain block revision references that are not currently validated against the materialized B001 revision graph.

Required correction:

Define the semantics of a Research Block revision and make each materialized revision self-consistent. At minimum:

- B001 revision 1 must contain all refs needed by the first scientific state.
- B001 revision 2 must contain all refs needed by the revised scientific state, including the revised decision/action/history as defined by the chosen contract semantics.
- Cross-object validation must reject stale or impossible block revision refs.

## P1-D3 — Original explicit-type schema requirement remains incomplete across the 12 contracts

The four schemas strengthened in Revision 3 are much better, but other canonical schemas still contain constraints such as `pattern` or `format` without an explicit string type. For example `research-block.schema.json` currently has fields such as `block_id`, `research_question.question_id`, `created_at`, and `updated_at` where `pattern` / `format` is present without `type: string`.

JSON Schema string-only keywords do not reject non-string instances by themselves. Therefore malformed IDs/dates can still bypass the intended contract.

Required correction:

- Audit **all 12 Phase 1 schemas**, not only the four recently edited schemas.
- Every patterned ID/reference/path/version and every date/date-time field must have an explicit type.
- Nested objects/arrays used in Phase 1 must have their intended item/object types.
- Add negative tests demonstrating that numeric IDs and non-string date fields are rejected.

## P1-D4 — Stage 1 does not yet validate temporal revision bindings

Stage 1 validates schemas, ledger hash/replay, and snapshot equality, but it does not prove that Slide Specs and Deck Manifests bind a block revision that actually exists at their `source_cursor`.

Required correction:

Stage 1 / semantic validation must prove for every generated slide/manifest entry:

- referenced block exists at `source_event_cursor`;
- referenced block revision equals the revision materialized at that cursor (or follows an explicitly documented revision-binding rule);
- referenced Claim/Evidence/Asset/Action/Decision objects are reachable and temporally valid for that cursor;
- a future revision cannot be referenced by an earlier build.

Add negative tests for future-revision leakage and wrong manifest/Slide-Spec block revisions.

## P1-D5 — First Deck Manifest points to the revised QA report

`MASTER-PHASE1-FIRST.manifest.json` identifies the first build but its `qa_report_refs` contains `QA-MASTER-PHASE1-REVISED`. The committed QA report itself identifies `BUILD-MASTER-PHASE1-REVISED` / `MASTER-PHASE1-REVISED`.

A later QA result must not retroactively masquerade as the QA record for an earlier immutable build.

Required correction:

Choose one explicit design:

1. create a distinct first-build QA report and bind the first manifest to it; or
2. allow the first manifest to have no QA ref until a matching QA record exists; or
3. introduce an explicit cross-build audit record type whose scope names both builds.

Whichever design is chosen, semantic validation must reject a manifest QA ref whose `deck_id` / `build_id` scope is incompatible with the manifest.

## P1-D6 — Legacy QA bypass can still synthesize PASS states

`run_pipeline(..., critical_findings=...)` retains a legacy branch that constructs stage statuses directly instead of executing the owning gate checks. This preserves the exact class of bypass that earlier reviews prohibited.

Required correction:

- Remove this bypass, or make non-executed stages explicitly `not_run`/`blocked` rather than `pass`.
- No public/runtime path may manufacture Stage 1–7 PASS without running the owning checks.
- Add a regression test proving the bypass cannot certify an unvalidated deck.

## Non-blocking Phase 2 note

The current SVG bridge targets the last generated slide by filename sorting. It is acceptable for the bounded two-slide Phase 1 fixture, but before multi-block/full-deck expansion it must target the exact slide corresponding to the SVG-bearing Slide Spec rather than assuming the last slide. Also remove path-depth assumptions such as deriving repository root from a fixed template-path parent count before private-template ingestion.

## Acceptance gate for the next submission

Phase 1 may be approved when the corrected artifacts demonstrate:

1. first snapshot = B001 rev1;
2. revised snapshot = B001 rev2 after a real revision event;
3. Slide Specs / Manifests bind the correct block revision at each cursor;
4. B001 revision refs are graph-closed and temporally valid;
5. all 12 schemas reject wrong primitive types for IDs/date fields;
6. first-build QA provenance is not bound to a revised-only QA record;
7. no QA code path can synthesize Stage 1–7 PASS without executing checks;
8. all previous P1-C1–P1-C7 regressions remain green.
