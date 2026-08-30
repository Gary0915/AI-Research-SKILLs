# scientific-figure-router

## Triggers
Use for a ledger-bound scientific visual request.
## Do-not-trigger conditions
Do not use for decoration, raw prose, or unprovenanced requests.
## Required inputs
FigureProductionPlan, materialized state, source cursor, and CP3 style profile.
## Workflow
Validate science bindings; classify visual class; select one specialist; persist route only.
## Allowed downstream Skills/tools
Only the selected specialist director.
## Forbidden actions
Do not render, generate images, invent science, or bypass FigureCritic.
## Output contract
Schema-valid FigureProductionPlan.
## Provenance behavior
Bind source, claim, evidence, block, stage, and cursor refs.
## Failure modes
Unknown class, missing ref, or evidence-role mismatch.
## Blocked states
blocked_missing_provenance or blocked_evidence_boundary.
## Handoff
Selected specialist director, then FigureCritic.
## QA owner
provenance-qa.
