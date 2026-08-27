# fishbone-director

## Purpose
Render stable, hierarchical, revision-aware fishbone research maps.

## Triggers
Use for creating or revising a research fishbone, selecting current focus branches, or auditing map history.

## Do-not-trigger conditions
Do not flatten parent branches, renumber stable IDs, mutate historical SVGs, or use generated imagery as evidence.

## Required inputs
Schema-valid fishbone revision, stable branch IDs, parent refs, status, focus refs, and historical cursor.

## Ordered workflow
1. Validate duplicate IDs, orphan parents, and cycles.
2. Preserve root positions and place children relative to declared parents.
3. Mark the current focus with prominent metadata.
4. Render SVG plus preview and compare revisions.
5. Verify older revision bytes remain unchanged after growth.

## Tool / downstream Skill routing
Handoff SVG assets and hierarchy evidence to `layout-director` and `professor-qa`.

## Outputs
Editable hierarchical SVG, preview, position metadata, and validation report.

## Provenance rules
Each map is bound to its ledger revision and source event cursor; it is not a screenshot recreation.

## Professor-specific invariants
Every layer shows its historical fishbone and current focus; completed, partial, failed, and future branches remain visible.

## Failure/block conditions
Block on cycle, orphan, duplicate, unknown focus, overflow, or historical hash change.

## Handoff conditions
Handoff when hierarchy and stability checks pass.
