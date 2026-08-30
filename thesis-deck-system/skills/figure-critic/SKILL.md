# figure-critic

## Triggers
Use after a future output manifest exists.
## Do-not-trigger conditions
Do not use on a raw Figure Spec or incomplete asset.
## Required inputs
Output manifest, spec, provenance, and executed QA evidence.
## Workflow
Audit provenance and figure correctness; approve, fail, or block.
## Allowed downstream Skills/tools
layout-director only after APPROVED_FIGURE.
## Forbidden actions
Do not generate figures or self-approve missing evidence.
## Output contract
FigureCriticReport with APPROVED_FIGURE, FAIL, or BLOCKED.
## Provenance behavior
Bind every decision to output/spec hashes.
## Failure modes
Missing provenance or failed figure QA.
## Blocked states
blocked_figure_critic.
## Handoff
layout-director only for APPROVED_FIGURE.
## QA owner
figure-critic.
