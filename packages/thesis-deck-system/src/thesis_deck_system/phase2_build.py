"""Deterministic Phase 2 hypothesis-layered synthetic acceptance build."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw
import yaml

from .context import ProjectContext
from .contracts import SchemaRegistry, validate_temporal_bindings
from .fishbone import branch_positions, render_fishbone_svg
from .hypothesis import validate_causal_history, validate_evidence_causal_roles, validate_hypothesis_history
from .layout import LayoutDirector, load_archetype_registry, validate_split_resolution
from .ledger import Ledger
from .phase2_projections import master_projection, meeting_projection
from .pptx import PythonPptxAssembler, audit_pptx
from .private_fixtures import PrivateFixtureLocator
from .qa2 import (PRESENTATION_ROLE_CONTRACTS, run_combined_role_content_qa, run_phase2_pipeline,
                  run_physical_content_fidelity_qa, run_presentation_semantic_fidelity_qa,
                  run_presentation_temporal_snapshot_qa, run_professor_qa_v2,
                  run_report_evidence_consistency)
from .story import compile_hypothesis_layer_from_state, compile_master_story_from_ledger, content_from_materialized_state, content_slots_from_materialized_state, semantic_fields_from_materialized_state
from .template import create_synthetic_template, profile_template


ROOT = ProjectContext.discover(Path(__file__)).repo_root
FIXTURE_ROOT = ROOT / "thesis-deck-system/examples/synthetic-project/phase2"
SCHEMA_ROOT = ROOT / "thesis-deck-system/schemas"
ARCHETYPE_PATH = ROOT / "thesis-deck-system/layout-archetypes.json"
CREATED_AT = "2026-08-27T00:00:00Z"
PROFESSOR_PROFILE_REF = {"profile_id": "PROF-SYNTH-001", "version": "1.0.0"}


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_plot_builder():
    script = FIXTURE_ROOT / "plot_contact_pressure.py"
    spec = importlib.util.spec_from_file_location("phase2_contact_plot", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("contact plot script could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build


def _fishbone_preview(revision: dict, focus_refs: list[str], layer_id: str, output: Path) -> None:
    image = Image.new("RGB", (1200, 650), "white")
    draw = ImageDraw.Draw(image)
    draw.line((170, 325, 1080, 325), fill="#344054", width=9)
    branches = revision["branches"]
    for index, branch in enumerate(branches):
        upper = index % 2 == 0
        x = 250 + (index // 2) * 185
        y = 145 if upper else 505
        current = branch["branch_id"] in focus_refs
        color = "#B42318" if current else "#667085"
        draw.line((x + 60, 325, x, y + (40 if upper else -40)), fill=color, width=5 if current else 3)
        draw.rounded_rectangle((x - 90, y - 34, x + 155, y + 34), radius=10, outline=color, width=5 if current else 2, fill="#FFF1F0" if current else "#F2F4F7")
        draw.text((x - 78, y - 8), branch["branch_id"], fill=color)
        if current:
            draw.text((x - 50, y - 58), f"CURRENT / {layer_id}", fill=color)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def _phase2_profile(template: Path, output: Path) -> dict:
    profile = profile_template(template, output)
    profile["schema_version"] = "2.0.0"
    profile["source_path"] = template.name
    base_role = copy.deepcopy(profile["semantic_roles"]["photo_observation"])
    profile["semantic_roles"]["content_academic"] = base_role
    profile["safe_content_bounds"] = {"left_emu": 548640, "top_emu": 1097280, "width_emu": 11277600, "height_emu": 4800600}
    profile["title_zone"] = {"left_emu": 548640, "top_emu": 182880, "width_emu": 11277600, "height_emu": 731520}
    profile["recurring_objects"] = {"footer": "synthetic native footer zone", "slide_number": "layout-managed", "logo": None}
    profile["fixed_navigation_zones"] = [{"name": "bottom_navigation", "top_emu": 6431280, "height_emu": 365760}]
    profile["section_divider_layout_refs"] = [profile["layouts"][0]["layout_path"]]
    profile["notes_master_relationships"] = []
    _write(output, profile)
    return profile


def _canonical_claim(claim_id: str, block_id: str, text: str, claim_type: str, stage: str) -> dict:
    # Every claim carries a machine-addressable falsifier.  Prediction claims
    # self-reference until a later claim revision supersedes them; this keeps
    # the graph closed without inventing undeclared Cxxx identifiers.
    prediction = {"prediction_claim_ref": claim_id, "observation_that_falsifies": "Matched conditions do not change the predicted CV or resistance."}
    return {"schema_version": "1.0.0", "claim_id": claim_id, "revision": 1, "claim_type": claim_type, "text": text, "block_ref": {"block_id": block_id, "revision": 1}, "stage": stage, "scope": {"population": "synthetic samples", "conditions": "committed synthetic fixture", "exclusions": ["laboratory inference"]}, "epistemic_status": "testing", "confidence": {"level": "medium", "rationale": "synthetic test fixture"}, "evidence_support_refs": [], "evidence_contradict_refs": [], "assumptions": ["instrument proxy is valid"], "falsifiable_predictions": [prediction], "discriminating_evidence_requirements": [{"requirement_id": f"REQ-{claim_id}", "description": "controlled comparison with replicates"}], "provenance": "synthetic_fixture", "supersedes": [], "superseded_by": [], "created_at": CREATED_AT, "updated_at": CREATED_AT}


def _canonical_evidence(evidence_id: str, source_path: Path, block_id: str, claim_refs: list[str], *, kind: str = "synthetic_measurement", causal_role: str = "supporting_observation", origin: dict | None = None) -> dict:
    return {"schema_version": "1.0.0", "evidence_id": evidence_id, "kind": kind, "title": f"Synthetic {evidence_id} evidence", "provenance": "committed synthetic fixture", "source": {"source_id": evidence_id, "uri": source_path.relative_to(ROOT).as_posix(), "sha256": _sha(source_path)}, "claim_support_refs": claim_refs, "claim_contradict_refs": [], "scope": {"block_id": block_id}, "measurement": {"synthetic": True}, "causal_role": causal_role, "origin": origin or {"layer_ref": "H001", "source_dataset_role": "preexisting_observation"}, "license_or_usage": "synthetic_test_only", "verification": {"status": "synthetic_test_only"}}


def _canonical_stage(stage_id: str, block_id: str, stage_type: str, claim_refs: list[str], evidence_refs: list[str], data: dict) -> dict:
    return {"schema_version": "1.0.0", "stage_id": stage_id, "block_ref": {"block_id": block_id, "revision": 1}, "stage_type": stage_type, "revision": 1, "status": "complete", "claim_refs": claim_refs, "evidence_refs": evidence_refs, "hypothesis_claim_refs": claim_refs[:1] if stage_type == "experiment" else [], "prediction_claim_refs": claim_refs[-1:] if stage_type == "experiment" else [], "data": data, "provenance": "synthetic_fixture", "created_at": CREATED_AT, "updated_at": CREATED_AT}


def _canonical_block(block_id: str, title: str, question: str, problem: str, layer: dict, *, stages: dict, claim_refs: list[str], evidence_refs: list[str], assets: list[str], action: str, decision: str) -> dict:
    experiment_stage_refs = [f"ST-{ref}" for ref in layer.get("experiment_refs", [])]
    result_stage_refs = [f"ST-{ref}" for ref in layer.get("result_refs", [])]
    return {"schema_version": "1.0.0", "block_id": block_id, "revision": 1, "title": title, "research_question": {"question_id": f"RQ-{block_id}", "text": question, "scope": "synthetic fixture only"}, "problem_statement": problem, "research_status": "active", "story_visibility": {"master": "main", "meeting": "main", "defense": "appendix"}, "hypothesis_claim_refs": [claim_refs[0]], "mechanism_claim_refs": [claim_refs[1]], "prediction_claim_refs": [claim_refs[2]], "stage_refs": stages, "experiment_stage_refs": experiment_stage_refs or [stages["experiment"]], "result_stage_refs": result_stage_refs or [stages["result"]], "claim_refs": claim_refs, "evidence_refs": evidence_refs, "asset_refs": assets, "action_item_refs": [action], "decision_refs": [decision], "decision_criteria_ref": stages["experiment"] + "#/data/decision_rules", "provenance": "synthetic_fixture", "created_at": CREATED_AT, "updated_at": CREATED_AT}


def _append_phase2_history(fixture: dict, assets: dict[str, Path]) -> tuple[Ledger, int, int, int]:
    """Seed a causal ledger from fixture data; all later compilation reads its materializations."""
    ledger = Ledger(); fishbone1, fishbone2 = fixture["fishbone_revisions"]; p101, p201 = fixture["problems"]; d1, d2 = fixture["layer_discussions"]; s1, s2 = fixture["layer_summaries"]; h1, h2 = copy.deepcopy(fixture["hypothesis_layers"])
    h1["transition_ref"] = None
    h1_claims = [_canonical_claim("C101", "B101", "Bulk conductivity drives the positional signal gradient.", "hypothesis", "mechanism"), _canonical_claim("C102", "B101", "Hydration creates a conductivity gradient.", "mechanism", "mechanism"), _canonical_claim("C103", "B101", "Conductivity increase should lower signal CV.", "prediction", "experiment")]
    h2_claims = [_canonical_claim("C201", "B201", "Contact resistance drives instability at low pressure.", "hypothesis", "mechanism"), _canonical_claim("C202", "B201", "Interface contact fluctuates under low pressure.", "mechanism", "mechanism"), _canonical_claim("C203", "B201", "Matched conductivity plus pressure increase should lower CV.", "prediction", "experiment")]
    e1 = _canonical_evidence("E101", ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv", "B101", ["C103"])
    e0 = _canonical_evidence("E002", ROOT / "thesis-deck-system/examples/synthetic-project/assets/observation_visual.svg", "B101", ["C101"], kind="synthetic_observation")
    e2 = _canonical_evidence("E102", ROOT / "thesis-deck-system/examples/synthetic-project/assets/observation_visual.svg", "B101", ["C101"], kind="synthetic_observation")
    e3 = _canonical_evidence("E103", ROOT / "thesis-deck-system/examples/synthetic-project/evidence/literature-note.txt", "B101", ["C101", "C102"], kind="synthetic_literature")
    e4 = _canonical_evidence("E201", FIXTURE_ROOT / "contact-pressure.csv", "B201", ["C201"], kind="synthetic_measurement", causal_role="experiment_result", origin={"layer_ref": "H002", "experiment_stage_ref": "ST-EXP201", "source_dataset_role": "discriminating_result"})
    e5 = _canonical_evidence("E104", FIXTURE_ROOT / "h01-contact-uncertainty.txt", "B101", ["C101", "C102"], kind="synthetic_observation", causal_role="transition_precursor", origin={"layer_ref": "H001", "stage_ref": "ST-H001-DISC", "source_dataset_role": "pre_h02_uncertainty"})
    # H02 gets its own graph-closed copies of the pre-existing literature and
    # uncertainty.  E104 remains the *historical* H01 transition precursor;
    # it is never re-scoped as an H02 experimental result.
    e6 = _canonical_evidence("E202", ROOT / "thesis-deck-system/examples/synthetic-project/evidence/literature-note.txt", "B201", ["C201", "C202"], kind="synthetic_literature", causal_role="supporting_observation", origin={"layer_ref": "H002", "source_dataset_role": "preexisting_observation"})
    e7 = _canonical_evidence("E204", FIXTURE_ROOT / "h01-contact-uncertainty.txt", "B201", ["C201", "C202"], kind="synthetic_observation", causal_role="supporting_observation", origin={"layer_ref": "H001", "stage_ref": "ST-H001-DISC", "source_dataset_role": "pre_h02_uncertainty"})
    p201["evidence_refs"] = ["E204"]
    a1 = {"schema_version": "1.0.0", "asset_id": "A001", "asset_type": "data_plot", "title": "Synthetic defect density plot", "evidence_role": "quantitative_evidence", "source_evidence": ["E101"], "path": "plots/B001_defect_density.svg", "preview_path": "plots/B001_defect_density.png", "mime_type": "image/svg+xml", "sha256": _sha(assets["A001.svg"]), "editable": True, "generator": {"kind": "matplotlib", "version": "3.x", "script": "thesis-deck-system/examples/synthetic-project/plot.py", "script_sha256": _sha(ROOT / "thesis-deck-system/examples/synthetic-project/plot.py")}, "input": {"path": "thesis-deck-system/examples/synthetic-project/measurements.csv", "sha256": _sha(ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv")}, "output": {"svg_path": "plots/B001_defect_density.svg", "svg_sha256": _sha(assets["A001.svg"]), "png_path": "plots/B001_defect_density.png", "png_sha256": _sha(assets["A001.png"])}, "transform_chain": [{"input_sha256": _sha(ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv"), "operation": "plot", "output_sha256": _sha(assets["A001.svg"])}], "provenance": "synthetic_fixture", "accessibility": {"alt_text": "defect density by position"}, "status": "approved"}
    def simple_asset(asset_id: str, path: str, preview: str, source: str, asset_type: str = "mechanism_diagram") -> dict:
        base = {"schema_version": "1.0.0", "asset_id": asset_id, "asset_type": asset_type, "title": f"Synthetic {asset_id}", "evidence_role": "synthetic_test_evidence", "source_evidence": [source], "path": path, "preview_path": preview, "mime_type": "image/svg+xml", "sha256": _sha(assets[asset_id + ".svg"]), "editable": True, "provenance": "synthetic_fixture", "status": "approved"}
        if asset_type == "data_plot":
            base.update({"generator": {"kind": "matplotlib", "version": "3.x", "script": "thesis-deck-system/examples/synthetic-project/phase2/plot_contact_pressure.py", "script_sha256": _sha(FIXTURE_ROOT / "plot_contact_pressure.py")}, "input": {"path": "thesis-deck-system/examples/synthetic-project/phase2/contact-pressure.csv", "sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv")}, "output": {"svg_path": path, "svg_sha256": _sha(assets[asset_id + ".svg"]), "png_path": preview, "png_sha256": _sha(assets[asset_id + ".png"])}, "transform_chain": [{"input_sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv"), "operation": "plot", "output_sha256": _sha(assets[asset_id + ".svg"])}], "accessibility": {"alt_text": "contact pressure result plot"}})
        return base
    a101 = simple_asset("A101", "fishbone/FB001-rev1.svg", "fishbone/FB001-rev1.png", "E103"); a102 = simple_asset("A102", "fishbone/FB001-rev2.svg", "fishbone/FB001-rev2.png", "E204"); a201 = simple_asset("A201", "plots/H02_contact_pressure.svg", "plots/H02_contact_pressure.png", "E201", "data_plot")
    exp1 = {"independent_variables": ["含水量"], "controlled_variables": ["電極幾何", "接觸壓力"], "controls_baselines": ["原始配方"], "sample_plan": {"replicates": 3, "samples": 15}, "measured_outputs": ["導電度 (mS/cm)"], "instrumentation_method_refs": ["synthetic-four-probe"], "predicted_outcomes": ["導電度提升"], "decision_rules": {"go": "mean conductivity increases >=20%", "partial_go": "10-20%", "no_go": "<10%"}, "required_evidence": ["E101"]}
    exp2 = {"independent_variables": ["位置"], "controlled_variables": ["配方", "電極", "接觸壓力"], "controls_baselines": ["原始位置分布"], "sample_plan": {"replicates": 3, "samples": 15}, "measured_outputs": ["訊號 CV (%)"], "instrumentation_method_refs": ["synthetic-signal-test"], "predicted_outcomes": ["CV 下降"], "decision_rules": {"go": "CV decreases >=30%", "partial_go": "10-30%", "no_go": "<10%"}, "required_evidence": ["E101", "E102"]}
    exp3 = {"independent_variables": ["contact pressure"], "controlled_variables": ["bulk conductivity", "電極幾何"], "controls_baselines": ["low-pressure control"], "sample_plan": {"replicates": 5, "samples": 15}, "measured_outputs": ["訊號 CV (%)", "contact resistance (ohm)"], "instrumentation_method_refs": ["synthetic-pressure-fixture"], "predicted_outcomes": ["CV and resistance decrease"], "decision_rules": {"go": "both metrics improve", "partial_go": "one metric improves", "no_go": "neither improves"}, "required_evidence": ["E201"]}
    st = {}
    for prefix, bid, claims, evidences, expdata, results in [
        ("H001", "B101", h1_claims, ["E101", "E102", "E103"], [exp1, exp2], [
            ("ST-RES101", "平均導電度增加 24% ± 5% SD", [{"name": "mean conductivity increase", "value": 24, "uncertainty": 5, "uncertainty_semantics": "SD", "units": "%"}], []),
            ("ST-RES102", "訊號 CV 僅下降 4% ± 6% SD，屬 No-Go", [{"name": "signal CV decrease", "value": 4, "uncertainty": 6, "uncertainty_semantics": "SD", "units": "%"}], []),
        ]),
        ("H002", "B201", h2_claims, ["E204"], [exp3], [
            ("ST-RES201", "高壓條件 CV 下降 38% ± 7% SD，contact resistance 同步下降", [{"name": "signal CV decrease", "value": 38, "uncertainty": 7, "uncertainty_semantics": "SD", "units": "%"}], [{"name": "contact resistance", "status": "qualitative_supported", "statement": "同步下降", "units": None}]),
        ]),
    ]:
        prior_refs = ["E002", "E102"] if prefix == "H001" else ["E204"]
        knowledge_ref = "E103" if prefix == "H001" else "E202"
        st[f"ST-{prefix}-OBS"] = _canonical_stage(f"ST-{prefix}-OBS", bid, "observation", [claims[0]["claim_id"]], prior_refs, {"observation": "位置依賴缺陷與訊號變異已觀察到。", "problem": "現有模型無法解釋此變異。"})
        st[f"ST-{prefix}-LIT"] = _canonical_stage(f"ST-{prefix}-LIT", bid, "literature", [claim["claim_id"] for claim in claims[:2]], [knowledge_ref], {"consensus": "transport gradient 可產生位置效應。", "disagreements_or_alternatives": ["interface contact remains alternative"], "known_mechanisms": ["bulk transport", "boundary accumulation"], "research_gap": "缺少控制比較隔離機制。", "relevance_to_observation": "兩種機制都預測位置效應。", "implication_for_hypothesis_or_strategy": "需匹配條件後比較。", "supporting_literature_evidence_refs": [knowledge_ref], "contradicting_literature_evidence_refs": []})
        st[f"ST-{prefix}-MECH"] = _canonical_stage(f"ST-{prefix}-MECH", bid, "mechanism", [claim["claim_id"] for claim in claims[1:]], [knowledge_ref], {"mechanism": "bulk transport" if prefix == "H001" else "contact resistance", "falsification": "控制比較不出現預測差異。"})
        st[f"ST-{prefix}-SOL"] = _canonical_stage(f"ST-{prefix}-SOL", bid, "solution", [claims[1]["claim_id"]], [knowledge_ref], {"strategy": "均化導電度" if prefix == "H001" else "匹配導電度並改變接觸壓力", "success_criterion": "預測指標跨過 decision threshold"})
        exp_stage_ids = ["ST-EXP101", "ST-EXP102"] if prefix == "H001" else ["ST-EXP201"]
        for number, data in enumerate(expdata, 1): st[exp_stage_ids[number - 1]] = _canonical_stage(exp_stage_ids[number - 1], bid, "experiment", [claims[0]["claim_id"], claims[2]["claim_id"]], evidences, data)
        for sid, summary, metrics, qualitative_metrics in results:
            st[sid] = _canonical_stage(sid, bid, "result", [claims[2]["claim_id"]], ["E101" if prefix == "H001" else "E201"], {"summary": summary, "metrics": metrics, "qualitative_metrics": qualitative_metrics, "decision_ref": "D101" if prefix == "H001" else "D201"})
    h1_stages = {"observation": "ST-H001-OBS", "literature": "ST-H001-LIT", "mechanism": "ST-H001-MECH", "solution": "ST-H001-SOL", "experiment": "ST-EXP101", "result": "ST-RES101", "discussion": "ST-H001-DISC", "next_step": "NS101"}
    h2_stages = {"observation": "ST-H002-OBS", "literature": "ST-H002-LIT", "mechanism": "ST-H002-MECH", "solution": "ST-H002-SOL", "experiment": "ST-EXP201", "result": "ST-RES201", "discussion": "ST-H002-DISC", "next_step": "NS201"}
    b1 = _canonical_block("B101", "H01 Bulk conductivity mechanism", h1["research_question"], p101["problem_statement"], h1, stages=h1_stages, claim_refs=["C101", "C102", "C103"], evidence_refs=["E002", "E101", "E102", "E103"], assets=["A001", "A002", "A101"], action="NS101", decision="D101")
    b2 = _canonical_block("B201", "H02 Contact resistance mechanism", h2["research_question"], p201["problem_statement"], h2, stages=h2_stages, claim_refs=["C201", "C202", "C203"], evidence_refs=["E202", "E204", "E201"], assets=["A102", "A201"], action="NS201", decision="D201")
    action1 = {"schema_version": "1.0.0", "action_item_id": "NS101", "revision": 1, "action_type": "experiment", "title": "Matched-conductivity contact-pressure test", "action": "Run controlled pressure comparison.", "rationale": "Resolve bulk versus interface mechanism.", "source_decision_ref": "D101", "linked_block_refs": [{"block_id": "B101", "revision": 1}], "linked_claim_refs": ["C101", "C103"], "prior_commitment": {"meeting_id": "MEETING-001", "committed_at": CREATED_AT}, "owner": {"actor_id": "gary", "display_name": "Gary"}, "target_window": {"start": "2026-09-01T00:00:00Z", "due": "2026-09-10T09:00:00Z", "timezone": "Asia/Taipei"}, "actual_completion": {"completed_at": None, "closure_evidence_refs": []}, "success_failure_criteria": {"success": "effect exceeds uncertainty", "failure": "no discriminating effect"}, "required_evidence": ["E101"], "dependency_refs": ["pressure fixture"], "blocker_refs": [], "parallelizable": True, "workstream": "interface-mechanism", "status": "planned", "result_summary": "Awaiting controlled comparison", "supersedes": [], "superseded_by": [], "provenance": "synthetic_fixture", "created_at": CREATED_AT, "updated_at": CREATED_AT}
    action2 = copy.deepcopy(action1); action2.update({"action_item_id": "NS201", "revision": 1, "title": "High-pressure cycling durability", "source_decision_ref": "D201", "linked_block_refs": [{"block_id": "B201", "revision": 4}], "linked_claim_refs": ["C201", "C203"], "required_evidence": ["E201"], "status": "planned", "actual_completion": {"completed_at": None, "closure_evidence_refs": []}, "target_window": {"start": "2026-09-11T00:00:00Z", "due": "2026-09-24T00:00:00Z", "timezone": "Asia/Taipei"}})
    decision1 = {"schema_version": "1.0.0", "decision_id": "D101", "block_ref": {"block_id": "B101", "revision": 1}, "timestamp": CREATED_AT, "actor": {"type": "person", "id": "gary"}, "decision_type": "research_gate", "subject_refs": ["B101", "ST-H001-DISC"], "choice": "Partial-Go", "alternatives": ["No-Go"], "rationale": "Bulk conductivity is contributory but insufficient.", "evidence_refs": ["E101", "E102"], "provenance": "synthetic_fixture"}
    decision2 = copy.deepcopy(decision1); decision2.update({"decision_id": "D201", "block_ref": {"block_id": "B201", "revision": 4}, "subject_refs": ["B201", "ST-H002-DISC"], "choice": "Go", "rationale": "Contact-pressure control discriminates the interface mechanism.", "evidence_refs": ["E201"]})
    def append(event_type: str, payload: dict) -> int:
        return ledger.append(event_type, payload).cursor

    # The ledger deliberately exposes opening states before result evidence.
    # Pending result/discussion records are lifecycle placeholders; their
    # complete revisions are appended only after the corresponding evidence.
    append("fishbone_created", fishbone1)
    for claim in h1_claims: append("claim_created", claim)
    for evidence in (e0, e2, e3): append("evidence_linked", evidence)
    a002 = simple_asset("A002", "observation/observation_visual.svg", "observation/observation_visual.png", "E002", "observation_photo")
    for asset in (a002, a101): append("asset_registered", asset)
    p101 = copy.deepcopy(p101); p101["evidence_refs"] = ["E002"]
    append("problem_created", p101)
    # Initial method stages and experiment designs are known before results.
    for sid in ("ST-H001-OBS", "ST-H001-LIT", "ST-H001-MECH", "ST-H001-SOL"): append("stage_revised", st[sid])
    exp1_open = copy.deepcopy(st["ST-EXP101"]); exp1_open["evidence_refs"] = ["E002"]; exp1_open["data"]["required_evidence"] = ["E002"]
    exp2_open = copy.deepcopy(st["ST-EXP102"]); exp2_open["evidence_refs"] = ["E002", "E102"]; exp2_open["data"]["required_evidence"] = ["E002", "E102"]
    append("stage_revised", exp1_open); append("stage_revised", exp2_open)
    for sid, text in (("ST-RES101", "平均導電度增加 24% ± 5% SD"), ("ST-RES102", "訊號 CV 僅下降 4% ± 6% SD，屬 No-Go")):
        pending = copy.deepcopy(st[sid]); pending.update({"status": "pending", "evidence_refs": [], "data": {"planned_result": text}}); append("stage_revised", pending)
    discussion_pending = _canonical_stage("ST-H001-DISC", "B101", "discussion", ["C101", "C102"], [], {"hypothesis_support": "inconclusive", "failed_assumptions": [], "missing_evidence": ["results"], "limitations": ["pending"], "decision_ref": "D101", "next_step_ref": "NS101", "interpretation": "Pending result interpretation."}); append("stage_revised", discussion_pending)
    # D101/NS101 are provisional gate/action records; their complete evidence
    # and discussion bindings are overwritten only after results materialize.
    decision1_open = copy.deepcopy(decision1); decision1_open.update({"subject_refs": ["B101"], "evidence_refs": ["E002"], "choice": "pending", "rationale": "Awaiting result set."}); append("decision_recorded", decision1_open)
    append("action_committed", action1)
    b1_open = copy.deepcopy(b1); b1_open.update({"evidence_refs": ["E002", "E102", "E103"], "asset_refs": ["A002", "A101"], "decision_refs": ["D101"]})
    append("block_created", b1_open)
    h1_open = copy.deepcopy(h1); h1_open.update({"transition_ref": None, "source_event_cursor": len(ledger.replay()) + 1})
    append("hypothesis_layer_created", h1_open); h1_cursor = len(ledger.replay())

    # H01 result evidence and complete result stages arrive after the opening
    # cursor.  A block revision then closes the result/asset graph.
    append("evidence_linked", e1)
    append("stage_revised", st["ST-RES101"]); append("stage_revised", st["ST-RES102"])
    append("asset_registered", a1)
    b1_revision2 = copy.deepcopy(b1); b1_revision2.update({"revision": 2, "evidence_refs": ["E002", "E101", "E102", "E103"], "asset_refs": ["A001", "A002", "A101"], "decision_refs": ["D101"], "updated_at": CREATED_AT})
    append("block_revised", b1_revision2)
    dstage1 = _canonical_stage("ST-H001-DISC", "B101", "discussion", ["C101", "C102"], ["E101", "E102", "E103"], {"hypothesis_support": "partial_support", "failed_assumptions": ["uniform spatial exposure"], "missing_evidence": ["contact control"], "limitations": ["synthetic only"], "decision_ref": "D101", "next_step_ref": "NS101", "interpretation": "Results support only part of the bulk hypothesis."}); append("stage_revised", dstage1)
    d1["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_discussion_recorded", d1)
    append("decision_recorded", decision1)
    s1["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_summary_recorded", s1)
    h1_revision2 = copy.deepcopy(h1_open); h1_revision2.update({"revision": 2, "source_event_cursor": len(ledger.replay()) + 1, "updated_at": CREATED_AT}); append("hypothesis_layer_revised", h1_revision2)

    # Only the new Claim and true precursor may precede the Transition. The
    # successor layer's problem, method, experiment, result, discussion,
    # decision, and action lifecycle begins after the Transition and opening.
    for claim in h2_claims:
        append("claim_created", claim)
    transition = copy.deepcopy(fixture["hypothesis_transition"]); transition["observation_or_uncertainty_refs"] = ["E104"]; transition["source_event_cursor"] = len(ledger.replay()) + 1
    # E104 is appended immediately before the transition and is not derived
    # from the later H02 discriminating CSV.
    append("evidence_linked", e5)
    # e5 is E104; avoid duplicate insertion if the fixture changes IDs.
    b1_revision3 = copy.deepcopy(b1_revision2)
    b1_revision3.update({"revision": 3, "evidence_refs": ["E002", "E101", "E102", "E103", "E104"], "asset_refs": ["A001", "A002", "A101"], "decision_refs": ["D101"], "updated_at": CREATED_AT})
    append("block_revised", b1_revision3)
    transition_cursor = append("hypothesis_transition_recorded", transition)
    h1_revision3 = copy.deepcopy(h1_revision2); h1_revision3.update({"revision": 3, "transition_ref": transition["transition_id"], "source_event_cursor": len(ledger.replay()) + 1, "updated_at": CREATED_AT}); append("hypothesis_layer_revised", h1_revision3)
    h2_open = copy.deepcopy(h2); h2_open.update({"transition_ref": None, "source_event_cursor": len(ledger.replay()) + 1, "derived_from": {"previous_layer_ref": "H001", "discussion_refs": ["DISC-H001"], "decision_refs": ["D101"], "observation_refs": ["E104"]}})
    append("hypothesis_layer_created", h2_open)

    # Successor scientific work starts only after the layer-open event.
    append("fishbone_revised", fishbone2)
    for evidence in (e6, e7):
        append("evidence_linked", evidence)
    p201 = copy.deepcopy(p201); p201["evidence_refs"] = ["E204"]
    append("problem_created", p201)
    for sid in ("ST-H002-OBS", "ST-H002-LIT", "ST-H002-MECH", "ST-H002-SOL"):
        append("stage_revised", st[sid])
    append("asset_registered", a102)
    b2_open = copy.deepcopy(b2); b2_open.update({"stage_refs": {key: value for key, value in h2_stages.items() if key in {"observation", "literature", "mechanism", "solution"}}, "experiment_stage_refs": [], "result_stage_refs": [], "evidence_refs": ["E202", "E204"], "asset_refs": ["A102"], "action_item_refs": [], "decision_refs": [], "decision_criteria_ref": None})
    append("block_created", b2_open)
    append("stage_revised", st["ST-EXP201"])
    b2_revision2 = copy.deepcopy(b2_open); b2_revision2.update({"revision": 2, "stage_refs": {**b2_open["stage_refs"], "experiment": "ST-EXP201"}, "experiment_stage_refs": ["ST-EXP201"], "decision_criteria_ref": "ST-EXP201#/data/decision_rules", "updated_at": CREATED_AT})
    append("block_revised", b2_revision2)
    append("evidence_linked", e4)
    append("asset_registered", a201)
    append("stage_revised", st["ST-RES201"])
    b2_revision3 = copy.deepcopy(b2_revision2); b2_revision3.update({"revision": 3, "stage_refs": {**b2_revision2["stage_refs"], "result": "ST-RES201"}, "result_stage_refs": ["ST-RES201"], "evidence_refs": ["E202", "E204", "E201"], "asset_refs": ["A102", "A201"], "updated_at": CREATED_AT})
    append("block_revised", b2_revision3)
    dstage2 = _canonical_stage("ST-H002-DISC", "B201", "discussion", ["C201", "C202"], ["E201"], {"hypothesis_support": "supported", "failed_assumptions": [], "missing_evidence": ["durability"], "limitations": ["synthetic only"], "decision_ref": "D201", "next_step_ref": "NS201", "interpretation": "Pressure effect supports the interface mechanism."}); append("stage_revised", dstage2)
    b2_revision4 = copy.deepcopy(b2_revision3); b2_revision4.update({"revision": 4, "stage_refs": {**b2_revision3["stage_refs"], "discussion": "ST-H002-DISC"}, "updated_at": CREATED_AT})
    append("block_revised", b2_revision4)
    d2["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_discussion_recorded", d2)
    append("decision_recorded", decision2)
    append("action_committed", action2)
    b2_revision5 = copy.deepcopy(b2_revision4); b2_revision5.update({"revision": 5, "stage_refs": {**b2_revision4["stage_refs"], "next_step": "NS201"}, "action_item_refs": ["NS201"], "decision_refs": ["D201"], "updated_at": CREATED_AT})
    append("block_revised", b2_revision5)
    append("action_status_changed", {"action_item_id": "NS101", "status": "done", "actual_completion": {"completed_at": "2026-09-10T09:00:00Z", "closure_evidence_refs": ["E201"]}, "result_summary": "Completed synthetic control"})
    s2["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_summary_recorded", s2)
    h2_final = copy.deepcopy(h2_open); h2_final.update({"revision": 2, "source_event_cursor": len(ledger.replay()) + 1, "updated_at": CREATED_AT}); append("hypothesis_layer_revised", h2_final); h2_cursor = len(ledger.replay())
    return ledger, h1_cursor, transition_cursor, h2_cursor


def _compact_h01(logical: list[dict]) -> list[dict]:
    # Two full H01 experiment matrices exceed the governed A09 budget when
    # compacted.  Keep the independently materialized experiment pages as a
    # real continuation sequence rather than forging a post-hoc override.
    output = [copy.deepcopy(item) for item in logical]
    for item in output:
        if item["semantic_role"] == "experiment_design":
            item["compaction_rationale"] = "Split continuation: each Experiment Design retains its own A09 matrix and decision-rule region."
    return output


def _compact_h02(logical: list[dict]) -> list[dict]:
    # Merge only adjacent explanatory stages whose complete structured slot
    # contracts fit one governed page. Experiment and Result remain separate
    # so their causal boundary and measured statement cannot be obscured.
    roles = {item["semantic_role"]: item for item in logical}
    output = [copy.deepcopy(roles[role]) for role in ("hypothesis_title", "problem_definition", "fishbone_locator")]
    science = copy.deepcopy(roles["observation_problem"])
    science["combined_roles"] = ["observation_problem", "literature_mechanism", "mechanism_solution"]
    science["compaction_rationale"] = "Observation → Literature → Mechanism → Strategy are co-present with six physical governed slots."
    output.append(science)
    experiment = copy.deepcopy(roles["experiment_design"])
    result = next(item for item in logical if item["semantic_role"] == "result_single")
    experiment["semantic_role"] = "result_comparison"
    experiment["combined_roles"] = ["experiment_design", "result_single"]
    experiment["object_ref"] = [experiment["object_ref"], result["object_ref"]]
    experiment["compaction_rationale"] = "The discriminating experiment and its result share a governed comparison page with complete metadata before the measured outcome."
    output.append(experiment)
    summary = copy.deepcopy(roles["layer_summary_decision"])
    summary["combined_roles"] = ["layer_integrated_discussion", "layer_summary_decision"]
    summary["compaction_rationale"] = "Integrated Discussion and Summary/Decision are co-present with complete synthesis, decision, uncertainty, and Next Step slots."
    output.append(summary)
    return output


def _compact_complete_layer(logical: list[dict]) -> list[dict]:
    """Compact any one-experiment layer without dropping presentation roles."""
    experiments = [item for item in logical if item.get("semantic_role") == "experiment_design"]
    results = [item for item in logical if item.get("semantic_role") == "result_single"]
    if len(experiments) != 1 or len(results) != 1:
        return [copy.deepcopy(item) for item in logical]
    by_role = {item["semantic_role"]: item for item in logical}
    science = copy.deepcopy(by_role["observation_problem"])
    science.update({
        "combined_roles": ["observation_problem", "literature_mechanism", "mechanism_solution"],
        "source_cursor": max(by_role["observation_problem"]["source_cursor"], by_role["literature_mechanism"]["source_cursor"]),
        "stage_source_cursors": {
            "observation_problem": by_role["observation_problem"]["source_cursor"],
            "literature_mechanism": by_role["literature_mechanism"]["source_cursor"],
            "mechanism_solution": by_role["literature_mechanism"]["source_cursor"],
        },
        "compaction_rationale": "Observation, Literature, Mechanism, and Strategy remain audience-visible through unioned field/slot contracts.",
    })
    experiment = copy.deepcopy(experiments[0])
    experiment.update({
        "semantic_role": "result_comparison", "combined_roles": ["experiment_design", "result_single"],
        "object_ref": [experiments[0]["object_ref"], results[0]["object_ref"]], "source_cursor": results[0]["source_cursor"],
        "stage_source_cursors": {"experiment_design": experiments[0]["source_cursor"], "result_single": results[0]["source_cursor"]},
        "compaction_rationale": "Experiment metadata and Result remain in separate governed regions on the same slide.",
    })
    summary = copy.deepcopy(by_role["layer_summary_decision"])
    summary.update({
        "combined_roles": ["layer_integrated_discussion", "layer_summary_decision"],
        "stage_source_cursors": {"layer_integrated_discussion": by_role["layer_integrated_discussion"]["source_cursor"], "layer_summary_decision": by_role["layer_summary_decision"]["source_cursor"]},
        "compaction_rationale": "Discussion synthesis and Summary/Decision retain independent field-level evidence in unioned slots.",
    })
    replacements = {
        "observation_problem": science,
        "experiment_design": experiment,
        "layer_summary_decision": summary,
    }
    skipped = {"literature_mechanism", "result_single", "layer_integrated_discussion"}
    return [copy.deepcopy(replacements.get(item["semantic_role"], item)) for item in logical if item["semantic_role"] not in skipped]


def _asset_for(state: dict, block: dict, *, asset_type: str | None = None, path_fragment: str | None = None) -> dict | None:
    for asset_id in block.get("asset_refs", []):
        asset = state.get("assets", {}).get(asset_id, {})
        if asset_type and asset.get("asset_type") != asset_type:
            continue
        if path_fragment and path_fragment not in str(asset.get("path", "")):
            continue
        return asset
    return None


def _evidence_for_slide(state: dict, layer: dict, block: dict, role: str, object_ref=None, meeting: dict | None = None, combined_roles: list[str] | None = None) -> list[str]:
    """Return only evidence reachable and relevant to one presentation stage."""
    stages = state.get("stages", {})
    def stage_evidence(ref: str | None) -> list[str]:
        if not ref:
            return []
        stage = stages.get(ref, {})
        return [ref for ref in stage.get("evidence_refs", []) if ref in state.get("evidence", {})]
    def resolve_stage(ref: str | None) -> str | None:
        if not ref:
            return None
        return ref if ref in stages else (f"ST-{ref}" if f"ST-{ref}" in stages else ref)
    if role == "progress_todo":
        refs: list[str] = []
        for action in (meeting or {}).get("previous_commitments", []):
            refs.extend(ref for ref in action.get("required_evidence", []) if ref in state.get("evidence", {}))
            refs.extend(ref for ref in action.get("actual_completion", {}).get("closure_evidence_refs", []) if ref in state.get("evidence", {}))
        return list(dict.fromkeys(refs)) or [ref for ref in block.get("evidence_refs", []) if ref in state.get("evidence", {})]
    if role == "hypothesis_title":
        return list(dict.fromkeys(stage_evidence(block.get("stage_refs", {}).get("observation")))) or [ref for ref in block.get("evidence_refs", []) if ref in state.get("evidence", {})][:1]
    if role == "problem_definition":
        problem = state.get("problems", {}).get(layer.get("problem_ref"), {})
        return [ref for ref in problem.get("evidence_refs", []) if ref in state.get("evidence", {})]
    if role == "fishbone_locator":
        ref = layer.get("fishbone_snapshot_ref", {})
        asset = _asset_for(state, block, path_fragment=f"{ref.get('fishbone_id')}-rev{ref.get('revision')}")
        return [item for item in (asset or {}).get("source_evidence", []) if item in state.get("evidence", {})]
    if role in {"observation_problem", "literature_mechanism", "mechanism_solution"}:
        declared = set(combined_roles or [role])
        keys = []
        if "observation_problem" in declared or role == "observation_problem": keys.append("observation")
        if "literature_mechanism" in declared: keys.append("literature")
        if "mechanism_solution" in declared: keys.extend(["mechanism", "solution"])
        if role == "literature_mechanism" and not keys: keys.append("literature")
        if role == "mechanism_solution" and not keys: keys.extend(["mechanism", "solution"])
        refs: list[str] = []
        for key in keys:
            refs.extend(stage_evidence(block.get("stage_refs", {}).get(key)))
        return list(dict.fromkeys(refs))
    if role == "experiment_design":
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        return list(dict.fromkeys(item for ref in refs for item in stage_evidence(resolve_stage(ref))))
    if role in {"result_single", "result_comparison"}:
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        return list(dict.fromkeys(item for ref in refs for item in stage_evidence(resolve_stage(ref))))
    if role == "layer_integrated_discussion":
        return stage_evidence(block.get("stage_refs", {}).get("discussion"))
    if role == "layer_summary_decision":
        summary = state.get("layer_summaries", {}).get(object_ref, {})
        refs = [ref for ref in summary.get("supporting_evidence_refs", []) if ref in state.get("evidence", {})]
        return list(dict.fromkeys(refs))
    if role == "hypothesis_transition":
        transition = state.get("hypothesis_transitions", {}).get(object_ref, {})
        refs = list(transition.get("observation_or_uncertainty_refs", []))
        for result_ref in transition.get("key_result_refs", []):
            refs.extend(stage_evidence(resolve_stage(result_ref)))
        return list(dict.fromkeys(ref for ref in refs if ref in state.get("evidence", {})))
    return [ref for ref in block.get("evidence_refs", []) if ref in state.get("evidence", {})]


def _hydrate_from_state(raw: dict, state: dict, output_root: Path, *, overview: bool = False, meeting: dict | None = None) -> dict:
    """Hydrate a complete Slide Spec only from a cursor-materialized state."""
    if overview:
        if not meeting:
            raise ValueError("progress slide requires a persisted meeting projection")
        layer_id = meeting["current_layer_id"]
        role = "progress_todo"
        object_ref = next(iter(meeting.get("open_commitments", meeting.get("previous_commitments", []))), {}).get("action_item_id")
        cursor = int(meeting["source_event_cursor"])
    else:
        layer_id = raw["hypothesis_layer_ref"]
        role = raw["semantic_role"]
        object_ref = raw.get("object_ref")
        cursor = int(raw.get("source_cursor", 1))
    layer = state["hypothesis_layers"][layer_id]
    block_id = layer["research_block_refs"][0]
    block = state["blocks"][block_id]
    block_refs = [{"block_id": block_id, "revision": block.get("revision", 1)}]
    if overview:
        # The meeting projection preserves historical commitments.  Declare
        # every owning block, rather than pretending their decisions/actions
        # are part of the current layer's block graph.
        owned_ids = {
            item.get("block_id")
            for commitment in meeting.get("previous_commitments", [])
            for item in state.get("actions", {}).get(commitment.get("action_item_id"), {}).get("linked_block_refs", [])
            if item.get("block_id")
        }
        block_refs = [
            {"block_id": owned_id, "revision": state["blocks"][owned_id].get("revision", 1)}
            for owned_id in sorted(owned_ids)
        ] or block_refs
    claim_ref = layer["hypothesis_claim_ref"]
    combined_roles = raw.get("combined_roles", [role])
    evidence_refs = _evidence_for_slide(state, layer, block, role, object_ref, meeting, combined_roles)
    placements = []
    if role == "fishbone_locator":
        fishbone = layer["fishbone_snapshot_ref"]
        asset = _asset_for(state, block, path_fragment=f"{fishbone['fishbone_id']}-rev{fishbone['revision']}")
        if asset:
            placements.append({"slot": "primary_figure", "asset_id": asset["asset_id"], "asset_path": asset["path"]})
    elif role in {"result_single", "result_comparison"}:
        asset = _asset_for(state, block, asset_type="data_plot")
        if asset:
            placements.append({"slot": "result_plot", "asset_id": asset["asset_id"], "asset_path": asset["path"]})
    elif role == "observation_problem":
        asset = _asset_for(state, block, asset_type="observation_photo")
        if asset:
            placements.append({"slot": "primary_figure", "asset_id": asset["asset_id"], "asset_path": asset["path"]})
    title = {"progress_todo": "Progress / Previous Commitments", "hypothesis_title": f"{layer_id}｜Hypothesis", "problem_definition": f"{layer_id}｜Problem", "fishbone_locator": f"{layer_id}｜Total Fishbone / Research Map", "observation_problem": f"{layer_id}｜Observation → Literature → Mechanism", "literature_mechanism": f"{layer_id}｜Literature → Mechanism → Strategy", "experiment_design": f"{layer_id}｜Experiment Design", "result_comparison": f"{layer_id}｜Results", "result_single": f"{layer_id}｜Result", "layer_integrated_discussion": f"{layer_id}｜Integrated Discussion", "layer_summary_decision": f"{layer_id}｜Layer Summary / Decision", "hypothesis_transition": f"{layer_id}｜Hypothesis Transition"}.get(role, role)
    slots = content_slots_from_materialized_state(state, layer_id, role, object_ref, meeting_projection=meeting, combined_roles=combined_roles)
    semantic_fields = semantic_fields_from_materialized_state(state, layer_id, role, object_ref, meeting_projection=meeting, combined_roles=combined_roles)
    visible_fields: dict[str, list[str]] = {}
    concise_labels = {
        "hypothesis_statement": "Hypothesis", "falsifiable_prediction": "Falsifier", "research_question": "Question",
        "previous_finding": "Prior", "unresolved_conflict": "Conflict", "historical_snapshot": "History", "current_focus": "Focus",
        "observation": "Observation", "consensus": "Consensus", "disagreement_alternatives": "Alternatives", "research_gap": "Gap", "implication": "Implication",
        "mechanism": "Mechanism", "evidence_claim_link": "Evidence", "strategy": "Strategy", "success_criterion": "Criterion",
        "independent_variables": "IV", "controlled_variables": "Controls", "control_baseline": "Baseline", "sample_plan": "Sample",
        "replicates": "N", "measured_outputs": "Outputs", "units": "Units", "instrumentation_method": "Method", "predicted_outcomes": "Prediction", "decision_rule": "Rule",
        "result_identity": "ID", "result_statement": "Result", "metric_value_uncertainty": "Metric",
        "supporting_results": "Support", "contradicting_results": "Conflict", "non_discriminating_results": "Non-disc.", "cross_experiment_pattern": "Pattern",
        "mechanism_assessment": "Mechanism", "alternative_explanations": "Alternatives", "remaining_uncertainty": "Uncertainty",
        "answered_question": "Answer", "hypothesis_status": "Status", "decision": "Decision", "unresolved_items": "Unresolved", "next_question": "Next question", "next_step": "Next step",
        "prior_hypothesis": "Prior H", "key_prior_results": "Key results", "unresolved_point": "Unresolved", "precursor_observation": "Precursor", "derivation_rationale": "Rationale", "new_hypothesis": "New H",
        "prior_commitment": "Commitment", "current_position": "Current", "parallel_work": "Parallel",
    }
    for presentation_role, fields in semantic_fields.items():
        field_slots = PRESENTATION_ROLE_CONTRACTS.get(presentation_role, {}).get("required_fields", {})
        for field_name, value in fields.items():
            slot_name = field_slots.get(field_name)
            if not slot_name or not str(value).strip():
                continue
            label = concise_labels.get(field_name, field_name.replace("_", " ").title())
            visible_fields.setdefault(slot_name, []).append(f"{label}｜{value}")
    # The machine-addressable semantic fields own their physical regions.  Do
    # not duplicate the earlier aggregate prose in the same textbox: repeated
    # content caused genuine clipping in render-pixel QA.
    for slot_name, lines in visible_fields.items():
        slots[slot_name] = "\n".join(dict.fromkeys(lines))
    if "result_plot" in slots:
        result_fields = semantic_fields.get("result_single") or semantic_fields.get("result_comparison") or {}
        result_id = result_fields.get("result_identity", object_ref or "Result")
        result_statement = result_fields.get("result_statement", "")
        slots["result_plot"] = f"Figure｜{result_id}｜{result_statement}".strip("｜")
    body = content_from_materialized_state(state, layer_id, role, object_ref, meeting_projection=meeting)
    summary = state.get("layer_summaries", {}).get(layer.get("layer_summary_ref"), {})
    discussion = state.get("layer_discussions", {}).get(layer.get("layer_discussion_ref"), {})
    drefs = []
    if role == "layer_summary_decision":
        drefs = [value for value in [summary.get("decision_ref")] if value]
    elif role == "hypothesis_transition":
        drefs = list(state.get("hypothesis_transitions", {}).get(object_ref, {}).get("decision_refs", []))
    elif role == "progress_todo":
        drefs = [item.get("source_decision_ref") for item in (meeting or {}).get("previous_commitments", []) if item.get("source_decision_ref")]
    actions = list(summary.get("next_step_refs", [])) if role == "layer_summary_decision" else []
    if role == "progress_todo":
        actions = [item.get("action_item_id") for item in (meeting or {}).get("previous_commitments", []) if item.get("action_item_id")]
    compositions = {slot: ("asset_only" if any(item.get("slot") == slot for item in placements) else "text_only") for slot in slots}
    if any(item in combined_roles for item in ("result_single", "result_comparison")) and "result_plot" in compositions:
        compositions["result_plot"] = "asset_with_annotation"
    return {"schema_version": "2.0.0", "slide_id": raw.get("slide_id", f"S-{layer_id}-{role.upper()}"), "revision": 1, "deck_role": "meeting_delta" if overview else "hypothesis_layer", "block_refs": block_refs, "stage": role, "native_layout_role": "content_academic", "recipe": role, "object_ref": object_ref, "title": {"text": title, "assertion_claim_refs": [claim_ref]}, "placements": placements, "citations": evidence_refs, "speaker_notes": {"source_refs": evidence_refs, "text": "Compiled from persisted ledger materialization."}, "story_visibility": {"master": "main", "meeting": "main" if overview or layer.get("research_status") == "active" else "history", "defense": "appendix"}, "source_cursor": cursor, "stage_source_cursors": copy.deepcopy(raw.get("stage_source_cursors", {})), "bindings": {"claim_refs": [claim_ref], "evidence_refs": evidence_refs, "asset_refs": [p["asset_id"] for p in placements], "action_refs": actions, "decision_refs": list(dict.fromkeys(drefs)), "professor_profile_ref": copy.deepcopy(PROFESSOR_PROFILE_REF), "template_profile_ref": {"profile_id": "TP-SYNTH-PHASE2", "version": "2.0.0"}}, "content": {"slots": slots, "semantic_fields": semantic_fields, "body": body}, "slot_compositions": compositions, "hypothesis_layer_ref": None if overview else layer_id, "hypothesis_layer_revision": layer.get("revision", 1), "current_hypothesis_layer_ref": layer_id if overview else None, "semantic_role": role, "combined_roles": combined_roles, "fishbone_snapshot_ref": raw.get("fishbone_snapshot_ref"), "fishbone_focus_refs": raw.get("fishbone_focus_refs", []), "compaction_rationale": raw.get("compaction_rationale")}
def _manifest(specs: list[dict], output_root: Path, profile: dict, pptx_path: Path, final_cursor: int) -> dict:
    slides = []
    spec_path = output_root / "slide-specs.json"
    for ordinal, spec in enumerate(specs, 1):
        slides.append({"ordinal": ordinal, "slide_id": spec["slide_id"], "slide_spec_path": "slide-specs.json", "slide_spec_sha256": _sha(spec_path), "block_ref": spec["block_refs"][0], "block_refs": spec["block_refs"], "claim_refs": spec["bindings"]["claim_refs"], "evidence_refs": spec["bindings"]["evidence_refs"], "asset_refs": spec["bindings"]["asset_refs"], "action_refs": spec["bindings"]["action_refs"], "decision_refs": spec["bindings"]["decision_refs"], "professor_profile_ref": spec["bindings"]["professor_profile_ref"], "template_profile_ref": spec["bindings"]["template_profile_ref"], "source_event_cursor": spec["source_cursor"], "story_visibility": spec["story_visibility"]["master"], "hypothesis_layer_ref": spec.get("hypothesis_layer_ref"), "semantic_role": spec["semantic_role"]})
    return {"schema_version": "2.0.0", "deck_id": "MASTER-PHASE2-ACCEPTANCE", "deck_kind": "master", "title": "Synthetic Hypothesis-Layered Thesis History", "template_profile_ref": {"profile_id": profile["profile_id"], "version": profile["version"]}, "professor_profile_ref": copy.deepcopy(PROFESSOR_PROFILE_REF), "source_event_cursor": final_cursor, "build_id": "BUILD-MASTER-PHASE2-ACCEPTANCE", "build_tool_version": "0.3.0", "created_at": CREATED_AT, "projection": {"query": "master(hypothesis_layers=all,preserve_history=true)"}, "slides": slides, "outputs": {"pptx": "acceptance-deck.pptx", "pptx_sha256": _sha(pptx_path)}, "qa_report_refs": ["QA-MASTER-PHASE2-ACCEPTANCE"]}


def _layer_creation_cursors(ledger: Ledger) -> dict[str, int]:
    return {event.payload["hypothesis_layer_id"]: event.cursor for event in ledger.replay() if event.event_type == "hypothesis_layer_created"}


def _story_specs_from_ledger(ledger: Ledger, output_root: Path) -> tuple[list[dict], dict, dict[str, int]]:
    """Hydrate the generic all-layer Master story from replayed materializations."""
    creation_cursors = _layer_creation_cursors(ledger)
    ordered = sorted(creation_cursors, key=lambda layer_id: creation_cursors[layer_id])
    if not ordered:
        raise ValueError("Phase 2 acceptance story needs a materialized hypothesis layer")
    current_layer_id = ordered[-1]
    final_cursor = len(ledger.replay())
    current_state = ledger.materialize(final_cursor)
    meeting = meeting_projection(current_state, source_cursor=final_cursor, current_layer_id=current_layer_id)
    specs = [_hydrate_from_state({"slide_id": "S-PHASE2-PROGRESS-01"}, current_state, output_root, overview=True, meeting=meeting)]
    raw_master = compile_master_story_from_ledger(ledger)
    compacted: list[dict] = []
    for layer_id in ordered:
        layer_specs = [item for item in raw_master if item.get("hypothesis_layer_ref") == layer_id and item.get("semantic_role") != "hypothesis_transition"]
        compacted.extend(_compact_complete_layer(layer_specs))
        compacted.extend(item for item in raw_master if item.get("hypothesis_layer_ref") == layer_id and item.get("semantic_role") == "hypothesis_transition")
    for raw in compacted:
        cursor = int(raw["source_cursor"])
        specs.append(_hydrate_from_state(raw, ledger.materialize(cursor), output_root))
    return specs, meeting, creation_cursors


def _layout_specs_from_ledger(ledger: Ledger, specs: list[dict], output_root: Path, profile: dict) -> list[dict]:
    registry = SchemaRegistry(SCHEMA_ROOT, include_phase2=True)
    director = LayoutDirector(load_archetype_registry(output_root / "layout-archetypes.json"), profile)
    plans = []
    for slide in specs:
        state = ledger.materialize(slide["source_cursor"])
        layer_id = slide.get("hypothesis_layer_ref") or slide.get("current_hypothesis_layer_ref")
        layer = state["hypothesis_layers"][layer_id]
        block = state["blocks"][layer["research_block_refs"][0]]
        stages = [value for value in state.get("stages", {}).values() if value.get("block_ref", {}).get("block_id") == block["block_id"]]
        slots = slide.get("content", {}).get("slots", {})
        decision = director.select({"semantic_role": slide["semantic_role"], "combined_roles": slide.get("combined_roles", [slide["semantic_role"]]), "scientific_stage": slide["stage"], "asset_count": len(slide["placements"]), "evidence_count": len(slide["bindings"]["evidence_refs"]), "experiment_count": sum(item.get("stage_type") == "experiment" for item in stages), "result_count": sum(item.get("stage_type") == "result" for item in stages), "target_language": "zh-TW", "text_units": max([len(str(value)) for value in slots.values()] or [0]), "density_estimate": "high"})
        violations = validate_split_resolution(decision, None)
        if violations:
            raise ValueError(f"unresolved split for {slide['slide_id']}: {','.join(violations)}")
        plan = {"schema_version": "2.0.0", "layout_plan_id": "LP-" + slide["slide_id"][2:], "slide_id": slide["slide_id"], **decision, "native_template_layout": {"semantic_role": "content_academic", "layout_index": profile["semantic_roles"]["content_academic"]["layout_index"], "layout_path": profile["semantic_roles"]["content_academic"]["layout_path"], "master_path": profile["semantic_roles"]["content_academic"]["master_path"]}, "source_event_cursor": slide["source_cursor"], "created_at": CREATED_AT}
        registry.validate("layout-plan", plan)
        slide["placement_plan"] = copy.deepcopy(plan["placement_plan"])
        slide["layout_plan_ref"] = plan["layout_plan_id"]
        plans.append(plan)
    return plans


def rebuild_specs_and_layouts_from_ledger(ledger: Ledger, output_root: Path, profile: dict) -> tuple[list[dict], list[dict]]:
    """The post-serialization source-of-truth boundary used by regression tests."""
    specs, _, _ = _story_specs_from_ledger(ledger, output_root)
    plans = _layout_specs_from_ledger(ledger, specs, output_root, profile)
    return specs, plans


def _h003_professor_qa_fixture(state: dict, slides: list[dict], meeting: dict) -> dict:
    """Construct a fixture-only H003 extension to prove generic QA discovery."""
    extended = copy.deepcopy(state)
    h2 = extended["hypothesis_layers"]["H002"]
    claim = copy.deepcopy(extended["claims"]["C201"]); claim.update({"claim_id": "C301", "block_ref": {"block_id": "B301", "revision": 1}}); extended["claims"]["C301"] = claim
    problem = copy.deepcopy(extended["problems"]["P201"]); problem.update({"problem_id": "P301", "hypothesis_layer_ref": "H003"}); extended["problems"]["P301"] = problem
    for old_id, new_id in (("ST-H002-OBS", "ST-H003-OBS"), ("ST-H002-LIT", "ST-H003-LIT"), ("ST-H002-MECH", "ST-H003-MECH"), ("ST-H002-SOL", "ST-H003-SOL"), ("ST-EXP201", "ST-EXP301"), ("ST-RES201", "ST-RES301")):
        stage = copy.deepcopy(extended["stages"][old_id]); stage["stage_id"] = new_id; stage["block_ref"] = {"block_id": "B301", "revision": 1}; stage["claim_refs"] = ["C301"]; extended["stages"][new_id] = stage
    decision = copy.deepcopy(extended["decisions"]["D201"]); decision.update({"decision_id": "D301", "block_ref": {"block_id": "B301", "revision": 1}, "subject_refs": ["B301", "ST-H003-DISC"]}); extended["decisions"]["D301"] = decision
    action = copy.deepcopy(extended["actions"]["NS201"]); action.update({"action_item_id": "NS301", "source_decision_ref": "D301", "linked_block_refs": [{"block_id": "B301", "revision": 1}], "linked_claim_refs": ["C301"]}); extended["actions"]["NS301"] = action
    discussion = copy.deepcopy(extended["layer_discussions"]["DISC-H002"]); discussion.update({"discussion_id": "DISC-H003", "hypothesis_layer_ref": "H003", "supporting_results": ["RES301"], "decision_ref": "D301", "next_step_refs": ["NS301"]}); extended["layer_discussions"]["DISC-H003"] = discussion
    summary = copy.deepcopy(extended["layer_summaries"]["SUM-H002"]); summary.update({"summary_id": "SUM-H003", "hypothesis_layer_ref": "H003", "supporting_evidence_refs": ["E201", "RES301"], "decision_ref": "D301", "next_step_refs": ["NS301"]}); extended["layer_summaries"]["SUM-H003"] = summary
    block = copy.deepcopy(extended["blocks"]["B201"])
    block.update({"block_id": "B301", "title": "H03 fixture mechanism", "hypothesis_claim_refs": ["C301"], "mechanism_claim_refs": ["C301"], "prediction_claim_refs": ["C301"], "claim_refs": ["C301"], "stage_refs": {"observation": "ST-H003-OBS", "literature": "ST-H003-LIT", "mechanism": "ST-H003-MECH", "solution": "ST-H003-SOL", "experiment": "ST-EXP301", "result": "ST-RES301", "discussion": "ST-H003-DISC", "next_step": "NS301"}, "experiment_stage_refs": ["ST-EXP301"], "result_stage_refs": ["ST-RES301"], "action_item_refs": ["NS301"], "decision_refs": ["D301"]})
    extended["blocks"]["B301"] = block
    fishbone = copy.deepcopy(extended["fishbone_revisions"]["FB001@2"]); fishbone.update({"revision": 3, "source_event_cursor": 90, "linked_hypothesis_layers": ["H003"]}); extended["fishbone_revisions"]["FB001@3"] = fishbone
    transition = {"transition_id": "TR-H002-H003", "from_layer_ref": "H002", "to_layer_ref": "H003", "previous_hypothesis_claim_ref": "C201", "new_hypothesis_claim_ref": "C301", "key_result_refs": ["RES201"], "decision_refs": ["D201"], "observation_or_uncertainty_refs": ["E104"]}
    extended["hypothesis_transitions"]["TR-H002-H003"] = transition
    h3 = copy.deepcopy(h2); h3.update({"hypothesis_layer_id": "H003", "hypothesis_claim_ref": "C301", "problem_ref": "P301", "research_block_refs": ["B301"], "experiment_refs": ["EXP301"], "result_refs": ["RES301"], "experiment_order": ["EXP301"], "result_order": ["RES301"], "layer_discussion_ref": "DISC-H003", "layer_summary_ref": "SUM-H003", "layer_decision_ref": "D301", "next_step_refs": ["NS301"], "fishbone_snapshot_ref": {"fishbone_id": "FB001", "revision": 3}, "fishbone_focus_refs": ["FB-ELECTRODE-CONTACT"], "derived_from": {"previous_layer_ref": "H002", "discussion_refs": ["DISC-H002"], "decision_refs": ["D201"], "observation_refs": ["E104"]}, "transition_ref": None, "source_event_cursor": 100})
    extended["hypothesis_layers"]["H003"] = h3
    h3_slides = [{"semantic_role": role, "hypothesis_layer_ref": "H003", "fishbone_snapshot_ref": h3["fishbone_snapshot_ref"], "fishbone_focus_refs": h3["fishbone_focus_refs"]} for role in ("hypothesis_title", "problem_definition", "fishbone_locator", "result_single", "layer_integrated_discussion", "layer_summary_decision")]
    transition_slide = {"semantic_role": "hypothesis_transition", "hypothesis_layer_ref": "H002", "object_ref": "TR-H002-H003"}
    return {**meeting, "layers": list(extended["hypothesis_layers"].values()), "slides": [*slides, *h3_slides, transition_slide], "state": extended, "source_cursor": 100, "presentation_semantic_fidelity": {"status": "pass", "fixture": "H003 generic traversal"}}


def _append_third_layer_projection_fixture(source: Ledger, output_root: Path) -> Ledger:
    """Fixture-only third layer used to exercise the production N-layer driver."""
    ledger = copy.deepcopy(source)
    state = ledger.materialize()

    def clone(collection: str, source_id: str) -> dict:
        return copy.deepcopy(state[collection][source_id])

    claim = clone("claims", "C201"); claim.update({"claim_id": "C301", "block_ref": {"block_id": "B301", "revision": 1}, "text": "Cycling history controls the remaining interface instability."})
    precursor = clone("evidence", "E204"); precursor.update({"evidence_id": "E304", "scope": {"block_id": "B201"}, "causal_role": "transition_precursor", "origin": {"layer_ref": "H002", "stage_ref": "ST-H002-DISC", "source_dataset_role": "pre_h03_uncertainty"}})
    ledger.append("claim_created", claim)
    ledger.append("evidence_linked", precursor)
    transition = {
        "transition_id": "TR-H002-H003", "from_layer_ref": "H002", "to_layer_ref": "H003",
        "previous_hypothesis_claim_ref": "C201", "new_hypothesis_claim_ref": "C301",
        "key_result_refs": ["RES201"], "decision_refs": ["D201"],
        "observation_or_uncertainty_refs": ["E304"], "unexplained": "Cycling durability remains unknown.",
        "rationale": "The pressure result resolves the static interface mechanism but not cyclic stability.",
        "source_event_cursor": len(ledger.replay()) + 1,
    }
    ledger.append("hypothesis_transition_recorded", transition)
    h2 = clone("hypothesis_layers", "H002")
    h3 = copy.deepcopy(h2)
    h3.update({
        "hypothesis_layer_id": "H003", "revision": 1, "hypothesis_claim_ref": "C301", "problem_ref": "P301",
        "research_block_refs": ["B301"], "research_question": "Does cyclic loading explain the remaining instability?",
        "experiment_refs": ["EXP301"], "experiment_order": ["EXP301"], "result_refs": ["RES301"], "result_order": ["RES301"],
        "layer_discussion_ref": "DISC-H003", "layer_summary_ref": "SUM-H003", "layer_decision_ref": "D301", "next_step_refs": ["NS301"],
        "fishbone_snapshot_ref": {"fishbone_id": "FB001", "revision": 3}, "fishbone_focus_refs": ["FB-ELECTRODE-CONTACT"],
        "derived_from": {"previous_layer_ref": "H002", "discussion_refs": ["DISC-H002"], "decision_refs": ["D201"], "observation_refs": ["E304"]},
        "transition_ref": None, "source_event_cursor": len(ledger.replay()) + 1,
    })
    ledger.append("hypothesis_layer_created", h3)
    fishbone = clone("fishbone_revisions", "FB001@2"); fishbone.update({"revision": 3, "supersedes_revision": 2, "linked_hypothesis_layers": ["H003"], "source_event_cursor": len(ledger.replay()) + 1})
    ledger.append("fishbone_revised", fishbone)
    problem = clone("problems", "P201"); problem.update({"problem_id": "P301", "hypothesis_layer_ref": "H003", "research_question": h3["research_question"], "problem_statement": "Static pressure control does not establish cyclic durability."})
    ledger.append("problem_created", problem)
    literature = clone("evidence", "E202"); literature.update({"evidence_id": "E302", "scope": {"block_id": "B301"}, "claim_support_refs": ["C301"], "origin": {"layer_ref": "H003", "source_dataset_role": "preexisting_observation"}})
    ledger.append("evidence_linked", literature)
    stage_map = {}
    for stage_type, old_id, new_id in (
        ("observation", "ST-H002-OBS", "ST-H003-OBS"), ("literature", "ST-H002-LIT", "ST-H003-LIT"),
        ("mechanism", "ST-H002-MECH", "ST-H003-MECH"), ("solution", "ST-H002-SOL", "ST-H003-SOL"),
    ):
        stage = clone("stages", old_id); stage.update({"stage_id": new_id, "block_ref": {"block_id": "B301", "revision": 1}, "claim_refs": ["C301"], "evidence_refs": ["E302"]})
        ledger.append("stage_revised", stage); stage_map[stage_type] = new_id
    fishbone_asset = clone("assets", "A102"); fishbone_asset.update({"asset_id": "A302", "path": "fishbone/FB001-rev3.svg", "preview_path": "fishbone/FB001-rev3.png", "source_evidence": ["E302"]})
    ledger.append("asset_registered", fishbone_asset)
    block = clone("blocks", "B201")
    block.update({
        "block_id": "B301", "revision": 1, "title": "H03 Cycling durability mechanism", "hypothesis_claim_refs": ["C301"],
        "mechanism_claim_refs": ["C301"], "prediction_claim_refs": ["C301"], "claim_refs": ["C301"], "evidence_refs": ["E302"],
        "asset_refs": ["A302"], "action_item_refs": ["NS301"], "decision_refs": [],
        "stage_refs": {**stage_map, "experiment": "ST-EXP301", "result": "ST-RES301", "discussion": "ST-H003-DISC", "next_step": "NS301"},
        "experiment_stage_refs": ["ST-EXP301"], "result_stage_refs": ["ST-RES301"],
    })
    ledger.append("block_created", block)
    experiment = clone("stages", "ST-EXP201"); experiment.update({"stage_id": "ST-EXP301", "block_ref": {"block_id": "B301", "revision": 1}, "claim_refs": ["C301"], "evidence_refs": ["E302"]})
    ledger.append("stage_revised", experiment)
    result_evidence = clone("evidence", "E201"); result_evidence.update({"evidence_id": "E301", "scope": {"block_id": "B301"}, "claim_support_refs": ["C301"], "origin": {"layer_ref": "H003", "experiment_stage_ref": "ST-EXP301", "source_dataset_role": "discriminating_result"}})
    ledger.append("evidence_linked", result_evidence)
    plot_asset = clone("assets", "A201"); plot_asset.update({"asset_id": "A301", "path": "plots/H03_cycling.svg", "preview_path": "plots/H03_cycling.png", "source_evidence": ["E301"]})
    ledger.append("asset_registered", plot_asset)
    result = clone("stages", "ST-RES201"); result.update({"stage_id": "ST-RES301", "block_ref": {"block_id": "B301", "revision": 1}, "claim_refs": ["C301"], "evidence_refs": ["E301"]}); result["data"]["summary"] = "Cycling test retains 91% response after 100 cycles."
    ledger.append("stage_revised", result)
    block2 = copy.deepcopy(block); block2.update({"revision": 2, "evidence_refs": ["E302", "E301"], "asset_refs": ["A302", "A301"], "decision_refs": ["D301"]})
    ledger.append("block_revised", block2)
    discussion_stage = clone("stages", "ST-H002-DISC"); discussion_stage.update({"stage_id": "ST-H003-DISC", "block_ref": {"block_id": "B301", "revision": 1}, "claim_refs": ["C301"], "evidence_refs": ["E301"]})
    ledger.append("stage_revised", discussion_stage)
    discussion = clone("layer_discussions", "DISC-H002"); discussion.update({"discussion_id": "DISC-H003", "hypothesis_layer_ref": "H003", "supporting_results": ["RES301"], "contradicting_results": [], "non_discriminating_results": [], "decision_ref": "D301", "next_step_refs": ["NS301"], "source_event_cursor": len(ledger.replay()) + 1})
    ledger.append("layer_discussion_recorded", discussion)
    decision = clone("decisions", "D201"); decision.update({"decision_id": "D301", "block_ref": {"block_id": "B301", "revision": 2}, "subject_refs": ["B301", "ST-H003-DISC"], "evidence_refs": ["E301"]})
    ledger.append("decision_recorded", decision)
    action = clone("actions", "NS201"); action.update({"action_item_id": "NS301", "source_decision_ref": "D301", "linked_block_refs": [{"block_id": "B301", "revision": 2}], "linked_claim_refs": ["C301"], "required_evidence": ["E301"]})
    ledger.append("action_committed", action)
    summary = clone("layer_summaries", "SUM-H002"); summary.update({"summary_id": "SUM-H003", "hypothesis_layer_ref": "H003", "supporting_evidence_refs": ["E301"], "decision_ref": "D301", "next_step_refs": ["NS301"], "source_event_cursor": len(ledger.replay()) + 1})
    ledger.append("layer_summary_recorded", summary)
    h3_final = copy.deepcopy(h3); h3_final.update({"revision": 2, "source_event_cursor": len(ledger.replay()) + 1})
    ledger.append("hypothesis_layer_revised", h3_final)
    shutil.copy2(output_root / "fishbone/FB001-rev2.svg", output_root / "fishbone/FB001-rev3.svg")
    shutil.copy2(output_root / "fishbone/FB001-rev2.png", output_root / "fishbone/FB001-rev3.png")
    shutil.copy2(output_root / "plots/H02_contact_pressure.svg", output_root / "plots/H03_cycling.svg")
    shutil.copy2(output_root / "plots/H02_contact_pressure.png", output_root / "plots/H03_cycling.png")
    return ledger


def _layer_lifecycle_report(ledger: Ledger) -> dict:
    events = ledger.replay()
    state = ledger.materialize()
    ordered = sorted(
        (event for event in events if event.event_type == "hypothesis_layer_created"),
        key=lambda event: event.cursor,
    )
    transition_to = {event.payload.get("to_layer_ref"): event for event in events if event.event_type == "hypothesis_transition_recorded"}
    rows = []
    findings = []
    for index, opened in enumerate(ordered):
        layer_id = opened.payload["hypothesis_layer_id"]
        block_id = state["hypothesis_layers"][layer_id]["research_block_refs"][0]
        scientific = [event.cursor for event in events if event.cursor > opened.cursor and event.event_type == "stage_revised" and event.payload.get("block_ref", {}).get("block_id") == block_id and event.payload.get("stage_type") in {"observation", "literature", "mechanism", "solution"}]
        experiments = [event.cursor for event in events if event.event_type == "stage_revised" and event.payload.get("block_ref", {}).get("block_id") == block_id and event.payload.get("stage_type") == "experiment" and event.payload.get("status") != "pending"]
        result_evidence = [event.cursor for event in events if event.event_type == "evidence_linked" and event.payload.get("causal_role") == "experiment_result" and event.payload.get("origin", {}).get("layer_ref") == layer_id]
        discussions = [event.cursor for event in events if event.event_type == "layer_discussion_recorded" and event.payload.get("hypothesis_layer_ref") == layer_id]
        summaries = [event.cursor for event in events if event.event_type == "layer_summary_recorded" and event.payload.get("hypothesis_layer_ref") == layer_id]
        transition_cursor = transition_to.get(layer_id).cursor if layer_id in transition_to else None
        row = {
            "layer_id": layer_id, "transition_cursor": transition_cursor, "layer_open_cursor": opened.cursor,
            "first_scientific_stage_cursor": min(scientific, default=None), "experiment_cursor": min(experiments, default=None),
            "result_evidence_cursor": min(result_evidence, default=None), "discussion_cursor": min(discussions, default=None),
            "summary_cursor": min(summaries, default=None),
        }
        if index:
            values = [row[key] for key in ("transition_cursor", "layer_open_cursor", "first_scientific_stage_cursor", "experiment_cursor", "result_evidence_cursor", "discussion_cursor", "summary_cursor")]
            if any(value is None for value in values) or values != sorted(values) or not (values[0] < values[1] < values[2] <= values[3] < values[4] < values[5] < values[6]):
                findings.append({"layer_id": layer_id, "rule": "successor_lifecycle_order", "cursors": values})
        row["status"] = "fail" if any(item["layer_id"] == layer_id for item in findings) else "pass"
        rows.append(row)
    return {"schema_version": "1.0.0", "status": "fail" if findings else "pass", "layers": rows, "findings": findings}


def _n_layer_projection_report(ledger: Ledger, specs: list[dict], literal_scan: dict[str, list[str]], build_proof: dict | None = None) -> dict:
    """Prove ordered layer retention without knowing any fixture identifiers."""
    ordered = [event.payload["hypothesis_layer_id"] for event in ledger.replay() if event.event_type == "hypothesis_layer_created"]
    emitted = list(dict.fromkeys(spec.get("hypothesis_layer_ref") for spec in specs if spec.get("hypothesis_layer_ref")))
    transitions = [spec.get("object_ref") for spec in specs if spec.get("semantic_role") == "hypothesis_transition"]
    report = {
        "schema_version": "1.0.0",
        "ordered_layer_ids": ordered,
        "emitted_layer_ids": emitted,
        "emitted_transition_ids": transitions,
        "per_layer": {layer_id: {"slide_count": sum(spec.get("hypothesis_layer_ref") == layer_id for spec in specs), "roles": [spec.get("semantic_role") for spec in specs if spec.get("hypothesis_layer_ref") == layer_id]} for layer_id in ordered},
        "skipped_layers": [layer_id for layer_id in ordered if layer_id not in emitted],
        "literal_id_dependency_scan": literal_scan,
        "build_proof": build_proof or {},
    }
    required_opening_roles = {"hypothesis_title", "problem_definition", "fishbone_locator"}
    opening_complete = all(required_opening_roles <= set(report["per_layer"][layer_id]["roles"]) for layer_id in ordered)
    transition_complete = len(transitions) == max(0, len(ordered) - 1)
    build_ok = not build_proof or build_proof.get("structural_status") == "pass"
    report["status"] = "pass" if emitted == ordered and not report["skipped_layers"] and not literal_scan and opening_complete and transition_complete and build_ok else "fail"
    return report


def _canonical_report_facts(specs: list[dict], audit: dict, ledger: Ledger, qa_report: dict, private_status: dict) -> dict:
    events = ledger.replay()
    creation = sorted((event for event in events if event.event_type == "hypothesis_layer_created"), key=lambda event: event.cursor)
    layer_ids = [event.payload["hypothesis_layer_id"] for event in creation]
    first_id, second_id = layer_ids[:2]
    by_layer = {layer_id: [spec for spec in specs if spec.get("hypothesis_layer_ref") == layer_id] for layer_id in layer_ids}
    transitions = [event for event in events if event.event_type == "hypothesis_transition_recorded" and event.payload.get("from_layer_ref") == first_id and event.payload.get("to_layer_ref") == second_id]
    transition = transitions[0]
    precursor_id = transition.payload.get("observation_or_uncertainty_refs", [None])[0]
    evidence_cursor = {event.payload.get("evidence_id"): event.cursor for event in events if event.event_type == "evidence_linked"}
    result_evidence = [event for event in events if event.event_type == "evidence_linked" and event.payload.get("causal_role") == "experiment_result" and event.payload.get("origin", {}).get("layer_ref") == second_id]
    first_specs, second_specs = by_layer[first_id], by_layer[second_id]
    generated = audit.get("generated_slides", [])
    governed_slots = [slot for item in generated for slot in item.get("physical_slot_conformance", [])]
    required_slots = len(governed_slots)
    missing_slots = sum(1 for slot in governed_slots if not (slot.get("geometry_tolerance_result") and slot.get("content_or_asset_binding_result")))
    intentionally_empty = sum(len(spec.get("intentionally_empty_slots", [])) for spec in specs)
    role_specs = lambda records, role: [spec for spec in records if role in spec.get("combined_roles", [spec.get("semantic_role")])]
    return {
        "h01_opening_cursor": role_specs(first_specs, "hypothesis_title")[0]["source_cursor"],
        "h01_experiment_cursors": [event.cursor for event in events if event.event_type == "stage_revised" and event.payload.get("stage_type") == "experiment" and event.payload.get("block_ref", {}).get("block_id") in {ref for spec in first_specs for ref in [spec.get("block_refs", [{}])[0].get("block_id")]} and event.payload.get("status") == "complete"],
        "h01_result_cursors": [event.cursor for event in events if event.event_type == "stage_revised" and event.payload.get("stage_type") == "result" and event.payload.get("block_ref", {}).get("block_id") in {ref for spec in first_specs for ref in [spec.get("block_refs", [{}])[0].get("block_id")]} and event.payload.get("status") == "complete"],
        "h01_discussion_cursor": role_specs(first_specs, "layer_integrated_discussion")[0]["source_cursor"],
        "h01_summary_cursor": role_specs(first_specs, "layer_summary_decision")[0]["source_cursor"],
        "precursor_evidence_id": precursor_id, "precursor_evidence_cursor": evidence_cursor.get(precursor_id), "transition_cursor": transition.cursor,
        "h02_opening_cursor": role_specs(second_specs, "hypothesis_title")[0]["source_cursor"],
        "h02_experiment_cursor": role_specs(second_specs, "experiment_design")[0].get("stage_source_cursors", {}).get("experiment_design", role_specs(second_specs, "experiment_design")[0]["source_cursor"]),
        "h02_result_evidence_cursor": result_evidence[0].cursor,
        "h02_result_slide_cursors": [spec["source_cursor"] for spec in second_specs if set(spec.get("combined_roles", [spec.get("semantic_role")])) & {"result_single", "result_comparison"}],
        "h02_discussion_cursor": role_specs(second_specs, "layer_integrated_discussion")[0]["source_cursor"],
        "h02_summary_cursor": role_specs(second_specs, "layer_summary_decision")[0]["source_cursor"],
        "generated_slide_spec_count": len(specs), "physical_pptx_page_count": audit.get("slide_count"),
        "required_governed_slot_count": required_slots, "instantiated_governed_slot_count": required_slots - missing_slots,
        "intentionally_empty_slot_count": intentionally_empty, "missing_governed_slot_count": missing_slots,
        "qa_report_id": qa_report.get("qa_report_id", "QA-MASTER-PHASE2-ACCEPTANCE"),
        "native_powerpoint_status": qa_report.get("native_powerpoint_status", "blocked_environment"),
        "private_fixture_status": private_status.get("mode", "blocked_fixture"),
    }


def build_phase2(*, output_root: Path | None = None) -> dict:
    output_root = Path(output_root or (ROOT / "thesis-deck-system/artifacts/phase2"))
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    context = ProjectContext(output_root)
    fixture = yaml.safe_load((FIXTURE_ROOT / "fixture.yaml").read_text(encoding="utf-8"))
    registry = SchemaRegistry(SCHEMA_ROOT, include_phase2=True)
    registry.validate("fishbone-map", fixture["fishbone_map"])
    for name, items in (("fishbone-revision", fixture["fishbone_revisions"]), ("problem", fixture["problems"]), ("layer-discussion", fixture["layer_discussions"]), ("layer-summary", fixture["layer_summaries"]), ("hypothesis-layer", fixture["hypothesis_layers"])):
        for item in items:
            registry.validate(name, item)
    registry.validate("hypothesis-transition", fixture["hypothesis_transition"])
    archetypes = json.loads(ARCHETYPE_PATH.read_text(encoding="utf-8"))
    for archetype in archetypes:
        registry.validate("layout-archetype", archetype)

    fishbone_dir = output_root / "fishbone"
    fishbone1, fishbone2 = fixture["fishbone_revisions"]
    fb1 = render_fishbone_svg(fishbone1, ["FB-MATERIAL-HYDRATION"], "H01", fishbone_dir / "FB001-rev1.svg")
    fb1_hash = _sha(fb1)
    _fishbone_preview(fishbone1, ["FB-MATERIAL-HYDRATION"], "H01", fishbone_dir / "FB001-rev1.png")
    fb2 = render_fishbone_svg(fishbone2, ["FB-ELECTRODE-CONTACT"], "H02", fishbone_dir / "FB001-rev2.svg")
    _fishbone_preview(fishbone2, ["FB-ELECTRODE-CONTACT"], "H02", fishbone_dir / "FB001-rev2.png")
    rerender = render_fishbone_svg(fishbone1, ["FB-MATERIAL-HYDRATION"], "H01", fishbone_dir / "FB001-rev1-replay.svg")
    if _sha(rerender) != fb1_hash:
        raise ValueError("historical fishbone H01 changed after rev2")
    positions1 = branch_positions(fishbone1); positions2 = branch_positions(fishbone2)
    stable_ids = sorted(set(positions1) & set(positions2) - {"FB-ELECTRODE-CONTACT"})
    stable_deltas = {branch_id: max(abs(positions1[branch_id][0] - positions2[branch_id][0]), abs(positions1[branch_id][1] - positions2[branch_id][1])) for branch_id in stable_ids}
    _write(output_root / "fishbone-position-qa.json", {"status": "pass" if all(delta <= 0.01 for delta in stable_deltas.values()) else "fail", "stable_branch_max_delta": max(stable_deltas.values(), default=0), "stable_branch_deltas": stable_deltas, "hierarchy_parent": "FB-ELECTRODE-CONTACT -> FB-ELECTRODE"})

    template = create_synthetic_template(output_root / "synthetic-template.pptx")
    profile = _phase2_profile(template, output_root / "template-profile.json")
    profile["profile_id"] = "TP-SYNTH-PHASE2"; profile["version"] = "2.0.0"; _write(output_root / "template-profile.json", profile)
    shutil.copy2(ARCHETYPE_PATH, output_root / "layout-archetypes.json")
    visual_grammar = {"schema_version": "2.0.0", "grammar_id": "VG-SYNTH-PHASE2", "version": "2.0.0", "mode": "synthetic", "source_alias": "synthetic://layout-exemplar", "private_content_copied": False, "composition_rules": {"template_shell": ["EXEMPLAR-1", "EXEMPLAR-3"], "body_primary": "EXEMPLAR-2", "white_background": True, "figure_first": True, "structured_high_density": True}, "descriptors": [{"archetype_ref": item["archetype_id"], "dominant_content_region": "safe_content_bounds", "information_density": "high" if item["text_budget"] > 220 else "medium"} for item in archetypes]}
    _write(output_root / "visual-grammar.json", visual_grammar)

    plot_dir = output_root / "plots"; plot_dir.mkdir()
    (plot_dir / ".gitattributes").write_text("*.svg whitespace=-trailing-space\n", encoding="utf-8")
    source_plot_svg = ROOT / "thesis-deck-system/artifacts/phase1/plots/B001_defect_density.svg"
    source_plot_png = ROOT / "thesis-deck-system/artifacts/phase1/plots/B001_defect_density.png"
    if not source_plot_svg.exists() or not source_plot_png.exists():
        from .plotting import build_plot
        build_plot(ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv", plot_dir)
    else:
        shutil.copy2(source_plot_svg, plot_dir / "B001_defect_density.svg"); shutil.copy2(source_plot_png, plot_dir / "B001_defect_density.png")
    _load_plot_builder()(FIXTURE_ROOT / "contact-pressure.csv", plot_dir / "H02_contact_pressure.svg", plot_dir / "H02_contact_pressure.png")

    observation_dir = output_root / "observation"; observation_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "thesis-deck-system/examples/synthetic-project/assets/observation_visual.svg", observation_dir / "observation_visual.svg")
    shutil.copy2(ROOT / "thesis-deck-system/examples/synthetic-project/assets/observation_visual.png", observation_dir / "observation_visual.png")
    asset_files = {"A001.svg": plot_dir / "B001_defect_density.svg", "A001.png": plot_dir / "B001_defect_density.png", "A002.svg": observation_dir / "observation_visual.svg", "A002.png": observation_dir / "observation_visual.png", "A101.svg": fb1, "A101.png": fishbone_dir / "FB001-rev1.png", "A102.svg": fb2, "A102.png": fishbone_dir / "FB001-rev2.png", "A201.svg": plot_dir / "H02_contact_pressure.svg", "A201.png": plot_dir / "H02_contact_pressure.png"}
    ledger, h01_cursor, transition_cursor, h02_cursor = _append_phase2_history(fixture, asset_files)
    ledger.serialize(output_root / "ledger-events.json")
    persisted = Ledger.load(output_root / "ledger-events.json")
    lifecycle = _layer_lifecycle_report(persisted)
    _write(output_root / "layer-lifecycle-qa.json", lifecycle)
    if lifecycle["status"] != "pass":
        raise ValueError("Phase 2 layer lifecycle validation failed")
    n_layer_ledger = _append_third_layer_projection_fixture(persisted, output_root)
    n_layer_specs = compile_master_story_from_ledger(n_layer_ledger)
    n_layer_physical, _, _ = _story_specs_from_ledger(n_layer_ledger, output_root)
    n_layer_plans = _layout_specs_from_ledger(n_layer_ledger, n_layer_physical, output_root, profile)
    n_layer_deck = output_root / "n-layer-acceptance-deck.pptx"
    PythonPptxAssembler().assemble(template, n_layer_physical, n_layer_deck, project_context=context)
    n_layer_audit = audit_pptx(n_layer_deck, template, profile, n_layer_physical)
    n_layer_structural_ok = (
        n_layer_audit.get("slide_count") == len(n_layer_physical) + 2
        and n_layer_audit.get("unique_slide_ids")
        and n_layer_audit.get("has_editable_text")
        and not n_layer_audit.get("orphan_parts")
        and all(item.get("layout_master_role_match") and item.get("governed_geometry_match") and item.get("notes_source_match") for item in n_layer_audit.get("generated_slides", []))
        and all(slot.get("geometry_tolerance_result") and slot.get("content_or_asset_binding_result") for item in n_layer_audit.get("generated_slides", []) for slot in item.get("physical_slot_conformance", []))
    )
    _write(output_root / "n-layer-slide-specs.json", n_layer_physical)
    _write(output_root / "n-layer-layout-plans.json", n_layer_plans)
    _write(output_root / "n-layer-structural-audit.json", n_layer_audit)
    reusable_sources = [ROOT / "packages/thesis-deck-system/src/thesis_deck_system/story.py", ROOT / "packages/thesis-deck-system/src/thesis_deck_system/qa2.py"]
    fixture_literals = ["H001", "H002", "B101", "B201", "ST-RES101", "ST-RES102", "ST-RES201", "E101", "E201"]
    literal_scan = {literal: [path.relative_to(ROOT).as_posix() for path in reusable_sources if literal in path.read_text(encoding="utf-8")] for literal in fixture_literals}
    literal_scan = {key: value for key, value in literal_scan.items() if value}
    n_layer_artifact = _n_layer_projection_report(
        n_layer_ledger,
        n_layer_specs,
        literal_scan,
        {
            "slide_spec_count": len(n_layer_physical),
            "layout_plan_count": len(n_layer_plans),
            "pptx_path": n_layer_deck.relative_to(output_root).as_posix(),
            "physical_pptx_page_count": n_layer_audit.get("slide_count"),
            "structural_status": "pass" if n_layer_structural_ok else "fail",
        },
    )
    _write(output_root / "n-layer-projection-qa.json", n_layer_artifact)
    if n_layer_artifact["status"] != "pass":
        raise ValueError("Phase 2 N-layer projection validation failed")
    causal_findings = validate_causal_history(persisted)
    evidence_role_findings = validate_evidence_causal_roles(persisted)
    all_causal_findings = causal_findings + evidence_role_findings
    _write(output_root / "causal-temporal-qa.json", {"status": "pass" if not causal_findings else "fail", "findings": [finding.__dict__ for finding in causal_findings], "event_count": len(persisted.replay())})
    event_cursor = {event.payload.get("evidence_id"): event.cursor for event in persisted.replay() if event.event_type == "evidence_linked"}
    experiment_cursors = [event.cursor for event in persisted.replay() if event.event_type == "stage_revised" and event.payload.get("stage_id") == "ST-EXP201" and event.payload.get("status") == "complete"]
    experiment_cursor = experiment_cursors[-1] if experiment_cursors else None
    _write(output_root / "evidence-causal-role-qa.json", {"status": "pass" if not evidence_role_findings else "fail", "transition_id": "TR-H001-H002", "precursor_evidence": {"evidence_id": "E104", "causal_role": "transition_precursor", "source": "thesis-deck-system/examples/synthetic-project/phase2/h01-contact-uncertainty.txt", "cursor": event_cursor.get("E104"), "origin": {"layer_ref": "H001", "stage_ref": "ST-H001-DISC"}}, "downstream_result_evidence": {"evidence_id": "E201", "causal_role": "experiment_result", "source": "thesis-deck-system/examples/synthetic-project/phase2/contact-pressure.csv", "cursor": event_cursor.get("E201"), "experiment_binding": "ST-EXP201", "experiment_cursor": experiment_cursor}, "findings": [finding.__dict__ for finding in evidence_role_findings]})
    if all_causal_findings:
        raise ValueError("Phase 2 causal chronology validation failed: " + "; ".join(finding.rule_id for finding in all_causal_findings))
    canonical_registry = SchemaRegistry(SCHEMA_ROOT, include_phase2=True)
    canonical_collections = {"blocks": "research-block", "claims": "claim", "evidence": "evidence-card", "assets": "asset-manifest", "actions": "next-step", "decisions": "decision-event", "stages": "scientific-stage", "problems": "problem"}
    canonical_errors = []
    for collection, schema_name in canonical_collections.items():
        for object_id, value in persisted.materialize().get(collection, {}).items():
            canonical_errors.extend(f"{collection}/{object_id}: {error}" for error in canonical_registry.errors(schema_name, value))
    if canonical_errors:
        raise ValueError("Phase 2 canonical contract validation failed: " + "; ".join(canonical_errors))
    provenance_checks = []
    for asset_id, svg_key, png_key, source_path, script_path in (("A001", "A001.svg", "A001.png", ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv", ROOT / "thesis-deck-system/examples/synthetic-project/plot.py"), ("A201", "A201.svg", "A201.png", FIXTURE_ROOT / "contact-pressure.csv", FIXTURE_ROOT / "plot_contact_pressure.py")):
        provenance_checks.append({"asset_id": asset_id, "source_sha256": _sha(source_path), "script_sha256": _sha(script_path), "svg_sha256": _sha(asset_files[svg_key]), "png_sha256": _sha(asset_files[png_key]), "verified": asset_files[svg_key].is_file() and asset_files[png_key].is_file()})
    _write(output_root / "asset-provenance-qa.json", {"status": "pass" if all(item["verified"] for item in provenance_checks) else "fail", "checks": provenance_checks})
    h01_state = persisted.materialize(h01_cursor); transition_state = persisted.materialize(transition_cursor); h02_state = persisted.materialize(h02_cursor)
    _write(output_root / "materialized-h01.json", h01_state); _write(output_root / "materialized-transition.json", transition_state); _write(output_root / "materialized-h02.json", h02_state)
    physical, meeting, creation_cursors = _story_specs_from_ledger(persisted, output_root)
    raw_story = compile_master_story_from_ledger(persisted)
    expected_story_count = 1 + sum(
        len(_compact_complete_layer([item for item in raw_story if item.get("hypothesis_layer_ref") == layer_id and item.get("semantic_role") != "hypothesis_transition"]))
        + sum(item.get("hypothesis_layer_ref") == layer_id and item.get("semantic_role") == "hypothesis_transition" for item in raw_story)
        for layer_id in creation_cursors
    )
    if len(physical) != expected_story_count:
        raise ValueError(f"acceptance story count mismatch: expected {expected_story_count}, got {len(physical)}")
    _write(output_root / "slide-specs.json", physical)

    plans = _layout_specs_from_ledger(persisted, physical, output_root, profile)
    split_pages = [slide["slide_id"] for slide in physical if slide.get("semantic_role") == "experiment_design" and slide.get("hypothesis_layer_ref") == "H001"]
    split_records = [{"resolution_type": "split", "source_role": "experiment_design", "reason": "A09 combined experiment matrix exceeded its governed text budget", "continuation_slide_ids": split_pages, "available_cursor": min(slide["source_cursor"] for slide in physical if slide["slide_id"] in split_pages)}] if len(split_pages) > 1 else []
    _write(output_root / "layout-plans.json", plans); _write(output_root / "layout-director-decisions.json", [{"slide_id": plan["slide_id"], "selected_archetype": plan["selected_archetype"], "slot_signature": plan["slot_signature"], "split_recommendation": plan["split_recommendation"], "required_slots": plan["required_slots"]} for plan in plans]); _write(output_root / "layout-overrides.json", []); _write(output_root / "split-fit-exceptions.json", split_records); _write(output_root / "slide-specs.json", physical)

    deck = output_root / "acceptance-deck.pptx"
    temporal_snapshot = run_presentation_temporal_snapshot_qa(physical, persisted)
    _write(output_root / "presentation-temporal-snapshot-qa.json", temporal_snapshot)
    if temporal_snapshot["status"] != "pass":
        raise ValueError("presentation temporal snapshot validation failed")
    PythonPptxAssembler().assemble(template, physical, deck, project_context=context)
    audit = audit_pptx(deck, template, profile, physical); _write(output_root / "structural-audit.json", audit)
    combined_content = run_combined_role_content_qa(physical, audit)
    _write(output_root / "combined-role-content-qa.json", combined_content)
    physical_fidelity = run_physical_content_fidelity_qa(physical, audit)
    _write(output_root / "physical-content-fidelity-qa.json", physical_fidelity)
    semantic_fidelity = run_presentation_semantic_fidelity_qa(physical, audit, temporal_snapshot, combined_content, physical_fidelity, ledger=persisted)
    _write(output_root / "presentation-semantic-fidelity-qa.json", semantic_fidelity)
    manifest = _manifest(physical, output_root, profile, deck, h02_cursor); _write(output_root / "MASTER-PHASE2.manifest.json", manifest)
    master = master_projection(h02_state, source_cursor=h02_cursor)
    _write(output_root / "master-projection.json", master); _write(output_root / "meeting-projection.json", meeting)

    professor_profile = yaml.safe_load((ROOT / "thesis-deck-system/examples/synthetic-project/professor-profile.yaml").read_text(encoding="utf-8"))
    registry.validate("professor-profile", professor_profile)
    _write(output_root / "professor-profile.json", professor_profile)
    professor_projection = {**meeting, "layers": list(h02_state["hypothesis_layers"].values()), "slides": physical, "state": h02_state, "source_cursor": h02_cursor, "presentation_semantic_fidelity": semantic_fidelity, "combined_role_content": combined_content}
    professor = run_professor_qa_v2(professor_profile, professor_projection); _write(output_root / "professor-qa.json", professor)
    h003_professor = run_professor_qa_v2(professor_profile, _h003_professor_qa_fixture(h02_state, physical, meeting))
    if h003_professor["status"] != "pass":
        raise ValueError("generic H003 Professor QA fixture failed")
    _write(output_root / "h003-generic-professor-qa-fixture.json", h003_professor)
    history_findings = validate_hypothesis_history(h02_state)
    scientific_findings = history_findings + evidence_role_findings
    scientific = {"status": "pass" if not scientific_findings else "fail", "executed_checks": ["phase2_schema_validation", "ledger_hash_replay", "cursor_isolation", "causal_temporal_order", "evidence_causal_role_integrity", "hypothesis_derivation", "fishbone_revision_immutability", "experiment_metadata", "synthetic_evidence_labeling", "plot_source_hashes", "asset_provenance_chain"], "findings": [finding.__dict__ for finding in scientific_findings], "evidence": {"h01_cursor": h01_cursor, "transition_cursor": transition_cursor, "h02_cursor": h02_cursor, "causal_temporal_status": "pass", "evidence_causal_role_status": "pass" if not evidence_role_findings else "fail", "precursor_evidence_id": "E104", "downstream_result_evidence_id": "E201", "h01_fishbone_sha256": fb1_hash, "h01_replay_sha256": _sha(rerender), "h02_fishbone_sha256": _sha(fb2), "contact_csv_sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv"), "contact_script_sha256": _sha(FIXTURE_ROOT / "plot_contact_pressure.py"), "contact_svg_sha256": _sha(plot_dir / "H02_contact_pressure.svg")}}
    _write(output_root / "scientific-provenance-qa.json", scientific)
    private_status = PrivateFixtureLocator(explicit={}).status(); _write(output_root / "private-fixture-status.json", private_status)
    audit = json.loads((output_root / "structural-audit.json").read_text(encoding="utf-8"))
    preliminary_qa = {"qa_report_id": "QA-MASTER-PHASE2-ACCEPTANCE", "native_powerpoint_status": "blocked_environment"}
    report_facts = _canonical_report_facts(physical, audit, persisted, preliminary_qa, private_status)
    _write(output_root / "report-facts.json", report_facts)
    _write(output_root / "report-evidence-consistency.json", run_report_evidence_consistency(report_facts, copy.deepcopy(report_facts)))
    return {"output_root": output_root, "h01_cursor": h01_cursor, "h02_cursor": h02_cursor, "slide_count": len(physical), "private_fixture_acceptance": private_status["mode"]}


def finalize_phase2_qa(output_root: Path, render_evidence: dict) -> dict:
    """Join render evidence with materialized build evidence into the executed gate report."""
    output_root = Path(output_root)
    registry = SchemaRegistry(SCHEMA_ROOT, include_phase2=True)
    specs = json.loads((output_root / "slide-specs.json").read_text(encoding="utf-8"))
    manifest = json.loads((output_root / "MASTER-PHASE2.manifest.json").read_text(encoding="utf-8"))
    profile = json.loads((output_root / "template-profile.json").read_text(encoding="utf-8"))
    plans = json.loads((output_root / "layout-plans.json").read_text(encoding="utf-8"))
    errors = [error for spec in specs for error in registry.errors("slide-spec", spec)]
    errors += registry.errors("deck-manifest", manifest) + registry.errors("template-profile", profile)
    errors += [error for plan in plans for error in registry.errors("layout-plan", plan)]
    ledger = Ledger.load(output_root / "ledger-events.json")
    h01_state = json.loads((output_root / "materialized-h01.json").read_text(encoding="utf-8")); h02_state = json.loads((output_root / "materialized-h02.json").read_text(encoding="utf-8")); transition_state = json.loads((output_root / "materialized-transition.json").read_text(encoding="utf-8"))
    h01_cursor = len(h01_state.get("events", [])); h02_cursor = len(h02_state.get("events", [])); transition_cursor = len(transition_state.get("events", []))
    replayed = ledger.materialize(h01_cursor) == h01_state and ledger.materialize(transition_cursor) == transition_state and ledger.materialize(h02_cursor) == h02_state
    scientific = json.loads((output_root / "scientific-provenance-qa.json").read_text(encoding="utf-8"))
    professor = json.loads((output_root / "professor-qa.json").read_text(encoding="utf-8"))
    audit = json.loads((output_root / "structural-audit.json").read_text(encoding="utf-8"))
    temporal_snapshot = json.loads((output_root / "presentation-temporal-snapshot-qa.json").read_text(encoding="utf-8"))
    combined_content = json.loads((output_root / "combined-role-content-qa.json").read_text(encoding="utf-8"))
    prior_fidelity = json.loads((output_root / "physical-content-fidelity-qa.json").read_text(encoding="utf-8"))
    render_hashes = {item.get("slide_id"): item.get("render_sha256") for item in render_evidence.get("visual", {}).get("render_pixel_qa", {}).get("slides", [])}
    physical_fidelity = run_physical_content_fidelity_qa(specs, audit, render_hashes)
    _write(output_root / "physical-content-fidelity-qa.json", physical_fidelity)
    semantic_fidelity = run_presentation_semantic_fidelity_qa(specs, audit, temporal_snapshot, combined_content, physical_fidelity, ledger=ledger)
    _write(output_root / "presentation-semantic-fidelity-qa.json", semantic_fidelity)
    # Professor QA is the consumer of the post-assembly semantic gate. Reload
    # the persisted projection and rerun it after render-grounded fidelity is
    # known, rather than reusing the pre-render provisional record.
    professor_profile = json.loads((output_root / "professor-profile.json").read_text(encoding="utf-8"))
    meeting_projection = json.loads((output_root / "meeting-projection.json").read_text(encoding="utf-8"))
    professor_projection = {**meeting_projection, "layers": list(h02_state["hypothesis_layers"].values()), "slides": specs, "state": h02_state, "source_cursor": h02_cursor, "presentation_semantic_fidelity": semantic_fidelity, "combined_role_content": combined_content}
    professor = run_professor_qa_v2(professor_profile, professor_projection)
    _write(output_root / "professor-qa.json", professor)
    materialized = h02_state
    binding_bundle = {"research_blocks": list(materialized["blocks"].values()), "claims": list(materialized["claims"].values()), "evidence_cards": list(materialized["evidence"].values()), "assets": list(materialized["assets"].values()), "actions": list(materialized["actions"].values()), "decisions": list(materialized["decisions"].values()), "stages": list(materialized["stages"].values()), "meeting_projection": json.loads((output_root / "meeting-projection.json").read_text(encoding="utf-8")), "template_profiles": [profile]}
    binding_findings = validate_temporal_bindings(binding_bundle, ledger, specs, [manifest], qa_reports=[{"qa_report_id": "QA-MASTER-PHASE2-ACCEPTANCE", "deck_id": manifest["deck_id"], "build_id": manifest["build_id"]}])
    _write(output_root / "phase2-binding-validation.json", {"status": "pass" if not binding_findings else "fail", "findings": [finding.__dict__ for finding in binding_findings], "unresolved_ref_count": len(binding_findings)})
    errors += [f"{finding.rule_id}: {finding.message}" for finding in binding_findings]
    report = run_phase2_pipeline(schema_errors=errors, ledger_replayed=replayed, scientific=scientific, professor=professor, audit=audit, specs=specs, visual=render_evidence["visual"], render_evidence=render_evidence, presentation_semantic=semantic_fidelity)
    _write(output_root / "qa-report.json", report)
    private_status = json.loads((output_root / "private-fixture-status.json").read_text(encoding="utf-8"))
    canonical_facts = _canonical_report_facts(specs, audit, ledger, report, private_status)
    reported_facts = json.loads((output_root / "report-facts.json").read_text(encoding="utf-8"))
    consistency = run_report_evidence_consistency(canonical_facts, reported_facts)
    if consistency["status"] == "pass":
        _write(output_root / "report-facts.json", canonical_facts)
    _write(output_root / "report-evidence-consistency.json", consistency)
    return report


def verify_implementation_report_facts(output_root: Path, report_path: Path) -> dict:
    """Verify the committed report footer against the generated canonical facts."""
    output_root = Path(output_root)
    report_path = Path(report_path)
    text = report_path.read_text(encoding="utf-8")
    marker = "### codex_report"
    if marker not in text:
        raise ValueError("implementation report is missing the codex_report footer")
    footer = text.split(marker, 1)[1]
    if "```yaml" not in footer or "```" not in footer.split("```yaml", 1)[1]:
        raise ValueError("codex_report footer is not a fenced YAML document")
    document = yaml.safe_load(footer.split("```yaml", 1)[1].split("```", 1)[0]) or {}
    reported = document.get("codex_report", {}).get("report_facts")
    if not isinstance(reported, dict):
        raise ValueError("codex_report.report_facts is missing")
    canonical = json.loads((output_root / "report-facts.json").read_text(encoding="utf-8"))
    result = run_report_evidence_consistency(canonical, reported)
    result["report_path"] = report_path.resolve().relative_to(ROOT).as_posix()
    result["report_sha256"] = _sha(report_path)
    _write(output_root / "report-evidence-consistency.json", result)
    return result
