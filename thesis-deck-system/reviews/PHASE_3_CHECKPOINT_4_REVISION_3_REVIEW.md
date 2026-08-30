# Phase 3 Checkpoint 4 — Revision 3 Review

## Verdict

**REVISE**

Reviewed implementation commit: `7fbbfcf6db6f08b1da10402ed652c1e0bb16d20d`.

This revision closes most CP4 control-plane gaps: the real CP3 style profile is required, ten classes are exercised, a closed routing-request schema exists, candidate-state regression evidence carries an independent tested hash, `FigureOutputManifest` is normalized, and the report/test counts are reconciled.

Checkpoint 4 is still not safe to hand to production Figure Directors because the public router can return a plan that its own registered route discriminator rejects, and the plan→ScientificFigureSpec handoff drops route policy that downstream Skills need.

## Blocking findings

### CP4-D1 — Router may emit a contract-invalid plan

`route_figure_request()` validates the request and computes a route but does not validate the returned FigureProductionPlan before returning it.

The request schema does not cross-bind every visual class to its allowed evidence provenance. A concrete example exists in the focused suite: `literature_figure` is routed from the default synthetic request whose `evidence_status` is `empirical`; the route succeeds, even though the registered `_FIGURE_ROUTES` discriminator requires `literature_evidence` for that class. The later batch builder happens to use a corrected acceptance request, so persisted production artifacts validate, but the router API itself is not fail-closed.

The evidence policy also must not be reduced to a single evidence status when a visual class legitimately supports multiple provenance modes. A mechanism explanation may be derived from empirical results or from literature synthesis; a fair comparison may likewise compare empirical or literature-backed alternatives. The route policy needs an explicit allowed-evidence set rather than an accidental one-value coupling.

### CP4-D2 — Source requirement is not preserved as a v4 route contract

The route table distinguishes `canonical_data`, `real_evidence`, `literature_source`, `structured_spec`, and `non_evidence_only`, but the v4 FigureProductionPlan only persists the lossy boolean `source_asset_required`.

Downstream control needs the actual source requirement identity. `canonical_data` and `structured_spec` are both currently reduced to `false`; therefore a downstream consumer cannot reconstruct the route requirement from the plan alone.

Persist a controlled v4 `source_requirement` and include it in route discrimination and QA.

### CP4-D3 — ScientificFigureSpec drops critical FigureProductionPlan policy

The repo-local specialist Skills consume `ScientificFigureSpec`, not the original request. The current spec projection drops several control-plane decisions, including at least:

- `figure_plan_id` / explicit plan binding;
- `scientific_claim_support`;
- `source_requirement` / source-asset policy;
- `ai_generation_allowed`;
- `native_shape_eligibility`;
- route-specific style-category requirements / consumption states;
- blocked material-semantic-color state;
- requested archetype when relevant.

This means CP5 directors could receive a schema-valid ScientificFigureSpec without the exact restrictions CP4 resolved. The control plane must preserve the safety-critical policy through the specialist handoff, or the specialist input contract must explicitly require both FigureProductionPlan and ScientificFigureSpec. Do not rely on implicit re-derivation.

### CP4-D4 — Graph audit does not validate every declared downstream edge

The graph validator checks each Skill's `handoff_target`, but `allowed_downstream` is itself a declared edge set. An extra unknown or contract-incompatible entry in `allowed_downstream` can exist while the handoff target remains valid.

Audit every declared downstream edge, not only the selected handoff target. Keep the canonical path:

`FigureProductionPlan → specialist → FigureOutputManifest → FigureCritic → APPROVED_FIGURE → Layout`.

### CP4-D5 — Final QA must own the new end-to-end handoff invariants

Add execution-derived checks proving:

- every public router result validates as a FigureProductionPlan before return;
- every persisted ScientificFigureSpec is losslessly bound to one plan for all safety-critical policy fields;
- source-requirement counts reconcile across the 10-class acceptance set;
- every declared `allowed_downstream` edge resolves and is contract-compatible;
- route/evidence alternate modes are deterministic and schema-valid;
- candidate-bound disposable regression covers the new schema/source/Skill state.

## Accepted and frozen behavior

Do not regress:

- actual CP3 style identity `VSP003` consumption without a production fallback;
- closed `FigureRoutingRequest`;
- 10/10 visual-class acceptance coverage;
- 17 repo-local Skills;
- private alias/source/render counters `0 / 0 / 0`;
- concept imagery as non-evidence only;
- empirical/literature AI prohibitions;
- fabrication separation and unknown-condition preservation;
- Fishbone revision/focus/history provenance;
- SVG-first structured-diagram policy;
- unresolved native-shape threshold;
- unresolved material-semantic colors;
- mandatory FigureCritic before Layout;
- 18/18 A01–A18 routing with geometry calibration `not_run`;
- independent candidate/tested hash equality;
- one reviewed historical privacy exception and zero unexcepted findings;
- no production rendering, PPTX, template reconstruction, benchmark, or acceptance deck.

## Review conclusion

Checkpoint 4 is structurally close to closure. The final correction is not another architecture expansion: make the router itself fail-closed, preserve the resolved route policy into the specialist input, and audit all declared graph edges. Only then should Vector Figure Production begin.
