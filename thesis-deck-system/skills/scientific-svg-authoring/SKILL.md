# scientific-svg-authoring

## Triggers
Use only to author or validate a CP5-A canonical Scientific SVG from a schema-valid ScientificFigureSpec.

## Do-not-trigger conditions
Do not use for scientific truth, figure routing, professor-style selection, layout, PPTX assembly, private fixtures, or production figure rendering before the authorized director checkpoint.

## Required inputs
Scientific SVG profile ID/version, semantic role registry ID/version, a schema-valid Figure Spec, controlled synthetic or approved future director geometry, and the static validator.

## Workflow
1. Create only allowed SVG elements and element-specific attributes.
2. Keep editable Unicode text in `text`/`tspan` and assign stable object IDs.
3. Attach only rendering-neutral local semantic metadata.
4. Canonicalize without reordering children.
5. Hand off to the CP5-A static validator; block on any finding.

## Allowed downstream Skills/tools
semantic-svg-governor and the static SVG validator; a future FigureOutputManifest only after CP5-C authorization.

## Forbidden actions
Do not encode Ledger, Claim, Evidence, cursor, Decision, Action, or source provenance in SVG. Do not use remote/local/private resources, script, HTML, CSS, raster fallback, or a PPTX backend.

## Output contract
Canonical Scientific SVG plus Scientific SVG identity/hash record and static SVG QA report.

## Provenance behavior
Figure identity is bound to the supplied ScientificFigureSpec externally. SVG metadata is never scientific provenance.

## Failure modes
Unknown element/attribute/role, invalid geometry/resource/reference, noncanonical text/order, invalid Figure Spec binding, or validator bypass.

## Blocked states
blocked_static_svg_contract.

## Handoff
Static validation only in CP5-A; no FigureCritic approval or Layout handoff exists yet.

## QA owner
semantic-svg-governor.
