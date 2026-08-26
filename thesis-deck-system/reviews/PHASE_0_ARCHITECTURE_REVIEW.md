# Phase 0 Architecture Review

## Verdict

**REVISE**

The Phase 0 report is substantially strong and the overall architecture direction is approved in principle: contract-first multi-skill orchestration, an append-only event-backed research ledger, projection-based Master/meeting/defense decks, type-specific figure routing, native PowerPoint template preservation, and independent QA gates are the correct foundation.

However, several data-contract inconsistencies must be corrected before Phase 1 implementation. These are not cosmetic issues: if Phase 1 encodes the current draft literally, the system will be unable to enforce some of the professor's core research/reporting requirements.

Do **not** start Phase 1 until the report is revised and re-reviewed.

---

## What is approved

1. **Contract-first architecture over a canonical ledger** is approved.
2. **Master/meeting/defense as projections over the same research history** is approved.
3. **Failed and superseded work remains immutable/addressable** is approved.
4. **Scientific assets are routed by evidence type rather than through one image generator** is approved.
5. **Literature figures must be extracted from verified sources and may not be hallucinated/recreated as evidence** is approved.
6. **Mechanism/setup diagrams must end as editable vector artifacts** is approved.
7. **Native PPTX master/layout relationships must be preserved and tested** is approved.
8. **Scientific, provenance, professor-style, visual, and PPTX engineering QA remain separate gates** is approved.
9. **A bounded vertical Phase 1 proof before public skill registration** is approved.
10. The proposed recurring layout recipe library is directionally correct.

---

## Required revisions

### R1 — CRITICAL: add a first-class Claim contract

The report uses claim IDs such as `C001` in research blocks, evidence cards, slide assertions, QA findings, and decisions, but the proposed schema set contains no `claim.schema.json` and no explicit Claim contract.

This creates a dangling central entity and makes claim/evidence entailment impossible to validate rigorously.

Add a first-class Claim schema and include it in the Phase 1 schema set.

Minimum required fields:

- `schema_version`
- `claim_id`
- `revision`
- `claim_type` such as `observation`, `literature_synthesis`, `hypothesis`, `mechanism`, `prediction`, `result`, `discussion`, `takeaway`
- `text`
- `block_ref` and `stage`
- `scope`
- `epistemic_status` / confidence state
- `evidence_support_refs`
- `evidence_contradict_refs`
- `assumptions`
- `provenance`
- `supersedes` / `superseded_by`
- timestamps

Hypothesis/mechanism claims must be able to encode falsifiable predictions and discriminating evidence requirements.

### R2 — CRITICAL: research question and hypothesis must be first-class

The professor's reporting logic is not only a sequence of stage headings. Every block must make it explicit **which question is being answered** and **what hypothesis/mechanism is being tested**.

The current research-block example has no first-class `research_question`, and the eight-stage sequence collapses hypothesis into mechanism implicitly.

Add at minimum:

- `research_question`
- `problem_statement` or equivalent
- explicit `hypothesis_claim_refs`
- `mechanism_claim_refs`
- `predictions`
- `decision_criteria`

The Scientific Method narrative may still render as:

`Observation → Literature → Mechanism → Solution/Strategy → Experiment → Result → Discussion → Next Step`

but the underlying block contract must preserve question/hypothesis explicitly so the QA system can ask "What question does this experiment answer?" and "What evidence would falsify the hypothesis?"

### R3 — MAJOR: Literature must be a synthesis, not merely evidence references

The professor does not want a list of papers. Literature must lead to the mechanism/hypothesis/strategy.

Add structured literature-synthesis fields or a schema-backed stage contract that can represent:

- `consensus`
- `disagreements_or_alternatives`
- `known_mechanisms`
- `research_gap`
- `relevance_to_observation`
- `implication_for_hypothesis_or_strategy`
- supporting/contradicting literature evidence refs

The narrative Markdown can remain human-friendly, but these fields must be machine-addressable.

### R4 — CRITICAL: fix the eight-stage contract inconsistency around Next Step

The report states that every block has eight stages and Gate 1 checks through `Next Step`, but the research-block example's `stage_files` / `stage_state` stop at `discussion`; `next_step` is nested inside `discussion_contract`.

Choose one canonical representation and make it consistent everywhere.

Reviewer requirement: **Next Step must be a first-class structured object/stage**, not only prose inside Discussion.

It should contain at least:

- action / experiment
- rationale
- source decision reference
- success/failure criterion
- required evidence
- owner
- target date or time window
- dependencies
- `parallelizable` / workstream information
- status

Discussion may reference the selected Next Step but must not duplicate it as a second source of truth.

### R5 — CRITICAL: model professor-style progress management, not only a timeline slide recipe

The professor expects prior commitments, completion state, next actions, timing, dependencies, and parallel work to remain visible across meetings.

A `timeline/to-do` visual recipe alone cannot provide this behavior.

Add either a dedicated `action-item.schema.json` / commitment contract or make the first-class Next Step contract sufficiently complete to support:

- previous meeting action
- owner
- planned date / due date / time window
- actual completion date
- status (`planned`, `in_progress`, `blocked`, `done`, `cancelled`, `superseded`)
- blocker/dependency refs
- parallel workstream
- linked research block / decision
- result or closure evidence

`meeting-delta-builder` must project these commitments so a weekly report can answer:

1. What was assigned last time?
2. What was completed?
3. What changed or failed?
4. What is next?
5. When will the next result be available?
6. What can run in parallel?

### R6 — CRITICAL: free-form stage Markdown cannot be the only machine-readable scientific contract

The architecture claims deterministic schema validation of Scientific Method completeness, controls, replication, metrics, decision criteria, and missing evidence, while the research-block example points to free-form `*.md` stage files.

That is insufficient unless every stage has schema-backed metadata.

Use one of these acceptable patterns:

- Markdown files with validated YAML frontmatter, or
- structured `stage.yaml` / `stage.json` plus optional Markdown narrative, or
- a structured block YAML containing stage metadata plus linked narrative files.

The structured layer must be the source of truth for QA-relevant fields.

For the Experiment stage, machine-readable fields should include at minimum:

- independent variable(s)
- controlled variable(s)
- control/baseline group(s)
- sample/replicate count or explicit `unknown/not_yet_defined`
- measured outputs / metrics
- units
- instrumentation/method refs
- expected outcome/predictions
- decision thresholds / Go-PartialGo-NoGo mapping

Do not require the model to infer these repeatedly from prose.

### R7 — MAJOR: split research status from presentation visibility

The report correctly says main-story visibility is independent from existence, but it also places `archived_from_main_story` in the same status transition set as `active`, `resolved`, `failed_but_informative`, and `superseded`.

These are different dimensions.

Separate at least:

- `research_status`: `active | resolved | failed_but_informative | superseded` (extendable)
- `story_visibility`: `main | appendix | history | hidden_from_default_view`

A failed block can still be important in the main story; a resolved block can be hidden from the current meeting view. Do not conflate epistemic/research lifecycle with presentation curation.

### R8 — MAJOR: normalize QA order and the engineering/visual boundary

The report currently describes the QA order inconsistently across routing logic, the module diagram, and Gate numbering.

Define one canonical release pipeline. Preferred order:

1. schema/ledger integrity
2. scientific reasoning
3. citation/evidence provenance
4. professor-style logic
5. compile/assemble PPTX
6. structural PPTX engineering QA
7. render/montage visual QA
8. native PowerPoint open/render/round-trip acceptance for the authoritative fixture
9. final deck/version audit and release

Repairs must identify which downstream gates must rerun.

### R9 — MAJOR: make the professor rubric a versioned project input

`professor-qa` must not encode generic academic style as immutable skill logic.

Add a versioned project-level profile/rubric contract, e.g. `professor-profile.yaml` plus references. It should be independently updateable as new professor feedback is received.

For this project, the current known rubric must support at least:

- Scientific Method narrative is mandatory.
- Research is presented one logical block at a time.
- High information density is acceptable only when structured.
- Figures/diagrams dominate; text supports interpretation.
- Do not jump directly to data without the question/mechanism context.
- Literature must form hypothesis/mechanism/strategy rather than be a paper list.
- Discussion is mandatory and must update the research decision.
- Failed experiments and changed hypotheses remain traceable.
- Fishbone/research map is a persistent orientation view.
- Group Meeting includes previous commitments, current progress, next steps, and timing.
- Master Deck grows cumulatively; meeting and defense decks are projections/curations.

Visual exemplar rules are separate from scientific correctness and must be learned from the provided lab decks when available.

### R10 — MEDIUM: clarify runtime/tool boundaries before Phase 1

The proposed repository tree uses TypeScript implementation filenames while the report later prefers `python-pptx` initially and uses Python/Matplotlib for figures. The adapter idea is correct, but Phase 1 should not accidentally implement duplicate stacks.

Revise the report to specify the minimal Phase 1 runtime split explicitly. A suitable direction is:

- one orchestration/schema/ledger runtime as the canonical control plane;
- Python worker(s) for Matplotlib and, if selected for the Phase 1 fixture, PPTX/native-template manipulation;
- an explicit assembler adapter interface so a later backend can replace the PPTX implementation without changing data contracts.

Do not benchmark or implement multiple PPTX backends in Phase 1 unless the fixture requires it.

---

## Reviewer decisions on the unresolved questions

1. **Template/exemplars:** the project visual rule is already known conceptually: the first and third decks define the Master/template language; the second deck is the primary reference for content layout and figure composition. The actual PPTX files are still required as local/private fixtures before visual-fidelity acceptance. Do not invent their native layouts from screenshots.
2. **Phase 1 fixture:** Phase 1 may use a committed synthetic fixture for the mechanical vertical slice, but a private/sanitized real thesis fixture is mandatory before the system is accepted for real Group Meeting production.
3. **Native PowerPoint:** do not assume availability/version. Detect and report the environment. LibreOffice may be a secondary interim renderer; final real-template fidelity requires native Windows PowerPoint round-trip acceptance when available.
4. **Binary storage:** canonical schemas, ledger, source assets, scripts, and manifests belong in Git. Generated PPTX/PDF/render binaries are build/release artifacts by default; do not make them the canonical history. Do not commit private lab templates without explicit permission.
5. **Language/fonts:** treat Traditional Chinese as primary presentation language with English technical terminology as needed. Do not hard-code final fonts before profiling the real template; record required/fallback fonts in the approved template profile.
6. **Professor calibration:** create the rubric as a versioned project input now using the known requirements above; later calibrate visual thresholds against the real exemplar decks and reviewer annotations.

---

## Required Phase 0 revision

Update `thesis-deck-system/reports/PHASE_0_IMPLEMENTATION_REPORT.md` in place. Do not add production code.

The revised report must:

- incorporate R1–R10;
- update the architecture/repository structure/data contracts/QA/Test Plan/Phase 1 proposal consistently;
- add Claim and action/next-step contracts to the proposed schema set;
- resolve the eight-stage `Next Step` inconsistency;
- explicitly represent research question and hypothesis;
- make stage QA fields schema-backed rather than prose-only;
- separate research status from story visibility;
- normalize QA ordering;
- define the professor profile as a versioned project input;
- state the Phase 1 runtime/backend boundary;
- keep Phase 1 bounded and synthetic/private-fixture based;
- continue to stop before production implementation.

### Acceptance criteria for the revised report

The next review will return **APPROVE** only if all of the following are true:

- no dangling `Cxxx` claim references exist without a Claim contract;
- `research_question` and explicit hypothesis refs are first-class;
- Literature synthesis is structured;
- `Next Step` is represented consistently as a first-class structured object/stage;
- schedule/commitment data can generate a real weekly To-Do/timeline view;
- Experiment metadata is machine-validatable;
- research status and story visibility are separate dimensions;
- one canonical QA pipeline is stated everywhere;
- professor profile/rubric is versioned and project-specific;
- Phase 1 implementation scope reflects these corrections.

**Reviewer verdict: REVISE**
