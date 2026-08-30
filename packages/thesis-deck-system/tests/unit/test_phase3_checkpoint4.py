"""Checkpoint 4 control-plane contracts are test-first and renderer-free."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[4]
ARTIFACTS = ROOT / "thesis-deck-system" / "artifacts" / "phase3"


def _cp3_inputs() -> dict[str, dict]:
    import json
    names = (
        "professor-template-resolved.json", "body-composition-profile.json",
        "professor-visual-grammar-v3.json", "visual-style-profile.json",
        "resolver-evidence.json", "checkpoint-3-qa.json",
    )
    return {name: json.loads((ARTIFACTS / name).read_text(encoding="utf-8")) for name in names}


def _request(**overrides: object) -> dict:
    value = {
        "figure_plan_id": "FPL001", "visual_class": "quantitative_measured_result",
        "scientific_purpose": "result_display", "evidence_status": "empirical",
        "scientific_claim_support": "required", "source_refs": ["E101"], "claim_refs": ["C101"],
        "evidence_refs": ["E101"], "hypothesis_layer_ref": "H001", "research_block_refs": ["B101"],
        "stage_ref": "ST-RES101", "source_cursor": 20, "requested_archetype": "A10",
        "provenance_rule_ids": ["CP4-ROUTE-QUANTITATIVE"],
    }
    value.update(overrides)
    return value


def _style() -> dict:
    """Committed CP3 input; never a router production default."""
    return _cp3_inputs()["visual-style-profile.json"]


def test_quantitative_routes_to_vector_plot_and_is_deterministic_under_input_reorder():
    from thesis_deck_system.phase3_checkpoint4 import route_figure_request

    first = route_figure_request(_request(), _style())
    reversed_request = _request(source_refs=["E101"], claim_refs=["C101"], evidence_refs=["E101"])
    second = route_figure_request(reversed_request, _style())
    assert first["selected_specialist_skill"] == "scientific-plot-director"
    assert first["canonical_output_kind"] in {"svg_vector", "pdf_vector"}
    assert first == second


@pytest.mark.parametrize(
    ("visual_class", "expected"),
    [
        ("real_experiment_photo", "photo-annotation-director"),
        ("literature_figure", "literature-figure-director"),
        ("mechanism_explanation", "mechanism-diagram-director"),
        ("experiment_setup", "experiment-schematic-director"),
        ("fabrication_process", "fabrication-process-director"),
        ("fishbone_history", "fishbone-director"),
        ("fair_comparison", "comparison-figure-director"),
        ("image_matrix", "image-matrix-director"),
        ("organic_concept", "concept-illustration-director"),
    ],
)
def test_router_selects_the_bounded_specialist(visual_class: str, expected: str):
    from thesis_deck_system.phase3_checkpoint4 import route_figure_request

    value = _request(visual_class=visual_class)
    if visual_class == "organic_concept":
        value.update(evidence_status="non_evidence", scientific_claim_support="forbidden", claim_refs=[], evidence_refs=[], source_refs=[])
    if visual_class == "fabrication_process":
        value["fabrication_steps"] = [{"ordinal": 1, "condition_state": "unknown"}]
    if visual_class == "fishbone_history":
        value["fishbone_binding"] = {"fishbone_revision_ref": "FB001-R001", "focus_ref": "BR001", "history_ref": "H001"}
    assert route_figure_request(value, _style())["selected_specialist_skill"] == expected


def test_empirical_and_literature_requests_reject_ai_or_concept_masquerading():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, route_figure_request

    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request(visual_class="organic_concept"), _style())
    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request(visual_class="literature_figure", ai_generation_requested=True), _style())
    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request(visual_class="real_experiment_photo", source_refs=[]), _style())


def test_fabrication_is_never_absorbed_and_unknown_condition_is_preserved():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, route_figure_request

    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request(visual_class="mechanism_explanation", fabrication_steps=[{"ordinal": 1, "condition_state": "unknown"}]), _style())
    plan = route_figure_request(_request(visual_class="fabrication_process", fabrication_steps=[{"ordinal": 1, "condition_state": "unknown"}]), _style())
    assert plan["selected_specialist_skill"] == "fabrication-process-director"
    assert plan["specialist_payload"]["steps"][0]["condition_state"] == "unknown"


def test_svg_first_and_native_shape_threshold_fail_closed():
    from thesis_deck_system.phase3_checkpoint4 import route_figure_request

    plan = route_figure_request(_request(visual_class="mechanism_explanation", structured_edges=2), _style())
    assert plan["renderer_class"] == "deterministic_svg_vector"
    assert plan["native_shape_eligibility"]["status"] == "insufficient_evidence"


def test_layout_rejects_raw_or_unapproved_figure():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, validate_layout_figure_handoff

    with pytest.raises(Checkpoint4Error):
        validate_layout_figure_handoff({"artifact_kind": "scientific_figure_spec", "status": "draft"})
    with pytest.raises(Checkpoint4Error):
        validate_layout_figure_handoff({"artifact_kind": "figure_output_manifest", "status": "unapproved"})


def test_routing_matrix_covers_all_archetypes_and_unknown_skill_fails_closed():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, archetype_routing_matrix, validate_skill_registry

    matrix = archetype_routing_matrix()
    assert {item["archetype_id"] for item in matrix} == {f"A{i:02d}" for i in range(1, 19)}
    registry = yaml.safe_load((ROOT / "thesis-deck-system" / "skill-routing.yaml").read_text(encoding="utf-8"))
    registry = copy.deepcopy(registry)
    registry["skills"].append({"skill_id": "unknown-route"})
    with pytest.raises(Checkpoint4Error):
        validate_skill_registry(registry)


def test_cp4_build_is_sanitized_only_and_binds_cp3_inputs_registry_and_schemas():
    from thesis_deck_system.phase3_checkpoint4 import build_checkpoint4_artifacts, capture_regression_evidence

    outputs = build_checkpoint4_artifacts(
        _cp3_inputs(),
        privacy_config={
            "config_id": "CP4-TEST-PRIVACY",
            "private_root_signatures": ["synthetic-private-root"],
            "forbidden_basenames": ["synthetic-private-source.pptx"],
        }, regression_evidence=capture_regression_evidence(_cp3_inputs(), disposable_worktree=True, tests_passed=1, tests_failed=0, suite_id="unit"),
    )
    assert outputs["qa"]["aggregate_status"] == "pass"
    assert outputs["execution"]["private_alias_resolution_attempts"] == 0
    assert outputs["execution"]["private_source_open_attempts"] == 0
    assert outputs["execution"]["private_render_attempts"] == 0
    keys = outputs["execution"]["candidate_state"]["component_hashes"]
    assert any(key.startswith("cp3:") for key in keys)
    assert any(key.startswith("skill-registry:") for key in keys)
    privacy = next(item for item in outputs["execution"]["owning_checks"] if item["check_id"] == "CP4-REPOSITORY-STAGED-PRIVACY")
    assert privacy["status"] == "pass"
    facts = {fact["name"]: fact.get("boolean") for fact in privacy["evidence"]["facts"] if "boolean" in fact}
    assert facts["repository_scan_executed"] is True
    assert facts["staged_scan_executed"] is True


def test_cp4_schema_closure_rejects_untyped_nested_plan_data():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_checkpoint4 import route_figure_request

    plan = route_figure_request(_request(), _style())
    plan["specialist_payload"]["unexpected"] = {"private": "no"}
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True)
    assert registry.errors("figure-production-plan", plan)


def test_every_registry_skill_has_a_complete_repo_local_contract_document():
    from thesis_deck_system.phase3_checkpoint4 import load_skill_registry

    required_sections = ("Triggers", "Do-not-trigger", "Required inputs", "Workflow", "Allowed downstream", "Forbidden actions", "Output contract", "Provenance", "Failure", "Blocked", "Handoff", "QA owner")
    for item in load_skill_registry()["skills"]:
        text = (ROOT / "thesis-deck-system" / "skills" / item["skill_id"] / "SKILL.md").read_text(encoding="utf-8")
        assert all(section in text for section in required_sections), item["skill_id"]


def test_router_binds_the_actual_cp3_style_profile_and_route_specific_categories():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, route_figure_request

    style = _cp3_inputs()["visual-style-profile.json"]
    mechanism = route_figure_request(_request(visual_class="mechanism_explanation"), style)
    photo = route_figure_request(_request(visual_class="real_experiment_photo"), style)
    assert mechanism["style_profile_ref"] == style["style_profile_id"]
    assert "connector_arrow_grammar" in mechanism["required_style_categories"]
    assert mechanism["required_style_categories"] != photo["required_style_categories"]
    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request(style_profile_ref="VSP001"), style)


def test_route_spec_discriminator_and_closed_concept_evidence_slots_fail_closed():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, route_figure_request

    style = _cp3_inputs()["visual-style-profile.json"]
    plan = route_figure_request(_request(visual_class="real_experiment_photo"), style)
    assert plan["figure_type"] == "real_photo"
    bad = _request(visual_class="organic_concept", evidence_status="non_evidence", scientific_claim_support="forbidden", source_refs=[], claim_refs=[], evidence_refs=[], observation_evidence_ref="E101")
    with pytest.raises(Checkpoint4Error):
        route_figure_request(bad, style)


def test_checkpoint_four_persists_all_ten_classes_and_candidate_regression_evidence():
    from thesis_deck_system.phase3_checkpoint4 import build_checkpoint4_artifacts, capture_regression_evidence

    outputs = build_checkpoint4_artifacts(_cp3_inputs(), privacy_config={"config_id":"CP4-TEST-PRIVACY","private_root_signatures":["synthetic-private-root"],"forbidden_basenames":["synthetic-private-source.pptx"]}, regression_evidence=capture_regression_evidence(_cp3_inputs(), disposable_worktree=True, tests_passed=1, tests_failed=0, suite_id="candidate"))
    assert len(outputs["plans"]) == 10
    coverage = next(x for x in outputs["execution"]["owning_checks"] if x["check_id"] == "CP4-VISUAL-CLASS-COVERAGE")
    assert coverage["status"] == "pass"
    regression = next(x for x in outputs["execution"]["owning_checks"] if x["check_id"] == "CP4-DISPOSABLE-REGRESSION")
    assert regression["status"] == "pass"


def test_actual_registry_graph_rejects_layout_bypass_and_direct_spec_to_critic():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, load_skill_registry, validate_skill_registry

    registry = load_skill_registry()
    registry["routes"]["整理這批實驗數據成結果頁"]["handoff"] = ["layout-director"]
    with pytest.raises(Checkpoint4Error):
        validate_skill_registry(registry)


def test_revision2_router_requires_an_actual_valid_cp3_style_profile():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, route_figure_request

    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request())
    with pytest.raises(Checkpoint4Error):
        route_figure_request(_request(), {"style_profile_id": "VSP003"})


@pytest.mark.parametrize("field", ["figure_type", "selected_specialist_skill", "renderer_class", "canonical_output_kind", "evidence_status"])
def test_every_route_rejects_cross_route_plan_discriminator_mutation(field: str):
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_checkpoint4 import ROUTES, route_figure_request

    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True)
    for visual_class in ROUTES:
        request = _request(visual_class=visual_class)
        if visual_class == "organic_concept":
            request.update(evidence_status="non_evidence", scientific_claim_support="forbidden", source_refs=[], claim_refs=[], evidence_refs=[])
        if visual_class == "fabrication_process":
            request["fabrication_steps"] = [{"ordinal": 1, "condition_state": "unknown"}]
        if visual_class == "fishbone_history":
            request["fishbone_binding"] = {"fishbone_revision_ref": "FB001-R001", "focus_ref": "BR001", "history_ref": "H001"}
        plan = route_figure_request(request, _style())
        plan[field] = "scientific_plot" if field == "figure_type" else "scientific-plot-director" if field == "selected_specialist_skill" else "reproducible_plot" if field == "renderer_class" else "svg_vector" if field == "canonical_output_kind" else "empirical"
        if visual_class != "organic_concept":
            plan[field] = "concept_illustration" if field == "figure_type" else "concept-illustration-director" if field == "selected_specialist_skill" else "generated_non_evidence" if field == "renderer_class" else "generated_non_evidence_substrate" if field == "canonical_output_kind" else "non_evidence"
        assert registry.errors("figure-production-plan", plan)


def test_figure_routing_request_schema_is_recursive_and_blocks_concept_empirical_slots():
    from thesis_deck_system.contracts import SchemaRegistry

    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True)
    request = _request(fabrication_steps=[{"ordinal": 1, "condition_state": "unknown", "unexpected": "x"}])
    assert registry.errors("figure-routing-request", request)
    concept = _request(visual_class="organic_concept", evidence_status="non_evidence", scientific_claim_support="forbidden", source_refs=[], claim_refs=[], evidence_refs=[], observation_evidence_ref="E101")
    assert registry.errors("figure-routing-request", concept)


def test_regression_evidence_is_independent_of_final_candidate_hash():
    from thesis_deck_system.phase3_checkpoint4 import Checkpoint4Error, build_checkpoint4_artifacts, capture_regression_evidence

    evidence = capture_regression_evidence(_cp3_inputs(), tests_passed=1, tests_failed=0, suite_id="unit", disposable_worktree=True)
    build_checkpoint4_artifacts(_cp3_inputs(), privacy_config={"config_id":"CP4-TEST-PRIVACY","private_root_signatures":["synthetic-private-root"],"forbidden_basenames":["synthetic-private-source.pptx"]}, regression_evidence=evidence)
    evidence["tested_candidate_hash"] = "0" * 64
    output = build_checkpoint4_artifacts(_cp3_inputs(), privacy_config={"config_id":"CP4-TEST-PRIVACY","private_root_signatures":["synthetic-private-root"],"forbidden_basenames":["synthetic-private-source.pptx"]}, regression_evidence=evidence)
    assert output["qa"]["aggregate_status"] == "fail"


def test_report_artifact_consistency_uses_executed_cp4_facts():
    from thesis_deck_system.phase3_checkpoint4 import build_checkpoint4_artifacts, capture_regression_evidence, validate_report_artifact_consistency

    inputs = _cp3_inputs()
    outputs = build_checkpoint4_artifacts(inputs, privacy_config={"config_id":"CP4-TEST-PRIVACY","private_root_signatures":["synthetic-private-root"],"forbidden_basenames":["synthetic-private-source.pptx"]}, regression_evidence=capture_regression_evidence(inputs, disposable_worktree=True, tests_passed=311, tests_failed=0, suite_id="unit"))
    report = ROOT / "thesis-deck-system" / "reports" / "PHASE_3_CHECKPOINT_4_IMPLEMENTATION_REPORT.md"
    assert validate_report_artifact_consistency(report, outputs)["status"] == "pass"
