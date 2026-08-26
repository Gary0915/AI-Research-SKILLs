import json
from pathlib import Path
from thesis_deck_system.build import build, PROJECT, ARTIFACTS
from thesis_deck_system.fixture import load_fixture
from thesis_deck_system.ledger import Ledger
from thesis_deck_system.pptx import audit_pptx

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
    assert specs[1]["content"]["discussion"] != "The gradient supports transport but does not discriminate boundary effects."
