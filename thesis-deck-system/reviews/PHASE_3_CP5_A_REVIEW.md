# Phase 3 CP5-A Review

Reviewed implementation commit: `4dd7b2574c7f28d397685f8e22f3a2e34033758a`

## Verdict

**REVISE.** CP5-A has the correct architecture and substantial test coverage, but the current Scientific SVG language is not yet safe enough to become the shared production IR for CP5-D/E directors.

The revision is intentionally narrow. Preserve the existing CP5-A architecture, synthetic-only boundary, CJK/editable-text direction, candidate-bound disposable regression, and all later-checkpoint `not_run` states.

## CP5A-B1 — Make the profile the executable language authority

The task requires the versioned Scientific SVG profile to define the language, including allowed attributes by element and namespaced-attribute policy. The committed profile lists allowed elements and broad policies, while the executable per-element attribute grammar lives separately in the Python `ATTRS` constant. The validator also decides legality from that hard-coded table rather than from the persisted profile.

This creates two authorities that can drift.

Required correction:

- Persist the element-specific attribute contract in `scientific-svg-profile.json` and its closed schema.
- Persist/identify the controlled path, points, transform and namespace grammar versions in the profile.
- Make the validator derive its allowed element/attribute behavior from the validated profile, or fail if code-registered grammar IDs do not match the profile.
- A profile mutation must either change validation behavior deterministically or fail a profile/code compatibility gate; it must never be silently ignored.
- Keep parser implementation code in Python where appropriate, but the selected grammar/version must be profile-owned and explicit.

## CP5A-B2 — Enforce XML namespaces and semantic-role visual-class/child policy

The validator currently strips namespaces with `rsplit("}", 1)[-1]`. Root namespace is checked, but child-element and attribute namespaces are not fail-closed. A foreign namespaced element such as `evil:rect` can be interpreted as `rect`, and a foreign namespaced presentation attribute can be collapsed to an unqualified attribute during canonicalization.

Required correction:

- Every SVG child element must be in the approved SVG namespace unless an explicitly reviewed namespace exception exists.
- Reject foreign element namespaces.
- Reject foreign attribute namespaces by default. Do not normalize a foreign namespaced attribute into an unqualified presentation attribute.
- If any namespaced attribute is intentionally supported, define the exact namespace/local-name pair in the profile.
- Restrict `data-visual-class` to the intended location (prefer root-only unless a concrete object-level need is documented).

The semantic-role registry also persists `allowed_visual_classes`, `children_allowed`, and `addressable`, but the validator currently enforces only role membership and allowed element type.

Required correction:

- Determine the effective visual class from the schema-valid `ScientificFigureSpec`; if root `data-visual-class` is present it must exactly match the Spec.
- Enforce each role's `allowed_visual_classes` (`any` or the effective class).
- Enforce `children_allowed`.
- Enforce the registry's `addressable` policy rather than treating those fields as documentation-only.
- Add adversarial tests for cross-visual-class role contamination, child-policy violations, foreign namespaces and visual-class mismatch.

The synthetic corpus must no longer validate all ten fixtures against the first quantitative Figure Spec. Give each fixture an explicit schema-valid synthetic Spec binding (or an equivalent deterministic binding) matching its intended visual class.

## CP5A-B3 — Replace loose path/transform/points checks with a real controlled grammar

The current `_valid_path()` checks only a minimum number of numeric arguments after a command. It can accept malformed path command arity such as an extra unmatched coordinate. `_valid_transform()` validates function names and numeric-looking content but does not enforce transform arity (for example, malformed `matrix(...)` argument counts can pass). Points grammar does not enforce the minimum pair count required by polyline/polygon semantics.

Before production directors generate Fishbones and mechanism diagrams, the shared IR parser must reject malformed geometry deterministically.

Required correction:

- Implement a deterministic controlled SVG path parser/validator for the allowed command subset.
- Enforce command parameter-group arity, repeated groups, moveto semantics, closepath semantics, and arc flag constraints if arc commands remain supported.
- Enforce transform arity: translate 1/2; scale 1/2; rotate 1/3; matrix 6 (or document a stricter subset).
- Enforce finite values.
- Enforce at least two coordinate pairs for polyline and at least three for polygon.
- Add negative tests for excess/missing path arguments, malformed arc groups/flags, wrong matrix/rotate/translate arity and insufficient point counts.

If full SVG path support is unnecessary for CP5-D, it is acceptable to reduce the allowed path-command subset rather than implement permissive parsing.

## CP5A-B4 — Make execution QA fully execution-derived

The execution evidence has good candidate-hash and privacy-scan records, but `CP5A-PRIVATE-ACCESS` is constructed from a literal `True` with hard-coded zero counters. Several status dimensions (`resource_policy`, `canonicalization_hash`, `synthetic_corpus`) are also written as unconditional `pass` values rather than projected from owning checks.

Required correction:

- No literal/self-certifying owning PASS.
- Private-access counters must come from an execution-owned input/session record; missing/unbound evidence must fail closed.
- Add owning checks for the core CP5-A language dimensions, at minimum: profile/code authority, schema closure, namespace policy, role/visual-class policy, geometry grammar, CJK/editable text, resource policy, canonicalization determinism, synthetic corpus, privacy, candidate-bound regression.
- Derive `checkpoint-5a-qa.json` status dimensions from owning-check results rather than writing unconditional PASS fields.
- Strengthen CP4 freeze evidence: validate the full consumed CP4 plan/spec collections and relevant schema/identity bindings, not only the first Spec.

## CP5A-B5 — Preserve significant text whitespace and canonicalization semantics

Canonicalization intentionally preserves child order, which is correct. However child-tail handling drops whitespace-only tails. Inside editable SVG text, whitespace between adjacent `<tspan>` nodes can be presentation-significant.

Required correction:

- Preserve significant text/tspan whitespace according to the declared text policy.
- Add tests such as adjacent `<tspan>` nodes separated by a meaningful space and prove canonicalization does not remove visible spacing.
- Keep formatting-only whitespace outside text presentation semantics normalizable.
- Add namespace-aware canonicalization tests to prove canonicalization never changes a foreign namespaced object/attribute into an approved SVG presentation object.

## Report consistency

The report correctly records 39 focused tests and 355 disposable-regression tests, but the YAML footer's `commit_sha: final_delivery_after_remote_verification` is not a real commit identity. Do not attempt an impossible self-referential commit hash. Use an explicit neutral value such as `not_embedded_self_reference`/`null` with remote verification reported externally, or another repository-approved convention.

## Preserve

Do not regress:

- Scientific SVG as visual IR only, not a second Ledger;
- 15-element conservative direction unless a revision is evidence-backed;
- editable UTF-8 Chinese/English text;
- no production figures/PPTX/private access;
- minimal semantic metadata;
- static metadata-invisibility evidence only;
- safe portable resource policy;
- child/z-order preservation;
- repository-local `scientific-svg-authoring` and `semantic-svg-governor` Skills;
- candidate-bound disposable-worktree regression;
- CP5-B and later checkpoints remain `not_run`.

## Reviewer gate

Do not start CP5-B until CP5A-B1 through CP5A-B5 are implemented, tested, committed, pushed and remotely verified.
