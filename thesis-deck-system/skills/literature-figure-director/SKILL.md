# literature-figure-director

## Triggers
Use for a cited literature figure.
## Do-not-trigger conditions
Do not use for AI recreation or uncited mechanism art.
## Required inputs
Literature source, citation/provenance, extracted asset identity, and cursor.
## Workflow
Validate extraction/citation; specify optional deterministic overlay.
## Allowed downstream Skills/tools
figure-critic.
## Forbidden actions
Do not recreate the literature figure with AI.
## Output contract
Source-extraction Figure Spec.
## Provenance behavior
Preserve citation and extracted-source identity.
## Failure modes
Missing citation, source, or extraction rights.
## Blocked states
blocked_missing_provenance.
## Handoff
figure-critic.
## QA owner
provenance-qa.
