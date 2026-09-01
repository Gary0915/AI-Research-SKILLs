# Task — Final Evidence, Figure Binding, and Incremental Research Deck Lineage Closure

Status: reviewer-authorized bounded closure design

Production baseline: `94060296906ad91dd34fac8495578a383e87c26d`

This task is **not a new Phase**, not CP5-J, and not a general architecture rewrite. It combines the remaining final-evidence/figure-binding corrections with the minimum incremental-deck behavior required for real research usage.

## 1. Why this closure exists

The production baseline already proved major reliability improvements and a 504-test zero-failure regression. The remaining issues are concentrated:

1. generated-PPTX privacy proof needs exact staged-index byte authority;
2. generated PPTX inputs/media need closed lineage;
3. final scientific figures must be slide-specific rather than route-only representative fixtures;
4. Fishbone fallback evidence must match actual vector/raster package representation;
5. final current evidence must be internally consistent;
6. the deck must grow incrementally instead of conceptually rebuilding old research every meeting;
7. latest user-supplied report lineage should become higher-priority body-composition evidence without changing the current thesis shell.

## 2. Read these reviewer materials first

On reviewer branch `review/incremental-deck-lineage-2026-09-01`:

- `thesis-deck-system/research/LATEST_HIGH_PRIORITY_BODY_COMPOSITION_AND_INCREMENTAL_DECK_ANALYSIS_2026-09-01.md`
- `thesis-deck-system/designs/INCREMENTAL_RESEARCH_DECK_LINEAGE_AND_REFERENCE_PRIORITY_POLICY_V1.md`
- `thesis-deck-system/designs/presentation-reference-priority-v2.json`

These documents contain sanitized derived observations only. Raw user-supplied reference binaries are not production inputs and must not be added to Git.

## 3. Preserve existing authorities

Scientific truth remains:

```text
canonical objects
→ append-only Ledger
→ cursor materialization
→ SlideSpec
→ presentation semantic projection
```

Shell authority remains the existing sanitized thesis/professor shell.

The latest JDP/TSMC reference lineage affects body composition only.

`PythonPptxAssembler` remains the sole public PPTX writer.

## 4. Closure workstreams

### FEC-01 — Exact staged-index generated-PPTX attestation

The authoritative privacy gate must attest exact Git-index bytes, not merely working-tree bytes.

Required evidence for each staged generated PPTX:

- repository-relative path;
- staged Git blob SHA;
- SHA-256 of exact staged bytes obtained from Git/index authority;
- working-tree SHA-256 if present;
- working-tree/staged equality status;
- candidate-state hash;
- artifact class;
- producer source identity/hash;
- source-closure hash;
- media-lineage hash;
- package-audit hash;
- sealed execution status.

Raw `private_pptx_candidate` detection remains fail-closed and visible. Generated-artifact adjudication is not a legacy exception.

### FEC-02 — Closed source/media lineage

Every generated PPTX direct authoritative input must have controlled identity and exact hash. Every package media part must map to an approved source/generated lineage.

Required zero counts:

- unresolved input;
- unresolved media part;
- undeclared media part;
- duplicate media lineage;
- private input;
- package privacy finding.

### FEC-03 — Slide-specific scientific figure binding

The final deck must not satisfy figure slots with generic representative fixtures selected only by route.

Required path:

```text
canonical slide scientific data
→ typed slide-specific figure input
→ existing director/specialist
→ Scientific SVG IR
→ FigureOutputManifest
→ Static FigureCritic
→ ApprovedFigureHandle
→ native plan / truthful fallback
→ slide
```

Result, experiment, mechanism/transition, and comparison figures bind to canonical scientific input hashes.

Representative builders remain permitted for unit tests/benchmarks only.

### FEC-04 — Fishbone physical representation truth

If the final PPTX physically embeds PNG preview bytes, evidence must classify it as explicit raster fallback.

Only classify SVG/vector fallback if the actual package contains a safe supported SVG/vector representation through the existing single-backend path.

### FEC-05 — Current evidence reconciliation

Final report-consistency artifacts must use one current authoritative facts projection. Stale historical test/hash/component counts cannot coexist with `aggregate_status: pass`.

## 5. Incremental deck workstreams

### IDL-01 — Slide lineage records

Add a closed record equivalent to:

```text
SlideLineageRecord
  slide_id
  topic_id
  semantic_parent_id
  source_cursor
  lifecycle_policy
  dependency_hash
  composition_family
  body_reference_evidence_ids[]
  artifact_hash
  accepted_revision
```

Minimum lifecycle policies:

- `historical_stable`
- `append_after_semantic_parent`
- `versioned_snapshot`

### IDL-02 — Incremental materialization decisions

Add a deterministic record equivalent to:

```text
SlideMaterializationDecision
  slide_id
  previous_artifact_hash
  previous_dependency_hash
  current_dependency_hash
  decision
  reason_code
  output_slide_id
  revision
```

Minimum decisions:

- `reuse_exact`
- `append_new`
- `new_revision`
- `rebuild_dependency_changed`
- `exclude_from_meeting_view_only`

### IDL-03 — Reuse unchanged accepted content

Previously accepted historical slides and approved figure/native-plan bundles are reused when authoritative dependency hashes are unchanged.

A newly appended research event must not automatically cause old slides or old figures to regenerate.

### IDL-04 — Append after semantic parent

New content is inserted where it belongs scientifically, not simply at the physical deck end.

Examples:

- experiment after its problem/hypothesis/strategy block;
- result after owning experiment;
- integrated discussion after its result set;
- transition between completed and new topic;
- new validation evidence after the method/precision-improvement block it validates.

### IDL-05 — Versioned snapshots

Versioned snapshot families include at least:

- Fishbone;
- research map;
- system blueprint;
- current summary;
- future plan/schedule;
- progress roadmap;
- threshold/evaluation overview when source specifications change.

Create a new revision; do not erase prior historical revision identity.

### IDL-06 — Canonical master deck vs meeting view

The canonical research deck preserves research history.

A `MeetingDeckView` is an ordered selection over canonical slide identities. Omission from a meeting export is not deletion.

### IDL-07 — Dependency-aware atomic rebuild

When an upstream scientific dependency changes, every dependent visible value, formula, figure, caption, callout, and summary must move to the same dependency generation.

Mixed-generation slides fail closed.

This rule is mandatory because the reviewed external lineage contains a real stale-update example in which updated dimensional/derived threshold evidence coexists with older explanatory threshold text.

## 6. Latest body-composition evidence

Do not copy the JDP/TSMC shell/background/footer. Use only sanitized body-composition findings.

Body reference priority:

1. `JDP-TSMC-2026-0814`
2. `JDP-TSMC-2026-0730`
3. `JDP-TSMC-2026-0617`
4. `JDP-TSMC-2026-0604`
5. `JDP-TSMC-2026-0525`

Priority is ordinal and applies only within equivalent body families.

Recommended controlled body families:

- `BCF-TEXT-TOP-DUAL-VISUAL`
- `BCF-PRINCIPLE-EQUIPMENT-SPLIT`
- `BCF-FEASIBILITY-EVIDENCE-MATRIX`
- `BCF-HARDWARE-DESIGN-PROCEDURE`
- `BCF-PHYSICAL-VALIDATION-MATRIX`
- `BCF-TECHNOLOGY-COMPARISON`
- `BCF-PROBLEM-TO-SOLUTION`
- `BCF-REAL-RESULT-VALIDATION`
- `BCF-LITERATURE-VISUAL-MATRIX`
- `BCF-THREE-COLUMN-PHYSICAL-COMPARISON`

These supplement current A01–A18 archetype authority. They do not replace archetype IDs.

Final composition model:

```text
scientific semantic stage
+ canonical archetype
+ high-priority body-composition family
+ current thesis shell
→ SlideCompositionPlan
```

## 7. Visual behavior to preserve

High-priority body grammar:

- structured high information density;
- technical evidence dominates decorative whitespace;
- photos/CAD/equations/plots can coexist when they form one scientific argument;
- light neutral evidence-caption strips directly under images;
- red focus outline/callout for critical regions, not generic red-bordered cards;
- heavy black arrows for major causal/process flow;
- red arrows for warning/critical location;
- thin/dashed lines for measurement/reference geometry;
- semantic color use rather than decorative palette expansion;
- literature pages are figure-led, with concise source labeling;
- result validation may show setup → measurement → software/plot → quantified interpretation in one slide.

Do not force a commercial-card aesthetic.

## 8. Style migration rule

A newly added higher-priority body exemplar does not automatically invalidate accepted historical slides.

Default:

```text
new body reference evidence
→ applies to new slides and already-invalidated slides
```

A deck-wide visual migration of historical slides is separate future work unless explicitly authorized.

## 9. Tests required

### Privacy

- staged exact bytes pass;
- staged/worktree divergence blocks finalization;
- restage invalidates old attestation;
- arbitrary staged PPTX without proof fails;
- source closure complete;
- all media parts have lineage.

### Figure binding

- RES101/RES102/RES201 each bind to canonical result-specific figure input;
- materially different result inputs do not silently reuse the same generic plot;
- different experiment inputs produce different figure-input hashes unless normalized input is truly equal;
- mechanism reuse requires equal scientific-input hash;
- Fishbone physical representation matches evidence enum.

### Incremental lineage

- unchanged historical slide → `reuse_exact`;
- new result → `append_new` after semantic parent;
- new topic → transition + new block without duplicating previous topic;
- Fishbone update → `new_revision`, old revision remains addressable;
- future-plan update → new snapshot revision;
- meeting view omission does not delete canonical slide;
- changed threshold/specification invalidates all dependent values/figures/text atomically;
- stale mixed-generation slide fails;
- unchanged figure-input hash reuses exact approved figure/native-plan bundle;
- new body-reference priority alone does not rebuild accepted historical slides;
- shell authority unchanged.

## 10. Performance and validation discipline

Use the already-implemented durable validation runner.

Implementation phase:

```text
targeted tests
→ focused closure tests
→ candidate-affecting artifact regeneration
→ freeze
```

Only after freeze:

```text
ONE definitive full regression
→ final exact staged privacy
→ evidence/report consistency
→ commit/push/remote verify
```

Do not run the complete regression after every small correction.

If the interactive session stops but durable child-process evidence completes with exact candidate hashes and exit status, reuse it.

## 11. Scope prohibitions

Do not implement:

- CP5-J;
- a new Phase;
- full general BuildGraph;
- repository-wide ProjectContext rewrite;
- full Ledger snapshot architecture;
- complete professor physical Master/Layout reconstruction;
- second PPTX writer;
- raw external reference ingestion into Git;
- historical deck-wide style migration;
- new external architecture research.

## 12. Final acceptance facts

The closure must be able to report at minimum:

- exact staged generated-PPTX attestations;
- source closure/media lineage zero unresolved counts;
- route-only representative final figure count = 0;
- result-specific figure-binding status for RES101/102/201;
- experiment/mechanism reuse decisions and scientific-input hashes;
- truthful Fishbone vector/raster fallback;
- current evidence consistency mismatch count = 0;
- canonical slide lineage count;
- reused historical slide count;
- newly appended slide count;
- new snapshot revision count;
- dependency-triggered rebuild count;
- meeting-view excluded-only count;
- stale mixed-generation slide count = 0;
- shell override by external body reference = 0;
- body-reference priority policy applied to new/invalidated slides;
- final full regression zero failures;
- final privacy zero unexcepted findings;
- production Group Meeting readiness remains false until actual required visual/native review passes.

## 13. Product principle

The system is successful when it behaves like a persistent research record, not a one-shot slide generator:

> Accepted research history is reused; new evidence is inserted where it scientifically belongs; changing overview/state slides are versioned; dependency changes rebuild only what is invalidated; meeting decks are focused views; and the newest trusted body-composition evidence improves future slides without replacing the thesis shell or rewriting valid history.
