from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from PIL import Image


def _module(name: str):
    try:
        return importlib.import_module(f"thesis_deck_system.{name}")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Phase 2 module is missing: {exc}")


def test_professor_qa_v2_reports_concrete_layer_findings():
    qa2 = _module("qa2")
    projection = {
        "layers": [{"hypothesis_layer_id": "H001", "hypothesis_status": "partial_support"}],
        "slides": [
            {"semantic_role": "hypothesis_title", "hypothesis_layer_ref": "H001"},
            {"semantic_role": "fishbone_locator", "hypothesis_layer_ref": "H001", "fishbone_focus_refs": []},
            {"semantic_role": "layer_integrated_discussion", "hypothesis_layer_ref": "H001", "content": {"supporting_results": ["RES101"]}},
        ],
        "previous_commitments": [],
    }
    report = qa2.run_professor_qa_v2({"profile_id": "PROF-SYNTH-001", "version": "2.0.0", "rules": {}}, projection)
    ids = {finding["rule_id"] for finding in report["findings"]}
    assert "PROF-HYPOTHESIS-PROBLEM-SEPARATE" in ids
    assert "PROF-FISHBONE-FOCUS" in ids
    assert "PROF-NEXT-STEP-OWNER-TIMING" in ids
    assert report["status"] == "fail"


def test_visual_qa_v2_executes_image_and_geometry_checks(tmp_path: Path):
    qa2 = _module("qa2")
    blank = tmp_path / "blank.png"
    Image.new("RGB", (1280, 720), "white").save(blank)
    slide = {"slide_id": "S-H001-HYP-01", "semantic_role": "hypothesis_title", "title": {"text": "假說一"}, "placement_plan": [{"left": 0, "top": 0, "width": 100, "height": 100, "font_size_pt": 12}]}
    report = qa2.run_visual_qa_v2([slide], {slide["slide_id"]: blank}, expected_size=(1280, 720))
    ids = {finding["rule_id"] for finding in report["findings"]}
    assert "VISUAL-BLANK-RENDER" in ids
    assert "VISUAL-MIN-FONT" in ids
    assert report["executed_checks"]


def test_professor_qa_gates_checks_from_persisted_profile_rules():
    qa2 = _module("qa2")
    projection = {
        "layers": [{"hypothesis_layer_id": "H001", "hypothesis_status": "partial_support"}],
        "slides": [{"semantic_role": "hypothesis_title", "hypothesis_layer_ref": "H001"}],
        "previous_commitments": [],
    }
    profile = {"profile_id": "PROF-SYNTH-001", "version": "1.0.0", "narrative_rules": {"require_question_before_data": False}}
    report = qa2.run_professor_qa_v2(profile, projection)
    assert "PROF-QUESTION-BEFORE-RESULT" not in report["executed_checks"]
    assert report["evidence"]["PROF-QUESTION-BEFORE-RESULT"]["skipped"] is True
    assert report["evidence"]["PROF-QUESTION-BEFORE-RESULT"]["profile_rule"] == "narrative_rules.require_question_before_data"


def test_professor_qa_rejects_incomplete_transition_provenance():
    qa2 = _module("qa2")
    projection = {
        "layers": [{"hypothesis_layer_id": "H001", "fishbone_snapshot_ref": {"revision": 1}, "research_block_refs": ["B101"], "result_refs": ["RES101"]}],
        "slides": [{"semantic_role": "hypothesis_title", "hypothesis_layer_ref": "H001"}, {"semantic_role": "hypothesis_transition", "hypothesis_layer_ref": "H001"}],
        "state": {"claims": {"C101": {}, "C201": {}}, "stages": {"ST-RES101": {}}, "decisions": {}, "evidence": {}, "hypothesis_transitions": {"TR-H001-H002": {"previous_hypothesis_claim_ref": "C101", "new_hypothesis_claim_ref": "C201", "key_result_refs": ["RES101"], "decision_refs": [], "observation_or_uncertainty_refs": []}}},
        "previous_commitments": [],
    }
    report = qa2.run_professor_qa_v2({"profile_id": "PROF-SYNTH-001", "version": "1.0.0"}, projection)
    assert "PROF-TRANSITION-PROVENANCE" in {finding["rule_id"] for finding in report["findings"]}


def test_visual_qa_rejects_nonhierarchical_title_and_unsplit_budget(tmp_path: Path):
    qa2 = _module("qa2")
    image = Image.new("RGB", (1280, 720), "white")
    image.putpixel((0, 0), (0, 0, 0))
    image_path = tmp_path / "nonhierarchical.png"
    image.save(image_path)
    slide = {
        "slide_id": "S-H001-HYP-02",
        "semantic_role": "hypothesis_title",
        "title": {"text": "Hypothesis"},
        "content": {"body": "long body"},
        "split_recommendation": True,
        "placement_plan": [
            {"slot": "hypothesis_statement", "left": 0, "top": 0, "width": 6, "height": 2, "font_size_pt": 16, "element_role": "assertion"},
            {"slot": "body", "left": 0, "top": 2, "width": 6, "height": 2, "font_size_pt": 18, "element_role": "body"},
        ],
    }
    report = qa2.run_visual_qa_v2([slide], {slide["slide_id"]: image_path}, expected_size=(1280, 720))
    ids = {finding["rule_id"] for finding in report["findings"]}
    assert "VISUAL-TITLE-HIERARCHY" in ids
    assert "VISUAL-DENSITY-BUDGET" in ids
