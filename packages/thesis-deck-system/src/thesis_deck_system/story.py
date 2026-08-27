"""Hypothesis-layer story compilation and hard professor-rule validation."""

from __future__ import annotations

from .contracts import Finding


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
    sequence.extend((("result_comparison" if len(result_refs) > 1 else "result_single"), ref) for ref in result_refs)
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
        return (f"Observation｜{obs.get('observation', '')}\nProblem｜{obs.get('problem', '')}\nResearch question｜{block.get('research_question', {}).get('text', '')}\n"
                f"Literature consensus｜{lit.get('consensus', '')}\nAlternatives｜{'; '.join(lit.get('disagreements_or_alternatives', []))}\nGap｜{lit.get('research_gap', '')}\nImplication｜{lit.get('implication_for_hypothesis_or_strategy', '')}\n"
                f"Mechanism｜{mech.get('mechanism', '')}\nStrategy｜{sol.get('strategy', '')}")
    if role == "experiment_design":
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        chunks = []
        for ref in refs:
            stage = state["stages"].get(_stage_id(state, ref), {})
            data = stage.get("data", {})
            chunks.append(f"{ref}｜IV: {data.get('independent_variables', '')}\nControls: {data.get('controls_baselines', '')}\nN/replicates: {data.get('sample_plan', '')}\nMetrics/units: {data.get('measured_outputs', '')}\nMethod: {data.get('instrumentation_method_refs', '')}\nPrediction: {data.get('predicted_outcomes', '')}\nDecision rule: {data.get('decision_rules', '')}")
        return "\n\n".join(chunks)
    if role in {"result_single", "result_comparison"}:
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        return "\n".join(f"{ref}｜{state['stages'].get(_stage_id(state, ref), {}).get('data', {}).get('summary', '')}" for ref in refs)
    if role == "layer_integrated_discussion":
        discussion = state["layer_discussions"].get(object_ref, {})
        return f"Supporting｜{', '.join(discussion.get('supporting_results', []))}\nContradicting｜{', '.join(discussion.get('contradicting_results', [])) or 'none'}\nCross-experiment pattern｜{discussion.get('cross_experiment_pattern', '')}\nMechanism assessment｜{discussion.get('mechanism_assessment', '')}\nAlternatives｜{'; '.join(discussion.get('alternative_explanations', []))}\nRemaining uncertainty｜{discussion.get('remaining_uncertainty', '')}"
    if role == "layer_summary_decision":
        summary = state["layer_summaries"].get(object_ref, {})
        decision = state["decisions"].get(summary.get("decision_ref"), {})
        return f"Answered｜{summary.get('answered', '')}\nHypothesis status｜{summary.get('hypothesis_status', '')}\nDecision｜{decision.get('choice', '')}: {decision.get('rationale', '')}\nUnresolved｜{summary.get('remaining_unresolved', '')}\nNext question｜{summary.get('next_question', '')}\nNext Step｜{', '.join(summary.get('next_step_refs', []))}"
    transition = state["hypothesis_transitions"].get(object_ref, {})
    return f"Previous hypothesis｜{transition.get('previous_hypothesis_claim_ref')}\nKey results｜{', '.join(transition.get('key_result_refs', []))}\nNot explained｜{transition.get('unexplained', '')}\nNew observation｜{', '.join(transition.get('observation_or_uncertainty_refs', []))}\nTherefore｜{transition.get('rationale', '')}\nNew hypothesis｜{transition.get('new_hypothesis_claim_ref')}"
