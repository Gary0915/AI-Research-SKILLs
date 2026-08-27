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
    signatures = {tuple(item[:5] for item in layout.ROLE_GEOMETRY[role]) for role in layout.ROLE_TO_ARCHETYPE}
    assert len(signatures) >= 6 and set(layout.ROLE_TO_ARCHETYPE) <= set(layout.ROLE_GEOMETRY)
    with pytest.raises(ValueError, match="must remain separate"):
        director.select({**request, "semantic_role": "hypothesis_problem_merged"})


def test_traditional_chinese_wrapping_preserves_punctuation_and_mixed_terms():
    typography = _module("typography")
    lines = typography.wrap_zh_tw("接觸電阻（Contact resistance）是否主導訊號不穩定？", max_chars=18)
    assert all(len(line) <= 18 for line in lines)
    assert not any(line.startswith(("，", "。", "？", "）")) for line in lines[1:])
    assert "Contact resistance" in "".join(lines)


def test_fishbone_hierarchy_rejects_duplicates_orphans_and_cycles(tmp_path: Path):
    fishbone = _module("fishbone")
    duplicate = {"fishbone_id": "FB001", "revision": 1, "branches": [{"branch_id": "FB-A", "label": "A", "parent_ref": None}, {"branch_id": "FB-A", "label": "A2", "parent_ref": None}]}
    orphan = {"fishbone_id": "FB001", "revision": 1, "branches": [{"branch_id": "FB-A", "label": "A", "parent_ref": "FB-NOT"}]}
    cycle = {"fishbone_id": "FB001", "revision": 1, "branches": [{"branch_id": "FB-A", "label": "A", "parent_ref": "FB-B"}, {"branch_id": "FB-B", "label": "B", "parent_ref": "FB-A"}]}
    for revision, expected in ((duplicate, "duplicate"), (orphan, "orphan"), (cycle, "cycle")):
        with pytest.raises(ValueError, match=expected):
            fishbone.render_fishbone_svg(revision, [], "H01", tmp_path / f"{expected}.svg")


def test_fishbone_child_connector_uses_declared_parent(tmp_path: Path):
    fishbone = _module("fishbone")
    revision = {"fishbone_id": "FB001", "revision": 2, "branches": [{"branch_id": "FB-ELECTRODE", "label": "電極", "parent_ref": None}, {"branch_id": "FB-ELECTRODE-CONTACT", "label": "接觸", "parent_ref": "FB-ELECTRODE"}]}
    svg = fishbone.render_fishbone_svg(revision, ["FB-ELECTRODE-CONTACT"], "H02", tmp_path / "hierarchy.svg").read_text(encoding="utf-8")
    assert 'data-parent-ref="FB-ELECTRODE"' in svg
    assert 'id="FB-ELECTRODE-CONTACT"' in svg


def test_causal_history_rejects_future_transition_and_early_discussion():
    from thesis_deck_system.hypothesis import validate_causal_history
    from thesis_deck_system.ledger import Ledger
    ledger = Ledger()
    ledger.append("claim_created", {"claim_id": "C101"})
    ledger.append("hypothesis_transition_recorded", {"transition_id": "TR-H001-H002", "previous_hypothesis_claim_ref": "C101", "new_hypothesis_claim_ref": "C201", "key_result_refs": ["RES101"], "observation_or_uncertainty_refs": ["E201"]})
    findings = {finding.rule_id for finding in validate_causal_history(ledger)}
    assert "P2-CAUSAL-TRANSITION-FUTURE-CLAIM" in findings
    assert "P2-CAUSAL-TRANSITION-FUTURE-RESULT" in findings
    assert "P2-CAUSAL-TRANSITION-FUTURE-OBSERVATION" in findings


def test_summary_compiler_resolves_its_explicit_decision_reference():
    story = _module("story")
    state = {"hypothesis_layers": {"H002": {"hypothesis_claim_ref": "C201", "problem_ref": "P201"}}, "claims": {"C201": {"falsifiable_predictions": [{"observation_that_falsifies": "falsifier"}], "text": "H02"}}, "problems": {"P201": {}}, "layer_summaries": {"SUM-H002": {"answered": "answered", "hypothesis_status": "supported", "decision_ref": "D002", "remaining_unresolved": "none", "next_question": "next", "next_step_refs": ["NS201"]}}, "decisions": {"D001": {"choice": "No-Go", "rationale": "old"}, "D002": {"choice": "Go", "rationale": "revised"}}}
    body = story.content_from_materialized_state(state, "H002", "layer_summary_decision", "SUM-H002")
    assert "Go: revised" in body and "No-Go" not in body


def test_persisted_state_content_is_immune_to_fixture_mutation(tmp_path: Path):
    from thesis_deck_system.phase2_build import build_phase2, _hydrate_from_state
    from thesis_deck_system.ledger import Ledger
    import json
    import shutil
    import yaml

    build_root = tmp_path / "build"
    result = build_phase2(output_root=build_root)
    source_fixture = ROOT / "thesis-deck-system" / "examples" / "synthetic-project" / "phase2" / "fixture.yaml"
    mutated_fixture_path = tmp_path / "mutated-fixture.yaml"
    shutil.copy2(source_fixture, mutated_fixture_path)
    mutated = yaml.safe_load(mutated_fixture_path.read_text(encoding="utf-8"))
    mutated["hypothesis_layers"][0]["title"] = "MUTATED UNCOMMITTED SOURCE"
    mutated["hypothesis_layers"][0]["research_question"] = "MUTATED QUESTION"
    mutated_fixture_path.write_text(yaml.safe_dump(mutated, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # Rebuild every spec from the persisted, hash-verified ledger.  The
    # mutated seed copy is intentionally not read by this replay path.
    ledger = Ledger.load(build_root / "ledger-events.json")
    persisted_specs = json.loads((build_root / "slide-specs.json").read_text(encoding="utf-8"))
    meeting = json.loads((build_root / "meeting-projection.json").read_text(encoding="utf-8"))
    rebuilt_specs = []
    for spec in persisted_specs:
        state = ledger.materialize(spec["source_cursor"])
        rebuilt_specs.append(_hydrate_from_state(spec, state, build_root, overview=spec["deck_role"] == "meeting_delta", meeting=meeting))

    derived_keys = {"layout_plan_ref", "placement_plan"}
    canonical = lambda spec: {key: value for key, value in spec.items() if key not in derived_keys}
    assert json.dumps([canonical(spec) for spec in rebuilt_specs], sort_keys=True, ensure_ascii=False) == json.dumps([canonical(spec) for spec in persisted_specs], sort_keys=True, ensure_ascii=False)
    assert "MUTATED UNCOMMITTED SOURCE" not in json.dumps(rebuilt_specs, ensure_ascii=False)
    assert "MUTATED QUESTION" not in json.dumps(rebuilt_specs, ensure_ascii=False)
    assert result["h01_cursor"] < result["h02_cursor"]
