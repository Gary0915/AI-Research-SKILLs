# Phase 3 Checkpoint 4 — Revision 2 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`76c7343042dd36b6701df9c92c2d5ddd5e410161`

Checkpoint 4 is materially improved and the overall control-plane architecture remains approved in direction, but it is not yet safe to authorize production Figure Skills.

The revision successfully adds 10/10 visual-class acceptance coverage, route-specific style categories, VSP003 in persisted plans, 17 Skill hashes, `contracts.py` hashing, a closed top-level request-key gate, and a disposable-regression record. However, six resolver/control-plane defects remain.

## CP4-C1 — Style profile consumption is still not fail-closed

`route_figure_request()` still contains a hard-coded fallback style object with `style_profile_id = VSP003` when `style_profile` is omitted.

This means the router can still produce a plan without consuming the approved CP3 `visual-style-profile.json`. If CP3 later advances to a new profile identity, direct callers can silently bind stale VSP003.

Required correction:

- remove the hard-coded fallback;
- require the actual consumed CP3 style profile for production CP4 routing;
- fail closed when the style profile is absent, schema-invalid, status-invalid, or its ID disagrees with the request/plan;
- keep any synthetic unit fixture explicitly labelled as a test fixture, not as a production default.

## CP4-C2 — Route-consistent FigurePlan/FigureSpec discrimination is not schema-enforced

The router now emits route-consistent `figure_type` values, but the v4 schemas still allow semantically inconsistent combinations.

For example, the schema does not structurally prevent a v4 plan/spec from combining a real-photo type with a plot director/renderer, or a literature type with the concept renderer, as long as each individual field satisfies its independent enum/pattern.

The focused tests only positively assert selected cases; they do not execute the required mismatch mutation matrix.

Required correction:

- add discriminated v4 route variants or an equivalent closed cross-field validator;
- bind `visual_class` / `figure_type` / specialist / renderer / output / evidence/source rules;
- add negative mutations for every visual-class mismatch family;
- schema-valid or contract-valid v4 objects must not be semantically cross-wired.

## CP4-C3 — FigureRoutingRequest is not yet a schema-backed closed contract

The implementation uses a Python `REQUEST_KEYS` allowlist, but no schema-backed `FigureRoutingRequest` contract was added.

This is weaker than the authorized requirement because nested request objects can still contain data that is silently dropped. For example, extra fabrication-step or Fishbone-binding fields are not rejected by an input schema before normalization.

Required correction:

- create a closed schema-backed `FigureRoutingRequest` or equivalent registered contract;
- strongly type all nested request variants;
- explicitly type empirical-slot fields and concept prohibitions;
- reject unknown nested fields, not merely unknown top-level keys;
- bind the new request schema into candidate-state hashing and schema-closure QA.

## CP4-C4 — The declared no-bypass graph still has contract-node inconsistencies

The registry now removes direct user-route-to-Layout paths, which is correct. However, the actual handoff contracts are still inconsistent:

- the canonical graph names `future_renderer_output_manifest`;
- several specialists hand off to `future_renderer_output_manifest`;
- `vector-figure-builder` declares output `future_output_manifest`;
- `figure-critic` declares input `[future_output_manifest]`.

Those are different contract identities.

The current graph validator checks the literal graph and prevents directors from handing directly to FigureCritic, but it does not prove that every downstream node exists as a declared Skill/contract node or that producer output contracts match consumer input contracts.

Required correction:

- normalize one canonical output-manifest contract identity;
- represent the renderer/output-manifest stage explicitly, either as a typed virtual contract node or an authorized repo-local Skill if the design calls for it;
- graph-audit every edge for producer-output → consumer-input compatibility;
- reject unknown downstream nodes, dangling handoffs, and contract-name mismatches;
- preserve the required FigureCritic gate before Layout.

## CP4-C5 — Disposable regression evidence is still self-bound, not externally bound

Candidate state now correctly hashes 32 components, including CP3 inputs, CP4 source, `contracts.py`, schemas, routing YAML, and all 17 Skill documents.

However, `build_checkpoint4_artifacts()` computes the current candidate hash and then writes that same current hash into `regression_candidate_state_hash` unconditionally. The supplied `regression_evidence` does not carry an independently captured candidate hash.

Therefore stale regression counts can be passed into a changed candidate and the artifact will relabel them with the current hash.

Required correction:

- the disposable regression harness must capture the candidate-state hash actually tested;
- pass that independent hash into artifact finalization;
- compare tested hash to current hash;
- mismatch must FAIL;
- mutation tests must prove that source/schema/routing/SKILL/CP3 changes invalidate old regression evidence.

## CP4-C6 — Owning QA and implementation report are not yet evidence-consistent

Most execution-owning checks still persist only `{result: true}` rather than the requested counts/IDs/hashes that constitute the proof. In particular, 10-class coverage, style identity/readiness, registry coverage, graph audit, CP3 input validation, schema closure, and disposable regression should persist their actual evidence.

The committed implementation report is also stale relative to the reviewed commit: it still reports 18 focused CP4 tests and 298 full regression tests, while the submitted revision reports 22 and 302. Its YAML footer still represents the initial CP4 file accounting and leaves `commit_sha: null`.

Additionally, the revised execution record reports zero approved legacy privacy exceptions whereas earlier approved CP3/CP4 evidence carried the reviewed historical exception. This may be legitimate only if the authoritative privacy configuration or repository state changed; the report currently does not explain or prove that transition.

Required correction:

- persist real evidence facts for owning checks;
- add report/artifact/delivery consistency validation;
- update report test counts, file scope, candidate component count, style ID, graph facts, owning-check count, and final commit SHA handling;
- prove the privacy scanner uses the authoritative configuration and explain/reconcile the approved-legacy-exception count rather than silently changing it.

## Preserve

Do not regress the following accepted CP4 behavior:

- sanitized-only CP4;
- private counters `0 / 0 / 0`;
- 10 bounded visual classes;
- 17 repo-local specialist/control Skills;
- fabrication / mechanism / experiment separation;
- Fishbone revision/focus/history preservation;
- concept imagery remains non-evidence only;
- empirical/literature/photo/plot AI prohibitions;
- 10/10 acceptance intent;
- route-specific CP3 style category requirements;
- material-semantic colors unresolved;
- SVG-first structured diagrams;
- native-shape threshold unresolved;
- FigureCritic mandatory before Layout;
- A01–A18 routing-only, geometry `not_run`;
- no production figure rendering;
- no PPTX/template/acceptance deck;
- production Group Meeting readiness `false`.

## Review gate

Checkpoint 4 remains **NOT APPROVED**.

Do not begin Checkpoint 5 / production Figure Stack until CP4-C1 through CP4-C6 are corrected and re-reviewed.
