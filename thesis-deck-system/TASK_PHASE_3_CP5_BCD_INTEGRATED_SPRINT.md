# TASK — Phase 3 CP5-A Final + CP5-B/C/D Integrated Sprint

## Status

This task is **PRE-AUTHORIZED FOR CONTINUOUS IMPLEMENTATION** across four internal gates.

Reviewed implementation baseline:

`12f1860699b5d5a5b54be29d43b87596d8931dd5`

Required design authority:

`thesis-deck-system/designs/PHASE_3_CP5_BCD_INTEGRATED_SPRINT_DESIGN.md`

Machine-readable baseline:

`thesis-deck-system/artifacts/phase3/cp5-bcd-integrated-sprint-baseline.json`

Codex is authorized to implement Gate A0 → Gate B → Gate C → Gate D in one continuous milestone sprint.

**Do not stop for reviewer approval after A0, B, or C if their internal gates pass.**

Stop and request reviewer input only for a genuine fail-closed blocker or after Gate D final delivery.

---

# 1. Required reading before modification

Synchronize with `origin/codex/thesis-deck-system`, verify the branch head includes this task, then read completely:

1. `thesis-deck-system/designs/PHASE_3_CP5_BCD_INTEGRATED_SPRINT_DESIGN.md`
2. `thesis-deck-system/artifacts/phase3/cp5-bcd-integrated-sprint-baseline.json`
3. `thesis-deck-system/designs/PHASE_3_CP5_TECHNIQUE_ASSIMILATION_PROPOSAL.md`
4. `thesis-deck-system/reports/PHASE_3_CP5_A_IMPLEMENTATION_REPORT.md`
5. `thesis-deck-system/TASK_PHASE_3_CP5_A_REVISION_4.md`
6. `thesis-deck-system/REVIEW_PROTOCOL.md`
7. CP4 routing artifacts and ScientificFigureSpec/FigureProductionPlan schemas
8. CP3 `VSP003` visual style profile and its relevant QA/evidence
9. the existing repository-local Figure Skills involved in this sprint
10. committed Phase 2 synthetic Fishbone/history fixtures and any other committed non-private structured fixtures selected for acceptance.

Do not rely only on this task summary. The design file contains the normative architectural detail.

---

# 2. Preflight and scope classification

Before modification:

```text
git rev-parse HEAD
git status --short
git diff --name-status
git diff --check
```

Required:

- clean or explainable workspace;
- no unreviewed unrelated artifact diffs;
- no private source/render data;
- no CP5-E/F/G/H/I implementation already present outside reviewed scope.

Verify the reviewed baseline commit `12f1860...` is in branch ancestry.

Verify current committed baseline facts match `cp5-bcd-integrated-sprint-baseline.json` before changing candidate state.

If unrelated user-authored/unreviewed files are dirty, STOP and report exact repository-relative paths. Do not broad-reset them.

---

# 3. Sprint execution rule

The sprint has four internal gates:

```text
A0 → B → C → D → external reviewer
```

For each internal gate:

1. write RED tests first for new requirements;
2. implement only that gate;
3. run focused tests/schema checks;
4. create machine-readable gate QA/evidence;
5. verify privacy/scope locally;
6. make a checkpoint commit;
7. push and remote-verify the checkpoint when feasible;
8. persist durable local execution evidence;
9. continue automatically to the next gate if PASS.

Do **not** write `READY_FOR_REVIEW` after A0, B, or C.

Recommended checkpoint commit messages:

1. `phase3: finalize CP5-A registered validation operation`
2. `phase3: add CP5-B SVG native capability registry`
3. `phase3: add CP5-C static figure approval gate`
4. `phase3: add CP5-D structured scientific SVG directors`

Checkpoint commits are recovery boundaries, not reviewer handoffs.

---

# 4. Durable execution requirement

Long-running tests must not depend on the interactive Codex session surviving.

For each long run, use local-only durable evidence:

```text
PRE-HASH
→ exact command
→ stdout.log
→ stderr.log
→ numeric exit code
→ POST-HASH
→ completion marker
```

Do not commit local runner paths or secret/private inputs.

If a Codex session stops, inspect durable evidence before re-running completed work.

---

# 5. Gate A0 — CP5-A final registered-operation binding

## 5.1 Goal

Close the last CP5-A evidence-integrity loophole without expanding the SVG language.

Current unacceptable authoritative pattern:

```python
runner.run(lambda guard: None)
```

A generic successful callable cannot prove the approved CP5-A validation operation executed.

## 5.2 Required implementation

Implement a registered/fixed operation identity, preferably:

`CP5A_STATIC_VALIDATION_V1`

Acceptable API patterns include:

```python
runner.run_registered_operation("CP5A_STATIC_VALIDATION_V1", ...)
```

or a fixed method such as:

```python
runner.run_cp5a_static_validation(...)
```

The caller must not be able to substitute an arbitrary callback for authoritative completion.

The runner-owned registered operation must execute real synthetic CP5-A validation, including at minimum:

- CP5-A synthetic Scientific SVG corpus validation;
- frozen CP4 FigureProductionPlan validation;
- frozen CP4 ScientificFigureSpec validation;
- CP5-A static validator/profile binding checks required by the registered operation contract.

Do not duplicate the full QA system inside the runner. Reuse authoritative validation functions and return a deterministic operation result.

Authoritative private-access evidence must bind:

- `operation_id`;
- `operation_status`;
- `operation_result_hash`;
- `validation_executed`;
- execution ID;
- run ID;
- candidate hash;
- private attempt counters;
- runner-owned/sealed record identity/hash.

## 5.3 Required Gate A0 RED tests

- arbitrary no-op callback cannot produce authoritative evidence;
- arbitrary externally supplied callable is rejected/not accepted as the registered operation;
- unknown operation ID fails;
- registered operation exception/failure cannot seal completed PASS evidence;
- result/hash mutation fails finalization;
- wrong run identity fails;
- wrong candidate identity fails;
- alias/source/render guarded attempt fails;
- registered real operation produces non-empty deterministic result and accepted zero-attempt evidence.

## 5.4 Gate A0 freeze

Do not reopen CP5-A language features after this gate unless a later sprint regression proves an actual CP5-A defect.

Do not perform a full repository regression here. Run focused CP5-A/A0 tests, schema validation, candidate-state checks, and checkpoint evidence; the definitive full regression occurs after Gate D.

Continue to Gate B automatically when A0 passes.

---

# 6. Gate B — CP5-B SVG Native Capability Registry

## 6.1 Required contracts

Create versioned, closed schemas/contracts for equivalent concepts:

- `SVGNativeCapabilityRegistry`
- `SVGNativeCapabilityRecord`
- `SVGNativeTestVector`
- CP5-B execution evidence
- CP5-B QA

Exact filenames may follow repository conventions, but contracts must be registered with the canonical SchemaRegistry where appropriate.

## 6.2 Capability states

Exactly:

- `NATIVE_EXACT`
- `NATIVE_NORMALIZED`
- `VECTOR_FALLBACK`
- `RASTER_FALLBACK`
- `UNSUPPORTED`
- `UNKNOWN`

Evidence levels exactly:

- `upstream_declared`
- `source_inspected`
- `thesis_synthetic_verified`
- `native_powerpoint_verified`

Persist capability state and evidence level independently.

## 6.3 Evidence rules

- Legal Scientific SVG + native `UNKNOWN` is legal.
- Legal Scientific SVG + native `UNSUPPORTED` is still legal SVG.
- Native `UNKNOWN`/`UNSUPPORTED` does not block CP5-C/D static/SVG work.
- Missing registry identity/record is a Gate C blocker.
- Source inspection/upstream claims cannot be promoted to thesis `NATIVE_EXACT`/`NATIVE_NORMALIZED` without thesis-native evidence.
- Existing actual thesis synthetic vector relationship evidence may support only the narrowly proven `VECTOR_FALLBACK` behavior it demonstrates.
- Silent raster fallback is forbidden.
- No DrawingML compiler implementation in Gate B.

## 6.4 Required feature coverage

Registry feature IDs must cover at least:

- SVG root/viewBox;
- `g`;
- `rect`;
- `circle`;
- `ellipse`;
- `line`;
- `polyline`;
- `polygon`;
- supported `path` command subset;
- `text`;
- `tspan` and mixed CJK/Latin editable text behavior;
- `image`;
- `marker`;
- marker references;
- `clipPath`;
- clip references;
- `translate`;
- `scale`;
- `rotate`;
- `matrix`;
- stroke width/cap/join/dash;
- fill/stroke opacity;
- text anchor/baseline/font behavior;
- same-document references;
- full SVG vector fallback where existing evidence genuinely supports it.

Use feature-level granularity rather than one oversimplified state per element.

## 6.5 Synthetic test vectors

Create a canonical CP5-A-valid vector corpus exercising the registry feature set.

Each vector binds:

- vector ID;
- required Scientific SVG feature IDs;
- CP5-A profile version;
- source/canonical hash;
- expected registry coverage;
- evidence status;
- native status truth without unsupported promotion.

## 6.6 Gate B RED tests

At minimum:

- missing registry identity;
- missing feature record;
- duplicate feature ID;
- illegal state/evidence combination;
- source-inspected entry falsely promoted to thesis native exact/normalized;
- undeclared vector/raster fallback;
- silent raster fallback;
- legal SVG + native UNKNOWN passes SVG/static eligibility;
- legal SVG + native UNSUPPORTED remains legal SVG;
- illegal CP5-A SVG remains invalid regardless of registry.

## 6.7 Required Gate B artifacts

Expected equivalent artifacts:

- `artifacts/phase3/svg-native-capability-registry.json`
- `artifacts/phase3/svg-native-test-vectors.json`
- `artifacts/phase3/checkpoint-5b-execution-evidence.json`
- `artifacts/phase3/checkpoint-5b-qa.json`
- required schemas.

Create a Gate B checkpoint commit and continue automatically to Gate C on PASS.

---

# 7. Gate C — FigureOutputManifest + Static FigureCritic

## 7.1 Required pipeline

Implement the real mandatory gate:

```text
ScientificFigureSpec
→ canonical output
→ FigureOutputManifest
→ Static FigureCritic
→ APPROVED_FIGURE / FAIL / BLOCKED
```

Only `APPROVED_FIGURE` may become eligible for downstream Layout.

Raw SVG, raw director output, and unapproved manifests must not reach Layout.

## 7.2 FigureOutputManifest contract

Manifest must bind at least:

- manifest ID/version;
- figure ID/revision;
- FigureProductionPlan ref/hash;
- ScientificFigureSpec ref/hash;
- canonical output kind;
- canonical SVG/source artifact ref/hash;
- CP5-A profile ID/version;
- CP5-B registry ID/version;
- used feature IDs/capability refs;
- explicit fallback decision;
- source/evidence/provenance refs;
- style profile/style-resolution refs;
- privacy state;
- output lineage;
- critic ref/status;
- handoff state.

Scientific facts must remain references to authoritative source objects; do not copy the Ledger into the manifest.

## 7.3 Static FigureCritic

Implement deterministic executed checks for:

- FigureSpec schema and CP4 route validity;
- CP5-A SVG/static validity;
- manifest/spec/SVG identity consistency;
- physical hash consistency;
- CP5-B registry presence and feature coverage;
- declared fallback consistency;
- evidence/AI boundary;
- provenance/source closure;
- style token provenance;
- privacy leakage;
- Layout handoff gate.

Status model:

- `APPROVED_FIGURE`
- `FAIL`
- `BLOCKED`

Native `UNKNOWN` or `UNSUPPORTED` alone is not a static failure for legal SVG.

## 7.4 APPROVED_FIGURE

Create a small immutable approval identity object bound to:

- figure manifest identity/hash;
- critic report identity/hash;
- figure revision;
- approval status.

It must not be constructible as an arbitrary PASS flag without a passing executed static critic.

## 7.5 Gate C graph/handoff audit

Persist a machine-readable audit proving:

```text
raw figure → Layout
```

is forbidden, and:

```text
APPROVED_FIGURE → Layout eligibility
```

is the only legal handoff.

No Layout/PPTX generation is required or authorized.

## 7.6 Gate C RED tests

At minimum:

- manifest/spec figure-ID mismatch;
- wrong SVG hash;
- wrong spec hash;
- missing registry identity/feature record;
- undeclared fallback;
- critic PASS without executed checks;
- manually fabricated APPROVED_FIGURE;
- raw figure bypass to Layout;
- unapproved figure bypass to Layout;
- provenance mismatch;
- empirical slot bound to generated/non-evidence output;
- native UNKNOWN incorrectly causing static FAIL;
- native UNSUPPORTED incorrectly invalidating legal SVG.

## 7.7 Required Gate C artifacts

Expected equivalents:

- FigureOutputManifest schema
- Static FigureCritic report schema
- APPROVED_FIGURE schema
- synthetic positive/negative manifests
- `checkpoint-5c-execution-evidence.json`
- `checkpoint-5c-qa.json`
- graph/handoff audit.

Create a Gate C checkpoint commit and continue automatically to Gate D on PASS.

---

# 8. Gate D — Structured Scientific SVG Directors

Gate D must implement all five structured director families authorized by the design:

1. Fishbone
2. Mechanism
3. Experiment Schematic
4. Fabrication / Process
5. Fair Comparison

This is the first sprint that must produce genuinely visible scientific-diagram outputs.

## 8.1 Separate implementation ownership

Do not implement all scientific semantics as one catch-all generic diagram function.

Use separate modules/classes/functions or equivalent clearly separated implementation boundaries for each director.

A shared `vector-figure-builder` may own low-level deterministic SVG primitives only.

The shared builder must not decide:

- Fishbone hierarchy/history;
- causal mechanism truth;
- experimental controls;
- fabrication order;
- comparison fairness.

Those remain specialist-owned.

## 8.2 Director input contracts

Create closed, versioned schemas/contracts referenced by the top-level CP4 FigureSpec/manifest.

### Fishbone director input

Required equivalent fields:

- fishbone ID;
- revision ID;
- historical cursor/revision refs;
- branches with stable IDs;
- parent refs;
- branch label;
- branch status;
- current focus ref;
- prior revision/hash refs.

Validate:

- no duplicate IDs;
- no orphan parent;
- no cycle;
- focus exists;
- prior revision bytes/hash remain unchanged;
- completed/partial/failed/future branches are not deleted by rendering.

### Mechanism director input

Required equivalent fields:

- causal node IDs/labels;
- directed edges;
- known/unknown/uncertain state;
- alternative mechanism branches;
- external claim/evidence refs;
- uncertainty labels.

Do not invent causal certainty.

### Experiment schematic director input

Required equivalent fields:

- components/sample/system;
- variables;
- controls;
- instrumentation;
- measurement points;
- inputs;
- outputs;
- method/stage refs.

Do not omit controls or invent instruments/conditions.

### Fabrication/process director input

Required equivalent fields:

- ordered steps;
- material/state refs;
- state transitions;
- known/unknown conditions;
- source/provenance refs.

Unknown temperature/time/condition remains explicit UNKNOWN.

### Fair comparison director input

Required equivalent fields:

- compared groups/sides;
- explicit labels/control/baseline/proposed role;
- shared dimensions/metrics;
- scale policy;
- normalization policy where applicable.

Do not fabricate quantitative difference or visually bias one side by scale/area.

## 8.3 CP4 binding

Each director output must be bound to an approved CP4 route/spec.

If existing CP4 synthetic FigureSpecs lack sufficient director-detail fields, add separate CP5-D specialist input objects linked by stable refs/hashes rather than mutating scientific truth into SVG.

Do not silently broaden the CP4 ScientificFigureSpec with arbitrary untyped nested data.

## 8.4 Fixture/source policy

Use committed, non-private sources only.

Preferred:

- existing CP4 plans/specs;
- committed Phase 2 synthetic Fishbone revisions/history;
- committed Phase 2 synthetic scientific state;
- new explicitly synthetic director fixtures where required.

Fishbone representative fixture must demonstrate actual revision history and current-focus behavior, preferably using the existing committed FB001 family.

Do not access private PPTX exemplars.

## 8.5 CP3 style consumption

All five directors must consume `VSP003` through `visual-style-governor` or equivalent approved style-resolution path.

Persist token origin/tier:

- professor recurring;
- professor provisional;
- fallback;
- unresolved/not consumed.

Never invent material-semantic colors.

If a director uses neutral/emphasis color and does not require material identity, record that material semantic colors were not consumed.

## 8.6 Scientific SVG output

All structured vector outputs must:

- conform to the frozen CP5-A Scientific SVG language;
- canonicalize deterministically;
- preserve editable CJK/Latin text;
- use stable object IDs/semantic roles;
- use only registered SVG features;
- produce used-feature lists resolvable against CP5-B registry;
- avoid scientific provenance authority in SVG metadata.

## 8.7 CP5-C approval pipeline

Every representative output must traverse:

```text
director input
→ CP4 FigureSpec binding
→ canonical Scientific SVG
→ FigureOutputManifest
→ executed Static FigureCritic
→ APPROVED_FIGURE
```

No director may bypass this pipeline.

## 8.8 Representative and stress cases

For EACH of the five families, produce at least:

- one representative positive fixture/output;
- one stress/negative fixture family.

Required negative coverage:

### Fishbone

- duplicate branch;
- orphan;
- cycle;
- missing focus;
- historical mutation;
- failed/partial branch disappearance.

### Mechanism

- missing causal endpoint;
- unknown promoted to certain;
- fabrication chronology absorbed;
- empirical evidence replaced by conceptual mechanism.

### Experiment

- missing control;
- missing measurement point;
- invented instrument/condition;
- fabrication chronology mixed into setup.

### Fabrication

- duplicated/missing ordinal;
- unknown condition invented;
- missing state transition;
- unsourced reordering.

### Comparison

- unequal scale;
- missing side label;
- asymmetric metric set;
- visual-area bias;
- invented quantitative difference.

## 8.9 Visible preview outputs

When a deterministic SVG→PNG renderer is available, create non-gating reviewer previews.

Target at least:

- `fishbone-representative.svg`
- `fishbone-representative.png`
- `mechanism-representative.svg`
- `mechanism-representative.png`
- `experiment-schematic-representative.svg`
- `experiment-schematic-representative.png`
- `fabrication-process-representative.svg`
- `fabrication-process-representative.png`
- `comparison-representative.svg`
- `comparison-representative.png`
- `structured-director-montage.png`

Place them under a clear CP5-D artifact directory.

These PNGs are reviewer previews only.

Do NOT claim:

- CP5-F render critic PASS;
- image-capable qualitative review PASS;
- professor visual calibration PASS.

If deterministic preview rendering is unavailable, record `preview_render_blocked_environment` and continue static CP5-D validation.

## 8.10 Director Skill updates

Update repository-local Skill contracts only where implementation/handoff contracts need to match reality.

Do not publicly register Skills.

Preserve specialist boundaries and FigureCritic handoff requirements.

---

# 9. Final sprint-level validation

After Gate D implementation is complete, freeze the integrated candidate.

## 9.1 Focused suites

Run and report separate focused pass/fail counts for:

- Gate A0 / CP5-A final closure;
- CP5-B;
- CP5-C;
- CP5-D;
- cross-gate integration.

## 9.2 Schema/contract validation

Validate all new/modified schemas with Draft 2020-12 FormatChecker and recursive closure audit.

Validate generated canonical objects against exact schemas.

## 9.3 Cross-gate integration validation

Prove:

- every CP5-D output is CP5-A-valid;
- every used feature has CP5-B registry coverage;
- every representative output has a FigureOutputManifest;
- every representative manifest receives an executed CP5-C critic result;
- every accepted representative output has APPROVED_FIGURE;
- no raw director output bypasses CP5-C;
- CP3 style tokens remain provenance-bound;
- no private access occurs.

## 9.4 Definitive disposable regression

Use durable execution.

Before test:

- capture TESTED candidate hash;
- create a fresh disposable worktree with exact candidate;
- verify candidate hash equality before starting.

Run the complete CP1+CP2+CP3+CP4+CP5-A+B+C+D test collection.

Persist:

- stdout;
- stderr;
- exit code;
- tests passed;
- tests failed;
- pre-hash;
- post-hash;
- completion marker.

After completion:

- independently compute active CURRENT candidate hash;
- require TESTED == disposable POST == CURRENT;
- require tests_failed == 0.

## 9.5 Privacy

Run final authoritative repository and staged privacy scans.

Required:

- repository unexcepted findings = 0;
- staged unexcepted findings = 0;
- approved historical exceptions = 1;
- private alias/source/render attempts = `0 / 0 / 0`.

Do not open private exemplar files.

## 9.6 Repository/scope audit

Run at least:

```text
git status --short
git diff --check
```

plus exact scope audit and remote verification.

No PPTX/new template/CP5-E+ implementation is allowed.

---

# 10. Required sprint-level report

Create:

`thesis-deck-system/reports/PHASE_3_CP5_BCD_INTEGRATED_SPRINT_IMPLEMENTATION_REPORT.md`

It must include all standard REVIEW_PROTOCOL sections and additionally:

1. baseline commit and baseline CP5-A evidence;
2. internal gate commit SHAs A0/B/C/D;
3. whether any session interruption occurred and how durable evidence was reused;
4. Gate A0 operation-binding summary;
5. CP5-B registry state/evidence distribution;
6. CP5-B feature/vector coverage;
7. CP5-C manifest/critic/APPROVED_FIGURE counts;
8. CP5-C bypass/graph audit;
9. CP5-D director implementation summary by family;
10. per-family representative/stress fixture counts;
11. canonical SVG paths/hashes;
12. manifest/critic/approval paths;
13. preview paths and montage path/status;
14. CP3 style token consumption summary by origin/tier;
15. cross-gate integration QA;
16. focused test counts by gate;
17. definitive full regression count;
18. candidate tested/current hashes;
19. privacy counts;
20. CP5-E through CP5-I statuses;
21. production Group Meeting readiness = false.

Required footer:

```yaml
codex_report:
  phase: PHASE_3_CP5_BCD_INTEGRATED_SPRINT
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: <final sprint SHA>
  internal_gate_commits:
    cp5a_final: <sha>
    cp5b: <sha>
    cp5c: <sha>
    cp5d: <sha>
  files_added: []
  files_modified: []
  files_deleted: []
  artifacts: []
  render_previews: []
  tests_run: []
  tests_passed: []
  tests_failed: []
  known_failures: []
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```

---

# 11. Final truth/status constraints

At final delivery, do not claim more than:

- CP5-A final closure: implemented, awaiting integrated review;
- CP5-B: implemented, awaiting integrated review;
- CP5-C: implemented, awaiting integrated review;
- CP5-D: implemented, awaiting integrated review;
- CP5-E: `not_run`;
- CP5-F: `not_run`;
- CP5-G: `not_run`;
- CP5-H: `not_run`;
- CP5-I: `not_run`;
- render critic: `not_run`;
- image-capable qualitative review: `not_run`;
- professor visual calibration: `not_run`;
- DrawingML compiler: `not_run`;
- PPTX: `not_run`;
- template reconstruction: `not_run`;
- acceptance deck: `not_run`;
- native PowerPoint acceptance: `not_run`;
- production Group Meeting ready: `false`.

A non-gating PNG preview is not a render-critic PASS.

---

# 12. Hard prohibitions

Do NOT:

- start CP5-E/F/G/H/I;
- implement DrawingML compiler;
- create a second PPTX backend;
- generate PPTX;
- reconstruct templates;
- open private exemplars;
- use private renders;
- create real-thesis/private acceptance fixtures;
- use AI-generated imagery as evidence;
- duplicate Ledger scientific truth into SVG;
- silently rasterize unsupported vectors;
- self-certify production readiness.

---

# 13. Final delivery

After Gate D, definitive validation, final commit/push, and remote verification, return:

- repository
- branch
- sprint final commit SHA
- pushed
- remote verification
- internal gate commit SHAs A0/B/C/D
- files added/modified/deleted
- Gate A0 focused tests pass/fail
- CP5-B focused tests pass/fail
- CP5-C focused tests pass/fail
- CP5-D focused tests pass/fail
- cross-gate integration tests pass/fail
- full disposable regression pass/fail
- Gate A0 registered-operation summary
- CP5-B registry record count
- CP5-B capability state distribution
- CP5-B evidence-level distribution
- CP5-B synthetic vector count/coverage
- CP5-C manifest count
- CP5-C critic report count/status distribution
- CP5-C APPROVED_FIGURE count
- CP5-C bypass/graph audit status
- CP5-D directors implemented
- per-director representative/stress fixture counts
- per-director canonical SVG paths
- manifest/critic/approval paths
- preview/montage paths and status
- style-token origin/tier summary
- candidate-state component count
- tested/current hash/equality
- privacy scanner findings
- approved historical exception count
- private alias/source/render counters
- CP5-E through CP5-I status
- known failures
- blocked conditions
- technical debt
- deviations
- unresolved questions
- recommended next sprint.

Only after final commit, push, and remote verification write:

`READY_FOR_CP5_BCD_INTEGRATED_REVIEW: yes`

Then STOP and wait for the reviewer.
