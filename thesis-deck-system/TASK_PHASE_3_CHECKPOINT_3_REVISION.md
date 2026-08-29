# TASK — Phase 3 Checkpoint 3 Revision

## Status

Authorized only after reviewer verdict `PHASE_3_CHECKPOINT_3_REVIEW.md` = REVISE.

This task corrects CP3-B1 through CP3-B6 only. It does not authorize later Phase 3 stages.

## Required inputs

Read completely before implementation:

1. `thesis-deck-system/reviews/PHASE_3_CHECKPOINT_3_REVIEW.md`
2. `thesis-deck-system/TASK_PHASE_3_IMPLEMENTATION_CHECKPOINT_3.md`
3. `thesis-deck-system/designs/PHASE_3_VISUAL_FIDELITY_DESIGN.md`
4. `thesis-deck-system/plans/PHASE_3_TDD_IMPLEMENTATION_PLAN.md`
5. `thesis-deck-system/reports/PHASE_3_CHECKPOINT_3_IMPLEMENTATION_REPORT.md`
6. `thesis-deck-system/REVIEW_PROTOCOL.md`

Checkpoint 3 remains sanitized-domain-only.

---

## CP3-B1 — Execution-derived owning QA

Replace the literal/self-certifying CP3 checks with real owning validators.

At minimum implement owning validation for:

- input artifact/schema/hash validation;
- exact exemplar identities;
- sanitized-domain/no-private-access boundary;
- asymmetric authority;
- Exemplar-2 shell contamination prevention;
- conflict completeness/hard-conflict behavior;
- evidence tier correctness;
- recurring-pattern minimum support;
- active-theme authority;
- descriptor-qualified theme identity;
- unresolved/supplemental typography exclusion;
- body family-range reconciliation;
- unavailable metric preservation;
- Figure grammar semantic non-invention;
- Visual Style Governor provenance/coverage;
- fallback separation;
- deterministic output;
- privacy scan;
- recursive schema closure.

Each owning check must persist enough sanitized evidence to explain the result, for example counts, referenced rule IDs, artifact hashes or finding counts.

Final `checkpoint-3-qa.json` must be derived from these results. A failing owning check must produce an honest failure state.

The QA schema must permit failure states rather than requiring every structural status to be `pass` by schema.

No check may be represented by a literal `True` solely to manufacture PASS.

---

## CP3-B2 — Strong nested schemas

Strengthen all CP3 output schemas so every nested core object is typed and fail-closed.

Required closed contracts include at least:

- shell token;
- typed shell token value variants;
- conflict record;
- body family grammar;
- per-family metric distribution/range;
- theme metadata token;
- resolved semantic style token;
- typography token;
- Figure grammar token;
- material unresolved token;
- Visual Style Governor token;
- owning check/evidence record;
- resolver evidence object;
- Checkpoint 3 statuses.

Arrays must define typed `items`.

Core nested objects must use `additionalProperties: false`.

Avoid unconstrained `{}` for values that enter later calibration. Use a discriminated or finite typed value model.

Add negative schema/runtime tests for unexpected nested fields, invalid IDs, invalid evidence tiers, invalid source authority, invalid value variants and malformed conflict records.

---

## CP3-B3 — Family-conditioned body grammar

Rework body grammar so reusable composition metrics are resolved per composition family, not as a single global distribution across heterogeneous slides.

For each family with adequate sanitized support, persist:

- family ID/class;
- source profile/authority;
- supporting real sanitized slide/descriptor IDs;
- sample count;
- source confidence;
- evidence tier;
- family-local metric distributions;
- bounded observed range;
- robust center/median where meaningful;
- preferred/medoid descriptor ID;
- outlier descriptor IDs;
- unavailable metrics;
- status.

Do not fabricate semantic families.

`other_insufficient_structural_evidence` is audit/insufficient evidence and must not become a reusable professor layout family merely because many slides fall into it.

A metric's sample count across unrelated families cannot by itself make that metric `recurring_pattern`.

If useful, package-wide metric summaries may remain as explicitly `audit_only` / non-authoritative summaries and must not feed Visual Style Governor professor-derived coverage.

Add tests proving:

- identical metric names in different families remain separate;
- mutation in one family does not change another family's range;
- family medoid/preferred ID is deterministic;
- outlier calculation is deterministic;
- unsupported family does not become reusable grammar;
- null/unavailable remains unavailable.

---

## CP3-B4 — Theme/style authority and recurrence truth

Separate active theme metadata from professor-derived style preferences.

`usage_state = referenced` proves reachability, not recurrence of every palette slot.

Preserve active theme palettes as sanitized reference metadata.

A palette/color token may become `professor_derived` style only when there is sanitized support that the color/style role is actually observed/recurrent in the authorized source scope.

Do not label every token in an active Office theme `recurring_pattern`.

Apply asymmetric authority:

- Exemplar 1/3 may provide formal-shell color roles according to shell token-family authority;
- Exemplar 2 may provide body/annotation/emphasis color evidence only where CP2 body observations support it;
- Exemplar 2 may not become formal-shell palette authority.

Do not numerically blend conflicts.

Add tests proving:

- active-but-unused palette slot remains metadata only;
- referenced theme existence alone cannot become recurring preference;
- Exemplar-2 palette cannot create formal-shell color token;
- observed body emphasis color may remain body-scoped evidence;
- descriptor-local theme identity remains isolated.

---

## CP3-B5 — Visual Style Governor must expose actual controlled grammar

Rebuild the Visual Style Governor profile as the reusable structural style layer required by CP3-8.

Where supported by CP2/CP3 evidence, include controlled tokens for:

### Formal shell

- canvas;
- content title region;
- cover/divider title region;
- footer/page-number/navigation;
- safe content bounds/alignment evidence;
- formal typography roles;
- authority-correct active shell colors.

### Generic scientific visuals

- line-width distribution/role;
- connector/arrow classes and direction/marker style evidence;
- generic accent/emphasis/red-callout evidence;
- panel spacing/gutter;
- caption/body scale ratio where supported;
- figure/text dominance by family;
- matrix/panel spacing;
- annotation density by family.

Do not invent unsupported tokens.

Every governor token must carry:

- origin (`professor_derived | phase2_fallback | implementation_fallback | unresolved`);
- evidence tier;
- source authority/scope;
- supporting sanitized IDs;
- resolver rule ID.

Typography tokens generated by the grammar must not disappear from the governor when they are valid for the governed role.

Use a status such as `partial_structural_calibration` when coverage is incomplete. Do not claim fully `calibrated` merely because some tokens exist.

Coverage must distinguish at least:

- professor-derived recurring;
- professor-derived provisional;
- fallback;
- unresolved;
- reference-only metadata.

Fallback/reference-only values do not increase professor-fidelity coverage.

---

## CP3-B6 — Resolver-safe shell evidence

Strengthen `professor-template-resolved.json` so it carries the shell evidence needed by later template reconstruction/A01–A18 calibration.

Required:

1. **Safe content bounds**
   - apply the design intersection rule when both shell exemplars provide defensible compatible bounds;
   - empty/impractically-small intersection = hard blocking;
   - missing evidence = `insufficient_evidence`.

2. **Content master/layout topology**
   - Exemplar 1 remains authority;
   - preserve sanitized topology/role evidence required by later reconstruction.

3. **Support truth**
   - derive support/container counts and evidence tier from CP2 `support_by_scope` / container evidence;
   - do not hard-code `support_count = 1` merely because one profile was selected;
   - retain supporting sanitized container/measurement IDs.

4. **Multiple structural variants**
   - do not choose a lexicographically/arbitrarily first matching region when multiple variants exist;
   - preserve typed variants or apply an explicit deterministic role-specific resolver rule.

5. **Conflicts**
   - fully type conflict records;
   - retain losing alternative descriptor evidence and source IDs;
   - unmapped hard conflict blocks output.

6. **Hypothesis/history**
   - do not equate a generic subtitle region with the complete Hypothesis/history motif unless evidence supports that mapping;
   - mark insufficient/provisional truthfully where only partial shell evidence exists.

Add mutation tests for support counts, safe-bound conflicts, multiple variants, topology source authority and losing-descriptor conflict evidence.

---

## CP3 focused test expansion

The previous focused suite had only nine tests. Expand the CP3 focused suite to directly cover the required CP3-9 properties and CP3-B1–B6 corrections.

At minimum add explicit tests for all twenty CP3-9 properties from the original task plus the new correction tests above.

Do not target a fixed count. Report the actual implemented focused test count.

---

## Privacy and scope preservation

Checkpoint 3 still consumes only committed sanitized CP2 artifacts.

Required counters remain:

- production private alias resolution attempts = 0;
- private source open attempts = 0;
- private render attempts = 0.

No private PPTX, local raw profile, screenshot, render, text, media or notes may be accessed.

Do not add a new privacy exception.

Preserve the exact prior regression-artifact cleanup discipline and run the complete regression in a disposable worktree.

---

## Not authorized

Do not begin:

- A01–A18 production calibration;
- reconstructed native template;
- PPTX output;
- production Figure Skills/renderers;
- reconstruction benchmarks;
- acceptance deck;
- Phase 4;
- public/global Skill registration.

---

## Required rebuild

Regenerate/update as necessary:

- `thesis-deck-system/artifacts/phase3/professor-template-resolved.json`
- `thesis-deck-system/artifacts/phase3/body-composition-profile.json`
- `thesis-deck-system/artifacts/phase3/professor-visual-grammar-v3.json`
- `thesis-deck-system/artifacts/phase3/visual-style-profile.json`
- `thesis-deck-system/artifacts/phase3/resolver-evidence.json`
- `thesis-deck-system/artifacts/phase3/checkpoint-3-qa.json`
- all corresponding schemas;
- `thesis-deck-system/reports/PHASE_3_CHECKPOINT_3_IMPLEMENTATION_REPORT.md`.

The report must explicitly trace CP3-B1 through CP3-B6 and correct any prior statement that implied literal checks were execution-owned.

---

## Required validation

Run at minimum:

1. focused CP3 tests;
2. CP1 + CP2 + CP3 tests;
3. full disposable-worktree regression;
4. CP2 input schemas/hash validation;
5. all CP3 output schemas + FormatChecker;
6. recursive `additionalProperties:false` / array-items closure audit;
7. execution-owned QA evidence consistency;
8. family-conditioned range/medoid/outlier reconciliation;
9. theme metadata vs professor-token authority QA;
10. Visual Style Governor provenance/coverage QA;
11. shell safe-bounds/topology/support QA;
12. mutation/determinism QA;
13. repository/staged privacy scan;
14. `git diff --check`;
15. remote branch/artifact verification.

---

## Delivery

Commit and push only the authorized Checkpoint 3 revision work.

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

CP3-B1:
CP3-B2:
CP3-B3:
CP3-B4:
CP3-B5:
CP3-B6:

focused CP3 tests count:
full regression status:

private alias resolution attempts:
private source open attempts:
private render attempts:

body family grammar summary:
style-governor coverage summary:
shell resolver support/safe-bound/topology summary:
QA owning-check summary:

private qualitative visual review:
acceptance deck visual fidelity:
archetype calibration coverage:
native PowerPoint acceptance:
production Group Meeting ready:

regression artifact cleanup summary:

known failures:
technical debt:
unresolved questions:

READY_FOR_CHECKPOINT_3_REVIEW: yes

Only write `READY_FOR_CHECKPOINT_3_REVIEW: yes` after push and remote verification.

Then STOP.
