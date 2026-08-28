# Phase 3 TDD Implementation Plan Revision 2 Review

## Verdict

**REVISE — production Phase 3 implementation remains unauthorized.**

The revised plan closes the previous P3-PLAN-B1–B6 blockers and materially improves the visual-production architecture. It now has deterministic figure routing, SVG-first vector production, specialist figure Skills, VisualStyleGovernor, FigureCritic-before-Layout, representative+stress benchmarks, private-render minimization, fresh package lineage, and decomposed fidelity statuses.

Four plan-level corrections remain before production implementation.

## P3-PLAN-C1 — Figure output contract must be artifact-type aware

The current plan states that `figure-output-manifest` requires a canonical SVG path/hash. That is correct for vector diagrams and most scientific plots, but it is not correct for every figure class.

A real experimental photo, extracted literature figure, generated conceptual raster substrate, and native-shape-only figure must not be forced to masquerade as an SVG artifact.

Replace the universal SVG requirement with a typed/discriminated primary-artifact contract. At minimum support:

- `vector_diagram`: canonical SVG, optional native plan/PNG fallback;
- `scientific_plot`: canonical SVG and/or PDF vector, optional PNG fallback;
- `real_photo`: immutable source evidence asset + deterministic annotation overlay (SVG/native), optional composed preview;
- `literature_figure`: extracted source asset + citation/provenance + optional annotation overlay;
- `concept_illustration`: generated non-evidence substrate + deterministic annotation overlay;
- `native_shape_figure`: canonical native-shape plan + geometry manifest, optional SVG/render preview.

The manifest must preserve one unambiguous `primary_artifact_kind` and provenance chain. Tests must reject cross-class masquerading (for example raster experimental evidence declared as a generated SVG figure).

## P3-PLAN-C2 — Observation archetype may not use conceptual imagery as evidence

The A04 routing matrix currently permits `real photo annotation or approved concept` for Observation.

For professor Scientific Method semantics, an Observation page must not satisfy its observation/evidence requirement with a generated conceptual image. A non-evidence concept may be an auxiliary illustration only when explicitly separated from the Observation evidence.

Required rule:

- empirical Observation requirement → real Evidence / measurement / photo / source-derived visual;
- conceptual illustration → auxiliary `non_evidence`, never satisfies evidence binding, never substitutes Observation.

Add routing and presentation-semantic negative tests.

## P3-PLAN-C3 — Private image review provider requires privacy authorization, not capability alone

`ImageReviewProvider` currently preflights image capability and hash binding, but private exemplar renders contain private research information.

The provider contract must also declare and enforce a privacy capability before it may inspect private renders. Plan fields should include an equivalent of:

- `private_content_allowed`;
- `egress_mode` / local-vs-remote handling class;
- `retention_class`;
- `approved_for_private_exemplars`;
- audit/provider identifier.

If a provider is image-capable but is not approved to receive private exemplar content, it may inspect sanitized renders only. Private-reference qualitative comparison remains `blocked_visual_review` unless an approved private-safe provider exists.

Add RED tests proving a capable-but-private-unauthorized provider cannot inspect private slides or produce professor-fidelity PASS.

## P3-PLAN-C4 — Add a fabrication/process-flow specialist

The current specialist set covers mechanism explanation and measurement/experiment schematic, but not fabrication/process flow. Materials/hydrogel presentations frequently require preparation sequences such as mixing → molding → curing/crosslinking → washing/swelling → electrode integration.

Do not overload causal mechanism or measurement setup with this responsibility.

Add a repo-local specialist such as `fabrication-process-director` (name may differ) whose bounded responsibility is chronological sample/device preparation flow. It should route to native/SVG vector primitives and preserve process order, conditions, materials, optional timing/temperature, and sample-state transitions without inventing process parameters.

Add it to Figure Router policy, Skill contracts, `skill-routing.yaml` plan, A01–A18 mappings where relevant, and RED tests.

## Accepted strengths to preserve

Do not regress:

- P3-PLAN-B1–B6 corrections;
- two-domain fail-closed privacy boundary;
- structural-first streaming private rendering;
- asymmetric Exemplar 1/3 shell vs Exemplar 2 body/figure authority;
- evidence tiers;
- SVG-first policy with evidence-backed native-shape threshold;
- no generative replacement of experiment/literature/quantitative evidence;
- VisualStyleGovernor;
- FigureCritic before Layout Director;
- one `PythonPptxAssembler` backend;
- representative+stress benchmarks;
- fresh package lineage and benign-boilerplate classification;
- independent final fidelity/readiness dimensions;
- Phase 1–2 temporal/scientific/provenance invariants.

## Scope

This is a short plan correction, not an architecture reset. Revise only the implementation plan. Production Phase 3 work remains unauthorized until reviewer approval.