# TASK — Phase 3 Final Visual Composition Closure

## Authorized scope

Implement V1–V5 on top of CP5-H/I.  Preserve the CP5-I deck as baseline and
produce a new final deck through `PythonPptxAssembler` only.

## Required outcomes

1. Validate and repair downstream result projection for RES101, RES102, and
   RES201 from materialized canonical state.
2. Deduplicate alias-equivalent presentation fields while preserving source
   fields and notes/provenance.
3. Persist one composition plan for the fresh cover plus every Phase 2 source
   slide, with real archetype/layout/visual bindings.
4. Build a new figure-first PPTX; raw Python/JSON/backend field dumps must not
   be visible on formal slides.
5. Persist semantic, layout/archetype, figure-placement, render/release, and
   privacy evidence; run focused tests, a frozen-candidate disposable full
   regression, and final privacy/package checks.

## Hard boundaries

Private alias/source/render counters remain zero.  Do not create CP5-J,
another presentation exporter, new scientific evidence, production figures
beyond approved CP5 outputs, or a PPTX binary based on the existing deck.
