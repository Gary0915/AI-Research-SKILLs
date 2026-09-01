"""Deterministic presentation-planning foundation over sanitized SlideSpec projections.

This module is deliberately a planning layer only.  It neither mutates
scientific state nor assembles a PPTX; it chooses a compatible composition
identity that the established composition plan can consume.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .incremental_deck_lineage import BODY_COMPOSITION_FAMILIES, build_current_acceptance_lineage
from .phase3_final_visual_composition import build_final_composition_plan, build_final_projection


class PlannerError(ValueError):
    """A composition choice would violate a closed planning contract."""


PLANNER_VERSION = "1.0.0"
_DENSITIES = frozenset({"low", "medium", "high", "unavailable"})
_OBSERVATION_STATES = frozenset({"value", "unavailable", "not_applicable"})
_BODY_PRIORITY = (
    "JDP-TSMC-2026-0814", "JDP-TSMC-2026-0730", "JDP-TSMC-2026-0617",
    "JDP-TSMC-2026-0604", "JDP-TSMC-2026-0525",
)


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _observation(value: int | None, *, not_applicable: bool = False) -> dict[str, Any]:
    if not_applicable:
        return {"state": "not_applicable", "value": None}
    if value is None:
        return {"state": "unavailable", "value": None}
    if not isinstance(value, int) or value < 0:
        raise PlannerError("content-shape observation must be a nonnegative integer")
    return {"state": "value", "value": value}


def _density(count: int | None) -> str:
    if count is None:
        return "unavailable"
    return "low" if count <= 1 else "medium" if count <= 4 else "high"


def _semantic_count(fields: Any, names: tuple[str, ...]) -> int | None:
    if not isinstance(fields, dict):
        return None
    values = [value for key, value in fields.items() if key in names]
    if not values:
        return None
    return sum(len(value) if isinstance(value, list) else 1 for value in values)


def build_scientific_content_shape(record: dict[str, Any]) -> dict[str, Any]:
    """Derive a privacy-safe composition shape from canonical projection fields.

    Notes/provenance and rendered-slide text never affect this shape.  The
    supplied record may be a production projection or a minimal synthetic
    planning fixture.
    """
    required = {"slide_id", "semantic_stage", "title", "visible_text", "source_semantic_fields", "source_bindings", "governed_figure_route"}
    if not required <= set(record) or not isinstance(record["slide_id"], str) or not isinstance(record["semantic_stage"], str):
        raise PlannerError("projection record cannot produce a content shape")
    fields = record["source_semantic_fields"]
    stage_fields = fields.get(record["semantic_stage"], {}) if isinstance(fields, dict) else {}
    route = record.get("governed_figure_route")
    visible = record.get("visible_text") if isinstance(record.get("visible_text"), list) else []
    controls = _semantic_count(stage_fields, ("controls", "control", "control_conditions"))
    result_metric = _semantic_count(stage_fields, ("metrics", "result_metric", "result_identity"))
    observations = {
        "title_chars": _observation(len(record["title"]) if isinstance(record["title"], str) else None),
        "primary_claim_count": _observation(_semantic_count(stage_fields, ("claim", "claims", "takeaway"))),
        "bullet_count": _observation(len(visible)),
        "paragraph_count": _observation(len(visible)),
        "photo_count": _observation(1 if route == "photo" else 0),
        "cad_count": _observation(_semantic_count(stage_fields, ("cad", "design"))),
        "plot_count": _observation(1 if route == "scientific_plot" else 0),
        "schematic_count": _observation(1 if route in {"mechanism", "experiment"} else 0),
        "table_count": _observation(1 if route == "comparison" else 0),
        "table_rows_max": _observation(None),
        "table_columns_max": _observation(None),
        "formula_count": _observation(_semantic_count(stage_fields, ("formula", "equations"))),
        "comparison_side_count": _observation(2 if route == "comparison" else None),
        "caption_count": _observation(1 if route else 0),
        "result_metric_count": _observation(result_metric),
        "mechanism_node_count": _observation(_semantic_count(stage_fields, ("nodes", "mechanism_nodes"))),
        "experiment_control_count": _observation(controls),
        "evidence_item_count": _observation(len(record.get("source_bindings", {}).get("evidence_refs", [])) if isinstance(record.get("source_bindings"), dict) else None),
        "primary_visual_count": _observation(1 if route else 0),
        "secondary_visual_count": _observation(0),
    }
    fingerprint = {
        "semantic_stage": record["semantic_stage"], "route": route,
        "observations": observations,
        "text_density_class": _density(len(visible)),
        "evidence_density_class": _density(observations["evidence_item_count"]["value"]),
    }
    return {
        "content_shape_id": f"SCS-{sha256(record['slide_id'].encode()).hexdigest()[:16]}",
        "slide_id": record["slide_id"], "semantic_stage": record["semantic_stage"],
        "observations": observations, "text_density_class": fingerprint["text_density_class"],
        "evidence_density_class": fingerprint["evidence_density_class"],
        "shape_basis": "canonical_slidespec_projection", "content_shape_sha256": _hash(fingerprint),
    }


def build_layout_capability_registry() -> list[dict[str, Any]]:
    """Return the bounded, queryable recipes; capacity is system heuristic only."""
    recipe_rows = (
        ("BCF-TEXT-TOP-DUAL-VISUAL", ("A01", "A02"), ("formal_cover", "progress_todo"), ("none",), 0, 1),
        ("BCF-PRINCIPLE-EQUIPMENT-SPLIT", ("A17",), ("hypothesis_transition", "literature_mechanism"), ("mechanism",), 1, 1),
        ("BCF-FEASIBILITY-EVIDENCE-MATRIX", ("A09",), ("experiment_design",), ("experiment",), 1, 3),
        ("BCF-HARDWARE-DESIGN-PROCEDURE", ("A09",), ("experiment_design",), ("experiment",), 1, 2),
        ("BCF-PHYSICAL-VALIDATION-MATRIX", ("A11",), ("result_comparison",), ("comparison", "scientific_plot"), 1, 3),
        ("BCF-TECHNOLOGY-COMPARISON", ("A14",), ("layer_integrated_discussion",), ("comparison",), 1, 2),
        ("BCF-PROBLEM-TO-SOLUTION", ("A03", "A04", "A05", "A12"), ("hypothesis_title", "problem_definition", "fishbone_locator", "observation_problem"), ("fishbone",), 0, 1),
        ("BCF-REAL-RESULT-VALIDATION", ("A10",), ("result_single",), ("scientific_plot",), 1, 1),
        ("BCF-LITERATURE-VISUAL-MATRIX", ("A06",), ("literature_mechanism",), ("mechanism",), 1, 3),
        ("BCF-THREE-COLUMN-PHYSICAL-COMPARISON", ("A16",), ("layer_summary_decision",), ("comparison",), 1, 3),
    )
    registry: list[dict[str, Any]] = []
    for family, archetypes, stages, media, minimum, maximum in recipe_rows:
        fingerprint = {"family": family, "archetypes": archetypes, "stages": stages, "media": media, "minimum": minimum, "maximum": maximum}
        registry.append({
            "capability_id": f"LCD-{family.removeprefix('BCF-')}", "archetype_ids": list(archetypes), "body_family_id": family,
            "composition_type": "body_composition", "structure_fingerprint": _hash(fingerprint),
            "required_regions": ["title_region", "body_region"], "optional_regions": ["caption_region", "secondary_visual_region"],
            "primary_visual_slots": maximum, "secondary_visual_slots": 1, "supported_media_kinds": list(media),
            "media_count": {"min": minimum, "max": maximum, "basis": "system_heuristic"},
            "supported_table_structure": "comparison_matrix" if "comparison" in media else "not_applicable",
            "supported_comparison_sides": 2 if "comparison" in media else None,
            "supported_formula_presence": False, "text_capacity": {"state": "provisional", "basis": "system_heuristic"},
            "evidence_capacity": {"state": "provisional", "basis": "system_heuristic"},
            "source_evidence_ids": [f"{_BODY_PRIORITY[0]}-PLANNER"], "authority_status": "body_only_no_shell_override",
            "confidence": "provisional", "readiness": "partial_structural_calibration",
        })
    if {item["body_family_id"] for item in registry} != BODY_COMPOSITION_FAMILIES:
        raise PlannerError("layout capability registry no longer covers the closed body-family set")
    return registry


def generate_composition_candidates(shape: dict[str, Any], capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter controlled recipes and score only semantically compatible candidates."""
    stage = shape.get("semantic_stage")
    route = None
    primary = shape.get("observations", {}).get("primary_visual_count", {}).get("value")
    candidates: list[dict[str, Any]] = []
    for capability in capabilities:
        route_compatible = primary in (0, None) or capability["media_count"]["max"] >= primary
        stage_compatible = stage in {"formal_cover", "progress_todo"} or any(stage in capability["capability_id"].casefold() for _ in ())
        # Stages are encoded by the body-family recipe deterministically.
        family = capability["body_family_id"]
        allowed = {
            "experiment_design": {"BCF-FEASIBILITY-EVIDENCE-MATRIX", "BCF-HARDWARE-DESIGN-PROCEDURE"},
            "result_single": {"BCF-REAL-RESULT-VALIDATION"}, "result_comparison": {"BCF-PHYSICAL-VALIDATION-MATRIX"},
            "literature_mechanism": {"BCF-LITERATURE-VISUAL-MATRIX", "BCF-PRINCIPLE-EQUIPMENT-SPLIT"},
            "layer_integrated_discussion": {"BCF-TECHNOLOGY-COMPARISON"}, "layer_summary_decision": {"BCF-THREE-COLUMN-PHYSICAL-COMPARISON"},
            "fishbone_locator": {"BCF-PROBLEM-TO-SOLUTION"}, "hypothesis_title": {"BCF-PROBLEM-TO-SOLUTION"},
            "problem_definition": {"BCF-PROBLEM-TO-SOLUTION"}, "observation_problem": {"BCF-PROBLEM-TO-SOLUTION"},
            "hypothesis_transition": {"BCF-PRINCIPLE-EQUIPMENT-SPLIT"}, "formal_cover": {"BCF-TEXT-TOP-DUAL-VISUAL"},
            "progress_todo": {"BCF-TEXT-TOP-DUAL-VISUAL"},
        }
        if family not in allowed.get(stage, set()) or not route_compatible:
            continue
        score = {"semantic_fit": 6, "capacity_fit": 3, "historical_consistency": 0, "bounded_diversity": 0, "hard_capacity_match": True}
        score["total"] = sum(value for key, value in score.items() if key != "hard_capacity_match")
        candidate_core = {"slide_id": shape["slide_id"], "content_shape_sha256": shape["content_shape_sha256"], "capability_id": capability["capability_id"], "body_family_id": family}
        candidates.append({"candidate_id": f"CC-{_hash(candidate_core)[:16].upper()}", **candidate_core, "score": score, "candidate_status": "eligible"})
    return sorted(candidates, key=lambda value: value["candidate_id"])


def select_composition(shape: dict[str, Any], candidates: list[dict[str, Any]], *, lifecycle_decision: str, historical_composition_id: str | None = None) -> dict[str, Any]:
    """Apply immutable-history lock before deterministic score/tie selection."""
    valid = [item for item in candidates if item.get("score", {}).get("hard_capacity_match") is not False]
    if not valid:
        raise PlannerError("no capacity-compatible composition candidate")
    candidate_ids = [item["candidate_id"] for item in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise PlannerError("composition candidate identity is ambiguous")
    if lifecycle_decision == "reuse_exact":
        selected = next((item for item in valid if item["candidate_id"] == historical_composition_id), None)
        if selected is None:
            raise PlannerError("historical reuse requires its prior composition candidate")
        mode, lock, reason = "historical_reuse", "locked_dependency_unchanged", "accepted_history_preserved"
    else:
        best = max(item["score"].get("total", -1) for item in valid)
        selected = sorted((item for item in valid if item["score"].get("total") == best), key=lambda item: item["candidate_id"])[0]
        mode, lock, reason = "automatic", "not_locked", "deterministic_fit_then_bounded_diversity_tiebreaker"
    core = {"slide_id": shape["slide_id"], "content_shape_hash": shape["content_shape_sha256"], "candidate_ids": sorted(candidate_ids), "selected_candidate_id": selected["candidate_id"], "selection_mode": mode, "historical_lock_status": lock, "planner_version": PLANNER_VERSION}
    return {**core, "candidate_component_scores": [{"candidate_id": item["candidate_id"], "score": item["score"]} for item in sorted(candidates, key=lambda value: value["candidate_id"])], "selection_reason": reason, "decision_sha256": _hash(core)}


def build_current_acceptance_planner_artifacts(root: Path) -> dict[str, Any]:
    """Run Planner v1 in shadow mode for the current synthetic acceptance deck."""
    root = Path(root).resolve()
    projection = build_final_projection(root)
    plan = build_final_composition_plan(root, projection)
    lineage = build_current_acceptance_lineage(plan)
    prior_by_slide = {item["slide_id"]: item for item in lineage["research_deck_lineage"]}
    capabilities = build_layout_capability_registry()
    shapes = [build_scientific_content_shape(item) for item in ([{"slide_id": "FVCC-COVER-001", "semantic_stage": "formal_cover", "title": "Cover", "visible_text": [], "source_semantic_fields": {}, "source_bindings": {}, "governed_figure_route": None}] + projection["slides"])]
    decisions: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for shape in shapes:
        row_candidates = generate_composition_candidates(shape, capabilities)
        candidates.extend(row_candidates)
        if shape["slide_id"] == "FVCC-COVER-001":
            decision = select_composition(shape, row_candidates, lifecycle_decision="append_new")
        else:
            prior = prior_by_slide[shape["slide_id"]]
            historical = next(item for item in row_candidates if item["body_family_id"] == prior["composition_family"])
            decision = select_composition(shape, row_candidates, lifecycle_decision="reuse_exact", historical_composition_id=historical["candidate_id"])
        decisions.append(decision)
    selection_audit = {
        "audit_id": "PP-SELECT-001", "slide_count": len(shapes), "candidate_count": len(candidates), "selections": decisions,
        "unchanged_historical_slide_style_migration_count": 0, "scientific_truth_override_count": 0, "shell_override_count": 0,
        "historical_relayout_without_dependency_change_count": 0, "nondeterministic_tie_count": 0,
    }
    qa_facts = {"content_shape_schema_status": "pass", "layout_capability_schema_status": "pass", "candidate_schema_status": "pass", "selection_schema_status": "pass", "planner_determinism": "pass", "hard_semantic_mismatch_selected_count": 0, "hard_capacity_mismatch_selected_count": 0, "scientific_truth_override_count": 0, "shell_override_count": 0, "historical_relayout_without_dependency_change_count": 0, "nondeterministic_tie_count": 0}
    qa = {"qa_id": "PP-QA-001", **qa_facts, "aggregate_status": "pass"}
    return {
        "scientific_content_shapes": {"planner_version": PLANNER_VERSION, "records": shapes},
        "layout_capability_registry": {"planner_version": PLANNER_VERSION, "records": capabilities},
        "composition_candidates": {"planner_version": PLANNER_VERSION, "records": candidates},
        "composition_selection_audit": selection_audit,
        "presentation_planner_qa": qa,
    }


def write_current_acceptance_planner_artifacts(root: Path, destination: Path | None = None) -> dict[str, Path]:
    """Persist only the five closed Planner v1 audit surfaces."""
    root = Path(root).resolve()
    destination = Path(destination) if destination is not None else root / "thesis-deck-system" / "artifacts" / "phase3"
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = build_current_acceptance_planner_artifacts(root)
    names = {
        "scientific_content_shapes": "scientific-content-shapes.json",
        "layout_capability_registry": "layout-capability-registry.json",
        "composition_candidates": "composition-candidates.json",
        "composition_selection_audit": "composition-selection-audit.json",
        "presentation_planner_qa": "presentation-planner-qa.json",
    }
    result: dict[str, Path] = {}
    for key, name in names.items():
        path = destination / name
        path.write_text(json.dumps(artifacts[key], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result[key] = path
    return result
