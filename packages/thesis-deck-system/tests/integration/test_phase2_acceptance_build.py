from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from thesis_deck_system.ledger import Ledger
from thesis_deck_system.contracts import SchemaRegistry


ROOT = Path(__file__).resolve().parents[4]


def test_phase2_acceptance_build_is_cursor_aware_and_reviewable(tmp_path: Path):
    try:
        phase2_build = importlib.import_module("thesis_deck_system.phase2_build")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Phase 2 build module is missing: {exc}")
    result = phase2_build.build_phase2(output_root=tmp_path)
    expected = [
        "ledger-events.json", "materialized-h01.json", "materialized-h02.json",
        "slide-specs.json", "layout-plans.json", "MASTER-PHASE2.manifest.json",
        "meeting-projection.json", "fishbone/FB001-rev1.svg", "fishbone/FB001-rev2.svg",
        "acceptance-deck.pptx", "structural-audit.json", "professor-qa.json",
        "scientific-provenance-qa.json", "evidence-causal-role-qa.json",
        "h003-generic-professor-qa-fixture.json", "private-fixture-status.json",
    ]
    assert all((tmp_path / path).is_file() for path in expected)
    ledger = Ledger.load(tmp_path / "ledger-events.json")
    h01 = json.loads((tmp_path / "materialized-h01.json").read_text(encoding="utf-8"))
    h02 = json.loads((tmp_path / "materialized-h02.json").read_text(encoding="utf-8"))
    assert ledger.materialize(result["h01_cursor"]) == h01
    assert ledger.materialize(result["h02_cursor"]) == h02
    assert set(h01["hypothesis_layers"]) == {"H001"}
    assert set(h02["hypothesis_layers"]) == {"H001", "H002"}
    assert h02["hypothesis_layers"]["H001"]["fishbone_snapshot_ref"]["revision"] == 1
    assert h02["hypothesis_layers"]["H002"]["fishbone_snapshot_ref"]["revision"] == 2

    specs = json.loads((tmp_path / "slide-specs.json").read_text(encoding="utf-8"))
    # H01's two experiment matrices are now a real governed split rather
    # than a self-approved one-page override.
    assert len(specs) == 19
    h01_specs = [spec for spec in specs if spec.get("hypothesis_layer_ref") == "H001"]
    h02_specs = [spec for spec in specs if spec.get("hypothesis_layer_ref") == "H002"]
    assert h01_specs[0]["semantic_role"] == "hypothesis_title"
    assert h01_specs[1]["semantic_role"] == "problem_definition"
    assert h01_specs[2]["semantic_role"] == "fishbone_locator"
    assert h02_specs[0]["semantic_role"] == "hypothesis_title"
    assert h02_specs[1]["semantic_role"] == "problem_definition"
    assert h02_specs[2]["semantic_role"] == "fishbone_locator"
    transition_spec = next(spec for spec in h01_specs if spec["semantic_role"] == "hypothesis_transition")
    assert transition_spec["source_cursor"] > result["h01_cursor"]
    assert all(spec["source_cursor"] == result["h01_cursor"] for spec in h01_specs if spec is not transition_spec)
    assert all(spec["source_cursor"] == result["h02_cursor"] for spec in h02_specs)

    audit = json.loads((tmp_path / "structural-audit.json").read_text(encoding="utf-8"))
    generated = {item["slide_spec_id"]: item for item in audit["generated_slides"]}
    h01_fishbone = next(spec for spec in h01_specs if spec["semantic_role"] == "fishbone_locator")
    h02_fishbone = next(spec for spec in h02_specs if spec["semantic_role"] == "fishbone_locator")
    assert generated[h01_fishbone["slide_id"]]["svg_asset_relationships"][0]["asset_id"] == "A101"
    assert generated[h02_fishbone["slide_id"]]["svg_asset_relationships"][0]["asset_id"] == "A102"
    assert not audit["orphan_parts"]
    assert audit["source_template_unchanged"] is True

    private = json.loads((tmp_path / "private-fixture-status.json").read_text(encoding="utf-8"))
    assert private["mode"] == "blocked_fixture"
    assert json.loads((tmp_path / "evidence-causal-role-qa.json").read_text(encoding="utf-8"))["status"] == "pass"
    assert json.loads((tmp_path / "h003-generic-professor-qa-fixture.json").read_text(encoding="utf-8"))["status"] == "pass"

    registry = SchemaRegistry(ROOT / "thesis-deck-system/schemas", include_phase2=True)
    assert all(not registry.errors("slide-spec", spec) for spec in specs)
    manifest = json.loads((tmp_path / "MASTER-PHASE2.manifest.json").read_text(encoding="utf-8"))
    profile = json.loads((tmp_path / "template-profile.json").read_text(encoding="utf-8"))
    plans = json.loads((tmp_path / "layout-plans.json").read_text(encoding="utf-8"))
    assert not registry.errors("deck-manifest", manifest)
    assert not registry.errors("template-profile", profile)
    assert all(not registry.errors("layout-plan", plan) for plan in plans)

    forbidden = ("D:/", "C:/", "C:\\\\", "D:\\\\", "\\\\\\\\")
    for path in tmp_path.rglob("*"):
        if path.suffix.lower() in {".json", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            assert not any(marker in text for marker in forbidden), path
