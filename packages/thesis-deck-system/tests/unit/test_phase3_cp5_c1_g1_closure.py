"""Cross-gate acceptance proof for the bounded C1–G1 closure sprint."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def test_cross_gate_acceptance_persists_execution_backed_facts(tmp_path: Path):
    from thesis_deck_system.phase3_cp5_c1_g1_closure import write_cross_gate_acceptance

    result = write_cross_gate_acceptance(ROOT, tmp_path)
    payload = json.loads((tmp_path / "checkpoint-c1-g1-cross-gate-acceptance.json").read_text(encoding="utf-8"))
    assert result["cross_gate_status"] == payload["cross_gate_status"] == "pass"
    assert payload["invariant_count"] >= 12
    assert all(item["status"] in {"pass", "blocked"} and item["facts"] for item in payload["invariants"])
