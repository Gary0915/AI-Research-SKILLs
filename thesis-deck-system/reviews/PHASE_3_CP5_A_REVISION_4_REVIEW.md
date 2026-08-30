# Phase 3 CP5-A Revision 3 Review

## Verdict

**REVISE — two final contract-closure blockers remain.**

Reviewed implementation commit:

`9d08b344bf8963a3c5ef31daf198dbc38138fc75`

The implementation closes the canonical namespace/idempotence, profile-owned object/reference ID grammar, exact `viewBox` parsing, privacy scanner finalization, and candidate-bound disposable regression requirements. The committed execution evidence reports 77 focused tests and 394 disposable-regression tests with zero failures and matching candidate hash `9125a492a1aa4fe1381f8ebe794d4c2cbf1329cecb891916efcd833c632fa5e5`.

CP5-A is still not approved because the following two issues contradict the Revision 3 contract or committed report claims.

---

## CP5A-E1 — private-access lifecycle is still caller-self-attested

`Cp5aPrivateAccessSession` now stores `run_id`, `candidate_state_hash`, `_validation_completed`, and requires them before `seal()`. However the caller can still perform the complete trust transition directly:

```python
session = Cp5aPrivateAccessSession("CP5A-ACCESS-001")
session.bind_execution("CP5A-EXEC-001", candidate_hash)
session.complete_validation()
session.seal()
```

No checkpoint runner owns `complete_validation()`, no validation operation is required to execute between bind and complete, and `build_cp5a_artifacts()` merely verifies the sealed fields/hash after the caller has self-declared completion.

The committed positive test follows this same pattern: it manually binds, manually calls `complete_validation()`, seals, then passes the object into `build_cp5a_artifacts()`.

This does not satisfy `TASK_PHASE_3_CP5_A_REVISION_3.md`, which requires:

1. create execution identity;
2. create/bind private-access guard session;
3. bind candidate/test context;
4. **execute checkpoint validation/QA operations**;
5. record guarded counters throughout execution;
6. **seal only during execution finalization**;
7. persist run/candidate/counter/hash identity;
8. only then allow artifact finalization.

The task explicitly says `build_cp5a_artifacts()` must consume **execution-owned evidence** and must not treat an arbitrary freshly-instantiated session as an authoritative trust token.

### Required correction

Introduce a minimal CP5-A execution context/runner (or equivalent unforgeable state transition) that owns the lifecycle. The public caller must not be able to make an unexecuted session authoritative merely by calling `complete_validation()`.

Acceptable designs include a runner that:

- creates/binds the session internally;
- executes the CP5-A validation/QA callback or artifact-build preflight under that context;
- marks completion only after those operations return successfully;
- seals internally during finalization;
- returns immutable/sealed evidence to `build_cp5a_artifacts()` or writes artifacts itself.

The important invariant is behavioral, not class naming:

> no actual execution under the bound context -> no valid completed private-access evidence.

Add RED tests proving a caller cannot fabricate a completed record by direct lifecycle calls, while the real runner can produce a valid zero-attempt record.

---

## CP5A-E2 — positive marker-dimension claim is not backed by the profile

Revision 3 correctly removed the hidden code-only union:

`positive_dimension_attributes | {markerWidth, markerHeight}`

and now uses only the persisted profile list. But the committed `scientific-svg-profile.json` still declares:

```json
"positive_dimension_attributes": ["width", "height", "r", "rx", "ry"]
```

It does **not** include `markerWidth` or `markerHeight`.

Therefore negative/zero marker dimensions are no longer rejected by the positive-dimension policy; they are only required to be finite. This directly conflicts with the implementation report statement:

> “Positive marker dimensions remain profile/compatibility-bound.”

and with the broader D4 report claim that non-positive dimensions reject.

### Required correction

Choose one explicit v1 language policy and make code/profile/tests/report agree.

Preferred for this Scientific SVG subset:

- add `markerWidth` and `markerHeight` to the typed persisted `positive_dimension_attributes` policy;
- validate zero/negative marker dimensions as failures;
- add focused RED tests;
- keep the report claim.

Alternative only if intentionally designed:

- explicitly document that marker dimensions are finite-only, not positive-only;
- remove the false report/QA claim and add a test proving the intended policy.

Do not restore a hidden code-only union.

---

## Confirmed passing areas

The reviewer found the following Revision 3 changes materially implemented and suitable to preserve:

- canonical output re-emits the SVG namespace;
- canonical SVG is revalidated during `author_svg_for_spec()`;
- canonicalization is idempotent in the focused tests;
- local marker/clip references extract the wrapper and use the active profile-owned object-ID matcher;
- `viewBox` uses the exact consuming number-sequence parser;
- all CP4 plans/specs remain candidate-bound;
- repository/staged privacy evidence reports 0/0 findings and one approved historical exception;
- private alias/source/render counters remain 0/0/0;
- focused 77/0 and disposable 394/0 results are recorded with matching candidate hash;
- CP5-B through CP5-I remain `not_run` and production readiness remains false.

---

## Scope

Do not begin CP5-B. Only correct CP5A-E1 and CP5A-E2, regenerate CP5-A execution/QA/report artifacts, rerun the focused suite and definitive disposable regression against the new candidate, and return for review.
