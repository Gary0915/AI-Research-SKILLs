# Phase 2 Revision 3 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`b6595f4e672c5d5db86c0c830060c765a453d2b9`

Phase 3 is **not authorized**.

The previous P2-C1–P2-C6 correction substantially improved causal evidence roles, physical slot realization, split governance, render-pixel QA, generic H003 traversal, and persisted-ledger layout reconstruction. Those corrections must be preserved.

However, the acceptance build still contains four blocking defects that would corrupt the professor-facing append-only research history or allow the QA system to certify content that is not physically present on the slide.

---

## P2-D1 — Layer-opening slides are not temporally frozen

### Finding

The Hypothesis / Problem / Fishbone / early Scientific Method pages are still compiled from the **layer-close cursor**, after experiments, results, discussion, decision, and summary already exist.

For H002:

- `ST-EXP201` is cursor 44.
- `E201` experiment-result evidence is cursor 45.
- H002 is materialized/created at cursor 55.
- H002 Hypothesis and Problem Slide Specs use `source_cursor: 55`.
- Those opening slides bind/cite `E201` in addition to pre-existing evidence.

The visible Hypothesis text may not explicitly quote E201 today, but the historical page is not causally frozen. A later rebuild can backfill later evidence into what is supposed to represent the beginning of H002.

The same pattern exists conceptually for H001: the Hypothesis Layer is materialized only after its result/discussion/summary graph is closed.

### Why this blocks Phase 2

The professor explicitly wants research history to accumulate layer by layer. The system must be able to preserve what was known when the Hypothesis was proposed, not only what was known when the layer was later closed.

A valid layer needs at least two temporal boundaries:

1. **layer_opened** — Hypothesis / Problem / Fishbone / initial reasoning state.
2. **layer_closed or layer_revised** — Results / Discussion / Summary / Decision.

Opening slides must not bind future experiment-result evidence, actions, or decisions.

### Required correction

Introduce a layer-opening snapshot/event/revision and stage-aware Slide Spec cursor assignment.

At minimum:

- Hypothesis slide cursor <= layer-open boundary.
- Problem slide cursor <= layer-open boundary.
- Historical Fishbone slide cursor <= layer-open boundary.
- Observation/Literature/Mechanism/Solution slide cursor <= the latest evidence available before Experiment execution.
- Experiment slide cursor >= experiment definition and < result evidence.
- Result slide cursor >= corresponding result evidence.
- Integrated Discussion cursor > complete result set.
- Summary/Decision cursor > discussion/decision.
- Transition cursor > prior-layer decision + precursor evidence and < successor experiment result.

Citations and bindings must be stage-scoped, not copied from the final block-wide evidence list.

Add negative tests proving an H002 Hypothesis/Problem page cannot bind E201 or any later result evidence.

---

## P2-D2 — `combined_roles` can claim Scientific Method content that is not actually rendered

### Finding

`_compact_h02()` changes metadata without constructing a content-complete merged slide.

Examples:

1. H002 Observation page sets:

`combined_roles = [observation_problem, literature_mechanism, mechanism_solution]`

but it still hydrates as `observation_problem`, so its governed A04 slots contain only observation visual / research question / observation text. Literature synthesis, mechanism, and strategy are not physically represented.

2. H002 experiment/result page changes the semantic role to `result_comparison` and declares:

`combined_roles = [experiment_design, result_single]`

but the A11 slots contain only a control label and result figure/result label. The required Experiment metadata (IV, controlled variables, N/replicates, method, prediction, decision rule) is not physically preserved.

3. H002 Summary page declares:

`combined_roles = [layer_integrated_discussion, layer_summary_decision]`

but its A15 physical slots contain Summary/Decision content only. The Integrated Discussion fields (supporting/contradicting/non-discriminating results, cross-experiment pattern, mechanism assessment, alternatives) are not physically rendered.

Professor QA currently treats the mere presence of a name in `combined_roles` as proof that the role exists, while validating the scientific objects separately in state. This allows metadata to certify a Scientific Method stage that the audience cannot see.

### Why this blocks Phase 2

The professor requirement is presentation-visible reasoning:

Observation → Literature → Mechanism → Solution → Experiment → Results → Integrated Discussion → Summary / Decision.

State completeness is not presentation completeness.

### Required correction

Implement a **combined-role content contract**.

For every Slide Spec:

- each semantic role in `combined_roles` must declare its required presentation fields;
- those fields must map to physical slots or explicitly governed nested subregions;
- structural QA must verify that each combined role's required content is physically bound;
- Professor QA must fail if a combined role is metadata-only.

Preferred correction for the acceptance deck:

- Either stop compacting H002 and render separate Literature/Mechanism, Experiment, Result, Integrated Discussion, and Summary slides;
- Or create explicit merged archetypes whose slots are the union of the required scientific content and prove the content physically exists.

Do not use `combined_roles` as a shortcut around page generation.

---

## P2-D3 — Asset placement can silently replace required text content

### Finding

The current assembler treats a governed slot as either an asset **or** text:

- if a placement owns the slot, it inserts the image;
- the slot's structured text is not rendered.

Structural audit then considers the slot valid when either an asset is present or expected text is present.

This loses scientific content when a slot needs both a figure and a result annotation/caption.

Concrete acceptance evidence:

- `S-H001-RESULT-COMPARISON-08` has `proposed_panel = "Result｜平均導電度增加 24% ± 5% SD"` plus asset A001.
- `S-H001-RESULT-COMPARISON-09` has `proposed_panel = "Result｜訊號 CV 僅下降 4% ± 6% SD，屬 No-Go"` plus the same A001 asset.
- The committed qualitative-review artifact records **the exact same render SHA-256** for both slides.

Therefore two scientifically different Result pages render identically. The textual result distinction has been lost behind the shared plot asset.

The qualitative review even accepts this as a deliberate repeated plot, which means current visual QA does not detect semantic presentation loss.

### Why this blocks Phase 2

A slide cannot be considered provenance-correct merely because the correct SVG is physically attached. The audience must also see the Slide Spec's distinguishing scientific conclusion/annotation.

### Required correction

Introduce explicit slot composition semantics, for example:

- `content_kind: text`
- `content_kind: asset`
- `content_kind: asset_with_caption`
- nested `figure` + `annotation` subslots

A slot that has both expected asset and expected scientific text must require **both** physical bindings.

Structural QA must compare:

Slide Spec slot contract
→ expected asset binding
→ expected text binding
→ actual named shapes
→ actual geometry
→ extracted text equality/containment
→ asset relationship

Add a regression test using two Slide Specs with the same plot but different result summaries and require different PPTX text extraction and different rendered output.

The final H001 result slides must no longer be pixel-identical unless their complete visible scientific content is intentionally identical.

---

## P2-D4 — QA/report truth must include presentation-level semantic fidelity

### Finding

The current QA pipeline passes Professor QA because it validates underlying state plus role names, but it does not prove that each scientific stage is physically represented with the required content.

There is also a factual inconsistency in the implementation delivery:

- the implementation report states the H001→H002 transition is cursor **38**;
- committed QA evidence and the Transition Slide Spec use cursor **41**.

The report and canonical artifacts must not disagree on research history coordinates.

### Required correction

Add a `presentation_semantic_fidelity_qa` gate before Professor QA passes.

It must verify, per slide/combined role:

- required role fields exist in Slide Spec structured content;
- required role fields map to physical shapes;
- expected scientific text survives PPTX assembly;
- expected figure/asset survives PPTX assembly;
- no required content is displaced by an asset-only branch;
- opening-page bindings contain no later-stage result evidence;
- combined roles are actually content-complete.

The implementation report must derive key cursor facts from committed generated artifacts, not hard-code stale numbers.

Add an automated report-evidence consistency test for at least:

- H01 opening cursor
- transition cursor
- H02 opening cursor
- H02 experiment cursor
- H02 result-evidence cursor
- slide count
- generated slot count

---

## Accepted corrections that must not regress

Preserve all of the following:

- real E104 precursor evidence separate from E201;
- evidence causal-role validation;
- E201 downstream of ST-EXP201;
- no fabricated split approvals;
- real H001 Experiment Design continuation slides;
- stable `tds-slot:<slot>` physical identities;
- 44/44 current physical slot geometry conformance as a baseline;
- H003 generic Professor-QA traversal;
- persisted-ledger story/layout reconstruction;
- hierarchical/versioned Fishbone behavior;
- Hypothesis and Problem always separate;
- exact SVG-to-owning-slide relationship logic;
- repository-local Skills remain unregistered globally;
- private fixture remains `blocked_fixture` until actually available;
- native PowerPoint remains `blocked_environment` until actually available;
- Phase 3 remains unstarted.

---

## Exit criteria

Phase 2 may be approved only when all P2-D1–P2-D4 items are demonstrated by committed artifacts and negative tests.

The most important acceptance proof is no longer just:

`state is correct`

but:

`historical state at the correct cursor → Slide Spec semantic content → physical PPTX shapes → rendered audience-visible scientific meaning`

Phase 3 must not start before this review is closed.
