# Phase 3 CP5-A Revision 3 Review

## Verdict

**REVISE**

Reviewed implementation commit:

`6e0596268bc57dc713e05aabcd44fcfa99e70bca`

CP5-A remains **not approved**. CP5-B is not authorized.

## What is now accepted

The prior CP5A-C1–C6 corrections are substantially implemented:

- profile/code compatibility is fail-closed for major executable policy fields;
- path/points/transform parsing is now consuming and materially stricter;
- `author_svg_for_spec()` validates the CP4 `ScientificFigureSpec` through the registered schema/route validator;
- role visual-class, child, and addressability policy is enforced;
- local marker/clip references are exact and typed;
- CP4 freeze covers all 10 plans and all 10 specs;
- 21 owning QA checks are persisted;
- the definitive disposable regression is 385 passed / 0 failed with tested/current candidate-hash equality;
- private exemplar/source/render counters remain 0 / 0 / 0;
- CP5-B through CP5-I remain not run.

These behaviors must be preserved.

## Remaining blockers

### CP5A-D1 — Canonical Scientific SVG is not closed under its own language

`canonicalize_svg()` serializes every element using the local tag name only. `xml.etree.ElementTree` does not retain the default `xmlns` declaration as a normal attribute, and `_canonical_element()` does not re-emit it on the root.

Therefore a valid namespaced input such as:

```xml
<svg xmlns="http://www.w3.org/2000/svg" ...>
```

can canonicalize to a root equivalent to:

```xml
<svg ...>
```

without the SVG namespace declaration.

That canonical result is not a valid CP5-A Scientific SVG under the validator's own namespace contract. `author_svg_for_spec()` returns this canonical SVG as the authoring output, so the canonical IR is currently not guaranteed to revalidate.

Required property:

`valid Scientific SVG -> canonicalize -> canonical Scientific SVG -> validate against the same FigureSpec -> PASS`

Canonicalization must preserve/reconstruct the approved namespace semantics and must be idempotent.

### CP5A-D2 — Same-document reference grammar still bypasses profile-owned object-ID policy

Object IDs are now profile-driven through `profile.id_policy.pattern`, but local references still hard-code:

`obj-[a-z][a-z0-9-]{0,63}`

for `marker-start`, `marker-end`, `clip-path`, and same-document `href`.

This creates language drift: a future profile-compatible object-ID pattern can accept an object ID while local references to that ID are rejected by a separate hard-coded regex.

Required behavior:

- parse exact `url(#...)` / `#...` syntax;
- extract the target ID;
- validate the extracted ID with the validator's active profile-owned object-ID matcher;
- then resolve and type-check the target.

No second object-ID grammar may exist inside the reference validator.

### CP5A-D3 — Private-access evidence is still self-attestable at finalization time

`Cp5aPrivateAccessSession` is better than a caller-provided dictionary, but any caller can still instantiate:

```python
Cp5aPrivateAccessSession("CP5A-ACCESS-001").seal()
```

immediately before `build_cp5a_artifacts()` and receive a valid zero-attempt record. The current focused test explicitly treats that freshly-created object as acceptable.

This proves only that *that object* recorded no guarded attempts; it does not prove the validation execution lifecycle was instrumented by that session.

Required behavior:

- the authoritative CP5-A execution runner creates the private-access session before validation starts;
- all guarded private-access entrypoints for the checkpoint bind to that same execution session;
- the session is sealed only after the checkpoint execution finishes;
- the produced evidence is bound to the CP5-A execution identity and tested candidate state/run evidence;
- the final artifact builder consumes the execution-owned record rather than accepting a newly-created session as a trust token.

A newly-created-and-immediately-sealed session at finalization must fail acceptance.

### CP5A-D4 — Remaining closed-language numeric/reference invariants need direct proof

The closed Scientific SVG language should also prove the following before becoming the shared production IR:

1. `viewBox` uses an exact consuming four-number grammar. Inputs with repeated/empty separators such as double commas must not normalize into valid input accidentally.
2. Canonical SVG round-trip preserves namespace, child order, z-order, CJK/editable text, and significant `tspan` whitespace.
3. Canonicalization is idempotent: canonicalizing an already canonical valid SVG produces the same canonical SVG/hash.
4. Marker/clip local references remain valid after canonicalization and revalidation.
5. Any positive-dimension behavior not directly stored in the profile (for example marker dimensions, if retained) must be explicitly compatibility-bound to a registered grammar/policy rather than silently extending the profile language.

## Required final reviewer properties

Before CP5-A approval, the reviewer must be able to verify:

1. canonical output is itself schema/language-valid Scientific SVG;
2. canonicalization is namespace-safe and idempotent;
3. exactly one profile-owned object-ID grammar governs both objects and local references;
4. private-access zero evidence is lifecycle-bound rather than finalizer-self-certified;
5. exact `viewBox` and local-reference round-trip mutation tests pass;
6. owning QA contains execution-derived facts for these properties;
7. CP5-B and all production figure work remain `not_run`.

## Scope

This is a narrow CP5-A language-hardening revision. Do not add figure rendering, native capability, FigureCritic, professor calibration, DrawingML, PPTX, or production scientific figures.
