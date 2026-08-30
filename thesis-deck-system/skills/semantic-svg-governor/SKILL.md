# semantic-svg-governor

## Triggers
Use to govern local visual semantic metadata, semantic-role registry membership, stable visual-object identity, and metadata invisibility for canonical Scientific SVG.

## Do-not-trigger conditions
Do not use to manage Ledger state, Claims, Evidence, hypothesis logic, source cursors, scientific provenance, professor visual grammar, layout, or PPTX.

## Required inputs
Approved Scientific SVG profile, versioned semantic role registry, canonical SVG, and static validator.

## Workflow
1. Verify only minimal root/object semantic attributes are present.
2. Verify every addressable local object has a stable unique ID and registered local role.
3. Strip approved metadata and compare the static presentation AST.
4. Reject scientific provenance-like attributes and any unknown metadata.
5. Emit execution-owned static governance findings.

## Allowed downstream Skills/tools
scientific-svg-authoring validation handoff and future CP5-C manifest construction only after authorization.

## Forbidden actions
Do not store or infer Ledger, Claim, Evidence, Decision, Action, source hash, research block, stage, or hypothesis provenance. Do not treat semantic attributes as rendering controls.

## Output contract
Static SVG QA report and metadata-invisibility evidence.

## Provenance behavior
Semantic roles are local visual semantics only. Canonical scientific provenance stays in ScientificFigureSpec and future FigureOutputManifest.

## Failure modes
Unknown role, incompatible element/role pair, duplicate/mutable ID, forbidden provenance metadata, or presentation AST change after stripping metadata.

## Blocked states
blocked_semantic_svg_governance.

## Handoff
Return only validated SVG language evidence; no FigureCritic, Layout, renderer, or PPTX handoff in CP5-A.

## QA owner
semantic-svg-governor.
