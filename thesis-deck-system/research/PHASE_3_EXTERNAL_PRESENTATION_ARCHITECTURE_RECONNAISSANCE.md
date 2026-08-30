# Phase 3 — External Presentation Architecture Reconnaissance

## Scope, freeze, and evidence limits

This CP5-preparation research gate is design-only. It inspects only pinned
public upstream material and committed sanitized CP2/CP3/CP4 artifacts. No
external code was vendored, no CP1–CP4 implementation changed, and private
alias resolution, private source-open, and private render attempts are all
`0`.

The CP4 freeze preflight remains unchanged: 10 bounded visual classes and 10
plans/specs, 18 routed archetypes, 19 execution-owned checks, and equal tested
and current candidate hashes. Production rendering, calibration, template
reconstruction, acceptance deck, and native PowerPoint remain `not_run`.

The machine-readable source record is
[`external-repo-provenance.json`](../artifacts/phase3/external-repo-provenance.json),
and the 24-decision disposition record is
[`external-technique-assimilation-matrix.json`](../artifacts/phase3/external-technique-assimilation-matrix.json).

## Pinned sources and inspection method

| Project | Pinned commit | License | Inspected public surface | Dependency burden |
| --- | --- | --- | --- | --- |
| PPT Master | `e5a05edebe24c7c00c589dbed4f4777cb9855c91` | MIT | constrained SVG contract/checker, mapping docs, template topology, routing/review, converter/editor modules and tests | Python/OOXML/SVG; optional Office rendering |
| open-slide | `90bb86172f7e390c29bbf2f33067c7b05c646b70` | MIT | Skills, inspector/selection/comments, export modules, package manifests and tests | Node/pnpm/React/Vite/TypeScript/Playwright |

Both remote `main` refs equalled the supplied baselines at inspection. PPT
Master’s executable dependency closure was unavailable in the throwaway
environment. The synthetic benchmark families B01–B10 were attempted and all
remain `blocked_environment`; no thesis capability result is inferred from
documentation, code inspection, or upstream tests.

## Findings that remain accepted

1. The thesis Ledger and cursor-materialized scientific projections remain the
   sole science/history/provenance authority.
2. A thesis-owned constrained Scientific SVG IR is useful between a specialist
   and a critic; arbitrary browser SVG is not an acceptable contract.
3. A feature-level native capability registry is required before a native
   DrawingML claim.
4. Any compiler is an internal implementation detail of
   `PythonPptxAssembler`, never a competing PPTX backend.
5. The interaction concepts behind CurrentSlideContext, selection, comments,
   and immutable ReviewAction are useful later; React/DOM/browser state is not
   canonical science or rendering authority.
6. CP2/CP3 already preserve a sufficient profile authority split. A profile
   migration is deferred until a concrete contract limitation exists.
7. Native PPTX round-trip is deferred until new-deck production and native
   acceptance are proven.

## Corrected Scientific SVG and artifact ownership conclusion

Scientific SVG is a visual authoring IR. Its mandatory metadata is only an SVG
profile/version, figure ID, stable object ID, and local semantic role; visual
class is optional. Metadata is rendering-neutral—removing it cannot change
visible output.

Research bindings remain authoritative outside SVG in
`ScientificFigureSpec`, `FigureOutputManifest`, and Ledger records. In
particular, Hypothesis Layer, Research Block, Stage, Claim, Evidence, source
cursor/hash, evidence role/mode, Decision, Action, and full provenance chain
must not be duplicated into SVG. A future tooling mirror is allowed only as an
optional `non_authoritative_mirror` that is manifest-validated and cannot be
used as scientific truth or reuse authority.

```text
ScientificFigureSpec (Ledger-bound requirements)
  → canonical Scientific SVG (editable visual structure only)
  → static SVG QA / static FigureCritic
  → FigureOutputManifest (hash, provenance, capability, QA)
  → Approved Figure (gated identity)
  → Layout Director
  → PythonPptxAssembler / optional internal DrawingML adapter
  → PPTX structural audit / render review / Professor QA
  → Master Deck
```

## Corrected capability and readiness model

Every `SVGNativeCapabilityRegistry` entry records a capability state and an
evidence level. Valid states are `NATIVE_EXACT`, `NATIVE_NORMALIZED`,
`VECTOR_FALLBACK`, `RASTER_FALLBACK`, `UNSUPPORTED`, and `UNKNOWN`; evidence
levels are `upstream_declared`, `source_inspected`,
`thesis_synthetic_verified`, and `native_powerpoint_verified`.

An upstream mapping may be declared or source-inspected, but it cannot become
thesis-verified `NATIVE_EXACT` or `NATIVE_NORMALIZED` without thesis-owned
benchmark evidence. `UNKNOWN` is an honest initial state; raster fallback is
always explicit and auditable. A valid canonical SVG is not invalid merely
because its native capability is unknown.

Readiness is deliberately split:

| Status | Owns | Native PowerPoint unavailable |
| --- | --- | --- |
| `svg_visual_fidelity_status` | canonical SVG contract/static evidence | independent |
| `render_visual_fidelity_status` | render-derived evidence | independent |
| `professor_visual_calibration_status` | professor grammar + SVG/render benchmarks | independent |
| `drawingml_native_fidelity_status` | thesis compiler/native vectors | blocked/not run |
| `native_powerpoint_acceptance_status` | native round-trip acceptance | blocked/not run |
| `production_release_status` | all release gates | blocked |

Thus a native PowerPoint block prevents native/PPTX release but does not
prevent Scientific SVG work, figure director work, static/render criticism, or
A01–A18 SVG/render calibration. Scientific SVG legality is separately owned by
the future CP5-A `svg_ir_support_state` (`supported`, `unsupported`, or
`unknown_contract`); the CP5-B native compilation state does not determine SVG
legality. Legal SVG with native `UNKNOWN` or `UNSUPPORTED` remains valid
canonical SVG and can proceed as SVG/render evidence through CP5-G, while its
native compilation claim remains unresolved for CP5-H.

## open-slide export classification

At pinned commit `90bb86172f7e390c29bbf2f33067c7b05c646b70`, inspection of
`packages/core/src/app/lib/export-pptx.ts` found a React-slide export that uses
`html-to-image`, captures a page PNG, and inserts that PNG as the PPTX slide
surface. This is **raster/image-slide PPTX export**, not native editable
PowerPoint authoring.

It is therefore rejected as a canonical thesis PPTX backend and cannot satisfy
the editable-native-output requirement. The separate interaction ideas—current
slide context, element selection, comments/review loop, and live preview—stay
useful as renderer-neutral CP5-F concepts.

## Final CP5 architecture recommendation

The full acyclic CP5 dependency DAG, checkpoint inputs/outputs, static versus
render FigureCritic split, stop conditions, reviewer gates, and prohibited work
are maintained in the revised
[`CP5 technique-assimilation roadmap`](../designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md).

Its required order is:

1. CP5-A — Scientific SVG IR and static SVG QA.
2. CP5-B — native capability registry and synthetic vectors.
3. CP5-C — FigureOutputManifest and deterministic static FigureCritic.
4. CP5-D — structured Scientific SVG directors.
5. CP5-E — evidence-bound visual directors.
6. CP5-F — render/image-capable critic and deictic review interaction.
7. CP5-G — A01–A18 SVG/render calibration and professor benchmarks.
8. CP5-H — DrawingML adapter under the one assembler and native vectors.
9. CP5-I — fresh template reconstruction, acceptance deck, native acceptance,
   and a production release decision.

This ordering removes the former director/Critic cycle: the deterministic
static critic exists at CP5-C before either director track starts. CP5-F reports
static-critic, render-critic, image-capable qualitative-review, and human-review
statuses independently. A `blocked_visual_review` provider outcome blocks only
qualitative acceptance; CP5-G may still perform authorized SVG/render and
geometry/composition calibration, but cannot claim professor qualitative visual
acceptance from those metrics alone. CP5-G is not native-gated. CP5-H and CP5-I
alone carry native fidelity and production-release requirements. `cycle_count =
0`.

## Technique disposition and reuse decision

The disposition matrix remains **ADOPT 6, ADAPT 8, REJECT 5, DEFER 5**:

- adopt/adapt constrained IR, static validation, capability taxonomy, artifact
  ownership, and future review interaction concepts;
- reject generic narrative planning, React/HTML as final rendering authority,
  whole-slide screenshot PPTX export, and competing exporters;
- defer compiler reuse, native round trip, and profile migration until their
  required thesis evidence exists.

No source is copied. Any future direct reuse requires a separate architectural
decision, pinned provenance, MIT attribution, closure inventory, isolated
namespace, maintainer ownership, and upstream-plus-thesis test evidence.

## Professor and scientific authority remain above presentation technique

External patterns do not weaken the required Scientific Method sequence:
Observation → Literature → Mechanism → Solution → Experiment → Result →
Discussion → Decision → Next Step. They also do not weaken N-layer history,
separate Hypothesis/Problem pages, immutable Fishbone revisions, failed
experiment history, asymmetric exemplar authority, or high-information-density
scientific composition where hierarchy is clear.

```yaml
codex_report:
  phase: PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_RECONNAISSANCE
  status: awaiting_external_architecture_review
  branch: codex/thesis-deck-system
  commit_sha: pending_final_commit
  files_added: []
  files_modified:
    - thesis-deck-system/research/PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_RECONNAISSANCE.md
    - thesis-deck-system/designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md
    - thesis-deck-system/artifacts/phase3/external-repo-provenance.json
    - thesis-deck-system/artifacts/phase3/external-technique-assimilation-matrix.json
  files_deleted: []
  artifacts:
    - thesis-deck-system/artifacts/phase3/external-repo-provenance.json
    - thesis-deck-system/artifacts/phase3/external-technique-assimilation-matrix.json
  render_previews: []
  tests_run:
    - JSON structure and 24-record disposition-count validation
    - repository privacy scan with the approved historical exception
    - staged-index privacy scan with the approved historical exception
    - targeted CP3 privacy-scanner pytest selection
    - EAR traceability and CP4 freeze-scope audit
    - absolute private-path scan
    - git diff --cached --check
    - remote SHA/tree/blob verification
  tests_passed:
    - JSON structure and disposition counts: PASS (ADOPT 6, ADAPT 8, REJECT 5, DEFER 5)
    - repository and staged privacy scans: PASS (1 approved historical exception, 0 unexcepted findings)
    - targeted CP3 privacy-scanner tests: 2 passed, 43 deselected
    - EAR traceability / CP4 freeze-scope audit: PASS
    - absolute private-path scan: PASS
    - git diff --cached --check: PASS
    - remote SHA/tree/blob verification: PASS
  tests_failed: []
  known_failures:
    - B01-B10 blocked_environment
  deviations: []
  reviewer_questions: []
  private_access_counters: [0, 0, 0]
  next_action_requested: EXTERNAL_ARCHITECTURE_REVIEW
```
