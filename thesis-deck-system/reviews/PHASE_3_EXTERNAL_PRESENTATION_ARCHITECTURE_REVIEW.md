# Phase 3 External Presentation Architecture Review

## Verdict

**REVISE — reconnaissance evidence is useful, but the CP5 assimilation proposal has three architecture blockers that should be corrected before CP5 implementation begins.**

Reviewed implementation commit: `7299083ec4148adbe84473f1f78c2a642fbfe9ad`.

## What is approved from the reconnaissance

The following conclusions are accepted and should be preserved:

1. Keep thesis-deck-system as the scientific/narrative/provenance authority.
2. Do not adopt open-slide as the canonical final renderer or research state.
3. Adopt/adapt a thesis-owned constrained Scientific SVG IR rather than arbitrary browser SVG.
4. Keep SVG research provenance in Ledger/manifest contracts rather than duplicating full Claim/Evidence chains inside SVG.
5. Add an explicit SVG→PowerPoint native-capability registry before any native-fidelity claim.
6. Keep any future DrawingML compiler below the single `PythonPptxAssembler` public backend boundary.
7. Adopt the interaction concepts behind CurrentSlideContext and immutable ReviewAction later.
8. Defer native PPTX round-trip until new-deck production and native acceptance are proven.
9. Do not rename/migrate the current professor profile contracts without a concrete contract limitation.
10. No external source code should be vendored merely because it is MIT; any future reuse requires a separate dependency/license/test decision.

## Blocker R1 — Circular FigureCritic dependency in the proposed CP5 sequence

The proposal currently places FigureCritic/live-review implementation in CP5-E, but CP5-C already requires `FigureCritic approval` and claims `Critic reports` as outputs. CP5-E itself says it depends on approved canonical SVG output from CP5-C/D. This creates a circular lifecycle:

`CP5-C/D directors → FigureCritic approval → CP5-E FigureCritic implementation → approved C/D output`.

Before implementing any director, the system needs a non-circular gate. Introduce the FigureOutputManifest/static FigureCritic contract and deterministic static critic implementation before production directors. Image-capable/live/deictic review can remain later.

Recommended split:

- CP5-A: Scientific SVG IR + semantic/static SVG QA + canonical artifact ownership.
- CP5-B: SVGNativeCapabilityRegistry + synthetic test-vector corpus.
- CP5-C: FigureOutputManifest + deterministic/static FigureCritic gate and approval contract. **No production figures yet.**
- CP5-D: structured scientific SVG directors.
- CP5-E: evidence-bound visual directors + strict non-evidence concept boundary.
- CP5-F: render-derived/image-capable review + CurrentSlideContext + ReviewAction/live review.
- CP5-G: A01–A18 visual calibration and professor render benchmarks at the SVG/render layer.
- CP5-H: DrawingML compiler adapter/native test-vector integration under `PythonPptxAssembler`.
- CP5-I: reconstructed native template + acceptance deck + native PowerPoint release gate.

Equivalent decomposition is acceptable if the dependency graph remains acyclic.

## Blocker R2 — Scientific SVG semantic metadata is still broader than necessary

The reconnaissance correctly says scientific truth and detailed provenance belong in Ledger/manifests, but it simultaneously proposes SVG root metadata such as `data-hypothesis-layer` and `data-research-block`.

Those values are research/provenance bindings and can become stale when a reusable figure is copied, revised, or rebound. The SVG should be the visual authoring IR, not a second scientific provenance store.

The CP5-A design should use a minimal rendering-neutral marker set. Preferred mandatory metadata:

- SVG schema/profile version,
- `figure_id`,
- stable `object_id`,
- local `semantic_role`,
- optionally `visual_class` where useful for static validation.

Scientific bindings such as Hypothesis Layer, Research Block, Stage, Claim, Evidence, source cursor, source hash and evidence mode should remain canonical in `ScientificFigureSpec` / `FigureOutputManifest` / Ledger. If any such field is mirrored into SVG for tooling convenience, it must be explicitly non-authoritative, manifest-validated, optional, and excluded from scientific truth/reuse decisions.

## Blocker R3 — Native PowerPoint acceptance must not block visual calibration

The proposal currently makes CP5-G archetype calibration/professor benchmarks depend on CP5-F compiler/native acceptance. This unnecessarily couples professor visual learning to an environment-dependent native-PowerPoint gate.

A01–A18 geometry/style calibration and professor visual benchmarks can be performed at the canonical SVG/render level after the figure directors and FigureCritic are stable. Native DrawingML fidelity is a later release dimension.

Therefore separate:

- **visual fidelity readiness**: canonical SVG + render + professor grammar + FigureCritic;
- **native editability readiness**: DrawingML/OpenXML/native PowerPoint acceptance.

A blocked native PowerPoint environment must block native/PPTX release, but should not prevent SVG/render-level archetype calibration.

## Blocker R4 — CP5-B must be evidence-honest because B01–B10 are currently blocked

All ten compiler benchmark families were `blocked_environment`. Therefore CP5-B may create the registry and test-vector contracts, but must not pre-populate `NATIVE_EXACT` or `NATIVE_NORMALIZED` claims from documentation alone.

Initial state rules:

- unmeasured compiler fidelity = `UNKNOWN`;
- source-inspected mapping may be recorded as `declared_upstream_capability`, not thesis-verified capability;
- native/editable claims require thesis-owned execution evidence;
- SVG directors may still use valid canonical SVG even when native capability remains unknown;
- no silent raster fallback.

The benchmark block is not a reason to stop CP5-A/C/D visual work.

## Blocker R5 — open-slide PPTX export must be explicitly classified as raster/screenshot style

At the pinned open-slide commit, `export-pptx.ts` captures each React slide through `html-to-image` and writes the captured PNG as a full-slide picture in PPTX. It is useful evidence for why open-slide must not become the native thesis exporter, but the reconnaissance should explicitly classify this path as raster/image-PPTX rather than merely listing a PPTX export module.

This clarification matters because the thesis system explicitly rejects whole-slide raster skins as canonical editable output.

## Required revision outcome

Revise only the reconnaissance/proposal artifacts. Do not modify CP1–CP4 code, schemas, Skills, routing, private data, or start CP5 implementation.

The revised proposal must provide:

1. an acyclic CP5 dependency graph;
2. a minimal/non-authoritative semantic SVG policy;
3. independent visual-fidelity vs native-editability gates;
4. an honest initial capability-registry evidence model;
5. an explicit classification of open-slide PPTX as raster/image-slide export at the pinned commit;
6. a final recommended CP5 sequence with prerequisites, artifacts, stop conditions and reviewer gates.

After those changes, the architecture gate can be approved and CP5-A can begin.