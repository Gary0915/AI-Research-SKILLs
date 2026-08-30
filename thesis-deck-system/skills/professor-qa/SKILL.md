# professor-qa

## Purpose
Execute project-specific professor rubric checks against the actual ledger-derived meeting projection and rendered deck.

## Triggers
Use for deck review, release gating, professor-style logic, and acceptance evidence.

## Do-not-trigger conditions
Do not claim checks that were not executed, use generic academic style in place of the project profile, or approve unresolved critical findings.

## Required inputs
Versioned professor profile, materialized state, Meeting projection, Slide Specs, Layout Plans, structural audit, and render inspection record.

## Ordered workflow
1. Load and validate the persisted professor profile.
2. Execute each rule with inspectable evidence.
3. Check scientific order, provenance, hypothesis history, commitments, and geometry.
4. Persist positive/negative findings and check IDs.
5. Block release on any unresolved critical finding.

## Tool / downstream Skill routing
Consume outputs from `master-deck-ledger` and `layout-director`; route visual evidence to render QA.

## Outputs
Versioned QA report, executed check list, evidence paths, findings, and release decision.

## Provenance rules
Every QA claim points to a projection, Slide Spec, ledger cursor, or persisted inspection record.

## Professor-specific invariants
Hypothesis/Problem separation, structured literature, result-before-discussion, historical fishbone, and prior-commitment continuity.

## Failure/block conditions
Block on missing profile, unexecuted check, failed falsifier, future reference, lost history, or unresolved critical finding.

## Handoff conditions
Handoff to release only when all required checks execute and pass; otherwise return actionable blockers.

## Allowed downstream Skills/tools
Release gates only after owning checks pass.
## Forbidden actions
Do not certify qualitative review, figures, or private fidelity without their owning evidence.
## Output contract
Hash-bound professor QA report.
## Provenance behavior
Reference materialized state, Slide Specs, and persisted inspection records.
## Failure modes
Missing profile, unexecuted check, or open critical finding.
## Blocked states
blocked_missing_provenance.
## Handoff
Release gate.
## QA owner
professor-qa.
## Workflow
Execute the declared contract only after its input validation passes.
