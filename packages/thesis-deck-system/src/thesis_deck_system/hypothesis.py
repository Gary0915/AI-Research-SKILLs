"""Hypothesis-layer revision classification and temporal history validation."""

from __future__ import annotations

from .contracts import Finding


def classify_hypothesis_change(current: dict, new_mechanism_key: str, *, requested: str | None) -> dict:
    if requested not in {"same_layer_revision", "new_hypothesis_layer"}:
        raise ValueError("explicit classification is required")
    layer_id = current["hypothesis_layer_id"]
    if requested == "same_layer_revision":
        if current.get("mechanism_key") != new_mechanism_key:
            raise ValueError("same-layer revision cannot change the core mechanism")
        return {"classification": requested, "layer_id": layer_id, "next_revision": current["revision"] + 1}
    number = int(layer_id[1:]) + 1
    return {"classification": requested, "layer_id": f"H{number:03d}", "next_revision": 1, "previous_layer_ref": layer_id}


def validate_hypothesis_history(state: dict) -> list[Finding]:
    findings: list[Finding] = []
    layers = state.get("hypothesis_layers", {})
    ordered = sorted(layers.values(), key=lambda item: item.get("source_event_cursor", 0))
    for index, layer in enumerate(ordered):
        layer_id = layer.get("hypothesis_layer_id", "unknown")
        cursor = layer.get("source_event_cursor", 0)
        derivation = layer.get("derived_from")
        if index and not derivation:
            findings.append(Finding("P2-HISTORY-MISSING-DERIVATION", "scientific_reasoning", f"{layer_id} has no preceding-layer derivation", layer_id))
            continue
        if derivation:
            previous = derivation.get("previous_layer_ref")
            if previous not in layers or layers[previous].get("source_event_cursor", 0) >= cursor:
                findings.append(Finding("P2-HISTORY-PREVIOUS-LAYER-INVALID", "schema_ledger_integrity", f"{layer_id} previous layer is absent or future", layer_id))
            for decision_ref in derivation.get("decision_refs", []):
                decision = state.get("decisions", {}).get(decision_ref)
                if not decision or decision.get("source_event_cursor", 0) >= cursor:
                    findings.append(Finding("P2-HISTORY-FUTURE-DECISION", "schema_ledger_integrity", f"{decision_ref} is absent or future for {layer_id}", layer_id))
            for discussion_ref in derivation.get("discussion_refs", []):
                discussion = state.get("layer_discussions", {}).get(discussion_ref)
                if not discussion or discussion.get("source_event_cursor", 0) >= cursor:
                    findings.append(Finding("P2-HISTORY-FUTURE-DISCUSSION", "schema_ledger_integrity", f"{discussion_ref} is absent or future for {layer_id}", layer_id))
        fishbone_ref = layer.get("fishbone_snapshot_ref", {})
        key = f"{fishbone_ref.get('fishbone_id')}@{fishbone_ref.get('revision')}"
        fishbone = state.get("fishbone_revisions", {}).get(key)
        if not fishbone or fishbone.get("source_event_cursor", 0) > cursor:
            findings.append(Finding("P2-HISTORY-FUTURE-FISHBONE", "schema_ledger_integrity", f"{key} is absent or future for {layer_id}", layer_id))
    return findings
