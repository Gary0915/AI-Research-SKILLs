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


def test_v2_candidate_eligibility_is_derived_from_content_shape_and_items_not_a_caller_family_list():
    from thesis_deck_system.presentation_planner import (
        build_layout_capability_registry,
        build_scientific_content_shape,
        generate_composition_candidates,
    )

    record = {
        "slide_id": "S-EXP-V2-001",
        "semantic_stage": "experiment_design",
        "title": "Hardware procedure",
        "visible_text": ["purpose", "controls", "GO criterion"],
        "source_semantic_fields": {"experiment_design": {"controls": ["C1", "C2"]}},
        "source_bindings": {"evidence_refs": ["EV-001", "EV-002"]},
        "governed_figure_route": "experiment",
        "composition_content_items": [
            {"item_id": "ITEM-CAD", "semantic_role": "hardware", "presentation_role": "primary_visual", "content_kind": "cad", "required": True},
            {"item_id": "ITEM-CONTROLS", "semantic_role": "controls", "presentation_role": "procedure", "content_kind": "text", "required": True},
            {"item_id": "ITEM-GO", "semantic_role": "decision", "presentation_role": "go_criterion", "content_kind": "metric", "required": True},
        ],
    }

    shape = build_scientific_content_shape(record)
    families = {item["body_family_id"] for item in generate_composition_candidates(shape, build_layout_capability_registry())}

    missing_hardware_shape = build_scientific_content_shape(record | {
        "slide_id": "S-EXP-V2-002",
        "composition_content_items": [
            {"item_id": "ITEM-TEXT", "semantic_role": "purpose", "presentation_role": "body", "content_kind": "text", "required": True},
        ],
    })
    missing_hardware_families = {
        item["body_family_id"]
        for item in generate_composition_candidates(missing_hardware_shape, build_layout_capability_registry())
    }

    assert "BCF-HARDWARE-DESIGN-PROCEDURE" in families
    assert "BCF-HARDWARE-DESIGN-PROCEDURE" not in missing_hardware_families


def test_content_items_are_the_authoritative_capacity_observations_and_hash_input():
    from thesis_deck_system.presentation_planner import build_scientific_content_shape

    base = {
        "slide_id": "S-SHAPE-ITEMS-001",
        "semantic_stage": "experiment_design",
        "title": "Synthetic capacity fixture",
        "visible_text": ["controlled text"],
        "source_semantic_fields": {"experiment_design": {}},
        "source_bindings": {"evidence_refs": ["EV-001"]},
        "governed_figure_route": None,
        "composition_content_items": [
            {"item_id": "PHOTO", "semantic_role": "setup", "presentation_role": "primary_visual", "content_kind": "photo", "required": True},
            {"item_id": "PLOT", "semantic_role": "validation", "presentation_role": "secondary_visual", "content_kind": "plot", "required": True},
            {"item_id": "CAP", "semantic_role": "validation", "presentation_role": "caption", "content_kind": "caption", "required": True},
            {"item_id": "CITE", "semantic_role": "citation", "presentation_role": "citation_strip", "content_kind": "citation", "required": True},
            {"item_id": "METRIC", "semantic_role": "validation", "presentation_role": "metric_callout", "content_kind": "metric", "required": True},
        ],
    }
    first = build_scientific_content_shape(base)
    changed_kind = build_scientific_content_shape(base | {"composition_content_items": base["composition_content_items"][:-1] + [{**base["composition_content_items"][-1], "content_kind": "callout"}]})

    assert first["observations"]["photo_count"]["value"] == 1
    assert first["observations"]["plot_count"]["value"] == 1
    assert first["observations"]["caption_count"]["value"] == 1
    assert first["observations"]["citation_count"]["value"] == 1
    assert first["observations"]["metric_count"]["value"] == 1
    assert first["observations"]["primary_visual_count"]["value"] == 1
    assert first["observations"]["secondary_visual_count"]["value"] == 1
    assert first["content_shape_sha256"] != changed_kind["content_shape_sha256"]


def test_selection_rejects_candidates_that_fail_any_v2_hard_fit_gate():
    from thesis_deck_system.presentation_planner import select_composition

    shape = {
        "slide_id": "PPA-HARD-GATE-001",
        "content_shape_sha256": "a" * 64,
    }
    invalid = {
        "candidate_id": "CC-INVALID",
        "score": {
            "semantic_hard_match": False,
            "capacity_hard_match": True,
            "required_role_coverage": True,
            "total": 999,
        },
    }
    valid = {
        "candidate_id": "CC-VALID",
        "score": {
            "semantic_hard_match": True,
            "capacity_hard_match": True,
            "required_role_coverage": True,
            "total": 1,
        },
    }

    decision = select_composition(shape, [invalid, valid], lifecycle_decision="append_new")

    assert decision["selected_candidate_id"] == "CC-VALID"


def test_fit_score_uses_reference_specific_body_recurrence_not_a_constant_placeholder():
    from thesis_deck_system.presentation_planner import build_layout_capability_registry, build_scientific_content_shape, generate_composition_candidates

    record = {
        "slide_id": "S-PRINCIPLE-RECURRENCE-001", "semantic_stage": "hypothesis_transition",
        "title": "Principle / Equipment", "visible_text": ["controlled fixture"],
        "source_semantic_fields": {"hypothesis_transition": {}}, "source_bindings": {},
        "governed_figure_route": None,
        "composition_content_items": [
            {"item_id": "PRINCIPLE", "semantic_role": "principle", "presentation_role": "primary_visual", "content_kind": "schematic", "required": True},
            {"item_id": "EQUIPMENT", "semantic_role": "equipment", "presentation_role": "secondary_visual", "content_kind": "table", "required": True},
            {"item_id": "FORMULA", "semantic_role": "principle", "presentation_role": "formula", "content_kind": "formula", "required": True},
        ],
    }
    candidates = generate_composition_candidates(build_scientific_content_shape(record), build_layout_capability_registry())
    recurrent = next(item for item in candidates if item["body_family_id"] == "BCF-PRINCIPLE-EQUIPMENT-SPLIT")

    assert recurrent["score"]["body_recurrence_fit"] > 1
    assert recurrent["score"]["body_recurrence_evidence"]["reference_count"] == 3
    assert recurrent["score"]["semantic_fit"] > 0
    assert recurrent["score"]["capacity_fit"] > 0


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
