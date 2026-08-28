# Phase 3 Checkpoint 2 Revision 5 Review

## Verdict

REVISE — one final typography extraction correction is required before Checkpoint 2 can be closed and Professor Visual Grammar resolution can begin.

Reviewed implementation commit:

`8dbc8b79c53af68e609d99c7d01fd465eacbfdfe`

## Accepted work

CP2-E1 through CP2-E4 are substantially implemented and must be preserved:

- `dt` is represented as `date_time`, not navigation.
- shell recurrence/support is scope-aware and uses scope-local denominators.
- per-theme profiles and Master→Theme topology are persisted.
- direct/theme color evidence is bound to theme profile identity.
- Unicode-safe font names, script roles, theme-font roles, and evidence states exist.
- body observations use `slide_body`.
- private renders remain zero and private qualitative review remains honestly blocked.
- full regression was executed in a disposable worktree.

## Blocking finding — CP2-F1: per-script typography extraction is incomplete

The implementation currently searches `a:latin`, `a:ea`, and `a:cs`, but uses a single `next(...)` expression. Therefore a run containing more than one script-specific font node emits only the first matching script observation, normally Latin. The implementation report's statement that all three script classes are profiled is therefore too strong.

This matters for the body exemplar because the committed typography summary contains no East-Asian observations while most body observations remain inherited-unresolved. The resolver must not lose an explicitly present East-Asian or complex-script typeface merely because a Latin node is also present on the same run.

Required correction:

1. For every relevant run/default-run property set, inspect `a:latin`, `a:ea`, and `a:cs` independently.
2. Emit one sanitized typography observation per structurally present script-specific font node, with deterministic IDs and the same supporting object as appropriate.
3. If no explicit script node is present, preserve truthful inherited/unresolved evidence without inventing a family.
4. Theme tokens (`+mj-*`, `+mn-*`) must resolve independently for each script.
5. Do not double-count a single script node or silently collapse multiple script nodes into one observation.

## Blocking finding — CP2-F2: supplemental theme-script fonts are not preserved

The current theme-font parser records only direct `a:latin`, `a:ea`, and `a:cs` children of `a:majorFont` / `a:minorFont`. Office themes can also carry script-specific font mappings using `a:font script="..." typeface="..."`. These mappings are especially relevant when the direct East-Asian slot is empty.

Required correction:

1. Preserve privacy-safe supplemental theme font mappings as controlled structural metadata.
2. Support at least the common Office script codes needed for CJK/complex-script resolution (for example `Hans`, `Hant`, `Jpan`, `Hang`, plus any other observed safe script codes through a controlled sanitizer).
3. Keep script code and safe typeface only; do not export private text.
4. Do not guess which supplemental mapping applies to a run unless structurally supported. If the run cannot be bound to a specific supplemental script mapping, remain unresolved.
5. Theme profile data must remain descriptor-local or use a compound source-qualified reference. QA and future resolvers must not merge local `T001`/`T002` IDs from different exemplar descriptors into one global dictionary.

## Required owning QA

Add execution-derived checks proving:

- a synthetic run containing both `a:latin` and `a:ea` emits both script observations;
- a run containing `a:latin`, `a:ea`, and `a:cs` preserves all three;
- independent major/minor theme tokens resolve per script;
- supplemental `a:font script="Hant" ...>` survives sanitizer as controlled theme-font metadata;
- unsafe supplemental typefaces fail closed;
- supplemental theme mappings do not falsely resolve a run with no structural script binding;
- theme-profile lookups are source-descriptor scoped and cannot collide across two descriptors that both contain local `T001` with different palettes/font schemes;
- typography resolution counts equal the persisted typography observations by script/evidence-state.

## Scope

This is a narrow CP2 correction only. Do not begin Professor Visual Grammar Resolver, VisualStyleGovernor calibration, A01–A18 calibration, production Figure Skills, template reconstruction, benchmarks, acceptance-deck generation, Phase 4, or public/global Skill registration.

No private render is required. Re-opening the same three authorized aliases through the guarded CP2 flow is permitted after the existing pre-open gates pass.

## Approval condition

Checkpoint 2 may be approved after CP2-F1/F2 are implemented, all owning QA passes, the bounded private rebuild remains leak-free, and the complete regression remains green.
