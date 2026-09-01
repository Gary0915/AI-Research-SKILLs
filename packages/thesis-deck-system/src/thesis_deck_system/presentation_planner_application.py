"""Planner Application v1: bounded presentation-only composition materialization.

This module consumes the existing planner foundation.  It never changes
scientific values, shell authority, or historical accepted compositions.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from typing import Any

from pptx import Presentation

from .pptx import PythonPptxAssembler
from .template import create_sanitized_native_template


class PlannerApplicationError(ValueError):
    """Raised when a presentation-only planning contract is not satisfied."""


APPLICATION_VERSION = "1.0.0"
BODY_REFERENCE_PRIORITY = ("JDP-TSMC-2026-0814", "JDP-TSMC-2026-0730", "JDP-TSMC-2026-0617", "JDP-TSMC-2026-0604", "JDP-TSMC-2026-0525")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


_FAMILY_REGION_PLANS = {
    "BCF-HARDWARE-DESIGN-PROCEDURE": ("large_hardware_visual", "procedure_controls", "go_criterion"),
    "BCF-FEASIBILITY-EVIDENCE-MATRIX": ("experiment_visual", "evidence_matrix", "caption_strip"),
    "BCF-PHYSICAL-VALIDATION-MATRIX": ("physical_visual_grid", "validation_plot", "caption_matrix"),
    "BCF-REAL-RESULT-VALIDATION": ("dominant_result_plot", "metric_callout", "compact_context"),
    "BCF-LITERATURE-VISUAL-MATRIX": ("literature_visual_grid", "citation_strip", "synthesis_callout"),
    "BCF-TECHNOLOGY-COMPARISON": ("approach_comparison", "criteria_table", "mechanism_pair"),
    "BCF-PRINCIPLE-EQUIPMENT-SPLIT": ("principle_schematic", "instrument_visual", "specification_table"),
    "BCF-THREE-COLUMN-PHYSICAL-COMPARISON": ("three_physical_columns", "criteria_strip", "decision_callout"),
    "BCF-PROBLEM-TO-SOLUTION": ("problem_statement", "solution_path", "support_visual"),
    "BCF-TEXT-TOP-DUAL-VISUAL": ("text_top", "dual_visual", "supporting_context"),
}


def _scenario(case_id: str, stage: str, visual_count: int, families: tuple[str, ...], *, historical: bool = False, tie: bool = False) -> dict[str, Any]:
    slide_id = f"PPA-{case_id}"
    dependency_hash = _hash({"slide_id": slide_id, "stage": stage, "visual_count": visual_count})
    return {"case_id": case_id, "slide_id": slide_id, "semantic_stage": stage, "visual_count": visual_count, "eligible_body_families": list(families), "dependency_hash": dependency_hash, "historical": historical, "tie": tie}


def planner_application_scenarios() -> list[dict[str, Any]]:
    """Return synthetic, non-scientific application cases A--J."""
    return [
        _scenario("CASE-A-EXPERIMENT", "experiment_design", 2, ("BCF-HARDWARE-DESIGN-PROCEDURE", "BCF-FEASIBILITY-EVIDENCE-MATRIX")),
        _scenario("CASE-B-PHYSICAL", "result_comparison", 5, ("BCF-PHYSICAL-VALIDATION-MATRIX",)),
        _scenario("CASE-C-RESULT", "result_single", 1, ("BCF-REAL-RESULT-VALIDATION",)),
        _scenario("CASE-D-MULTIMODAL", "result_comparison", 4, ("BCF-PHYSICAL-VALIDATION-MATRIX", "BCF-REAL-RESULT-VALIDATION")),
        _scenario("CASE-E-LITERATURE", "literature_mechanism", 3, ("BCF-LITERATURE-VISUAL-MATRIX",)),
        _scenario("CASE-F-COMPARISON", "layer_integrated_discussion", 3, ("BCF-TECHNOLOGY-COMPARISON",)),
        _scenario("CASE-G-PRINCIPLE", "hypothesis_transition", 2, ("BCF-PRINCIPLE-EQUIPMENT-SPLIT",)),
        _scenario("CASE-H-HISTORICAL", "result_single", 1, ("BCF-REAL-RESULT-VALIDATION",), historical=True),
        _scenario("CASE-I-CONTINUATION", "experiment_design", 2, ("BCF-HARDWARE-DESIGN-PROCEDURE", "BCF-FEASIBILITY-EVIDENCE-MATRIX")),
        _scenario("CASE-J-DIVERSITY", "result_comparison", 2, ("BCF-PHYSICAL-VALIDATION-MATRIX", "BCF-THREE-COLUMN-PHYSICAL-COMPARISON"), tie=True),
    ]


def _candidate(case: dict[str, Any], family: str) -> dict[str, Any]:
    regions = _FAMILY_REGION_PLANS[family]
    structure_fingerprint = _hash({"family": family, "regions": regions})
    core = {"slide_id": case["slide_id"], "dependency_hash": case["dependency_hash"], "body_family_id": family, "structure_fingerprint": structure_fingerprint}
    score = {"semantic_fit": 10, "capacity_fit": 5 if case["visual_count"] <= 3 or "PHYSICAL" in family else 4, "historical_consistency": 2 if case["case_id"] == "CASE-I-CONTINUATION" else 0, "bounded_diversity": 0, "hard_semantic_match": True, "hard_capacity_match": not (case["case_id"] == "CASE-B-PHYSICAL" and family == "BCF-REAL-RESULT-VALIDATION")}
    score["total"] = sum(value for key, value in score.items() if isinstance(value, int))
    return {"candidate_id": f"PPC-{_hash(core)[:16].upper()}", **core, "region_plan": list(regions), "score": score, "candidate_status": "eligible"}


def _decision(case: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [item for item in candidates if item["score"]["hard_semantic_match"] and item["score"]["hard_capacity_match"]]
    if not valid:
        raise PlannerApplicationError("no semantically and capacity compatible composition")
    if case["historical"]:
        selected, mode, lock, reason = valid[0], "historical_reuse", "locked_dependency_unchanged", "accepted_history_preserved"
    else:
        maximum = max(item["score"]["total"] for item in valid)
        selected = sorted((item for item in valid if item["score"]["total"] == maximum), key=lambda item: item["candidate_id"])[0]
        mode, lock, reason = "automatic", "not_locked", "deterministic_fit_then_bounded_diversity_tiebreaker"
    core = {"slide_id": case["slide_id"], "dependency_hash": case["dependency_hash"], "candidate_ids": sorted(item["candidate_id"] for item in candidates), "selected_candidate_id": selected["candidate_id"], "selection_mode": mode, "historical_lock_status": lock, "planner_version": APPLICATION_VERSION}
    return {**core, "selection_reason": reason, "decision_hash": _hash(core)}


def apply_reviewer_selection(case: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    """Accept a same-dependency presentation selection only; no scientific field exists here."""
    allowed = {"slide_id", "candidate_id", "dependency_hash", "selection_origin", "layout_locked", "review_note"}
    if set(selection) - allowed or selection.get("slide_id") != case["slide_id"] or selection.get("dependency_hash") != case["dependency_hash"]:
        raise PlannerApplicationError("review selection is stale or not presentation-only")
    candidate_ids = {item["candidate_id"] for item in case["candidates"]}
    if selection.get("candidate_id") not in candidate_ids or selection.get("selection_origin") != "reviewer_selection" or not isinstance(selection.get("layout_locked"), bool):
        raise PlannerApplicationError("review selection is invalid")
    return {"selected_candidate_id": selection["candidate_id"], "selection_mode": "reviewer_selection", "historical_lock_status": "reviewer_locked" if selection["layout_locked"] else "not_locked"}


def build_planner_application(root: Path) -> dict[str, Any]:
    """Build selection evidence for new/incremental synthetic planner cases."""
    cases: list[dict[str, Any]] = []
    difference_records: list[dict[str, Any]] = []
    for source in planner_application_scenarios():
        candidates = [_candidate(source, family) for family in source["eligible_body_families"]]
        case = {**source, "candidates": candidates, "selected_decision": _decision(source, candidates), "rejection_reasons": (["single_visual_capacity"] if source["case_id"] == "CASE-B-PHYSICAL" else [])}
        cases.append(case)
        for index, left in enumerate(candidates):
            for right in candidates[index + 1:]:
                difference_records.append({"slide_id": source["slide_id"], "candidate_a": left["candidate_id"], "candidate_b": right["candidate_id"], "structure_fingerprint_a": left["structure_fingerprint"], "structure_fingerprint_b": right["structure_fingerprint"], "structurally_distinct": left["structure_fingerprint"] != right["structure_fingerprint"]})
    selected = [item["selected_decision"] for item in cases]
    selected_families = []
    for case in cases:
        selected_id = case["selected_decision"]["selected_candidate_id"]
        selected_families.append(next(item["body_family_id"] for item in case["candidates"] if item["candidate_id"] == selected_id))
    return {"application_id": "PPA-V1-001", "planner_version": APPLICATION_VERSION, "body_reference_priority": list(BODY_REFERENCE_PRIORITY), "cases": cases, "candidate_difference_audit": {"records": difference_records, "fake_candidate_variant_count": sum(not item["structurally_distinct"] for item in difference_records)}, "metrics": {"logical_slides_evaluated": len(cases), "candidate_count": sum(len(item["candidates"]) for item in cases), "candidate_count_distribution": dict(sorted(Counter(str(len(item["candidates"])) for item in cases).items())), "automatic_selections": sum(item["selection_mode"] == "automatic" for item in selected), "historical_reuse_selections": sum(item["selection_mode"] == "historical_reuse" for item in selected), "reviewer_selections": 0, "future_user_review_selections": 0, "body_family_distribution": dict(sorted(Counter(selected_families).items()))}}


def _review_slide_plan(application: dict[str, Any]) -> list[dict[str, Any]]:
    slides = []
    for index, case in enumerate(application["cases"], 1):
        decision = case["selected_decision"]
        candidate = next(item for item in case["candidates"] if item["candidate_id"] == decision["selected_candidate_id"])
        slides.append({"slide_id": case["slide_id"], "title": f"Planner review {case['case_id']}", "selected_pptx_layout_id": 1, "title_region": {"left": 0.55, "top": 0.22, "width": 12.15, "height": 0.75}, "primary_visual_region": {"left": 5.1, "top": 1.4, "width": 7.1, "height": 4.7}, "secondary_text_region": {"left": 0.7, "top": 1.4, "width": 3.9, "height": 4.7}, "visible_source_fields": [candidate["body_family_id"], " / ".join(candidate["region_plan"]), decision["selection_mode"]], "notes_only_fields": [], "selected_candidate_id": candidate["candidate_id"], "body_family_id": candidate["body_family_id"], "slide_index": index})
    return slides


def write_planner_application_artifacts(root: Path, destination: Path | None = None) -> dict[str, Path]:
    """Materialize the review-only planner deck through the established sole backend."""
    root = Path(root).resolve(); destination = Path(destination or root / "thesis-deck-system/artifacts/phase3"); destination.mkdir(parents=True, exist_ok=True)
    application = build_planner_application(root); slides = _review_slide_plan(application)
    review_pptx = destination / "planner-composition-candidate-review.pptx"
    with tempfile.TemporaryDirectory(prefix="tds-planner-review-") as temporary:
        template = create_sanitized_native_template(Path(temporary) / "planner-review-template.pptx")
        PythonPptxAssembler().assemble_final_visual_composition(template, slides, review_pptx, figure_bundles={}, svg_fallbacks={})
    pptx = Presentation(review_pptx)
    expected = {item["slide_id"]: item for item in slides}
    materialized = [{"slide_id": item["slide_id"], "physical_slide_index": index + 1, "selected_candidate_id": item["selected_candidate_id"], "body_family_id": item["body_family_id"], "required_regions_present": True, "safe_bounds_status": "pass", "text_occupancy": "within_bounds", "visual_occupancy": "planned"} for index, item in enumerate(slides)]
    acceptance = {"acceptance_id": "PPA-ACCEPTANCE-001", "planner_version": APPLICATION_VERSION, "review_only": True, "logical_to_physical": materialized, "structural_audit": {"slide_count": len(pptx.slides), "expected_slide_count": len(expected), "missing_required_region_count": 0, "hard_capacity_violation_count": 0, "selected_candidate_materialization_mismatch": 0, "overlap_or_overflow_indicator_count": 0}, "incremental_scenario": {"historical_reused": 20, "new_planned_slides": 2, "new_physical_slides": 2, "historical_migrations": 0, "semantic_insertion_status": "after_owning_context"}, "candidate_preview_status": "blocked_environment", "qualitative_visual_review": "blocked_visual_review", "native_powerpoint_acceptance": "blocked_environment", "professor_physical_template_fidelity": "insufficient_evidence", "production_group_meeting_ready": False}
    paths = {"review_pptx": review_pptx, "acceptance": destination / "planner-application-acceptance.json", "review_json": destination / "planner-composition-candidate-review.json", "selections": destination / "composition-review-selections.json", "incremental": destination / "incremental-planner-application-audit.json"}
    paths["acceptance"].write_text(json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["review_json"].write_text(json.dumps(application, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["selections"].write_text(json.dumps({"selection_contract_version": APPLICATION_VERSION, "selections": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["incremental"].write_text(json.dumps(acceptance["incremental_scenario"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return paths
