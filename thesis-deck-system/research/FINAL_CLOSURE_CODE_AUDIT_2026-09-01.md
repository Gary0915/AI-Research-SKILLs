# Final Closure Code Audit — 2026-09-01

## Scope and authority

This audit is a reviewer-side code/architecture analysis for the thesis-deck-system final closure. It is intentionally non-executable and does not modify production code, generated artifacts, private aliases, private sources, renders, or PPTX files.

The audit baseline is remote commit `e422c794a85cbd5e76c73fa364abd4542f524eb6` on `codex/thesis-deck-system`. The active Codex workspace may contain a newer unpushed final-composition candidate (reported as candidate hash `61813a…1b0eae`); therefore every implementation task below must first compare the current workspace against this audit and preserve newer correct work.

## Final-closure objective

The immediate objective is not to redesign the entire system. The objective is to remove correctness/reliability blockers that can invalidate the final deck or repeatedly interrupt Codex execution, while preserving all previously accepted scientific, privacy, provenance, single-backend, and fail-closed contracts.

The closure sprint must remain bounded to:

1. generated-PPTX privacy adjudication;
2. native compiler/materializer parity and style fidelity;
3. build/test reliability and inexpensive performance fixes;
4. durable validation execution with one definitive full regression;
5. final evidence/reporting.

Large architectural refactors are explicitly deferred.

## P0 findings

### FC-P0-01 — Native compiler/materializer truth mismatch

Observed baseline behavior:

- `ScientificSvgNativeCompiler._compile_object()` recognizes simple object kinds including `polyline`, `polygon`, `marker`, `tspan`, and others.
- the compiler can classify legal objects as `DRAWINGML_EMITTED`;
- `PythonPptxAssembler.add_compiled_figure()` only materializes a narrower subset and can increment `fallback_count` / skip an object after the compiler already declared it native.

Risk:

A plan can claim native DrawingML emission while the final PPTX silently omits an object. This is a release-truth defect.

Required invariant:

> Every object whose plan outcome is `DRAWINGML_EMITTED` must produce exactly one controlled native materialization record, or the assembler must fail closed. The assembler may not silently downgrade or skip an object after plan approval.

Unsupported object families must be classified as fallback before materialization.

### FC-P0-02 — Native style fidelity is incomplete

Observed baseline behavior:

The native plan carries visual fields such as fill, stroke, stroke width, dash, font family/size/weight, marker references, and transform. The assembler path visibly applies only a subset, especially for text, while native shapes can lose the source SVG visual identity.

Risk:

The PPTX may remain editable but cease to preserve the approved Scientific SVG / professor-derived visual style.

Required closure:

- define the exact supported native style subset;
- materialize each supported field into DrawingML/python-pptx;
- classify unsupported style/transform semantics as explicit fallback before the assembler;
- add plan→PPTX parity checks for geometry, fill, stroke, line width, text/font, z-order, and any supported arrows/markers.

Do not claim native fidelity for a field that is not actually emitted.

### FC-P0-03 — Sanitized template reconstruction is structurally partial

Observed baseline behavior:

`create_sanitized_native_template()` creates a fresh default 16:9 PowerPoint package. I0 then annotates a generated profile and maps several semantic roles to default layouts. The professor-resolved shell evidence contains measured recurring shell geometry/topology, but not all of it is physically reconstructed into master/layout objects.

Risk:

A report may overstate “professor template reconstruction” when the physical template is a fresh default package plus downstream explicit composition.

Required policy for this closure sprint:

- do **not** perform a large master/layout reconstruction refactor now;
- make release truth exact: distinguish `fresh_sanitized_base_template`, `professor_shell_tokens_consumed`, and `physical_professor_template_reconstruction`;
- the last state must remain `partial`/`insufficient_evidence` unless measured shell tokens are actually written into master/layout structures and validated.

A future dedicated template-reconstruction checkpoint may implement the full physical reconstruction.

### FC-P0-04 — Assembler still contains synthetic-era hard-coded composition authority

Observed baseline behavior:

The assembler directly assigns title geometry/font sizes and several recipe-specific boxes in inches.

Risk:

Backend constants can override professor profile/archetype/composition authority.

Required closure scope:

Do not rewrite the entire layout system. Instead:

- ensure the newest final-composition path consumes the authoritative composition/placement plan where present;
- prohibit new final-composition code from adding hard-coded geometry that bypasses the composition plan;
- retain legacy branches only for backward compatibility and mark them non-authoritative for the final acceptance deck;
- add an acceptance invariant that every final-composition source slide has governed placement provenance.

### FC-P0-05 — Broad SVG fallback exception can hide real defects and pollute inputs

Observed baseline behavior:

The legacy assembler uses broad `except Exception` fallback behavior for SVG picture insertion, and a compatibility path can create a PNG beside an input SVG.

Risk:

- real programming/path/permission defects can be mislabeled as renderer limitations;
- tests/builds may modify source or tracked fixture directories;
- interrupted builds can create unexplained artifact diffs.

Required closure:

- catch only a bounded decoder/format failure class or use an explicit capability probe;
- never write generated compatibility previews beside source assets;
- all transient previews must live under a caller-owned temporary/build output directory;
- add a test proving source/fixture trees are unchanged after the relevant build path.

### FC-P0-06 — Generated PPTX privacy boundary lacks artifact attestation

Current blocker:

The staged privacy gate reports `private_pptx_candidate` for generated/sanitized PPTX files because `.pptx` is conservatively classified as a candidate regardless of provenance.

Required design:

Keep the scanner fail-closed. Add a separate `GeneratedArtifactAdjudicator` or equivalent attestation boundary. A generated PPTX may be approved only if all of the following are execution-derived and candidate-bound:

1. path belongs to an allowlisted generated artifact class;
2. producer is an approved thesis-owned builder/assembler;
3. declared inputs contain no private source/alias inputs;
4. package lineage/provenance is closed and hash-bound;
5. package inspection detects no private paths/basenames/canaries/media lineage;
6. repository/staged textual privacy scans still pass;
7. raw private values are not persisted into the attestation;
8. approval cannot be caller-asserted without executed checks.

The historical exception mechanism must remain separate and unchanged.

## P1 reliability/performance findings

### FC-P1-01 — Repeated expensive builds inside tests

H/I tests repeatedly execute I0→I1→I2 pipelines in separate tests. Phase 2 integration/revision suites also rebuild expensive acceptance artifacts more than once.

Required quick win:

- introduce immutable session/module-scoped expensive fixtures where test isolation permits;
- tests consume the same frozen generated build output read-only;
- mutation tests deep-copy structured objects or use copy-on-write temp outputs instead of rebuilding the deck;
- preserve at least one explicit end-to-end rebuild test per production pipeline.

Acceptance measurement:

Run `pytest --durations=25` before and after. Persist top-duration nodes and total wall-clock values. Do not claim a speedup without measured evidence.

### FC-P1-02 — SchemaRegistry repeatedly reparses/revalidates schemas

Required quick win:

Cache parsed schemas and compiled Draft 2020-12 validators by schema path/content identity for the process lifetime. Invalidate naturally when a different file hash/path is supplied. Preserve identical validation output and FormatChecker behavior.

This change must not weaken schema closure or semantic cross-field checks.

### FC-P1-03 — Ledger materialization repeatedly replays history

`run_presentation_temporal_snapshot_qa()` can materialize the ledger for many slide cursors, and `Ledger.materialize()` replays from the beginning.

Closure-sprint policy:

Only implement a small, behavior-preserving memoization/index improvement if profiling proves it is in the slow-test hot path. Otherwise defer to a later scaling refactor.

### FC-P1-04 — Synthetic determinism and wall-clock timestamps

The Ledger appends `datetime.now()` into event identity/hash, while synthetic acceptance builds describe themselves as deterministic.

Closure-sprint policy:

Do not rewrite historical artifacts now unless required by current final-composition determinism. Record the inconsistency as technical debt unless a focused RED test demonstrates current acceptance artifacts are nondeterministic in a release-affecting way.

### FC-P1-05 — Destructive build publication

A build that deletes a canonical output root before reconstruction is vulnerable to interruption.

Required bounded fix for any final-composition rebuild path touched by this sprint:

- build into a staging/temp directory;
- validate there;
- promote only after success;
- failure/interruption must leave prior canonical outputs intact.

Do not broadly rewrite every legacy build unless needed.

### FC-P1-06 — No validation tiers / slow-test classification

Add pytest markers or an equivalent deterministic test manifest for at least:

- `fast_contract`
- `privacy`
- `build`
- `pptx`
- `render`
- `release`
- `slow`

The authoritative full regression remains the complete collected suite. Markers are for development selection and sharding only, never for excluding required release tests.

### FC-P1-07 — Full regression is coupled to one Codex process

Required execution policy:

The definitive regression may be sharded across durable processes or CI, provided:

- every shard runs against the exact same frozen candidate SHA/hash;
- the union of collected node IDs equals the authoritative complete test collection exactly once (no missing tests; duplicates explicitly identified and rejected or normalized);
- all exit codes are persisted;
- pre/post candidate hashes remain identical;
- an aggregator produces one acceptance record.

A single monolithic pytest process is not intrinsically more authoritative than complete same-candidate sharded execution.

If CI cannot be added safely in the current environment, implement a local durable validation runner instead. Do not spend the sprint debugging CI infrastructure.

## Explicitly deferred work

The following are valuable but out of scope for this closure sprint unless required to fix a P0 defect:

- broad Phase 2 / CP3 / CP5 module decomposition;
- full content-addressed BuildGraph;
- full Ledger snapshot/index architecture;
- repository-wide ProjectContext dependency injection;
- complete professor Master/Layout physical reconstruction;
- universal SVG→DrawingML support;
- native PowerPoint round-trip if the environment remains unavailable;
- Git LFS/storage migration;
- unrelated Phase 1 cleanup/refactors.

## Required closure evidence

The final implementation report must include, at minimum:

- baseline HEAD/candidate classification;
- exact files changed;
- traceability FC-P0-01 through FC-P0-06 and any implemented P1 items;
- native plan→assembler parity counts (planned native / emitted native / explicit fallback / mismatch);
- native style parity coverage by field;
- generated-PPTX attestation results and raw privacy findings;
- test duration before/after for the top 25 slow nodes where measurable;
- focused test counts;
- exact authoritative full-regression test collection count;
- full-regression execution model (single-process or shards), per-shard exit codes, union-coverage proof, and aggregate result;
- candidate pre/post/current hashes;
- repository/staged privacy findings and approved historical exception count;
- private alias/source/render counters;
- explicit release truth for template reconstruction, native PowerPoint, visual qualitative review, and production Group Meeting readiness.

## Stop conditions

Stop without commit/push if any of these occur:

- P0 native parity remains inconsistent;
- generated PPTX is approved without execution-derived attestation;
- any private alias/source/render access occurs;
- candidate changes during definitive validation;
- full-regression collection coverage cannot be proven;
- privacy has unexcepted findings;
- unrelated Phase 1 or previously accepted artifacts are modified outside the authorized dependency closure;
- a required environment capability is unavailable and the implementation would need to fake a pass.
