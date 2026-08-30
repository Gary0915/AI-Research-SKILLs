# image-matrix-director

## Triggers
Use for ordered multi-panel/image-matrix evidence.
## Do-not-trigger conditions
Do not use for arbitrary collages or generated empirical replacements.
## Required inputs
Panel order, source assets, captions/scales, and cursor.
## Workflow
Validate identity/order/scales; issue a structured matrix spec.
## Allowed downstream Skills/tools
vector-figure-builder and figure-critic.
## Forbidden actions
Do not reorder panels, lose scale, or replace evidence imagery.
## Output contract
Typed image-matrix Figure Spec.
## Provenance behavior
Bind every panel to its source evidence.
## Failure modes
Missing panel, caption, scale, or source.
## Blocked states
blocked_missing_provenance.
## Handoff
vector-figure-builder.
## QA owner
figure-critic.
