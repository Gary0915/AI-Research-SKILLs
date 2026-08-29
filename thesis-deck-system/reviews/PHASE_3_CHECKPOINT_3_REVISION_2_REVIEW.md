# Phase 3 Checkpoint 3 — Revision 2 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`6498c60506ab04c7219006cdc3138c1ee20e71ed`

Checkpoint 3 is materially improved and the previous B1–B6 corrections are mostly implemented. It is not yet approved for A01–A18 calibration, template reconstruction, Figure Skill production, benchmarks, or acceptance-deck work.

## What now passes review

1. CP3 remains sanitized-domain-only and records zero private alias/source/render attempts.
2. Literal `True` QA was replaced by executed validators with typed persisted facts.
3. Core CP3 schemas are substantially closed and nested arrays now have typed item contracts.
4. Body metrics are now family-conditioned; package-wide metrics are audit-only.
5. Active theme metadata is no longer automatically promoted into professor style tokens.
6. The Visual Style Governor is honestly marked `partial_structural_calibration`.
7. Shell support retains CP2 scope/container evidence, variants, Exemplar-1 layout→master topology, and safe-bound status.
8. Hypothesis/history remains unresolved when direct motif evidence is absent.
9. Full regression is isolated in a disposable worktree.

## Remaining blockers

### CP3-C1 — Typography authority is still not enforced and typography fidelity is dropped

`_typography()` iterates every accepted typography record from both shell exemplars and the body exemplar. It does not enforce the fixed role authority matrix:

- Primary 1: content / Hypothesis roles;
- Primary 3: cover / divider / footer roles;
- Exemplar 2: body / caption / annotation scale evidence only.

Therefore an explicit font from the wrong shell exemplar can still enter active grammar.

In addition, CP2 already preserves `size_pt`, `weight`, and `style`, but CP3 typography records do not preserve those fields and the Governor explicitly emits every typography token with `size_pt: null`.

This loses measured visual hierarchy immediately before archetype calibration.

Required correction:

- enforce role-family authority before a typography observation becomes professor-derived;
- preserve safe measured `size_pt`, weight, style, role confidence where available;
- resolve role-level typography distributions rather than outputting raw independent observations when recurrence is supported;
- keep fallback fonts separate.

### CP3-C2 — Actual color / line / connector evidence is being discarded

CP2 contains usage-backed style evidence, including direct shell colors such as `888888` and `C00000`, plus measured body connectors with directedness and arrow markers.

Current CP3 correctly keeps whole Office themes as reference-only metadata, but then promotes **zero** usage-backed color tokens and does not resolve connector/arrow or line-width grammar. The current Figure/Style layer is therefore mostly family metric ranges plus typography family names.

This does not meet the intended Visual Style Governor / Figure Skill handoff. The resolver must distinguish:

- theme palette existence — reference metadata only;
- actually measured style usage — eligible structural evidence.

Required correction:

- derive sanitized usage-backed generic color roles from `style_roles` / object style evidence under the fixed exemplar authority;
- derive line-width distributions where measured;
- derive connector/arrow class grammar from measured connector records (head/tail marker, direction, orientation, flip-normalized class as structurally supportable);
- preserve generic red/emphasis evidence only when actual measured usage supports it;
- do not infer scientific material semantics.

### CP3-C3 — Family binding and preferred representative are not robust enough

`resolve_body_grammar()` pairs `candidate_families[index]` with `body_measurements[index]`. The candidate object itself has no slide identifier. This means independent reordering of the two arrays can silently associate the wrong family with the wrong measured slide.

The current family-level `preferred_descriptor_id` is also not a true resolver-safe medoid. It sums raw absolute deviations from per-metric centers across heterogeneous metric scales and skips missing metrics; a descriptor with fewer available metrics can receive an artificially small score.

Before A01–A18 calibration, representative selection must be stable and meaningful.

Required correction:

- introduce an explicit normalized candidate→slide binding contract or fail-closed invariant proving the parallel-array relationship;
- mutation/reordering must never silently relabel measurements;
- representative selection must use a documented normalized distance over comparable available metrics, or a true deterministic pairwise medoid;
- missingness must not reward a descriptor;
- persist the distance method and comparable-metric count/evidence.

### CP3-C4 — Owning QA is improved but still incomplete relative to the authoritative CP3 task

The 19 checks are real executions, but the required owning QA also included deterministic resolver output, CP2 input artifact/schema/hash validation, supplemental-font exclusion, and full regression evidence.

Current `CP3-INPUT-VALIDATION` only proves CP2 aggregate PASS plus four computed hashes; it does not itself validate the four canonical input objects against their schemas/integrity relationships.

Current `CP3-PRIVACY-SCAN` is a local substring scan over a subset of generated objects, while the report separately claims repository/staged privacy scanning.

Required correction:

- persist an owning determinism check, not only unit tests;
- persist canonical CP2 input schema/integrity validation facts;
- persist supplemental/reference-only font exclusion facts;
- persist regression candidate/result evidence or an execution record bound to the candidate hash;
- bind the privacy owning check to the actual approved repository/staged privacy scanner result, rather than a second weaker substring-only implementation.

### CP3-C5 — Governor coverage currently overstates reusable visual calibration

The Governor reports 37 professor-derived tokens, but many are provisional family metrics and typography tokens that have lost size/weight/style. Meanwhile the directly useful figure-language evidence (connector classes, line widths, usage-backed color roles) is absent.

Coverage must distinguish at least:

- shell geometry;
- typography hierarchy;
- body composition;
- figure primitive/connector grammar;
- style/color grammar;
- unresolved families.

A single aggregate token count is not sufficient for deciding whether a later archetype or Figure Skill has enough calibrated evidence.

Required correction:

- add family/category coverage dimensions;
- count only reusable, authority-valid tokens in the corresponding coverage category;
- provisional tokens remain provisional and do not imply the visual family is fully calibrated.

## Decision

Checkpoint 3 remains **NOT APPROVED**.

The next implementation is limited to CP3-C1–CP3-C5. Do not start A01–A18 calibration, template reconstruction, Figure Skill production, PPTX generation, reconstruction benchmarks, acceptance deck, Phase 4, or global/public Skill registration.
