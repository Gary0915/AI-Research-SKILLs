# Phase 3 Checkpoint 3 — Reviewer Verdict

## Verdict

**REVISE**

Reviewed implementation commit: `2db850ea054068f40f7e5abb5923f7bbd81203bc`

Checkpoint 3 is not approved yet. The implementation correctly preserves the sanitized-domain-only boundary, asymmetric source identity at a coarse level, unresolved material semantics, no PPTX/render production, and the independent readiness/status model. However, the current resolver is not yet safe to feed into A01–A18 calibration or template/figure production.

## Blocking findings

### CP3-B1 — QA is self-certifying instead of execution-owned

`resolve_checkpoint3()` currently constructs most owning checks as literal `True` values. Examples include input validation, exemplar identities, no-private-access, authority, shell contamination, evidence tiers, active themes, typography truth, body range, figure non-invention, style provenance, determinism, privacy scan, and schema closure. The aggregate therefore mostly certifies assertions written by the same builder rather than results produced by owning validation functions.

This directly violates CP3-11: no QA status may be literalized without owning evidence.

Required correction:

- implement real owning check functions;
- persist check evidence/measurements, not only check IDs/status;
- derive the final QA object from those check results;
- allow failed checks to serialize honestly;
- do not hard-code structural resolver statuses to `pass` in the QA schema.

### CP3-B2 — Resolver schemas are not strongly typed/fail-closed at nested boundaries

The new schemas do not yet satisfy CP3-1's requirement that all nested objects be strongly typed with `additionalProperties: false`.

Examples:

- `professor-visual-grammar-v3.schema.json` declares several arrays (`formal_shell_rules`, `body_composition_rules`, `active_theme_tokens`, `typography_tokens`, `figure_grammar`) without typed `items` contracts;
- `professor-template-resolved.schema.json` leaves `conflicts` untyped and permits an unconstrained `value`;
- `checkpoint-3-qa.schema.json` leaves `owning_checks` untyped;
- `visual-style-profile.schema.json` uses an unconstrained token `value`.

Required correction:

- define closed nested schemas/defs for shell tokens, conflicts, family grammar, metric/range tokens, theme tokens, typography tokens, figure grammar tokens, style tokens, owning checks and evidence records;
- use discriminated typed value structures rather than `{}` where practical;
- add recursive schema-closure and mutation negative tests proving unexpected nested fields fail.

### CP3-B3 — Body range model is global rather than family-conditioned

CP3-6 requires body grammar to group compatible descriptors by composition family and preserve range, robust center, medoid/preferred descriptor, outliers, sample count and evidence tier. The current implementation instead computes global metric medians/ranges across heterogeneous slides.

For example, `annotation_density`, `figure_text_ratio`, `whitespace_fraction`, and similar metrics are aggregated across the deck regardless of family. These values are then promoted to `recurring_pattern` whenever enough slides contain the metric. This can create a professor preference from mixed families that are not geometrically comparable.

The current body profile also lacks the required family-local medoid/preferred descriptor and outlier IDs.

Required correction:

- compute metric distributions per supported family;
- only aggregate descriptors whose family evidence is compatible;
- persist per-family range/median/medoid/outliers/sample count;
- preserve global statistics only as explicitly non-authoritative audit summaries if useful;
- a metric observed across unrelated families must not become a reusable family grammar merely from count.

### CP3-B4 — Active theme existence is being over-promoted to recurring professor style

`_active_theme_tokens()` marks every palette entry of every topology-referenced theme as `recurring_pattern` and `professor_derived`.

`referenced` means the theme is in use; it does not prove every palette slot is a recurring professor preference. Theme-token existence is not recurrence evidence. The current Visual Style Governor therefore counts many theme palette entries as professor-derived coverage even if they are merely unused slots in an active Office theme.

In addition, all active Exemplar-2 theme palette entries are inserted into the general style profile. Exemplar 2 has body-composition authority, not unrestricted formal-shell palette authority.

Required correction:

- distinguish `active_theme_metadata` from `resolved_professor_style_token`;
- require actual sanitized usage/support evidence before a palette token becomes professor-derived recurring style;
- preserve unused palette slots as reference/audit metadata;
- apply source-authority constraints to color tokens;
- body exemplar colors may influence body/annotation/emphasis roles only when supported by body observations, never formal-shell palette authority.

### CP3-B5 — Visual Style Governor is not yet the required governor profile

CP3-8 requires the governor to expose evidence-backed shell and scientific-visual tokens such as formal typography, line widths, arrows/connectors, accent/emphasis roles, panel spacing, caption/body scale, figure/text dominance and matrix spacing.

The current `visual-style-profile.json` is dominated by:

- global body metrics;
- shell geometry;
- full active theme palettes;
- one fallback font token.

It does not actually include the resolved typography tokens produced in Professor Visual Grammar, and it does not resolve the available CP2 connector/primitive/line-style evidence into controlled arrow/line/emphasis grammar. Therefore `status = calibrated` is too strong.

Required correction:

- include authority-correct formal typography in the governor;
- derive generic connector/arrow/line-width/emphasis/panel/caption tokens from available CP2 evidence where defensible;
- preserve insufficient evidence honestly when not defensible;
- do not substitute whole theme palettes for semantic style roles;
- governor status must distinguish partial structural calibration from fully calibrated style coverage.

### CP3-B6 — Shell resolver drops required resolver evidence and uses profile-level support instead of CP2 support

The resolved shell currently selects one region per role and assigns `support_count = 1` with only the source profile ID as support. It does not consume the CP2 scope/container support evidence that was specifically built to distinguish recurring Master/Layout support. It also omits safe-content-bounds resolution and content master/layout topology from the resolved shell, both of which are required by the design/task.

Required correction:

- resolve safe content bounds using the authorized intersection rule or `insufficient_evidence`;
- carry Exemplar-1 content master/layout topology as shell evidence;
- derive support/evidence tier from CP2 `support_by_scope`/container evidence, not from one profile-level selection;
- retain supporting sanitized container/measurement IDs;
- do not select an arbitrary first matching region when multiple structural variants exist; preserve role variants or choose via an explicit deterministic rule with evidence;
- conflict records must be fully typed and retain the actual losing descriptor evidence.

## Additional reviewer observations

1. The current focused CP3 suite contains only nine tests, while CP3-9 requires at least twenty explicit mutation/determinism properties. Several required cases are only indirectly covered or not covered at all.
2. The report states that CP3-11's fifteen checks determine aggregate status rather than prefilled PASS fields, but the implementation currently literalizes most checks. The report must be corrected after implementation.
3. The zero-private-access boundary appears architecturally preserved because CP3 consumes sanitized JSON only; keep this property. Do not weaken it while fixing QA evidence.
4. The regression-artifact cleanup discipline was handled correctly and should remain unchanged.

## Scope decision

Checkpoint 3 remains open. Do **not** begin:

- A01–A18 calibration;
- template reconstruction;
- Figure Skill production;
- reconstruction benchmarks;
- acceptance deck;
- Phase 4;
- global/public Skill registration.

Reviewer status: **CP3_REVISE**
