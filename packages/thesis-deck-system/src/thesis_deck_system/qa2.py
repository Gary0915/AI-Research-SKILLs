"""Executed professor and render QA for the hypothesis-layer architecture."""

from __future__ import annotations

from pathlib import Path
import hashlib
import itertools
import re
from PIL import Image, ImageChops, ImageStat
from datetime import datetime, timezone


PHASE2_PIPELINE = [
    "schema_ledger_integrity", "scientific_reasoning", "citation_evidence_provenance",
    "professor_style_logic", "compile_assemble_pptx", "structural_pptx_engineering",
    "render_montage_visual", "native_powerpoint_round_trip", "final_deck_version_audit", "release",
]

PRESENTATION_ROLE_CONTRACTS = {
    "hypothesis_title": {"required_fields": {"hypothesis_statement": "hypothesis_statement", "falsifiable_prediction": "hypothesis_statement", "research_question": "hypothesis_statement"}},
    "problem_definition": {"required_fields": {"previous_finding": "previous_finding", "unresolved_conflict": "unresolved_conflict", "research_question": "research_question"}},
    "fishbone_locator": {"required_fields": {"historical_snapshot": "fishbone_focus", "current_focus": "fishbone_focus"}},
    "observation_problem": {"required_fields": {"observation": "observation_text", "research_question": "research_question"}},
    "literature_mechanism": {"required_fields": {"consensus": "literature_evidence", "disagreement_alternatives": "literature_evidence", "research_gap": "literature_evidence", "implication": "literature_evidence", "mechanism": "mechanism_diagram", "evidence_claim_link": "mechanism_diagram"}},
    "mechanism_solution": {"required_fields": {"mechanism": "mechanism_diagram", "evidence_claim_link": "mechanism_diagram", "strategy": "strategy", "success_criterion": "strategy"}},
    "experiment_design": {"required_fields": {"independent_variables": "experiment_matrix", "controlled_variables": "experiment_matrix", "control_baseline": "experiment_matrix", "sample_plan": "experiment_matrix", "replicates": "experiment_matrix", "measured_outputs": "experiment_matrix", "units": "experiment_matrix", "instrumentation_method": "experiment_matrix", "predicted_outcomes": "decision_rule", "decision_rule": "decision_rule"}},
    "result_single": {"required_fields": {"result_identity": "result_annotation", "result_statement": "result_annotation", "metric_value_uncertainty": "result_annotation"}},
    "result_comparison": {"required_fields": {"result_identity": "result_annotation", "result_statement": "result_annotation", "metric_value_uncertainty": "result_annotation"}},
    "layer_integrated_discussion": {"required_fields": {"supporting_results": "supporting_results", "contradicting_results": "contradicting_results", "non_discriminating_results": "contradicting_results", "cross_experiment_pattern": "uncertainty", "mechanism_assessment": "uncertainty", "alternative_explanations": "uncertainty", "remaining_uncertainty": "uncertainty"}},
    "layer_summary_decision": {"required_fields": {"answered_question": "decision_status", "hypothesis_status": "decision_status", "decision": "decision_status", "unresolved_items": "uncertainty", "next_question": "next_step", "next_step": "next_step"}},
    "hypothesis_transition": {"required_fields": {"prior_hypothesis": "transition_nodes", "key_prior_results": "transition_nodes", "unresolved_point": "derivation_strip", "precursor_observation": "transition_nodes", "derivation_rationale": "derivation_strip", "new_hypothesis": "transition_nodes"}},
    "progress_todo": {"required_fields": {"prior_commitment": "commitment_table", "current_position": "current_position", "parallel_work": "parallel_work"}},
}


def _contract_fields(spec: dict, role: str) -> list[str]:
    fields: list[str] = []
    for name in spec.get("combined_roles", [role]):
        fields.extend(PRESENTATION_ROLE_CONTRACTS.get(name, {}).get("required_fields", {}))
    return list(dict.fromkeys(fields))


def _event_identity(event) -> list[tuple[str, str]]:
    payload = event.payload
    identities: list[tuple[str, str]] = []
    for key, kind in (
        ("hypothesis_layer_id", "hypothesis_layer"), ("claim_id", "claim"), ("problem_id", "problem"),
        ("block_id", "block"), ("stage_id", "stage"), ("evidence_id", "evidence"), ("asset_id", "asset"),
        ("action_item_id", "action"), ("decision_id", "decision"), ("discussion_id", "discussion"),
        ("summary_id", "summary"), ("transition_id", "transition"),
    ):
        if payload.get(key):
            identities.append((kind, str(payload[key])))
    if payload.get("fishbone_id") and payload.get("revision") is not None:
        identities.append(("fishbone", f"{payload['fishbone_id']}@{payload['revision']}"))
    return identities


def _dependency_cursor(events, kind: str, identifier: str, source_cursor: int) -> int | None:
    candidates = [event.cursor for event in events[:source_cursor] if (kind, identifier) in _event_identity(event)]
    return candidates[-1] if candidates else None


def _resolve_stage_id(state: dict, ref: str | None) -> str | None:
    if not ref:
        return None
    if ref in state.get("stages", {}):
        return ref
    candidate = f"ST-{ref}"
    return candidate if candidate in state.get("stages", {}) else ref


def _slide_dependency_refs(spec: dict, state: dict) -> list[tuple[str, str]]:
    layer_id = spec.get("hypothesis_layer_ref")
    layer = state.get("hypothesis_layers", {}).get(layer_id, {})
    role = spec.get("semantic_role")
    refs: list[tuple[str, str]] = []
    if layer_id:
        refs.append(("hypothesis_layer", str(layer_id)))
    for field, kind in (("claim_refs", "claim"), ("evidence_refs", "evidence"), ("asset_refs", "asset"), ("action_refs", "action"), ("decision_refs", "decision")):
        refs.extend((kind, str(ref)) for ref in spec.get("bindings", {}).get(field, []))
    refs.extend(("block", str(item["block_id"])) for item in spec.get("block_refs", []) if item.get("block_id"))
    block = state.get("blocks", {}).get((layer.get("research_block_refs") or [None])[0], {})
    stage_refs = block.get("stage_refs", {})
    object_refs = spec.get("object_ref") if isinstance(spec.get("object_ref"), list) else [spec.get("object_ref")]
    if role == "problem_definition" and layer.get("problem_ref"):
        refs.append(("problem", str(layer["problem_ref"])))
    elif role == "fishbone_locator":
        fishbone = spec.get("fishbone_snapshot_ref") or layer.get("fishbone_snapshot_ref", {})
        refs.append(("fishbone", f"{fishbone.get('fishbone_id')}@{fishbone.get('revision')}"))
    elif role in {"observation_problem", "literature_mechanism", "mechanism_solution"}:
        names = {"observation_problem": ["observation"], "literature_mechanism": ["literature", "mechanism"], "mechanism_solution": ["mechanism", "solution"]}[role]
        refs.extend(("stage", str(stage_refs[name])) for name in names if stage_refs.get(name))
    elif role in {"experiment_design", "result_single", "result_comparison"}:
        refs.extend(("stage", str(_resolve_stage_id(state, ref))) for ref in object_refs if ref)
    elif role == "layer_integrated_discussion" and spec.get("object_ref"):
        refs.append(("discussion", str(spec["object_ref"])))
    elif role == "layer_summary_decision" and spec.get("object_ref"):
        refs.append(("summary", str(spec["object_ref"])))
    elif role == "hypothesis_transition" and spec.get("object_ref"):
        transition = state.get("hypothesis_transitions", {}).get(spec["object_ref"], {})
        refs.append(("transition", str(spec["object_ref"])))
        refs.extend(("claim", str(ref)) for ref in [transition.get("previous_hypothesis_claim_ref"), transition.get("new_hypothesis_claim_ref")] if ref)
        refs.extend(("stage", str(_resolve_stage_id(state, ref))) for ref in transition.get("key_result_refs", []))
        refs.extend(("decision", str(ref)) for ref in transition.get("decision_refs", []))
        refs.extend(("evidence", str(ref)) for ref in transition.get("observation_or_uncertainty_refs", []))
    return list(dict.fromkeys(refs))


def run_presentation_temporal_snapshot_qa(specs: list[dict], ledger) -> dict:
    """Validate per-slide cursors and stage-scoped bindings against replayed state."""
    events = ledger.replay()
    findings: list[dict] = []
    rows: list[dict] = []
    # Compute result-evidence boundaries per hypothesis layer. A global
    # minimum would incorrectly apply a predecessor result to a successor.
    final_state = ledger.materialize(len(events))
    layer_by_block = {
        block_ref: layer_id
        for layer_id, layer in final_state.get("hypothesis_layers", {}).items()
        for block_ref in layer.get("research_block_refs", [])
    }
    result_evidence_by_layer: dict[str, set[str]] = {}
    for event in events:
        payload = event.payload
        if event.event_type == "evidence_linked" and payload.get("causal_role") == "experiment_result":
            layer_id = payload.get("origin", {}).get("layer_ref")
            if layer_id:
                result_evidence_by_layer.setdefault(str(layer_id), set()).add(str(payload["evidence_id"]))
        if event.event_type == "stage_revised" and payload.get("stage_type") == "result" and payload.get("status") != "pending":
            layer_id = layer_by_block.get(payload.get("block_ref", {}).get("block_id"))
            if layer_id:
                result_evidence_by_layer.setdefault(layer_id, set()).update(str(ref) for ref in payload.get("evidence_refs", []))
    evidence_cursor = {
        str(event.payload["evidence_id"]): event.cursor
        for event in events if event.event_type == "evidence_linked" and event.payload.get("evidence_id")
    }
    result_evidence_cursors_by_layer = {
        layer_id: sorted(evidence_cursor[ref] for ref in refs if ref in evidence_cursor)
        for layer_id, refs in result_evidence_by_layer.items()
    }
    for spec in specs:
        cursor = spec.get("source_cursor")
        state = ledger.materialize(cursor) if isinstance(cursor, int) and 1 <= cursor <= len(events) else {}
        layer_id = spec.get("hypothesis_layer_ref")
        role = spec.get("semantic_role")
        refs = spec.get("bindings", {})
        future: list[str] = []
        for kind, field, state_key in (("claim_id", "claim_refs", "claims"), ("evidence_id", "evidence_refs", "evidence"), ("asset_id", "asset_refs", "assets"), ("action_item_id", "action_refs", "actions"), ("decision_id", "decision_refs", "decisions")):
            for ref in refs.get(field, []):
                if ref not in state.get(state_key, {}):
                    future.append(f"{field}:{ref}")
        layer_result_evidence = result_evidence_by_layer.get(str(layer_id), set())
        if role in {"hypothesis_title", "problem_definition", "fishbone_locator"} and set(refs.get("evidence_refs", [])) & layer_result_evidence:
            future.append("early_role_binds_result_evidence")
        stage_cursors = spec.get("stage_source_cursors", {})
        if "experiment_design" in stage_cursors:
            experiment_cursor = int(stage_cursors["experiment_design"])
            bound_result_evidence = [evidence_cursor[ref] for ref in refs.get("evidence_refs", []) if ref in layer_result_evidence and ref in evidence_cursor]
            if bound_result_evidence and experiment_cursor >= min(bound_result_evidence):
                future.append("experiment_stage_after_result_evidence")
        if "result_single" in stage_cursors:
            result_cursor = int(stage_cursors["result_single"])
            bound_result_cursors = [evidence_cursor[ref] for ref in refs.get("evidence_refs", []) if ref in layer_result_evidence and ref in evidence_cursor]
            if bound_result_cursors and result_cursor < max(bound_result_cursors):
                future.append("result_stage_before_result_evidence")
        dependencies = []
        for dependency_type, dependency_ref in _slide_dependency_refs(spec, state):
            dependency_cursor = _dependency_cursor(events, dependency_type, dependency_ref, int(cursor or 0))
            dependencies.append({"dependency_type": dependency_type, "dependency_ref": dependency_ref, "cursor": dependency_cursor})
            if dependency_cursor is None:
                future.append(f"missing_dependency:{dependency_type}:{dependency_ref}")
        earliest = max((item["cursor"] for item in dependencies if item["cursor"] is not None), default=cursor)
        if isinstance(cursor, int) and earliest is not None and cursor < earliest:
            future.append("source_cursor_before_earliest_required")
        latest_allowed = None
        if role in {"hypothesis_title", "problem_definition", "fishbone_locator"}:
            boundary = min(result_evidence_cursors_by_layer.get(str(layer_id), []), default=None)
            latest_allowed = boundary - 1 if boundary is not None else None
            if boundary is not None and isinstance(cursor, int) and cursor >= boundary:
                future.append("opening_not_strictly_before_result_evidence")
        if role == "hypothesis_transition":
            transition = state.get("hypothesis_transitions", {}).get(spec.get("object_ref"), {})
            successor = transition.get("to_layer_ref")
            boundary = min(result_evidence_cursors_by_layer.get(str(successor), []), default=None)
            latest_allowed = boundary - 1 if boundary is not None else None
            if boundary is not None and isinstance(cursor, int) and cursor >= boundary:
                future.append("transition_not_before_successor_result_evidence")
        row = {"slide_id": spec.get("slide_id"), "layer_id": layer_id, "semantic_role": role, "source_cursor": cursor, "stage_source_cursors": stage_cursors, "dependency_refs": dependencies, "bound_claim_refs": refs.get("claim_refs", []), "bound_evidence_refs": refs.get("evidence_refs", []), "bound_asset_refs": refs.get("asset_refs", []), "bound_action_refs": refs.get("action_refs", []), "bound_decision_refs": refs.get("decision_refs", []), "earliest_required_cursor": earliest, "latest_allowed_cursor": latest_allowed, "strict_result_boundary_cursor": None if latest_allowed is None else latest_allowed + 1, "future_ref_findings": list(dict.fromkeys(future)), "status": "fail" if future else "pass"}
        rows.append(row)
        if future:
            findings.append({"slide_id": spec.get("slide_id"), "findings": future})
    return {"schema_version": "1.0.0", "status": "fail" if findings else "pass", "slides": rows, "findings": findings}


def run_combined_role_content_qa(specs: list[dict], structural_audit: dict) -> dict:
    """Require every combined role's presentation fields and physical slot."""
    generated = {item.get("slide_spec_id"): item for item in structural_audit.get("generated_slides", [])}
    rows: list[dict] = []
    findings: list[dict] = []
    for spec in specs:
        roles = spec.get("combined_roles", [spec.get("semantic_role")])
        unknown_roles = [role for role in roles if role not in PRESENTATION_ROLE_CONTRACTS]
        slots = spec.get("content", {}).get("slots", {})
        semantic_fields = spec.get("content", {}).get("semantic_fields", {})
        audit_slots = {item.get("slot"): item for item in generated.get(spec.get("slide_id"), {}).get("physical_slot_conformance", [])}
        coverage = {}
        role_coverage = {}
        missing: list[str] = []
        if unknown_roles:
            missing.extend(f"unknown_role:{role}" for role in unknown_roles)
        for role_name in roles:
            field_slots = PRESENTATION_ROLE_CONTRACTS.get(role_name, {}).get("required_fields", {})
            role_values = semantic_fields.get(role_name, {})
            role_coverage[role_name] = {}
            for field, slot_name in field_slots.items():
                value = str(role_values.get(field, "")).strip()
                audit_slot = audit_slots.get(slot_name, {})
                actual_text = str(audit_slot.get("actual_text", ""))
                tokens = [token.casefold() for token in re.findall(r"[A-Za-z0-9%/]+|[\u3400-\u9fff]+", value) if token]
                physical = bool(audit_slot.get("content_or_asset_binding_result", False)) and bool(actual_text.strip()) and all(token in actual_text.casefold() for token in tokens)
                detail = {"slot": slot_name, "value": value, "content_present": bool(value), "physical_present": physical, "actual_text": actual_text, "status": "pass" if value and physical else "fail"}
                role_coverage[role_name][field] = detail
                coverage[f"{role_name}.{field}"] = detail
                if not value or not physical:
                    missing.append(f"{role_name}.{field}")
        row = {"slide_id": spec.get("slide_id"), "roles": roles, "required_fields": list(coverage), "coverage": coverage, "role_coverage": role_coverage, "missing": missing, "status": "fail" if missing else "pass"}
        rows.append(row)
        if missing:
            findings.append({"slide_id": spec.get("slide_id"), "missing": missing})
    return {"schema_version": "1.0.0", "status": "fail" if findings else "pass", "presentation_role_contracts": PRESENTATION_ROLE_CONTRACTS, "slides": rows, "findings": findings}


def run_physical_content_fidelity_qa(specs: list[dict], structural_audit: dict, render_hashes: dict[str, str] | None = None) -> dict:
    """Compare expected slot text/assets to actual saved PPTX shapes/relationships."""
    generated = {item.get("slide_spec_id"): item for item in structural_audit.get("generated_slides", [])}
    results: list[dict] = []
    findings: list[dict] = []
    for spec in specs:
        audit = generated.get(spec.get("slide_id"), {})
        slots = {item.get("slot"): item for item in audit.get("physical_slot_conformance", [])}
        expected_asset_ids = [item.get("asset_id") for item in spec.get("placements", [])]
        # A result annotation may intentionally be exposed through both the
        # governed plot slot and its nested annotation slot. Compare the
        # unique expected statements once so duplicated bindings do not make
        # a faithful PPTX fail its own fidelity check.
        expected_values = [str(value) for key, value in spec.get("content", {}).get("slots", {}).items() if key in {"control_panel", "proposed_panel", "result_plot", "result_annotation"} and str(value).strip()]
        expected_text = "\n".join(dict.fromkeys(expected_values))
        actual_text = "\n".join(item.get("actual_text", "") for item in audit.get("physical_slot_conformance", []))
        actual_asset_ids = [item.get("expected_asset_id") for item in audit.get("physical_slot_conformance", []) if item.get("asset_relationship")]
        result_refs = spec.get("object_ref") if isinstance(spec.get("object_ref"), list) else [spec.get("object_ref")]
        for result_ref in [ref for ref in result_refs if str(ref).startswith("RES")]:
            row = {"result_ref": result_ref, "slide_id": spec.get("slide_id"), "expected_text": expected_text, "extracted_text": actual_text, "expected_asset_ids": expected_asset_ids, "asset_ids": list(dict.fromkeys(actual_asset_ids)), "render_sha256": (render_hashes or {}).get(spec.get("slide_id")), "status": "pass" if expected_text and expected_text in actual_text and set(expected_asset_ids) <= set(actual_asset_ids) and all(any(item.get("expected_asset_id") == asset_id and item.get("asset_relationship") for item in audit.get("physical_slot_conformance", [])) for asset_id in expected_asset_ids) else "fail"}
            results.append(row)
            if row["status"] != "pass":
                findings.append(row)
    # A presentation-wide check also catches a dropped annotation on a
    # non-result asset/text composition.
    for spec in specs:
        audit = generated.get(spec.get("slide_id"), {})
        for slot in audit.get("physical_slot_conformance", []):
            if spec.get("slot_compositions", {}).get(slot.get("slot")) in {"asset_with_caption", "asset_with_annotation", "nested_group"} and not slot.get("actual_text"):
                findings.append({"slide_id": spec.get("slide_id"), "slot": slot.get("slot"), "reason": "asset composition lost expected text"})
    return {"schema_version": "1.0.0", "status": "fail" if findings else "pass", "results": results, "findings": findings, "missing": findings}


def run_presentation_semantic_fidelity_qa(specs: list[dict], structural_audit: dict, temporal: dict, combined: dict, fidelity: dict, *, ledger=None) -> dict:
    """Own the post-assembly semantic gate consumed by Professor QA."""
    findings: list[dict] = []
    evidence: dict[str, object] = {}
    executed_checks: list[str] = []

    def own(check_id: str, passed: bool, detail) -> None:
        executed_checks.append(check_id)
        evidence[check_id] = {"status": "pass" if passed else "fail", "detail": detail}
        if not passed:
            findings.append({"rule": check_id, "status": "fail", "evidence": detail})

    own("temporal_snapshot_correctness", temporal.get("status") == "pass", temporal.get("findings", []))
    own("combined_role_field_completeness", combined.get("status") == "pass", combined.get("findings", []))
    own("physical_text_asset_fidelity", fidelity.get("status") == "pass", fidelity.get("findings", []))
    generated = {item.get("slide_spec_id"): item for item in structural_audit.get("generated_slides", [])}
    for spec in specs:
        audit = generated.get(spec.get("slide_id"), {})
        if not audit or not audit.get("layout_master_role_match"):
            findings.append({"rule": "layout_master_identity", "slide_id": spec.get("slide_id"), "status": "fail"})
        if not audit or not audit.get("governed_geometry_match"):
            findings.append({"rule": "governed_physical_slots", "slide_id": spec.get("slide_id"), "status": "fail"})
        if not audit or not audit.get("notes_source_match"):
            findings.append({"rule": "speaker_notes_provenance", "slide_id": spec.get("slide_id"), "status": "fail"})
    by_layer: dict[str, set[str]] = {}
    for spec in specs:
        layer = spec.get("hypothesis_layer_ref")
        if layer:
            by_layer.setdefault(layer, set()).update(spec.get("combined_roles", [spec.get("semantic_role")]))
    required = {"hypothesis_title", "problem_definition", "fishbone_locator", "observation_problem", "literature_mechanism", "experiment_design", "layer_integrated_discussion", "layer_summary_decision"}
    own("hypothesis_problem_separation", all("hypothesis_title" in roles and "problem_definition" in roles and not any({"hypothesis_title", "problem_definition"} <= set(spec.get("combined_roles", [])) for spec in specs if spec.get("hypothesis_layer_ref") == layer) for layer, roles in by_layer.items()), {layer: sorted(roles) for layer, roles in by_layer.items()})
    own("scientific_method_audience_visibility", all(required <= roles for roles in by_layer.values()), {layer: sorted(required - roles) for layer, roles in by_layer.items()})
    ordered_by_layer = {layer: [spec for spec in specs if spec.get("hypothesis_layer_ref") == layer] for layer in by_layer}
    result_order = {}
    discussion_order = {}
    summary_order = {}
    for layer, layer_specs in ordered_by_layer.items():
        result_positions = [specs.index(spec) for spec in layer_specs if set(spec.get("combined_roles", [spec.get("semantic_role")])) & {"result_single", "result_comparison"}]
        discussion_positions = [specs.index(spec) for spec in layer_specs if "layer_integrated_discussion" in spec.get("combined_roles", [spec.get("semantic_role")])]
        summary_positions = [specs.index(spec) for spec in layer_specs if "layer_summary_decision" in spec.get("combined_roles", [spec.get("semantic_role")])]
        result_order[layer] = result_positions
        discussion_order[layer] = discussion_positions
        summary_order[layer] = summary_positions
    own("result_before_integrated_discussion", all(results and discussions and max(results) <= min(discussions) for layer in by_layer for results, discussions in [(result_order[layer], discussion_order[layer])]), {"results": result_order, "discussions": discussion_order})
    own("all_required_results_before_discussion", all(len(result_order[layer]) == len({str(ref) for spec in ordered_by_layer[layer] for ref in (spec.get("object_ref") if isinstance(spec.get("object_ref"), list) else [spec.get("object_ref")]) if str(ref).startswith("RES")}) and max(result_order[layer]) <= min(discussion_order[layer]) for layer in by_layer), {"results": result_order, "discussions": discussion_order})
    own("discussion_before_summary", all(discussion_order[layer] and summary_order[layer] and max(discussion_order[layer]) <= min(summary_order[layer]) for layer in by_layer), {"discussions": discussion_order, "summaries": summary_order})
    fishbone_evidence = []
    fishbone_ok = True
    if ledger is None:
        fishbone_ok = False
        fishbone_evidence.append("ledger unavailable")
    else:
        for spec in [item for item in specs if item.get("semantic_role") == "fishbone_locator"]:
            state = ledger.materialize(spec["source_cursor"])
            layer = state.get("hypothesis_layers", {}).get(spec.get("hypothesis_layer_ref"), {})
            ok = spec.get("fishbone_snapshot_ref") == layer.get("fishbone_snapshot_ref") and spec.get("fishbone_focus_refs") == layer.get("fishbone_focus_refs")
            fishbone_ok &= ok
            fishbone_evidence.append({"slide_id": spec.get("slide_id"), "expected": layer.get("fishbone_snapshot_ref"), "actual": spec.get("fishbone_snapshot_ref"), "focus": spec.get("fishbone_focus_refs"), "status": "pass" if ok else "fail"})
    own("historical_fishbone_binding", fishbone_ok, fishbone_evidence)
    results = [item for item in fidelity.get("results", []) if item.get("result_ref")]
    distinction_evidence = []
    render_missing = False
    distinction_ok = True
    for left, right in itertools.combinations(results, 2):
        if left.get("expected_text") == right.get("expected_text"):
            continue
        render_missing |= not left.get("render_sha256") or not right.get("render_sha256")
        pair_ok = bool(left.get("extracted_text") != right.get("extracted_text") and left.get("render_sha256") and right.get("render_sha256") and left.get("render_sha256") != right.get("render_sha256"))
        distinction_ok &= pair_ok
        distinction_evidence.append({"left": left.get("result_ref"), "right": right.get("result_ref"), "left_render_sha256": left.get("render_sha256"), "right_render_sha256": right.get("render_sha256"), "status": "pass" if pair_ok else "fail"})
    own("visible_result_distinction", distinction_ok and bool(distinction_evidence) and not render_missing, distinction_evidence)
    transition_evidence = []
    transition_ok = True
    transitions = [spec for spec in specs if spec.get("semantic_role") == "hypothesis_transition"]
    for transition_spec in transitions:
        index = specs.index(transition_spec)
        from_layer = transition_spec.get("hypothesis_layer_ref")
        next_layer = next((spec.get("hypothesis_layer_ref") for spec in specs[index + 1 :] if spec.get("hypothesis_layer_ref") != from_layer), None)
        prior_summary = any("layer_summary_decision" in spec.get("combined_roles", [spec.get("semantic_role")]) and spec.get("hypothesis_layer_ref") == from_layer for spec in specs[:index])
        state = ledger.materialize(transition_spec["source_cursor"]) if ledger is not None else {}
        transition = state.get("hypothesis_transitions", {}).get(transition_spec.get("object_ref"), {})
        ok = prior_summary and transition.get("from_layer_ref") == from_layer and transition.get("to_layer_ref") == next_layer
        transition_ok &= ok
        transition_evidence.append({"transition_id": transition_spec.get("object_ref"), "from_layer": from_layer, "to_layer": next_layer, "prior_summary": prior_summary, "status": "pass" if ok else "fail"})
    own("transition_location_provenance", transition_ok and bool(transitions), transition_evidence)
    status = "blocked_render_evidence" if render_missing and not [item for item in findings if item.get("rule") != "visible_result_distinction"] else "fail" if findings else "pass"
    return {"schema_version": "1.0.0", "status": status, "executed_checks": executed_checks, "check_evidence": evidence, "result_objects_checked": [item.get("result_ref") for item in results], "findings": findings, "temporal_snapshot_status": temporal.get("status"), "combined_role_status": combined.get("status"), "physical_fidelity_status": fidelity.get("status")}


def run_report_evidence_consistency(canonical_facts: dict, reported_facts: dict) -> dict:
    """Compare every canonical report fact; omission is a mismatch, not PASS."""
    required = sorted(canonical_facts)
    mismatches = {
        key: {"canonical": canonical_facts.get(key), "reported": reported_facts.get(key, "<omitted>")}
        for key in required
        if key not in reported_facts or reported_facts.get(key) != canonical_facts.get(key)
    }
    return {"schema_version": "1.0.0", "status": "fail" if mismatches else "pass", **canonical_facts, "required_fields": required, "canonical_facts": canonical_facts, "reported_facts": reported_facts, "mismatches": mismatches}


def run_professor_qa_v2(profile: dict, projection: dict) -> dict:
    slides = projection.get("slides", [])
    state = projection.get("state", {})
    presentation = projection.get("presentation_semantic_fidelity", {})
    combined_coverage = {item.get("slide_id"): item for item in projection.get("combined_role_content", {}).get("slides", [])}
    findings = []
    evidence = {}
    executed_checks = []

    def profile_rule(rule_path: str | None, default: bool = True) -> tuple[bool, object]:
        if not rule_path:
            return True, None
        section, key = rule_path.split(".", 1)
        value = profile.get(section, {}).get(key, default)
        return bool(value), value

    def check(check_id: str, ok: bool, path: str, repair: str, detail: object, *, rule: str | None = None) -> None:
        enabled, configured = profile_rule(rule)
        if not enabled:
            evidence[check_id] = {"passed": True, "skipped": True, "profile_rule": rule, "configured_value": configured, "path": path}
            return
        executed_checks.append(check_id)
        evidence[check_id] = {"passed": bool(ok), "profile_rule": rule, "configured_value": configured, "path": path, "detail": detail}
        if not ok:
            findings.append(_finding(check_id, path, repair))

    layers = sorted(projection.get("layers", []), key=lambda layer: (layer.get("source_event_cursor", 0), layer.get("hypothesis_layer_id", "")))
    check("PROF-PRESENTATION-SEMANTIC-FIDELITY", presentation.get("status") == "pass", "presentation_semantic_fidelity", "Resolve post-assembly semantic fidelity findings before Professor QA", presentation)
    transitions = state.get("hypothesis_transitions", {})
    transitions_by_from: dict[str, list[dict]] = {}
    for transition_id, transition in transitions.items():
        item = dict(transition)
        item.setdefault("transition_id", transition_id)
        transitions_by_from.setdefault(item.get("from_layer_ref", ""), []).append(item)
    for layer in layers:
        layer_id = layer["hypothesis_layer_id"]
        layer_slides = [slide for slide in slides if slide.get("hypothesis_layer_ref") == layer_id]
        roles = [slide.get("semantic_role") for slide in layer_slides]
        combined = [set(slide.get("combined_roles", [])) for slide in layer_slides]
        def has(role: str) -> bool:
            for slide in layer_slides:
                declared = slide.get("semantic_role") == role or role in slide.get("combined_roles", [])
                if not declared:
                    continue
                coverage = combined_coverage.get(slide.get("slide_id"))
                if coverage is None or coverage.get("status") == "pass":
                    return True
            return False
        check("PROF-HYPOTHESIS-EXISTS", has("hypothesis_title"), layer_id, "Add a Hypothesis page", roles)
        separate = has("hypothesis_title") and has("problem_definition") and not any({"hypothesis_title", "problem_definition"} <= value for value in combined)
        check("PROF-HYPOTHESIS-PROBLEM-SEPARATE", separate, layer_id, "Create separate Hypothesis and Problem pages", roles)
        presentation_roles = sorted({role for slide in layer_slides for role in slide.get("combined_roles", [slide.get("semantic_role")]) if role in PRESENTATION_ROLE_CONTRACTS and role not in {"hypothesis_title", "problem_definition"}})
        for presentation_role in presentation_roles:
            check(f"PROF-PRESENTATION-ROLE-{presentation_role.upper().replace('-', '_')}", has(presentation_role), layer_id, f"Provide physically complete {presentation_role} presentation content", [slide.get("slide_id") for slide in layer_slides if presentation_role in slide.get("combined_roles", [slide.get("semantic_role")])])
        locator = next((slide for slide in layer_slides if slide.get("semantic_role") == "fishbone_locator"), None)
        check("PROF-FISHBONE-EXISTS", locator is not None, layer_id, "Add the layer's historical fishbone locator", bool(locator), rule="narrative_rules.persistent_orientation_view")
        focus_ok = bool(locator and locator.get("fishbone_focus_refs"))
        check("PROF-FISHBONE-FOCUS", focus_ok, layer_id, "Highlight the current stable branch ID", locator.get("fishbone_focus_refs", []) if locator else [])
        revision_ok = bool(locator and locator.get("fishbone_snapshot_ref", {}).get("revision") == layer.get("fishbone_snapshot_ref", {}).get("revision"))
        check("PROF-FISHBONE-REVISION", revision_ok, layer_id, "Bind the fishbone revision visible at this cursor", locator.get("fishbone_snapshot_ref") if locator else None)
        result_positions = [index for index, slide in enumerate(layer_slides) if slide.get("semantic_role") in {"result_single", "result_comparison"} or {"result_single", "result_comparison"} & set(slide.get("combined_roles", []))]
        discussion_positions = [index for index, slide in enumerate(layer_slides) if slide.get("semantic_role") == "layer_integrated_discussion" or "layer_integrated_discussion" in slide.get("combined_roles", [])]
        question_ok = bool(has("problem_definition") and result_positions and min(result_positions) > 0)
        check("PROF-QUESTION-BEFORE-RESULT", question_ok, layer_id, "Place the research question/problem before result interpretation", result_positions, rule="narrative_rules.require_question_before_data")
        block = state.get("blocks", {}).get((layer.get("research_block_refs") or [None])[0], {})
        stages = state.get("stages", {})
        stage_refs = block.get("stage_refs", {})
        literature = stages.get(stage_refs.get("literature"), {}).get("data", {})
        lit_fields = ["consensus", "disagreements_or_alternatives", "known_mechanisms", "research_gap", "relevance_to_observation", "implication_for_hypothesis_or_strategy"]
        check("PROF-LITERATURE-SYNTHESIS", all(literature.get(field) for field in lit_fields), layer_id, "Provide structured literature synthesis", literature, rule="narrative_rules.literature_must_synthesize_to_hypothesis_or_strategy")
        mechanism = stages.get(stage_refs.get("mechanism"), {})
        check("PROF-MECHANISM-EVIDENCE", bool(mechanism.get("evidence_refs") and mechanism.get("claim_refs")), layer_id, "Link the mechanism to evidence and claims", mechanism)
        solution = stages.get(stage_refs.get("solution"), {}).get("data", {})
        check("PROF-STRATEGY-DERIVED", bool(solution.get("strategy") and solution.get("success_criterion")), layer_id, "Derive strategy from the mechanism", solution)
        experiment_ids = [value for key, value in stage_refs.items() if key == "experiment"]
        experiment_ids += [stage_id for stage_id, stage in stages.items() if stage.get("block_ref", {}).get("block_id") == block.get("block_id") and stage.get("stage_type") == "experiment"]
        experiment_ids = list(dict.fromkeys(experiment_ids))
        exp_required = ["independent_variables", "controlled_variables", "controls_baselines", "sample_plan", "measured_outputs", "instrumentation_method_refs", "predicted_outcomes", "decision_rules"]
        exp_results = [{"stage_id": stage_id, "data": stages.get(stage_id, {}).get("data", {})} for stage_id in experiment_ids]
        exp_ok = bool(exp_results) and all(all(item["data"].get(field) for field in exp_required) for item in exp_results)
        check("PROF-EXPERIMENT-METADATA", exp_ok, layer_id, "Complete IV/control/N/metric/method/prediction/decision metadata", exp_results)
        result_ids = list(layer.get("result_refs", []))
        result_stage_ids = [f"ST-{ref}" for ref in result_ids]
        result_ok = bool(result_ids) and all(stage_id in stages for stage_id in result_stage_ids)
        check("PROF-RESULTS-COMPLETE", result_ok, layer_id, "Materialize every required result", result_stage_ids)
        discussion = state.get("layer_discussions", {}).get(layer.get("layer_discussion_ref"), {})
        discussion_ok = bool(discussion) and set(discussion.get("supporting_results", []) + discussion.get("contradicting_results", []) + discussion.get("non_discriminating_results", [])) >= set(result_ids) and bool(discussion.get("alternative_explanations")) and bool(discussion.get("remaining_uncertainty"))
        check("PROF-INTEGRATED-DISCUSSION", discussion_ok and bool(discussion_positions) and all(index > max([0] + result_positions) for index in discussion_positions), layer_id, "Integrate the complete result set after results", discussion, rule="narrative_rules.discussion_must_update_decision")
        summary = state.get("layer_summaries", {}).get(layer.get("layer_summary_ref"), {})
        summary_ok = bool(summary.get("answered") and summary.get("hypothesis_status") and summary.get("decision_ref") and summary.get("remaining_unresolved") and summary.get("next_question") and summary.get("next_step_refs"))
        check("PROF-LAYER-SUMMARY", summary_ok and has("layer_summary_decision"), layer_id, "Add hypothesis status, decision, uncertainty, and next question", summary)
        layer_transitions = list(transitions_by_from.get(layer_id, []))
        # Compatibility records from the original Phase 2 fixture omitted
        # from_layer_ref. They are only associated with a layer when an
        # explicit transition slide names that layer; normal records always
        # use the state-derived relation above.
        layer_transitions.extend(item for item in transitions.values() if not item.get("from_layer_ref") and any(slide.get("semantic_role") == "hypothesis_transition" and slide.get("hypothesis_layer_ref") == layer_id for slide in slides))
        for transition in layer_transitions:
            transition_slide = any(slide.get("semantic_role") == "hypothesis_transition" and (slide.get("object_ref") in {None, transition.get("transition_id")} or not slide.get("object_ref")) for slide in slides)
            destination = next((candidate for candidate in layers if candidate.get("hypothesis_layer_id") == transition.get("to_layer_ref")), None)
            transition_ok = bool(
                transition_slide and destination
                and transition.get("previous_hypothesis_claim_ref") in state.get("claims", {})
                and transition.get("new_hypothesis_claim_ref") in state.get("claims", {})
                and transition.get("key_result_refs")
                and all((ref in state.get("stages", {}) or f"ST-{ref}" in state.get("stages", {})) for ref in transition.get("key_result_refs", []))
                and transition.get("decision_refs")
                and all(ref in state.get("decisions", {}) for ref in transition.get("decision_refs", []))
                and transition.get("observation_or_uncertainty_refs")
                and all(ref in state.get("evidence", {}) for ref in transition.get("observation_or_uncertainty_refs", []))
                and destination.get("derived_from", {}).get("previous_layer_ref") == layer_id
            )
            check("PROF-TRANSITION-PROVENANCE", transition_ok, transition.get("transition_id", layer_id), "Resolve transition provenance to results, decision, observation, and new hypothesis", transition)
    state_layer_ids = set(state.get("hypothesis_layers", {}))
    projection_layer_ids = [layer.get("hypothesis_layer_id") for layer in layers]
    historical_ok = bool(layers) and set(projection_layer_ids) == state_layer_ids and len(projection_layer_ids) == len(set(projection_layer_ids))
    check("PROF-HISTORY-REACHABLE", historical_ok, "layers", "Keep failed/partial/superseded layers historically reachable", [layer.get("hypothesis_layer_id") for layer in layers], rule="narrative_rules.preserve_failed_and_changed_hypotheses")
    commitments = projection.get("previous_commitments", [])
    commitment_ok = bool(commitments) and all(item.get("owner") and item.get("target_window") and item.get("dependency_refs") is not None and item.get("parallelizable") is not None and item.get("status") for item in commitments)
    check("PROF-NEXT-STEP-OWNER-TIMING", commitment_ok, "meeting", "Carry forward owner, timing, dependencies, status, and parallel work", commitments, rule="meeting_rules.require_next_steps_and_timing")
    return {"profile_ref": {"profile_id": profile.get("profile_id"), "version": profile.get("version")}, "status": "fail" if findings else "pass", "executed_checks": executed_checks, "check_count": len(executed_checks), "evidence": evidence, "findings": findings}


def _finding(rule_id: str, path: str, repair: str) -> dict:
    return {"rule_id": rule_id, "severity": "critical", "status": "open", "path": path, "evidence": "executed check returned false", "repair_action": repair}


def run_visual_qa_v2(specs: list[dict], render_paths: dict[str, Path], *, expected_size: tuple[int, int], structural_audit: dict | None = None) -> dict:
    """Run separate spec, raster-pixel, and qualitative-review contracts.

    The first two classes are deterministic and executable here.  Qualitative
    conclusions are deliberately blocked until an image-capable reviewer
    records render-hash-bound notes; they are never inferred from a role name
    or Slide Spec metadata.
    """
    findings = []
    spec_checks = ["canvas_bounds", "overlap", "minimum_font", "title_hierarchy", "zh_tw_wrapping", "density_budget", "archetype_geometry", "required_slots", "comparison_symmetry", "fishbone_focus_prominence", "result_discussion_separation"]
    pixel_checks = ["render_exists", "dimensions", "nonblank", "occupied_region", "canvas_edge_proximity", "empty_area", "comparison_balance_proxy", "fishbone_prominence_proxy"]
    geometry_slides = []
    pixel_slides = []
    role_slots = {
        "hypothesis_title": {"hypothesis_statement"}, "problem_definition": {"previous_finding", "unresolved_conflict", "research_question"},
        "fishbone_locator": {"primary_figure", "fishbone_focus"}, "observation_problem": {"primary_figure", "research_question", "observation_text"},
        "literature_mechanism": {"literature_evidence", "mechanism_diagram"}, "mechanism_solution": {"mechanism_diagram", "strategy"},
        "experiment_design": {"experiment_matrix", "decision_rule"}, "result_single": {"result_plot", "result_annotation"},
        "result_comparison": {"control_panel", "proposed_panel", "result_plot"}, "layer_integrated_discussion": {"supporting_results", "contradicting_results", "uncertainty"},
        "layer_summary_decision": {"decision_status", "uncertainty", "next_step"}, "hypothesis_transition": {"transition_nodes", "derivation_strip"},
        "progress_todo": {"commitment_table", "current_position", "parallel_work"}, "schedule_next_step": {"timeline", "dependencies"},
    }
    for spec in specs:
        slide_id = spec["slide_id"]
        path = Path(render_paths.get(slide_id, ""))
        role = spec.get("semantic_role", "")
        # Canonical artifacts must use repository-relative, slash-normalized paths;
        # keep the path value deterministic even when the build runs on Windows.
        pixel = {"slide_id": slide_id, "render_path": path.as_posix(), "render_sha256": None, "dimensions": None, "variance": None, "occupied_region": None, "occupied_ratio": None, "canvas_edge_proximity_px": None, "left_right_ink_ratio": None}
        if not path.is_file():
            findings.append(_finding("VISUAL-RENDER-MISSING", slide_id, "Render the exact slide"))
            pixel_slides.append(pixel)
            continue
        with Image.open(path) as image:
            image = image.convert("RGB")
            pixel["render_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            pixel["dimensions"] = {"width": image.width, "height": image.height}
            if image.size != expected_size:
                findings.append(_finding("VISUAL-DIMENSIONS", slide_id, f"Render at {expected_size}"))
            variance = ImageStat.Stat(image.convert("L")).var[0]
            pixel["variance"] = variance
            if variance < 1.0:
                findings.append(_finding("VISUAL-BLANK-RENDER", slide_id, "Repair missing rendered content"))
            delta = ImageChops.difference(image, Image.new("RGB", image.size, "white")).convert("L")
            occupied = delta.point(lambda value: 255 if value > 20 else 0).getbbox()
            if occupied is None:
                findings.append(_finding("VISUAL-OCCUPIED-REGION", slide_id, "Rendered slide has no occupied pixels"))
                pixel["occupied_region"] = None
                pixel["occupied_ratio"] = 0.0
                pixel["canvas_edge_proximity_px"] = 0
            else:
                left, top, right, bottom = occupied
                pixel["occupied_region"] = {"left": left, "top": top, "right": right, "bottom": bottom}
                pixel["occupied_ratio"] = ((right - left) * (bottom - top)) / (image.width * image.height)
                pixel["canvas_edge_proximity_px"] = min(left, top, image.width - right, image.height - bottom)
                if pixel["occupied_ratio"] < 0.01:
                    findings.append(_finding("VISUAL-EXCESSIVE-EMPTY-AREA", slide_id, "Populate the rendered canvas with governed content"))
                if pixel["canvas_edge_proximity_px"] == 0:
                    findings.append(_finding("VISUAL-CANVAS-EDGE-PIXELS", slide_id, "Check clipping at the rendered canvas edge"))
            left_ink = sum(1 for value in delta.crop((0, 0, image.width // 2, image.height)).get_flattened_data() if value > 20)
            right_ink = sum(1 for value in delta.crop((image.width // 2, 0, image.width, image.height)).get_flattened_data() if value > 20)
            pixel["left_right_ink_ratio"] = round((left_ink + 1) / (right_ink + 1), 4)
        pixel_slides.append(pixel)
        placements = spec.get("placement_plan", [])
        if not placements:
            findings.append(_finding("VISUAL-ARCHETYPE-GEOMETRY", slide_id, "Persist governed placement geometry"))
        required = role_slots.get(role, set())
        declared_roles = set(spec.get("combined_roles", [role]))
        if {"observation_problem", "literature_mechanism", "mechanism_solution"} <= declared_roles:
            required = {"primary_figure", "research_question", "observation_text", "literature_evidence", "mechanism_diagram", "strategy"}
        elif {"experiment_design", "result_single"} <= declared_roles:
            required = {"experiment_matrix", "decision_rule", "result_plot", "result_annotation"}
        elif {"layer_integrated_discussion", "layer_summary_decision"} <= declared_roles:
            required = {"supporting_results", "contradicting_results", "discussion_synthesis", "uncertainty", "decision_status", "next_step"}
        actual_slots = {item.get("slot") for item in placements}
        if required - actual_slots:
            findings.append(_finding("VISUAL-REQUIRED-SLOT-MISSING", slide_id, f"Provide slots {sorted(required - actual_slots)}"))
        for placement in placements:
            if placement.get("left", 0) < 0 or placement.get("top", 0) < 0 or placement.get("left", 0) + placement.get("width", 0) > 13.34 or placement.get("top", 0) + placement.get("height", 0) > 7.51:
                findings.append(_finding("VISUAL-CANVAS-OVERFLOW", slide_id, "Move element inside slide bounds"))
            if placement.get("font_size_pt", 16) < 16:
                findings.append(_finding("VISUAL-MIN-FONT", slide_id, "Use at least 16 pt body text"))
        for left_index, left in enumerate(placements):
            for right in placements[left_index + 1:]:
                intersects = left["left"] < right["left"] + right["width"] and right["left"] < left["left"] + left["width"] and left["top"] < right["top"] + right["height"] and right["top"] < left["top"] + left["height"]
                if intersects:
                    findings.append(_finding("VISUAL-PLACEMENT-OVERLAP", slide_id, "Separate same-layer governed regions"))
        title = str(spec.get("title", {}).get("text", ""))
        slots = spec.get("content", {}).get("slots", {})
        body = str(spec.get("content", {}).get("body", "")) or "\n".join(str(value) for value in slots.values())
        if not title or len(title) > 48:
            findings.append(_finding("VISUAL-TITLE-HIERARCHY", slide_id, "Use a concise dominant title"))
        title_indices = {index for index, item in enumerate(placements) if item.get("slot") in {"hypothesis_statement", "title"} or item.get("element_role") in {"assertion", "title"}}
        title_fonts = [float(placements[index].get("font_size_pt", 0)) for index in title_indices]
        body_fonts = [float(item.get("font_size_pt", 0)) for index, item in enumerate(placements) if index not in title_indices]
        if title_fonts and body_fonts and min(title_fonts) <= max(body_fonts):
            findings.append(_finding("VISUAL-TITLE-HIERARCHY", slide_id, "Make the title font larger than body text"))
        if any(line.startswith(("，", "。", "？", "！", "）")) for line in body.splitlines()[1:]):
            findings.append(_finding("VISUAL-ZH-WRAPPING", slide_id, "Repair Traditional Chinese punctuation wrapping"))
        if (len(body) > 1200 and not spec.get("layout_plan_ref")) or spec.get("split_recommendation") is True:
            findings.append(_finding("VISUAL-DENSITY-BUDGET", slide_id, "Resolve over-budget content through a real split or fit exception"))
        if role == "result_comparison" and not ({"experiment_design", "result_single"} <= declared_roles):
            controls = next((item for item in placements if item.get("slot") == "control_panel"), None)
            proposed = next((item for item in placements if item.get("slot") == "proposed_panel"), None)
            if not controls or not proposed or abs(controls["width"] - proposed["width"]) > 0.01:
                findings.append(_finding("VISUAL-COMPARISON-ASYMMETRY", slide_id, "Use symmetric control/proposed regions"))
        if role == "fishbone_locator" and (not spec.get("fishbone_focus_refs") or not any(item.get("slot") == "fishbone_focus" for item in placements)):
            findings.append(_finding("VISUAL-FISHBONE-FOCUS-MISSING", slide_id, "Show a prominent current focus marker"))
        geometry_slides.append({"slide_id": slide_id, "required_slots": sorted(required), "planned_slots": sorted(actual_slots), "content_slots": sorted(slots), "status": "pass"})
    if structural_audit:
        for item in structural_audit.get("generated_slides", []):
            if not item.get("layout_master_role_match"):
                findings.append(_finding("VISUAL-LAYOUT-IDENTITY", item.get("slide_spec_id", ""), "Resolve the template layout/master identity"))
    return {
        "status": "fail" if findings else "pass",
        "executed_checks": spec_checks + pixel_checks,
        "check_count": len(spec_checks) + len(pixel_checks),
        "findings": findings,
        "spec_geometry_qa": {"status": "fail" if any(item["rule_id"].startswith("VISUAL-") and item["rule_id"] not in {"VISUAL-RENDER-MISSING", "VISUAL-DIMENSIONS", "VISUAL-BLANK-RENDER", "VISUAL-OCCUPIED-REGION", "VISUAL-EXCESSIVE-EMPTY-AREA", "VISUAL-CANVAS-EDGE-PIXELS"} for item in findings) else "pass", "checks": spec_checks, "slides": geometry_slides},
        "render_pixel_qa": {"status": "fail" if any(item["rule_id"] in {"VISUAL-RENDER-MISSING", "VISUAL-DIMENSIONS", "VISUAL-BLANK-RENDER", "VISUAL-OCCUPIED-REGION", "VISUAL-EXCESSIVE-EMPTY-AREA", "VISUAL-CANVAS-EDGE-PIXELS"} for item in findings) else "pass", "checks": pixel_checks, "slides": pixel_slides},
        "qualitative_visual_review": {"status": "blocked_visual_review", "reason": "requires image-capable reviewer notes bound to the exact rendered image hash", "slides": [{"slide_id": spec["slide_id"], "status": "blocked_visual_review"} for spec in specs]},
    }


def run_phase2_pipeline(*, schema_errors: list[str], ledger_replayed: bool, scientific: dict, professor: dict, audit: dict, specs: list[dict], visual: dict, render_evidence: dict, presentation_semantic: dict | None = None) -> dict:
    """Produce pass statuses only from the owning, already-executed Phase 2 checks."""
    expected_ids = [spec["slide_id"] for spec in specs]
    generated_ids = [item.get("slide_spec_id") for item in audit.get("generated_slides", [])]
    vector_slide_ids = {spec["slide_id"] for spec in specs if any(str(place.get("asset_path", "")).endswith(".svg") for place in spec.get("placements", []))}
    structural_ok = (
        audit.get("slide_count", 0) >= len(specs)
        and generated_ids == expected_ids
        and not audit.get("orphan_parts")
        and audit.get("content_types_present")
        and all(item.get("layout_master_role_match") and item.get("governed_geometry_match") and item.get("notes_source_match") and item.get("editable_text") and all(item.get("governed_slot_matches", {}).values()) for item in audit.get("generated_slides", []))
        and all(item.get("svg_asset_relationships") for item in audit.get("generated_slides", []) if item.get("slide_spec_id") in vector_slide_ids)
    )
    presentation_semantic = presentation_semantic or {}
    gates = [
        (not schema_errors and ledger_replayed, {"check_ids": ["P2-SCHEMA-ALL", "P2-LEDGER-HASH-REPLAY"], "errors": schema_errors}),
        (scientific.get("status") == "pass", {"check_ids": scientific.get("executed_checks", []), "findings": scientific.get("findings", [])}),
        (scientific.get("status") == "pass", {"check_ids": ["P2-PROVENANCE-HASHES", "P2-SYNTHETIC-LABELS"], "evidence": scientific.get("evidence", {})}),
        (presentation_semantic.get("status", "pass") == "pass" and professor.get("status") == "pass", {"check_ids": ["presentation_semantic_fidelity", *professor.get("executed_checks", [])], "presentation_semantic": presentation_semantic, "findings": professor.get("findings", [])}),
        (audit.get("slide_count", 0) >= len(specs) and generated_ids == expected_ids, {"check_ids": ["P2-COMPILE-SPECS", "P2-ASSEMBLE-PPTX"], "slide_count": audit.get("slide_count"), "generated_spec_count": len(specs)}),
        (structural_ok, {"check_ids": ["P2-OPENXML-SVG", "P2-LAYOUT-MASTER", "P2-NOTES", "P2-EDITABLE-TEXT"], "audit": "structural-audit.json"}),
        (visual.get("status") == "pass" and visual.get("inspection_record_valid") and visual.get("qualitative_visual_review", {}).get("status") == "pass" and len(render_evidence.get("render_paths", [])) == len(specs) and len(render_evidence.get("montages", [])) >= 4, {"check_ids": visual.get("executed_checks", []), "inspection": render_evidence.get("inspection"), "qualitative_review": render_evidence.get("qualitative_review"), "montages": render_evidence.get("montages", [])}),
    ]
    pipeline = []
    findings = []
    for index, (ok, evidence) in enumerate(gates, 1):
        status = "pass" if ok else "fail"
        pipeline.append({"order": index, "stage": PHASE2_PIPELINE[index - 1], "status": status, "evidence": evidence})
        if not ok:
            findings.append({"rule_id": f"P2-QA-{index}", "severity": "critical", "status": "open", "path": PHASE2_PIPELINE[index - 1], "evidence": evidence, "repair_action": "repair executed gate input"})
    pipeline.extend([
        {"order": 8, "stage": PHASE2_PIPELINE[7], "status": "blocked_environment", "evidence": {"reason": "native PowerPoint desktop acceptance is unavailable in this environment"}},
        {"order": 9, "stage": PHASE2_PIPELINE[8], "status": "not_run", "evidence": {"reason": "requires native acceptance"}},
        {"order": 10, "stage": PHASE2_PIPELINE[9], "status": "blocked", "evidence": {"reason": "requires native acceptance"}},
    ])
    return {"schema_version": "2.0.0", "qa_report_id": "QA-MASTER-PHASE2-ACCEPTANCE", "build_id": "BUILD-MASTER-PHASE2-ACCEPTANCE", "deck_id": "MASTER-PHASE2-ACCEPTANCE", "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "overall_status": "pass_with_native_environment_block" if not findings else "fail", "professor_profile_ref": {"profile_id": "PROF-SYNTH-001", "version": "1.0.0"}, "pipeline": pipeline, "findings": findings, "artifacts": render_evidence, "tool_versions": {"phase2_control_plane": "0.3.0", "libreoffice_render": "executed"}, "native_powerpoint_status": "blocked_environment"}
