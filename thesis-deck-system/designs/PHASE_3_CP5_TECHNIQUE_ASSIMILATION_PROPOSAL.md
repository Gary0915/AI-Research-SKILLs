# Phase 3 — CP5 Technique-Assimilation Proposal

## Decision and guardrails

CP5 should assimilate only the external engineering techniques identified by
the reconnaissance, with the thesis Ledger, stage-aware projections,
Hypothesis Layers, field-level semantic contracts and `PythonPptxAssembler`
remaining the controlling architecture. This proposal is design-only. It does
not authorize CP5 implementation, source reuse, figure generation, PPTX
creation, template reconstruction, private access or a public Skill registry.

The planned architecture is:

```text
Ledger/Evidence -> Hypothesis Layer -> Scientific Method -> Slide Spec
-> FigureProductionPlan -> ScientificFigureSpec -> specialist
-> canonical Scientific SVG -> semantic/structural SVG QA -> FigureCritic
-> Approved Figure -> Layout Director -> DrawingML compiler adapter
   (inside PythonPptxAssembler) -> native PPTX -> render/professor QA -> Master Deck
```

The optional correction loop is explicitly non-authoritative:

```text
preview -> CurrentSlideContext -> ReviewAction -> source-revision request
-> specialist or Layout Director -> canonical source revision
```

## CP5-A — canonical Scientific SVG language and semantic contract

- **Scope:** add an allowlisted SVG profile, stable object IDs, minimal
  rendering-neutral semantic markers, SVG ownership model, and static
  validator. No renderer.
- **Prerequisites:** CP4’s self-validating plan/spec route; current external
  reconnaissance review approval.
- **Artifacts:** Scientific SVG schema/contract, capability-independent SVG QA
  report and source/manifest binding records.
- **RED tests:** unknown SVG feature/metadata; visible output depending on
  metadata; manifest/SVG figure-ID mismatch; duplicated object ID; embedded
  claim/evidence provenance that must remain manifest-only; forbidden raster
  fallback.
- **Stop condition:** every SVG contract passes and no object can bypass
  FigureCritic; otherwise reviewer gate blocks CP5-B.
- **Blocked dependencies:** none for synthetic figures; private data remains
  irrelevant.

## CP5-B — vector builder and native-capability policy

- **Scope:** `SVGNativeCapabilityRegistry`, exact/normalized/vector/raster/
  unsupported states, deterministic static test vectors and capability QA.
- **Prerequisites:** CP5-A closed IR.
- **Artifacts:** capability registry, versioned test-vector corpus, capability
  decision records.
- **RED tests:** undeclared feature; native claim without mapping; fallback
  without manifest status; unsupported CJK/transform treatment; change in
  registry invalidating output manifest.
- **Stop condition:** each planned specialist primitive has an honest class;
  unmeasured native fidelity stays unresolved.
- **Reviewer gate:** approve no-silent-fallback policy before any director.

## CP5-C — structured scientific directors

- **Scope:** Fishbone, mechanism, experiment schematic and fabrication/process
  directors emit canonical SVG only from CP4 specs.
- **Prerequisites:** CP5-A/B; specialist contracts from CP4.
- **Artifacts:** deterministic SVGs, FigureOutputManifests, Critic reports and
  static QA. Historical Fishbone revision bindings remain immutable.
- **RED tests:** altered Fishbone history/focus; invented fabrication condition;
  mechanism absorbing fabrication role; evidence/spec mismatch; SVG outside
  capability registry.
- **Stop condition:** FigureCritic approval plus provenance/semantic QA for
  each figure class; no slide/PPTX output yet.

## CP5-D — evidence-bound visual directors

- **Scope:** scientific plots, photo annotations, literature figures, image
  matrices and fair comparisons; no generated evidence.
- **Prerequisites:** CP5-A/B and CP4 evidence/source requirements.
- **Artifacts:** class-specific output manifests, source identity hashes,
  overlays distinct from evidence, comparison fairness QA.
- **RED tests:** generated concept used as observation; literature provenance
  absent; plot canonical vector absent; photo source identity replaced; control
  and proposed panels asymmetrically transformed.
- **Stop condition:** empirical/literature evidence stays immutable and each
  visual can be audited to canonical source inputs.

## CP5-E — FigureCritic, local visual review and deictic correction

- **Scope:** render/static review synthesis, CurrentSlideContext and
  ReviewAction design/implementation, temporary token override workflow.
- **Prerequisites:** approved canonical SVG output from CP5-C/D.
- **Artifacts:** image-capable review records with render hashes; CurrentSlideContext;
  immutable ReviewActions and approved override events.
- **RED tests:** stale selection context; object ID not in manifest; comment
  mutating source directly; private-unauthorized review provider; qualitative
  pass from metadata; preview override counted as professor calibration.
- **Stop condition:** each visual correction is traceable to source revision;
  private review remains blocked unless a provider passes its existing gate.

## CP5-F — compiler integration beneath the single assembler

- **Scope:** decide implementation of the DrawingML compiler adapter only after
  capability-vector/native acceptance evidence; compile approved figures under
  `PythonPptxAssembler`.
- **Prerequisites:** CP5-A/B plus approved test vectors and native acceptance
  environment. No code reuse decision is presumed.
- **Artifacts:** adapter contract, compilation records, OpenXML relationship
  audits and native/vector/fallback capability evidence.
- **RED tests:** unapproved SVG reaches Layout; compiler causes raster fallback
  without declaration; output object lacks slide relationship; a second
  exporter is invoked; unsupported object claimed native-exact.
- **Stop condition:** structural and native PowerPoint acceptance are both
  passing for agreed test vectors; otherwise compiler remains blocked.

## CP5-G — archetype calibration and professor visual benchmarks

- **Scope:** only after CP5-C–F, calibrate A01–A18 and run sanitized professor
  benchmarks/acceptance deck workflow under existing private-provider policy.
- **Prerequisites:** native template reconstruction authorization and a passing
  compiler gate.
- **Artifacts:** calibrated geometry, benchmark metrics, acceptance deck,
  render/montage, image-capable review and native acceptance evidence.
- **RED tests:** uncalibrated archetype marked calibrated; body exemplar
  contaminating shell; review pass without private authorization; historical
  scientific state lost at a slide cursor.
- **Stop condition:** all visual, semantic, temporal, structural and native
  gates pass. Group Meeting readiness requires a separate reviewer decision.

## New bounded future technical components

| Component | Decision | Earliest checkpoint | Boundary |
| --- | --- | --- | --- |
| `scientific-svg-authoring` | NEEDED_BEFORE_CP5 | CP5-A | technical reference; does not plan science |
| `semantic-svg-governor` | NEEDED_BEFORE_CP5 | CP5-A | owns only SVG marker allowlist |
| `svg-native-capability-registry` | NEEDED_DURING_CP5 | CP5-B | declares editable/fallback truth |
| `current-slide-context` | NEEDED_DURING_CP5 | CP5-E | transient selection resolves to manifest revision |
| `figure-live-review` | NEEDED_DURING_CP5 | CP5-E | emits ReviewAction, never direct science edits |
| `drawingml-compiler-adapter` | NEEDED_DURING_CP5 | CP5-F | internal to sole assembler |
| `native-roundtrip-editor` | LATER | post-generation | deferred cumulative maintenance |

## Profile-layering recommendation

Do not migrate now to `ProfessorBrandProfile`, `ProfessorLayoutProfile`,
`ProfessorCompositionStyle`, and `ProfessorScientificFigureGrammar`. CP2/CP3
already preserve the necessary authority split. A future migration is justified
only by a concrete inability to express a token’s ownership or conflicting
authorities. It would require backward-compatible adapters for
VisualStyleProfile/TemplateProfile/body-composition/figure grammar schemas,
artifact migration tests, provenance preservation, and CP3-calibration
regression—not merely renamed fields.

## Evidence and dependency rules

Source inspection supports the CP5-A/B/E/F techniques; upstream checker/comment
tests support only their local implementation claims; no synthetic benchmark
claim is made because B01–B10 are `blocked_environment`. Any external code
reuse must receive separate reviewer authorization, carry MIT notice and pinned
source SHA, close dependencies, stay namespaced inside the assembler boundary,
and add thesis-owned tests. No external source is copied by this proposal.

```yaml
codex_report:
  phase: PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL
  status: awaiting_external_architecture_review
  implementation_authorized: false
  private_access_counters: [0, 0, 0]
  next_action_requested: REVIEW
```
