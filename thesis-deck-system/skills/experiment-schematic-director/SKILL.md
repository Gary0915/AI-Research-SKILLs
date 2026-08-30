# experiment-schematic-director

## Triggers
Use for experimental setup, sample stack, or measurement path.
## Do-not-trigger conditions
Do not use for fabrication chronology or photo replacement.
## Required inputs
Stage metadata, variables, controls, instrumentation, inputs, outputs, and cursor.
## Workflow
Validate method fields; preserve measurement points; issue a vector/native-plan request.
## Allowed downstream Skills/tools
vector-figure-builder and figure-critic.
## Forbidden actions
Do not omit controls, invent conditions, or absorb fabrication.
## Output contract
Typed experiment-schematic Figure Spec.
## Provenance behavior
Bind Stage and method references.
## Failure modes
Missing control, variable, method, or instrument.
## Blocked states
blocked_missing_provenance.
## Handoff
vector-figure-builder.
## QA owner
figure-critic.
