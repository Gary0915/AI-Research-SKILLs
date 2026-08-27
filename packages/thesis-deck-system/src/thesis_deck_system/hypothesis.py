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


def validate_causal_history(ledger_or_events) -> list[Finding]:
    """Validate the causal ordering of persisted Phase 2 events.

    This check deliberately consumes replayed ledger events, rather than the
    fixture or a final materialization, so a future reference cannot be hidden
    by a later overwrite.
    """
    events = ledger_or_events.replay() if hasattr(ledger_or_events, "replay") else list(ledger_or_events)
    findings: list[Finding] = []
    by_key: dict[tuple[str, str], int] = {}
    by_type: dict[str, list[int]] = {}
    for event in events:
        by_type.setdefault(event.event_type, []).append(event.cursor)
        payload = event.payload
        for key in ("stage_id", "result_id", "claim_id", "evidence_id", "action_item_id", "decision_id", "discussion_id", "summary_id", "transition_id", "hypothesis_layer_id", "block_id"):
            if payload.get(key):
                by_key[(key, str(payload[key]))] = event.cursor
        if event.event_type == "stage_revised" and str(payload.get("stage_id", "")).startswith("ST-RES"):
            by_key[("result_id", str(payload["stage_id"])[3:])] = event.cursor

    def cursor(kind: str, identifier: str) -> int | None:
        return by_key.get((kind, str(identifier)))

    def require_before(ref_kind: str, ref: str, target: int, rule: str, message: str) -> None:
        value = cursor(ref_kind, ref)
        if value is None or value >= target:
            findings.append(Finding(rule, "scientific_reasoning", message, str(ref)))

    stage_payloads = {payload.get("stage_id"): payload for event in events for payload in [event.payload] if event.event_type == "stage_revised"}
    for event in events:
        payload = event.payload
        if event.event_type == "layer_discussion_recorded":
            for result_ref in payload.get("supporting_results", []) + payload.get("contradicting_results", []) + payload.get("non_discriminating_results", []):
                require_before("result_id", result_ref, event.cursor, "P2-CAUSAL-DISCUSSION-BEFORE-RESULT", "Discussion references a result appended at or after the discussion")
        elif event.event_type == "decision_recorded":
            for subject in payload.get("subject_refs", []):
                if str(subject).startswith("ST-"):
                    require_before("stage_id", subject, event.cursor, "P2-CAUSAL-DECISION-BEFORE-DISCUSSION", "Decision subject stage is not available before the decision")
                elif str(subject).startswith("DISC-"):
                    require_before("discussion_id", subject, event.cursor, "P2-CAUSAL-DECISION-BEFORE-DISCUSSION", "Decision cites a future discussion")
        elif event.event_type == "layer_summary_recorded":
            decision_ref = payload.get("decision_ref")
            if decision_ref:
                require_before("decision_id", decision_ref, event.cursor, "P2-CAUSAL-SUMMARY-BEFORE-DECISION", "Summary cites a decision appended at or after the summary")
            layer_id = payload.get("hypothesis_layer_ref")
            discussion = next((e for e in events if e.event_type == "layer_discussion_recorded" and e.payload.get("hypothesis_layer_ref") == layer_id), None)
            if discussion is None or discussion.cursor >= event.cursor:
                findings.append(Finding("P2-CAUSAL-SUMMARY-BEFORE-DISCUSSION", "scientific_reasoning", "Summary is not after its layer discussion", str(payload.get("summary_id"))))
        elif event.event_type == "hypothesis_transition_recorded":
            for result_ref in payload.get("key_result_refs", []):
                require_before("result_id", result_ref, event.cursor, "P2-CAUSAL-TRANSITION-FUTURE-RESULT", "Transition references a future result")
            for claim_ref in [payload.get("previous_hypothesis_claim_ref"), payload.get("new_hypothesis_claim_ref")]:
                if claim_ref:
                    require_before("claim_id", claim_ref, event.cursor, "P2-CAUSAL-TRANSITION-FUTURE-CLAIM", "Transition references a future Claim")
            for evidence_ref in payload.get("observation_or_uncertainty_refs", []):
                require_before("evidence_id", evidence_ref, event.cursor, "P2-CAUSAL-TRANSITION-FUTURE-OBSERVATION", "Transition references a future observation/evidence")
            for decision_ref in payload.get("decision_refs", []):
                require_before("decision_id", decision_ref, event.cursor, "P2-CAUSAL-TRANSITION-FUTURE-DECISION", "Transition references a future decision")
        elif event.event_type in {"hypothesis_layer_created", "hypothesis_layer_revised"}:
            transition_ref = payload.get("transition_ref")
            if transition_ref:
                require_before("transition_id", transition_ref, event.cursor, "P2-CAUSAL-LAYER-FUTURE-TRANSITION", "Hypothesis Layer binds a transition that is not yet materialized")
    # Every Result must be downstream of its experiment stage when both are
    # declared in the same block.
    for event in events:
        if event.event_type != "stage_revised" or event.payload.get("stage_type") != "result":
            continue
        block_id = event.payload.get("block_ref", {}).get("block_id")
        experiment_events = [e for e in events if e.event_type == "stage_revised" and e.payload.get("stage_type") == "experiment" and e.payload.get("block_ref", {}).get("block_id") == block_id]
        if not experiment_events or max(e.cursor for e in experiment_events) >= event.cursor:
            findings.append(Finding("P2-CAUSAL-RESULT-BEFORE-EXPERIMENT", "scientific_reasoning", "Result is not appended after experiment metadata", str(event.payload.get("stage_id"))))
    return findings
