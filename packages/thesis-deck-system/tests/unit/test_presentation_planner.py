"""Closed, deterministic Presentation Planner Foundation v1 contracts."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]


def test_content_shape_is_deterministic_and_ignores_presentation_only_provenance():
    from thesis_deck_system.presentation_planner import build_scientific_content_shape

    record = {
        "slide_id": "S-EXP-001",
        "semantic_stage": "experiment_design",
        "title": "Experiment",
        "visible_text": ["canonical bullet"],
        "source_semantic_fields": {"experiment_design": {"controls": ["C1", "C2", "C3"]}},
        "source_bindings": {"evidence_refs": ["EV-001"]},
        "governed_figure_route": "experiment",
    }
    first = build_scientific_content_shape(record)
    second = build_scientific_content_shape(record | {"notes_only_fields": ["private-provenance"]})

    assert first["content_shape_sha256"] == second["content_shape_sha256"]
    assert first["observations"]["experiment_control_count"]["value"] == 3


def test_candidate_selection_reuses_historical_composition_before_scoring_new_candidates():
    from thesis_deck_system.presentation_planner import select_composition

    shape = {"slide_id": "S-RESULT-001", "content_shape_sha256": "a" * 64, "semantic_stage": "result_single"}
    candidates = [
        {"candidate_id": "CC-A", "capability_id": "LC-RESULT", "body_family_id": "BCF-REAL-RESULT-VALIDATION", "score": {"total": 4}},
        {"candidate_id": "CC-B", "capability_id": "LC-RESULT", "body_family_id": "BCF-PHYSICAL-VALIDATION-MATRIX", "score": {"total": 9}},
    ]
    decision = select_composition(shape, candidates, lifecycle_decision="reuse_exact", historical_composition_id="CC-A")

    assert decision["selection_mode"] == "historical_reuse"
    assert decision["selected_candidate_id"] == "CC-A"
    assert decision["historical_lock_status"] == "locked_dependency_unchanged"


def test_capacity_mismatch_is_not_selected_and_equal_new_candidates_use_deterministic_diversity_tiebreaker():
    from thesis_deck_system.presentation_planner import PlannerError, select_composition

    shape = {"slide_id": "S-NEW-001", "content_shape_sha256": "b" * 64, "semantic_stage": "experiment_design"}
    candidates = [
        {"candidate_id": "CC-Z", "capability_id": "LC-EXP", "body_family_id": "BCF-HARDWARE-DESIGN-PROCEDURE", "score": {"total": 8, "hard_capacity_match": True}},
        {"candidate_id": "CC-A", "capability_id": "LC-EXP", "body_family_id": "BCF-FEASIBILITY-EVIDENCE-MATRIX", "score": {"total": 8, "hard_capacity_match": True}},
    ]
    assert select_composition(shape, candidates, lifecycle_decision="append_new")["selected_candidate_id"] == "CC-A"
    with pytest.raises(PlannerError):
        select_composition(shape, [{"candidate_id": "CC-X", "capability_id": "LC-X", "body_family_id": "BCF-TEXT-TOP-DUAL-VISUAL", "score": {"total": 99, "hard_capacity_match": False}}], lifecycle_decision="append_new")


def test_current_acceptance_deck_planner_audit_is_closed_and_never_migrates_historical_slides():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.presentation_planner import build_current_acceptance_planner_artifacts

    artifacts = build_current_acceptance_planner_artifacts(ROOT)
    assert artifacts["presentation_planner_qa"]["aggregate_status"] == "pass"
    assert artifacts["composition_selection_audit"]["unchanged_historical_slide_style_migration_count"] == 0
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5hi=True)
    assert registry.errors("presentation-planner-qa", artifacts["presentation_planner_qa"]) == []


def test_planner_artifacts_are_persisted_with_closed_registered_contracts(tmp_path: Path):
    from thesis_deck_system.presentation_planner import write_current_acceptance_planner_artifacts

    paths = write_current_acceptance_planner_artifacts(ROOT, tmp_path)
    assert {path.name for path in paths.values()} == {
        "scientific-content-shapes.json", "layout-capability-registry.json", "composition-candidates.json",
        "composition-selection-audit.json", "presentation-planner-qa.json",
    }
