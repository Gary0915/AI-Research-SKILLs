# TASK — Phase 3 CP5-A Revision 3

## Status

CP5-A remains **NOT APPROVED**.

Implementation commit reviewed:

`6e0596268bc57dc713e05aabcd44fcfa99e70bca`

Implement only CP5A-D1 through CP5A-D4 below.

Do not begin CP5-B or later checkpoints.

---

## CP5A-D1 — Canonical SVG round-trip closure

The canonical Scientific SVG must remain inside the same Scientific SVG language.

### Required implementation

1. Preserve/reconstruct the approved SVG namespace in canonical output.
2. A valid source must satisfy:

   `validate(source, spec) = pass`

   `canonical = canonicalize(source)`

   `validate(canonical, spec) = pass`

3. `author_svg_for_spec()` must return canonical SVG that revalidates against the same `ScientificFigureSpec`.
4. Canonicalization must be idempotent:

   `canonicalize(canonical_svg).canonical_svg == canonical_svg`

   and canonical hashes remain stable.
5. Preserve:
   - child order;
   - z-order;
   - transforms;
   - CJK text;
   - editable `<text>/<tspan>`;
   - significant inter-`tspan` whitespace;
   - local marker/clip reference semantics.

### Required RED tests

- valid source -> canonical -> revalidate PASS;
- canonical root preserves SVG namespace semantics;
- canonicalization twice is identical;
- canonical hash is stable on the second pass;
- canonicalized marker reference still resolves;
- canonicalized clipPath reference still resolves;
- canonicalized CJK/tspan fixture remains valid.

---

## CP5A-D2 — One profile-owned object-ID grammar

Do not hard-code a second `obj-*` grammar inside local-reference validation.

### Required implementation

For `marker-start`, `marker-end`, `clip-path`, and same-document `href`:

1. parse exact wrapper syntax;
2. extract target ID as a string;
3. validate the extracted ID using the active profile-owned `self.object_id_re` or an equivalent single registered object-ID matcher;
4. resolve the target;
5. type-check the target where required.

Do not embed a separate object-ID regex in reference parsing.

### Required RED tests

- mutate the profile object-ID pattern to a supported alternate pattern;
- object with alternate valid ID passes object-ID validation;
- matching local marker/clip reference to that alternate ID also passes;
- malformed target ID fails;
- valid wrapper + invalid target ID fails;
- exact wrapper + missing target fails;
- exact wrapper + wrong target type fails;
- profile-ID mutation cannot create object/reference grammar drift.

If the product decision is that the object-ID profile must remain one fixed registered pattern in v1, then reject any alternate profile pattern at validator construction. In that case local references must still derive from that same registered matcher; do not duplicate the regex.

---

## CP5A-D3 — Lifecycle-bound private-access execution evidence

A newly-created and immediately-sealed access-session object must not certify a completed CP5-A execution.

### Required architecture

Introduce or reuse a checkpoint execution runner/context with the following lifecycle:

1. create execution identity;
2. create/bind private-access guard session;
3. bind candidate/test context;
4. execute checkpoint validation/QA operations;
5. record guarded attempt counters throughout execution;
6. seal the access record only during execution finalization;
7. persist an evidence record bound to:
   - execution ID;
   - tested candidate hash or execution candidate identity;
   - checkpoint/run identity;
   - guard counters;
   - evidence hash;
8. only then allow artifact finalization.

`build_cp5a_artifacts()` / final artifact writing must consume execution-owned evidence. It must not treat an arbitrary freshly-instantiated session as an authoritative trust token.

### Required RED tests

- raw dict -> FAIL;
- unsealed session -> FAIL;
- freshly-created-and-immediately-sealed session with no bound run identity -> FAIL;
- evidence from different candidate/run -> FAIL;
- mutated evidence hash -> FAIL;
- nonzero alias/source/render attempt -> FAIL;
- completed lifecycle-bound zero-attempt execution record -> PASS;
- private evidence identity is persisted in owning QA.

No private source may actually be opened for these tests.

---

## CP5A-D4 — Closed numeric/reference invariants

### Exact `viewBox`

Validate `viewBox` with an exact consuming grammar.

Required:

- exactly four finite numbers;
- width and height positive;
- controlled legal separators only;
- no repeated/empty comma groups;
- no unconsumed characters.

Reject at least:

- `0,,0 10 10`
- `0 0 10`
- `0 0 10 10 garbage`
- `0 0 NaN 10`
- `0 0 0 10`

### Positive dimension policy

Any additional positive-only dimension behavior not explicitly declared by the persisted profile must be either:

- added to a typed profile policy, or
- compatibility-bound to an explicit registered grammar/policy identity.

Do not silently extend the declared profile semantics in code.

### Canonical/local-reference invariant

After canonicalization, all same-document references must retain the same target identity and target type.

---

## Execution-owned QA additions

Add execution-derived owning checks or extend existing checks so the final evidence explicitly proves:

- `CP5A-CANONICAL-ROUNDTRIP`
- `CP5A-CANONICAL-IDEMPOTENCE`
- `CP5A-OBJECT-REFERENCE-ID-AUTHORITY`
- `CP5A-VIEWBOX-GRAMMAR`
- `CP5A-PRIVATE-ACCESS-LIFECYCLE`

Names may vary if traceability is unambiguous.

Do not add literal PASS flags.

Relevant status dimensions must fail if these owning checks fail.

---

## Candidate-state binding

Update candidate-state coverage for every new execution-affecting source/schema/test/profile/Skill dependency introduced by Revision 3.

The definitive full regression must be run in a disposable worktree.

Capture TESTED candidate hash from the actual tested candidate and recompute CURRENT candidate hash independently.

Required:

- `tested_hash == current_hash`
- `tests_failed == 0`
- disposable worktree = true.

---

## Preserve

Do not regress:

- profile-owned element/attribute policy;
- strict namespace rejection;
- role visual-class / child / addressability policy;
- exact path/points/transform grammar;
- CP4 ScientificFigureSpec schema/route validation;
- synthetic fixture/spec binding;
- CJK editable text;
- significant tspan whitespace;
- metadata invisibility static QA;
- local typed marker/clip targets;
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
- production Fishbone SVG;
- production mechanism diagrams;
- experiment schematic rendering;
- fabrication rendering;
- plot/photo/literature production rendering;
- A01–A18 calibration;
- DrawingML compiler;
- template reconstruction;
- PPTX;
- acceptance deck;
- Phase 4.

---

## Validation

Run at minimum:

1. focused CP5-A Revision 3 RED→GREEN suite;
2. full CP1+CP2+CP3+CP4+CP5-A regression;
3. definitive disposable-worktree regression;
4. all CP5-A schemas + FormatChecker;
5. recursive schema closure;
6. canonical SVG round-trip suite;
7. canonicalization idempotence suite;
8. profile-owned object/reference ID suite;
9. exact viewBox grammar suite;
10. private-access lifecycle spoofing/binding suite;
11. CJK/significant-whitespace regression;
12. typed local-reference regression;
13. all CP4 plan/spec validation;
14. candidate-state mutation audit;
15. independently captured tested/current hash equality;
16. repository privacy scan;
17. staged privacy scan;
18. absolute private-path scan;
19. `git diff --check`;
20. exact scope audit;
21. commit/push;
22. remote SHA/tree/blob verification.

---

## Report

Update:

`thesis-deck-system/reports/PHASE_3_CP5_A_IMPLEMENTATION_REPORT.md`

Add explicit CP5A-D1–D4 traceability and actual final test counts.

Keep:

- CP5-B through CP5-I = `not_run`;
- production rendering = `not_run`;
- PPTX = `not_run`;
- production Group Meeting ready = `false`.

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
- CP5A-D1–D4 traceability
- canonical round-trip summary
- canonical idempotence summary
- object/reference ID authority summary
- viewBox grammar summary
- private-access lifecycle evidence summary
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
