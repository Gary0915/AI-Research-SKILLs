from __future__ import annotations

import importlib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]


def _module(name: str):
    try:
        return importlib.import_module(f"thesis_deck_system.{name}")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Phase 2 module is missing: {exc}")


def _layer():
    return {
        "hypothesis_layer_id": "H001",
        "revision": 1,
        "title": "Bulk conductivity hypothesis",
        "hypothesis_claim_ref": "C101",
        "problem_ref": "P101",
        "research_question": "導電度提升是否足以改善重複性？",
        "fishbone_snapshot_ref": {"fishbone_id": "FB001", "revision": 1},
        "fishbone_focus_refs": ["FB-MATERIAL-HYDRATION"],
        "research_block_refs": ["B101"],
        "experiment_refs": ["EXP101", "EXP102"],
        "result_refs": ["RES101", "RES102"],
        "layer_discussion_ref": "DISC-H001",
        "layer_summary_ref": "SUM-H001",
        "layer_decision_ref": "D101",
        "next_step_refs": ["NS101"],
        "transition_ref": "TR-H001-H002",
        "source_event_cursor": 20,
    }


def test_story_compiler_keeps_hypothesis_problem_and_fishbone_separate():
    story = _module("story")
    specs = story.compile_hypothesis_layer(_layer(), source_cursor=20)
    roles = [spec["semantic_role"] for spec in specs]
    assert roles[:3] == ["hypothesis_title", "problem_definition", "fishbone_locator"]
    assert all(not ({"hypothesis_title", "problem_definition"} <= set(spec.get("combined_roles", []))) for spec in specs)
    assert len([spec for spec in specs if spec["semantic_role"] == "fishbone_locator"]) == 1


def test_multi_experiment_results_precede_integrated_discussion_and_summary():
    story = _module("story")
    specs = story.compile_hypothesis_layer(_layer(), source_cursor=20)
    roles = [spec["semantic_role"] for spec in specs]
    exp_indices = [index for index, role in enumerate(roles) if role == "experiment_design"]
    result_indices = [index for index, role in enumerate(roles) if role in {"result_single", "result_comparison"}]
    discussion_index = roles.index("layer_integrated_discussion")
    summary_index = roles.index("layer_summary_decision")
    assert len(exp_indices) == 2 and len(result_indices) == 2
    assert max(exp_indices) < min(result_indices) < max(result_indices) < discussion_index < summary_index


def test_story_validator_rejects_merged_pages_and_early_discussion():
    story = _module("story")
    specs = story.compile_hypothesis_layer(_layer(), source_cursor=20)
    merged = [dict(spec) for spec in specs]
    merged[0]["combined_roles"] = ["hypothesis_title", "problem_definition"]
    assert "P-HARD-01" in {finding.rule_id for finding in story.validate_story_order(_layer(), merged)}
    early = [dict(spec) for spec in specs]
    discussion = next(spec for spec in early if spec["semantic_role"] == "layer_integrated_discussion")
    early.remove(discussion)
    early.insert(4, discussion)
    assert "P-HARD-05" in {finding.rule_id for finding in story.validate_story_order(_layer(), early)}


def test_layout_director_is_deterministic_and_never_merges_hypothesis_problem():
    layout = _module("layout")
    registry = layout.load_archetype_registry(ROOT / "thesis-deck-system" / "layout-archetypes.json")
    director = layout.LayoutDirector(registry)
    request = {"semantic_role": "hypothesis_title", "scientific_stage": "hypothesis", "asset_count": 0, "evidence_count": 1, "experiment_count": 2, "result_count": 2, "target_language": "zh-TW"}
    first = director.select(request)
    second = director.select(dict(request))
    assert first == second
    assert first["selected_archetype"] == "A01"
    with pytest.raises(ValueError, match="must remain separate"):
        director.select({**request, "semantic_role": "hypothesis_problem_merged"})


def test_traditional_chinese_wrapping_preserves_punctuation_and_mixed_terms():
    typography = _module("typography")
    lines = typography.wrap_zh_tw("接觸電阻（Contact resistance）是否主導訊號不穩定？", max_chars=18)
    assert all(len(line) <= 18 for line in lines)
    assert not any(line.startswith(("，", "。", "？", "）")) for line in lines[1:])
    assert "Contact resistance" in "".join(lines)
