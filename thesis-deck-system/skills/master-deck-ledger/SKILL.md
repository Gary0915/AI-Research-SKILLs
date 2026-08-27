# master-deck-ledger

## Purpose
Maintain the append-only ledger and materialized Master/Meeting projections used by every deck build.

## Triggers
Use for committing research events, replaying history, building Master Decks, or compiling meeting deltas.

## Do-not-trigger conditions
Do not mutate canonical objects in place, rewrite history, or store slide prose outside the ledger projection.

## Required inputs
Schema-valid event payload, previous ledger hash, source cursor, project profile, and projection request.

## Ordered workflow
1. Append through `Ledger.append()`.
2. Serialize hashes and reload with `Ledger.load()`.
3. Replay/materialize from zero at requested cursors.
4. Validate graph reachability and revision compatibility.
5. Produce Master and Meeting projections before slide compilation.

## Tool / downstream Skill routing
Handoff layer projections to `hypothesis-layer-planner`; send slide plans to `layout-director` and QA to `professor-qa`.

## Outputs
Persisted ledger, cursor materializations, projections, and replay evidence.

## Provenance rules
The ledger is the sole scientific source of truth; generated PPTX/PDF/renders are derived artifacts.

## Professor-specific invariants
Carry prior commitments, owners, timing, blockers, dependencies, parallel work, and status into Meeting projection.

## Failure/block conditions
Block on hash mismatch, cursor leakage, dangling references, or lost commitments.

## Handoff conditions
Handoff only after reload/replay and per-slide cursor bindings pass.
