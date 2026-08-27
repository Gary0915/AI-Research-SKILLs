from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path

import pytest

from thesis_deck_system.contracts import SchemaRegistry


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = ROOT / "thesis-deck-system" / "schemas"


PHASE2_SCHEMAS = {
    "hypothesis-layer",
    "problem",
    "fishbone-map",
    "fishbone-revision",
    "layer-discussion",
    "layer-summary",
    "hypothesis-transition",
    "layout-archetype",
    "layout-plan",
}


def _phase2_module(name: str):
    try:
        return importlib.import_module(f"thesis_deck_system.{name}")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Phase 2 module is missing: {exc}")


def test_phase2_schemas_are_registered_draft_2020_12_and_typed():
    registry = SchemaRegistry(SCHEMA_DIR, include_phase2=True)
    assert PHASE2_SCHEMAS <= set(registry.names)
    for name in PHASE2_SCHEMAS:
        schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

        def walk(node, path="$"):
            defects = []
            if isinstance(node, dict):
                if ("pattern" in node or node.get("format") in {"date", "date-time"}) and node.get("type") != "string":
                    defects.append(path)
                for key, value in node.items():
                    defects.extend(walk(value, f"{path}/{key}"))
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    defects.extend(walk(value, f"{path}/{index}"))
            return defects

        assert walk(schema) == []


def test_hypothesis_change_classification_is_explicit_and_non_destructive():
    module = _phase2_module("hypothesis")
    current = {"hypothesis_layer_id": "H001", "revision": 1, "mechanism_key": "bulk_conductivity"}
    same = module.classify_hypothesis_change(current, "bulk_conductivity", requested="same_layer_revision")
    assert same == {"classification": "same_layer_revision", "layer_id": "H001", "next_revision": 2}
    new = module.classify_hypothesis_change(current, "contact_resistance", requested="new_hypothesis_layer")
    assert new["classification"] == "new_hypothesis_layer"
    assert new["layer_id"] == "H002"
    with pytest.raises(ValueError, match="explicit classification"):
        module.classify_hypothesis_change(current, "contact_resistance", requested=None)


def test_history_validator_rejects_future_and_missing_derivation():
    module = _phase2_module("hypothesis")
    h01 = {
        "hypothesis_layer_id": "H001",
        "revision": 1,
        "source_event_cursor": 10,
        "derived_from": None,
        "fishbone_snapshot_ref": {"fishbone_id": "FB001", "revision": 1},
    }
    h02 = {
        "hypothesis_layer_id": "H002",
        "revision": 1,
        "source_event_cursor": 20,
        "derived_from": {"previous_layer_ref": "H001", "decision_refs": ["D101"], "discussion_refs": ["DISC-H001"]},
        "fishbone_snapshot_ref": {"fishbone_id": "FB001", "revision": 2},
    }
    state = {"hypothesis_layers": {"H001": h01, "H002": h02}, "decisions": {"D101": {"source_event_cursor": 12}}, "layer_discussions": {"DISC-H001": {"source_event_cursor": 11}}, "fishbone_revisions": {"FB001@1": {"source_event_cursor": 5}, "FB001@2": {"source_event_cursor": 15}}}
    assert module.validate_hypothesis_history(state) == []
    missing = copy.deepcopy(state)
    missing["hypothesis_layers"]["H002"]["derived_from"] = None
    assert "P2-HISTORY-MISSING-DERIVATION" in {finding.rule_id for finding in module.validate_hypothesis_history(missing)}
    future = copy.deepcopy(state)
    future["decisions"]["D101"]["source_event_cursor"] = 21
    assert "P2-HISTORY-FUTURE-DECISION" in {finding.rule_id for finding in module.validate_hypothesis_history(future)}
