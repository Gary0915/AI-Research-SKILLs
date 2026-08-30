# mechanism-diagram-director

## Triggers
Use for a causal mechanism or interface explanation.
## Do-not-trigger conditions
Do not use for fabrication chronology, measurement setup, or evidence figures.
## Required inputs
Mechanism Figure Spec, claim refs, uncertainty, alternatives, and governed style.
## Workflow
Validate causal nodes/edges; retain unknowns; issue a deterministic vector-spec request.
## Allowed downstream Skills/tools
vector-figure-builder and figure-critic.
## Forbidden actions
Do not absorb fabrication, replace experiment evidence, or infer certainty.
## Output contract
Typed mechanism Figure Spec.
## Provenance behavior
Preserve claim/evidence references and cursor.
## Failure modes
Missing causal or uncertainty binding.
## Blocked states
blocked_missing_provenance.
## Handoff
vector-figure-builder.
## QA owner
figure-critic.
