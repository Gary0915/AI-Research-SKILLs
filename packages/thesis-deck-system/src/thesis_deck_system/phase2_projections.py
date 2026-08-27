"""Cursor-materialized Master and Group Meeting projections."""

from __future__ import annotations


def _ordered_layers(state: dict) -> list[dict]:
    return sorted(state.get("hypothesis_layers", {}).values(), key=lambda item: (item.get("source_event_cursor", 0), item.get("hypothesis_layer_id", "")))


def master_projection(state: dict, *, source_cursor: int) -> dict:
    layers = _ordered_layers(state)
    return {
        "projection_kind": "master",
        "source_event_cursor": source_cursor,
        "append_only": True,
        "layers": layers,
        "history_reachable_layer_refs": [layer["hypothesis_layer_id"] for layer in layers],
    }


def meeting_projection(state: dict, *, source_cursor: int, current_layer_id: str) -> dict:
    layers = _ordered_layers(state)
    layer_ids = [layer["hypothesis_layer_id"] for layer in layers]
    if current_layer_id not in layer_ids:
        raise ValueError(f"current hypothesis layer not materialized: {current_layer_id}")
    fishbones = list(state.get("fishbone_revisions", {}).items())
    latest = max(fishbones, key=lambda pair: pair[1].get("revision", 0)) if fishbones else None
    commitments = sorted(
        [item for item in state.get("actions", {}).values() if item.get("status") not in {"done", "cancelled", "superseded"}],
        key=lambda item: item.get("action_item_id", ""),
    )
    return {
        "projection_kind": "meeting",
        "source_event_cursor": source_cursor,
        "current_layer_id": current_layer_id,
        "historical_layer_refs": [layer_id for layer_id in layer_ids if layer_id != current_layer_id],
        "current_layer": state["hypothesis_layers"][current_layer_id],
        "latest_fishbone_ref": None if latest is None else {"fishbone_id": latest[1].get("fishbone_id", latest[0].split("@", 1)[0]), "revision": latest[1]["revision"]},
        "previous_commitments": commitments,
    }
