from __future__ import annotations

import json
import copy
from pathlib import Path

from thesis_deck_system.phase2_build import build_phase2
from thesis_deck_system.ledger import Ledger
from thesis_deck_system.qa2 import run_combined_role_content_qa, run_physical_content_fidelity_qa, run_presentation_temporal_snapshot_qa, run_professor_qa_v2


def _load(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def test_presentation_temporal_snapshots_are_stage_aware_and_future_safe(tmp_path: Path):
    result = build_phase2(output_root=tmp_path)
    specs = _load(tmp_path, "slide-specs.json")
    qa = _load(tmp_path, "presentation-temporal-snapshot-qa.json")
    assert qa["status"] == "pass"
    h01_results = [s for s in specs if s.get("hypothesis_layer_ref") == "H001" and s["semantic_role"] in {"result_single", "result_comparison"}]
    h01_opening = next(s for s in specs if s["slide_id"] == "S-H001-HYPOTHESIS-TITLE-01")
    assert h01_opening["source_cursor"] < min(s["source_cursor"] for s in h01_results)
    assert not set(h01_opening["bindings"]["evidence_refs"]) & {"E101", "E201"}
    h02_opening = next(s for s in specs if s["slide_id"] == "S-H002-HYPOTHESIS-TITLE-01")
    assert "E201" not in h02_opening["bindings"]["evidence_refs"]
    assert result["h01_cursor"] < result["h02_cursor"]


def test_combined_roles_have_physical_content_contract_coverage(tmp_path: Path):
    build_phase2(output_root=tmp_path)
    qa = _load(tmp_path, "combined-role-content-qa.json")
    assert qa["status"] == "pass"
    h02_science = next(item for item in qa["slides"] if item["slide_id"] == "S-H002-OBSERVATION-PROBLEM-04")
    assert set(h02_science["roles"]) >= {"observation_problem", "literature_mechanism", "mechanism_solution"}
    assert not h02_science["missing"]
    h02_summary = next(item for item in qa["slides"] if item["slide_id"] == "S-H002-LAYER-SUMMARY-DECISION-09")
    assert set(h02_summary["roles"]) >= {"layer_integrated_discussion", "layer_summary_decision"}
    assert not h02_summary["missing"]


def test_result_text_and_asset_composition_are_preserved(tmp_path: Path):
    build_phase2(output_root=tmp_path)
    fidelity = _load(tmp_path, "physical-content-fidelity-qa.json")
    assert fidelity["status"] == "pass"
    assert fidelity["missing"] == []
    result_records = {item["result_ref"]: item for item in fidelity["results"]}
    assert result_records["RES101"]["extracted_text"] != result_records["RES102"]["extracted_text"]
    assert result_records["RES101"]["asset_ids"] == ["A001"]
    assert result_records["RES102"]["asset_ids"] == ["A001"]
    # build_phase2 owns assembly; render hashes are populated by the required
    # phase2_render/finalize step.  The pre-render artifact must still expose
    # the binding field for that later render-grounded check.
    assert "render_sha256" in result_records["RES101"]
    assert "render_sha256" in result_records["RES102"]


def test_presentation_semantic_fidelity_is_an_executed_gate(tmp_path: Path):
    build_phase2(output_root=tmp_path)
    assert _load(tmp_path, "presentation-semantic-fidelity-qa.json")["status"] == "pass"
    consistency = _load(tmp_path, "report-evidence-consistency.json")
    assert consistency["status"] == "pass"
    assert consistency["transition_cursor"] == _load(tmp_path, "materialized-transition.json")["events"][-1]["cursor"]


def test_future_result_citation_is_rejected_and_early_state_is_immutable(tmp_path: Path):
    result = build_phase2(output_root=tmp_path)
    ledger = Ledger.load(tmp_path / "ledger-events.json")
    specs = _load(tmp_path, "slide-specs.json")
    tampered = copy.deepcopy(specs)
    title = next(item for item in tampered if item["slide_id"] == "S-H002-HYPOTHESIS-TITLE-01")
    title["bindings"]["evidence_refs"] = ["E201"]
    assert run_presentation_temporal_snapshot_qa(tampered, ledger)["status"] == "fail"
    early = ledger.materialize(result["h01_cursor"])
    ledger.append("evidence_linked", {"evidence_id": "E999", "block_ref": {"block_id": "B201", "revision": 2}, "source": {"source_id": "E999", "path": "examples/synthetic-project/phase2/h01-contact-uncertainty.txt", "sha256": "0" * 64}, "kind": "synthetic_observation", "claim_refs": [], "causal_role": "supporting_observation", "origin": {"layer_ref": "H002"}, "provenance": "synthetic_fixture"})
    assert ledger.materialize(result["h01_cursor"]) == early


def test_combined_role_and_asset_text_contracts_fail_when_physical_content_is_dropped(tmp_path: Path):
    build_phase2(output_root=tmp_path)
    specs = _load(tmp_path, "slide-specs.json")
    audit = _load(tmp_path, "structural-audit.json")
    broken_audit = copy.deepcopy(audit)
    science = next(item for item in broken_audit["generated_slides"] if item["slide_spec_id"] == "S-H002-OBSERVATION-PROBLEM-04")
    science["physical_slot_conformance"] = [item for item in science["physical_slot_conformance"] if item["slot"] != "literature_evidence"]
    assert run_combined_role_content_qa(specs, broken_audit)["status"] == "fail"
    result_audit = next(item for item in broken_audit["generated_slides"] if item["slide_spec_id"] == "S-H001-RESULT-SINGLE-08")
    for slot in result_audit["physical_slot_conformance"]:
        if slot["slot"] == "result_plot":
            slot["actual_text"] = ""
            slot["content_or_asset_binding_result"] = False
    assert run_physical_content_fidelity_qa(specs, broken_audit)["status"] == "fail"


def test_combined_experiment_and_discussion_contracts_are_complete(tmp_path: Path):
    build_phase2(output_root=tmp_path)
    specs = _load(tmp_path, "slide-specs.json")
    experiment = next(item for item in specs if item["slide_id"] == "S-H002-EXPERIMENT-DESIGN-06")
    assert set(experiment["combined_roles"]) >= {"experiment_design", "result_single"}
    assert set(experiment["content"]["slots"]) >= {"experiment_matrix", "decision_rule", "result_plot", "result_annotation"}
    summary = next(item for item in specs if item["slide_id"] == "S-H002-LAYER-SUMMARY-DECISION-09")
    assert set(summary["combined_roles"]) >= {"layer_integrated_discussion", "layer_summary_decision"}
    assert set(summary["content"]["slots"]) >= {"supporting_results", "contradicting_results", "discussion_synthesis", "uncertainty", "decision_status", "next_step"}


def test_professor_qa_rejects_metadata_only_combined_role(tmp_path: Path):
    build_phase2(output_root=tmp_path)
    state = _load(tmp_path, "materialized-h02.json")
    meeting = _load(tmp_path, "meeting-projection.json")
    profile = _load(tmp_path, "professor-profile.json")
    specs = _load(tmp_path, "slide-specs.json")
    combined = _load(tmp_path, "combined-role-content-qa.json")
    broken = copy.deepcopy(combined)
    row = next(item for item in broken["slides"] if item["slide_id"] == "S-H002-OBSERVATION-PROBLEM-04")
    row["status"] = "fail"
    row["missing"] = ["literature_evidence"]
    projection = {**meeting, "layers": list(state["hypothesis_layers"].values()), "slides": specs, "state": state, "presentation_semantic_fidelity": {"status": "pass"}, "combined_role_content": broken}
    assert run_professor_qa_v2(profile, projection)["status"] == "fail"
