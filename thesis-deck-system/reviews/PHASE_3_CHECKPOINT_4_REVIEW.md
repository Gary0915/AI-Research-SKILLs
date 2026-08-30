# Phase 3 Checkpoint 4 — Review

## Verdict

**REVISE.**

Reviewed implementation commit:

`a9d8065b00a222145e3efa0118065b3b9c9a8fbc`

Checkpoint 4 is not approved for downstream Figure production yet. The routing architecture is directionally correct, but six control-plane defects can cause a later director to consume the wrong style authority, accept a semantically mismatched Figure Spec, bypass FigureCritic/output-manifest gates, or reuse regression evidence that is not bound to the complete executable routing state.

Preserve the sanitized-only boundary, zero private access, SVG-first default, fabrication separation, Fishbone binding, no production rendering, no A01–A18 geometry calibration, and all later-stage `not_run` / `false` statuses.

---

## CP4-B1 — Visual Style Governor identity and route-specific readiness are not actually bound

The approved CP3 artifact currently has:

`style_profile_id = VSP003`

but CP4 hard-codes:

`style_profile_ref = VSP001`

in both router output and v4 Figure Plan/Figure Spec schemas. The implementation report also claims that plans reference `VSP001` while calling it the CP3 profile.

This is a broken provenance identity, not a cosmetic naming issue.

In addition, every plan currently receives the same hard-coded style categories:

- `body_composition`
- `line_style_grammar`
- `color_emphasis_grammar`

regardless of visual class. CP4 therefore does not actually evaluate the category-specific CP3 readiness that the task requires. Mechanism/Fishbone should care about connector/arrow grammar; plot/photo/literature routes have different style dependencies; shell/typography should be requested only when relevant.

### Required correction

- derive `style_profile_ref` from the consumed `visual-style-profile.json` identity;
- schema-bind the current consumed identity rather than a stale constant;
- derive required style categories per visual class;
- persist, per required category, the actual CP3 readiness status and allowed consumption mode (`recurring`, `provisional_with_flag`, `fallback`, `blocked/unresolved`);
- fail closed if the referenced profile ID or category status does not match the consumed CP3 artifact;
- unresolved material semantic colors remain blocked.

---

## CP4-B2 — ScientificFigureSpec semantic type is not discriminated by route

The CP4 builder currently maps every non-quantitative plan to:

`figure_type = vector_diagram`

This would misclassify future:

- real photos;
- literature figures;
- concept illustrations;
- other non-vector primary evidence classes.

The schema permits `real_photo`, `literature_figure`, and `concept_illustration`, but does not enforce route-consistent pairings among:

- visual class;
- Figure Spec type;
- director Skill;
- renderer class;
- canonical output target;
- evidence status.

As a result, a schema-valid future record can semantically masquerade as the wrong figure family.

### Required correction

Implement an explicit route-to-spec discriminator matrix. At minimum:

- quantitative result → `scientific_plot`;
- real experiment/photo → `real_photo`;
- literature route → `literature_figure`;
- organic concept → `concept_illustration`;
- mechanism / experiment schematic / fabrication / Fishbone / comparison / matrix composition → the explicitly authorized structured diagram type or another documented typed variant.

The v4 schema must reject mismatched class/type/director/renderer/output combinations.

---

## CP4-B3 — Execution-owned routing QA covers only three of ten visual classes

The committed synthetic acceptance set contains only:

- quantitative result;
- Fishbone;
- fabrication.

There are ten supported visual classes.

The unit test parametrization calls the remaining routes, but the persisted execution-owned QA does not. This makes several owning checks partial or vacuous.

For example, `CP4-SVG-FIRST` evaluates only the three persisted plans. If real photo, literature, or concept plans were added, the current blanket non-quantitative expression would not even represent the correct renderer policy. Likewise the persisted empirical/AI boundary does not execution-own the complete route table.

There is also no separate execution-owned visual-class coverage fact proving 10/10 classes were exercised.

### Required correction

Create a deterministic sanitized acceptance request for every supported visual class and persist/validate 10/10 route coverage.

Execution-owned QA must independently prove at least:

- visual-class coverage 10/10;
- specialist identity per class;
- class-appropriate renderer policy;
- source/evidence requirements;
- AI prohibition where applicable;
- non-evidence concept boundary;
- fabrication separation;
- Fishbone provenance;
- source-backed real/literature/image-matrix handling;
- native-shape fail-closed behavior.

Do not let a check PASS because the relevant class is absent from the acceptance set.

---

## CP4-B4 — The persisted Skill registry contains real bypass paths despite a correct-looking handoff_graph

The registry declares the desired graph:

`scientific_state → FigureProductionPlan → selected specialist → future renderer/output manifest → FigureCritic → APPROVED_FIGURE → Layout`

but the actual `routes` section still contains user workflows that hand scientific work directly toward `layout-director` without the new figure-router/output/FigureCritic chain. Examples include result pages, literature/mechanism pages, and Fishbone workflows.

There is a second graph inconsistency: several specialist Skill contracts hand directly to `figure-critic` while their declared output contracts are still specs/requests, not a renderer-produced output manifest. `figure-critic` itself declares `future_output_manifest` as its trigger/input.

The current `CP4-HANDOFF-NO-BYPASS` check only compares the literal `handoff_graph` list and plan handoff target; it does not validate the executable/user-route graph or per-Skill downstream graph.

### Required correction

Normalize the routing registry so every scientific visual path obeys the no-bypass rule.

- user routes that contain scientific visuals must enter `scientific-figure-router` before Layout;
- specialist director contracts must hand off to the correct future renderer/builder/output-manifest stage before FigureCritic;
- FigureCritic must never be handed a raw spec when its contract requires an output manifest;
- Layout must appear only after `APPROVED_FIGURE` for scientific visuals;
- validate all downstream targets and graph transitions, not only the declarative `handoff_graph` string list;
- legacy non-figure routes may remain only when explicitly classified as non-scientific-figure paths.

---

## CP4-B5 — Observation boundary is not fail-closed at router input

The router checks `claim_refs` and `evidence_refs` for concepts, but the request itself has no closed schema and unknown input keys are silently ignored.

Therefore a concept request could carry an empirical slot such as:

`observation_evidence_ref = E...`

or an experimental/quantitative/literature evidence-slot binding, and CP4 would currently ignore that field while still routing the concept as non-evidence.

That does not satisfy the explicit Scientific Method boundary in the task.

### Required correction

Introduce a closed schema-backed routing-request contract or an equivalent fail-closed validator before classification.

Explicitly model or reject empirical slot bindings, including at least:

- Observation evidence;
- empirical evidence refs;
- experimental image/evidence slot;
- quantitative result evidence slot;
- literature figure evidence slot.

For `organic_concept`, all empirical slot bindings must be absent/empty and `scientific_claim_support` must remain `forbidden`.

Unknown request fields that can affect scientific/evidence semantics must not be silently discarded.

Add adversarial tests for masquerading empirical slot fields.

---

## CP4-B6 — Candidate-state hashing is not yet complete regression binding

The execution artifact contains a composite component hash, but:

1. there is no execution-owned `CP4-DISPOSABLE-REGRESSION` check binding the reported 298/0 regression result to that exact composite state;
2. no persisted regression evidence object records candidate hash, test count, failure count, and disposable-worktree status;
3. only `skill-routing.yaml` is hashed; the 17 repo-local `SKILL.md` contracts that define routing behavior are not hashed;
4. `contracts.py`, which was modified and affects schema execution, is not hashed;
5. execution dependencies used by CP4 privacy/schema behavior are not explicitly covered by the candidate component contract.

The task explicitly requires source/schema/routing-registry/spec mutation to invalidate prior regression evidence.

### Required correction

Persist candidate-bound disposable regression evidence and make it an owning PASS condition.

The candidate state must include every execution-affecting CP4 source/contract, at minimum:

- all six consumed CP3 input hashes;
- CP4 router/control-plane source;
- `contracts.py` where CP4 schema registration affects execution;
- all CP4 schemas;
- `skill-routing.yaml`;
- all 17 repo-local `SKILL.md` contract hashes;
- any additional CP4 source dependency whose mutation changes routing/privacy/schema semantics.

Persist:

- component hash map;
- composite candidate-state hash;
- disposable-worktree flag;
- regression passed count;
- regression failed count;
- exact candidate-state hash tested.

Mutation of source, schema, routing YAML, or any Skill contract must invalidate old regression evidence.

---

## Required additional QA correction

The 13 owning checks are too coarse relative to the task's required owning dimensions. Do not increase the number cosmetically; instead make each required dimension execution-owned and evidence-bearing.

Boolean facts may be used for atomic outcomes, but key checks must persist inspectable counts/identities/hashes where applicable, especially:

- 10/10 visual-class coverage;
- 17/17 Skill contract coverage;
- 18/18 archetype routing coverage;
- route/type/director/renderer consistency;
- CP3 style profile ID and per-category readiness bindings;
- no-bypass graph edge audit;
- empirical-slot rejection counts;
- candidate-bound full regression evidence.

---

## Preserve

Do not regress the following accepted behaviors:

- CP3 remains approved and immutable except for strictly necessary compatibility fixes;
- CP4 remains sanitized-only;
- private alias/source/render attempts remain `0 / 0 / 0`;
- no private exemplar access;
- no production SVG/PDF/PNG/plot/image/PPTX;
- fabrication remains distinct from mechanism and experiment schematic;
- unknown fabrication conditions remain unknown;
- Fishbone revision/focus/history remain canonical bindings;
- structured diagrams remain SVG-first while native eligibility is unresolved;
- material semantic colors remain unresolved;
- FigureCritic remains mandatory before Layout;
- A01–A18 geometry calibration remains `not_run`;
- template reconstruction, acceptance deck, native PowerPoint remain `not_run`;
- production Group Meeting readiness remains `false`.

## Final reviewer status

`READY_FOR_CHECKPOINT_4_REVISION: yes`
