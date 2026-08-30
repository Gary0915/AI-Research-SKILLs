# photo-annotation-director

## Triggers
Use for a real experimental photo, microscopy, or instrument output.
## Do-not-trigger conditions
Do not use for generated imagery or source replacement.
## Required inputs
Immutable source asset, empirical Evidence Card, overlay request, and cursor.
## Workflow
Validate source identity; specify deterministic separate annotation overlay.
## Allowed downstream Skills/tools
figure-critic.
## Forbidden actions
Do not generate or replace empirical pixels.
## Output contract
Source-preserving photo annotation Figure Spec.
## Provenance behavior
Bind asset SHA and Evidence Card.
## Failure modes
Missing immutable source/evidence binding.
## Blocked states
blocked_missing_provenance.
## Handoff
figure-critic.
## QA owner
provenance-qa.
