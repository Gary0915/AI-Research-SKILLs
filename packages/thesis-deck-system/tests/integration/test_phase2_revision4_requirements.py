from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from thesis_deck_system.ledger import Ledger
from thesis_deck_system.phase2_build import _n_layer_projection_report, build_phase2
from thesis_deck_system.qa2 import (
    run_combined_role_content_qa,
    run_presentation_semantic_fidelity_qa,
    run_presentation_temporal_snapshot_qa,
    run_report_evidence_consistency,
)
from thesis_deck_system.story import compile_master_story_from_ledger


def _load(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase2-revision4")
    build_phase2(output_root=root)
    return root


def _layer(layer_id: str, block_id: str, claim_id: str, problem_id: str, fishbone_revision: int) -> dict:
    number = layer_id[-3:]
    return {
        "hypothesis_layer_id": layer_id,
        "revision": 1,
        "hypothesis_claim_ref": claim_id,
        "problem_ref": problem_id,
        "research_block_refs": [block_id],
        "research_question": f"Question {layer_id}?",
        "experiment_refs": [f"EXP{number}"],
        "experiment_order": [f"EXP{number}"],
        "result_refs": [f"RES{number}"],
        "result_order": [f"RES{number}"],
        "layer_discussion_ref": f"DISC-{layer_id}",
        "layer_summary_ref": f"SUM-{layer_id}",
        "fishbone_snapshot_ref": {"fishbone_id": "FB777", "revision": fishbone_revision},
        "fishbone_focus_refs": [f"FB-FOCUS-{number}"],
        "source_event_cursor": 0,
    }


def _three_layer_ledger() -> Ledger:
    ledger = Ledger()
    previous = None
    previous_suffix = None
    for index, layer_id in enumerate(("H011", "H022", "H033"), 1):
        block_id = f"B{index}77"
        claim_id = f"C{index}77"
        problem_id = f"P{index}77"
        layer = _layer(layer_id, block_id, claim_id, problem_id, index)
        ledger.append("claim_created", {"claim_id": claim_id})
        if previous:
            transition = {
                "transition_id": f"TR-{previous}-{layer_id}",
                "from_layer_ref": previous,
                "to_layer_ref": layer_id,
                "previous_hypothesis_claim_ref": f"C{index - 1}77",
                "new_hypothesis_claim_ref": claim_id,
                "key_result_refs": [f"RES{previous_suffix}"],
                "decision_refs": [f"D{index - 1}77"],
                "observation_or_uncertainty_refs": [f"E{index - 1}70"],
            }
            ledger.append("hypothesis_transition_recorded", transition)
        layer["source_event_cursor"] = len(ledger.replay()) + 1
        ledger.append("hypothesis_layer_created", layer)
        ledger.append("problem_created", {"problem_id": problem_id})
        ledger.append("fishbone_created" if index == 1 else "fishbone_revised", {"fishbone_id": "FB777", "revision": index})
        stage_refs = {}
        for stage_type in ("observation", "literature", "mechanism", "solution"):
            stage_id = f"ST-{layer_id}-{stage_type.upper()}"
            stage_refs[stage_type] = stage_id
            ledger.append("stage_revised", {"stage_id": stage_id, "stage_type": stage_type, "status": "complete", "block_ref": {"block_id": block_id}})
        asset_id = f"A{index}77"
        ledger.append("asset_registered", {"asset_id": asset_id, "asset_type": "data_plot"})
        ledger.append("block_created", {"block_id": block_id, "revision": 1, "stage_refs": stage_refs, "asset_refs": [asset_id]})
        suffix = layer_id[-3:]
        ledger.append("stage_revised", {"stage_id": f"ST-EXP{suffix}", "stage_type": "experiment", "status": "complete", "block_ref": {"block_id": block_id}})
        ledger.append("evidence_linked", {"evidence_id": f"E{index}77", "causal_role": "experiment_result", "origin": {"layer_ref": layer_id, "experiment_stage_ref": f"ST-EXP{suffix}"}})
        ledger.append("stage_revised", {"stage_id": f"ST-RES{suffix}", "stage_type": "result", "status": "complete", "block_ref": {"block_id": block_id}, "evidence_refs": [f"E{index}77"], "data": {"summary": f"Result {layer_id}"}})
        ledger.append("layer_discussion_recorded", {"discussion_id": f"DISC-{layer_id}", "hypothesis_layer_ref": layer_id})
        ledger.append("decision_recorded", {"decision_id": f"D{index}77"})
        ledger.append("layer_summary_recorded", {"summary_id": f"SUM-{layer_id}", "hypothesis_layer_ref": layer_id, "decision_ref": f"D{index}77"})
        previous = layer_id
        previous_suffix = suffix
    return ledger


def test_production_n_layer_projection_keeps_every_middle_layer_and_transition():
    specs = compile_master_story_from_ledger(_three_layer_ledger())
    layer_order = []
    for spec in specs:
        layer_id = spec.get("hypothesis_layer_ref")
        if layer_id and layer_id not in layer_order:
            layer_order.append(layer_id)
    assert layer_order == ["H011", "H022", "H033"]
    assert [spec["object_ref"] for spec in specs if spec["semantic_role"] == "hypothesis_transition"] == [
        "TR-H011-H022",
        "TR-H022-H033",
    ]
    for layer_id in layer_order:
        roles = {spec["semantic_role"] for spec in specs if spec.get("hypothesis_layer_ref") == layer_id}
        assert {"hypothesis_title", "problem_definition", "fishbone_locator"} <= roles


def test_n_layer_projection_report_rejects_a_skipped_middle_layer():
    ledger = _three_layer_ledger()
    specs = [spec for spec in compile_master_story_from_ledger(ledger) if spec.get("hypothesis_layer_ref") != "H022"]
    report = _n_layer_projection_report(ledger, specs, {})
    assert report["status"] == "fail"
    assert report["skipped_layers"] == ["H022"]


def test_reusable_story_and_temporal_drivers_have_no_fixture_literal_dependencies():
    paths = [
        Path("packages/thesis-deck-system/src/thesis_deck_system/story.py"),
        Path("packages/thesis-deck-system/src/thesis_deck_system/qa2.py"),
    ]
    forbidden = {"H001", "H002", "B101", "B201", "ST-RES101", "ST-RES102", "ST-RES201", "E101", "E201"}
    reusable_text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert not (forbidden & {item for item in forbidden if item in reusable_text})


def test_successor_lifecycle_is_transition_then_open_then_science(built: Path):
    lifecycle = _load(built, "layer-lifecycle-qa.json")
    assert lifecycle["status"] == "pass"
    second = lifecycle["layers"][1]
    assert second["transition_cursor"] < second["layer_open_cursor"]
    assert second["layer_open_cursor"] < second["first_scientific_stage_cursor"]
    assert second["first_scientific_stage_cursor"] <= second["experiment_cursor"]
    assert second["experiment_cursor"] < second["result_evidence_cursor"]


def test_generic_temporal_qa_derives_result_evidence_and_strict_opening_bound():
    ledger = Ledger()
    ledger.append("claim_created", {"claim_id": "C777"})
    ledger.append("evidence_linked", {"evidence_id": "E700", "causal_role": "supporting_observation", "origin": {"layer_ref": "H777"}})
    ledger.append("problem_created", {"problem_id": "P777"})
    ledger.append("fishbone_created", {"fishbone_id": "FB777", "revision": 1})
    ledger.append("block_created", {"block_id": "B777", "revision": 1})
    ledger.append("hypothesis_layer_created", _layer("H777", "B777", "C777", "P777", 1))
    ledger.append("stage_revised", {"stage_id": "ST-EXP777", "stage_type": "experiment", "status": "complete", "block_ref": {"block_id": "B777"}})
    result_evidence_cursor = ledger.append("evidence_linked", {"evidence_id": "E777", "causal_role": "experiment_result", "origin": {"layer_ref": "H777", "experiment_stage_ref": "ST-EXP777"}}).cursor
    result_cursor = ledger.append("stage_revised", {"stage_id": "ST-RES777", "stage_type": "result", "status": "complete", "block_ref": {"block_id": "B777"}, "evidence_refs": ["E777"]}).cursor
    opening = {
        "slide_id": "S-H777-HYPOTHESIS-TITLE-01", "hypothesis_layer_ref": "H777", "semantic_role": "hypothesis_title",
        "source_cursor": result_evidence_cursor, "object_ref": "C777", "bindings": {"claim_refs": ["C777"], "evidence_refs": ["E700"], "asset_refs": [], "action_refs": [], "decision_refs": []},
        "fishbone_snapshot_ref": None, "fishbone_focus_refs": [], "stage_source_cursors": {},
    }
    result = {
        "slide_id": "S-H777-RESULT-SINGLE-02", "hypothesis_layer_ref": "H777", "semantic_role": "result_single",
        "source_cursor": result_cursor, "object_ref": "RES777", "bindings": {"claim_refs": ["C777"], "evidence_refs": ["E777"], "asset_refs": [], "action_refs": [], "decision_refs": []},
        "fishbone_snapshot_ref": None, "fishbone_focus_refs": [], "stage_source_cursors": {"result_single": result_cursor},
    }
    qa = run_presentation_temporal_snapshot_qa([opening, result], ledger)
    assert qa["status"] == "fail"
    opening_row, result_row = qa["slides"]
    assert opening_row["latest_allowed_cursor"] == result_evidence_cursor - 1
    assert "opening_not_strictly_before_result_evidence" in opening_row["future_ref_findings"]
    assert result_row["earliest_required_cursor"] == result_cursor
    assert any(item["dependency_ref"] == "E777" for item in result_row["dependency_refs"])


def test_generic_transition_uses_true_dependency_and_successor_result_bounds():
    ledger = Ledger()
    ledger.append("claim_created", {"claim_id": "C700"})
    ledger.append("hypothesis_layer_created", _layer("H700", "B700", "C700", "P700", 1))
    ledger.append("decision_recorded", {"decision_id": "D700"})
    ledger.append("layer_discussion_recorded", {"discussion_id": "DISC-H700", "hypothesis_layer_ref": "H700"})
    ledger.append("evidence_linked", {"evidence_id": "E770", "causal_role": "transition_precursor", "origin": {"layer_ref": "H700"}})
    ledger.append("claim_created", {"claim_id": "C777"})
    transition_cursor = ledger.append("hypothesis_transition_recorded", {"transition_id": "TR-H700-H777", "from_layer_ref": "H700", "to_layer_ref": "H777", "previous_hypothesis_claim_ref": "C700", "new_hypothesis_claim_ref": "C777", "key_result_refs": [], "decision_refs": ["D700"], "observation_or_uncertainty_refs": ["E770"]}).cursor
    ledger.append("hypothesis_layer_created", _layer("H777", "B777", "C777", "P777", 2))
    ledger.append("stage_revised", {"stage_id": "ST-EXP777", "stage_type": "experiment", "status": "complete", "block_ref": {"block_id": "B777"}})
    result_evidence_cursor = ledger.append("evidence_linked", {"evidence_id": "E777", "causal_role": "experiment_result", "origin": {"layer_ref": "H777", "experiment_stage_ref": "ST-EXP777"}}).cursor
    spec = {"slide_id": "S-H700-HYPOTHESIS-TRANSITION-01", "hypothesis_layer_ref": "H700", "semantic_role": "hypothesis_transition", "source_cursor": transition_cursor, "object_ref": "TR-H700-H777", "bindings": {"claim_refs": ["C700", "C777"], "evidence_refs": ["E770"], "asset_refs": [], "action_refs": [], "decision_refs": ["D700"]}, "fishbone_snapshot_ref": None, "fishbone_focus_refs": [], "stage_source_cursors": {}}
    row = run_presentation_temporal_snapshot_qa([spec], ledger)["slides"][0]
    assert row["status"] == "pass"
    assert row["earliest_required_cursor"] == transition_cursor
    assert row["latest_allowed_cursor"] == result_evidence_cursor - 1


@pytest.mark.parametrize(
    ("role", "field"),
    [
        ("experiment_design", "replicates"),
        ("experiment_design", "instrumentation_method"),
        ("literature_mechanism", "research_gap"),
        ("layer_integrated_discussion", "mechanism_assessment"),
        ("layer_integrated_discussion", "alternative_explanations"),
        ("layer_summary_decision", "hypothesis_status"),
        ("layer_summary_decision", "next_question"),
    ],
)
def test_field_level_contract_rejects_one_missing_subfield_with_nonempty_parent_slot(built: Path, role: str, field: str):
    specs = _load(built, "slide-specs.json")
    audit = _load(built, "structural-audit.json")
    target = next(spec for spec in specs if role in spec.get("combined_roles", [spec["semantic_role"]]))
    broken = copy.deepcopy(specs)
    broken_target = next(spec for spec in broken if spec["slide_id"] == target["slide_id"])
    del broken_target["content"]["semantic_fields"][role][field]
    assert any(str(value).strip() for value in broken_target["content"]["slots"].values())
    report = run_combined_role_content_qa(broken, audit)
    row = next(item for item in report["slides"] if item["slide_id"] == target["slide_id"])
    assert row["status"] == "fail"
    assert f"{role}.{field}" in row["missing"]


def test_semantic_gate_checks_all_results_with_render_grounding_and_story_order(built: Path):
    specs = _load(built, "slide-specs.json")
    audit = _load(built, "structural-audit.json")
    temporal = _load(built, "presentation-temporal-snapshot-qa.json")
    combined = _load(built, "combined-role-content-qa.json")
    fidelity = _load(built, "physical-content-fidelity-qa.json")
    assert len(fidelity["results"]) >= 3
    for index, row in enumerate(fidelity["results"]):
        row["render_sha256"] = f"render-{index}"
    fidelity["results"][2]["render_sha256"] = fidelity["results"][1]["render_sha256"]
    report = run_presentation_semantic_fidelity_qa(specs, audit, temporal, combined, fidelity, ledger=Ledger.load(built / "ledger-events.json"))
    assert report["status"] == "fail"
    assert any(item["rule"] == "visible_result_distinction" for item in report["findings"])
    assert set(report["executed_checks"]) >= {
        "hypothesis_problem_separation", "result_before_integrated_discussion", "discussion_before_summary",
        "historical_fishbone_binding", "transition_location_provenance", "visible_result_distinction",
    }


@pytest.mark.parametrize("mutation", ["story_order", "historical_fishbone"])
def test_semantic_gate_rejects_story_order_and_historical_fishbone_mutations(built: Path, mutation: str):
    specs = _load(built, "slide-specs.json")
    audit = _load(built, "structural-audit.json")
    temporal = _load(built, "presentation-temporal-snapshot-qa.json")
    combined = _load(built, "combined-role-content-qa.json")
    fidelity = _load(built, "physical-content-fidelity-qa.json")
    broken = copy.deepcopy(specs)
    if mutation == "story_order":
        discussion_index = next(index for index, spec in enumerate(broken) if "layer_integrated_discussion" in spec.get("combined_roles", []))
        result_index = next(index for index, spec in enumerate(broken) if "result_single" in spec.get("combined_roles", []))
        broken.insert(result_index, broken.pop(discussion_index))
    else:
        fishbone = next(spec for spec in broken if spec.get("semantic_role") == "fishbone_locator")
        fishbone["fishbone_snapshot_ref"]["revision"] = 999
    report = run_presentation_semantic_fidelity_qa(broken, audit, temporal, combined, fidelity, ledger=Ledger.load(built / "ledger-events.json"))
    assert report["status"] == "fail"
    expected_rule = "result_before_integrated_discussion" if mutation == "story_order" else "historical_fishbone_binding"
    assert any(item["rule"] == expected_rule for item in report["findings"])


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("precursor_evidence_cursor", 32),
        ("h01_experiment_cursors", []),
        ("physical_pptx_page_count", 999),
        ("missing_governed_slot_count", 1),
    ],
)
def test_report_consistency_rejects_stale_or_omitted_canonical_fact(built: Path, field: str, replacement):
    facts = _load(built, "report-facts.json")
    reported = copy.deepcopy(facts)
    reported[field] = replacement
    result = run_report_evidence_consistency(facts, reported)
    assert result["status"] == "fail"
    assert field in result["mismatches"]
