# Phase 0 Final Architecture Review

## Verdict

**APPROVE**

Reviewed remote branch: `codex/thesis-deck-system`

Reviewed implementation commit: `0e6c2b5d4b67fdb0c72a303a5d11d25e8006afb1`

The revised Phase 0 architecture is accepted. Codex may proceed only to the bounded Phase 1 vertical slice defined by `thesis-deck-system/TASK_PHASE_1.md`.

## Acceptance summary

The reviewer verified that the remote branch head is the reported commit and that the revised architecture addresses R1–R10.

### R1 — first-class Claim contract
Accepted. `claim.schema.json` is now first-class; `Cxxx` references must resolve, carry epistemic status, evidence links, scope, falsifiability, and revision history.

### R2 — research question / hypothesis / falsification
Accepted. Research question, problem statement, hypothesis/mechanism/prediction Claims, falsifying observations, discriminating evidence, and decision criteria are machine-addressable.

### R3 — literature synthesis
Accepted. Literature is no longer a source list. Consensus, disagreement/alternatives, known mechanisms, research gap, relevance to the observation, and implication for hypothesis/strategy are required.

### R4 — first-class Next Step
Accepted. The eighth Scientific Method stage resolves to one canonical Action Item / Next Step object. Discussion references it rather than duplicating canonical owner/timing/criteria data.

### R5 — progress/commitment management
Accepted. Prior commitment, owner, target window, actual completion, closure evidence, dependencies, blockers, parallel workstream, status, linked blocks/claims, and source decision are represented. Unfinished commitments must survive meeting cursor boundaries.

### R6 — schema-backed Scientific Method stages
Accepted. Deterministic QA fields are structured instead of inferred repeatedly from prose. Experiment variables, controls, sample/replicate plan, metrics/units, instrumentation/methods, predictions, and Go/Partial-Go/No-Go rules are represented.

### R7 — research status vs story visibility
Accepted. `research_status` and `story_visibility` are independent state machines/events. Presentation curation cannot erase scientific history.

### R8 — canonical QA/release pipeline
Accepted. The report uses one ordered pipeline:

1. schema/ledger integrity
2. scientific reasoning
3. citation/evidence provenance
4. professor-style logic
5. compile/assemble PPTX
6. structural PPTX engineering QA
7. render/montage visual QA
8. native PowerPoint round-trip acceptance
9. final deck/version audit
10. release

Repairs specify downstream rerun ranges and release is blocked by unresolved required failures.

### R9 — versioned Professor Profile
Accepted. Professor-specific narrative, meeting, density, exemplar, language, and template rules are project inputs and are versioned. Scientific correctness remains separate from preference calibration.

### R10 — Phase 1 runtime/backend boundary
Accepted. Phase 1 uses one Python control plane and one Python PPTX worker behind a backend-neutral `PptxAssembler` interface. Duplicate PPTX stacks are explicitly out of scope.

## Additional accepted architecture properties

- Append-only event-backed history is the scientific source of truth.
- Failed experiments and superseded hypotheses remain addressable and can remain visible in the main story, history, or appendix independently of research status.
- Master, meeting, and defense outputs are projections over the same ledger rather than independently rewritten truths.
- Generated contextual illustrations cannot support scientific Claims.
- Literature figures must retain original-source provenance and may not be hallucinated/recreated as evidence.
- Quantitative plots must retain data/code/output lineage.
- Mechanism/setup assets are editable vectors for final evidence-bearing use.
- Native PowerPoint layouts/masters must be profiled from actual PPTX inputs; screenshot reconstruction is not acceptable.
- Traditional Chinese is the primary project language; final font locking waits for actual template profiling.

## Remaining operational dependencies

These do **not** block the synthetic Phase 1 mechanics slice, but they **do block production Group Meeting acceptance**:

1. private/local PPTX exemplar paths: exemplars 1 and 3 for Master/template language; exemplar 2 for content composition,
2. a private/local or explicitly permitted sanitized real thesis fixture,
3. an authoritative Windows PowerPoint version/environment for native round-trip acceptance.

Phase 1 must expose these as explicit `blocked_environment` / `pending_private_fixture` conditions rather than pretending production acceptance passed.

## Phase boundary

Phase 0 is closed and approved.

Codex is authorized to implement **Phase 1 only**, according to `thesis-deck-system/TASK_PHASE_1.md` and `REVIEW_PROTOCOL.md`.

Codex must stop after the Phase 1 implementation report and wait for reviewer approval. It must not proceed to full skill catalog registration, full recipe library, production Group Meeting use, or Phase 2 automatically.
