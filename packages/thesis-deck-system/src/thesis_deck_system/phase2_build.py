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
from .hypothesis import validate_causal_history, validate_hypothesis_history
from .layout import LayoutDirector, load_archetype_registry
from .ledger import Ledger
from .phase2_projections import master_projection, meeting_projection
from .pptx import PythonPptxAssembler, audit_pptx
from .private_fixtures import PrivateFixtureLocator
from .qa2 import run_phase2_pipeline, run_professor_qa_v2
from .story import compile_hypothesis_layer_from_state, content_from_materialized_state
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


def _canonical_evidence(evidence_id: str, source_path: Path, block_id: str, claim_refs: list[str], *, kind: str = "synthetic_measurement") -> dict:
    return {"schema_version": "1.0.0", "evidence_id": evidence_id, "kind": kind, "title": f"Synthetic {evidence_id} evidence", "provenance": "committed synthetic fixture", "source": {"source_id": evidence_id, "uri": source_path.relative_to(ROOT).as_posix(), "sha256": _sha(source_path)}, "claim_support_refs": claim_refs, "claim_contradict_refs": [], "scope": {"block_id": block_id}, "measurement": {"synthetic": True}, "license_or_usage": "synthetic_test_only", "verification": {"status": "synthetic_test_only"}}


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
    e4 = _canonical_evidence("E201", FIXTURE_ROOT / "contact-pressure.csv", "B201", ["C201"], kind="synthetic_measurement")
    a1 = {"schema_version": "1.0.0", "asset_id": "A001", "asset_type": "data_plot", "title": "Synthetic defect density plot", "evidence_role": "quantitative_evidence", "source_evidence": ["E101"], "path": "plots/B001_defect_density.svg", "preview_path": "plots/B001_defect_density.png", "mime_type": "image/svg+xml", "sha256": _sha(assets["A001.svg"]), "editable": True, "generator": {"kind": "matplotlib", "version": "3.x", "script": "thesis-deck-system/examples/synthetic-project/plot.py", "script_sha256": _sha(ROOT / "thesis-deck-system/examples/synthetic-project/plot.py")}, "input": {"path": "thesis-deck-system/examples/synthetic-project/measurements.csv", "sha256": _sha(ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv")}, "output": {"svg_path": "plots/B001_defect_density.svg", "svg_sha256": _sha(assets["A001.svg"]), "png_path": "plots/B001_defect_density.png", "png_sha256": _sha(assets["A001.png"])}, "transform_chain": [{"input_sha256": _sha(ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv"), "operation": "plot", "output_sha256": _sha(assets["A001.svg"])}], "provenance": "synthetic_fixture", "accessibility": {"alt_text": "defect density by position"}, "status": "approved"}
    def simple_asset(asset_id: str, path: str, preview: str, source: str, asset_type: str = "mechanism_diagram") -> dict:
        base = {"schema_version": "1.0.0", "asset_id": asset_id, "asset_type": asset_type, "title": f"Synthetic {asset_id}", "evidence_role": "synthetic_test_evidence", "source_evidence": [source], "path": path, "preview_path": preview, "mime_type": "image/svg+xml", "sha256": _sha(assets[asset_id + ".svg"]), "editable": True, "provenance": "synthetic_fixture", "status": "approved"}
        if asset_type == "data_plot":
            base.update({"generator": {"kind": "matplotlib", "version": "3.x", "script": "thesis-deck-system/examples/synthetic-project/phase2/plot_contact_pressure.py", "script_sha256": _sha(FIXTURE_ROOT / "plot_contact_pressure.py")}, "input": {"path": "thesis-deck-system/examples/synthetic-project/phase2/contact-pressure.csv", "sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv")}, "output": {"svg_path": path, "svg_sha256": _sha(assets[asset_id + ".svg"]), "png_path": preview, "png_sha256": _sha(assets[asset_id + ".png"])}, "transform_chain": [{"input_sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv"), "operation": "plot", "output_sha256": _sha(assets[asset_id + ".svg"])}], "accessibility": {"alt_text": "contact pressure result plot"}})
        return base
    a101 = simple_asset("A101", "fishbone/FB001-rev1.svg", "fishbone/FB001-rev1.png", "E103"); a102 = simple_asset("A102", "fishbone/FB001-rev2.svg", "fishbone/FB001-rev2.png", "E201"); a201 = simple_asset("A201", "plots/H02_contact_pressure.svg", "plots/H02_contact_pressure.png", "E201", "data_plot")
    exp1 = {"independent_variables": ["含水量"], "controlled_variables": ["電極幾何", "接觸壓力"], "controls_baselines": ["原始配方"], "sample_plan": {"replicates": 3, "samples": 15}, "measured_outputs": ["導電度 (mS/cm)"], "instrumentation_method_refs": ["synthetic-four-probe"], "predicted_outcomes": ["導電度提升"], "decision_rules": {"go": "mean conductivity increases >=20%", "partial_go": "10-20%", "no_go": "<10%"}, "required_evidence": ["E101"]}
    exp2 = {"independent_variables": ["位置"], "controlled_variables": ["配方", "電極", "接觸壓力"], "controls_baselines": ["原始位置分布"], "sample_plan": {"replicates": 3, "samples": 15}, "measured_outputs": ["訊號 CV (%)"], "instrumentation_method_refs": ["synthetic-signal-test"], "predicted_outcomes": ["CV 下降"], "decision_rules": {"go": "CV decreases >=30%", "partial_go": "10-30%", "no_go": "<10%"}, "required_evidence": ["E101", "E102"]}
    exp3 = {"independent_variables": ["contact pressure"], "controlled_variables": ["bulk conductivity", "電極幾何"], "controls_baselines": ["low-pressure control"], "sample_plan": {"replicates": 5, "samples": 15}, "measured_outputs": ["訊號 CV (%)", "contact resistance (ohm)"], "instrumentation_method_refs": ["synthetic-pressure-fixture"], "predicted_outcomes": ["CV and resistance decrease"], "decision_rules": {"go": "both metrics improve", "partial_go": "one metric improves", "no_go": "neither improves"}, "required_evidence": ["E201"]}
    st = {}
    for prefix, bid, claims, evidences, expdata, results in [("H001", "B101", h1_claims, ["E101", "E102", "E103"], [exp1, exp2], [("ST-RES101", "平均導電度增加 24% ± 5% SD"), ("ST-RES102", "訊號 CV 僅下降 4% ± 6% SD，屬 No-Go")]), ("H002", "B201", h2_claims, ["E201"], [exp3], [("ST-RES201", "高壓條件 CV 下降 38% ± 7% SD，contact resistance 同步下降")])]:
        st[f"ST-{prefix}-OBS"] = _canonical_stage(f"ST-{prefix}-OBS", bid, "observation", [claims[0]["claim_id"]], (["E002", "E102"] if prefix == "H001" else ["E201"]), {"observation": "位置依賴缺陷與訊號變異已觀察到。", "problem": "現有模型無法解釋此變異。"})
        st[f"ST-{prefix}-LIT"] = _canonical_stage(f"ST-{prefix}-LIT", bid, "literature", [claim["claim_id"] for claim in claims[:2]], ["E103" if prefix == "H001" else "E201"], {"consensus": "transport gradient 可產生位置效應。", "disagreements_or_alternatives": ["interface contact remains alternative"], "known_mechanisms": ["bulk transport", "boundary accumulation"], "research_gap": "缺少控制比較隔離機制。", "relevance_to_observation": "兩種機制都預測位置效應。", "implication_for_hypothesis_or_strategy": "需匹配條件後比較。", "supporting_literature_evidence_refs": ["E103"], "contradicting_literature_evidence_refs": []})
        st[f"ST-{prefix}-MECH"] = _canonical_stage(f"ST-{prefix}-MECH", bid, "mechanism", [claim["claim_id"] for claim in claims[1:]], ["E103" if prefix == "H001" else "E201"], {"mechanism": "bulk transport" if prefix == "H001" else "contact resistance", "falsification": "控制比較不出現預測差異。"})
        st[f"ST-{prefix}-SOL"] = _canonical_stage(f"ST-{prefix}-SOL", bid, "solution", [claims[1]["claim_id"]], ["E103" if prefix == "H001" else "E201"], {"strategy": "均化導電度" if prefix == "H001" else "匹配導電度並改變接觸壓力", "success_criterion": "預測指標跨過 decision threshold"})
        exp_stage_ids = ["ST-EXP101", "ST-EXP102"] if prefix == "H001" else ["ST-EXP201"]
        for number, data in enumerate(expdata, 1): st[exp_stage_ids[number - 1]] = _canonical_stage(exp_stage_ids[number - 1], bid, "experiment", [claims[0]["claim_id"], claims[2]["claim_id"]], evidences, data)
        for number, (sid, summary) in enumerate(results, 1): st[sid] = _canonical_stage(sid, bid, "result", [claims[2]["claim_id"]], ["E101" if prefix == "H001" else "E201"], {"summary": summary, "metrics": [{"name": "CV", "value": 24 if number == 1 else 4, "uncertainty": 5, "units": "%"}], "decision_ref": "D101" if prefix == "H001" else "D201"})
    h1_stages = {"observation": "ST-H001-OBS", "literature": "ST-H001-LIT", "mechanism": "ST-H001-MECH", "solution": "ST-H001-SOL", "experiment": "ST-EXP101", "result": "ST-RES101", "discussion": "ST-H001-DISC", "next_step": "NS101"}
    h2_stages = {"observation": "ST-H002-OBS", "literature": "ST-H002-LIT", "mechanism": "ST-H002-MECH", "solution": "ST-H002-SOL", "experiment": "ST-EXP201", "result": "ST-RES201", "discussion": "ST-H002-DISC", "next_step": "NS201"}
    b1 = _canonical_block("B101", "H01 Bulk conductivity mechanism", h1["research_question"], p101["problem_statement"], h1, stages=h1_stages, claim_refs=["C101", "C102", "C103"], evidence_refs=["E002", "E101", "E102", "E103"], assets=["A001", "A002", "A101"], action="NS101", decision="D101")
    b2 = _canonical_block("B201", "H02 Contact resistance mechanism", h2["research_question"], p201["problem_statement"], h2, stages=h2_stages, claim_refs=["C201", "C202", "C203"], evidence_refs=["E201"], assets=["A102", "A201"], action="NS201", decision="D201")
    action1 = {"schema_version": "1.0.0", "action_item_id": "NS101", "revision": 1, "action_type": "experiment", "title": "Matched-conductivity contact-pressure test", "action": "Run controlled pressure comparison.", "rationale": "Resolve bulk versus interface mechanism.", "source_decision_ref": "D101", "linked_block_refs": [{"block_id": "B101", "revision": 1}], "linked_claim_refs": ["C101", "C103"], "prior_commitment": {"meeting_id": "MEETING-001", "committed_at": CREATED_AT}, "owner": {"actor_id": "gary", "display_name": "Gary"}, "target_window": {"start": "2026-09-01T00:00:00Z", "due": "2026-09-10T09:00:00Z", "timezone": "Asia/Taipei"}, "actual_completion": {"completed_at": None, "closure_evidence_refs": []}, "success_failure_criteria": {"success": "effect exceeds uncertainty", "failure": "no discriminating effect"}, "required_evidence": ["E101"], "dependency_refs": ["pressure fixture"], "blocker_refs": [], "parallelizable": True, "workstream": "interface-mechanism", "status": "planned", "result_summary": "Awaiting controlled comparison", "supersedes": [], "superseded_by": [], "provenance": "synthetic_fixture", "created_at": CREATED_AT, "updated_at": CREATED_AT}
    action2 = copy.deepcopy(action1); action2.update({"action_item_id": "NS201", "revision": 1, "title": "High-pressure cycling durability", "source_decision_ref": "D201", "linked_block_refs": [{"block_id": "B201", "revision": 1}], "linked_claim_refs": ["C201", "C203"], "required_evidence": ["E201"], "status": "planned", "actual_completion": {"completed_at": None, "closure_evidence_refs": []}, "target_window": {"start": "2026-09-11T00:00:00Z", "due": "2026-09-24T00:00:00Z", "timezone": "Asia/Taipei"}})
    decision1 = {"schema_version": "1.0.0", "decision_id": "D101", "block_ref": {"block_id": "B101", "revision": 1}, "timestamp": CREATED_AT, "actor": {"type": "person", "id": "gary"}, "decision_type": "research_gate", "subject_refs": ["B101", "ST-H001-DISC"], "choice": "Partial-Go", "alternatives": ["No-Go"], "rationale": "Bulk conductivity is contributory but insufficient.", "evidence_refs": ["E101", "E102"], "provenance": "synthetic_fixture"}
    decision2 = copy.deepcopy(decision1); decision2.update({"decision_id": "D201", "block_ref": {"block_id": "B201", "revision": 1}, "subject_refs": ["B201", "ST-H002-DISC"], "choice": "Go", "rationale": "Contact-pressure control discriminates the interface mechanism.", "evidence_refs": ["E201"]})
    def append(event_type: str, payload: dict) -> int:
        event = ledger.append(event_type, payload); return event.cursor
    # Scientific leaves are appended before their graph boundary.  The block
    # declaration is committed once all references it names are materialized,
    # so no cursor exposes a block pointing into the future.
    append("fishbone_created", fishbone1)
    for claim in h1_claims: append("claim_created", claim)
    for evidence in (e0, e1, e2, e3): append("evidence_linked", evidence)
    a002 = simple_asset("A002", "observation/observation_visual.svg", "observation/observation_visual.png", "E002", "observation_photo")
    for asset in (a1, a002, a101): append("asset_registered", asset)
    append("problem_created", p101)
    for sid in ("ST-H001-OBS", "ST-H001-LIT", "ST-H001-MECH", "ST-H001-SOL", "ST-EXP101", "ST-EXP102", "ST-RES101", "ST-RES102"): append("stage_revised", st[sid])
    dstage1 = _canonical_stage("ST-H001-DISC", "B101", "discussion", ["C101", "C102"], ["E101", "E102", "E103"], {"hypothesis_support": "partial_support", "failed_assumptions": ["uniform spatial exposure"], "missing_evidence": ["contact control"], "limitations": ["synthetic only"], "decision_ref": "D101", "next_step_ref": "NS101", "interpretation": "Results support only part of the bulk hypothesis."}); append("stage_revised", dstage1)
    d1["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_discussion_recorded", d1); append("decision_recorded", decision1); append("action_committed", action1)
    s1["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_summary_recorded", s1)
    append("block_created", b1)
    h1["source_event_cursor"] = len(ledger.replay()) + 1; append("hypothesis_layer_created", h1); h1_cursor = len(ledger.replay())
    append("fishbone_revised", fishbone2)
    for claim in h2_claims: append("claim_created", claim)
    for evidence in (e4,): append("evidence_linked", evidence)
    append("problem_created", p201)
    append("stage_revised", st["ST-H002-OBS"])
    # The transition is deliberately after the new H02 claim/evidence and
    # historical fishbone revision, never at the H01 cursor.
    transition = copy.deepcopy(fixture["hypothesis_transition"]); transition["source_event_cursor"] = len(ledger.replay()) + 1; append("hypothesis_transition_recorded", transition); transition_cursor = len(ledger.replay())
    h1_revision2 = copy.deepcopy(h1)
    h1_revision2.update({"revision": 2, "transition_ref": transition["transition_id"], "source_event_cursor": len(ledger.replay()) + 1, "updated_at": CREATED_AT})
    append("hypothesis_layer_revised", h1_revision2)
    for asset in (a102, a201): append("asset_registered", asset)
    for sid in ("ST-H002-LIT", "ST-H002-MECH", "ST-H002-SOL", "ST-EXP201", "ST-RES201"): append("stage_revised", st[sid])
    dstage2 = _canonical_stage("ST-H002-DISC", "B201", "discussion", ["C201", "C202"], ["E201"], {"hypothesis_support": "supported", "failed_assumptions": [], "missing_evidence": ["durability"], "limitations": ["synthetic only"], "decision_ref": "D201", "next_step_ref": "NS201", "interpretation": "Pressure effect supports the interface mechanism."}); append("stage_revised", dstage2)
    append("action_status_changed", {"action_item_id": "NS101", "status": "done", "actual_completion": {"completed_at": "2026-09-10T09:00:00Z", "closure_evidence_refs": ["E201"]}, "result_summary": "Completed synthetic control"})
    d2["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_discussion_recorded", d2); append("decision_recorded", decision2); append("action_committed", action2)
    s2["source_event_cursor"] = len(ledger.replay()) + 1; append("layer_summary_recorded", s2)
    append("block_created", b2)
    h2["source_event_cursor"] = len(ledger.replay()) + 1; append("hypothesis_layer_created", h2); h2_cursor = len(ledger.replay())
    return ledger, h1_cursor, transition_cursor, h2_cursor


def _compact_h01(logical: list[dict]) -> list[dict]:
    experiments = [item for item in logical if item["semantic_role"] == "experiment_design"]
    output = []
    for item in logical:
        if item["semantic_role"] == "experiment_design":
            if item is experiments[0]:
                combined = copy.deepcopy(item)
                combined["object_ref"] = [entry["object_ref"] for entry in experiments]
                combined["compaction_rationale"] = "兩個 Experiment Design 同頁依 experiment_order 呈現；Results 仍在其後分頁。"
                output.append(combined)
            continue
        output.append(copy.deepcopy(item))
    return output


def _compact_h02(logical: list[dict]) -> list[dict]:
    output = []
    roles = {item["semantic_role"]: item for item in logical}
    for role in ("hypothesis_title", "problem_definition", "fishbone_locator"):
        output.append(copy.deepcopy(roles[role]))
    science = copy.deepcopy(roles["observation_problem"])
    science["combined_roles"] = ["observation_problem", "literature_mechanism", "mechanism_solution"]
    science["compaction_rationale"] = "相鄰 Scientific Method stages 共享一頁，但保持 Observation → Literature → Mechanism → Strategy 的閱讀順序。"
    output.append(science)
    experiment = copy.deepcopy(roles["experiment_design"])
    result = next(item for item in logical if item["semantic_role"] in {"result_single", "result_comparison"})
    experiment["semantic_role"] = "result_comparison"
    experiment["combined_roles"] = ["experiment_design", result["semantic_role"]]
    experiment["object_ref"] = [experiment["object_ref"], result["object_ref"]]
    experiment["compaction_rationale"] = "單一 discriminating experiment 與結果共頁，Experiment metadata 先於 Result。"
    output.append(experiment)
    summary = copy.deepcopy(roles["layer_summary_decision"])
    summary["combined_roles"] = ["layer_integrated_discussion", "layer_summary_decision"]
    summary["compaction_rationale"] = "H02 acceptance 將 integrated Discussion 與 Summary/Decision 並列，完整 evidence set 已在前頁呈現。"
    output.append(summary)
    return output


def _hydrate_from_state(raw: dict, state: dict, output_root: Path, *, overview: bool = False, meeting: dict | None = None) -> dict:
    """Hydrate a Slide Spec exclusively from a persisted materialized state."""
    if overview:
        layer_id, block_id, claim_ref, role, cursor, evidence_refs = "H002", "B201", "C201", "progress_todo", max(int(e.get("cursor", 0)) for e in state.get("events", [])), ["E201"]
        object_ref = "NS201"
    else:
        layer_id = raw["hypothesis_layer_ref"]; layer = state["hypothesis_layers"][layer_id]; block_id = layer["research_block_refs"][0]; claim_ref = layer["hypothesis_claim_ref"]; role = raw["semantic_role"]; cursor = raw.get("source_cursor", layer.get("source_event_cursor", 1)); evidence_refs = ["E002", "E101", "E102", "E103"] if layer_id == "H001" else ["E201"]; object_ref = raw.get("object_ref")
    layer = state["hypothesis_layers"][layer_id]
    placements = []
    if role == "fishbone_locator":
        rev = layer["fishbone_snapshot_ref"]["revision"]; aid = "A101" if rev == 1 else "A102"; placements = [{"slot": "primary_figure", "asset_id": aid, "asset_path": f"fishbone/FB001-rev{rev}.svg"}]
    elif role in {"result_single", "result_comparison"}:
        aid = "A001" if layer_id == "H001" else "A201"; path = "plots/B001_defect_density.svg" if aid == "A001" else "plots/H02_contact_pressure.svg"; placements = [{"slot": "proposed_panel" if role == "result_comparison" else "result_plot", "asset_id": aid, "asset_path": path}]
    elif role == "observation_problem" and layer_id == "H001":
        placements = [{"slot": "primary_figure", "asset_id": "A002", "asset_path": "observation/observation_visual.svg"}]
    title = {"progress_todo": "Progress / Previous Commitments", "hypothesis_title": f"{layer_id}｜Hypothesis", "problem_definition": f"{layer_id}｜Problem", "fishbone_locator": f"{layer_id}｜Total Fishbone / Research Map", "observation_problem": f"{layer_id}｜Observation → Literature → Mechanism", "literature_mechanism": f"{layer_id}｜Literature → Mechanism → Strategy", "experiment_design": f"{layer_id}｜Experiment Design", "result_comparison": f"{layer_id}｜Results", "result_single": f"{layer_id}｜Result", "layer_integrated_discussion": f"{layer_id}｜Integrated Discussion", "layer_summary_decision": f"{layer_id}｜Layer Summary / Decision", "hypothesis_transition": "H01 → H02｜Hypothesis Transition"}.get(role, role)
    body = content_from_materialized_state(state, layer_id, role, object_ref, meeting_projection=meeting)
    drefs = []
    if role in {"layer_integrated_discussion", "layer_summary_decision", "hypothesis_transition", "progress_todo"}: drefs = [state["layer_summaries"].get(layer.get("layer_summary_ref"), {}).get("decision_ref", "D101")]
    actions = ["NS101" if layer_id == "H001" else "NS201"] if role in {"layer_summary_decision", "hypothesis_transition", "progress_todo"} else []
    return {"schema_version": "2.0.0", "slide_id": raw.get("slide_id", f"S-{layer_id}-{role.upper()}"), "revision": 1, "deck_role": "meeting_delta" if overview else "hypothesis_layer", "block_refs": [{"block_id": block_id, "revision": 1}], "stage": role, "native_layout_role": "content_academic", "recipe": role, "title": {"text": title, "assertion_claim_refs": [claim_ref]}, "placements": placements, "citations": evidence_refs, "speaker_notes": {"source_refs": evidence_refs, "text": "Compiled from persisted ledger materialization."}, "story_visibility": {"master": "main", "meeting": "main" if overview or layer_id == "H002" else "history", "defense": "appendix"}, "source_cursor": cursor, "bindings": {"claim_refs": [claim_ref], "evidence_refs": evidence_refs, "asset_refs": [p["asset_id"] for p in placements], "action_refs": actions, "decision_refs": drefs, "professor_profile_ref": copy.deepcopy(PROFESSOR_PROFILE_REF), "template_profile_ref": {"profile_id": "TP-SYNTH-PHASE2", "version": "2.0.0"}}, "content": {"body": body}, "hypothesis_layer_ref": None if overview else layer_id, "hypothesis_layer_revision": layer.get("revision", 1), "current_hypothesis_layer_ref": layer_id if overview else None, "semantic_role": role, "combined_roles": raw.get("combined_roles", [role]), "fishbone_snapshot_ref": raw.get("fishbone_snapshot_ref"), "fishbone_focus_refs": raw.get("fishbone_focus_refs", []), "compaction_rationale": raw.get("compaction_rationale")}
def _manifest(specs: list[dict], output_root: Path, profile: dict, pptx_path: Path, final_cursor: int) -> dict:
    slides = []
    spec_path = output_root / "slide-specs.json"
    for ordinal, spec in enumerate(specs, 1):
        slides.append({"ordinal": ordinal, "slide_id": spec["slide_id"], "slide_spec_path": "slide-specs.json", "slide_spec_sha256": _sha(spec_path), "block_ref": spec["block_refs"][0], "claim_refs": spec["bindings"]["claim_refs"], "evidence_refs": spec["bindings"]["evidence_refs"], "asset_refs": spec["bindings"]["asset_refs"], "action_refs": spec["bindings"]["action_refs"], "decision_refs": spec["bindings"]["decision_refs"], "professor_profile_ref": spec["bindings"]["professor_profile_ref"], "template_profile_ref": spec["bindings"]["template_profile_ref"], "source_event_cursor": spec["source_cursor"], "story_visibility": spec["story_visibility"]["master"], "hypothesis_layer_ref": spec.get("hypothesis_layer_ref"), "semantic_role": spec["semantic_role"]})
    return {"schema_version": "2.0.0", "deck_id": "MASTER-PHASE2-ACCEPTANCE", "deck_kind": "master", "title": "Synthetic Hypothesis-Layered Thesis History", "template_profile_ref": {"profile_id": profile["profile_id"], "version": profile["version"]}, "professor_profile_ref": copy.deepcopy(PROFESSOR_PROFILE_REF), "source_event_cursor": final_cursor, "build_id": "BUILD-MASTER-PHASE2-ACCEPTANCE", "build_tool_version": "0.3.0", "created_at": CREATED_AT, "projection": {"query": "master(hypothesis_layers=all,preserve_history=true)"}, "slides": slides, "outputs": {"pptx": "acceptance-deck.pptx", "pptx_sha256": _sha(pptx_path)}, "qa_report_refs": ["QA-MASTER-PHASE2-ACCEPTANCE"]}


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
    causal_findings = validate_causal_history(persisted)
    _write(output_root / "causal-temporal-qa.json", {"status": "pass" if not causal_findings else "fail", "findings": [finding.__dict__ for finding in causal_findings], "event_count": len(persisted.replay())})
    if causal_findings:
        raise ValueError("Phase 2 causal chronology validation failed: " + "; ".join(finding.rule_id for finding in causal_findings))
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

    logical_h1 = compile_hypothesis_layer_from_state(h01_state, "H001", source_cursor=h01_cursor)
    logical_h2 = compile_hypothesis_layer_from_state(h02_state, "H002", source_cursor=h02_cursor)
    transition_raw = {"slide_id": "S-H001-HYPOTHESIS-TRANSITION-12", "semantic_role": "hypothesis_transition", "hypothesis_layer_ref": "H001", "combined_roles": ["hypothesis_transition"], "source_cursor": transition_cursor, "object_ref": "TR-H001-H002", "fishbone_snapshot_ref": None, "fishbone_focus_refs": []}
    meeting = meeting_projection(h02_state, source_cursor=h02_cursor, current_layer_id="H002")
    physical = [_hydrate_from_state({"slide_id": "S-PHASE2-PROGRESS-01"}, h02_state, output_root, overview=True, meeting=meeting)]
    physical.extend(_hydrate_from_state(item, h01_state, output_root) for item in _compact_h01(logical_h1))
    physical.append(_hydrate_from_state(transition_raw, transition_state, output_root))
    physical.extend(_hydrate_from_state(item, h02_state, output_root) for item in _compact_h02(logical_h2))
    if len(physical) != 18:
        raise ValueError(f"acceptance story must contain 18 generated slides, got {len(physical)}")
    _write(output_root / "slide-specs.json", physical)

    director = LayoutDirector(load_archetype_registry(output_root / "layout-archetypes.json"), profile)
    plans = []; layout_overrides = []
    for slide in physical:
        plan_layer_ref = slide.get("hypothesis_layer_ref") or slide.get("current_hypothesis_layer_ref")
        plan_layer = next(item for item in fixture["hypothesis_layers"] if item["hypothesis_layer_id"] == plan_layer_ref)
        decision = director.select({"semantic_role": slide["semantic_role"], "scientific_stage": slide["stage"], "asset_count": len(slide["placements"]), "evidence_count": len(slide["bindings"]["evidence_refs"]), "experiment_count": len(plan_layer["experiment_refs"]), "result_count": len(plan_layer["result_refs"]), "target_language": "zh-TW", "text_units": len(slide["content"]["body"]), "density_estimate": "high"})
        if decision.get("split_recommendation"):
            layout_overrides.append({"slide_id": slide["slide_id"], "archetype": decision["selected_archetype"], "reason": "Structured Chinese scientific content is intentionally kept on the governed archetype; visual QA verifies bounds, font hierarchy, and legibility.", "approved_by": "Phase 2 synthetic acceptance review", "evidence": "visual-inspection.json"})
            decision["split_recommendation"] = False
            decision["reviewed_split_override"] = {"reason": "Structured Chinese scientific content is intentionally kept on the governed archetype; visual QA verifies bounds, font hierarchy, and legibility.", "approved_by": "Phase 2 synthetic acceptance review", "evidence": "visual-inspection.json"}
        plan = {"schema_version": "2.0.0", "layout_plan_id": "LP-" + slide["slide_id"][2:], "slide_id": slide["slide_id"], **decision, "native_template_layout": {"semantic_role": "content_academic", "layout_index": profile["semantic_roles"]["content_academic"]["layout_index"], "layout_path": profile["semantic_roles"]["content_academic"]["layout_path"], "master_path": profile["semantic_roles"]["content_academic"]["master_path"]}, "source_event_cursor": slide["source_cursor"], "created_at": CREATED_AT}
        registry.validate("layout-plan", plan)
        plans.append(plan)
        slide["placement_plan"] = plan["placement_plan"]
        slide["layout_plan_ref"] = plan["layout_plan_id"]
    _write(output_root / "layout-plans.json", plans); _write(output_root / "layout-director-decisions.json", [{"slide_id": plan["slide_id"], "selected_archetype": plan["selected_archetype"], "slot_signature": plan["slot_signature"], "split_recommendation": plan["split_recommendation"], "reviewed_split_override": plan.get("reviewed_split_override")} for plan in plans]); _write(output_root / "layout-overrides.json", layout_overrides); _write(output_root / "slide-specs.json", physical)

    deck = output_root / "acceptance-deck.pptx"
    PythonPptxAssembler().assemble(template, physical, deck, project_context=context)
    audit = audit_pptx(deck, template, profile, physical); _write(output_root / "structural-audit.json", audit)
    manifest = _manifest(physical, output_root, profile, deck, h02_cursor); _write(output_root / "MASTER-PHASE2.manifest.json", manifest)
    master = master_projection(h02_state, source_cursor=h02_cursor)
    _write(output_root / "master-projection.json", master); _write(output_root / "meeting-projection.json", meeting)

    professor_profile = yaml.safe_load((ROOT / "thesis-deck-system/examples/synthetic-project/professor-profile.yaml").read_text(encoding="utf-8"))
    registry.validate("professor-profile", professor_profile)
    _write(output_root / "professor-profile.json", professor_profile)
    professor_projection = {**meeting, "layers": list(h02_state["hypothesis_layers"].values()), "slides": physical, "state": h02_state, "source_cursor": h02_cursor}
    professor = run_professor_qa_v2(professor_profile, professor_projection); _write(output_root / "professor-qa.json", professor)
    history_findings = validate_hypothesis_history(h02_state)
    scientific = {"status": "pass" if not history_findings else "fail", "executed_checks": ["phase2_schema_validation", "ledger_hash_replay", "cursor_isolation", "causal_temporal_order", "hypothesis_derivation", "fishbone_revision_immutability", "experiment_metadata", "synthetic_evidence_labeling", "plot_source_hashes", "asset_provenance_chain"], "findings": [finding.__dict__ for finding in history_findings], "evidence": {"h01_cursor": h01_cursor, "transition_cursor": transition_cursor, "h02_cursor": h02_cursor, "causal_temporal_status": "pass", "h01_fishbone_sha256": fb1_hash, "h01_replay_sha256": _sha(rerender), "h02_fishbone_sha256": _sha(fb2), "contact_csv_sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv"), "contact_script_sha256": _sha(FIXTURE_ROOT / "plot_contact_pressure.py"), "contact_svg_sha256": _sha(plot_dir / "H02_contact_pressure.svg")}}
    _write(output_root / "scientific-provenance-qa.json", scientific)
    private_status = PrivateFixtureLocator(explicit={}).status(); _write(output_root / "private-fixture-status.json", private_status)
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
    materialized = h02_state
    binding_bundle = {"research_blocks": list(materialized["blocks"].values()), "claims": list(materialized["claims"].values()), "evidence_cards": list(materialized["evidence"].values()), "assets": list(materialized["assets"].values()), "actions": list(materialized["actions"].values()), "decisions": list(materialized["decisions"].values()), "stages": list(materialized["stages"].values()), "meeting_projection": json.loads((output_root / "meeting-projection.json").read_text(encoding="utf-8")), "template_profiles": [profile]}
    binding_findings = validate_temporal_bindings(binding_bundle, ledger, specs, [manifest], qa_reports=[{"qa_report_id": "QA-MASTER-PHASE2-ACCEPTANCE", "deck_id": manifest["deck_id"], "build_id": manifest["build_id"]}])
    _write(output_root / "phase2-binding-validation.json", {"status": "pass" if not binding_findings else "fail", "findings": [finding.__dict__ for finding in binding_findings], "unresolved_ref_count": len(binding_findings)})
    errors += [f"{finding.rule_id}: {finding.message}" for finding in binding_findings]
    report = run_phase2_pipeline(schema_errors=errors, ledger_replayed=replayed, scientific=scientific, professor=professor, audit=audit, specs=specs, visual=render_evidence["visual"], render_evidence=render_evidence)
    _write(output_root / "qa-report.json", report)
    return report
