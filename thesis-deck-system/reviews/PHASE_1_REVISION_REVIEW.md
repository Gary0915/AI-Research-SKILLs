# Thesis Deck System — Phase 1 Revision Review

## Verdict

**REVISE — Phase 1 is not yet approved. Phase 2 remains unauthorized.**

Reviewer inspected remote branch `codex/thesis-deck-system` at Codex delivery head:

`c043599ef76c1d26371ed33307b1380ef65960bc`

The second implementation is materially better: the committed Stage/Evidence/Decision fixture exists, persisted ledger records now contain hashes, Slide Specs/manifests are persisted, Discussion v2 is present, and the build produces PPTX/render artifacts. However, several P1-R requirements are still only superficially satisfied. The current artifacts can report PASS while violating the explicit Phase 1 contracts.

## Approved progress

The following direction is retained:

- one Python control plane and one PPTX backend;
- committed B001 Stage/Evidence/Decision directories;
- persisted append/hash ledger records;
- first/revised snapshots and Slide Specs;
- Discussion v1/v2 and D001/D002;
- Matplotlib plot source and generated SVG/PNG;
- native PowerPoint acceptance honestly remains `blocked_environment`.

Do not rewrite these parts without need.

## Blocking findings

### P1-B1 — Vector requirement is still not satisfied (`P1-R6`, `P1-R8`)

`PythonPptxAssembler` attempts to insert the SVG, catches decoder failure, and inserts the PNG preview into the result slide. It then writes `ppt/media/plot-canonical.svg` into the ZIP as a detached package part.

`audit_pptx()` declares `vector_media_used=true` merely when **any** `.svg` exists under `ppt/media/`, regardless of whether the result slide has a relationship to that SVG.

This violates the explicit contract:

- the result slide must actually use/reference vector media;
- Stage 6 must fail if the slide uses only PNG;
- structural audit must identify slide → media relationship.

A detached SVG stored in the PPTX ZIP is provenance storage, not vector use.

### P1-B2 — The required schema strengthening was not implemented (`P1-R12`)

`FormatChecker` was enabled, but the actual schema files remain shallow. Examples:

- `slide-spec.schema.json` does not define the committed `content` property despite `additionalProperties: false`;
- nested `placements`, `bindings`, `story_visibility`, profile refs and IDs remain weakly typed/unconstrained;
- `deck-manifest.schema.json` does not constrain per-slide records or ordinal uniqueness/sequencing;
- `template-profile.schema.json` does not constrain semantic-role/layout structures;
- patterned IDs still exist without explicit string type in several schemas;
- generated A001 now contains `input` and `output`, which are not represented by the old Asset Manifest schema.

Therefore several committed Phase 1 artifacts would fail if actually validated by the schemas they claim to conform to.

### P1-B3 — Canonical absolute paths still exist (`P1-R10`)

Canonical repository artifacts still contain machine-specific paths. Examples include:

- `slide-specs-revised.json` → `content.observation_visual_path = D:\\Gary\\...`;
- `plots/A001.asset.json` → top-level `path` and `preview_path = D:/Gary/...`.

The revision contract requires canonical YAML/JSON to contain repository-relative POSIX paths only. Runtime-local paths must not leak into canonical records.

### P1-B4 — QA Stages 1–7 are still not strong enough to justify PASS (`P1-R3`, `P1-R4`)

The revised `run_pipeline()` is better than the original status template, but key gates are still placeholders:

- Stage 1 checks `not semantic_findings(bundle)`; it does not execute SchemaRegistry validation of all canonical build artifacts and does not use the supplied `ledger` argument to load/replay/verify persisted history.
- Stage 3 checks only one generated-context condition and does not verify Evidence/Asset source file existence or recorded hashes.
- Stage 4 professor checks are too weak: `question_before_data` is only `bool(research_blocks)` rather than verifying a research question; `photo_visual` only checks that placements exist; `hero_content` only checks Discussion rather than plot + Discussion + decision + Next Step.
- Stage 5 is `bool(specs)` rather than evidence that validated Slide Specs were assembled into the expected PPTX.
- Stage 7 trusts an injected `{status: pass}` record rather than checking the committed render files/dimensions/counts and a persisted human-inspection record.

Because these checks are weak, `qa-report.json` reports Stages 1–7 PASS even while schema/path/vector/provenance violations remain.

### P1-B5 — The end-to-end deck is still not driven by materialized ledger state (`P1-R2`, `P1-R11`)

The revision task explicitly required the reloaded/materialized ledger state or projection to drive the deck build. Current `build.py` still hard-codes scientific presentation content in local dictionaries:

- `obs = {...}`
- `res = {...}`
- `res2 = {...}`

These strings duplicate Stage/Decision/Action truth rather than compiling from `materialized-first.json` / `materialized-revised.json`.

Likewise `meeting_delta.json` is manually augmented with `md.update(...)` instead of deriving the full previous/current commitment view from ledger history.

This creates two sources of scientific truth and can allow PPT content to drift from the ledger.

A visible symptom is `changed_block_ids: []` even though Discussion B001 changed after the cursor. `meeting_delta()` looks for `payload.block_id`, while persisted `stage_revised` records carry `payload.block_ref.block_id`.

### P1-B6 — Semantic layout-role resolution can silently fall back (`P1-R5`, `P1-R8`)

Template profiling stores semantic role tokens such as `slideLayout1` / `slideLayout2` from OpenXML part names. The assembler compares those tokens against `python-pptx` `SlideLayout.name`, which normally represents the human layout name. If no match is found, it silently falls back to `prs.slide_layouts[1]`.

That does not prove recipe → Template Profile → native layout resolution.

The resolver must use a stable identity actually shared between the profile and python-pptx/OpenXML (e.g. layout index + partname/relationship), and a missing mapping must block rather than silently fall back.

### P1-B7 — Observation visual asset identity/provenance is incorrect (`P1-R5`, `P1-R7`, `P1-R9`)

The observation Slide Spec points to `observation_visual.svg`, but its placement/binding uses `asset_id: A001`. A001 is the **data plot** asset.

There is no distinct committed Asset Manifest for the observation visual. As a result, the observation slide’s Asset binding is semantically wrong even though its Evidence binding is E002.

Create a distinct observation asset (e.g. A002) with correct source Evidence/provenance/hash and bind `photo_observation` to it.

### P1-B8 — Evidence provenance hashes are placeholders (`P1-R9`, Stage 3)

Committed E001/E002/E003 use all-zero SHA-256 values. Stage 3 still passes because it does not verify them.

Required correction:

- E001 hash must match committed `measurements.csv`;
- E002 hash must match the committed observation source;
- E003 should point to a separate committed synthetic literature source/note with a real hash. Avoid self-referential hashing of E003 itself.
- generated A001 must be validated against real CSV/script/SVG/PNG hashes.

### P1-B9 — Structural audit is materially incomplete/misleading (`P1-R8`)

Current structural audit reports package-level properties but does not prove the requested relationship graph:

- generated slide → native layout;
- layout → master;
- generated slide → media part(s), with media type;
- expected semantic layout role;
- result slide → SVG specifically;
- source template hash before assembly versus generated output hash after assembly.

`source_template_hash` currently hashes the generated PPTX path, not the source template. `vector_media_used` is package-presence only. Both names therefore overstate what was checked.

## Required state before Phase 1 can be approved

The next correction must demonstrate all of the following from committed artifacts and tests:

1. Every canonical Phase 1 schema validates the exact committed/generated records that claim to implement it.
2. Negative schema tests reject wrong types, extra canonical fields, absolute paths, invalid nested bindings and duplicate ordinals.
3. The result slide has an actual OpenXML relationship to the canonical SVG; a detached SVG does not count.
4. Structural audit reports the exact media relationship used by each generated slide.
5. Recipe layout roles resolve through a stable Template Profile identity and never silently fall back.
6. Observation visual has its own Asset ID/Manifest and correct Evidence binding.
7. Evidence and Asset hashes are real and verified against files.
8. All canonical JSON/YAML paths are repository-relative POSIX paths.
9. Slide content is compiled from reloaded/materialized ledger state, not duplicated hard-coded scientific strings in `build.py`.
10. Meeting delta derives the prior/current action and changed B001 directly from history; `changed_block_ids` includes B001 for the Discussion revision.
11. QA Stages 1–7 execute the owning checks and persist concrete evidence/results, not generic PASS messages.
12. Stage 8 may remain `blocked_environment`; no production release is required for Phase 1.

## Reviewer decision

`REVISE`

Do not begin Phase 2. Do not register public skills. Do not use this build for production Group Meeting acceptance yet.
