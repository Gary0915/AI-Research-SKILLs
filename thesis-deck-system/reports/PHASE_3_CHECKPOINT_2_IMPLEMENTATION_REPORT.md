# Phase 3 Checkpoint 2 — Implementation Report (Revision 5)

## 1. Objective completed

Corrected CP2-F1 and CP2-F2 only: per-script typography extraction, controlled
supplemental theme-script font metadata, descriptor-local theme identity, and
execution-derived owning QA. No Professor Visual Grammar Resolver,
VisualStyleGovernor calibration, A01–A18 calibration, production Figure Skills,
template reconstruction, reconstruction benchmark, acceptance deck, Phase 4,
or public/global Skill registration was started.

## 2. Architecture decisions

- A DrawingML text run now emits one observation for each present direct
  `latin`, `east_asian`, and `complex_script` node. Observations share the
  supporting object when appropriate but have deterministic unique IDs.
- Major/minor theme-font tokens are resolved per script only through the
  bound descriptor-local theme scheme. Missing direct evidence remains
  `theme_font_unresolved` or `inherited_unresolved`; supplemental mappings are
  never guessed onto a run.
- Supplemental Office script mappings use a finite controlled code set and a
  strict safe-font policy. They preserve only role, script code, and family.
- Theme IDs remain local to a sanitized descriptor. QA uses descriptor-qualified
  theme collections rather than a global `T001` lookup.
- All new CP2-F checks derive from persisted descriptors and execution evidence;
  none is a literal PASS.

## 3. Files changed

Modified:

- `packages/thesis-deck-system/src/thesis_deck_system/phase3_checkpoint2.py`
- `packages/thesis-deck-system/tests/unit/test_phase3_checkpoint2.py`
- `thesis-deck-system/schemas/sanitized-shell-structural-descriptors.schema.json`
- `thesis-deck-system/schemas/sanitized-body-structural-descriptors.schema.json`
- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`
- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

Added: none. Deleted: none.

## 4. Behavior implemented

### CP2-F1 — per-script typography observations

`_slide_profile()` no longer uses a first-match lookup. It independently reads
direct `a:latin`, `a:ea`, and `a:cs` children for every applicable run/default
run property set, emitting one typed observation per present script. Each keeps
script role, family, theme-font role, evidence state, size, weight, style,
source scope, and supporting object. A run with no direct script node remains
truthfully inherited-unresolved and does not invent a family.

### CP2-F2 — supplemental theme script-font metadata

The theme profiler now preserves safe controlled supplemental mappings from
`a:font` for major/minor theme roles. The allowlist includes `Hans`, `Hant`,
`Jpan`, `Hang`, and other finite Office script codes. The sanitizer constructs
these records anew and rejects unsafe families or unapproved script codes.
Supplemental mappings remain reference evidence; they cannot by themselves
resolve an East-Asian body run. Descriptor-qualified theme lookup prevents a
local `T001` in one exemplar from colliding with another descriptor's `T001`.

## 5. Commands/tests run and results

- RED: `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint2.py -q`
  — 9 expected failures before the CP2-F1/F2 implementation.
- Focused GREEN: `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint2.py -q`
  — **66 passed**.
- `python -m pytest packages/thesis-deck-system/tests/unit/test_phase3_checkpoint1.py packages/thesis-deck-system/tests/unit/test_phase3_checkpoint2.py -q`
  — **130 passed**.
- Disposable detached worktree complete suite:
  `python -m pytest packages/thesis-deck-system/tests -q` — **230 passed,
  0 failed**. The first run was blocked only by that temporary worktree's Git
  safe-directory policy; the same suite was rerun with a process-local Git
  safe-directory setting and completed successfully.
- Guarded bounded authorized-alias rebuild — aggregate `pass`; it produced no
  private render.
- Draft 2020-12 schema plus FormatChecker validation — zero errors for all
  committed CP2 descriptor/QA artifacts.
- Recursive `additionalProperties: false` audit — zero unclosed object nodes.
- Persisted per-script count reconciliation, supplemental sanitizer closure,
  descriptor-local theme-reference QA, repository/staged privacy scan, ignored
  raw-root verification, and `git diff --check` — run before delivery.

## 6. Artifacts produced

- `thesis-deck-system/artifacts/phase3/sanitized-exemplar-manifest.json`
- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

No PPTX, PNG, private render, montage, screenshot, private media, private text,
or private path was committed.

## 7. Visual QA evidence

Private render counts created/deleted/retained are **0 / 0 / 0**.
Private qualitative review remains `blocked_visual_review`; no visual PASS is
derived from metadata or provider capability.

## 8. Scientific/provenance QA evidence

The production empirical Observation policy remains passed. CP2-F1/F2 changes
only sanitized visual-structural typography evidence and do not modify the
approved ledger, claims, evidence cards, Research Blocks, source cursors,
Hypothesis Layer history, Fishbone versions, or Phase 1–2 provenance.

## 9. Descriptor and execution evidence

- Source sessions: **3 attempts / 3 successful closed / 0 failed**;
  unauthorized attempts: **0**.
- Body typography: **211** observations: Latin **209**, East-Asian **0**,
  complex-script **2**. The zero East-Asian count is the truthful structural
  result for this bounded run; it is not inferred from theme supplemental
  mappings. All body observations use `slide_body`.
- Supplemental theme-font records: **54** in the body descriptor; **204** in
  each shell descriptor. These records are controlled metadata only.
- Descriptor-quality QA: **27/27 pass**, including
  `CP2-DQ-PER-SCRIPT-TYPOGRAPHY`,
  `CP2-DQ-TYPOGRAPHY-COUNT-RECONCILIATION`,
  `CP2-DQ-SUPPLEMENTAL-THEME-FONT-CLOSURE`, and
  `CP2-DQ-DESCRIPTOR-LOCAL-THEME-IDENTITY`.
- Checkpoint aggregate status: `pass`.
- Privacy scan: one approved historical legacy exception, zero unexcepted
  findings, and zero staged findings.

## 10. Known failures / technical debt

- `blocked_visual_review` remains expected: no authorized private
  image-review-provider/render operation was performed.
- Native PowerPoint acceptance, Professor Visual Grammar resolution, and every
  later Phase 3 checkpoint remain unauthorized.
- The local ignored raw-profile root contains only local execution state and
  requires the already-specified final Phase 3 cleanup.

## 11. Unrelated regression artifact cleanup

- Phase 1 generated artifacts detected: 38
- verified generated-only: 38
- restored from HEAD: 38
- unsafe/unclassified: 0
- visual-inspection.json included: yes
- CP2 scoped changes preserved: yes

## 12. Deviations from reviewer prompt

None. The disposable-worktree safe-directory limitation was an environment
constraint; it was handled with a process-local Git configuration and did not
change repository configuration, code, or test expectations.

## 13. Questions requiring reviewer decision

None. Reviewer approval is required before Professor Visual Grammar resolution.

## 14. Recommended next phase

Stop at Checkpoint 2 Revision 5 and await review.

```yaml
codex_report:
  phase: PHASE_3_CHECKPOINT_2
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: <sha-or-null>
  files_added: []
  files_modified:
    - packages/thesis-deck-system/src/thesis_deck_system/phase3_checkpoint2.py
    - packages/thesis-deck-system/tests/unit/test_phase3_checkpoint2.py
    - thesis-deck-system/schemas/sanitized-shell-structural-descriptors.schema.json
    - thesis-deck-system/schemas/sanitized-body-structural-descriptors.schema.json
    - thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json
    - thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json
    - thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json
    - thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md
  files_deleted: []
  artifacts:
    - thesis-deck-system/artifacts/phase3/sanitized-exemplar-manifest.json
    - thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json
    - thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json
    - thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json
  render_previews: []
  tests_run:
    - focused CP2 tests
    - CP1 plus CP2 tests
    - complete Phase 1–2 plus CP1 plus CP2 disposable-worktree regression
    - guarded bounded production-private rebuild
    - schema and FormatChecker validation
    - typography reconciliation and supplemental-theme-font QA
  tests_passed:
    - 66 focused tests
    - 130 CP1 plus CP2 tests
    - 230 full regression tests
  tests_failed: []
  known_failures:
    - private qualitative review blocked_visual_review
    - native PowerPoint and later Phase 3 work remain unauthorized
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```
