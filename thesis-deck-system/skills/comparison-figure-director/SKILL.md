# comparison-figure-director

## Triggers
Use for Control/Proposed or other fair comparison.
## Do-not-trigger conditions
Do not use for a single result without paired panels.
## Required inputs
Panel bindings, source refs, scales, metrics, and cursor.
## Workflow
Validate panel pairing and fair scale; issue a comparison spec.
## Allowed downstream Skills/tools
vector-figure-builder and figure-critic.
## Forbidden actions
Do not swap sides, alter scale, or hide uncertainty.
## Output contract
Typed comparison Figure Spec.
## Provenance behavior
Bind each panel to its evidence.
## Failure modes
Missing panel/scale binding.
## Blocked states
blocked_missing_provenance.
## Handoff
vector-figure-builder.
## QA owner
figure-critic.
