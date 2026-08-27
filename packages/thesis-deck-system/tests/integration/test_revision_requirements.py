import json
from pathlib import Path
from thesis_deck_system.build import build, PROJECT, ARTIFACTS
from thesis_deck_system.fixture import load_fixture
from thesis_deck_system.ledger import Ledger
from thesis_deck_system.pptx import audit_pptx
from thesis_deck_system.contracts import SchemaRegistry

def test_committed_bundle_persisted_replay_and_bindings():
    build()
    bundle=load_fixture(PROJECT)
    assert len(bundle["stages"]) == 8 and len(bundle["evidence_cards"]) >= 3
    ledger=Ledger.load(ARTIFACTS/"ledger-events.json")
    state=ledger.materialize()
    assert len(ledger.replay()) >= 13 and state["stages"]["ST-DISC"]["revision"] == 2
    specs=json.loads((ARTIFACTS/"slide-specs-revised.json").read_text(encoding="utf-8"))
    manifest=json.loads((ARTIFACTS/"MASTER-PHASE1-REVISED.manifest.json").read_text(encoding="utf-8"))
    assert [s["ordinal"] for s in manifest["slides"]] == [1,2]
    assert all(s["slide_spec_path"].startswith("thesis-deck-system/") for s in manifest["slides"])
    audit=audit_pptx(ARTIFACTS/"master_revised_build.pptx")
    assert audit["content_types_present"] and audit["unique_slide_ids"] and audit["vector_media_used"]
    assert audit["result_slide_svg_relationship"][0]["referenced_in_slide"] is True
    assert specs[0]["bindings"]["asset_refs"] == ["A002"] and specs[0]["bindings"]["evidence_refs"] == ["E002"]
    registry=SchemaRegistry(PROJECT.parents[1]/"schemas")
    assert not registry.errors("slide-spec",specs[0])
    assert not registry.errors("deck-manifest",manifest)
    for name in ("A001.asset.json","A002.asset.json"):
        assert not registry.errors("asset-manifest",json.loads((ARTIFACTS/"plots"/name).read_text(encoding="utf-8")))
    delta=json.loads((ARTIFACTS/"meeting-delta.json").read_text(encoding="utf-8"))
    assert "B001" in delta["changed_block_ids"]
    assert specs[1]["content"]["discussion"] != "The gradient supports transport but does not discriminate boundary effects."
