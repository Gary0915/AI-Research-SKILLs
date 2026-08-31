# Phase 3 CP5 C0–D0–E–F–G integrated sprint report

## Scope and checkpoint commits

| Gate | Commit | Result |
| --- | --- | --- |
| P0 | `b2bd8f2` | Integrated design, baseline, and task contract committed. |
| C0 | `499bed0` | Approval boundary, runtime handle, re-verification, and execution-owned critic checks implemented. |
| D0 | `d4197e7` | Five distinct structured semantic SVG director outputs and real mutation tests implemented. |
| E | `8fcb980` | Evidence-bound route layer implemented. |
| F | `f61b5a6` | Capability-gated render/review infrastructure implemented. |
| G | `1a00ba4` | Structural A01–A18 calibration artifacts and benchmarks implemented. |

This sprint consumed only committed/sanitized Phase 3 and CP4 contracts. It did not resolve an alias, open a private source, render a private source, create a PPTX, or start CP5-H/I.

## Traceability

### P0

The integrated task, design, and baseline make gate order, frozen inputs, explicit non-goals, and the single external-review handoff auditable.

### C0 — approval trust boundary

`StaticFigureCritic` now emits 21 execution-derived checks (C0-01 through C0-21) with facts. A persisted approval is not a layout input: it is reverified from the SVG envelope, plan/spec binding, critic report, and exact hashes before a private runtime `ApprovedFigureHandle` can be issued. CP1 FigureOutputManifest remains a lineage relationship; CP5-C’s SVG envelope, StaticFigureCritic report, approval record, and runtime handle are distinct artifacts.

The actual `VSP003` category map resolves style categories against committed token evidence. Each route stores token provenance and an application trace; unavailable category evidence is explicitly traceable rather than silently fabricated.

### D0 — semantic structured directors

Five representative outputs are materially distinct and use semantic geometry:

- fishbone: spine, branches, focus, revision/history binding;
- mechanism: causal nodes, causal/uncertain connectors, alternatives;
- experiment: sample/control/instrument/interface/input/output separation;
- fabrication: ordered process steps, material states, explicit UNKNOWN conditions;
- comparison: paired panels, shared metric treatment, parity/symmetry.

The real mutation suite changes semantic SVG/manifest fields and requires a critic rejection or altered approval outcome. The structural-distinctness artifact and montage are committed as synthetic language/contract evidence, not professor-fidelity or production figures.

### E — evidence-bound visual directors

| Route | Status |
| --- | --- |
| scientific plot | `APPROVED_FIGURE` — synthetic test evidence only, with data/provenance binding |
| photo annotation | `BLOCKED_SOURCE` |
| literature figure | `BLOCKED_SOURCE` |
| image matrix | `APPROVED_FIGURE` — synthetic test assets only |
| concept illustration | `APPROVED_FIGURE` — non-evidence only |

No blocked source was substituted, recreated, or silently downgraded into evidence.

### F — render and review infrastructure

The renderer capability probe is `blocked_environment`; no renderer is claimed. Render count is 0. Static critic is available, render critic is `blocked_environment`, image-capable qualitative review is `blocked_visual_review`, and human review is `not_run`.

`CurrentSlideContext` is transient/immutable context. `ReviewAction` is immutable, versioned review intent and does not mutate Ledger, evidence, Professor Visual Grammar, or canonical SVG.

### G — structural calibration

G writes an 18-archetype (`A01`–`A18`) structural calibration inventory, family calibration, Fishbone style profile, and reconstruction benchmark plan. Coverage is structural geometry only; style-token calibration is provisional, render calibration is `blocked_environment`, image-capable qualitative calibration is `blocked_visual_review`, and professor visual acceptance is `blocked`.

The Fishbone profile records revision/focus/history requirements. Benchmarks are not executed reconstruction claims.

## Mandatory SVG artifacts

- `artifacts/phase3/cp5d/fishbone.svg`
- `artifacts/phase3/cp5d/mechanism.svg`
- `artifacts/phase3/cp5d/experiment.svg`
- `artifacts/phase3/cp5d/fabrication.svg`
- `artifacts/phase3/cp5d/comparison.svg`
- `artifacts/phase3/cp5d/structured-director-montage.svg`
- `artifacts/phase3/cp5e/scientific-plot.svg`
- `artifacts/phase3/cp5e/image-matrix.svg`
- `artifacts/phase3/cp5e/concept-illustration.svg`
- `artifacts/phase3/cp5g/archetype-calibration-montage.svg`
- `artifacts/phase3/cp5g/figure-family-calibration-montage.svg`

No PNG was retained or required because no renderer passed the environment gate.

## Validation evidence

- Focused C0, D0, and E/F/G unit coverage: passed (the named focused executions completed with no failure).
- Cross-gate CP5-C0/D0/E/F/G contract and schema coverage: passed.
- Definitive disposable-worktree regression: `437 passed`, `0 failed`, exit code `0`.
- Test command: `python -m pytest packages/thesis-deck-system/tests -q`.
- Candidate-state identity domain: SHA-256 over the exact Git `ls-tree -r --full-tree HEAD` path/blob identity list, captured in the disposable worktree before the definitive run.
- Tested candidate hash: `80a6165429e3f3efd588c0c8d0d2e4fcc125d7100f87122395ebc8e10b9f9813`.
- Independently recomputed current candidate hash: `80a6165429e3f3efd588c0c8d0d2e4fcc125d7100f87122395ebc8e10b9f9813`.
- Candidate hash equality: pass.
- Repository privacy scan: 0 findings.
- Staged privacy scan: 0 findings.
- Approved historical exception count: 1.
- Private alias/source/render counters: `0 / 0 / 0`.
- `git diff --check`: pass before final report creation; it will be rerun before commit.

The prior two disposable executions also completed `437 passed / 0 failed`; the first lacked a durable numeric exit-code record and therefore was not used as final acceptance evidence. The definitive evidence is the final, independently hash-bound run above.

## Status and limits

Known failures: none in the definitive regression.

Blocked conditions: local SVG render capability, image-capable qualitative review, photo/literature source bindings, and all later native/PPTX work.

Technical debt: visual style application is traceable at route level, but qualitative professor-fidelity assessment is intentionally unavailable until a suitable later authorized review/calibration gate.

Deviations: none from the authorized C0–G scope.

Unresolved questions: exact CP5-H compiler capability and CP5-I native acceptance remain intentionally unaddressed.

Recommended next sprint: external review of this integrated C0–G handoff; do not start CP5-H/I without new authorization.

## Footer

Phase 3 / CP5 C0–D0–E–F–G status: implementation complete, awaiting external review.

CP5-H: not run. CP5-I: not run. Production figures: not run. PPTX: not run. Production Group Meeting ready: false.
