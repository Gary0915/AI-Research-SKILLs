# Phase 3 CP5-A — Scientific SVG Language and Static SVG QA

## Scope and status

CP5-A establishes a closed, synthetic-only Scientific SVG visual-authoring IR. It does not render production figures, resolve private sources, create the CP5-C FigureOutputManifest/Static FigureCritic gate, or compile PPTX. Scientific truth remains in the Ledger/materialization/ScientificFigureSpec chain; SVG carries only local visual semantics.

## CP5-A1–A19 traceability

| Requirement | Implemented evidence | Status |
| --- | --- | --- |
| A1 profile | `scientific-svg-profile.json`, closed schema, `SSVG-P001` v1.0.0 | pass |
| A2 allowlist | 15 controlled SVG elements; unknown/executable/browser elements reject | pass |
| A3 attributes | per-element attribute allowlists and deterministic presentation attributes | pass |
| A4 metadata | minimal root/object local metadata; provenance attributes prohibit | pass |
| A5 IDs | stable object-ID grammar, uniqueness and required-addressability checks | pass |
| A6 roles | versioned local visual role registry and element compatibility checks | pass |
| A7 geometry | required viewBox; finite numeric, path, points and transform checks | pass |
| A8 CJK text | editable Unicode `<text>/<tspan>` fixtures and canonicalization checks | pass |
| A9 resources | safe relative/synthetic data policy; remote, absolute and traversal references reject | pass |
| A10 validator | deterministic XML, policy, identity, role, reference, privacy and binding checks | pass |
| A11 canonicalization | versioned, child-order-preserving canonicalization plus SHA-256 identity | pass |
| A12 invisibility | static presentation-AST comparison after approved metadata stripping | pass |
| A13 corpus | ten non-production synthetic language fixtures | pass |
| A14 Skills | repository-local `scientific-svg-authoring` and `semantic-svg-governor` | pass |
| A15 schemas | eight CP5-A JSON schemas, typed and closed at core nesting | pass |
| A16 CP4 freeze | consumed CP4 plans/specs/schemas/routing bind into candidate state | pass |
| A17 execution QA | independently tested/current candidate hashes, owning checks and zero private counters | pass |
| A18 RED coverage | focused suite exercises the required negative/mutation contracts | pass |
| A19 status truth | later work remains explicitly not run; production readiness is false | pass |

## CP5A-B1–B5 revision traceability

| Revision | Corrected implementation | Status |
| --- | --- | --- |
| B1 profile authority | Profile-owned element/attribute contract, namespace policy, and registered path/points/transform grammar bindings; unknown bindings fail closed. | pass |
| B2 namespaces and roles | Foreign element/attribute namespaces reject; root visual class binds to FigureSpec; local role visual-class, child, and addressability policies execute. | pass |
| B3 exact geometry | Exact path command groups, transform arity, arc flags, and polyline/polygon minimum-point rules replace count-only parsing. | pass |
| B4 execution-owned QA | Bound private-access record, expanded owning checks, and all CP4 plan/spec collection validation project final status dimensions. | pass |
| B5 canonicalization | Canonical text preserves meaningful inter-`tspan` space while normalizing formatting-only whitespace; foreign namespaces cannot canonicalize as SVG. | pass |

## CP5A-C1–C6 revision 2 traceability

| Revision | Corrected implementation | Status |
| --- | --- | --- |
| C1 profile/code authority | The persisted profile now drives or compatibility-binds object-ID matching, root contract, semantic placement, transform functions, resource modes, coordinate/text policy, canonicalization, and closed controlled attributes. Unsupported declarations fail validator construction. | pass |
| C2 exact consuming grammar | Path, points, and transform parsers consume the complete input, reject empty/repeated separators and malformed exponents, require initial moveto, and retain exact controlled arities/arc flags. | pass |
| C3 FigureSpec handoff | `author_svg_for_spec()` validates the full CP4 ScientificFigureSpec schema and registered route discriminator before binding SVG identity. | pass |
| C4 private access evidence | A sealed `Cp5aPrivateAccessSession` owns guarded counters; arbitrary dictionaries and unsealed records cannot certify zero private access, and the sealed evidence identity/hash is persisted. | pass |
| C5 owning QA | CP5-A persists 21 execution-derived profile, namespace, attribute, role, grammar, text, resource, local-reference, corpus, CP4-freeze, privacy, private-access, and regression checks. Status dimensions are projected from those checks. | pass |
| C6 local references | Marker and clip references require exact `url(#object-id)` syntax and resolve to same-document typed targets. | pass |

## Execution recovery and regression evidence

- Automatic usage-limit stop encountered: yes; automatic stops encountered: 2; workspace preserved: yes; local recovery snapshot preserved: yes.
- Authorized Phase 1 cleanup: 39 supplied textual lines, 38 unique paths, including one duplicate `thesis-deck-system/artifacts/phase1/render_revised/slide-1.png`; 19 modified + 19 deleted paths restored from `HEAD`; unreviewed paths: 0.
- CP5-A draft preservation after cleanup: pass. The earlier snapshot remains retained locally; three CP5-A implementation files advanced after that snapshot during the same authorized session and are bound by the final candidate hash below.
- Focused pre-stop correction tests: 14 passed / 0 failed. Final focused CP5-A Revision 2 suite: 68 passed / 0 failed.
- Preliminary active-worktree regression: 353 passed / 0 failed; classification: `preliminary_only`; acceptance eligible: false because it ran in the active worktree and mutated unrelated generated artifacts.
- Interrupted disposable regression: reached 93%; `incomplete_not_accepted` because completion and exit evidence were unavailable.
- First resumed disposable run: 381 passed / 4 failed; rejected as an environment-invalid run because the temporary checkout lacked Git safe-directory authorization for CP1/CP2 privacy tests.
- Definitive CP5-A Revision 2 disposable regression rerun: 385 passed / 0 failed; tested candidate hash `3190717039e684053d7a3ab63017696ca06c8b82a621bd1e2a4a3e6977446baf`; independently recomputed current candidate hash is identical; equality: pass.

## Results

- Profile: `SSVG-P001` / `1.0.0`; 15 allowed SVG elements, profile-owned attribute contracts, three registered grammars, and 34 local semantic roles.
- Semantic metadata is limited to profile/version, figure ID, object ID, local semantic role, and optional visual class. Scientific provenance is prohibited in SVG.
- Metadata invisibility is static AST evidence only—not pixel or render equivalence.
- Privacy scanner: repository and staged scans executed; unexcepted findings `0`; approved historical exceptions `1`.
- Private alias/source/render attempts: `0 / 0 / 0`.

## Later checkpoint status

| Dimension | Status |
| --- | --- |
| Scientific SVG language / static validator / semantic governance | pass |
| CJK static text / resource policy / canonicalization and hash / synthetic corpus | pass |
| CP5-B native capability registry | not_run |
| CP5-C Static FigureCritic | not_run |
| Production figure rendering / render critic / qualitative review | not_run |
| A01–A18 calibration / DrawingML compiler / template reconstruction / acceptance deck | not_run |
| Native PowerPoint acceptance | not_run |
| Production Group Meeting ready | false |

## Known limitations

CP5-A does not establish professor visual fidelity, native PowerPoint fidelity, a production FigureOutputManifest, Static FigureCritic, production rendering, or any acceptance deck. Native capability remains unmeasured rather than inferred.

```yaml
codex_report:
  phase: PHASE_3_CP5_A
  status: awaiting_review
  branch: codex/thesis-deck-system
  commit_sha: not_embedded_self_reference
  artifacts:
    - artifacts/phase3/scientific-svg-profile.json
    - artifacts/phase3/semantic-svg-role-registry.json
    - artifacts/phase3/scientific-svg-synthetic-corpus.json
    - artifacts/phase3/checkpoint-5a-execution-evidence.json
    - artifacts/phase3/checkpoint-5a-qa.json
  render_previews: []
  tests_run:
    - focused CP5-A suite
    - full disposable-worktree regression
  tests_passed:
    focused_cp5a_revision_2: 68
    full_disposable_regression: 385
  tests_failed:
    focused_cp5a_revision_2: 0
    full_disposable_regression: 0
  known_failures: []
  deviations: []
  reviewer_questions: []
  next_action_requested: REVIEW
```
