"""Source-closed real-research fixtures for human visual acceptance review.

This module deliberately produces review-only content descriptors.  It does
not change canonical science, historical slides, or a production deck.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any


class ResearchVisualAcceptanceError(ValueError):
    """Raised when a review fixture cannot be bound to canonical content."""


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


_FIXTURE_SPECS = (
    ("R01", "論文研究目標", "S-H002-HYPOTHESIS-TITLE-01", "tsmc_dominant", "以控制接觸壓力辨識低壓下訊號不穩定的主導機制。", "canonical_supported", ()),
    ("R02", "研究系統架構", "S-H002-OBSERVATION-PROBLEM-04", "tsmc_dominant", "由水凝膠元件、接觸介面與電性量測鏈共同檢驗訊號穩定性。", "canonical_supported", ()),
    ("R03", "研究傳承與目前定位", "S-PHASE2-PROGRESS-01", "historical_reuse", "目前工作承接 H002：先驗證接觸電阻，再決定後續實驗。", "canonical_supported", ()),
    ("R04", "研究缺口", "S-H002-PROBLEM-DEFINITION-02", "tsmc_dominant", "低接觸壓力下，contact resistance 是否主導訊號不穩定仍待控制比較。", "canonical_supported", ()),
    ("R05", "文獻證據：自發感測前例", "S-H001-LITERATURE-MECHANISM-05", "tsmc_dominant", "文獻指出 transport gradient 可產生位置效應；接觸介面仍是替代解釋。", "canonical_supported", ()),
    ("R06", "文獻綜整至主要機制", "S-H002-OBSERVATION-PROBLEM-04", "tsmc_dominant", "以匹配導電度並改變接觸壓力，隔離 contact resistance 的機制貢獻。", "canonical_supported", ()),
    ("R07", "研究魚骨：目前分支位置", "S-H002-FISHBONE-LOCATOR-03", "group_meeting_dominant", "保留 FB001 rev2 歷史結構，僅標示目前接觸介面分支。", "canonical_supported", ()),
    ("R08", "G02 優先實驗：接觸壓力量測", "S-H002-EXPERIMENT-DESIGN-06", "group_meeting_dominant", "在匹配導電度條件下改變接觸壓力，量測訊號 CV 與接觸電阻。", "canonical_supported", ()),
    ("R09", "量測架構：電性量測鏈", "S-H002-EXPERIMENT-DESIGN-06", "group_meeting_dominant", "以量測儀器、樣品接觸點與資料記錄鏈路對應每一個控制變因。", "canonical_supported", ()),
    ("R10", "實驗設計與 Go / No-Go", "S-H002-EXPERIMENT-DESIGN-06", "group_meeting_dominant", "若控制比較後訊號 CV 跨過決策門檻，才進入下一輪驗證。", "canonical_supported", ()),
    ("R11", "結果與討論版面示意", "S-H002-EXPERIMENT-DESIGN-06", "group_meeting_dominant", "預期版面示意，不代表實驗結果；主圖保留給未來量測結果。", "synthetic_non_evidence", ("visual_layout_fixture",)),
    ("R12", "問題至機制至解法", "S-H002-OBSERVATION-PROBLEM-04", "group_meeting_dominant", "問題：低壓接觸不穩；機制：contact resistance；策略：匹配導電度並改變壓力。", "canonical_supported", ()),
    ("R13", "物理驗證與比較", "S-H002-EXPERIMENT-DESIGN-06", "group_meeting_dominant", "以相同位置與相同判準水平對齊 control / treatment 的比較結果。", "canonical_supported", ()),
    ("R14", "決策與下一步", "S-H002-LAYER-SUMMARY-DECISION-09", "group_meeting_dominant", "依控制比較結果決定是否保留接觸介面假說，並安排下一步驗證。", "canonical_supported", ()),
)


def build_real_research_fixture_pack(root: Path) -> dict[str, Any]:
    """Create the review-only fixture descriptors from tracked slide specs."""
    root = Path(root).resolve()
    source_path = root / "thesis-deck-system/artifacts/phase2/slide-specs.json"
    try:
        source_records = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchVisualAcceptanceError("canonical slide specs are unavailable") from exc
    by_slide = {item["slide_id"]: item for item in source_records}
    fixtures = []
    for fixture_id, title, source_slide_id, body_source_class, visible_text, evidence_status, synthetic_roles in _FIXTURE_SPECS:
        source = by_slide.get(source_slide_id)
        if source is None:
            raise ResearchVisualAcceptanceError(f"fixture source is missing: {source_slide_id}")
        source_refs = {
            "slide_spec_id": source_slide_id,
            "claim_refs": list(source["bindings"]["claim_refs"]),
            "evidence_refs": list(source["bindings"]["evidence_refs"]),
            "asset_refs": list(source["bindings"]["asset_refs"]),
            "action_refs": list(source["bindings"]["action_refs"]),
            "decision_refs": list(source["bindings"]["decision_refs"]),
            "source_cursor": source["source_cursor"],
        }
        dependency_hash = _hash({"source_refs": source_refs, "source_content": source["content"]["semantic_fields"]})
        fixtures.append({
            "fixture_id": fixture_id,
            "logical_slide_id": f"RRVA-{fixture_id}",
            "title": title,
            "visible_text": visible_text,
            "traditional_chinese_primary": True,
            "body_source_class": body_source_class,
            "canonical_source_refs": source_refs,
            "dependency_hash": dependency_hash,
            "scientific_evidence_status": evidence_status,
            "source_only_role_indicators": list(synthetic_roles),
            "human_visual_acceptance": "not_reviewed",
        })
    return {
        "schema_version": "1.0.0",
        "fixture_pack_id": "RRVFP-001",
        "fixtures": fixtures,
        "logical_fixture_count": len(fixtures),
        "invented_scientific_claim_count": 0,
        "invented_measured_value_count": 0,
        "traditional_chinese_primary": True,
        "historical_visual_migration_count": 0,
        "aggregate_status": "source_closed_review_fixture_pack",
    }


def write_real_research_fixture_pack(root: Path, destination: Path | None = None) -> Path:
    """Persist the review-only fixture contract after closed-schema validation."""
    from .contracts import SchemaRegistry

    root = Path(root).resolve()
    destination = Path(destination or root / "thesis-deck-system/artifacts/phase3")
    destination.mkdir(parents=True, exist_ok=True)
    payload = build_real_research_fixture_pack(root)
    SchemaRegistry(root / "thesis-deck-system/schemas", schema_names=("real-research-visual-fixture-pack",)).validate(
        "real-research-visual-fixture-pack", payload
    )
    path = destination / "real-research-visual-fixture-pack.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
