"""Checkpoint 4: sanitized-only scientific figure control plane.

This module deliberately creates routing records only.  It neither opens a
private source nor invokes a renderer, image provider, PPTX backend, or figure
director.  Those are later checkpoint responsibilities.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "thesis-deck-system" / "schemas"
ROUTING_PATH = ROOT / "thesis-deck-system" / "skill-routing.yaml"
CP3_INPUTS = (
    "professor-template-resolved.json", "body-composition-profile.json",
    "professor-visual-grammar-v3.json", "visual-style-profile.json",
    "resolver-evidence.json", "checkpoint-3-qa.json",
)
CP4_SCHEMAS = (
    "figure-production-plan.schema.json", "scientific-figure-spec.schema.json",
    "skill-routing.schema.json", "archetype-figure-routing.schema.json",
    "checkpoint-4-execution-evidence.schema.json", "checkpoint-4-qa.schema.json",
)
REQUIRED_SKILLS = {
    "thesis-deck-router", "scientific-figure-router", "fishbone-director",
    "mechanism-diagram-director", "experiment-schematic-director",
    "fabrication-process-director", "scientific-plot-director",
    "photo-annotation-director", "literature-figure-director",
    "comparison-figure-director", "image-matrix-director",
    "concept-illustration-director", "vector-figure-builder",
    "visual-style-governor", "figure-critic", "layout-director", "provenance-qa",
}
ROUTES = {
    "quantitative_measured_result": ("scientific-plot-director", "reproducible_plot", "svg_vector", False, "canonical_data"),
    "real_experiment_photo": ("photo-annotation-director", "real_evidence_overlay", "source_evidence_asset", False, "real_evidence"),
    "literature_figure": ("literature-figure-director", "source_extraction_overlay", "extracted_source_figure", False, "literature_source"),
    "mechanism_explanation": ("mechanism-diagram-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec"),
    "experiment_setup": ("experiment-schematic-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec"),
    "fabrication_process": ("fabrication-process-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec"),
    "fishbone_history": ("fishbone-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec"),
    "fair_comparison": ("comparison-figure-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec"),
    "image_matrix": ("image-matrix-director", "deterministic_svg_vector", "svg_vector", False, "real_evidence"),
    "organic_concept": ("concept-illustration-director", "generated_non_evidence", "generated_non_evidence_substrate", True, "non_evidence_only"),
}


class Checkpoint4Error(ValueError):
    """A routing/input boundary cannot be safely satisfied."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Checkpoint4Error(message)


def _list_strings(value: Any, name: str) -> list[str]:
    _require(isinstance(value, list) and all(isinstance(item, str) for item in value), f"{name} must be a string list")
    return sorted(set(value))


def route_figure_request(request: dict[str, Any]) -> dict[str, Any]:
    """Resolve a request into a deterministic FigureProductionPlan, never an asset."""
    visual_class = request.get("visual_class")
    _require(visual_class in ROUTES, "unknown visual class route")
    director, renderer, output, ai_allowed, source_requirement = ROUTES[visual_class]
    evidence_status = request.get("evidence_status")
    support = request.get("scientific_claim_support")
    sources = _list_strings(request.get("source_refs", []), "source_refs")
    claims = _list_strings(request.get("claim_refs", []), "claim_refs")
    evidence = _list_strings(request.get("evidence_refs", []), "evidence_refs")
    _require(request.get("figure_plan_id") and request.get("scientific_purpose"), "figure identity/purpose required")
    _require(request.get("hypothesis_layer_ref") and request.get("research_block_refs") and request.get("stage_ref"), "scientific binding required")
    _require(isinstance(request.get("source_cursor"), int) and request["source_cursor"] > 0, "source cursor required")
    _require(request.get("provenance_rule_ids"), "routing provenance required")
    if visual_class == "organic_concept":
        _require(evidence_status == "non_evidence" and support == "forbidden" and not claims and not evidence, "concept must remain non-evidence without claim/evidence binding")
    else:
        _require(evidence_status != "non_evidence", "non-concept visual cannot masquerade as non-evidence")
        _require(support != "forbidden", "scientific route requires its declared support state")
    if visual_class in {"quantitative_measured_result", "real_experiment_photo", "literature_figure", "image_matrix"}:
        _require(sources and evidence, "empirical/literature route requires source and evidence identity")
    _require(not request.get("ai_generation_requested") or ai_allowed, "AI generation prohibited for this visual class")
    if request.get("fabrication_steps") is not None:
        _require(visual_class == "fabrication_process", "fabrication chronology requires fabrication-process-director")
    if visual_class == "fabrication_process":
        steps = request.get("fabrication_steps")
        _require(isinstance(steps, list) and steps, "fabrication steps required")
        _require([step.get("ordinal") for step in steps] == list(range(1, len(steps) + 1)), "fabrication order must be explicit")
    if visual_class == "fishbone_history":
        binding = request.get("fishbone_binding")
        _require(isinstance(binding, dict) and all(binding.get(key) for key in ("fishbone_revision_ref", "focus_ref", "history_ref")), "fishbone revision/focus/history binding required")
    native = {"status": "insufficient_evidence", "rule_id": "CP4-SVG-FIRST-UNMEASURED-NATIVE-THRESHOLD", "reason": "no_cp3_measured_native_eligibility_threshold"}
    payload: dict[str, Any] = {"kind": visual_class}
    if visual_class == "fabrication_process":
        payload["steps"] = [{"ordinal": item["ordinal"], "condition_state": item.get("condition_state", "unknown")} for item in request["fabrication_steps"]]
    if visual_class == "fishbone_history":
        payload["fishbone_binding"] = {key: request["fishbone_binding"][key] for key in ("fishbone_revision_ref", "focus_ref", "history_ref")}
    return {
        "schema_version": "4.0.0", "figure_plan_id": request["figure_plan_id"], "visual_class": visual_class,
        "scientific_purpose": request["scientific_purpose"], "evidence_status": evidence_status,
        "scientific_claim_support": support, "source_refs": sources, "claim_refs": claims, "evidence_refs": evidence,
        "hypothesis_layer_ref": request["hypothesis_layer_ref"], "research_block_refs": sorted(set(request["research_block_refs"])),
        "stage_ref": request["stage_ref"], "source_cursor": request["source_cursor"],
        "selected_specialist_skill": director, "renderer_class": renderer, "canonical_output_kind": output,
        "source_asset_required": source_requirement in {"real_evidence", "literature_source"}, "ai_generation_allowed": ai_allowed,
        "native_shape_eligibility": native, "style_profile_ref": "VSP001",
        "required_style_categories": ["body_composition", "line_style_grammar", "color_emphasis_grammar"],
        "style_usage_policy": {"professor_recurring_allowed": True, "professor_provisional_allowed_with_flag": True, "fallback_required": True, "blocked_unresolved": ["material_semantic_colors"]},
        "required_qa": ["provenance_qa", "figure_critic"], "handoff_target": "selected_specialist_director",
        "status": "routed_not_rendered", "provenance_rule_ids": sorted(set(request["provenance_rule_ids"])),
        "specialist_payload": payload, "requested_archetype": request.get("requested_archetype"),
    }


def validate_layout_figure_handoff(candidate: dict[str, Any]) -> None:
    _require(candidate.get("artifact_kind") == "approved_figure" and candidate.get("status") == "APPROVED_FIGURE", "Layout Director accepts only FigureCritic-approved figures")
    _require(candidate.get("provenance_ref"), "approved figure provenance required")


def _skill_contract(skill_id: str, *, output: str, handoff: str) -> dict[str, Any]:
    return {"skill_id": skill_id, "trigger": "schema_valid_routed_request", "do_not_trigger": "missing_provenance_or_out_of_scope", "inputs": ["FigureProductionPlan"], "required_context": ["materialized_scientific_state", "source_cursor", "visual_style_profile"], "workflow": ["validate", "preserve_provenance", "emit_declared_contract"], "allowed_downstream": [handoff], "forbidden_actions": ["invent_science", "bypass_figure_critic"], "output_contract": output, "provenance_behavior": "hash_bound_input_refs", "failure_modes": ["missing_ref", "invalid_contract"], "blocked_states": ["blocked_missing_provenance"], "handoff_target": handoff, "qa_owner": "provenance-qa"}


def load_skill_registry() -> dict[str, Any]:
    return yaml.safe_load(ROUTING_PATH.read_text(encoding="utf-8"))


def validate_skill_registry(registry: dict[str, Any]) -> None:
    skills = registry.get("skills")
    _require(isinstance(skills, list), "skill registry requires skills")
    ids = [item.get("skill_id") for item in skills if isinstance(item, dict)]
    _require(set(ids) == REQUIRED_SKILLS and len(ids) == len(REQUIRED_SKILLS), "skill registry must have exact required identities")
    required = {"trigger", "do_not_trigger", "inputs", "required_context", "workflow", "allowed_downstream", "forbidden_actions", "output_contract", "provenance_behavior", "failure_modes", "blocked_states", "handoff_target", "qa_owner"}
    _require(all(required <= set(item) for item in skills), "skill contract incomplete")


def archetype_routing_matrix() -> list[dict[str, Any]]:
    routes = {
        "A01": ["thesis-deck-router"], "A02": ["thesis-deck-router"], "A03": ["fishbone-director"],
        "A04": ["photo-annotation-director"], "A05": ["literature-figure-director", "mechanism-diagram-director"],
        "A06": ["mechanism-diagram-director", "fabrication-process-director"], "A07": ["photo-annotation-director", "experiment-schematic-director", "fabrication-process-director"],
        "A08": ["comparison-figure-director"], "A09": ["experiment-schematic-director", "fabrication-process-director"],
        "A10": ["scientific-plot-director", "photo-annotation-director"], "A11": ["scientific-plot-director", "comparison-figure-director"],
        "A12": ["image-matrix-director"], "A13": ["scientific-plot-director"], "A14": ["thesis-deck-router"],
        "A15": ["thesis-deck-router"], "A16": ["mechanism-diagram-director"], "A17": ["thesis-deck-router"], "A18": ["thesis-deck-router"],
    }
    return [{"archetype_id": name, "route_skills": skills, "geometry_calibration_status": "not_run", "routing_only": True} for name, skills in sorted(routes.items())]


def _components(inputs: dict[str, dict], registry: dict[str, Any]) -> dict[str, str]:
    _require(set(inputs) == set(CP3_INPUTS), "exact CP3 input set required")
    component = {f"cp3:{key}": _hash(value) for key, value in sorted(inputs.items())}
    component["cp4:phase3_checkpoint4.py"] = sha256(Path(__file__).read_bytes()).hexdigest()
    component["skill-registry:skill-routing.yaml"] = sha256(ROUTING_PATH.read_bytes()).hexdigest()
    component.update({f"schema:{name}": sha256((SCHEMAS / name).read_bytes()).hexdigest() for name in CP4_SCHEMAS})
    return component


def _schema_registry() -> Any:
    from .contracts import SchemaRegistry
    return SchemaRegistry(SCHEMAS, include_phase3=True)


def _schema_closed(schema: Any) -> bool:
    if isinstance(schema, dict):
        if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
            # A map is closed when its dynamic values are themselves a bounded
            # primitive schema (component hashes), not an arbitrary object.
            additional = schema.get("additionalProperties")
            if not (isinstance(additional, dict) and ((additional.get("type") == "string" and additional.get("pattern") == "^[a-f0-9]{64}$") or "$ref" in additional)):
                return False
        return all(_schema_closed(value) for value in schema.values())
    if isinstance(schema, list):
        return all(_schema_closed(value) for value in schema)
    return True


def _cp3_inputs_valid(inputs: dict[str, dict]) -> bool:
    registry = _schema_registry()
    mapping = {
        "professor-template-resolved.json": "professor-template-resolved",
        "body-composition-profile.json": "body-composition-profile",
        "professor-visual-grammar-v3.json": "professor-visual-grammar-v3",
        "visual-style-profile.json": "visual-style-profile",
        "resolver-evidence.json": "resolver-evidence",
        "checkpoint-3-qa.json": "checkpoint-3-qa",
    }
    return set(inputs) == set(mapping) and all(not registry.errors(schema_name, inputs[name]) for name, schema_name in mapping.items())


def _privacy_scan(privacy_config: dict[str, Any] | None) -> tuple[bool, dict[str, Any]]:
    """Run the approved repository and index scanner without retaining secrets."""
    # CP3 owns the fail-closed scanner and its one reviewed historical exception.
    # CP4 consumes its sanitized count/hash result rather than duplicating policy.
    from .phase3_checkpoint3 import _approved_privacy_scan

    result, evidence = _approved_privacy_scan(privacy_config)
    required = {
        "scanner_id", "scanner_version", "configuration_hash", "repository_findings",
        "staged_findings", "approved_legacy_exceptions", "repository_scan_executed",
        "staged_scan_executed",
    }
    _require(required <= set(evidence), "privacy scanner evidence incomplete")
    return result, {key: evidence[key] for key in sorted(required)}


def build_checkpoint4_artifacts(inputs: dict[str, dict], *, privacy_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build deterministic synthetic routing records from sanitized CP3 artifacts only."""
    registry = load_skill_registry(); validate_skill_registry(registry)
    _require(_cp3_inputs_valid(inputs), "CP3 input schema validation failed")
    _require(inputs["checkpoint-3-qa.json"].get("aggregate_status") == "pass", "CP3 QA must pass")
    requests = [
        {"figure_plan_id": "FPL001", "visual_class": "quantitative_measured_result", "scientific_purpose": "result_display", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A10", "provenance_rule_ids": ["CP4-ROUTE-QUANTITATIVE"]},
        {"figure_plan_id": "FPL002", "visual_class": "fishbone_history", "scientific_purpose": "research_history", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A03", "provenance_rule_ids": ["CP4-ROUTE-FISHBONE"], "fishbone_binding": {"fishbone_revision_ref": "FB001-R001", "focus_ref": "BR001", "history_ref": "H001"}},
        {"figure_plan_id": "FPL003", "visual_class": "fabrication_process", "scientific_purpose": "process_chronology", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A09", "provenance_rule_ids": ["CP4-ROUTE-FABRICATION"], "fabrication_steps": [{"ordinal": 1, "condition_state": "unknown"}]},
    ]
    plans = [route_figure_request(item) for item in requests]
    matrix = archetype_routing_matrix(); _require(len(matrix) == 18, "archetype routing incomplete")
    components = _components(inputs, registry)
    schemas_closed = all(_schema_closed(json.loads((SCHEMAS / name).read_text(encoding="utf-8"))) for name in CP4_SCHEMAS)
    module_text = Path(__file__).read_text(encoding="utf-8")
    private_api_absent = all(token not in module_text for token in ("Private" + "FixtureLocator", "private" + "://", "open_" + "private_source", "render_" + "private"))
    privacy_passed, privacy_evidence = _privacy_scan(privacy_config)
    checks = [
        ("CP4-CP3-INPUTS", _cp3_inputs_valid(inputs) and inputs["checkpoint-3-qa.json"].get("aggregate_status") == "pass"),
        ("CP4-PRIVATE-ACCESS", private_api_absent),
        ("CP4-ROUTING-DETERMINISM", all(route_figure_request(item) == route_figure_request(dict(reversed(list(item.items())))) for item in requests)),
        ("CP4-SKILL-REGISTRY", set(item["skill_id"] for item in registry["skills"]) == REQUIRED_SKILLS),
        ("CP4-HANDOFF-NO-BYPASS", registry["handoff_graph"] == ["scientific_state", "FigureProductionPlan", "selected_specialist_director", "future_renderer_output_manifest", "figure-critic", "APPROVED_FIGURE", "layout-director"] and all(plan["handoff_target"] == "selected_specialist_director" for plan in plans)),
        ("CP4-A01-A18-ROUTING", {row["archetype_id"] for row in matrix} == {f"A{i:02d}" for i in range(1, 19)}),
        ("CP4-SVG-FIRST", all(plan["native_shape_eligibility"]["status"] == "insufficient_evidence" and plan["renderer_class"] == "deterministic_svg_vector" for plan in plans if plan["visual_class"] != "quantitative_measured_result")),
        ("CP4-EMPIRICAL-AI-BOUNDARY", all(not plan["ai_generation_allowed"] for plan in plans if plan["evidence_status"] != "non_evidence")),
        ("CP4-FABRICATION-SEPARATION", all(plan["selected_specialist_skill"] == "fabrication-process-director" for plan in plans if plan["visual_class"] == "fabrication_process")),
        ("CP4-FISHBONE-PROVENANCE", all(plan["specialist_payload"].get("fishbone_binding") for plan in plans if plan["visual_class"] == "fishbone_history")),
        ("CP4-STYLE-GOVERNOR", inputs["visual-style-profile.json"].get("status") == "partial_structural_calibration" and all("material_semantic_colors" in plan["style_usage_policy"]["blocked_unresolved"] for plan in plans)),
        ("CP4-SCHEMA-CLOSURE", schemas_closed),
        ("CP4-REPOSITORY-STAGED-PRIVACY", privacy_passed),
    ]
    owning_checks = [{"check_id": ident, "status": "pass" if result else "fail", "evidence": {"facts": [{"name": "result", "boolean": bool(result)}]}} for ident, result in checks]
    for check in owning_checks:
        if check["check_id"] == "CP4-REPOSITORY-STAGED-PRIVACY":
            check["evidence"]["facts"] = [
                {"name": "repository_scan_executed", "boolean": privacy_evidence["repository_scan_executed"]},
                {"name": "staged_scan_executed", "boolean": privacy_evidence["staged_scan_executed"]},
                {"name": "unexcepted_findings_zero", "boolean": privacy_evidence["repository_findings"] == 0 and privacy_evidence["staged_findings"] == 0},
            ]
    execution = {"schema_version": "4.0.0", "execution_id": "CP4-EXEC-001", "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "candidate_state": {"component_hashes": components, "composite_candidate_state_hash": _hash(components)}, "privacy_scan": privacy_evidence, "owning_checks": owning_checks}
    qa = {"schema_version": "4.0.0", "qa_id": "CP4-QA-001", "aggregate_status": "pass" if all(item["status"] == "pass" for item in owning_checks) else "fail", "owning_check_refs": [item["check_id"] for item in owning_checks], "status_dimensions": {"production_figure_rendering": "not_run", "figure_critic_visual_acceptance": "not_run", "archetype_calibration": "not_run", "template_reconstruction": "not_run", "acceptance_deck": "not_run", "private_qualitative_review": "blocked_visual_review", "native_powerpoint": "not_run", "production_group_meeting_ready": False}}
    specs = [{"schema_version": "4.0.0", "figure_id": plan["figure_plan_id"].replace("FPL", "FIG"), "figure_type": "scientific_plot" if plan["visual_class"] == "quantitative_measured_result" else "vector_diagram", "scientific_purpose": plan["scientific_purpose"], "evidence_status": plan["evidence_status"], "source_refs": plan["source_refs"], "claim_refs": plan["claim_refs"], "evidence_refs": plan["evidence_refs"], "hypothesis_layer_ref": plan["hypothesis_layer_ref"], "research_block_refs": plan["research_block_refs"], "stage_ref": plan["stage_ref"], "source_cursor": plan["source_cursor"], "director_skill": plan["selected_specialist_skill"], "renderer_class": plan["renderer_class"], "style_profile_ref": plan["style_profile_ref"], "canvas": {"width": 1600, "height": 900}, "components": [], "connections": [], "annotations": [], "labels": [], "visual_states": [], "provenance": {"rule_ids": plan["provenance_rule_ids"]}, "output_targets": [plan["canonical_output_kind"]], "qa_requirements": plan["required_qa"], "specialist_payload": plan["specialist_payload"]} for plan in plans]
    output_registry = _schema_registry()
    _require(all(not output_registry.errors("figure-production-plan", value) for value in plans), "FigureProductionPlan schema validation failed")
    _require(all(not output_registry.errors("scientific-figure-spec", value) for value in specs), "ScientificFigureSpec schema validation failed")
    _require(not output_registry.errors("skill-routing", registry), "Skill registry schema validation failed")
    _require(all(not output_registry.errors("archetype-figure-routing", value) for value in matrix), "Archetype routing schema validation failed")
    _require(not output_registry.errors("checkpoint-4-execution-evidence", execution), "Execution evidence schema validation failed")
    _require(not output_registry.errors("checkpoint-4-qa", qa), "Checkpoint QA schema validation failed")
    return {"plans": plans, "specs": specs, "registry": registry, "matrix": matrix, "execution": execution, "qa": qa}


def write_checkpoint4_artifacts(input_dir: Path, output_dir: Path, *, privacy_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Serialize the renderer-free CP4 artifact set deterministically."""
    inputs = {name: json.loads((input_dir / name).read_text(encoding="utf-8")) for name in CP3_INPUTS}
    outputs = build_checkpoint4_artifacts(inputs, privacy_config=privacy_config)
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "figure-production-plans.json": outputs["plans"],
        "scientific-figure-specs.json": outputs["specs"],
        "archetype-figure-routing.json": outputs["matrix"],
        "checkpoint-4-execution-evidence.json": outputs["execution"],
        "checkpoint-4-qa.json": outputs["qa"],
    }
    for name, value in files.items():
        (output_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return outputs
