"""Cross-gate acceptance proof for the bounded C1–G1 closure sprint."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def test_cross_gate_acceptance_persists_execution_backed_facts(tmp_path: Path):
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5_c1_g1_closure import write_cross_gate_acceptance

    result = write_cross_gate_acceptance(ROOT, tmp_path)
    payload = json.loads((tmp_path / "checkpoint-c1-g1-cross-gate-acceptance.json").read_text(encoding="utf-8"))
    assert result["cross_gate_status"] == payload["cross_gate_status"] == "pass"
    assert payload["invariant_count"] >= 12
    assert all(item["status"] in {"pass", "blocked"} and item["facts"] for item in payload["invariants"])
    fabrication = next(item for item in payload["invariants"] if item["invariant_id"] == "D1-FABRICATION-CONDITION-CONTRACT")
    assert fabrication["status"] == "pass"
    assert fabrication["facts"] == {
        "known_condition_preserved": True,
        "unknown_condition_preserved": True,
        "invalid_temperature_rejected": True,
        "implicit_coercion": False,
        "invented_condition_count": 0,
        "representative_fixture": "pass",
        "stress_fixture": "pass",
    }
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    assert registry.errors("checkpoint-c1-g1-cross-gate-acceptance", payload) == []


def test_cross_gate_candidate_hash_is_deterministic_and_binds_declared_components(tmp_path: Path):
    from thesis_deck_system.phase3_cp5_c1_g1_closure import candidate_state_hash

    first = candidate_state_hash(ROOT)
    second = candidate_state_hash(ROOT)
    assert first == second
    assert len(first["component_hashes"]) >= 20
    assert all(len(value) == 64 for value in first["component_hashes"].values())
    assert len(first["candidate_state_sha256"]) == 64


def test_cross_gate_candidate_component_hash_is_checkout_line_ending_invariant(tmp_path: Path):
    from thesis_deck_system.phase3_cp5_c1_g1_closure import _candidate_component_sha256

    component = tmp_path / "candidate.py"
    component.write_bytes(b"first\r\nsecond\r\n")
    crlf_hash = _candidate_component_sha256(component)
    component.write_bytes(b"first\nsecond\n")
    assert _candidate_component_sha256(component) == crlf_hash
