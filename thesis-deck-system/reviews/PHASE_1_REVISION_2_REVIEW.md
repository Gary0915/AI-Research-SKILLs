# Phase 1 Revision 2 — Reviewer Verdict

## Verdict

**REVISE**. Phase 2 remains unauthorized.

The revision resolves several previous blockers: the result slide now contains a real `svgBlip` relationship to the canonical SVG; A002 exists and the observation slide binds A002/E002; canonical absolute paths were largely removed; evidence source hashes are no longer placeholders; meeting delta contains B001; and Stage 1–7 QA now has more concrete execution evidence.

However, the reviewer found remaining contract and source-of-truth inconsistencies that prevent Phase 1 approval.

## Blocking findings

### P1-C1 — Template Profile layout identity is internally inconsistent

`profile_template()` builds the `layouts` array by lexicographically sorting OpenXML part paths and assigns `layout_index = len(layouts)`. This makes `layouts[1]` describe `slideLayout10.xml`, not runtime `python-pptx` layout index 1.

At the same time, `semantic_roles.photo_observation` and `semantic_roles.hero_plot_discussion` store:

- `layout_index: 1`
- `layout_path: ppt/slideLayouts/slideLayout2.xml`

The assembler uses only `layout_index`, so the build happens to resolve to runtime layout 1 / `slideLayout2.xml`, while the profile's own `layouts` table says index 1 belongs to `slideLayout10.xml`.

This means the template profile is not a self-consistent stable identity map.

Required correction:

- derive runtime layout index and OpenXML part path from the same `python-pptx` layout object;
- ensure each `layouts[]` record's `layout_index` corresponds to that exact runtime layout and `layout_path`;
- semantic-role resolution must verify both expected index and expected part path;
- broken/mismatched index/path mapping must block assembly/QA;
- do not silently use a role whose path disagrees with the resolved runtime layout.

### P1-C2 — Structural audit still does not prove slide → layout → master → semantic-role mapping

The current structural audit records generated slide → layout part, but it does **not** record:

- layout → master relationship target;
- expected semantic role for each generated slide;
- comparison of actual layout part against the Template Profile role mapping.

This was explicitly required by C7/C8.

Stage 6 currently passes on `orphan_parts`, content types, and SVG presence only. A deck with the wrong native layout could therefore still pass Stage 6.

Required correction:

- record generated slide ID/spec ID → actual slide part → actual layout part → actual master part → expected semantic role → expected role layout path/index;
- Stage 6 must fail if actual and expected mapping differ;
- add a deliberate role-mapping mismatch regression test.

### P1-C3 — Slide scientific content is not fully compiled from materialized history, and revised decision selection is wrong

`build.py` still constructs first-build content partly from fixture/bundle objects instead of the first materialized ledger state:

- first Observation content is read from `bundle["stages"]`;
- first Result/Discussion is manually built from `d1`, `bundle["decisions"][0]`, and `bundle["actions"][0]`.

This violates C5's requirement that both first and revised builds be compiled from persisted/replayed/materialized history.

More seriously, revised `state_content()` uses:

`decision = next(iter(state["decisions"].values()))`

With D001 inserted before D002, this selects D001 even after Discussion v2 points to D002. The committed revised Slide Spec confirms the bug: its Discussion is revision 2, but its displayed decision text is D001 rationale (`Trend supports the mechanism but a control is missing.`) rather than D002 rationale (`Reproducible trend remains non-discriminating.`).

Required correction:

- create a deterministic materialized-state content compiler for both first and revised builds;
- resolve Discussion `decision_ref` to the exact Decision object;
- resolve `next_step_ref` / Action ID to the exact current Action revision at the target cursor;
- Observation must also come from the materialized stage/state, not directly from the fixture bundle;
- add assertions proving first content equals first materialized state and revised content equals Discussion v2 + D002 + revised NS001.

### P1-C4 — Canonical schemas are still too shallow for the stated C2 contract

Although the schemas were improved, key nested structures remain unconstrained.

Examples:

- `slide-spec.schema.json`: `speaker_notes`, `story_visibility`, `bindings`, and `content` are still generic objects without full nested contracts;
- `deck-manifest.schema.json`: `block_ref`, Claim/Evidence/Asset/Action arrays, and profile refs are only generic objects/arrays;
- `asset-manifest.schema.json`: `generator`, `input`, `output`, `transform_chain`, and accessibility are generic structures, even though C2 explicitly required the A001/A002 provenance structures to be defined;
- `template-profile.schema.json`: `layouts`, `masters`, theme structures, and cross-consistency of semantic-role identity are not constrained sufficiently.

Schema acceptance therefore does not yet prove the semantics the report claims.

Required correction:

- define the exact Phase 1 nested structures and ID patterns used by generated artifacts;
- use `additionalProperties: false` for contract-bearing nested objects;
- require A001 data-plot provenance fields including input/script/output hashes and transform policy;
- constrain speaker-note source refs, story-visibility enums, scientific bindings, block/profile refs, and manifest ref arrays;
- add negative tests for malformed nested values, not only positive generated-artifact validation.

### P1-C5 — QA Stage 3/4/6/7 are still weaker than their owning requirements

#### Stage 3

The implementation verifies Evidence source files and only each Asset's top-level `path`/`sha256`. It does not verify the full A001 provenance chain required by C4/C9:

- input CSV hash;
- plot script hash;
- SVG output hash;
- PNG preview hash;
- transform/output consistency.

#### Stage 4

Professor QA checks `bool(bundle["meeting_projection"])`, but the build does not replace this with the actual ledger-derived `meeting-delta.json` projection before QA. Thus `previous_commitments` can pass without proving the real meeting projection carried the commitment.

#### Stage 6

As noted in P1-C2, Stage 6 does not validate semantic layout/master mapping and other relationship-aware requirements.

#### Stage 7

`finalize_visual_qa()` writes a predeclared inspection record and Stage 7 treats any non-empty `inspection_record` path as success. It does not consume and validate each inspection entry/status, expected image dimensions, or a blank-image heuristic. File size > 0 is not sufficient evidence of a valid render.

Required correction:

- Stage 3 must execute full A001/A002 provenance verification;
- Stage 4 must consume the actual ledger-derived meeting projection artifact/state;
- Stage 6 must own semantic layout/master validation;
- Stage 7 must load/validate the persisted inspection record and independently inspect render existence, dimensions, blankness/variance heuristic, montage existence, and per-generated-slide pass status.

### P1-C6 — Assembled speaker-note provenance does not follow Slide Spec bindings

`PythonPptxAssembler` hard-codes the same notes on every generated slide:

`Synthetic fixture: E001`

The Observation Slide Spec correctly binds E002, but the actual PPT notes still say E001. The assembler therefore discards `speaker_notes.source_refs` and creates a provenance mismatch between Slide Spec and PPTX.

Required correction:

- generate source notes from each Slide Spec's `speaker_notes.source_refs` and text;
- structural/content QA must verify the generated notes contain the expected source refs for each generated slide;
- Observation must contain E002; result/discussion must contain the correct E001/E003 refs.

### P1-C7 — `source_template_unchanged` is not an actual unchanged check

`audit_pptx()` sets:

`source_template_unchanged = source_hash is not None`

This is true whenever a template path is supplied and does not prove that the source template remained unchanged.

Required correction:

- either remove the misleading field, or record a pre-assembly source hash and post-assembly hash of the source template file and compare them;
- keep source template SHA and generated PPTX SHA as distinct fields.

## Items considered resolved from the previous review

The reviewer accepts the following as resolved for the bounded Phase 1 slice, subject to the corrections above remaining intact:

- canonical result SVG has a real slide relationship and slide XML reference;
- renderer compatibility copy is explicitly separate from the canonical PPTX;
- A002 is distinct from A001 and Observation binds A002/E002;
- `meeting-delta.json` now includes `B001` and prior/current action states;
- canonical path examples inspected are repository-relative;
- Evidence records no longer use all-zero source hashes;
- native PowerPoint remains honestly `blocked_environment` and is not a rejection reason for Phase 1.

## Approval gate

Phase 1 can be approved only when P1-C1 through P1-C7 are corrected and demonstrated by committed tests/artifacts. Do not begin Phase 2.