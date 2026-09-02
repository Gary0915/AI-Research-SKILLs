"""Real-research visual-acceptance fixtures are source-closed and non-inventive."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_real_research_fixture_pack_is_source_closed_chinese_primary_and_non_inventive():
    from thesis_deck_system.research_visual_acceptance import build_real_research_fixture_pack

    pack = build_real_research_fixture_pack(ROOT)

    assert pack["fixture_pack_id"] == "RRVFP-001"
    assert len(pack["fixtures"]) >= 14
    assert {item["fixture_id"] for item in pack["fixtures"]} >= {
        "R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R14",
    }
    assert all(item["canonical_source_refs"] for item in pack["fixtures"])
    assert all(len(item["dependency_hash"]) == 64 for item in pack["fixtures"])
    assert all(item["traditional_chinese_primary"] is True for item in pack["fixtures"])
    assert pack["invented_scientific_claim_count"] == 0
    assert pack["invented_measured_value_count"] == 0


def test_real_result_fixture_marks_layout_only_plot_as_synthetic_non_evidence():
    from thesis_deck_system.research_visual_acceptance import build_real_research_fixture_pack

    result = next(item for item in build_real_research_fixture_pack(ROOT)["fixtures"] if item["fixture_id"] == "R11")

    assert result["scientific_evidence_status"] == "synthetic_non_evidence"
    assert "不代表實驗結果" in result["visible_text"]
    assert result["source_only_role_indicators"] == ["visual_layout_fixture"]


def test_fixture_writer_persists_schema_valid_source_closed_artifact(tmp_path: Path):
    import json

    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.research_visual_acceptance import write_real_research_fixture_pack

    path = write_real_research_fixture_pack(ROOT, tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    SchemaRegistry(ROOT / "thesis-deck-system/schemas", schema_names=("real-research-visual-fixture-pack",)).validate(
        "real-research-visual-fixture-pack", payload
    )
    assert payload["aggregate_status"] == "source_closed_review_fixture_pack"
