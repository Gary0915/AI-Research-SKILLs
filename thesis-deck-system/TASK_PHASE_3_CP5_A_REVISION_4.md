# TASK — Phase 3 CP5-A Revision 4

## Status

CP5-A remains **NOT APPROVED**.

Reviewed implementation commit:

`9d08b344bf8963a3c5ef31daf198dbc38138fc75`

Implement only CP5A-E1 and CP5A-E2 below.

Do not begin CP5-B or later checkpoints.

---

## CP5A-E1 — execution-owned private-access lifecycle

The current session object is candidate-bound and hash-sealed, but completion is still caller-self-attested because a caller can directly call:

`bind_execution()` -> `complete_validation()` -> `seal()`

without any checkpoint validation actually executing under that session.

### Required invariant

A private-access evidence record may become authoritative only when an execution owner/runner proves this sequence:

1. establish execution ID and candidate identity;
2. create/bind the guard session internally;
3. execute the CP5-A validation/QA operation under that bound execution context;
4. record all guarded access attempts during execution;
5. mark validation complete only after the owned operation returns successfully;
6. seal the record internally during finalization;
7. bind evidence to execution/run/candidate/counters/hash;
8. only then permit CP5-A artifact finalization.

### Required implementation properties

- Direct caller construction of a session must not be sufficient to produce authoritative completed evidence.
- Direct caller invocation of a public `complete_validation()` state transition must not certify an unexecuted run.
- Prefer making completion/sealing internal to a CP5-A execution runner/context.
- `build_cp5a_artifacts()` must consume runner-owned sealed evidence, or the runner may own artifact construction itself.
- Candidate mismatch, run mismatch, evidence-hash mutation, nonzero guarded attempts, runner failure, or missing execution completion must fail closed.
- No private source may be opened.

### Required RED tests

At minimum:

- raw dictionary -> FAIL;
- unbound session -> FAIL;
- caller-created session cannot self-complete an authoritative execution -> FAIL;
- wrong run ID -> FAIL;
- wrong candidate hash -> FAIL;
- mutated evidence hash -> FAIL;
- validation callback raises/fails -> no completed evidence;
- alias/source/render attempt > 0 -> FAIL;
- real runner executes the validation callback, finalizes internally, and produces zero-attempt candidate-bound evidence -> PASS;
- the runner-produced evidence is accepted by CP5-A artifact finalization;
- private evidence identity/hash is persisted in owning QA.

Do not solve this by adding another caller-set boolean/token that merely renames self-attestation.

---

## CP5A-E2 — explicit positive marker-dimension policy

The current code now correctly reads positive-only dimensions from the persisted profile, but the profile does not include `markerWidth` or `markerHeight` while the report claims marker dimensions remain positive/profile-bound.

### Required implementation

Use the preferred v1 policy:

Add both:

- `markerWidth`
- `markerHeight`

to the typed persisted:

`coordinate_policy.positive_dimension_attributes`

Then ensure the existing profile-owned numeric validation rejects:

- `markerWidth="0"`
- negative `markerWidth`;
- `markerHeight="0"`;
- negative `markerHeight`.

Do not reintroduce a code-only union.

### Required RED tests

- positive markerWidth/markerHeight -> PASS;
- zero markerWidth -> FAIL numeric policy;
- negative markerWidth -> FAIL;
- zero markerHeight -> FAIL;
- negative markerHeight -> FAIL;
- removing either marker dimension from a mutated profile changes policy consistently or fails compatibility, but code must not silently restore positivity.

### Schema/profile

If the profile schema constrains the allowed members of `positive_dimension_attributes`, update it consistently and keep the contract closed.

Candidate-state coverage must include every changed profile/schema/test/source dependency.

---

## Execution-owned QA

Update/extend owning evidence so the final CP5-A evidence explicitly proves:

- runner-owned private-access lifecycle executed;
- the private record is not caller-self-attested;
- positive marker-dimension profile policy is active;
- zero/negative marker dimensions reject.

Do not use literal PASS flags.

---

## Validation

Run at minimum:

1. focused CP5-A Revision 4 RED->GREEN suite;
2. full CP1+CP2+CP3+CP4+CP5-A regression;
3. definitive disposable-worktree regression;
4. all CP5-A schemas + FormatChecker;
5. recursive schema closure;
6. private-access lifecycle runner/spoofing suite;
7. positive marker-dimension policy suite;
8. canonical round-trip/idempotence regression;
9. object/reference ID authority regression;
10. exact `viewBox` regression;
11. all CP4 plan/spec validation;
12. candidate-state mutation audit;
13. independently captured TESTED/CURRENT hash equality;
14. repository privacy scan;
15. staged privacy scan;
16. absolute private-path scan;
17. `git diff --check`;
18. exact scope audit;
19. commit/push;
20. remote SHA/tree/blob verification.

The privacy scanner may continue to use the already-approved caller-supplied ephemeral dictionary mechanism. Do not implement a production config loader.

---

## Preserve

Do not regress:

- canonical SVG namespace round-trip;
- canonical idempotence;
- profile-owned object/reference ID grammar;
- exact path/points/transform/viewBox grammar;
- full ScientificFigureSpec handoff validation;
- role/visual-class/child/addressability policy;
- CJK editable text and significant tspan whitespace;
- metadata-invisibility static QA;
- local typed marker/clip target resolution;
- repository/staged privacy scanner;
- one approved historical privacy exception;
- private alias/source/render attempts = 0/0/0;
- candidate-bound disposable regression;
- Scientific SVG as visual IR only;
- no scientific provenance authority in SVG.

---

## Not authorized

Do NOT start:

- CP5-B native capability registry;
- CP5-C FigureOutputManifest / Static FigureCritic;
- production Fishbone/mechanism/experiment/fabrication figures;
- plot/photo/literature production rendering;
- A01-A18 calibration;
- DrawingML compiler;
- template reconstruction;
- PPTX;
- acceptance deck;
- Phase 4.

---

## Report

Update:

`thesis-deck-system/reports/PHASE_3_CP5_A_IMPLEMENTATION_REPORT.md`

Add explicit CP5A-E1/E2 traceability, actual final focused/full test counts, runner-owned lifecycle summary, positive marker-dimension policy summary, candidate-state hash equality, privacy summary, and truthful later `not_run` statuses.

---

## Delivery

Return:

- repository
- branch
- implementation commit SHA
- pushed
- remote verification
- files added/modified/deleted
- focused test pass/fail
- full disposable regression pass/fail
- CP5A-E1/E2 traceability
- runner-owned private-access lifecycle summary
- marker positive-dimension profile summary
- owning QA count/status
- candidate-state component count
- tested/current hash/equality
- privacy scanner summary
- private alias/source/render counters
- later checkpoint statuses
- known failures
- blocked conditions
- technical debt
- unresolved questions

Only after commit, push, and remote verification write:

`READY_FOR_CP5_A_REVIEW: yes`

Then STOP.
