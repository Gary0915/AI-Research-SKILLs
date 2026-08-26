from thesis_deck_system.ledger import Ledger


def test_append_replay_hashes_and_monotonic_cursor():
    ledger = Ledger()
    first = ledger.append("block_created", {"block_id": "B001", "revision": 1})
    second = ledger.append("research_status_changed", {"block_id": "B001", "research_status": "failed_but_informative"})
    assert (first.cursor, second.cursor) == (1, 2)
    assert first.event_hash and second.previous_hash == first.event_hash
    assert ledger.replay() == [first, second]


def test_replay_preserves_independent_status_visibility_and_actions():
    ledger = Ledger()
    ledger.append("block_created", {"block_id": "B001", "revision": 1, "research_status": "active", "story_visibility": {"master": "main"}})
    ledger.append("research_status_changed", {"block_id": "B001", "research_status": "failed_but_informative"})
    ledger.append("story_visibility_changed", {"block_id": "B001", "deck": "meeting", "story_visibility": "history"})
    ledger.append("action_committed", {"action_item_id": "NS001", "status": "planned", "owner": "researcher"})
    state = ledger.materialize()
    assert state["blocks"]["B001"]["research_status"] == "failed_but_informative"
    assert state["blocks"]["B001"]["story_visibility"]["meeting"] == "history"
    assert state["actions"]["NS001"]["status"] == "planned"


def test_illegal_visibility_value_is_rejected():
    ledger = Ledger()
    ledger.append("block_created", {"block_id": "B001", "revision": 1, "research_status": "active"})
    try:
        ledger.append("story_visibility_changed", {"block_id": "B001", "deck": "meeting", "story_visibility": "archived_from_main_story"})
    except ValueError as error:
        assert "visibility" in str(error)
    else:
        raise AssertionError("illegal visibility transition accepted")
