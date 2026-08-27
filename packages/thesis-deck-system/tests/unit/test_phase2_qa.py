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
