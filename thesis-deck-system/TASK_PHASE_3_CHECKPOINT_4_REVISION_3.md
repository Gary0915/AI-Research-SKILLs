# TASK — Phase 3 Checkpoint 4 Revision 3

## Authorization

Implement **CP4-D1 through CP4-D5 only**.

Do not begin production figure rendering, A01–A18 geometry calibration, template reconstruction, benchmarks, PPTX, acceptance deck, Phase 4, or public/global Skill registration.

## Authoritative reviewed implementation

- reviewed commit: `7fbbfcf6db6f08b1da10402ed652c1e0bb16d20d`
- review: `thesis-deck-system/reviews/PHASE_3_CHECKPOINT_4_REVISION_3_REVIEW.md`

## CP4-D1 — Router output must be fail-closed

`route_figure_request()` must never return a FigureProductionPlan that fails the registered `figure-production-plan` contract.

Required flow:

1. validate `FigureRoutingRequest`;
2. resolve route;
3. build plan;
4. validate the final v4 plan with the canonical SchemaRegistry / semantic route discriminator;
5. return only if valid.

A public router call with a mismatched route/evidence combination must fail immediately.

### Evidence-policy matrix

Define a controlled allowed-evidence policy rather than assuming every visual class has exactly one evidence status.

At minimum preserve these strict classes:

- quantitative measured result → empirical only;
- real experiment photo → empirical only;
- literature figure → literature_evidence only;
- image matrix of real evidence → empirical only;
- organic concept → non_evidence only.

For structured explanatory classes where the scientific source may legitimately differ, define explicit allowed sets, for example:

- mechanism explanation → empirical and/or literature_evidence as supported by canonical refs;
- fair comparison → empirical and/or literature_evidence when source bindings satisfy the route;
- other structured method/history routes → document and test the allowed provenance modes rather than inheriting one accidental default.

Do not let evidence provenance change the specialist visual class silently.

Add RED tests proving the router itself rejects invalid combinations, not only later batch validation.

## CP4-D2 — Persist source requirement in v4 plans/specs

Promote the route-table source requirement into a first-class controlled field:

`canonical_data | real_evidence | literature_source | structured_spec | non_evidence_only`

Persist it in every v4 FigureProductionPlan.

Include it in cross-field route discrimination and QA.

Do not rely only on `source_asset_required`; that boolean is lossy.

Persist compatible source requirement information in ScientificFigureSpec as well.

Required mutations:

- plot + literature_source → fail;
- literature figure + canonical_data → fail;
- real photo + structured_spec → fail;
- concept + real_evidence → fail;
- structured SVG route + non_evidence_only → fail unless it is the explicitly allowed concept class.

## CP4-D3 — Preserve plan policy into ScientificFigureSpec

Every specialist input must retain the safety-critical decisions resolved by CP4.

Preferred approach: ScientificFigureSpec contains an explicit `figure_plan_ref` and copies the controlled policy fields required for downstream enforcement.

At minimum preserve:

- figure plan reference;
- scientific claim support;
- source requirement;
- source-asset-required state;
- AI-generation allowance;
- native-shape eligibility;
- route-specific required style categories;
- style-category readiness / consumption mode / source profile refs;
- style blocked/unresolved policy including material-semantic-color blocking;
- requested archetype when present;
- canonical scientific/source/provenance bindings already present.

All fields must be strongly typed and fail-closed.

The plan→spec projection must be deterministic and validation-owned.

Add a `CP4-PLAN-SPEC-POLICY-BINDING` owning check proving 10/10 specs reconcile exactly with their source plans for every controlled field.

Mutation of one policy field in a spec must fail schema/semantic binding QA.

Do not ask specialist Skills to re-infer these policies from visual class.

## CP4-D4 — Audit all graph edges

Treat every entry in `allowed_downstream` as a declared graph edge.

For every Skill and every downstream entry validate:

- downstream node exists or is an explicitly typed virtual contract node;
- producer output contract is compatible with downstream input contract;
- handoff target is contained in allowed downstream;
- no raw spec goes to FigureCritic;
- no scientific pre-Critic node goes to Layout;
- FigureCritic input is canonical `FigureOutputManifest`;
- FigureCritic output is `APPROVED_FIGURE`;
- Layout input is `APPROVED_FIGURE`.

Persist graph evidence:

- node count;
- declared edge count;
- handoff edge count;
- dangling edge count;
- contract mismatch count;
- bypass count;
- extra/unselected downstream edge count if retained.

Unknown extra `allowed_downstream` entries must fail closed.

## CP4-D5 — Execution-owned QA and candidate binding

Extend CP4 QA with real evidence for:

- router-output self-validation count = 10/10 acceptance plans;
- alternate evidence-mode validation count;
- source-requirement distribution/count reconciliation;
- plan→spec policy binding count = 10/10;
- graph all-edge audit;
- 17/17 Skill registry integrity;
- 18/18 archetype routing;
- style profile identity/readiness;
- schema closure including all new fields/contracts;
- repository/staged privacy scan with the approved historical exception;
- independent tested/current candidate-state hash equality;
- disposable regression counts.

No literal PASS.

Candidate-state hashing must include every modified source/schema/routing/Skill dependency introduced by this revision.

## Required RED tests

At minimum add direct tests for:

1. literature visual requested as empirical fails at router boundary;
2. quantitative visual requested as literature evidence fails;
3. valid literature-backed mechanism route succeeds if allowed by the documented matrix;
4. invalid evidence mode for mechanism fails;
5. router cannot return a plan rejected by SchemaRegistry;
6. source-requirement mutation fails;
7. every spec has exactly one source plan reference;
8. plan/spec scientific-claim-support mismatch fails;
9. plan/spec AI policy mismatch fails;
10. plan/spec native-shape policy mismatch fails;
11. plan/spec style-category policy mismatch fails;
12. plan/spec blocked material-color policy mismatch fails;
13. unknown `allowed_downstream` node fails;
14. additional incompatible `allowed_downstream` edge fails;
15. producer/consumer contract mismatch fails;
16. pre-Critic Layout bypass fails;
17. tested candidate hash becomes stale after any new schema/source mutation.

## Preserve

Do not regress any behavior listed as accepted/frozen in the Revision 3 review.

Private counters must remain `0 / 0 / 0`.

Production statuses must remain:

- figure rendering: `not_run`;
- FigureCritic visual acceptance: `not_run`;
- archetype geometry calibration: `not_run`;
- template reconstruction: `not_run`;
- acceptance deck: `not_run`;
- native PowerPoint: `not_run`;
- production Group Meeting ready: `false`.

## Validation

Run:

- focused CP4 Revision 3 RED→GREEN;
- CP1+CP2+CP3+CP4 package regression;
- full disposable-worktree regression;
- six CP3 input validations;
- FigureRoutingRequest schema validation;
- all CP4 output schemas + FormatChecker;
- recursive schema closure;
- router-output self-validation audit;
- evidence-policy matrix tests;
- source-requirement reconciliation;
- plan→spec policy-binding audit;
- all-edge graph audit;
- 17/17 Skill audit;
- 18/18 archetype audit;
- candidate-state mutation audit;
- repository/staged privacy scan;
- report/artifact consistency audit;
- `git diff --check`;
- remote SHA/tree/blob verification.

## Delivery

Return:

- repository;
- branch;
- commit SHA;
- pushed yes/no;
- remote verification yes/no;
- report path;
- files added/modified/deleted;
- focused/full regression pass/fail counts;
- CP4-D1–D5 traceability;
- router self-validation summary;
- evidence-policy matrix summary;
- source-requirement summary;
- plan→spec policy-binding summary;
- graph node/edge/dangling/mismatch/bypass summary;
- Skill registry and A01–A18 coverage;
- candidate-state component count/current hash/tested hash/equality;
- privacy scanner summary;
- private alias/source/render counters;
- all production not-run/blocked statuses;
- known failures;
- technical debt;
- unresolved questions.

Only after commit, push, and remote verification write:

`READY_FOR_CHECKPOINT_4_REVIEW: yes`

Then STOP.
