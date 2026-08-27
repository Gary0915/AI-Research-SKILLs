# thesis-deck-router

## Purpose
Route a user request to the smallest complete Thesis Deck workflow while preserving one scientific source of truth.

## Triggers
Use for Group Meeting updates, new hypotheses, experiment-result pages, fishbone updates, literature/mechanism pages, Master Deck updates, or deck review.

## Do-not-trigger conditions
Do not use for unrelated writing, arbitrary slide decoration, or public Skill registration.

## Required inputs
Request text, project routing map, current ledger cursor, project professor profile, and available source assets.

## Ordered workflow
1. Resolve the deterministic route from `skill-routing.yaml`.
2. Verify the required cursor and source-object inputs.
3. Handoff to the listed planner/ledger/layout/QA Skills in order.
4. Stop on unresolved provenance, schema, or QA blockers.

## Tool / downstream Skill routing
Use `scientific-method-planner`, `hypothesis-layer-planner`, `master-deck-ledger`, `fishbone-director`, `layout-director`, and `professor-qa` as routed by the map.

## Outputs
Route decision, ordered handoff list, source cursor, and blocking findings.

## Provenance rules
Never create scientific prose or references in the router; all content must resolve from persisted ledger materialization.

## Professor-specific invariants
Preserve Traditional Chinese, separate Hypothesis and Problem, preserve history, and require professor-profile QA.

## Failure/block conditions
Block on ambiguous route, missing ledger cursor, dangling references, or unavailable required fixture.

## Handoff conditions
Handoff only after route and input contract validation; return final QA/release status to the requester.
