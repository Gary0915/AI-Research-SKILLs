# Phase 3 Checkpoint 2 — Revision 6 Review

Reviewer verdict: **REVISE**.

Reviewed implementation: `61fc0a3dd1c507e85867b3d9e03e53c27fec80bf`.

The CP2-F1/F2 implementation correctly preserves multiple explicit script nodes, supplemental theme-script metadata, descriptor-local theme identity, and execution-derived count reconciliation. Checkpoint 2 is now structurally mature, but two final resolver-safety issues remain.

## CP2-G1 — an absent script node must not become Latin evidence

The profiler currently uses a fallback equivalent to `[("latin", None)]` when a run/default-run property set contains no direct `a:latin`, `a:ea`, or `a:cs` node. That produces `script_role = latin` + `font_evidence_state = inherited_unresolved` even though no Latin script evidence was structurally observed.

This makes the production summary `Latin 209 / East-Asian 0 / complex-script 2` misleading: most of the 209 observations are really *script-unspecified inherited typography*, not measured Latin typography.

Before Professor Visual Grammar resolution, absent direct script evidence must be represented truthfully, e.g. `script_role = unspecified`, unless a controlled safe language/script attribute provides defensible structural evidence. No private text inspection is authorized.

If `lang` / `altLang` metadata is used, it must be normalized through a finite safe language-to-script classifier and must never export arbitrary private strings.

## CP2-G2 — unreferenced theme parts must not become professor-style evidence

The committed shell descriptors preserve four theme profiles while each shell source has only two Master→Theme edges. This means some package theme parts are not reachable from an active Master.

Preserving them for audit is acceptable, but the future Resolver must not treat unreferenced/orphan theme profiles or their large supplemental font maps as active professor visual grammar.

Theme profiles therefore need explicit reachability/usage evidence, or the committed resolver-facing set must be restricted to topology-reachable themes. At minimum preserve descriptor-local usage such as active Master IDs / slide IDs or a controlled `usage_state`.

Supplemental script-font mappings from an unreferenced theme are reference metadata only and cannot count as professor preference evidence.

## Required outcome

After G1/G2, CP2 descriptors must distinguish:

- explicit per-script evidence;
- theme-token per-script evidence;
- script-unspecified inherited evidence;
- active/reachable theme profiles;
- unreferenced theme profiles, if retained;
- supplemental theme mappings as reference-only metadata rather than recurring professor preferences.

No new private render is required. No Professor Visual Grammar Resolver work is authorized in this correction.
