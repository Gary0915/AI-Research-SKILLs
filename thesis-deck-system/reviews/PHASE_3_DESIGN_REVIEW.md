# Phase 3 Design Review

## Verdict

APPROVE WITH CONDITIONS

The proposed **sanitized calibration pipeline** is the correct implementation direction for Phase 3.

It is preferred over direct-copy sanitization because it preserves privacy boundaries and avoids importing private OOXML/package parts, media, notes, relationships, or scientific content into committed artifacts. It is also preferred over simply applying measurements to the existing synthetic template because Phase 3 must demonstrate that Exemplar 1 + Exemplar 3 actually shape the formal shell and Exemplar 2 actually shapes body composition.

The following design constraints are mandatory before implementation proceeds.

## D3-1 — Sanitized native template must be reconstructed, not cleaned by copying

The proposed non-private sanitized native template must be built from sanitized measured descriptors and approved reusable shell primitives.

Do not create it by copying a private PPTX and deleting visible content.

No private package part, relationship, theme file, notes master, media, custom XML, embedded object, preview image, or unused orphan part may survive into the committed sanitized template unless independently reconstructed from sanitized metadata.

Required proof:
- package-part allowlist or reconstruction manifest;
- privacy scan over the resulting PPTX package;
- no source-private part hashes reused except intentionally public/non-private components with explicit justification.

## D3-2 — Private exemplar roles remain asymmetric

Do not average the three decks.

Authoritative roles:

- `template_primary_1` / `0825.pptx`: formal shell / Master language and secondary Hypothesis-history reference.
- `layout_exemplar_2` / `Group Meeting_20260817進度報告.pptx`: **primary body-composition / scientific-figure grammar**.
- `template_primary_3` / `口試模板.pptx`: formal shell / Master language.

The resolver must persist separate evidence showing which calibrated tokens/archetypes came from shell exemplars vs body exemplar.

## D3-3 — Raw private profiling outputs stay local-only

Raw private extraction may contain sensitive text, media names, notes, relationships, file paths, author metadata, or other identifiers.

Raw profiler output must live only in ignored local temporary storage.

Only a whitelist sanitizer may produce committed metadata.

The sanitizer must reject, not merely delete opportunistically, prohibited fields such as:
- absolute paths;
- slide text / notes;
- image/media payloads or filenames that disclose private content;
- author/company/document metadata;
- comments;
- linked/external URLs from private content;
- copied citations/literature titles;
- source filenames except stable private alias labels;
- package binary blobs.

Add negative privacy tests.

## D3-4 — Reconstruction benchmarking must separate local private evidence from committed sanitized metrics

Private source screenshots or full-slide renders may be used locally for visual comparison but must not be committed.

Committed benchmark artifacts may contain only:
- sanitized geometry descriptors;
- normalized coordinate deltas;
- layout-class labels;
- color/font/style-role deltas;
- aggregate fidelity scores;
- sanitized reconstructed slide renders containing no private source content.

Do not commit side-by-side images containing the original private slide.

## D3-5 — Visual fidelity needs measurable calibration targets

Do not treat `professor visual fidelity` as a subjective PASS only.

For each selected reconstruction/archetype, record measurable targets where applicable:
- title box position/size;
- content safe bounds;
- dominant-figure area ratio;
- text-to-figure area ratio;
- comparison symmetry;
- column widths/gutters;
- caption placement;
- callout/red-box geometry;
- image-matrix spacing;
- table/diagram proportions;
- footer/navigation alignment;
- font hierarchy;
- recurring line weights and spacing;
- fishbone branch spacing/highlight prominence.

Acceptance thresholds may vary by archetype, but must be explicit and evidenced.

## D3-6 — A01–A18 calibration must remain semantic-contract preserving

Real-exemplar calibration may change:
- geometry;
- typography tokens;
- spacing;
- visual emphasis;
- shell/layout mapping;
- visual composition rules.

It may not weaken Phase 2 scientific presentation contracts, Hypothesis/Problem separation, Fishbone history, field-level semantic completeness, or provenance rules.

Every calibrated archetype must retain a mapping to its semantic role contract.

## D3-7 — Fishbone calibration changes appearance, not research history semantics

`fishbone_calibrator` may modify visual tokens and geometry only.

It must not change:
- stable branch IDs;
- revision history;
- historical snapshot bindings;
- CURRENT/completed/partial/future semantics;
- layer-to-fishbone revision provenance.

## D3-8 — One PPTX backend remains mandatory

Continue using the approved `PythonPptxAssembler` adapter as the only assembly backend.

Profilers/reconstruction analyzers may inspect OOXML directly, but must not introduce a second deck assembly implementation.

## D3-9 — Image-capable qualitative review must be hash-bound and independently evidenced

Qualitative visual review must inspect the actual rendered candidate slide image.

Persist for each reviewed slide:
- slide ID;
- rendered image path (repository-relative for committed sanitized renders);
- SHA-256;
- reviewer/tool identity or review method;
- slide-specific observations;
- status/findings.

Do not infer qualitative visual approval from archetype metadata or layout plans alone.

## D3-10 — Native PowerPoint and production readiness remain separate gates

If native Microsoft PowerPoint is unavailable:
- Stage 8 remains `blocked_environment`;
- final production release remains blocked;
- LibreOffice remains compatibility/render QA only.

Private-exemplar profiling can still complete, but `production_group_meeting_ready` must remain false until native acceptance and the required real/sanitized thesis fixture acceptance are complete.

## Approved implementation sequence

1. Write and commit the Phase 3 design specification only.
2. Reviewer checks the design spec.
3. Create a TDD implementation plan.
4. Implement private profiler + strict sanitizer first.
5. Verify privacy gates before generating any committed private-derived profile.
6. Profile Exemplar 1/3 shell and Exemplar 2 body composition separately.
7. Build professor visual resolver and calibrated archetypes.
8. Reconstruct sanitized native template from sanitized descriptors.
9. Calibrate fishbone appearance.
10. Build reconstruction benchmarks.
11. Generate sanitized acceptance deck from existing ledger/materialized N-layer state.
12. Run structural, privacy, reconstruction, Professor, render-pixel and image-capable visual QA.
13. Report native PowerPoint status honestly.

## Current authorization

Codex is authorized **only to write and commit the Phase 3 design specification next**.

Do not begin Phase 3 production implementation until the reviewer approves that design specification.
