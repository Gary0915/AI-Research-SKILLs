# scientific-plot-director

## Triggers
Use for a quantitative measured result.
## Do-not-trigger conditions
Do not use for conceptual, literature, or raster-only requests.
## Required inputs
Canonical data/evidence refs, units, replicates, metric, and cursor.
## Workflow
Validate reproducible data provenance; specify future vector-capable plot.
## Allowed downstream Skills/tools
figure-critic.
## Forbidden actions
Do not use AI generation, omit units, or make PNG the canonical scientific output.
## Output contract
Typed scientific-plot Figure Spec.
## Provenance behavior
Bind data/evidence and source cursor.
## Failure modes
Missing data, units, or evidence.
## Blocked states
blocked_missing_provenance.
## Handoff
figure-critic.
## QA owner
provenance-qa.
