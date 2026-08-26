"""Deterministic projections over ledger events."""

from __future__ import annotations

from typing import Any


def meeting_delta(events: list[dict[str, Any]], since_cursor: int) -> dict[str, Any]:
    actions: dict[str, dict[str, Any]] = {}
    changed_blocks: list[str] = []
    for event in events:
        payload = event.get("payload", {})
        if event.get("event_type") in {"action_committed", "action_status_changed", "action_closed"}:
            actions.setdefault(payload["action_item_id"], {}).update(payload)
        if event.get("event_type") in {"block_created", "block_revised", "stage_revised"} and event.get("cursor", 0) > since_cursor:
            block_id = payload.get("block_id")
            if block_id and block_id not in changed_blocks:
                changed_blocks.append(block_id)
    carried = [action for action in actions.values() if action.get("status") not in {"done", "cancelled", "superseded"}]
    carried.sort(key=lambda item: item["action_item_id"])
    return {
        "since_cursor": since_cursor,
        "prior_commitment_ids": [item["action_item_id"] for item in carried],
        "included_action_ids": [item["action_item_id"] for item in carried],
        "actions": carried,
        "changed_block_ids": changed_blocks,
    }

