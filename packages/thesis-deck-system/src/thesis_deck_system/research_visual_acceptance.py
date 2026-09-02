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

_PROFILE_RULES = (
    ("RVA-LANGUAGE-001", "language_policy", "Traditional Chinese carries title and research narrative; English is limited to necessary technical terms.", "source_observed"),
    ("RVA-TYPE-001", "typography", "Slide titles target 28–32 pt.", "source_observed"),
    ("RVA-TYPE-002", "typography", "Main body targets 18–22 pt and never falls below 16 pt.", "source_observed"),
    ("RVA-TYPE-003", "typography", "Captions and citations use 10–12 pt controlled roles.", "source_observed"),
    ("RVA-MESSAGE-001", "main_message", "Each review candidate has one primary message.", "system_calibrated"),
    ("RVA-VISUAL-001", "visual_prominence", "Primary visual dominance is assessed by body family rather than one global ratio.", "source_recurrent"),
    ("RVA-BODY-001", "body_source", "Experiment/result/problem bodies use Group Meeting grammar; literature/system bodies use TSMC/JDP grammar.", "source_recurrent"),
    ("RVA-CAPTION-001", "caption", "Short figure-attached neutral caption strips are preferred.", "source_observed"),
    ("RVA-COMP-001", "comparison", "Comparable variables align horizontally and share one criterion strip.", "source_recurrent"),
    ("RVA-ARROW-001", "arrow", "Major flow is neutral, focus is controlled red, and measurement references are thin/dashed.", "source_observed"),
    ("RVA-ANTI-001", "prohibition", "Dashboard cards, persistent four-box footers, and giant debug labels are prohibited.", "system_calibrated"),
    ("RVA-HISTORY-001", "history", "Visual calibration may not migrate dependency-unchanged historical slides.", "source_observed"),
)

_REVIEW_STRATEGIES = {
    "R04": (("BCF-PROBLEM-TO-SOLUTION", "problem_question_with_mechanism_sidecar"), ("BCF-TECHNOLOGY-COMPARISON", "aligned_alternative_mechanism_comparison")),
    "R05": (("BCF-LITERATURE-VISUAL-MATRIX", "paper_visuals_with_short_takehomes"), ("BCF-TECHNOLOGY-COMPARISON", "precedent_to_gap_comparison")),
    "R08": (("BCF-HARDWARE-DESIGN-PROCEDURE", "large_setup_with_conditions_side_rail"), ("BCF-FEASIBILITY-EVIDENCE-MATRIX", "setup_evidence_matrix_with_parameters")),
    "R11": (("BCF-REAL-RESULT-VALIDATION", "dominant_plot_with_single_decision_sidecar"), ("BCF-PHYSICAL-VALIDATION-MATRIX", "plot_with_setup_and_decision_strip")),
    "R12": (("BCF-PROBLEM-TO-SOLUTION", "causal_path_with_support_visual"), ("BCF-PRINCIPLE-EQUIPMENT-SPLIT", "mechanism_and_measurement_split")),
    "R13": (("BCF-THREE-COLUMN-PHYSICAL-COMPARISON", "aligned_control_treatment_and_shared_criterion"), ("BCF-PHYSICAL-VALIDATION-MATRIX", "paired_validation_visuals_with_plot")),
    "R14": (("BCF-THREE-COLUMN-PHYSICAL-COMPARISON", "decision_tree_with_next_experiment"), ("BCF-HARDWARE-DESIGN-PROCEDURE", "decision_criterion_with_execution_rail")),
}


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


def build_research_presentation_visual_acceptance_profile(root: Path) -> dict[str, Any]:
    """Return the versioned policy used to calibrate real review fixtures."""
    del root  # The policy is controlled, but its evidence IDs remain explicit.
    rules = [
        {"rule_id": rule_id, "category": category, "statement": statement, "evidence_classification": classification}
        for rule_id, category, statement, classification in _PROFILE_RULES
    ]
    counts = {state: sum(rule["evidence_classification"] == state for rule in rules) for state in ("source_observed", "source_recurrent", "system_calibrated", "human_accepted", "insufficient_evidence")}
    return {
        "schema_version": "1.0.0",
        "profile_id": "RPVAP-001",
        "rules": rules,
        "rule_counts": counts,
        "traditional_chinese_primary_language": "pass",
        "title_font_target_pt": {"minimum": 28, "maximum": 32},
        "main_body_font_target_pt": {"minimum": 18, "maximum": 22},
        "main_content_minimum_font_pt": 16,
        "caption_citation_minimum_font_pt": 10,
        "human_visual_acceptance": "not_reviewed",
        "historical_visual_migration_count": 0,
        "aggregate_status": "structural_visual_calibration_complete_pending_human_review",
    }


def build_professor_visual_review_manifest(root: Path) -> dict[str, Any]:
    """Provide stable review-case identities without asserting human selection."""
    fixtures = {item["fixture_id"]: item for item in build_real_research_fixture_pack(root)["fixtures"]}
    cases = []
    for fixture_id, strategies in sorted(_REVIEW_STRATEGIES.items()):
        fixture = fixtures[fixture_id]
        candidates = []
        for index, (family, strategy) in enumerate(strategies, 1):
            core = {"fixture_id": fixture_id, "family": family, "strategy": strategy, "dependency_hash": fixture["dependency_hash"]}
            candidates.append({
                "candidate_id": f"RRVC-{_hash(core)[:16].upper()}",
                "body_family_id": family,
                "composition_strategy": strategy,
                "body_source_class": fixture["body_source_class"],
                "physical_plan_hash": _hash({"core": core, "plan_version": "review_only_v1"}),
                "algorithm_fit": {
                    "semantic_fit": 5,
                    "capacity_fit": 5,
                    "evidence_fit": 5 if fixture["scientific_evidence_status"] == "canonical_supported" else 3,
                    "primary_visual_prominence_fit": 4 + int(index == 1),
                    "text_density_fit": 4,
                    "caption_density_fit": 4,
                    "comparison_alignment_fit": 5 if "comparison" in strategy or fixture_id == "R13" else 3,
                    "technical_evidence_hierarchy_fit": 4,
                },
            })
        candidates = sorted(candidates, key=lambda item: item["candidate_id"])
        selected = max(candidates, key=lambda item: (sum(item["algorithm_fit"].values()), item["candidate_id"]))
        cases.append({
            "logical_slide_id": fixture["logical_slide_id"],
            "fixture_id": fixture_id,
            "scientific_content_dependency_hash": fixture["dependency_hash"],
            "candidate_ids": [item["candidate_id"] for item in candidates],
            "candidates": candidates,
            "selected_by_algorithm_candidate_id": selected["candidate_id"],
            "human_selection": None,
            "human_status": "pending",
            "review_dimensions": ["message_clarity", "figure_prominence", "text_density", "typography", "caption", "technical_density", "group_meeting_tsmc_fit", "overall_preference"],
        })
    return {
        "schema_version": "1.0.0",
        "review_manifest_id": "PVRM-001",
        "cases": cases,
        "pending_human_decision_count": len(cases),
        "aggregate_status": "ready_for_human_visual_acceptance_review",
    }


def write_visual_acceptance_review_artifacts(root: Path, destination: Path | None = None) -> dict[str, Path]:
    """Write only schema-valid policy and pending-review contracts."""
    from .contracts import SchemaRegistry

    root = Path(root).resolve()
    destination = Path(destination or root / "thesis-deck-system/artifacts/phase3")
    destination.mkdir(parents=True, exist_ok=True)
    payloads = {
        "profile": ("research-presentation-visual-acceptance-profile", build_research_presentation_visual_acceptance_profile(root)),
        "manifest": ("professor-visual-review-manifest", build_professor_visual_review_manifest(root)),
    }
    registry = SchemaRegistry(root / "thesis-deck-system/schemas", schema_names=tuple(name for name, _ in payloads.values()))
    outputs = {}
    for key, (schema_name, payload) in payloads.items():
        registry.validate(schema_name, payload)
        path = destination / ("research-presentation-visual-acceptance-profile.json" if key == "profile" else "professor-visual-review-manifest.json")
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        outputs[key] = path
    return outputs
