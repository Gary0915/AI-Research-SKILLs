# Phase 3 Checkpoint 2 — Revision 4 Review

Reviewed commit: `58b4df252ff00023cfc50f2210d38357f214cb1b`

Verdict: **REVISE**

Checkpoint 2 is materially improved and is close to resolver-ready. CP2-D1–D4 introduced truthful rotation exclusion, reconstructable color fields, occurrence/container recurrence fields, and body typography observations. The remaining blockers are narrowly scoped semantic/provenance defects that would otherwise be amplified by the Professor Visual Grammar Resolver.

## CP2-E1 — Placeholder semantics and shell source-scope truth

The current placeholder mapping treats DrawingML/PresentationML placeholder type `dt` as `navigation`. `dt` is a date/time placeholder, not a navigation semantic. This can cause a date/time placeholder to be learned as professor navigation grammar.

In addition, a single shell-region record may aggregate support from both `slide_master` and `slide_layout` containers while storing one `source_scope`, selected from the set of observed scopes. That single value is not a truthful provenance representation and can be nondeterministic. Coverage denominators also need to be scope-aware when the resolver uses them as strength evidence.

Required correction:

- represent `dt` as `date_time` (or another explicit date/time role), never navigation;
- navigation must require independent shape/role evidence and must not be inferred from `dt`;
- do not collapse mixed Master/Layout support into one arbitrary `source_scope`;
- preserve scope-aware support, either by separate records or an explicit `support_by_scope` structure;
- ensure coverage arithmetic is based on the eligible containers for the corresponding scope;
- keep per-container placeholder measurements so layout variants are not lost.

## CP2-E2 — Theme identity/topology must not be collapsed

The profiler currently walks all `ppt/theme/themeN.xml` parts into one token→RGB map using first-value retention. That is only safe if every theme part is identical. A presentation can contain multiple masters/themes, and template_primary_1 already has multiple masters.

Resolver-ready reconstruction must preserve sanitized theme identity and binding rather than assuming a package-wide single palette.

Required correction:

- assign sanitized theme IDs;
- preserve each theme palette separately;
- preserve `slide_master -> theme` binding/topology;
- use the correct bound theme palette when resolving Master/Layout/slide color evidence;
- if multiple theme parts are byte/semantically equivalent, they may be deduplicated only with explicit equivalence evidence;
- raw theme XML and private package paths remain local-only.

## CP2-E3 — Body typography is still mostly unresolved and theme-font roles are not actually derived

The body descriptor now contains 211 typography records, but the implementation extracts only direct `a:latin` typefaces and emits `theme_font_role=None`. The committed body descriptor contains many `family=unknown` observations. This does not yet satisfy the intended D2/D4 resolver-facing typography fidelity, especially for Chinese/East-Asian PowerPoint content where fonts may be specified via `a:ea`, `a:cs`, theme tokens, or inherited defaults.

The sanitizer also currently accepts only ASCII-form family names, which prevents safe localized font names from being preserved.

Required correction:

- parse privacy-safe font evidence for at least `a:latin`, `a:ea`, and `a:cs` when present;
- recognize PowerPoint theme font tokens such as major/minor Latin/East-Asian/complex-script references and preserve a controlled theme-font role/script;
- preserve sanitized theme font-scheme metadata needed to resolve those roles when structurally available;
- permit exact safe Unicode font family names under a strict safe-font policy rather than an ASCII-only regex;
- distinguish `explicit_font`, `theme_font`, `inherited_unresolved`, and `unknown` evidence states;
- do not claim font fidelity merely because `family="unknown"` is schema-valid;
- ordinary body-slide measurements should use an explicit `slide_body`/`slide_content` source scope rather than `slide_recurrence_derived`; reserve recurrence-derived scope for actual cross-slide recurrence evidence.

Full PowerPoint text-style inheritance does not need to be invented if it cannot be proven structurally. Unresolved inheritance should remain explicit rather than guessed.

## CP2-E4 — Owning QA must prove semantic resolution quality, not field presence

The current font-fidelity owning check accepts any truthy family other than `other_approved`, which means `unknown` passes. The body-typography check mainly verifies that the field exists and has the expected source scope. Color QA validates field-state shape but does not prove correct theme binding.

Required correction:

Execution-derived QA must own:

- `dt` cannot become navigation;
- shell support scope is internally consistent;
- scope-specific coverage arithmetic is correct;
- every theme-resolved color references a valid bound sanitized theme profile;
- theme/master topology is closed;
- body typography coverage reports explicit/theme/resolved/unresolved counts;
- `unknown` typography may be retained but cannot satisfy a font-fidelity PASS by itself;
- theme-font role evidence is validated when present;
- Unicode safe-font sanitization and private-string rejection are tested;
- body source scopes distinguish direct slide-body evidence from cross-slide recurrence.

Aggregate PASS must remain execution-derived. No literal status values.

## Accepted behavior to preserve

Do not regress:

- CP2-PRE-1 / CP2-PRE-2;
- exact legacy privacy exception;
- exactly three authorized stable aliases;
- fail-closed nested sanitizer;
- source session close only after sanitizer handoff;
- Master/Layout/theme shell authority;
- Exemplar 2 body authority;
- truthful unavailable metrics;
- conservative family confidence;
- group transform and connector marker/flip behavior;
- rotation exclusion;
- reconstructable direct RGB and color transforms;
- zero private renders and `blocked_visual_review` honesty;
- disposable-worktree regression discipline.

## Reviewer conclusion

The checkpoint is close, but the Resolver must not be allowed to learn that a date placeholder is navigation, bind a theme token to the wrong master palette, or treat unresolved Latin-only font extraction as professor typography fidelity. Correct CP2-E1–E4, rebuild the same sanitized artifacts, rerun the complete regression/QA suite, and stop for review.
