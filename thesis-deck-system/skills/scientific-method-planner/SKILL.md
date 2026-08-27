# scientific-method-planner

## Purpose
Turn canonical research objects into an ordered Observation → Literature → Mechanism → Strategy → Experiment → Result → Discussion → Decision plan.

## Triggers
Use when planning a new research block, literature synthesis, experiment, or result interpretation.

## Do-not-trigger conditions
Do not use to invent missing measurements, replace a ledger event, or design visual styling without scientific inputs.

## Required inputs
Research question, hypothesis Claim, problem, evidence cards, scientific stages, and decision criteria from the materialized cursor.

## Ordered workflow
1. Validate schema and question/hypothesis/falsifier.
2. Build structured literature synthesis including disagreement and gap.
3. Bind mechanism and strategy to evidence.
4. Validate experiment variables, controls, replicates, metrics, units, methods, predictions, and Go/Partial-Go/No-Go rules.
5. Require results before Discussion and Decision.

## Tool / downstream Skill routing
Handoff the validated plan to `hypothesis-layer-planner`, then `master-deck-ledger`.

## Outputs
Schema-valid stage plan and causal validation findings.

## Provenance rules
Every statement and metric must point to a materialized Claim, Evidence, or Stage; generated context is never scientific evidence.

## Professor-specific invariants
Research question precedes data; literature is synthesis rather than a bibliography; failed results remain visible.

## Failure/block conditions
Block on missing falsifier, controls, metrics, decision rule, or future result reference.

## Handoff conditions
Handoff only when causal stage ordering and evidence provenance pass.
