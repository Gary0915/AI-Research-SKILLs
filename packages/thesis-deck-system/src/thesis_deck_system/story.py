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


def content_slots_from_materialized_state(state: dict, layer_id: str, role: str, object_ref=None, *, meeting_projection: dict | None = None) -> dict[str, str]:
    """Compile slot-bound scientific content from one materialized cursor.

    `content.body` remains a human-readable compatibility concatenation; it
    is never the authoritative source used for placement.  Each governed slot
    receives a separately persisted string generated from the same state.
    """
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
        return {"primary_figure": "Historical fishbone SVG bound by Asset Manifest.", "fishbone_focus": line_map.get("Focus branch", "")}
    if role == "observation_problem":
        return {"primary_figure": "Registered observation visual.", "research_question": line_map.get("Research question", ""), "observation_text": "\n".join(line for line in body.splitlines() if line.startswith(("Observation｜", "Problem｜")))}
    if role == "literature_mechanism":
        return {"literature_evidence": "\n".join(line for line in body.splitlines() if line.startswith(("Literature consensus｜", "Alternatives｜", "Gap｜", "Implication｜"))), "mechanism_diagram": "\n".join(line for line in body.splitlines() if line.startswith(("Mechanism｜", "Strategy｜")))}
    if role == "mechanism_solution":
        return {"mechanism_diagram": line_map.get("Mechanism", body), "strategy": line_map.get("Strategy", "")}
    if role == "experiment_design":
        return {"experiment_matrix": "\n".join(line for line in body.splitlines() if any(key in line for key in ("IV:", "Controls:", "N/replicates:", "Metrics/units:", "Method:"))), "decision_rule": "\n".join(line for line in body.splitlines() if "Decision rule:" in line or "Prediction:" in line)}
    if role == "result_single":
        return {"result_plot": "Registered quantitative SVG.", "result_annotation": body}
    if role == "result_comparison":
        result_ref = object_ref[-1] if isinstance(object_ref, list) else object_ref
        result = stages.get(_stage_id(state, result_ref), {}).get("data", {}).get("summary", body)
        experiment_ref = (object_ref[0] if isinstance(object_ref, list) and object_ref else None)
        experiment = stages.get(_stage_id(state, experiment_ref), {}).get("data", {})
        return {"control_panel": f"Control｜{'; '.join(experiment.get('controls_baselines', []))}", "proposed_panel": f"Result｜{result}"}
    if role == "layer_integrated_discussion":
        return {"supporting_results": line_map.get("Supporting", ""), "contradicting_results": line_map.get("Contradicting", ""), "uncertainty": "\n".join(line for line in body.splitlines() if line.startswith(("Alternatives｜", "Remaining uncertainty｜", "Mechanism assessment｜")))}
    if role == "layer_summary_decision":
        return {"decision_status": "\n".join(line for line in body.splitlines() if line.startswith(("Hypothesis status｜", "Decision｜", "Answered｜"))), "uncertainty": line_map.get("Unresolved", ""), "next_step": "\n".join(line for line in body.splitlines() if line.startswith(("Next question｜", "Next Step｜")))}
    if role == "hypothesis_transition":
        return {"transition_nodes": "\n".join(line for line in body.splitlines() if line.startswith(("Previous hypothesis｜", "Key results｜", "New observation｜", "New hypothesis｜"))), "derivation_strip": "\n".join(line for line in body.splitlines() if line.startswith(("Not explained｜", "Therefore｜")))}
    if role == "progress_todo":
        commitments = (meeting_projection or {}).get("previous_commitments", [])
        return {"commitment_table": "\n".join(line for line in body.splitlines() if line.startswith("Commitment｜")), "current_position": line_map.get("Current position", ""), "parallel_work": "\n".join(line for line in body.splitlines() if line.startswith("Dependencies｜")) or ", ".join(str(item.get("workstream", "")) for item in commitments)}
    if role == "schedule_next_step":
        return {"timeline": body, "dependencies": ""}
    return {"content": body}
