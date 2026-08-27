# Phase 3 Visual Fidelity Design — Final Reviewer Verdict

## Verdict

**APPROVE**

Reviewed design commit: `e56e679b28fbe3bf1e077aa32ec8ec0687f6b45c`

The design is approved as the authoritative Phase 3 architecture for professor visual-fidelity calibration.

This approval authorizes creation of a **separate TDD implementation plan only**. It does not yet authorize production implementation.

## Why the design is approved

The design correctly preserves all approved Phase 1–2 scientific, temporal, provenance, Hypothesis-Layer, Fishbone, presentation-semantic, and single-backend invariants while adding a separate visual-calibration layer.

The following design choices are specifically approved:

1. **Two-domain privacy architecture**
   - private local profiling domain;
   - fail-closed sanitizer boundary;
   - committable sanitized descriptor domain.

2. **Asymmetric exemplar authority**
   - Exemplar 1 + Exemplar 3 govern the formal shell/template language;
   - Exemplar 2 governs primary body composition/scientific figure layout;
   - no generic averaging of all three decks.

3. **Descriptor-based native template reconstruction**
   - no copy-and-clean of private PPTX packages;
   - no reuse of private OOXML package parts;
   - reconstructed package generated from sanitized descriptors through the existing `PythonPptxAssembler` adapter boundary.

4. **Fail-closed whitelist sanitizer**
   - new sanitized objects are constructed from typed allowlisted selectors;
   - unknown fields and prohibited content fail the complete sanitization step.

5. **Private/local reconstruction benchmark evidence**
   - private reference renders remain local;
   - committed benchmark evidence is sanitized numeric/controlled metadata only.

6. **Measured visual-fidelity thresholds**
   - geometry, title, figure/text ratio, gutters, callouts, typography, colors, Fishbone stability and focus prominence are measurable;
   - global pixel similarity cannot independently certify fidelity.

7. **A01–A18 semantic preservation**
   - Phase 3 may calibrate geometry, style, hierarchy and native layout mapping;
   - Phase 2 scientific semantic contracts remain immutable.

8. **Fishbone visual-only calibration**
   - stable branch IDs, historical revisions, Hypothesis-Layer bindings and temporal provenance remain unchanged.

9. **Hash-bound image-capable review**
   - qualitative visual PASS requires actual rendered-image inspection;
   - metadata-only review cannot produce PASS.

10. **Native PowerPoint / production-readiness separation**
    - Stage 8 remains independent;
    - production Group Meeting readiness remains false without native acceptance and the later permitted real scientific fixture gate.

## Implementation-planning conditions

The TDD implementation plan must preserve the design exactly and explicitly address the following reviewer conditions.

### P3P-1 — Data minimization inside the private domain

The profiler should collect/store the minimum private information needed for visual measurement and privacy-canary checks.

Full raw slide text, notes, URLs and media should not be persisted merely because the raw model permits them. Prefer:

- ephemeral inspection;
- local one-way canary hashes/tokens where sufficient;
- geometry/style extraction without content retention.

If full private text/media must be persisted locally for a specific classifier/reviewer step, the plan must identify the exact owning step, retention scope, cleanup behavior and reason.

### P3P-2 — Private alias/hash handling

Committed artifacts may contain only the stable private alias URI and the approved source SHA-256/profile ID fields. Absolute paths, basenames and local diagnostic values remain local only.

The plan must include a repository-wide scan proving this.

### P3P-3 — Exemplar-2 shell contamination prevention

The implementation plan must add explicit tests proving Exemplar 2 cannot leak its own header/footer/master shell into the resolved formal template.

Exemplar 2 may influence only authorized body-composition token families.

### P3P-4 — Exemplar-1/3 conflict evidence

Every resolved shell token that has competing Exemplar 1/3 measurements must persist:

- selected token value;
- winning source role;
- losing alternative descriptor;
- conflict rule ID;
- blocking/non-blocking classification.

The plan must include hard-conflict negative tests.

### P3P-5 — Reconstruction package non-reuse proof

The plan must demonstrate that the sanitized template is a fresh package, not a cleaned private package.

Required evidence must include:

- reconstruction manifest coverage;
- allowed-part family audit;
- orphan/external relationship audit;
- generic metadata audit;
- local private-part hash non-reuse comparison;
- zero copied private binary/package parts.

Only aggregate/status evidence from private part-hash comparison may be committed.

### P3P-6 — Reconstruction benchmark role coverage

Benchmark selection must cover representative visual families, not only easy slides.

At minimum plan benchmarks for:

- formal shell/content page;
- Hypothesis/Problem shell;
- photo + schematic or equivalent figure-first body layout;
- Control vs Proposed/comparison;
- result + discussion;
- image matrix if direct evidence exists;
- Fishbone/research-history page where supported.

If a required family lacks real exemplar evidence, mark it `insufficient_evidence` rather than fabricating a benchmark.

### P3P-7 — Metric definition precision

The implementation plan must specify how each quantitative fidelity metric is computed, including coordinate normalization, edge/IoU rules, area calculation, font comparison, and color-space conversion where used.

For CIEDE2000, define the color conversion/reference assumptions rather than leaving the metric underspecified.

### P3P-8 — Image-capable review availability

The plan must identify the actual image-capable review mechanism available to the implementation environment.

If no such reviewer is available at execution time, the corresponding gate must be `blocked_environment` or `blocked_visual_review`; the system may not generate a qualitative PASS from metadata or pixel heuristics alone.

## Scope boundary

Design approval does **not** authorize:

- implementing the profiler/sanitizer/resolvers;
- reading private exemplars for production profiling beyond planning validation;
- generating sanitized profiles;
- reconstructing the template;
- calibrating A01–A18;
- generating the Phase 3 acceptance deck;
- starting Phase 4;
- globally registering Skills.

The next authorized artifact is only a TDD implementation plan.

## Required next artifact

Create:

`thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`

The plan must map every design section and P3P-1–P3P-8 condition to:

- implementation modules/files;
- schemas/contracts;
- red tests;
- green implementation milestone;
- generated evidence/artifacts;
- privacy boundary;
- stop/go criteria;
- rollback/failure behavior;
- dependencies between implementation phases.

Reviewer status: **DESIGN_APPROVED_PLAN_ONLY**
