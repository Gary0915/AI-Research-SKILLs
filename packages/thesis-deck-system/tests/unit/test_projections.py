from thesis_deck_system.projections import meeting_delta


def test_meeting_delta_carries_unfinished_commitment_and_parallel_work():
    events = [
        {"cursor": 1, "event_type": "action_committed", "payload": {"action_item_id": "NS001", "status": "planned", "owner": "researcher", "target_window": "2026-09-02", "source_decision_ref": "D001", "parallelizable": True, "workstream": "microscopy"}},
        {"cursor": 2, "event_type": "stage_revised", "payload": {"block_id": "B001", "revision": 2}},
    ]
    result = meeting_delta(events, since_cursor=1)
    assert result["prior_commitment_ids"] == ["NS001"]
    assert result["included_action_ids"] == ["NS001"]
    assert result["actions"][0]["owner"] == "researcher"
    assert result["actions"][0]["parallelizable"] is True
