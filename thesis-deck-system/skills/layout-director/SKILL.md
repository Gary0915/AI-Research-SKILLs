# layout-director

## Purpose
Select governed A01–A18 archetype geometry and bind it to a profiled native template layout.

## Triggers
Use when converting a validated Slide Spec into a placement plan or reviewing layout fit.

## Do-not-trigger conditions
Do not silently fall back to an arbitrary layout, ignore a split recommendation, or design from screenshots.

## Required inputs
Semantic role, stage metadata, asset/evidence counts, text budget, template profile identity, and archetype registry.

## Ordered workflow
1. Resolve semantic role to an archetype.
2. Select stable native layout/master identity from Template Profile.
3. Generate meaningful slots and geometry.
4. Resolve over-budget content with a continuation or reviewed override.
5. Persist plan, signature, and decision evidence for assembly.

## Tool / downstream Skill routing
Handoff plans to the single registered PPTX assembler and then structural/visual QA.

## Outputs
Schema-valid Layout Plan, archetype signature, slot decisions, and split/override record.

## Provenance rules
Geometry may transform presentation but may not change scientific wording or references.

## Professor-specific invariants
Figures lead interpretation; comparison panels are fair; research question is visually prior to deep results.

## Failure/block conditions
Block on identity mismatch, missing required slot, out-of-bounds geometry, unresolved split, or asymmetry.

## Handoff conditions
Handoff only after plan schema validation and conformance tests pass.

## Allowed downstream Skills/tools
PythonPptxAssembler after APPROVED_FIGURE only.
## Forbidden actions
Do not create, repair, or approve scientific figures.
## Output contract
Layout Plan containing only approved figure asset bindings.
## Provenance behavior
Require FigureCritic approval and provenance for every scientific asset.
## Failure modes
Raw spec, unapproved asset, missing provenance, or unresolved split.
## Blocked states
blocked_figure_critic.
## Handoff
PythonPptxAssembler.
## QA owner
provenance-qa.
## Workflow
Execute the declared contract only after its input validation passes.
