# provenance-qa

## Triggers
Use for a FigureProductionPlan, Figure Spec, future output manifest, or critic request.
## Do-not-trigger conditions
Do not use to create an asset or infer a source.
## Required inputs
Source, claim, evidence, asset, stage, block, and cursor bindings.
## Workflow
Resolve every declared identity against canonical materialized state; reject dangling or role-mismatched refs.
## Allowed downstream Skills/tools
figure-critic and release QA.
## Forbidden actions
Do not fabricate provenance, evidence, citations, or hashes.
## Output contract
Provenance report with resolved/broken chain results.
## Provenance behavior
Preserve evidence role and source cursor throughout the handoff graph.
## Failure modes
Dangling ref, generated-as-evidence, future cursor, or missing source.
## Blocked states
blocked_missing_provenance.
## Handoff
figure-critic.
## QA owner
provenance-qa.
