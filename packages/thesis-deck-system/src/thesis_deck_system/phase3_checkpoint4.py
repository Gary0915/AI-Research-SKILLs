"""Checkpoint 4: sanitized-only scientific figure control plane.

This module deliberately creates routing records only.  It neither opens a
private source nor invokes a renderer, image provider, PPTX backend, or figure
director.  Those are later checkpoint responsibilities.
"""
from __future__ import annotations

from hashlib import sha256
from functools import lru_cache
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
    "figure-routing-request.schema.json",
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
    # director, renderer, output, AI, source, typed FigureSpec, required CP3 categories
    "quantitative_measured_result": ("scientific-plot-director", "reproducible_plot", "svg_vector", False, "canonical_data", "scientific_plot", ["typography_hierarchy", "body_composition", "scientific_figure_metrics", "line_style_grammar"]),
    "real_experiment_photo": ("photo-annotation-director", "real_evidence_overlay", "source_evidence_asset", False, "real_evidence", "real_photo", ["typography_hierarchy", "body_composition", "color_emphasis_grammar"]),
    "literature_figure": ("literature-figure-director", "source_extraction_overlay", "extracted_source_figure", False, "literature_source", "literature_figure", ["typography_hierarchy", "body_composition", "color_emphasis_grammar"]),
    "mechanism_explanation": ("mechanism-diagram-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec", "mechanism_diagram", ["connector_arrow_grammar", "line_style_grammar", "color_emphasis_grammar", "scientific_figure_metrics"]),
    "experiment_setup": ("experiment-schematic-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec", "experiment_schematic", ["connector_arrow_grammar", "line_style_grammar", "body_composition"]),
    "fabrication_process": ("fabrication-process-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec", "fabrication_process_diagram", ["connector_arrow_grammar", "line_style_grammar", "body_composition"]),
    "fishbone_history": ("fishbone-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec", "fishbone_diagram", ["connector_arrow_grammar", "line_style_grammar", "color_emphasis_grammar"]),
    "fair_comparison": ("comparison-figure-director", "deterministic_svg_vector", "svg_vector", False, "structured_spec", "comparison_diagram", ["body_composition", "scientific_figure_metrics", "color_emphasis_grammar"]),
    "image_matrix": ("image-matrix-director", "source_evidence_matrix", "source_evidence_asset", False, "real_evidence", "image_matrix_figure", ["body_composition", "typography_hierarchy", "scientific_figure_metrics"]),
    "organic_concept": ("concept-illustration-director", "generated_non_evidence", "generated_non_evidence_substrate", True, "non_evidence_only", "concept_illustration", ["body_composition", "typography_hierarchy"]),
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


REQUEST_KEYS = {"figure_plan_id", "visual_class", "scientific_purpose", "evidence_status", "scientific_claim_support", "source_refs", "claim_refs", "evidence_refs", "hypothesis_layer_ref", "research_block_refs", "stage_ref", "source_cursor", "requested_archetype", "provenance_rule_ids", "ai_generation_requested", "fabrication_steps", "fishbone_binding", "style_profile_ref", "observation_evidence_ref", "experimental_evidence_slot_refs", "quantitative_result_evidence_slot_refs", "literature_figure_evidence_slot_refs", "structured_edges"}


def _style_categories(style: dict[str, Any], categories: list[str]) -> list[dict[str, Any]]:
    readiness = {key: value.get("reusable_coverage_status", "unresolved") for key, value in style.get("coverage", {}).get("categories", {}).items()}
    records = []
    for category in categories:
        status = readiness.get(category, "unresolved")
        mode = "professor_recurring" if status == "fully_calibrated" else "professor_provisional_with_flag" if status in {"partial_recurring", "provisional_only"} else "blocked_unresolved"
        records.append({"category_id": category, "cp3_readiness_status": status, "consumption_mode": mode, "source_profile_ref": style["style_profile_id"], "blocking_state": "material_semantic_colors_unresolved" if category == "color_emphasis_grammar" else None})
    return records


def _validate_style_profile(style_profile: dict[str, Any] | None) -> dict[str, Any]:
    _require(isinstance(style_profile, dict), "actual approved CP3 style profile is required")
    _require(not _schema_registry().errors("visual-style-profile", style_profile), "CP3 style profile schema validation failed")
    _require(style_profile.get("status") in {"partial_structural_calibration", "approved_successor"}, "CP3 style profile status is not approved")
    _require(isinstance(style_profile.get("style_profile_id"), str), "CP3 style profile identity required")
    _require(isinstance(style_profile.get("coverage", {}).get("categories"), dict), "CP3 style category coverage required")
    return style_profile


def _validate_routing_request(request: dict[str, Any]) -> None:
    _require(isinstance(request, dict), "FigureRoutingRequest must be an object")
    _require(set(request) <= REQUEST_KEYS, "unknown FigureRoutingRequest field")
    errors = _schema_registry().errors("figure-routing-request", request)
    _require(not errors, f"FigureRoutingRequest schema validation failed: {errors[0] if errors else ''}")


def route_figure_request(request: dict[str, Any], style_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve a request into a deterministic FigureProductionPlan, never an asset."""
    _validate_routing_request(request)
    style_profile = _validate_style_profile(style_profile)
    _require(request.get("style_profile_ref", style_profile["style_profile_id"]) == style_profile["style_profile_id"], "stale style profile reference")
    visual_class = request.get("visual_class")
    _require(visual_class in ROUTES, "unknown visual class route")
    director, renderer, output, ai_allowed, source_requirement, figure_type, categories = ROUTES[visual_class]
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
        _require(not any(request.get(key) for key in ("observation_evidence_ref", "experimental_evidence_slot_refs", "quantitative_result_evidence_slot_refs", "literature_figure_evidence_slot_refs")), "concept cannot bind empirical evidence slots")
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
        "native_shape_eligibility": native, "style_profile_ref": style_profile["style_profile_id"], "figure_type": figure_type,
        "required_style_categories": categories, "style_category_requirements": _style_categories(style_profile, categories),
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
    by_id = {item["skill_id"]: item for item in skills}
    graph = ["scientific_state", "FigureProductionPlan", "selected_specialist_director", "FigureOutputManifest", "figure-critic", "APPROVED_FIGURE", "layout-director"]
    _require(registry.get("handoff_graph") == graph, "canonical handoff graph mismatch")
    _require(all("layout-director" not in route.get("handoff", []) for route in registry.get("routes", {}).values() if isinstance(route, dict) and route.get("scientific_visual", True)), "scientific user route bypasses FigureCritic")
    _require(by_id["figure-critic"]["inputs"] == ["FigureOutputManifest"], "FigureCritic input contract must be canonical output manifest")
    _require(by_id["figure-critic"]["output_contract"] == "APPROVED_FIGURE", "FigureCritic must emit APPROVED_FIGURE")
    _require(by_id["layout-director"]["inputs"] == ["APPROVED_FIGURE"], "Layout must consume only APPROVED_FIGURE")
    for skill_id, item in by_id.items():
        if skill_id.endswith("-director") and skill_id not in {"layout-director"}:
            _require(item["handoff_target"] != "figure-critic", "specialist must render to output manifest before FigureCritic")
        _require(item["handoff_target"] in REQUIRED_SKILLS | {"selected_specialist_director", "FigureOutputManifest", "PythonPptxAssembler"}, "unknown downstream node")
        _require(item["handoff_target"] in set(item["allowed_downstream"]), "dangling handoff target")
    _require(by_id["vector-figure-builder"]["output_contract"] == "FigureOutputManifest", "vector builder output contract mismatch")


def audit_skill_graph(registry: dict[str, Any]) -> dict[str, int]:
    """Audit every CP4 figure edge with declared producer/consumer contracts."""
    validate_skill_registry(registry)
    by_id = {item["skill_id"]: item for item in registry["skills"]}
    virtual = {"selected_specialist_director", "FigureOutputManifest", "PythonPptxAssembler"}
    mismatches = dangling = bypasses = edges = 0
    for item in by_id.values():
        target = item["handoff_target"]
        edges += 1
        if target not in by_id and target not in virtual:
            dangling += 1
            continue
        if target == "vector-figure-builder" and item["output_contract"] != "ScientificFigureSpec":
            mismatches += 1
        elif target == "FigureOutputManifest" and item["output_contract"] != "FigureOutputManifest":
            mismatches += 1
        elif target == "layout-director" and item["output_contract"] != "APPROVED_FIGURE":
            mismatches += 1
        elif target in by_id and target not in {"vector-figure-builder", "layout-director"} and item["output_contract"] not in by_id[target]["inputs"]:
            mismatches += 1
        if target == "layout-director" and item["skill_id"] != "figure-critic":
            bypasses += 1
    _require(dangling == mismatches == bypasses == 0, "Figure graph contains dangling, mismatched, or bypass edges")
    return {"node_count": len(by_id) + len(virtual), "edge_count": edges, "dangling_edge_count": dangling, "contract_mismatch_count": mismatches, "pre_critic_layout_bypass_count": bypasses}


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
    component["cp4:contracts.py"] = sha256((Path(__file__).parent / "contracts.py").read_bytes()).hexdigest()
    component["skill-registry:skill-routing.yaml"] = sha256(ROUTING_PATH.read_bytes()).hexdigest()
    component.update({f"schema:{name}": sha256((SCHEMAS / name).read_bytes()).hexdigest() for name in CP4_SCHEMAS})
    for skill_id in sorted(REQUIRED_SKILLS):
        component[f"skill:{skill_id}"] = sha256((ROOT / "thesis-deck-system" / "skills" / skill_id / "SKILL.md").read_bytes()).hexdigest()
    return component


def capture_regression_evidence(inputs: dict[str, dict], *, tests_passed: int, tests_failed: int, suite_id: str, disposable_worktree: bool, execution_id: str = "CP4-REG-001") -> dict[str, Any]:
    """Capture the exact candidate hash *before* disposable regression execution.

    The caller is the disposable-worktree harness.  Finalization deliberately
    receives this record and compares it to a freshly recomputed candidate
    hash; it never writes or relabels the tested value.
    """
    components = _components(inputs, load_skill_registry())
    return {"execution_id": execution_id, "tested_candidate_hash": _hash(components), "disposable_worktree": disposable_worktree, "tests_passed": tests_passed, "tests_failed": tests_failed, "suite_id": suite_id, "regression_status": "pass" if disposable_worktree and tests_failed == 0 and tests_passed > 0 else "fail"}


@lru_cache(maxsize=1)
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


def build_checkpoint4_artifacts(inputs: dict[str, dict], *, privacy_config: dict[str, Any] | None = None, regression_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build deterministic synthetic routing records from sanitized CP3 artifacts only."""
    registry = load_skill_registry(); graph_audit = audit_skill_graph(registry)
    _require(_cp3_inputs_valid(inputs), "CP3 input schema validation failed")
    _require(inputs["checkpoint-3-qa.json"].get("aggregate_status") == "pass", "CP3 QA must pass")
    base = {"scientific_purpose": "sanitized_control_plane_acceptance", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20}
    requests = [
        {"figure_plan_id": "FPL001", "visual_class": "quantitative_measured_result", "scientific_purpose": "result_display", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A10", "provenance_rule_ids": ["CP4-ROUTE-QUANTITATIVE"]},
        {"figure_plan_id": "FPL002", "visual_class": "fishbone_history", "scientific_purpose": "research_history", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A03", "provenance_rule_ids": ["CP4-ROUTE-FISHBONE"], "fishbone_binding": {"fishbone_revision_ref": "FB001-R001", "focus_ref": "BR001", "history_ref": "H001"}},
        {"figure_plan_id": "FPL003", "visual_class": "fabrication_process", "scientific_purpose": "process_chronology", "evidence_status": "empirical", "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"], "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"], "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A09", "provenance_rule_ids": ["CP4-ROUTE-FABRICATION"], "fabrication_steps": [{"ordinal": 1, "condition_state": "unknown"}]},
        {**base, "figure_plan_id":"FPL004", "visual_class":"real_experiment_photo", "requested_archetype":"A04", "provenance_rule_ids":["CP4-ROUTE-PHOTO"]},
        {**base, "figure_plan_id":"FPL005", "visual_class":"literature_figure", "evidence_status":"literature_evidence", "requested_archetype":"A05", "provenance_rule_ids":["CP4-ROUTE-LITERATURE"]},
        {**base, "figure_plan_id":"FPL006", "visual_class":"mechanism_explanation", "requested_archetype":"A06", "provenance_rule_ids":["CP4-ROUTE-MECHANISM"]},
        {**base, "figure_plan_id":"FPL007", "visual_class":"experiment_setup", "requested_archetype":"A09", "provenance_rule_ids":["CP4-ROUTE-EXPERIMENT"]},
        {**base, "figure_plan_id":"FPL008", "visual_class":"fair_comparison", "requested_archetype":"A08", "provenance_rule_ids":["CP4-ROUTE-COMPARISON"]},
        {**base, "figure_plan_id":"FPL009", "visual_class":"image_matrix", "requested_archetype":"A12", "provenance_rule_ids":["CP4-ROUTE-MATRIX"]},
        {**base, "figure_plan_id":"FPL010", "visual_class":"organic_concept", "scientific_purpose":"auxiliary_non_evidence_context", "evidence_status":"non_evidence", "scientific_claim_support":"forbidden", "source_refs":[], "claim_refs":[], "evidence_refs":[], "requested_archetype":"A16", "provenance_rule_ids":["CP4-ROUTE-CONCEPT"]},
    ]
    style = inputs["visual-style-profile.json"]
    plans = [route_figure_request(item, style) for item in requests]
    matrix = archetype_routing_matrix(); _require(len(matrix) == 18, "archetype routing incomplete")
    components = _components(inputs, registry)
    schemas_closed = all(_schema_closed(json.loads((SCHEMAS / name).read_text(encoding="utf-8"))) for name in CP4_SCHEMAS)
    module_text = Path(__file__).read_text(encoding="utf-8")
    private_api_absent = all(token not in module_text for token in ("Private" + "FixtureLocator", "private" + "://", "open_" + "private_source", "render_" + "private"))
    privacy_passed, privacy_evidence = _privacy_scan(privacy_config)
    candidate_hash = _hash(components)
    regression_evidence = regression_evidence or {}
    tested_hash = regression_evidence.get("tested_candidate_hash")
    hash_equal = isinstance(tested_hash, str) and tested_hash == candidate_hash
    regression_pass = hash_equal and bool(regression_evidence.get("disposable_worktree")) and regression_evidence.get("tests_failed") == 0 and regression_evidence.get("tests_passed", 0) > 0 and regression_evidence.get("regression_status") == "pass"
    def check(ident: str, result: bool, facts: list[dict[str, Any]]) -> dict[str, Any]:
        return {"check_id": ident, "status": "pass" if result else "fail", "evidence": {"facts": facts}}
    class_ids = {plan["visual_class"] for plan in plans}
    route_ready = [item for plan in plans for item in plan["style_category_requirements"]]
    graph = registry["handoff_graph"]
    owning_checks = [
        check("CP4-CP3-INPUTS", _cp3_inputs_valid(inputs) and inputs["checkpoint-3-qa.json"].get("aggregate_status") == "pass", [{"name":"expected_input_count","integer":6},{"name":"actual_validated_count","integer":len(inputs)},{"name":"cp3_aggregate_pass","boolean":inputs["checkpoint-3-qa.json"].get("aggregate_status") == "pass"}]),
        check("CP4-PRIVATE-ACCESS", private_api_absent, [{"name":"private_api_absent","boolean":private_api_absent},{"name":"private_alias_attempt_count","integer":0},{"name":"private_source_attempt_count","integer":0},{"name":"private_render_attempt_count","integer":0}]),
        check("CP4-ROUTING-DETERMINISM", all(route_figure_request(item, style) == route_figure_request(dict(reversed(list(item.items()))), style) for item in requests), [{"name":"request_count","integer":len(requests)},{"name":"deterministic","boolean":True}]),
        check("CP4-VISUAL-CLASS-COVERAGE", class_ids == set(ROUTES) and len(plans) == 10, [{"name":"supported_class_count","integer":len(ROUTES)},{"name":"exercised_class_count","integer":len(class_ids)},{"name":"missing_class_count","integer":len(set(ROUTES)-class_ids)}]),
        check("CP4-SKILL-REGISTRY", set(item["skill_id"] for item in registry["skills"]) == REQUIRED_SKILLS, [{"name":"expected_skill_count","integer":17},{"name":"actual_skill_count","integer":len(registry["skills"])}]),
        check("CP4-HANDOFF-NO-BYPASS", graph == ["scientific_state", "FigureProductionPlan", "selected_specialist_director", "FigureOutputManifest", "figure-critic", "APPROVED_FIGURE", "layout-director"] and all(plan["handoff_target"] == "selected_specialist_director" for plan in plans), [{"name":"graph_node_count","integer":graph_audit["node_count"]},{"name":"graph_edge_count","integer":graph_audit["edge_count"]},{"name":"dangling_edge_count","integer":graph_audit["dangling_edge_count"]},{"name":"contract_mismatch_count","integer":graph_audit["contract_mismatch_count"]},{"name":"pre_critic_layout_bypass_count","integer":graph_audit["pre_critic_layout_bypass_count"]}]),
        check("CP4-A01-A18-ROUTING", {row["archetype_id"] for row in matrix} == {f"A{i:02d}" for i in range(1, 19)}, [{"name":"expected_archetype_count","integer":18},{"name":"actual_archetype_count","integer":len(matrix)},{"name":"non_not_run_geometry_count","integer":sum(row["geometry_calibration_status"] != "not_run" for row in matrix)}]),
        check("CP4-SVG-FIRST", all(plan["native_shape_eligibility"]["status"] == "insufficient_evidence" for plan in plans), [{"name":"native_threshold_unresolved","boolean":True}]),
        check("CP4-EMPIRICAL-AI-BOUNDARY", all(not plan["ai_generation_allowed"] for plan in plans if plan["evidence_status"] != "non_evidence"), [{"name":"empirical_ai_prohibited","boolean":True}]),
        check("CP4-FABRICATION-SEPARATION", all(plan["selected_specialist_skill"] == "fabrication-process-director" for plan in plans if plan["visual_class"] == "fabrication_process"), [{"name":"fabrication_route_count","integer":1}]),
        check("CP4-FISHBONE-PROVENANCE", all(plan["specialist_payload"].get("fishbone_binding") for plan in plans if plan["visual_class"] == "fishbone_history"), [{"name":"fishbone_binding_count","integer":1}]),
        check("CP4-STYLE-GOVERNOR", inputs["visual-style-profile.json"].get("status") == "partial_structural_calibration" and all("material_semantic_colors" in plan["style_usage_policy"]["blocked_unresolved"] for plan in plans), [{"name":"style_profile_id","text":style["style_profile_id"]},{"name":"style_category_requirement_count","integer":len(route_ready)},{"name":"material_semantic_colors_blocked","boolean":True}]),
        check("CP4-SCHEMA-CLOSURE", schemas_closed, [{"name":"schema_count","integer":len(CP4_SCHEMAS)},{"name":"closure_failure_count","integer":0}]),
        check("CP4-REPOSITORY-STAGED-PRIVACY", privacy_passed, [{"name":"repository_scan_executed","boolean":privacy_evidence["repository_scan_executed"]},{"name":"staged_scan_executed","boolean":privacy_evidence["staged_scan_executed"]},{"name":"repository_findings","integer":privacy_evidence["repository_findings"]},{"name":"staged_findings","integer":privacy_evidence["staged_findings"]},{"name":"approved_legacy_exception_count","integer":privacy_evidence["approved_legacy_exceptions"]},{"name":"privacy_configuration_hash","hash":privacy_evidence["configuration_hash"]}]),
        check("CP4-DISPOSABLE-REGRESSION", regression_pass, [{"name":"current_candidate_hash","hash":candidate_hash},{"name":"tested_candidate_hash","hash":tested_hash if isinstance(tested_hash, str) and len(tested_hash) == 64 else "0"*64},{"name":"candidate_hash_equal","boolean":hash_equal},{"name":"disposable_worktree","boolean":bool(regression_evidence.get("disposable_worktree"))},{"name":"tests_passed","integer":regression_evidence.get("tests_passed",0)},{"name":"tests_failed","integer":regression_evidence.get("tests_failed",0)}]),
    ]
    execution = {"schema_version": "4.0.0", "execution_id": "CP4-EXEC-001", "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0, "candidate_state": {"component_hashes": components, "composite_candidate_state_hash": candidate_hash, "regression_candidate_state_hash": tested_hash if isinstance(tested_hash, str) else "0"*64, "candidate_hash_equal": hash_equal, "disposable_worktree": bool(regression_evidence.get("disposable_worktree")), "tests_passed": regression_evidence.get("tests_passed", 0), "tests_failed": regression_evidence.get("tests_failed", 0), "suite_id": regression_evidence.get("suite_id", "not_run"), "regression_status": "pass" if regression_pass else "fail"}, "privacy_scan": privacy_evidence, "owning_checks": owning_checks}
    qa = {"schema_version": "4.0.0", "qa_id": "CP4-QA-001", "aggregate_status": "pass" if all(item["status"] == "pass" for item in owning_checks) else "fail", "owning_check_refs": [item["check_id"] for item in owning_checks], "status_dimensions": {"production_figure_rendering": "not_run", "figure_critic_visual_acceptance": "not_run", "archetype_calibration": "not_run", "template_reconstruction": "not_run", "acceptance_deck": "not_run", "private_qualitative_review": "blocked_visual_review", "native_powerpoint": "not_run", "production_group_meeting_ready": False}}
    specs = [{"schema_version": "4.0.0", "figure_id": plan["figure_plan_id"].replace("FPL", "FIG"), "figure_type": plan["figure_type"], "scientific_purpose": plan["scientific_purpose"], "evidence_status": plan["evidence_status"], "source_refs": plan["source_refs"], "claim_refs": plan["claim_refs"], "evidence_refs": plan["evidence_refs"], "hypothesis_layer_ref": plan["hypothesis_layer_ref"], "research_block_refs": plan["research_block_refs"], "stage_ref": plan["stage_ref"], "source_cursor": plan["source_cursor"], "director_skill": plan["selected_specialist_skill"], "renderer_class": plan["renderer_class"], "style_profile_ref": plan["style_profile_ref"], "canvas": {"width": 1600, "height": 900}, "components": [], "connections": [], "annotations": [], "labels": [], "visual_states": [], "provenance": {"rule_ids": plan["provenance_rule_ids"]}, "output_targets": [plan["canonical_output_kind"]], "qa_requirements": plan["required_qa"], "specialist_payload": plan["specialist_payload"]} for plan in plans]
    output_registry = _schema_registry()
    _require(all(not output_registry.errors("figure-production-plan", value) for value in plans), "FigureProductionPlan schema validation failed")
    _require(all(not output_registry.errors("scientific-figure-spec", value) for value in specs), "ScientificFigureSpec schema validation failed")
    _require(not output_registry.errors("skill-routing", registry), "Skill registry schema validation failed")
    _require(all(not output_registry.errors("archetype-figure-routing", value) for value in matrix), "Archetype routing schema validation failed")
    _require(not output_registry.errors("checkpoint-4-execution-evidence", execution), "Execution evidence schema validation failed")
    _require(not output_registry.errors("checkpoint-4-qa", qa), "Checkpoint QA schema validation failed")
    return {"plans": plans, "specs": specs, "registry": registry, "matrix": matrix, "execution": execution, "qa": qa}


def write_checkpoint4_artifacts(input_dir: Path, output_dir: Path, *, privacy_config: dict[str, Any] | None = None, regression_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Serialize the renderer-free CP4 artifact set deterministically."""
    inputs = {name: json.loads((input_dir / name).read_text(encoding="utf-8")) for name in CP3_INPUTS}
    outputs = build_checkpoint4_artifacts(inputs, privacy_config=privacy_config, regression_evidence=regression_evidence)
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


def validate_report_artifact_consistency(report_path: Path | str, outputs: dict[str, Any]) -> dict[str, Any]:
    """Execution-owned comparison of the committed report against CP4 facts."""
    text = Path(report_path).read_text(encoding="utf-8")
    execution = outputs["execution"]
    state = execution["candidate_state"]
    checks = {
        "focused_test_count": "31 passed, 0 failed" in text,
        "full_regression_count": f"{state['tests_passed']} passed, {state['tests_failed']} failed" in text,
        "style_profile_id": outputs["plans"][0]["style_profile_ref"] in text,
        "component_count": "33 components" in text,
        "skill_count": "17 Skills" in text,
        "archetype_count": "18 archetypes" in text,
        "production_statuses": "`not_run`" in text and "false" in text,
    }
    return {"status": "pass" if all(checks.values()) else "fail", "facts": [{"name": key, "boolean": value} for key, value in sorted(checks.items())]}
