# fabrication-process-director

## Triggers
Use for material preparation, mixing, degassing, molding, curing, washing, coating, electrode integration, or assembly chronology.
## Do-not-trigger conditions
Do not use for causal mechanisms or measurement apparatus.
## Required inputs
Ordered process steps, material/state refs, known conditions, and provenance.
## Workflow
Validate ordinal order; preserve state transitions and UNKNOWN conditions; select conservative vector route.
## Allowed downstream Skills/tools
vector-figure-builder and figure-critic.
## Forbidden actions
Do not invent temperature, time, conditions, materials, or replace process with a mechanism/schematic.
## Output contract
Typed fabrication-process Figure Spec.
## Provenance behavior
Bind every step to source and process references.
## Failure modes
Missing order, material, state, or provenance.
## Blocked states
blocked_missing_provenance.
## Handoff
vector-figure-builder.
## QA owner
provenance-qa.
