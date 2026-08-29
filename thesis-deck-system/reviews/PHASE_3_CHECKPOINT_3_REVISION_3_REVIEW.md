# Phase 3 Checkpoint 3 — Revision 3 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`d32b20bf6c1283d27460ff0faafc8e50fbd748b2`

Revision 2 materially improves the resolver. CP3-C1–C5 are partially implemented and the system is close to an approvable sanitized structural grammar. Checkpoint 3 is still not approved for A01–A18 calibration, template reconstruction, production Figure Skills, benchmarks, or acceptance-deck work.

## What now passes review

1. Typography records preserve measured size, weight, style, script, source scope, and provenance instead of dropping hierarchy.
2. Whole Office theme palettes remain reference metadata rather than automatic professor-style tokens.
3. Usage-backed structural style evidence is now present, including generic colors, connector classes, and measured nonzero line width.
4. Body metrics remain family-conditioned and package-wide distributions remain audit-only.
5. A normalized pairwise-medoid method with an explicit missing-data penalty is persisted.
6. Execution-owned QA now includes CP2 schema checks, determinism, regression evidence, and more detailed category coverage.
7. CP3 remains sanitized-domain-only; private alias/source/render counters remain zero.
8. Full regression remains isolated in a disposable worktree.

## Remaining blockers

### CP3-D1 — Candidate→slide binding is still positional and is not a real persisted binding contract

`_bind_body_candidates()` still chooses `measurements[index]` for `candidate_families[index]` and only checks whether object IDs from `evidence_basis` happen to exist in that paired slide.

This is not a robust identity binding:

- object IDs such as `O001`, `O002`, etc. are slide-local and recur on many slides;
- `other_insufficient_structural_evidence` candidates can contain no object IDs at all, so they receive no identity validation;
- swapping two rows whose referenced object IDs happen to exist on both slides can silently relabel the measurement;
- the generated `body-composition-profile.json` does not persist the claimed 13 candidate→slide bindings.

The owning `CP3-BODY-BINDINGS` check currently verifies only that each family preferred descriptor is contained in its supporting descriptor list. It does not validate candidate→slide bindings.

Required correction:

- create an explicit sanitized candidate binding record containing at least candidate identity/order evidence, `slide_id`, family, confidence, and binding evidence;
- preferably add a stable candidate ID / slide binding upstream in the sanitized contract, or derive a collision-resistant structural fingerprint that is validated fail-closed;
- no-index-only association may be relied upon by the resolver;
- persist all 13 bindings and validate them in owning QA;
- adversarial swaps of two slides with overlapping local object IDs and swaps of two no-object-evidence candidates must either normalize to the same binding or fail closed.

### CP3-D2 — The persisted privacy owning check is not actually bound to the approved repository + staged scanner

`_approved_privacy_scan()` currently calls `scan_repository_with_legacy_exception(..., forbidden_basenames=[])` and then serializes `staged_scan_bound: true` without executing or proving a staged-index scan in that function.

Therefore the QA artifact's PASS does not establish the claim made in the report that the owning check is bound to the approved repository/staged scanner. Passing an empty forbidden-basename set also weakens the production-private basename boundary.

Required correction:

- invoke the approved privacy scanner with the same authoritative forbidden basename/configuration set used by the Phase 3 privacy boundary;
- execute or consume a real staged-index scan result, not a literal `staged_scan_bound = true` assertion;
- persist scanner identity/version, repository finding count, staged finding count, approved legacy exception count, and configuration/hash evidence;
- fail the owning check if either repository or staged scan is missing or stale.

### CP3-D3 — Category coverage readiness is overclaimed and contradicts the implementation report

The implementation report says typography/body/figure/connector/line/color categories are `provisional_only`. The committed `visual-style-profile.json`, however, marks `connector_arrow_grammar` and `color_emphasis_grammar` as `fully_calibrated`.

The current implementation defines a category as `fully_calibrated` whenever the category contains *any* recurring professor-derived token, even if the same category still contains many provisional tokens. This is too weak for routing later Figure Skills.

Required correction:

- define an explicit category readiness rule based on required sub-capabilities / coverage, not `recurring_count > 0`;
- distinguish `partial_recurring`, `provisional_only`, `fully_calibrated`, and `unresolved` (or an equivalent controlled state model);
- connector readiness should separately account for orientation, directedness, marker grammar, and any intentionally unresolved directional/flip semantics;
- color/emphasis readiness should distinguish recurring generic color usage from complete emphasis-role calibration;
- make report facts, Governor artifact, and owning QA agree exactly.

### CP3-D4 — Typography authority still has an `unknown` role escape hatch and role-level grammar is not resolved

The fixed authority matrix authorizes Exemplar 2 for body/caption/annotation/panel-label typography. The implementation additionally authorizes role `unknown` for Exemplar 2, and the owning authority check explicitly blesses that state.

An explicit font with `role=unknown` can therefore become professor-derived without semantic authority. This is not fail-closed.

Also, `_typography()` still emits raw individual observations. It does not actually resolve repeated compatible observations into role-level typography distributions/hierarchy where recurrence is supported, even though this was part of CP3-C1.

Required correction:

- remove `unknown` from professor-derived typography authority;
- retain unknown-role explicit typography as audit-only/insufficient evidence if useful;
- group typography by authorized semantic role + script + compatible style family;
- persist role-level size range/center, weight/style consistency, support count, supporting IDs, and evidence tier;
- do not let duplicate runs within one slide/container create recurrence;
- preserve raw sanitized observations only as evidence, not as independent professor preferences.

### CP3-D5 — Candidate-bound regression evidence does not bind all resolver-critical candidate state

`_candidate_state_hash()` currently binds the four CP2 input hashes plus only the resolver Python source hash. CP3 schemas changed in this implementation, but those schema hashes are not part of the regression candidate binding.

A schema/contract change after a successful regression could therefore reuse the same candidate-state hash when the resolver source and CP2 inputs are unchanged.

Required correction:

- bind the disposable regression evidence to all resolver-critical implementation state, at minimum the resolver source and all six CP3 output schemas;
- persist the exact candidate-state component hashes;
- the owning regression check must verify this composite state before PASS;
- report the same composite candidate binding.

## Decision

Checkpoint 3 remains **NOT APPROVED**.

The next correction is limited to CP3-D1–CP3-D5. Do not start A01–A18 calibration, template reconstruction, production Figure Skills, PPTX generation, reconstruction benchmarks, acceptance deck, Phase 4, or public/global Skill registration.
