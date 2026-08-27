from __future__ import annotations

import importlib

import pytest

from thesis_deck_system.ledger import Ledger


def _payload(layer_id: str, cursor: int, fishbone_revision: int, previous: str | None = None) -> dict:
    return {
        "schema_version": "2.0.0", "hypothesis_layer_id": layer_id, "revision": 1,
        "title": layer_id, "source_event_cursor": cursor,
        "derived_from": None if previous is None else {"previous_layer_ref": previous, "discussion_refs": [f"DISC-{previous}"], "decision_refs": ["D101"], "observation_refs": ["E101"]},
        "fishbone_snapshot_ref": {"fishbone_id": "FB001", "revision": fishbone_revision},
    }


def test_phase2_ledger_replays_versioned_fishbone_and_hypothesis_layers():
    ledger = Ledger()
    ledger.append("fishbone_created", {"fishbone_id": "FB001", "revision": 1, "source_event_cursor": 1})
    ledger.append("problem_created", {"problem_id": "P101", "hypothesis_layer_ref": "H001"})
    ledger.append("hypothesis_layer_created", _payload("H001", 3, 1))
    h01_cursor = len(ledger.replay())
    ledger.append("layer_discussion_recorded", {"discussion_id": "DISC-H001", "source_event_cursor": 4})
    ledger.append("decision_recorded", {"decision_id": "D101", "source_event_cursor": 5})
    ledger.append("fishbone_revised", {"fishbone_id": "FB001", "revision": 2, "supersedes_revision": 1, "source_event_cursor": 6})
    ledger.append("hypothesis_transition_recorded", {"transition_id": "TR-H001-H002", "from_layer_ref": "H001", "to_layer_ref": "H002"})
    ledger.append("hypothesis_layer_created", _payload("H002", 8, 2, "H001"))
    state_h01 = ledger.materialize(h01_cursor)
    state_h02 = ledger.materialize()
    assert set(state_h01["hypothesis_layers"]) == {"H001"}
    assert set(state_h01["fishbone_revisions"]) == {"FB001@1"}
    assert set(state_h02["hypothesis_layers"]) == {"H001", "H002"}
    assert set(state_h02["fishbone_revisions"]) == {"FB001@1", "FB001@2"}
    assert state_h02["hypothesis_layers"]["H001"]["fishbone_snapshot_ref"]["revision"] == 1


def test_master_and_meeting_projections_preserve_history_but_focus_current_layer():
    try:
        projections = importlib.import_module("thesis_deck_system.phase2_projections")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Phase 2 projection module is missing: {exc}")
    state = {
        "hypothesis_layers": {"H001": _payload("H001", 3, 1), "H002": _payload("H002", 8, 2, "H001")},
        "actions": {"NS101": {"action_item_id": "NS101", "owner": "Gary", "target_window": {"due": "2026-09-10"}, "status": "in_progress"}},
        "fishbone_revisions": {"FB001@1": {"revision": 1}, "FB001@2": {"revision": 2}},
    }
    master = projections.master_projection(state, source_cursor=8)
    meeting = projections.meeting_projection(state, source_cursor=8, current_layer_id="H002")
    assert [item["hypothesis_layer_id"] for item in master["layers"]] == ["H001", "H002"]
    assert meeting["current_layer_id"] == "H002"
    assert meeting["historical_layer_refs"] == ["H001"]
    assert meeting["latest_fishbone_ref"] == {"fishbone_id": "FB001", "revision": 2}
    assert meeting["previous_commitments"][0]["action_item_id"] == "NS101"
