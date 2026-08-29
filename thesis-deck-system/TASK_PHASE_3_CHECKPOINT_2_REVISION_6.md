# TASK — Phase 3 Checkpoint 2 Revision 6

Authorization: **CP2 correction only**.

Do not begin Professor Visual Grammar Resolver, VisualStyleGovernor calibration, A01–A18 calibration, Figure Skill production, template reconstruction, reconstruction benchmark, acceptance deck, Phase 4, or public/global Skill registration.

## CP2-G1 — truthful unresolved script evidence

When a text run/default-run property set has no direct `a:latin`, `a:ea`, or `a:cs` typeface node, do **not** fabricate `script_role = latin`.

Add a controlled script state such as:

- `latin`
- `east_asian`
- `complex_script`
- `unspecified`

Use `unspecified` for inherited typography when script identity is not structurally established.

Optional safe enhancement: use DrawingML `lang` / `altLang` only through a finite controlled mapping to a script class. Do not inspect/export text content and do not persist arbitrary language strings.

Requirements:

1. Explicit `a:latin` remains Latin.
2. Explicit `a:ea` remains East-Asian.
3. Explicit `a:cs` remains complex-script.
4. Multiple explicit nodes remain multiple observations.
5. No direct script node -> `unspecified` unless controlled structural language metadata supports a script class.
6. `inherited_unresolved` remains truthful; do not guess family.
7. Typography counts must report `unspecified` separately.
8. `FONT-FIDELITY` must not count `unspecified + inherited_unresolved` as resolved evidence.
9. Sanitizer/schema/QA must accept only controlled script states.

Required RED tests include:

- absent script node is not Latin;
- absent node emits `unspecified` inherited evidence;
- explicit Latin/East-Asian/complex nodes remain independent;
- optional controlled `lang` mapping, if implemented, cannot accept arbitrary strings;
- persisted count reconciliation includes `unspecified` exactly.

## CP2-G2 — theme reachability / active-theme evidence

A PPTX may contain theme parts that are not referenced by an active Master/slide. Do not let those theme parts become active professor-style evidence merely because they exist in the ZIP.

For every sanitized theme profile preserve resolver-safe usage evidence, for example:

- `usage_state = referenced | unreferenced`
- `supporting_master_ids`
- `supporting_slide_ids` where applicable

or an equivalent strongly typed representation.

Requirements:

1. Master→Theme topology determines shell-theme reachability.
2. Slide→Theme topology determines body-theme reachability.
3. Every theme profile is either demonstrably referenced or explicitly unreferenced.
4. Unreferenced themes may be retained for audit but must be marked non-authoritative/reference-only.
5. Unreferenced theme palette/font/supplemental mappings cannot count as recurring professor grammar evidence.
6. Supplemental mappings must be explicitly reference metadata; they do not imply run usage.
7. Descriptor-local theme IDs remain compound/source-qualified in QA/lookup.
8. Active-theme QA must derive from actual topology, not list presence.

Required RED tests include:

- package with T001 referenced and T002 orphan -> T001 referenced / T002 unreferenced;
- orphan theme cannot satisfy active-theme professor-style evidence;
- supplemental font map on orphan theme remains reference-only;
- Master/slide topology to unknown theme fails;
- two descriptors with local T001 still remain isolated;
- active-theme counts reconcile with topology.

## Owning QA

Add execution-derived checks for at least:

- script-unspecified truth;
- per-script/unspecified count reconciliation;
- no fallback-Latin behavior;
- theme reachability closure;
- active vs unreferenced theme classification;
- supplemental-font reference-only behavior;
- descriptor-local theme identity;
- schema/additionalProperties closure;
- privacy scanner pass.

No literal PASS checks.

## Preserve

Preserve all approved CP2 behavior:

- exact three aliases only;
- privacy pre-open gates and historical exception;
- fail-closed sanitizer;
- source-session lifecycle;
- Master/Layout/theme shell authority;
- Exemplar-2 body authority;
- scope-aware shell support;
- `dt = date_time`;
- theme-bound RGB;
- per-theme identity;
- direct RGB and transforms;
- Unicode-safe font policy;
- per-script explicit typography;
- supplemental script mappings;
- group transforms / connector semantics / rotation exclusion;
- truthful unavailable metrics;
- zero private renders and `blocked_visual_review` honesty;
- disposable-worktree regression discipline;
- Phase 1–2 scientific/provenance invariants.

## Private access

You may reopen only the existing three authorized aliases through the guarded CP2 flow after pre-open gates pass. No new private source. No private render is required.

## Rebuild

Regenerate as needed:

- `thesis-deck-system/artifacts/phase3/sanitized-shell-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/sanitized-body-structural-descriptors.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-2-qa.json`

Update:

- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_2_IMPLEMENTATION_REPORT.md`

Run:

- focused CP2;
- CP1 + CP2;
- complete regression in disposable worktree;
- guarded private rebuild;
- schema + FormatChecker;
- recursive closure audit;
- script-truth/count reconciliation QA;
- theme-reachability QA;
- privacy scan;
- raw-root verification;
- `git diff --check`;
- remote verification.

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

CP2-G1:
CP2-G2:

script-role counts:
theme reachability summary:
unreferenced theme summary:
supplemental-font authority summary:

source-session attempts/success/failure:
private render counts/status:
descriptor-quality QA:
privacy scan status:
checkpoint aggregate status:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_2_REVIEW: yes

Then STOP.
