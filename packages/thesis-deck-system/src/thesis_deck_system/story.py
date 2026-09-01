"""Hypothesis-layer story compilation and hard professor-rule validation."""

from __future__ import annotations

from .contracts import Finding


def _format_result_metrics(metrics: object) -> str:
    """Project typed result metrics into editable presentation text.

    The source object stays structured; a SlideSpec must not leak a Python
    dictionary representation into a visual field.
    """
    if not isinstance(metrics, list):
        return ""
    items = []
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        name = str(metric.get("name", "metric"))
        value, uncertainty = metric.get("value"), metric.get("uncertainty")
        units = str(metric.get("units") or "")
        semantics = str(metric.get("uncertainty_semantics") or "")
        if isinstance(value, (int, float)) and isinstance(uncertainty, (int, float)):
            items.append(f"{name}: {value}{units} ± {uncertainty}{units} {semantics}".strip())
    return "; ".join(items)


def _spec(layer: dict, role: str, ordinal: int, source_cursor: int, *, object_ref: str | None = None) -> dict:
    layer_id = layer["hypothesis_layer_id"]
    return {
        "slide_id": f"S-{layer_id}-{role.upper().replace('_', '-')}-{ordinal:02d}",
        "hypothesis_layer_ref": layer_id,
        "hypothesis_layer_revision": layer["revision"],
        "semantic_role": role,
        "combined_roles": [role],
        "source_cursor": source_cursor,
        "object_ref": object_ref,
        "fishbone_snapshot_ref": layer.get("fishbone_snapshot_ref") if role == "fishbone_locator" else None,
        "fishbone_focus_refs": layer.get("fishbone_focus_refs", []) if role == "fishbone_locator" else [],
    }


def compile_hypothesis_layer(layer: dict, *, source_cursor: int) -> list[dict]:
    sequence: list[tuple[str, str | None]] = [
        ("hypothesis_title", layer.get("hypothesis_claim_ref")),
        ("problem_definition", layer.get("problem_ref")),
        ("fishbone_locator", None),
        ("observation_problem", layer.get("research_block_refs", [None])[0]),
        ("literature_mechanism", layer.get("research_block_refs", [None])[0]),
    ]
    sequence.extend(("experiment_design", ref) for ref in layer.get("experiment_order", layer.get("experiment_refs", [])))
    result_refs = layer.get("result_order", layer.get("result_refs", []))
    # Each persisted result receives its own governed result page.  A
    # comparison archetype remains available for an explicit comparison spec,
    # but never collapses distinct RESxxx statements into duplicate or
    # metadata-only pages.
    sequence.extend(("result_single", ref) for ref in result_refs)
    sequence.extend([
        ("layer_integrated_discussion", layer.get("layer_discussion_ref")),
        ("layer_summary_decision", layer.get("layer_summary_ref")),
    ])
    if layer.get("transition_ref"):
        sequence.append(("hypothesis_transition", layer["transition_ref"]))
    specs = [_spec(layer, role, index, source_cursor, object_ref=ref) for index, (role, ref) in enumerate(sequence, 1)]
    findings = validate_story_order(layer, specs)
    if findings:
        raise ValueError("invalid hypothesis story: " + ",".join(finding.rule_id for finding in findings))
    return specs


def validate_story_order(layer: dict, specs: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    roles = [spec.get("semantic_role") for spec in specs]
    for spec in specs:
        combined = set(spec.get("combined_roles", []))
        if {"hypothesis_title", "problem_definition"} <= combined:
            findings.append(Finding("P-HARD-01", "professor_style_logic", "Hypothesis and Problem were merged", spec.get("slide_id", "")))
    for required in ("hypothesis_title", "problem_definition", "fishbone_locator", "layer_integrated_discussion", "layer_summary_decision"):
        if required not in roles:
            findings.append(Finding("P-HARD-02" if required == "fishbone_locator" else "P2-STORY-MISSING-ROLE", "professor_style_logic", f"Missing required role {required}"))
    if "layer_integrated_discussion" in roles:
        discussion_index = roles.index("layer_integrated_discussion")
        result_indices = [index for index, role in enumerate(roles) if role in {"result_single", "result_comparison"}]
        if len(result_indices) != len(layer.get("result_refs", [])) or any(index > discussion_index for index in result_indices):
            findings.append(Finding("P-HARD-05", "scientific_reasoning", "Integrated Discussion appears before the complete result set"))
    return findings


def _stage_id(state: dict, ref: str | None) -> str | None:
    if not ref:
        return None
    if ref in state.get("stages", {}):
        return ref
    candidate = f"ST-{ref}"
    return candidate if candidate in state.get("stages", {}) else ref


def compile_hypothesis_layer_from_state(state: dict, layer_id: str, *, source_cursor: int) -> list[dict]:
    """Compile only from a cursor-materialized state, never from the seed fixture."""
    layer = state.get("hypothesis_layers", {}).get(layer_id)
    if not layer:
        raise ValueError(f"hypothesis layer {layer_id} is not materialized")
    return compile_hypothesis_layer(layer, source_cursor=source_cursor)


def _stage_ref(state: dict, ref: str | None) -> dict:
    stage_id = _stage_id(state, ref)
    return state.get("stages", {}).get(stage_id, {}) if stage_id else {}


def _role_ready(state: dict, layer_id: str, role: str, object_ref=None) -> bool:
    """Return whether a cursor materializes the scientific object a role presents."""
    layer = state.get("hypothesis_layers", {}).get(layer_id)
    if not layer:
        return False
    if layer.get("hypothesis_claim_ref") not in state.get("claims", {}):
        return False
    block_id = (layer.get("research_block_refs") or [None])[0]
    block = state.get("blocks", {}).get(block_id)
    if not block:
        return False
    if role == "hypothesis_title":
        return True
    if role == "problem_definition":
        return layer.get("problem_ref") in state.get("problems", {})
    if role == "fishbone_locator":
        fishbone = layer.get("fishbone_snapshot_ref", {})
        key = f"{fishbone.get('fishbone_id')}@{fishbone.get('revision')}"
        return key in state.get("fishbone_revisions", {})
    if role in {"observation_problem", "literature_mechanism", "mechanism_solution"}:
        required = {
            "observation_problem": ["observation"],
            "literature_mechanism": ["literature", "mechanism"],
            "mechanism_solution": ["mechanism", "solution"],
        }[role]
        return all(block.get("stage_refs", {}).get(name) in state.get("stages", {}) for name in required)
    if role in {"experiment_design", "result_single", "result_comparison"}:
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        stages = [_stage_ref(state, ref) for ref in refs]
        if not stages or any(not stage or stage.get("status") == "pending" for stage in stages):
            return False
        if role == "experiment_design":
            return all(stage.get("stage_type") == "experiment" for stage in stages)
        result_stages = [stage for stage in stages if stage.get("stage_type") == "result"]
        if not result_stages or any(not stage.get("data", {}).get("summary") for stage in result_stages):
            return False
        evidence = state.get("evidence", {})
        if any(any(ref not in evidence for ref in stage.get("evidence_refs", [])) for stage in result_stages):
            return False
        block_assets = [state.get("assets", {}).get(ref, {}) for ref in block.get("asset_refs", [])]
        return any(asset.get("asset_type") == "data_plot" for asset in block_assets)
    if role == "layer_integrated_discussion":
        return object_ref in state.get("layer_discussions", {})
    if role == "layer_summary_decision":
        summary = state.get("layer_summaries", {}).get(object_ref)
        return bool(summary and summary.get("decision_ref") in state.get("decisions", {}))
    if role == "hypothesis_transition":
        return object_ref in state.get("hypothesis_transitions", {})
    return False


def compile_master_story_from_ledger(ledger) -> list[dict]:
    """Project every persisted hypothesis layer and transition in causal order.

    This is the reusable Master-story driver.  It discovers identifiers from
    replayed events and never assumes a first/current two-layer fixture.
    """
    events = ledger.replay()
    final_state = ledger.materialize(len(events))
    creation_events = [event for event in events if event.event_type == "hypothesis_layer_created"]
    creation_events.sort(key=lambda event: event.cursor)
    transitions_by_from: dict[str, list] = {}
    for event in events:
        if event.event_type == "hypothesis_transition_recorded":
            transitions_by_from.setdefault(str(event.payload.get("from_layer_ref")), []).append(event)
    specs: list[dict] = []
    for creation in creation_events:
        layer_id = str(creation.payload["hypothesis_layer_id"])
        layer = final_state.get("hypothesis_layers", {}).get(layer_id)
        if not layer:
            raise ValueError(f"materialized layer missing: {layer_id}")
        logical = compile_hypothesis_layer(layer, source_cursor=creation.cursor)
        for raw in [item for item in logical if item.get("semantic_role") != "hypothesis_transition"]:
            ready_cursor = next(
                (
                    event.cursor
                    for event in events[creation.cursor - 1 :]
                    if _role_ready(ledger.materialize(event.cursor), layer_id, raw["semantic_role"], raw.get("object_ref"))
                ),
                None,
            )
            if ready_cursor is None:
                raise ValueError(f"no materializable cursor for {layer_id}/{raw['semantic_role']}/{raw.get('object_ref')}")
            raw["source_cursor"] = ready_cursor
            raw["stage_source_cursors"] = {raw["semantic_role"]: ready_cursor}
            specs.append(raw)
        for transition_event in sorted(transitions_by_from.get(layer_id, []), key=lambda event: event.cursor):
            transition = transition_event.payload
            specs.append(
                _spec(
                    layer,
                    "hypothesis_transition",
                    len([item for item in specs if item.get("hypothesis_layer_ref") == layer_id]) + 1,
                    transition_event.cursor,
                    object_ref=transition.get("transition_id"),
                )
            )
            specs[-1]["stage_source_cursors"] = {"hypothesis_transition": transition_event.cursor}
    return specs


def content_from_materialized_state(state: dict, layer_id: str, role: str, object_ref=None, *, meeting_projection: dict | None = None) -> str:
    """Turn canonical materialized objects into presentation prose."""
    if role == "progress_todo":
        projection = meeting_projection or {}
        commitments = projection.get("previous_commitments", [])
        current = projection.get("current_layer_id", layer_id)
        lines = [f"Current position｜{current}"]
        for action in commitments:
            owner = action.get("owner", {}).get("display_name", action.get("owner", "")) if isinstance(action.get("owner"), dict) else action.get("owner", "")
            due = action.get("target_window", {}).get("due", "")
            lines.append(f"Commitment｜{action.get('action_item_id')}｜{action.get('status')}｜Owner: {owner}｜Due: {due}")
            lines.append(f"Dependencies｜{', '.join(action.get('dependency_refs', action.get('dependencies', [])))}｜Parallel: {action.get('parallelizable')}")
        return "\n".join(lines)
    layer = state["hypothesis_layers"][layer_id]
    claim = state["claims"].get(layer["hypothesis_claim_ref"], {})
    problem = state["problems"].get(layer["problem_ref"], {})
    if role == "hypothesis_title":
        prediction = claim.get("falsifiable_predictions", [{}])[0].get("observation_that_falsifies", "")
        return f"Hypothesis｜{claim.get('text', '')}\nFalsifier｜{prediction}\nResearch question｜{layer.get('research_question', '')}"
    if role == "problem_definition":
        return f"Problem｜{problem.get('problem_statement', '')}\nPrevious finding｜{'; '.join(problem.get('previous_findings', []))}\nConflict｜{problem.get('unresolved_conflict', '')}\nResearch question｜{problem.get('research_question', '')}\nScope｜{problem.get('scope', '')}"
    if role == "fishbone_locator":
        ref = layer.get("fishbone_snapshot_ref", {})
        return f"Historical snapshot｜{ref.get('fishbone_id')} rev{ref.get('revision')}\nFocus branch｜{', '.join(layer.get('fishbone_focus_refs', []))}\nImmutable map; current branch highlighted."
    if role in {"observation_problem", "literature_mechanism", "mechanism_solution"}:
        block = state["blocks"].get(layer["research_block_refs"][0], {})
        refs = block.get("stage_refs", {})
        obs = state["stages"].get(refs.get("observation"), {}).get("data", {})
        lit = state["stages"].get(refs.get("literature"), {}).get("data", {})
        mech = state["stages"].get(refs.get("mechanism"), {}).get("data", {})
        sol = state["stages"].get(refs.get("solution"), {}).get("data", {})
        provenance_links = [*state["stages"].get(refs.get("mechanism"), {}).get("claim_refs", []), *state["stages"].get(refs.get("mechanism"), {}).get("evidence_refs", [])]
        return (f"Observation｜{obs.get('observation', '')}\nProblem｜{obs.get('problem', '')}\nResearch question｜{block.get('research_question', {}).get('text', '')}\n"
                f"Literature consensus｜{lit.get('consensus', '')}\nAlternatives｜{'; '.join(lit.get('disagreements_or_alternatives', []))}\nGap｜{lit.get('research_gap', '')}\nImplication｜{lit.get('implication_for_hypothesis_or_strategy', '')}\n"
                f"Mechanism｜{mech.get('mechanism', '')}\nEvidence/claim link｜{'; '.join(provenance_links)}\nStrategy｜{sol.get('strategy', '')}\nSuccess criterion｜{sol.get('success_criterion', '')}")
    if role == "experiment_design":
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        chunks = []
        for ref in refs:
            stage = state["stages"].get(_stage_id(state, ref), {})
            data = stage.get("data", {})
            chunks.append(f"{ref}｜IV: {data.get('independent_variables', '')}\nControlled variables: {data.get('controlled_variables', '')}\nControls/baselines: {data.get('controls_baselines', '')}\nSample plan: {data.get('sample_plan', '')}\nN/replicates: {data.get('sample_plan', {}).get('replicates', '')}\nMetrics/units: {data.get('measured_outputs', '')}\nMethod: {data.get('instrumentation_method_refs', '')}\nPrediction: {data.get('predicted_outcomes', '')}\nDecision rule: {data.get('decision_rules', '')}")
        return "\n\n".join(chunks)
    if role in {"result_single", "result_comparison"}:
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        chunks = []
        for ref in refs:
            data = state["stages"].get(_stage_id(state, ref), {}).get("data", {})
            chunks.append(f"{ref}｜{data.get('summary', '')}\nMetrics｜{_format_result_metrics(data.get('metrics', []))}")
        return "\n".join(chunks)
    if role == "layer_integrated_discussion":
        discussion = state["layer_discussions"].get(object_ref, {})
        return f"Supporting｜{', '.join(discussion.get('supporting_results', []))}\nContradicting｜{', '.join(discussion.get('contradicting_results', [])) or 'none'}\nCross-experiment pattern｜{discussion.get('cross_experiment_pattern', '')}\nMechanism assessment｜{discussion.get('mechanism_assessment', '')}\nAlternatives｜{'; '.join(discussion.get('alternative_explanations', []))}\nRemaining uncertainty｜{discussion.get('remaining_uncertainty', '')}"
    if role == "layer_summary_decision":
        summary = state["layer_summaries"].get(object_ref, {})
        decision = state["decisions"].get(summary.get("decision_ref"), {})
        return f"Answered｜{summary.get('answered', '')}\nHypothesis status｜{summary.get('hypothesis_status', '')}\nDecision｜{decision.get('choice', '')}: {decision.get('rationale', '')}\nUnresolved｜{summary.get('remaining_unresolved', '')}\nNext question｜{summary.get('next_question', '')}\nNext Step｜{', '.join(summary.get('next_step_refs', []))}"
    transition = state["hypothesis_transitions"].get(object_ref, {})
    return f"Previous hypothesis｜{transition.get('previous_hypothesis_claim_ref')}\nKey results｜{', '.join(transition.get('key_result_refs', []))}\nNot explained｜{transition.get('unexplained', '')}\nNew observation｜{', '.join(transition.get('observation_or_uncertainty_refs', []))}\nTherefore｜{transition.get('rationale', '')}\nNew hypothesis｜{transition.get('new_hypothesis_claim_ref')}"


def semantic_fields_from_materialized_state(state: dict, layer_id: str, role: str, object_ref=None, *, meeting_projection: dict | None = None, combined_roles: list[str] | None = None) -> dict[str, dict[str, str]]:
    """Return role-scoped, machine-addressable audience-visible science fields."""
    layer = state["hypothesis_layers"][layer_id]
    block = state.get("blocks", {}).get((layer.get("research_block_refs") or [None])[0], {})
    refs = block.get("stage_refs", {})
    stages = state.get("stages", {})
    roles = list(combined_roles or [role])
    output: dict[str, dict[str, str]] = {}

    def text(value) -> str:
        if isinstance(value, list):
            return "; ".join(str(item) for item in value) or "none"
        if isinstance(value, dict):
            return "; ".join(f"{key}: {item}" for key, item in value.items())
        return str(value or "")

    for current_role in roles:
        claim = state.get("claims", {}).get(layer.get("hypothesis_claim_ref"), {})
        problem = state.get("problems", {}).get(layer.get("problem_ref"), {})
        if current_role == "hypothesis_title":
            output[current_role] = {
                "hypothesis_statement": text(claim.get("text")),
                "falsifiable_prediction": text((claim.get("falsifiable_predictions") or [{}])[0].get("observation_that_falsifies")),
                "research_question": text(layer.get("research_question")),
            }
        elif current_role == "problem_definition":
            output[current_role] = {
                "previous_finding": text(problem.get("previous_findings")),
                "unresolved_conflict": text(problem.get("unresolved_conflict") or problem.get("problem_statement")),
                "research_question": text(problem.get("research_question") or layer.get("research_question")),
            }
            if problem.get("scope"):
                output[current_role]["scope"] = text(problem["scope"])
        elif current_role == "fishbone_locator":
            snapshot = layer.get("fishbone_snapshot_ref", {})
            output[current_role] = {"historical_snapshot": f"{snapshot.get('fishbone_id')} rev{snapshot.get('revision')}", "current_focus": text(layer.get("fishbone_focus_refs"))}
        elif current_role == "observation_problem":
            data = stages.get(refs.get("observation"), {}).get("data", {})
            output[current_role] = {"observation": text(data.get("observation")), "research_question": text(block.get("research_question", {}).get("text") or layer.get("research_question"))}
        elif current_role == "literature_mechanism":
            literature = stages.get(refs.get("literature"), {}).get("data", {})
            mechanism = stages.get(refs.get("mechanism"), {})
            output[current_role] = {
                "consensus": text(literature.get("consensus")),
                "disagreement_alternatives": text(literature.get("disagreements_or_alternatives")),
                "research_gap": text(literature.get("research_gap")),
                "implication": text(literature.get("implication_for_hypothesis_or_strategy")),
                "mechanism": text(mechanism.get("data", {}).get("mechanism")),
                "evidence_claim_link": text([*mechanism.get("claim_refs", []), *mechanism.get("evidence_refs", [])]),
            }
        elif current_role == "mechanism_solution":
            mechanism = stages.get(refs.get("mechanism"), {})
            solution = stages.get(refs.get("solution"), {}).get("data", {})
            output[current_role] = {
                "mechanism": text(mechanism.get("data", {}).get("mechanism")),
                "evidence_claim_link": text([*mechanism.get("claim_refs", []), *mechanism.get("evidence_refs", [])]),
                "strategy": text(solution.get("strategy")),
                "success_criterion": text(solution.get("success_criterion")),
            }
        elif current_role == "experiment_design":
            experiment_ref = object_ref[0] if isinstance(object_ref, list) else object_ref
            data = _stage_ref(state, experiment_ref).get("data", {})
            sample = data.get("sample_plan", {})
            output[current_role] = {
                "independent_variables": text(data.get("independent_variables")),
                "controlled_variables": text(data.get("controlled_variables")),
                "control_baseline": text(data.get("controls_baselines")),
                "sample_plan": text(sample),
                "replicates": text(sample.get("replicates")),
                "measured_outputs": text(data.get("measured_outputs")),
                "units": text(data.get("measured_outputs")),
                "instrumentation_method": text(data.get("instrumentation_method_refs")),
                "predicted_outcomes": text(data.get("predicted_outcomes")),
                "decision_rule": text(data.get("decision_rules")),
            }
        elif current_role in {"result_single", "result_comparison"}:
            result_ref = object_ref[-1] if isinstance(object_ref, list) else object_ref
            stage = _stage_ref(state, result_ref)
            metrics = stage.get("data", {}).get("metrics", [])
            output[current_role] = {
                "result_identity": text(result_ref),
                "result_statement": text(stage.get("data", {}).get("summary")),
                "metric_value_uncertainty": _format_result_metrics(metrics),
            }
        elif current_role == "layer_integrated_discussion":
            discussion_ref = object_ref if role == current_role else layer.get("layer_discussion_ref")
            discussion = state.get("layer_discussions", {}).get(discussion_ref, {})
            output[current_role] = {
                "supporting_results": text(discussion.get("supporting_results")),
                "contradicting_results": text(discussion.get("contradicting_results")),
                "non_discriminating_results": text(discussion.get("non_discriminating_results")),
                "cross_experiment_pattern": text(discussion.get("cross_experiment_pattern")),
                "mechanism_assessment": text(discussion.get("mechanism_assessment")),
                "alternative_explanations": text(discussion.get("alternative_explanations")),
                "remaining_uncertainty": text(discussion.get("remaining_uncertainty")),
            }
        elif current_role == "layer_summary_decision":
            summary_ref = object_ref if role == current_role else layer.get("layer_summary_ref")
            summary = state.get("layer_summaries", {}).get(summary_ref, {})
            decision = state.get("decisions", {}).get(summary.get("decision_ref"), {})
            output[current_role] = {
                "answered_question": text(summary.get("answered")),
                "hypothesis_status": text(summary.get("hypothesis_status")),
                "decision": text([decision.get("choice"), decision.get("rationale")]),
                "unresolved_items": text(summary.get("remaining_unresolved")),
                "next_question": text(summary.get("next_question")),
                "next_step": text(summary.get("next_step_refs")),
            }
        elif current_role == "hypothesis_transition":
            transition = state.get("hypothesis_transitions", {}).get(object_ref, {})
            output[current_role] = {
                "prior_hypothesis": text(transition.get("previous_hypothesis_claim_ref")),
                "key_prior_results": text(transition.get("key_result_refs")),
                "unresolved_point": text(transition.get("unexplained")),
                "precursor_observation": text(transition.get("observation_or_uncertainty_refs")),
                "derivation_rationale": text(transition.get("rationale")),
                "new_hypothesis": text(transition.get("new_hypothesis_claim_ref")),
            }
        elif current_role == "progress_todo":
            commitments = (meeting_projection or {}).get("previous_commitments", [])
            output[current_role] = {
                "prior_commitment": text([item.get("action_item_id") for item in commitments]),
                "current_position": text((meeting_projection or {}).get("current_layer_id")),
                "parallel_work": text([item.get("workstream") for item in commitments]),
            }
    return output


def content_slots_from_materialized_state(state: dict, layer_id: str, role: str, object_ref=None, *, meeting_projection: dict | None = None, combined_roles: list[str] | None = None) -> dict[str, str]:
    """Compile slot-bound scientific content from one materialized cursor.

    `content.body` remains a human-readable compatibility concatenation; it
    is never the authoritative source used for placement.  Each governed slot
    receives a separately persisted string generated from the same state.
    """
    combined_roles = list(combined_roles or [role])
    body = content_from_materialized_state(state, layer_id, role, object_ref, meeting_projection=meeting_projection)
    line_map = {}
    for line in body.splitlines():
        if "｜" in line:
            key, value = line.split("｜", 1)
            line_map.setdefault(key, value)
    layer = state.get("hypothesis_layers", {}).get(layer_id, {})
    block = state.get("blocks", {}).get((layer.get("research_block_refs") or [None])[0], {})
    stages = state.get("stages", {})
    stage_refs = block.get("stage_refs", {})
    if role == "hypothesis_title":
        return {"hypothesis_statement": body}
    if role == "problem_definition":
        return {"previous_finding": line_map.get("Previous finding", ""), "unresolved_conflict": line_map.get("Conflict", ""), "research_question": line_map.get("Research question", "")}
    if role == "fishbone_locator":
        snapshot = layer.get("fishbone_snapshot_ref", {})
        return {"primary_figure": "Historical fishbone SVG bound by Asset Manifest.", "fishbone_focus": f"Historical snapshot｜{snapshot.get('fishbone_id')} rev{snapshot.get('revision')}\nFocus branch｜{line_map.get('Focus branch', '')}"}
    if set(("observation_problem", "literature_mechanism", "mechanism_solution")) <= set(combined_roles):
        return {
            "primary_figure": "Registered observation visual.",
            "research_question": line_map.get("Research question", ""),
            "observation_text": "\n".join(line for line in body.splitlines() if line.startswith(("Observation｜", "Problem｜"))),
            "literature_evidence": "\n".join(line for line in body.splitlines() if line.startswith(("Literature consensus｜", "Alternatives｜", "Gap｜", "Implication｜"))),
            "mechanism_diagram": "\n".join(line for line in body.splitlines() if line.startswith(("Mechanism｜", "Evidence/claim link｜"))),
            "strategy": f"Strategy｜{line_map.get('Strategy', '')}\nSuccess criterion｜{line_map.get('Success criterion', '')}",
        }
    if role == "observation_problem":
        return {"primary_figure": "Registered observation visual.", "research_question": line_map.get("Research question", ""), "observation_text": "\n".join(line for line in body.splitlines() if line.startswith(("Observation｜", "Problem｜")))}
    if role == "literature_mechanism":
        return {"literature_evidence": "\n".join(line for line in body.splitlines() if line.startswith(("Literature consensus｜", "Alternatives｜", "Gap｜", "Implication｜"))), "mechanism_diagram": "\n".join(line for line in body.splitlines() if line.startswith(("Mechanism｜", "Evidence/claim link｜", "Strategy｜", "Success criterion｜")))}
    if role == "mechanism_solution":
        return {"mechanism_diagram": f"Mechanism｜{line_map.get('Mechanism', '')}\nEvidence/claim link｜{line_map.get('Evidence/claim link', '')}", "strategy": f"Strategy｜{line_map.get('Strategy', '')}\nSuccess criterion｜{line_map.get('Success criterion', '')}"}
    if role == "experiment_design":
        experiment_ref = object_ref[0] if isinstance(object_ref, list) else object_ref
        data = stages.get(_stage_id(state, experiment_ref), {}).get("data", {})
        compact = lambda value: "; ".join(str(item) for item in value) if isinstance(value, list) else "; ".join(f"{key}: {item}" for key, item in value.items()) if isinstance(value, dict) else str(value)
        sample = data.get("sample_plan", {})
        return {
            "experiment_matrix": "\n".join([
                f"IV: {compact(data.get('independent_variables', ''))}",
                f"Controlled variables: {compact(data.get('controlled_variables', ''))}",
                f"Controls/baselines: {compact(data.get('controls_baselines', ''))}",
                f"Sample plan: {compact(sample)}",
                f"N/replicates: {compact(sample.get('replicates', ''))}",
                f"Metrics/units: {compact(data.get('measured_outputs', ''))}",
                f"Method: {compact(data.get('instrumentation_method_refs', ''))}",
            ]),
            "decision_rule": f"Prediction: {compact(data.get('predicted_outcomes', ''))}\nDecision rule: {compact(data.get('decision_rules', ''))}",
        }
    if role == "result_single":
        # The plot slot carries the scientific result statement as its
        # annotation; the asset itself is never allowed to replace that text.
        return {"result_plot": body, "result_annotation": body}
    if role == "result_comparison" and set(("experiment_design", "result_single")) <= set(combined_roles):
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        experiment_ref = refs[0] if refs else None
        result_ref = refs[-1] if refs else None
        experiment = stages.get(_stage_id(state, experiment_ref), {}).get("data", {})
        result = stages.get(_stage_id(state, result_ref), {}).get("data", {}).get("summary", "")
        def compact(value):
            if isinstance(value, list):
                return "; ".join(str(item) for item in value)
            if isinstance(value, dict):
                return "; ".join(f"{key}: {item}" for key, item in value.items())
            return str(value)
        return {
            "experiment_matrix": "\n".join([f"IV: {compact(experiment.get('independent_variables', ''))}", f"Controls: {compact(experiment.get('controlled_variables', ''))}", f"Baselines: {compact(experiment.get('controls_baselines', ''))}", f"N/replicates: {compact(experiment.get('sample_plan', ''))}", f"Metrics/units: {compact(experiment.get('measured_outputs', ''))}", f"Method: {compact(experiment.get('instrumentation_method_refs', ''))}", f"Prediction: {compact(experiment.get('predicted_outcomes', ''))}"]),
            "decision_rule": compact(experiment.get("decision_rules", "")),
            "result_plot": result,
            "result_annotation": result,
        }
    if role == "result_comparison":
        result_ref = object_ref[-1] if isinstance(object_ref, list) else object_ref
        result = stages.get(_stage_id(state, result_ref), {}).get("data", {}).get("summary", body)
        experiment_ref = (object_ref[0] if isinstance(object_ref, list) and object_ref else None)
        experiment = stages.get(_stage_id(state, experiment_ref), {}).get("data", {})
        return {"control_panel": f"Control｜{'; '.join(experiment.get('controls_baselines', []))}", "proposed_panel": f"Result｜{result}", "result_plot": result, "result_annotation": result}
    if role == "layer_integrated_discussion":
        return {
            "supporting_results": line_map.get("Supporting", ""),
            "contradicting_results": f"Contradicting｜{line_map.get('Contradicting', 'none')}\nNon-discriminating｜{line_map.get('Non-discriminating', 'none')}",
            "uncertainty": "\n".join(line for line in body.splitlines() if line.startswith(("Cross-experiment pattern｜", "Alternatives｜", "Remaining uncertainty｜", "Mechanism assessment｜"))),
        }
    if role == "layer_summary_decision" and "layer_integrated_discussion" in combined_roles:
        summary = state.get("layer_summaries", {}).get(object_ref, {})
        discussion = state.get("layer_discussions", {}).get(summary.get("discussion_ref") or layer.get("layer_discussion_ref"), {})
        decision = state.get("decisions", {}).get(summary.get("decision_ref"), {})
        return {
            "supporting_results": "; ".join(discussion.get("supporting_results", [])) or "None identified",
            "contradicting_results": "; ".join(discussion.get("contradicting_results", [])) or "None identified",
            "discussion_synthesis": "\n".join([f"Cross-experiment pattern｜{discussion.get('cross_experiment_pattern', '')}", f"Mechanism assessment｜{discussion.get('mechanism_assessment', '')}", f"Alternatives｜{'; '.join(discussion.get('alternative_explanations', []))}"]),
            "uncertainty": f"Discussion uncertainty｜{discussion.get('remaining_uncertainty', '')}\nSummary unresolved｜{summary.get('remaining_unresolved', '')}",
            "decision_status": f"Hypothesis status｜{summary.get('hypothesis_status', '')}\nDecision｜{decision.get('choice', '')}: {decision.get('rationale', '')}",
            "next_step": f"Next question｜{summary.get('next_question', '')}\nNext Step｜{', '.join(summary.get('next_step_refs', []))}",
        }
    if role == "layer_summary_decision":
        return {"decision_status": "\n".join(line for line in body.splitlines() if line.startswith(("Hypothesis status｜", "Decision｜", "Answered｜"))), "uncertainty": line_map.get("Unresolved", ""), "next_step": "\n".join(line for line in body.splitlines() if line.startswith(("Next question｜", "Next Step｜")))}
    if role == "hypothesis_transition":
        return {"transition_nodes": "\n".join(line for line in body.splitlines() if line.startswith(("Previous hypothesis｜", "Key results｜", "New observation｜", "New hypothesis｜"))), "derivation_strip": "\n".join(line for line in body.splitlines() if line.startswith(("Not explained｜", "Therefore｜")))}
    if role == "progress_todo":
        commitments = (meeting_projection or {}).get("previous_commitments", [])
        dependencies = "\n".join(line for line in body.splitlines() if line.startswith("Dependencies｜"))
        workstreams = "; ".join(str(item.get("workstream", "")) for item in commitments)
        return {"commitment_table": "\n".join(line for line in body.splitlines() if line.startswith("Commitment｜")), "current_position": line_map.get("Current position", ""), "parallel_work": f"{dependencies}\nWorkstreams｜{workstreams}"}
    if role == "schedule_next_step":
        return {"timeline": body, "dependencies": ""}
    return {"content": body}
