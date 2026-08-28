# Phase 3 Checkpoint 2 Revision 2 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`7be3c1a6023f6e992b7451b459d77a0f584a587c`

Checkpoint 2 remains the active checkpoint. Do not begin Professor Visual Grammar resolution, VisualStyleGovernor calibration, A01–A18 calibration, Figure Skill production, template reconstruction, reconstruction benchmarking, acceptance-deck generation, Phase 4, or public/global Skill registration.

## What is accepted

The previous CP2-B corrections materially improved the implementation:

- shell/body descriptors are recursively typed and sanitizer reconstruction is substantially fail-closed;
- stable aliases, private-source access boundaries, legacy-exception handling, and production Observation policy remain intact;
- source sessions now have structured lifecycle fields and failed sessions can be represented;
- provider capability alone no longer fabricates a private render/review lifecycle;
- the production run retained zero private renders and kept private qualitative review blocked;
- the profiler now emits substantially richer object, connector, group, topology, typography, style, and region data than the prior revision.

However, the descriptors are still **not resolver-ready**. Several values currently labeled as shell/figure measurements are either sourced from the wrong OOXML layer, geometrically incorrect for grouped objects, or placeholder-derived rather than actually measured. The current descriptor-quality gate does not detect these problems.

## CP2-C1 — Shell evidence must come from the shell, not arbitrary slide content

The current shell pipeline measures `shell_regions`, `safe_content_bounds`, typography/style roles, and `shell_primitives` mainly from ordinary slide shapes. This contaminates shell evidence with body content.

Concrete evidence in the committed descriptor includes:

- `safe_content_bounds` for `private://template_primary_1` equal to the entire slide (`x=0, y=0, w=1, h=1`), which is not a useful professor-derived safe content region;
- shell primitives with recurrence count `1`, including pictures and connectors located in body-content regions;
- title/header/footer recurrence counts greater than slide count, showing that the current positional heuristic is collecting multiple slide-body objects rather than identifying stable shell objects.

The resolver must not learn body figures as Master/shell grammar.

Required correction:

1. Profile native slideMaster / slideLayout structure directly for shell evidence.
2. Parse and sanitize placeholder roles/types and their geometry where available.
3. Parse Master/Layout recurring shape geometry, typography, fills/strokes, and theme relationships.
4. Treat ordinary slide-level geometry only as secondary corroborating evidence, not as primary shell authority.
5. Add `source_scope` / equivalent provenance to every shell measurement, such as:
   - `slide_master`
   - `slide_layout`
   - `theme`
   - `slide_recurrence_derived`
   - `not_observable_structurally`
6. Safe content bounds must be derived from actual shell exclusions / layout content regions when evidence exists. If not defensible, mark them `not_observable_structurally`; do not return the full slide or another fallback and call it professor-derived.
7. A shell primitive should not be called recurring shell grammar merely because it appeared once on a slide.

Add negative tests proving that a unique body picture/connector on one slide cannot enter recurring shell primitives.

## CP2-C2 — Grouped-shape geometry and connector direction are not yet reliable

The current recursive group traversal reads child `a:xfrm` offsets/extents directly against slide width/height. In PowerPoint grouped shapes, child coordinates are relative to the group child coordinate system (`chOff` / `chExt`) and require the parent group transform to be applied.

Therefore grouped schematic geometry can currently be wrong even though it is labeled `basis=measured`.

The connector record also derives `start=[x,y]` and `end=[x+w,y+h]` without applying group transforms or flip semantics. `flipH`/`flipV`, head/tail arrowhead identity, and actual arrow direction are not represented. This is not sufficient for later professor arrow-grammar calibration.

Required correction:

- implement nested group transform composition to absolute normalized slide coordinates;
- support nested groups;
- preserve group membership and absolute geometry separately;
- account for `flipH` / `flipV` where applicable;
- record connector endpoint semantics and arrowhead direction/type in a sanitized controlled contract;
- distinguish a plain line from a directed arrow based on actual line-end properties;
- add synthetic PPTX tests with grouped shapes, nested groups, flipped connectors, and head/tail arrowheads.

A round-trip geometry test must prove the absolute coordinates are correct within an explicit tolerance.

## CP2-C3 — Several body metrics are still placeholders, not measurements

The current `_slide_profile` initializes or emits values such as:

- `panels = []`;
- `comparison_symmetry = 0.0`;
- `matrix_rows = 0`;
- `matrix_columns = 0`;
- `caption_candidate_count = 0`;
- `photo_schematic_relation = unknown`.

These are then committed as `basis=derived`, even when no derivation actually occurred.

The report states that panel/matrix/comparison metrics were recorded per slide, but recording a default zero is not measurement.

The family classifier also overclaims semantic confidence. Examples of overly weak rules include:

- `pictures >= 4` => `image_matrix`;
- `pictures >= 2` => `control_proposed_comparison`;
- `connectors >= 3` => `fishbone_research_map`.

Those structural signatures are insufficient to establish those semantic families.

Required correction:

1. Introduce typed metric observations with an explicit state such as:
   - `measured`
   - `derived`
   - `not_observable_structurally`
   - `insufficient_evidence`
2. Do not encode unknown/unmeasured values as numeric zero.
3. Implement real structural derivations where feasible:
   - panel clustering from repeated picture/shape geometry;
   - row/column matrix candidates;
   - normalized left/right comparison symmetry;
   - caption-region candidates based on proximity/geometry only, without text extraction;
   - photo/schematic spatial relationship based on picture vs vector/group regions;
   - dominant-region and gutter metrics using union/cluster geometry rather than naive summed areas where overlap materially matters.
4. Candidate-family classification must require a family-specific structural signature and persist the supporting feature IDs/metrics.
5. If a family cannot be established structurally, emit `provisional` or `insufficient_structural_evidence`; do not force a semantic label.
6. A Fishbone must not be inferred from connector count alone.

Add negative tests for multi-photo non-comparison slides, ordinary flowcharts with multiple connectors, and four unrelated pictures that are not a matrix.

## CP2-C4 — Descriptor-quality QA still contains self-certification and weak completeness checks

`CP2-DQ-PROHIBITED-FIELDS` is currently appended as literal `pass`. The shell/body completeness checks largely verify that fields exist, not that the fields are valid resolver-ready measurements.

This allows Checkpoint 2 aggregate PASS even when shell evidence is contaminated or body metrics are placeholder zeros.

Required correction:

- derive every descriptor-quality status from an owning executable check;
- scan the actual sanitized payload for prohibited field/value classes and persist the result;
- verify shell measurements have valid `source_scope` and do not contain unique slide-body objects as recurring shell evidence;
- verify derived metrics have derivation evidence and are not placeholder values;
- verify family confidence is consistent with its evidence signature;
- verify grouped-object absolute geometry consistency;
- verify source session lifecycle and sanitizer outcome consistency;
- do not close a source session as `success` until sanitizer handoff for that alias has passed; sanitizer failure must close that session as failed.

The final aggregate gate must consume these owning checks.

## CP2-C5 — Theme/style observability must distinguish unknown from absent

The current color/style extraction primarily recognizes direct `srgbClr` values. PowerPoint commonly uses `schemeClr`/theme colors. Returning `none` when a theme-backed color exists conflates "no fill/stroke" with "profiler did not resolve this color source".

Before a Professor Visual Grammar resolver consumes these records:

- profile theme relationships and controlled theme-color roles where structurally available;
- distinguish `none`, `unknown`, `theme_role`, and resolved sanitized color role;
- do not label unparsed theme-backed values as `none`;
- record basis/source scope for font and color observations;
- keep raw private theme XML local-only; only sanitized role/token observations may cross the boundary.

## Reviewer acceptance boundary

Checkpoint 2 may be approved only when the sanitized descriptors are safe **and** sufficiently truthful for the next resolver to consume without inventing meaning.

No private visual review is required to close these blockers. `blocked_visual_review` remains an acceptable Checkpoint 2 status.

## Current authorization

Codex is authorized only to correct CP2-C1 through CP2-C5 under a dedicated correction task. It may reopen only the same three stable aliases through the guarded Checkpoint 2 private flow after all pre-open gates pass.
