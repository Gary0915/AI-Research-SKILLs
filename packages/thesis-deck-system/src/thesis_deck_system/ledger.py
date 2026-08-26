"""Append-only event ledger with deterministic replay."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


VISIBILITY = {"main", "appendix", "history", "hidden_from_default_view"}
RESEARCH_STATUS = {"active", "resolved", "failed_but_informative", "superseded"}


@dataclass(frozen=True)
class Event:
    cursor: int
    event_type: str
    payload: dict[str, Any]
    timestamp: str
    previous_hash: str | None
    event_hash: str


class Ledger:
    def __init__(self) -> None:
        self._events: list[Event] = []

    @staticmethod
    def _canonical(record: dict[str, Any]) -> str:
        return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def append(self, event_type: str, payload: dict[str, Any]) -> Event:
        if event_type == "story_visibility_changed" and payload.get("story_visibility") not in VISIBILITY:
            raise ValueError("invalid story visibility")
        if event_type == "research_status_changed" and payload.get("research_status") not in RESEARCH_STATUS:
            raise ValueError("invalid research status")
        cursor = len(self._events) + 1
        previous_hash = self._events[-1].event_hash if self._events else None
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        unsigned = {"cursor": cursor, "event_type": event_type, "payload": payload, "timestamp": timestamp, "previous_hash": previous_hash}
        event_hash = hashlib.sha256(self._canonical(unsigned).encode("utf-8")).hexdigest()
        event = Event(cursor, event_type, payload, timestamp, previous_hash, event_hash)
        self._events.append(event)
        return event

    def replay(self) -> list[Event]:
        previous = None
        for expected_cursor, event in enumerate(self._events, 1):
            if event.cursor != expected_cursor or event.previous_hash != previous:
                raise ValueError("ledger cursor/hash chain invalid")
            previous = event.event_hash
        return list(self._events)

    def materialize(self) -> dict[str, Any]:
        state = {"blocks": {}, "claims": {}, "actions": {}, "decisions": {}, "stages": {}, "events": []}
        for event in self.replay():
            state["events"].append(asdict(event))
            payload = event.payload
            if event.event_type == "block_created":
                state["blocks"][payload["block_id"]] = dict(payload)
            elif event.event_type in {"block_revised", "research_status_changed", "story_visibility_changed"}:
                block = state["blocks"].setdefault(payload["block_id"], {})
                if event.event_type == "story_visibility_changed":
                    block.setdefault("story_visibility", {})[payload["deck"]] = payload["story_visibility"]
                else:
                    block.update({k: v for k, v in payload.items() if k != "block_id"})
            elif event.event_type in {"claim_created", "claim_revised", "claim_superseded"}:
                state["claims"][payload["claim_id"]] = dict(payload)
            elif event.event_type in {"action_committed", "action_status_changed", "action_closed"}:
                state["actions"].setdefault(payload["action_item_id"], {}).update(payload)
            elif event.event_type == "decision_recorded":
                state["decisions"][payload["decision_id"]] = dict(payload)
            elif event.event_type == "stage_revised":
                state["stages"][payload["stage_id"]] = dict(payload)
        return state

