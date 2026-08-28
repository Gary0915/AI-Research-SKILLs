# Phase 3 Checkpoint 2 — Revision 3 Review

## Verdict

**REVISE**. Checkpoint 2 privacy, source-session lifecycle, nested sanitization, null/unavailable metric semantics, grouped off/ext/chOff/chExt transforms, and conservative family classification are materially improved. The descriptors are not yet safe to hand to the Professor Visual Grammar resolver because several remaining measurements can still encode misleading style/recurrence semantics or lose fidelity that cannot be reconstructed later.

## CP2-D1 — Shell region role and recurrence semantics are not yet resolver-safe

The committed shell descriptor reports shell regions such as title/header/footer/navigation with recurrence counts that can exceed the number of source Master/Layout containers. `template_primary_1` has 2 masters + 19 layouts, yet region occurrence counts include title=24, header=25, footer=58, navigation=54. Title/header geometries also overlap strongly. This indicates the current region aggregation is counting raw matching shapes and applying overlapping positional predicates rather than proving one semantic shell role per source container.

Before resolver use, shell-region evidence must distinguish:

- placeholder-semantic role (`title`, `ctrTitle`, `ftr`, `sldNum`, etc.) when available;
- geometric heuristic role only when placeholder semantics are unavailable;
- `occurrence_count` (raw qualifying shapes);
- `source_container_count` (distinct masters/layouts that support the rule);
- `coverage_ratio` against eligible source containers;
- role-evidence basis and source IDs.

A single shape must not satisfy incompatible shell roles merely because positional predicates overlap. `recurrence_count` must not be used as if it meant distinct-layout recurrence when it actually counts shapes.

## CP2-D2 — Theme/color and font fidelity is still lossy

Current color extraction maps arbitrary direct RGB values into coarse roles (`accent`, `neutral`, `emphasis`) and maps scheme colors to `theme:<token>`. This preserves category but loses the actual sanitized palette values needed to reconstruct Exemplar 1/3 faithfully. A fresh reconstructed template cannot reproduce the professor shell from `theme:accent1` alone unless the resolved RGB (and relevant color transforms) are preserved.

Likewise, font families outside a small hard-coded allowlist collapse to `other_approved`. Resolver-ready profiling should preserve the exact safe font family used when it is a valid installed/font-scheme name, while still failing closed on arbitrary unsafe strings. Theme major/minor font scheme evidence should be captured where structurally observable.

Required safe style evidence should support at least:

- theme token;
- sanitized resolved RGB/ARGB where deterministically resolvable;
- direct RGB value when present;
- relevant tint/shade/lumMod/lumOff transforms or an explicit unsupported-transform state;
- exact safe font family / theme major-minor font role;
- source scope and measurement basis.

## CP2-D3 — Group/shape rotation is not handled or explicitly blocked

The implemented group transform composes `off`, `ext`, `chOff`, `chExt`, nesting and flips, but does not account for DrawingML rotation (`rot`) on groups or child transforms. The current tests/report likewise cover translation, scaling, nesting and flips, not rotation.

For resolver-safe geometry, any rotated group/child must either:

1. be transformed correctly into absolute slide coordinates, including rotation; or
2. be detected and explicitly marked unsupported/not-observable for geometry-dependent downstream metrics and high-confidence family classification.

Silently treating rotated geometry as unrotated measured geometry is not acceptable.

## CP2-D4 — Body typography/style evidence is incomplete for the primary body exemplar

`layout_exemplar_2` is the primary body-composition and scientific-figure-layout authority. Its committed body descriptor contains objects, connectors, groups, style roles and metrics, but does not preserve sanitized typography observations (font family/size/weight/role) even though the local profiler observes fonts. This loses information required to reproduce annotation hierarchy, captions, scientific labels and dense figure-first pages.

Add privacy-safe body typography observations without exporting slide text. At minimum support structural roles such as title/body/caption/annotation/panel-label when inferable from geometry/placeholder/style; otherwise mark role provisional/unknown. Preserve size, weight, safe font family, source scope, and evidence basis.

## QA requirements

Checkpoint 2 aggregate PASS must own tests that prove:

- shell region role assignment is non-overlapping or explicitly multi-role with separate evidence;
- recurrence is based on distinct source containers, not raw shape count;
- `occurrence_count` and `source_container_count` cannot be conflated;
- theme/direct color values needed for reconstruction are preserved in sanitized form;
- unknown/unsupported color transforms are not silently flattened;
- safe exact font names/theme font roles survive sanitization;
- rotated groups/shapes are either correctly transformed or excluded from geometry-dependent confidence;
- body typography observations are present or explicitly unavailable;
- no private text is exported while preserving typography/style metadata.

## Preserved approvals

Do not regress CP2-PRE-1/PRE-2, the exact legacy exception, three-alias guarded access, local-only raw profiles, fail-closed nested sanitizer, execution-derived QA, source-session close-after-sanitizer lifecycle, no private renders, null/unavailable metric semantics, conservative family confidence, group off/ext/chOff/chExt transforms, connector marker/flip semantics, repository/staged privacy scanning, or the disposable-worktree regression cleanup discipline.

## Scope

This is still Checkpoint 2 only. Do not begin Professor Visual Grammar resolution, VisualStyleGovernor calibration, A01–A18 calibration, production Figure Skills, template reconstruction, reconstruction benchmarks, acceptance deck generation, Phase 4, or global Skill registration.
