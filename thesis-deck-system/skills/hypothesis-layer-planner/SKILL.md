# hypothesis-layer-planner

## Purpose
Compile an immutable historical Hypothesis Layer and its transition without collapsing distinct hypotheses.

## Triggers
Use when adding or revising a hypothesis layer, deriving H02 from H01, or preparing a historical layer story.

## Do-not-trigger conditions
Do not use for same-layer cosmetic edits, future transition references at an earlier cursor, or unreviewed mechanism changes.

## Required inputs
Materialized layer, prior layer decision/discussion, fishbone revision, research block graph, and transition record when available.

## Ordered workflow
1. Confirm the exact research question and falsifiable hypothesis.
2. Keep Hypothesis and Problem pages separate.
3. Attach the historical fishbone snapshot and focused branch.
4. Order experiments/results before integrated Discussion and Summary.
5. Add a transition only at a cursor where all cited objects exist.

## Tool / downstream Skill routing
Handoff causal records to `master-deck-ledger`, then geometry to `layout-director`.

## Outputs
Layer projection, logical Slide Specs, transition provenance, and cursor validation evidence.

## Provenance rules
Compile only from `Ledger.load().materialize(cursor)`; never use fixture dictionaries as a parallel content source.

## Professor-specific invariants
H01 history is immutable, H02 derives from H01, and every layer has a fishbone history slide.

## Failure/block conditions
Block on future transition/claim/result, missing derivation, or a merged Hypothesis/Problem page.

## Handoff conditions
Handoff when layer graph, cursor, and story-order checks pass.
