"""Synthetic, privacy-safe incremental research-deck lineage contracts."""

from __future__ import annotations

from pathlib import Path

from thesis_deck_system.incremental_deck_lineage import (
    IncrementalLineageError,
    build_meeting_view,
    decide_materialization,
    insert_after_semantic_parent,
    validate_atomic_dependency_generation,
)


def _lineage(slide_id: str, *, parent: str | None = None, policy: str = "historical_stable", dependency: str = "a" * 64) -> dict[str, object]:
    return {
        "slide_id": slide_id,
        "topic_id": "TOPIC-H001",
        "semantic_parent_id": parent,
        "source_cursor": 1,
        "lifecycle_policy": policy,
        "dependency_hash": dependency,
        "composition_family": "BCF-REAL-RESULT-VALIDATION",
        "body_reference_evidence_ids": ["JDP-TSMC-2026-0814-P10"],
        "artifact_hash": "b" * 64,
        "accepted_revision": 1,
    }


def test_unchanged_historical_slide_reuses_and_new_result_is_inserted_after_semantic_parent():
    previous = _lineage("S-EXP-001")
    unchanged = _lineage("S-EXP-001")
    new_result = _lineage("S-RES-001", parent="S-EXP-001", policy="append_after_semantic_parent")

    reused = decide_materialization(previous, unchanged)
    appended = decide_materialization(None, new_result)
    ordered = insert_after_semantic_parent([previous], [new_result])

    assert reused["decision"] == "reuse_exact"
    assert appended["decision"] == "append_new"
    assert [item["slide_id"] for item in ordered] == ["S-EXP-001", "S-RES-001"]


def test_versioned_snapshot_preserves_old_revision_and_dependency_change_rebuilds_atomically():
    previous = _lineage("S-FB-001", policy="versioned_snapshot", dependency="a" * 64)
    snapshot = _lineage("S-FB-001", policy="versioned_snapshot", dependency="c" * 64)
    decision = decide_materialization(previous, snapshot)
    assert decision["decision"] == "new_revision"
    assert decision["output_slide_id"] != "S-FB-001"

    with __import__("pytest").raises(IncrementalLineageError):
        validate_atomic_dependency_generation({"title": "a" * 64, "figure": "c" * 64})


def test_meeting_view_omits_without_deleting_canonical_history_and_new_reference_does_not_rebuild():
    canonical = [_lineage("S-CONTEXT"), _lineage("S-RESULT", parent="S-CONTEXT", policy="append_after_semantic_parent")]
    view = build_meeting_view(canonical, selected_slide_ids=["S-RESULT"])
    assert view["selected_slide_ids"] == ["S-RESULT"]
    assert view["excluded_slide_ids"] == ["S-CONTEXT"]
    assert decide_materialization(canonical[0], canonical[0], body_reference_changed=True)["decision"] == "reuse_exact"


def test_lineage_contracts_are_registered_and_closed():
    from pathlib import Path

    from thesis_deck_system.contracts import SchemaRegistry

    root = Path(__file__).resolve().parents[4]
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5hi=True)
    record = _lineage("S-001")
    assert registry.errors("slide-lineage-record", record) == []
    assert registry.errors("slide-lineage-record", record | {"unexpected": True})


def test_current_acceptance_story_projects_closed_lineage_without_shell_override():
    from pathlib import Path

    from thesis_deck_system.incremental_deck_lineage import build_current_acceptance_lineage
    from thesis_deck_system.phase3_final_visual_composition import build_final_composition_plan, build_final_projection

    root = Path(__file__).resolve().parents[4]
    plan = build_final_composition_plan(root, build_final_projection(root))
    artifacts = build_current_acceptance_lineage(plan)
    assert len(artifacts["research_deck_lineage"]) == 20
    assert artifacts["incremental_build_audit"]["stale_mixed_generation_slide_count"] == 0
    assert artifacts["body_reference_evidence_resolution"]["shell_override_by_body_reference"] is False
    assert {item["priority_decision"] for item in artifacts["body_reference_evidence_resolution"]["resolutions"]} == {"not_applied_historical_stable"}


def test_incremental_lineage_acceptance_proof_executes_all_authorized_scenarios():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.incremental_deck_lineage import build_incremental_lineage_acceptance_proof

    proof = build_incremental_lineage_acceptance_proof()

    assert proof["aggregate_status"] == "pass"
    assert [item["scenario_id"] for item in proof["scenarios"]] == [f"IDL-{letter}" for letter in "ABCDEFGH"]
    assert proof["decision_counts"] == {
        "reuse_exact": 4,
        "append_new": 5,
        "new_revision": 2,
        "rebuild_dependency_changed": 1,
        "exclude_from_meeting_view_only": 1,
    }
    assert proof["stale_mixed_generation_rejection_count"] == 1
    assert proof["shell_override_by_body_reference_count"] == 0
    registry = SchemaRegistry(Path(__file__).resolve().parents[4] / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5hi=True)
    assert registry.errors("incremental-lineage-acceptance-proof", proof) == []
    assert registry.errors("incremental-lineage-acceptance-proof", proof | {"unexpected": True})
