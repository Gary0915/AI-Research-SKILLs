"""Production application tests for the bounded Planner v1 layer."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]


def test_application_cases_select_semantic_recipes_and_reject_single_visual_for_dense_validation():
    from thesis_deck_system.presentation_planner_application import build_planner_application

    application = build_planner_application(ROOT)
    by_case = {item["case_id"]: item for item in application["cases"]}
    assert "BCF-HARDWARE-DESIGN-PROCEDURE" in by_case["CASE-A-EXPERIMENT"]["eligible_body_families"]
    assert "BCF-PHYSICAL-VALIDATION-MATRIX" in by_case["CASE-B-PHYSICAL"]["eligible_body_families"]
    assert "BCF-REAL-RESULT-VALIDATION" in by_case["CASE-C-RESULT"]["eligible_body_families"]
    assert "BCF-LITERATURE-VISUAL-MATRIX" in by_case["CASE-E-LITERATURE"]["eligible_body_families"]
    assert "BCF-TECHNOLOGY-COMPARISON" in by_case["CASE-F-COMPARISON"]["eligible_body_families"]
    assert "BCF-PRINCIPLE-EQUIPMENT-SPLIT" in by_case["CASE-G-PRINCIPLE"]["eligible_body_families"]
    assert "single_visual_capacity" in by_case["CASE-B-PHYSICAL"]["rejection_reasons"]


def test_candidates_are_structurally_distinct_and_tie_break_is_deterministic():
    from thesis_deck_system.presentation_planner_application import build_planner_application

    first = build_planner_application(ROOT)
    second = build_planner_application(ROOT)
    first_j = next(item for item in first["cases"] if item["case_id"] == "CASE-J-DIVERSITY")
    second_j = next(item for item in second["cases"] if item["case_id"] == "CASE-J-DIVERSITY")
    assert len(first_j["candidates"]) == 2
    assert len({item["structure_fingerprint"] for item in first_j["candidates"]}) == 2
    assert first_j["selected_decision"]["selected_candidate_id"] == second_j["selected_decision"]["selected_candidate_id"]
    assert first["candidate_difference_audit"]["fake_candidate_variant_count"] == 0


def test_historical_lock_and_stale_reviewer_selection_never_migrate_or_change_science():
    from thesis_deck_system.presentation_planner_application import PlannerApplicationError, build_planner_application, apply_reviewer_selection

    application = build_planner_application(ROOT)
    historical = next(item for item in application["cases"] if item["case_id"] == "CASE-H-HISTORICAL")
    assert historical["selected_decision"]["selection_mode"] == "historical_reuse"
    candidate = historical["candidates"][0]
    review = {"slide_id": historical["slide_id"], "candidate_id": candidate["candidate_id"], "dependency_hash": "0" * 64, "selection_origin": "reviewer_selection", "layout_locked": True}
    with pytest.raises(PlannerApplicationError):
        apply_reviewer_selection(historical, review)
    assert "scientific_fields" not in review


def test_application_materializes_review_only_pptx_and_incremental_scenario(tmp_path: Path):
    from thesis_deck_system.presentation_planner_application import write_planner_application_artifacts
    from thesis_deck_system.contracts import SchemaRegistry

    outputs = write_planner_application_artifacts(ROOT, tmp_path)
    assert outputs["review_pptx"].is_file()
    assert outputs["acceptance"].is_file()
    import json
    acceptance = json.loads(outputs["acceptance"].read_text(encoding="utf-8"))
    assert acceptance["structural_audit"]["missing_required_region_count"] == 0
    assert acceptance["structural_audit"]["hard_capacity_violation_count"] == 0
    assert acceptance["structural_audit"]["selected_candidate_materialization_mismatch"] == 0
    assert acceptance["incremental_scenario"]["historical_migrations"] == 0
    assert acceptance["incremental_scenario"]["new_physical_slides"] == 2
    registry = SchemaRegistry(ROOT / "thesis-deck-system/schemas", include_cp5hi=True)
    registry.validate("planner-application-acceptance", acceptance)
    registry.validate("composition-review-selections", json.loads(outputs["selections"].read_text(encoding="utf-8")))
