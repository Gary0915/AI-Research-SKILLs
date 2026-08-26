# Thesis Deck System — Codex Task Phase 0

## Mission
Build a Codex-driven thesis presentation system for a long-running master's thesis project. The system must produce and maintain a cumulative **Master Deck**, preserve failed experiments and discussion history, and generate weekly Group Meeting decks and later defense decks without rewriting the research story from scratch.

This task is **Phase 0 only**: audit the repository and propose the implementation architecture. **Do not implement the system yet.** Return an implementation report for reviewer approval first.

## Collaboration contract
- **Codex = implementer**
- **ChatGPT = reviewer/spec owner**
- Do not silently continue into the next major phase.
- For every phase, Codex must return a structured implementation report and wait for review.
- Reviewer verdicts are: `APPROVE`, `REVISE`, `REJECT`.

Because repository Issues are disabled, use the repository as the communication channel:
- Read this task file.
- Write your Phase 0 response to `thesis-deck-system/reports/PHASE_0_IMPLEMENTATION_REPORT.md` on this branch.
- Do not change unrelated files.
- For Phase 0, do not add production code or skills.

## Non-negotiable research/presentation requirements

### 1. Scientific Method is the top-level narrative contract
Every research block must support this sequence:

`Observation → Literature → Mechanism → Solution/Strategy → Experiment → Result → Discussion → Next Step`

Discussion must explicitly state:
- whether the result supports the mechanism/hypothesis,
- what assumption failed if it does not,
- what evidence is still missing,
- the next experiment/decision gate.

### 2. The deck is cumulative / append-only in research history
The professor prefers the report to grow layer by layer. Failed experiments, rejected hypotheses, superseded mechanisms, and discussion history must not silently disappear.

The system should support stable research block IDs and statuses such as:
- `active`
- `resolved`
- `failed_but_informative`
- `superseded`
- `archived_from_main_story`

Weekly meeting output should be a **view over the Master Deck / research ledger**, not a separately rewritten deck.

### 3. Visual and layout requirements
- Master/template language: white academic theme, NCKU/AMPL-style structure, based on existing laboratory templates.
- Content layout philosophy: research-dense but structured; figures dominate; text supports interpretation.
- Important recurring layouts include:
  - photo + observation
  - photo + schematic
  - control vs treatment
  - observation | mechanism | solution
  - literature + mechanism
  - hero plot + discussion
  - main microscopy image + image matrix
  - experiment matrix
  - fabrication/process flow
  - measurement setup
  - hypothesis
  - fishbone/research map
  - go/partial-go/no-go
  - timeline/to-do
  - failure analysis
  - mechanism evolution

### 4. Asset-generation policy
Do **not** use one image-generation path for everything.

Route by asset type:
- experimental quantitative data → reproducible scientific plotting (Matplotlib/SVG/PDF preferred)
- mechanism / architecture / experimental setup → editable SVG / Draw.io-style vector
- literature figures → extract original source figure with provenance; never hallucinate/recreate evidence
- decorative/context illustration → image generation is allowed
- very difficult mechanism composition → image generation may be used as a visual draft/reference, then redraw as editable vector

### 5. Expected system architecture direction
We expect a multi-skill architecture, not one monolithic PPT skill. Candidate custom skills/modules include:

- `thesis-deck-router`
- `shi-scientific-method`
- `master-deck-ledger`
- `research-block-builder`
- `evidence-card-builder`
- `mechanism-figure-director`
- `experiment-figure-director`
- `scientific-plot-director`
- `literature-figure-extractor`
- `lab-layout-director`
- `ncku-template-profiler`
- `slide-spec-compiler`
- `pptx-assembler`
- `slide-visual-qa`
- `slide-science-qa`
- `professor-qa`
- `meeting-delta-builder`
- `defense-curator`
- `deck-version-auditor`

You may rename, merge, or split these, but explain why.

### 6. Desired data model direction
A likely structure is:

```text
thesis-deck/
├── master/
│   ├── master_deck.pptx
│   ├── deck_manifest.yaml
│   └── ...
├── blocks/
│   └── B001/
│       ├── observation.md
│       ├── literature.md
│       ├── mechanism.md
│       ├── solution.md
│       ├── experiment.md
│       ├── result.md
│       ├── discussion.md
│       └── status.yaml
├── assets/
│   ├── literature/
│   ├── experiments/
│   ├── plots/
│   ├── diagrams/
│   └── generated/
├── decisions/
│   └── decision_log.jsonl
├── meetings/
├── renders/
└── changelog/
```

Do not assume this exact structure is optimal; audit and propose improvements.

## Preferred tool philosophy
The final system should be able to route to the appropriate tool at the appropriate stage, for example:
- PowerPoint assembly/editing: PptxGenJS / compatible slide tooling
- template/master inspection: PPTX/OpenXML profiling
- scientific plots: Python/Matplotlib → SVG/PDF + preview
- editable mechanism/engineering diagrams: SVG/Draw.io
- literature retrieval/extraction and citation verification
- image generation only where scientifically appropriate
- render → montage → automated QA → repair → rerender
- Git-based history/versioning

## Phase 0 deliverable — IMPLEMENTATION REPORT
Write `thesis-deck-system/reports/PHASE_0_IMPLEMENTATION_REPORT.md` with the following exact sections:

# IMPLEMENTATION REPORT

## 1. Repository audit
- current relevant directory structure
- existing skill conventions
- existing reusable orchestration/research/plotting/presentation components
- conflicts or duplication risks

## 2. Proposed architecture
- module/skill diagram
- responsibilities and boundaries
- which parts should be custom vs reused
- routing logic

## 3. Proposed repository structure
List exact directories/files you would add or modify.

## 4. Data contracts
Define proposed schemas/interfaces for at least:
- research block
- evidence card
- asset manifest
- slide spec
- deck manifest
- QA report
- decision log

## 5. Master Deck strategy
Explain how append-only research history, superseded hypotheses, failed experiments, meeting views, and defense curation will work without losing provenance.

## 6. Slide/template strategy
Explain how you will profile and preserve native PowerPoint master/layout behavior rather than flattening everything into slide images.

## 7. Figure-generation routing
Give an explicit decision tree for:
- data plot
- mechanism diagram
- experimental setup
- literature figure
- microscopy/photo
- generated contextual illustration

## 8. QA gates
Define separate gates for:
- scientific reasoning
- citation/evidence
- professor-style logic review
- visual/layout QA
- PPTX engineering QA

## 9. Test plan
Specify smoke tests, unit/integration tests, fixture files, rendering checks, and failure cases.

## 10. Risks / unresolved questions
Rank by severity and explain proposed mitigation.

## 11. Phase 1 proposal
Give the smallest implementation slice that proves the architecture end-to-end. Do not implement it yet.

## 12. Files changed
For Phase 0 this should only list the report file itself. Do not add production code.

## Required implementation-message footer
At the end of every future Codex implementation report, include this machine-readable footer so the reviewer can judge quickly:

```yaml
codex_report:
  phase: PHASE_0
  status: awaiting_review
  branch: codex/thesis-deck-system
  files_added: []
  files_modified: []
  tests_run: []
  tests_passed: []
  known_failures: []
  reviewer_questions: []
  next_action_requested: REVIEW
```

## Important
- Do not optimize for minimum effort or cost.
- Prefer scientific correctness, editability, provenance, cumulative history, and repeatability over flashy one-shot slide generation.
- Do not flatten the whole deck to PNGs.
- Do not delete failed experiments from history.
- Do not fabricate citations, literature figures, numerical data, or experimental evidence.
- Do not start implementation before returning the Phase 0 report and receiving reviewer approval.
