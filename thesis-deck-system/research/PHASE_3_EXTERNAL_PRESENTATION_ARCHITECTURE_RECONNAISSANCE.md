# Phase 3 — External Presentation Architecture Reconnaissance

## Scope and freeze

This is a CP5-preparation research gate, not CP5 implementation. It inspected
only public, pinned upstream source plus the committed sanitized CP2/CP3/CP4
artifacts. No external code was vendored and no existing CP1–CP4 file was
changed. Private alias, source-open, and render attempts were respectively
`0`, `0`, and `0`.

The CP4 freeze preflight passed from the committed records: 10 bounded visual
classes and 10 plans/specs are present; 18 archetypes are routed; 19
execution-owned checks are recorded; the tested/current candidate hashes agree;
and production rendering, calibration, reconstruction, acceptance deck and
native PowerPoint remain `not_run`. The checked branch contains the frozen
candidate `362b29f47991b2c87fe2a109419d0255899e6921` unchanged.

## Provenance and method

| Project | Pinned default branch commit | License | Inspection | Runtime/dependency burden |
| --- | --- | --- | --- | --- |
| PPT Master | `e5a05edebe24c7c00c589dbed4f4777cb9855c91` | MIT | README/LICENSE, technical and mapping docs, routing/generation/review workflows, SVG contract/checker/tests, DrawingML converter modules, template/round-trip/editor modules | Python ≥3.10; OOXML/ZIP, SVG compiler/validation; optional office rendering |
| open-slide | `90bb86172f7e390c29bbf2f33067c7b05c646b70` | MIT | README/LICENSE/package manifests, five requested Skills, inspector/selection/comment/export modules and tests/e2e listings | Node ≥18, pnpm 10, React/Vite/TypeScript; Playwright for e2e |

Both current upstream `main` refs equal their provided baselines. The machine
readable provenance, inspection counts, benchmark status, and direct-code reuse
status are in
[`external-repo-provenance.json`](../artifacts/phase3/external-repo-provenance.json).

PPT Master source inspection was performed from temporary public-source copies.
The complete executable checkout/dependency closure could not be established in
the throwaway environment, so B01–B10 were attempted but all are honestly
`blocked_environment`; no claimed benchmark finding is inferred from docs or
code inspection. open-slide’s optional browser runtime experiment was not
required for the inspected source-backed context/comment/export boundary.

## Findings — PPT Master

### Constrained SVG, semantics, and ownership

PPT Master does not treat SVG as arbitrary browser markup. Its SVG contract,
semantic markers, closed native-object payloads, and quality checker define a
restricted authoring IR which the compiler validates before it writes DrawingML.
Its marker approach is useful, but the thesis system must keep scientific truth
out of the visible rendering dependency. A future thesis SVG allowlist should
carry only stable rendering-neutral object identifiers and local semantic roles:
`data-thesis-figure-id`, `data-visual-class`, `data-hypothesis-layer`,
`data-research-block`, `data-semantic-role`, and a revision-safe object ID.

`data-source-ref`, `data-claim-ref`, evidence mode, hash/provenance chains,
and detailed scientific bindings remain manifest/Ledger data. Duplicating them
inside SVG invites stale provenance. SVG metadata must be non-visible,
fail-closed, and never required to paint pixels.

Recommended artifact ownership is:

```text
ScientificFigureSpec (scientific requirements; Ledger-bound)
  -> canonical Scientific SVG (editable visual structure + minimal IDs)
  -> static/semantic SVG QA
  -> FigureOutputManifest (hashes, full provenance, capabilities, previews)
  -> FigureCritic approval
  -> PythonPptxAssembler compiled native objects
  -> PPTX structural audit / rendered slide / professor review
```

Canonical SVG is the figure authoring state; previews, PPTX objects and renders
are derived artifacts. The Master Deck remains the ledger-derived deck product,
not an SVG source of truth.

### Compiler and capability boundary

The inspected converter has dedicated DrawingML conversion paths for elements,
paths, text properties, semantic markers and package handling. The mapping
guide describes native/normalized handling for shapes, text, images,
connectors, groups, charts/tables/formulas through explicit marker contracts,
and explicit fallbacks/unsupported limits for items such as SmartArt and
arbitrary extension XML. This is sophisticated engineering, not proof of native
acceptance in this project.

The future thesis system needs `SVGNativeCapabilityRegistry` before compiler
integration. Every SVG feature must declare `NATIVE_EXACT`,
`NATIVE_NORMALIZED`, `VECTOR_FALLBACK`, `RASTER_FALLBACK`, `UNSUPPORTED`, or
`UNKNOWN`; a generated SVG is not evidence of editable PowerPoint fidelity.
No silent native-to-raster conversion is acceptable.

The recommendation for the inspected SVG→DrawingML implementation is **D —
defer until native-PowerPoint acceptance**. In CP5-F, evaluate its patterns and
test vectors first. If code reuse later wins, extract a minimal MIT-attributed
internal library under `PythonPptxAssembler`; otherwise write a thesis compiler
against the same capability tests. Either route leaves one public backend.

### Template, editor, review, and round trip

PPT Master’s separate template architecture and native-structure handling are
valuable references for preserving Master/Layout topology and reconstructing
fresh packages. They do not authorize copying private packages or replacing the
sanitized CP2/CP3 authority model. Its visual review separates static validation
from perceptual review better than a single pass/fail signal; the thesis system
already requires that separation and should retain its professor/image-capable
review honesty.

The SVG editor’s stable object IDs, selection, geometry/text/fill/stroke edits,
groups, multi-select, overlap selection, undo/history, and annotations are
promising for a later review experience. A direct editor state is transient:
the canonical action must become a versioned `ReviewAction` against a figure or
slide revision. Native PPTX round trip is useful for future incremental master
deck maintenance, but is deferred until new-deck production and native
acceptance are proven.

## Findings — open-slide

open-slide is a React/Vite 1920×1080 browser slide runtime. Its Skills
deliberately separate authoring workflow, technical reference, current-slide
context and comment application. Its inspector can select an element, create a
comment, persist source markers, and later apply pending edits. Its export
modules produce browser-oriented HTML/PDF/PPTX paths and its presenter notes
are source-export data.

Those patterns support a future *review* shell, not a thesis renderer. The
project must not use React pages/DOM, screenshots, comments, or browser state
as scientific truth. The useful extraction is a versioned `CurrentSlideContext`:

```text
deck_id, slide_id, slide_revision, figure_id, svg_object_id,
semantic_role, selection_bbox, updated_at, source_manifest_ref
```

It is produced from a preview and resolves deictic requests such as “move this
right”; the request becomes a ReviewAction and is checked against the canonical
figure/Slide Spec revision before any source change. `ReviewAction`, rather
than SVG comments or Slide Spec prose, should own review comments because it
keeps threads, author, status, requested change and approval separate from both
scientific data and rendering markup.

Temporary design-token overrides can be useful: preview override → human
review → approved ReviewAction → calibration/grammar revision. They must never
silently mutate CP2 observation evidence or CP3 professor-derived tokens.

## Side-by-side architecture map

| Domain | Assessment | Evidence-led conclusion |
| --- | --- | --- |
| 1 scientific knowledge source | OUR SYSTEM ALREADY STRONGER | Append-only Ledger and evidence contracts, not slides/React/SVG, own truth. |
| 2 provenance model | OUR SYSTEM ALREADY STRONGER | Cursor/materialization and Evidence chains exceed generic presentation provenance. |
| 3 historical revision model | OUR SYSTEM ALREADY STRONGER | Immutable Hypothesis/Fishbone history is domain-specific. |
| 4 narrative planner | OUR SYSTEM ALREADY STRONGER | Scientific Method stages outrank generic strategist/create-slide flows. |
| 5 visual-class router | COMPLEMENTARY | CP4’s typed ten-class router gains SVG capability input later. |
| 6 figure authoring representation | EXTERNAL SYSTEM STRONGER | PPT Master’s constrained SVG IR is a reusable design pattern. |
| 7 figure semantic metadata | COMPLEMENTARY | PPT Master markers inspire minimal SVG IDs; thesis manifests retain research provenance. |
| 8 style tokens | COMPLEMENTARY | CP3 authority/evidence tiers plus open-slide’s safe preview-token workflow. |
| 9 layout system | COMPLEMENTARY | Thesis has governed slots; external systems add editor/canvas ergonomics. |
| 10 Master/Layout system | EXTERNAL SYSTEM STRONGER | PPT Master exposes mature package/topology concepts; CP2 remains authority source. |
| 11 final renderer/compiler | COMPLEMENTARY | PPT Master is strong implementation reference; PythonPptxAssembler remains sole boundary. |
| 12 native editability | EXTERNAL SYSTEM STRONGER | Native DrawingML mapping is more mature; must be proven against thesis cases. |
| 13 incremental editing | COMPLEMENTARY | PPT Master round trip informs a later non-authoritative adapter. |
| 14 human visual review | COMPLEMENTARY | PPT Master editor/open-slide inspector inform future ReviewAction UX. |
| 15 AI visual review | OUR SYSTEM ALREADY STRONGER | Provider privacy authorization and blocked-honesty are explicit. |
| 16 live object selection | EXTERNAL SYSTEM STRONGER | open-slide supplies a useful deictic selection model. |
| 17 comments/revision requests | COMPLEMENTARY | open-slide loop motivates separate ReviewAction, not source markers. |
| 18 CJK handling | COMPLEMENTARY | PPT Master maps text/font paths; CP2 preserves script-aware font evidence. |
| 19 deterministic QA | COMPLEMENTARY | PPT checker patterns complement thesis temporal/schema/provenance QA. |
| 20 privacy model | OUR SYSTEM ALREADY STRONGER | CP1/CP2 scanning, bounded private sessions and sanitization are stricter. |
| 21 reproducibility | OUR SYSTEM ALREADY STRONGER | Ledger replay, candidate hashes and manifests are scientific reproducibility. |
| 22 license/dependency burden | OUR SYSTEM ALREADY STRONGER | Both external projects are MIT, but importing either expands Python/Node surface. |
| 23 backend conflicts | OUR SYSTEM ALREADY STRONGER | Explicit single backend rule rejects competing exporters. |
| 24 testability | COMPLEMENTARY | External checker/compiler test vectors can supplement thesis contract tests. |

## Adopt/adapt/reject/defer conclusion

The complete machine-readable matrix is
[`external-technique-assimilation-matrix.json`](../artifacts/phase3/external-technique-assimilation-matrix.json).
It records 24 techniques with pinned source paths, license, target component,
risk decision and evidence strength. Totals are **ADOPT 6, ADAPT 8, REJECT 5,
DEFER 5**.

### Direct-code-reuse analysis

| Candidate | Pinned upstream files / approximate surface | Tests / dependency closure | Recommendation and license implication |
| --- | --- | --- | --- |
| SVG quality checker | `scripts/svg_quality/checker.py`, `svg_contracts.py`, and checker tests; substantial Python validation surface | Source includes focused checker tests; closure includes the project’s XML/SVG contract modules | Reimplement thesis-specific checks from concepts/test vectors first. MIT notice and pinned-SHA attribution would be mandatory if any code is copied. |
| SVG→DrawingML compiler | `drawingml/converter.py`, `elements.py`, `paths.py`, `text_properties.py` plus package/marker helpers; large coupled compiler surface | Tests and a meaningful package/helper closure are required; a standalone file is not a viable reuse unit | **D — defer until native-PowerPoint acceptance.** Do not vendor now. Later choose minimal internal library only if a license/namespace/dependency audit and thesis-native tests justify it. |
| SVG editor | `svg_editor/server.py`, `annotations.py`, browser app; Python+browser surface | Editor behavior depends on its local server/static stack | Reimplement protocol-level CurrentSlideContext/ReviewAction interfaces; do not import editor code until a later UX-specific decision. |
| open-slide inspector/comments | `editing/comments.ts`, inspector hooks/components, comment tests; React/Vite runtime | Requires React/DOM/fiber/UI dependencies and source-marker model | Do not reuse code. Adapt the interaction model into renderer-neutral selection and immutable ReviewAction contracts. |

No direct code reuse occurred in this gate. Any future reuse needs an explicit
approved integration boundary, a dependency-closure inventory, source-SHA
attribution and MIT notice retention, targeted upstream-plus-thesis test
coverage, and a divergence maintenance owner.

## Synthetic technical benchmark ledger

| Family | Intended synthetic target | Result | Evidence class |
| --- | --- | --- | --- |
| B01 | basic shapes/connectors/arrowheads | `blocked_environment` | no inferred result |
| B02 | fishbone-like branches/current highlight | `blocked_environment` | no inferred result |
| B03 | mechanism groups/labels/arrows | `blocked_environment` | no inferred result |
| B04 | experimental schematic/callouts | `blocked_environment` | no inferred result |
| B05 | control/proposed symmetry | `blocked_environment` | no inferred result |
| B06 | axes/line/scatter/legend | `blocked_environment` | no inferred result |
| B07 | synthetic raster plus overlay | `blocked_environment` | no inferred result |
| B08 | image matrix | `blocked_environment` | no inferred result |
| B09 | Master/Layout/placeholder binding | `blocked_environment` | no inferred result |
| B10 | transforms/rotation/dashed paths/CJK | `blocked_environment` | no inferred result |

The block applies only to the local disposable benchmark environment. It does
not constitute a negative capability conclusion about either upstream project.

Hard rejections remain in force: open-slide is not the final renderer;
PPT Master/open-slide generic planning is not thesis narrative authority; SVG
or React cannot replace the Ledger; raster skins cannot become canonical;
there is never a second PPTX backend; no silent raster fallback; and AI cannot
recreate empirical or literature evidence.

## Answers to the architecture questions

1. **Scientific SVG IR:** yes, adapt a closed thesis-owned IR between
   specialist output and FigureCritic, starting CP5-A.
2. **Semantic SVG:** yes, but only rendering-neutral IDs/roles; provenance and
   scientific claims remain manifest/Ledger-owned.
3. **DrawingML compiler:** defer choice; inspect/adapt designs and test vectors
   first, then evaluate a minimal internal MIT-attributed adapter.
4. **One backend:** the compiler can only be an implementation detail under
   `PythonPptxAssembler`; it cannot export a parallel production deck.
5. **Capability registry:** yes, before any compiler integration.
6. **Template concepts:** explicit topology, safe reconstruction manifests,
   native-object fidelity taxonomy and static preflight improve CP3.
7. **Profile split:** defer conceptual migration. Current VisualStyleProfile,
   TemplateProfile, body composition and figure grammar already separate the
   authorities; “cleaner naming” is not a sufficient migration reason.
8. **Editor features:** stable IDs, selection, nudge/geometry, overlap picker,
   undo and annotations belong in FigureCritic/live review later.
9–10. **Current context:** adopt a manifest-bound CurrentSlideContext as listed
   above, never as scientific state.
11. **Comments:** use a separate immutable ReviewAction contract.
12. **Round trip:** defer until production generation has native acceptance.
13. **CP5 sequence:** see the attached assimilation proposal.
14. **Do not adopt:** generic strategist/create-slide planning, React/HTML/PDF
   export as the final renderer, screenshot authority, and parallel exporters.
15. **Evidence levels:** source inspection backs module findings; upstream tests
   back checker/comment claims; all B01–B10 execution claims are blocked; CP5
   sequencing is architectural inference.

```yaml
codex_report:
  phase: PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_RECONNAISSANCE
  status: awaiting_external_architecture_review
  branch: codex/thesis-deck-system
  commit_sha: pending_final_commit
  files_added:
    - thesis-deck-system/research/PHASE_3_EXTERNAL_PRESENTATION_ARCHITECTURE_RECONNAISSANCE.md
    - thesis-deck-system/designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md
    - thesis-deck-system/artifacts/phase3/external-repo-provenance.json
    - thesis-deck-system/artifacts/phase3/external-technique-assimilation-matrix.json
  files_modified: []
  files_deleted: []
  private_access_counters: [0, 0, 0]
  next_action_requested: EXTERNAL_ARCHITECTURE_REVIEW
```
