# Phase 3 CP5-A Revision 2 Review

Reviewed commit: `e8a8b6da76aa33193b832a83c0263ac6e3e4c726`

Verdict: **REVISE**.

The revision materially improves CP5-A and closes the previously identified namespace, visual-class/role, geometry arity, synthetic binding, significant-whitespace, candidate-state, and QA-projection gaps. However CP5-A is the shared production IR for all later Figure Directors, so the remaining language-authority and parser gaps must be closed before CP5-B is authorized.

## Accepted improvements

- Profile now owns the 15-element per-element attribute contract and explicit grammar bindings.
- Foreign element/attribute namespaces fail closed.
- Root visual class binds to the ScientificFigureSpec when present.
- Role allowed visual classes, child policy, and addressability are enforced.
- Synthetic corpus has explicit fixture→FigureSpec bindings.
- Path/transform/points validation is stricter than the prior minimum-count implementation.
- Significant inter-`tspan` whitespace is preserved for the tested case.
- CP4 plan/spec collections are validated as a set.
- Status dimensions are projected from owning checks rather than unconditional literals.
- Candidate-state evidence is bound to 24 components and a disposable regression.

## Remaining blockers

### CP5A-C1 — Profile authority is still partial

The profile is declared as the authoritative language contract, but several mutable profile policies are still ignored by execution code.

Examples:

- `id_policy.pattern` is mutable in the profile schema while object-ID validation still uses the hard-coded `OBJECT_ID_RE`.
- `transform_policy.allowed_functions` can be mutated while `_valid_transform()` still uses a hard-coded function/arity map.
- `resource_policy.allowed_reference_modes` can be mutated while `_validate_reference()` still accepts the hard-coded local/bundle/data modes.
- `namespace_policy.approved_attribute_namespaces` may contain records but the implementation rejects every namespaced attribute unconditionally.
- `semantic_attribute_placement`, `root_contract.required_attributes`, and other language-affecting policy fields can drift from execution behavior without profile/code compatibility failure.

Required correction: either derive execution behavior from those profile fields or fail profile/code compatibility when a profile value is not exactly supported by the registered implementation. No language-affecting profile mutation may be silently ignored.

Also close the profile schema vocabulary for `element_attribute_contract`: arbitrary attribute strings must not allow a profile mutation to introduce an uncontrolled attribute such as `style` without a compatibility failure.

### CP5A-C2 — Path/points lexical grammar is not yet exact

`_valid_path()` validates command arity but does not yet enforce full SVG path lexical/moveto semantics.

Concrete failures still accepted by the implementation include conceptually invalid forms such as:

- a path beginning with `L` instead of initial `M/m`;
- malformed numeric lexemes where the character whitelist is accepted but the token regex silently skips invalid characters, e.g. incomplete exponent forms;
- other cases where token extraction does not prove that every non-whitespace source character was consumed by the grammar.

`_valid_points()` and transform argument splitting also collapse repeated separators, so malformed forms such as double commas can normalize into valid numeric lists rather than fail closed.

Required correction: implement a consuming tokenizer/parser for the controlled path, points, and transform grammars. The parser must prove complete lexical consumption, initial moveto semantics, exact command groups, exact separators, finite values, and current arc constraints.

### CP5A-C3 — Authoring handoff must validate the full ScientificFigureSpec

`author_svg_for_spec()` currently passes an arbitrary dict to `ScientificSvgValidator.validate()`, which only consumes fields such as `figure_id` and `visual_class`. A caller can therefore provide a non-schema-valid pseudo-Spec with those fields and still obtain a validated authoring handoff.

Required correction: the canonical authoring handoff must first validate the supplied ScientificFigureSpec against the approved CP4 schema/cross-field discriminator, then validate SVG against that Spec. Invalid FigureSpec input must fail before an APPROVED CP5-A authoring result is possible.

### CP5A-C4 — Private-access evidence remains caller-asserted rather than execution-owned

The prior literal `True` was removed, but `private_access_evidence` is still an arbitrary caller-supplied dictionary. A fabricated `{"execution_id":"CP5A-ACCESS-001", ... zeros ...}` satisfies the current gate.

Required correction: bind CP5-A private-access evidence to an instrumented execution/session object or sealed canonical record whose counters are derived from the actual guarded entrypoints. Add a spoofed-zero negative test proving a manually constructed zero-count object cannot self-certify the checkpoint.

### CP5A-C5 — Owning QA is still missing required execution evidence for several policy families

The revision task required real owning checks for semantic role/visual class, role child/addressability policy, significant whitespace, profile/code policy authority, and other core gates. The persisted owning checks currently include profile authority, namespace, geometry, resource, static validator, metadata, CJK, canonicalization, corpus, privacy, candidate and private access, but they do not independently persist evidence that the negative role/visual-class/child/addressability and significant-whitespace gates actually executed.

Required correction: add explicit execution-derived owning checks/facts for at least:

- role + visual-class incompatibility rejection;
- child-policy rejection;
- addressability rejection;
- significant inter-`tspan` whitespace preservation;
- full profile/code compatibility across all executable language-policy fields;
- canonical FigureSpec schema validation at authoring handoff.

Final status dimensions must continue to project from owning checks.

### CP5A-C6 — Local SVG references need exact syntax and target resolution

`_validate_reference()` currently accepts local references through prefix checks such as `startswith("url(#obj-")`, which can accept malformed suffixes and does not prove that the referenced object ID exists or is suitable for the reference kind.

Required correction:

- exact local-reference grammar;
- reject trailing junk;
- resolve marker/clip references to an existing in-figure object ID;
- where practical, enforce target kind (`marker-*` → `marker`, `clip-path` → `clipPath`);
- no missing/dangling local references.

## Release gate

Do **not** authorize CP5-B until CP5A-C1 through CP5A-C6 are resolved and regression evidence is regenerated for the exact candidate.

Preserve all accepted CP5-A boundaries: Scientific SVG remains visual IR only; no production figures, no private exemplar access, no PPTX, no native-capability claims, and all later checkpoints remain `not_run`.
