# Task — Phase 3 Checkpoint 2 Revision 5

## Authorization

Implement only the final CP2 typography/theme-script corrections described in:

`thesis-deck-system/reviews/PHASE_3_CHECKPOINT_2_REVISION_5_REVIEW.md`

Do not begin any later Phase 3 checkpoint.

## Required corrections

### CP2-F1 — per-script run typography

Update the structural profiler so `a:latin`, `a:ea`, and `a:cs` are evaluated independently for each relevant run/default-run property set.

Requirements:

- emit deterministic separate typography observations for every present script-specific font node;
- preserve `script_role`, `theme_font_role`, `font_evidence_state`, size/weight/style, source scope, and supporting object;
- resolve `+mj-*` / `+mn-*` independently by script;
- do not let a Latin node suppress East-Asian or complex-script evidence;
- when no explicit resolvable script font exists, remain truthfully unresolved rather than inventing a family.

### CP2-F2 — supplemental theme script mappings + local theme identity

Extend sanitized theme font schemes to preserve controlled supplemental `a:font script="..." typeface="..."` entries when safe.

Requirements:

- preserve only controlled script code + safe font family + major/minor role;
- support common CJK script codes including at least Hans, Hant, Jpan, Hang when present;
- fail closed on unsafe typeface strings or malformed script codes;
- do not infer that a supplemental theme font applies to a body run without structural evidence;
- keep theme references descriptor-local or source-qualified;
- QA/future lookup code must not collapse `T001` from different exemplar descriptors into a single global theme identity.

## Required RED tests

Add tests proving at least:

1. one run with Latin + East-Asian nodes emits both observations;
2. one run with Latin + East-Asian + complex-script nodes emits three observations;
3. independent major/minor theme tokens resolve correctly per script;
4. an explicit East-Asian Unicode family survives sanitizer;
5. supplemental Hant/Hans/Jpan/Hang mappings survive as controlled metadata;
6. unsafe supplemental font family fails closed;
7. supplemental mapping alone does not fabricate a run-level resolved font;
8. two descriptors may each contain local `T001` with different values without QA/lookup collision;
9. persisted typography resolution counts exactly reconcile to persisted observations.

## Preserve

Preserve all previously accepted CP2 behavior, including privacy gates, source sessions, nested sanitizer closure, shell/body authority separation, scope-aware shell support, Master→Theme topology, direct/theme colors, group/connector geometry semantics, rotation exclusion, truthful unavailable metrics, conservative family classification, zero private renders, and disposable-worktree regression discipline.

## Private access

You may reopen only the existing three authorized aliases through the guarded CP2 flow after both pre-open gates pass. No new private source and no private render is authorized.

## Regenerate / validate

Regenerate as required:

- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`
- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

Run:

- focused CP2 tests;
- CP1+CP2 tests;
- complete Phase 1–2 + CP1 + CP2 regression in a disposable worktree;
- guarded bounded private rebuild;
- schema + FormatChecker validation;
- recursive `additionalProperties:false` audit;
- per-script typography reconciliation QA;
- supplemental-theme-font sanitizer QA;
- descriptor-local theme-reference collision QA;
- repository/staged privacy scan;
- ignored raw-root verification;
- `git diff --check`;
- remote branch/artifact verification.

## Delivery

Return:

repository:
branch:
commit SHA:
pushed:
remote verification:

report path:

files added:
files modified:
files deleted:

tests/checks run:
tests passed:
tests failed:

CP2-F1:
CP2-F2:

per-script body typography summary:
supplemental theme-font summary:
theme-reference scoping summary:
typography resolution reconciliation:

source-session attempts/success/failure:
private render counts/status:
descriptor-quality QA:
privacy scan status:
checkpoint aggregate status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_2_REVIEW: yes

Then STOP. Do not begin Professor Visual Grammar resolution.
