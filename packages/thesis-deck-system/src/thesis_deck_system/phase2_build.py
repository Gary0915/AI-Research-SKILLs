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
from .contracts import SchemaRegistry
from .fishbone import render_fishbone_svg
from .hypothesis import validate_hypothesis_history
from .layout import LayoutDirector, load_archetype_registry
from .ledger import Ledger
from .phase2_projections import master_projection, meeting_projection
from .pptx import PythonPptxAssembler, audit_pptx
from .private_fixtures import PrivateFixtureLocator
from .qa2 import run_phase2_pipeline, run_professor_qa_v2
from .story import compile_hypothesis_layer
from .template import create_synthetic_template, profile_template


ROOT = ProjectContext.discover(Path(__file__)).repo_root
FIXTURE_ROOT = ROOT / "thesis-deck-system/examples/synthetic-project/phase2"
SCHEMA_ROOT = ROOT / "thesis-deck-system/schemas"
ARCHETYPE_PATH = ROOT / "thesis-deck-system/layout-archetypes.json"
CREATED_AT = "2026-08-27T00:00:00Z"


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


def _append_phase2_history(fixture: dict) -> tuple[Ledger, int, int]:
    ledger = Ledger()
    fishbone1, fishbone2 = fixture["fishbone_revisions"]
    p101, p201 = fixture["problems"]
    d1, d2 = fixture["layer_discussions"]
    s1, s2 = fixture["layer_summaries"]
    h1, h2 = fixture["hypothesis_layers"]
    experiments = fixture["experiments"]
    results = fixture["results"]
    events = [
        ("fishbone_created", fishbone1),
        ("claim_created", {"claim_id": "C101", "revision": 1, "claim_type": "hypothesis", "text": "Bulk conductivity dominates positional instability.", "source_event_cursor": 2}),
        ("problem_created", p101),
        ("evidence_linked", {"evidence_id": "E101", "kind": "synthetic_measurement", "source_event_cursor": 4}),
        ("evidence_linked", {"evidence_id": "E102", "kind": "synthetic_measurement", "source_event_cursor": 5}),
        ("layer_discussion_recorded", d1),
        ("decision_recorded", {"decision_id": "D101", "choice": "Partial-Go", "rationale": "Bulk conductivity is contributory but insufficient.", "source_event_cursor": 7}),
        ("action_committed", {"action_item_id": "NS101", "title": "Matched-conductivity contact-pressure test", "owner": "Gary", "target_window": {"start": "2026-09-01", "due": "2026-09-10"}, "dependencies": ["pressure fixture"], "parallelizable": True, "status": "done", "source_event_cursor": 8}),
        ("layer_summary_recorded", s1),
        ("stage_revised", {"stage_id": "EXP101", "stage_type": "experiment", "data": experiments["EXP101"], "source_event_cursor": 10}),
        ("stage_revised", {"stage_id": "EXP102", "stage_type": "experiment", "data": experiments["EXP102"], "source_event_cursor": 11}),
        ("stage_revised", {"stage_id": "RES101", "stage_type": "result", "data": results["RES101"], "source_event_cursor": 12}),
        ("stage_revised", {"stage_id": "RES102", "stage_type": "result", "data": results["RES102"], "source_event_cursor": 13}),
        ("hypothesis_layer_created", h1),
        ("fishbone_revised", fishbone2),
        ("claim_created", {"claim_id": "C201", "revision": 1, "claim_type": "hypothesis", "text": "Contact resistance dominates instability under low contact pressure.", "source_event_cursor": 16}),
        ("problem_created", p201),
        ("evidence_linked", {"evidence_id": "E201", "kind": "synthetic_measurement", "source_event_cursor": 18}),
        ("hypothesis_transition_recorded", fixture["hypothesis_transition"]),
        ("layer_discussion_recorded", d2),
        ("decision_recorded", {"decision_id": "D201", "choice": "Go", "rationale": "Contact-pressure control discriminates the interface mechanism.", "source_event_cursor": 21}),
        ("action_committed", {"action_item_id": "NS201", "title": "High-pressure cycling durability", "owner": "Gary", "target_window": {"start": "2026-09-11", "due": "2026-09-24"}, "dependencies": ["cycling fixture"], "parallelizable": True, "status": "planned", "source_event_cursor": 22}),
        ("layer_summary_recorded", s2),
        ("stage_revised", {"stage_id": "EXP201", "stage_type": "experiment", "data": experiments["EXP201"], "source_event_cursor": 24}),
        ("stage_revised", {"stage_id": "RES201", "stage_type": "result", "data": results["RES201"], "source_event_cursor": 25}),
        ("hypothesis_layer_created", h2),
    ]
    for event_type, payload in events:
        event = ledger.append(event_type, payload)
        declared = payload.get("source_event_cursor")
        if declared is not None and declared != event.cursor:
            raise ValueError(f"fixture cursor mismatch for {event_type}: {declared} != {event.cursor}")
    return ledger, 14, 26


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


def _hydrate(raw: dict, fixture: dict, output_root: Path, *, overview: bool = False) -> dict:
    if overview:
        layer_id, cursor, claim_ref, block_id, evidence_refs = "H002", 26, "C201", "B201", ["E201"]
        role = "progress_todo"
        raw = {"slide_id": "S-PHASE2-PROGRESS-01", "semantic_role": role, "combined_roles": [role], "source_cursor": cursor, "hypothesis_layer_ref": None, "hypothesis_layer_revision": None, "current_hypothesis_layer_ref": layer_id, "object_ref": "NS201", "fishbone_snapshot_ref": None, "fishbone_focus_refs": []}
    else:
        layer_id = raw["hypothesis_layer_ref"]
        layer = next(item for item in fixture["hypothesis_layers"] if item["hypothesis_layer_id"] == layer_id)
        cursor, claim_ref, block_id = layer["source_event_cursor"], layer["hypothesis_claim_ref"], layer["research_block_refs"][0]
        evidence_refs = ["E101", "E102"] if layer_id == "H001" else ["E201"]
        role = raw["semantic_role"]
    title_map = {
        "progress_todo": "Progress / Previous Commitments",
        "hypothesis_title": f"{layer_id}｜Hypothesis",
        "problem_definition": f"{layer_id}｜Problem",
        "fishbone_locator": f"{layer_id}｜Total Fishbone / Research Map",
        "observation_problem": f"{layer_id}｜Observation → Literature → Mechanism",
        "literature_mechanism": f"{layer_id}｜Literature → Mechanism → Strategy",
        "experiment_design": f"{layer_id}｜Experiment Design",
        "result_comparison": f"{layer_id}｜Results",
        "result_single": f"{layer_id}｜Result",
        "layer_integrated_discussion": f"{layer_id}｜Integrated Discussion",
        "layer_summary_decision": f"{layer_id}｜Layer Summary / Decision",
        "hypothesis_transition": "H01 → H02｜Hypothesis Transition",
    }
    body = _content_text(role, layer_id, fixture, raw.get("object_ref"))
    placements = []
    if role == "fishbone_locator":
        asset_id = "A101" if layer_id == "H001" else "A102"
        revision = 1 if layer_id == "H001" else 2
        placements = [{"slot": "primary_figure", "asset_id": asset_id, "asset_path": f"fishbone/FB001-rev{revision}.svg"}]
    elif role in {"result_single", "result_comparison"}:
        if layer_id == "H001":
            placements = [{"slot": "primary_figure", "asset_id": "A001", "asset_path": "plots/B001_defect_density.svg"}]
        else:
            placements = [{"slot": "primary_figure", "asset_id": "A201", "asset_path": "plots/H02_contact_pressure.svg"}]
    return {
        "schema_version": "2.0.0", "slide_id": raw["slide_id"], "revision": 1, "deck_role": "meeting_delta" if overview else "hypothesis_layer",
        "block_refs": [{"block_id": block_id, "revision": 1}], "stage": role, "native_layout_role": "content_academic", "recipe": role,
        "title": {"text": title_map.get(role, role), "assertion_claim_refs": [claim_ref]}, "placements": placements, "citations": evidence_refs,
        "speaker_notes": {"source_refs": evidence_refs, "text": "Synthetic Phase 2 fixture; source refs are ledger-derived."},
        "story_visibility": {"master": "main", "meeting": "main" if layer_id == "H002" or overview else "history", "defense": "appendix"},
        "source_cursor": cursor,
        "bindings": {"claim_refs": [claim_ref], "evidence_refs": evidence_refs, "asset_refs": [item["asset_id"] for item in placements], "action_refs": ["NS101" if layer_id == "H001" else "NS201"] if role in {"progress_todo", "layer_summary_decision", "hypothesis_transition"} else [], "decision_refs": ["D101" if layer_id == "H001" else "D201"] if role in {"layer_integrated_discussion", "layer_summary_decision", "hypothesis_transition", "progress_todo"} else [], "professor_profile_ref": {"profile_id": "PROF-SYNTH-001", "version": "2.0.0"}, "template_profile_ref": {"profile_id": "TP-SYNTH-PHASE2", "version": "2.0.0"}},
        "content": {"body": body}, "hypothesis_layer_ref": raw.get("hypothesis_layer_ref", layer_id), "hypothesis_layer_revision": raw.get("hypothesis_layer_revision", 1), "current_hypothesis_layer_ref": raw.get("current_hypothesis_layer_ref"), "semantic_role": role,
        "combined_roles": raw.get("combined_roles", [role]), "fishbone_snapshot_ref": raw.get("fishbone_snapshot_ref"), "fishbone_focus_refs": raw.get("fishbone_focus_refs", []),
        "compaction_rationale": raw.get("compaction_rationale"),
    }


def _content_text(role: str, layer_id: str, fixture: dict, object_ref) -> str:
    layer = next(item for item in fixture["hypothesis_layers"] if item["hypothesis_layer_id"] == layer_id)
    problem = next(item for item in fixture["problems"] if item["problem_id"] == layer["problem_ref"])
    discussion = next(item for item in fixture["layer_discussions"] if item["discussion_id"] == layer["layer_discussion_ref"])
    summary = next(item for item in fixture["layer_summaries"] if item["summary_id"] == layer["layer_summary_ref"])
    if role == "progress_todo":
        return "Prior commitment｜NS101 matched-conductivity pressure test：done\nCurrent position｜H02 / FB-ELECTRODE-CONTACT\nNext｜NS201 high-pressure cycling；Owner: Gary；Due: 2026-09-24\nParallel work｜cycling fixture + electrode geometry review"
    if role == "hypothesis_title":
        return ("目前相信｜Bulk conductivity 主導位置不穩定。" if layer_id == "H001" else "目前相信｜低接觸壓力下，Contact resistance 主導訊號不穩定。") + "\nFalsifier｜" + ("導電度提升後重複性仍不改善。" if layer_id == "H001" else "匹配導電度後，改變接觸壓力不影響 CV。")
    if role == "problem_definition":
        return f"Unresolved problem｜{problem['problem_statement']}\nPrevious finding｜{'; '.join(problem['previous_findings'])}\nConflict｜{problem['unresolved_conflict']}\nResearch question｜{problem['research_question']}\nRemaining uncertainty｜{problem['scope']}"
    if role == "fishbone_locator":
        return f"Historical snapshot｜FB001 rev{layer['fishbone_snapshot_ref']['revision']}\nFocus branch｜{', '.join(layer['fishbone_focus_refs'])}\nOld layer topology is immutable; current overview uses latest revision."
    if role in {"observation_problem", "literature_mechanism"}:
        if layer_id == "H001":
            return "Observation｜缺陷密度沿位置增加，訊號 CV 同步升高。\nLiterature synthesis｜transport gradient 可改變 bulk conductivity；但 interface variability 仍是 alternative。\nMechanism｜含水量梯度 → conductivity gradient。\nStrategy｜提升並均化含水量，再檢查 CV 是否同步下降。"
        return "Observation｜H01 提升 conductivity，但 CV 未改善。\nLiterature synthesis｜bulk transport 與 interface contact 可產生不同可辨識預測。\nMechanism｜低壓造成 contact resistance 波動。\nStrategy｜匹配 bulk conductivity，僅改變 contact pressure。"
    if role == "experiment_design":
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        return "\n\n".join(f"{ref}｜{fixture['experiments'][ref]['title']}\nIV: {', '.join(fixture['experiments'][ref]['independent_variables'])}｜Control: {', '.join(fixture['experiments'][ref]['controls_baselines'])}\nN: {fixture['experiments'][ref]['sample_replicates']}｜Metric/units: {', '.join(fixture['experiments'][ref]['measured_outputs_metrics'])} / {', '.join(fixture['experiments'][ref]['units'])}\nDecision rule: {fixture['experiments'][ref]['decision_rule']}" for ref in refs)
    if role in {"result_single", "result_comparison"}:
        refs = object_ref if isinstance(object_ref, list) else [object_ref]
        result_refs = [ref for ref in refs if str(ref).startswith("RES")]
        if not result_refs:
            result_refs = layer["result_order"]
        return "\n".join(f"{ref}｜{fixture['results'][ref]['finding']}" for ref in result_refs)
    if role == "layer_integrated_discussion":
        return f"Supporting｜{', '.join(discussion['supporting_results'])}\nContradicting｜{', '.join(discussion['contradicting_results']) or 'none'}\nCross-experiment pattern｜{discussion['cross_experiment_pattern']}\nMechanism assessment｜{discussion['mechanism_assessment']}\nAlternatives｜{'; '.join(discussion['alternative_explanations'])}\nRemaining uncertainty｜{discussion['remaining_uncertainty']}"
    if role == "layer_summary_decision":
        return f"Answered｜{summary['answered']}\nEvidence｜{', '.join(summary['supporting_evidence_refs'])}\nHypothesis status｜{summary['hypothesis_status']}\nDecision｜{summary['decision_ref']}\nUnresolved｜{summary['remaining_unresolved']}\nNext question｜{summary['next_question']}\nNext Step｜{', '.join(summary['next_step_refs'])}｜Owner: Gary｜Timing committed"
    transition = fixture["hypothesis_transition"]
    return f"Previous hypothesis｜{transition['previous_hypothesis_claim_ref']}\nKey results｜{', '.join(transition['key_result_refs'])}\nNot explained｜{transition['unexplained']}\nNew observation｜{', '.join(transition['observation_or_uncertainty_refs'])}\nTherefore｜{transition['rationale']}\nNew hypothesis｜{transition['new_hypothesis_claim_ref']}"


def _manifest(specs: list[dict], output_root: Path, profile: dict, pptx_path: Path, final_cursor: int) -> dict:
    slides = []
    spec_path = output_root / "slide-specs.json"
    for ordinal, spec in enumerate(specs, 1):
        slides.append({"ordinal": ordinal, "slide_id": spec["slide_id"], "slide_spec_path": "slide-specs.json", "slide_spec_sha256": _sha(spec_path), "block_ref": spec["block_refs"][0], "claim_refs": spec["bindings"]["claim_refs"], "evidence_refs": spec["bindings"]["evidence_refs"], "asset_refs": spec["bindings"]["asset_refs"], "action_refs": spec["bindings"]["action_refs"], "decision_refs": spec["bindings"]["decision_refs"], "professor_profile_ref": spec["bindings"]["professor_profile_ref"], "template_profile_ref": spec["bindings"]["template_profile_ref"], "source_event_cursor": spec["source_cursor"], "story_visibility": spec["story_visibility"]["master"], "hypothesis_layer_ref": spec.get("hypothesis_layer_ref"), "semantic_role": spec["semantic_role"]})
    return {"schema_version": "2.0.0", "deck_id": "MASTER-PHASE2-ACCEPTANCE", "deck_kind": "master", "title": "Synthetic Hypothesis-Layered Thesis History", "template_profile_ref": {"profile_id": profile["profile_id"], "version": profile["version"]}, "professor_profile_ref": {"profile_id": "PROF-SYNTH-001", "version": "2.0.0"}, "source_event_cursor": final_cursor, "build_id": "BUILD-MASTER-PHASE2-ACCEPTANCE", "build_tool_version": "0.3.0", "created_at": CREATED_AT, "projection": {"query": "master(hypothesis_layers=all,preserve_history=true)"}, "slides": slides, "outputs": {"pptx": "acceptance-deck.pptx", "pptx_sha256": _sha(pptx_path)}, "qa_report_refs": ["QA-MASTER-PHASE2-ACCEPTANCE"]}


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

    ledger, h01_cursor, h02_cursor = _append_phase2_history(fixture)
    ledger.serialize(output_root / "ledger-events.json")
    persisted = Ledger.load(output_root / "ledger-events.json")
    h01_state = persisted.materialize(h01_cursor); h02_state = persisted.materialize(h02_cursor)
    _write(output_root / "materialized-h01.json", h01_state); _write(output_root / "materialized-h02.json", h02_state)

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

    template = create_synthetic_template(output_root / "synthetic-template.pptx")
    profile = _phase2_profile(template, output_root / "template-profile.json")
    profile["profile_id"] = "TP-SYNTH-PHASE2"; profile["version"] = "2.0.0"; _write(output_root / "template-profile.json", profile)
    shutil.copy2(ARCHETYPE_PATH, output_root / "layout-archetypes.json")
    visual_grammar = {"schema_version": "2.0.0", "grammar_id": "VG-SYNTH-PHASE2", "version": "2.0.0", "mode": "synthetic", "source_alias": "synthetic://layout-exemplar", "private_content_copied": False, "composition_rules": {"template_shell": ["EXEMPLAR-1", "EXEMPLAR-3"], "body_primary": "EXEMPLAR-2", "white_background": True, "figure_first": True, "structured_high_density": True}, "descriptors": [{"archetype_ref": item["archetype_id"], "dominant_content_region": "safe_content_bounds", "information_density": "high" if item["text_budget"] > 220 else "medium"} for item in archetypes]}
    _write(output_root / "visual-grammar.json", visual_grammar)

    plot_dir = output_root / "plots"; plot_dir.mkdir()
    source_plot_svg = ROOT / "thesis-deck-system/artifacts/phase1/plots/B001_defect_density.svg"
    source_plot_png = ROOT / "thesis-deck-system/artifacts/phase1/plots/B001_defect_density.png"
    if not source_plot_svg.exists() or not source_plot_png.exists():
        from .plotting import build_plot
        build_plot(ROOT / "thesis-deck-system/examples/synthetic-project/measurements.csv", plot_dir)
    else:
        shutil.copy2(source_plot_svg, plot_dir / "B001_defect_density.svg"); shutil.copy2(source_plot_png, plot_dir / "B001_defect_density.png")
    _load_plot_builder()(FIXTURE_ROOT / "contact-pressure.csv", plot_dir / "H02_contact_pressure.svg", plot_dir / "H02_contact_pressure.png")

    logical_h1 = compile_hypothesis_layer(fixture["hypothesis_layers"][0], source_cursor=h01_cursor)
    logical_h2 = compile_hypothesis_layer(fixture["hypothesis_layers"][1], source_cursor=h02_cursor)
    physical = [_hydrate({}, fixture, output_root, overview=True)]
    physical.extend(_hydrate(item, fixture, output_root) for item in _compact_h01(logical_h1))
    physical.extend(_hydrate(item, fixture, output_root) for item in _compact_h02(logical_h2))
    if len(physical) != 18:
        raise ValueError(f"acceptance story must contain 18 generated slides, got {len(physical)}")
    _write(output_root / "slide-specs.json", physical)

    director = LayoutDirector(load_archetype_registry(output_root / "layout-archetypes.json"), profile)
    plans = []
    for slide in physical:
        plan_layer_ref = slide.get("hypothesis_layer_ref") or slide.get("current_hypothesis_layer_ref")
        plan_layer = next(item for item in fixture["hypothesis_layers"] if item["hypothesis_layer_id"] == plan_layer_ref)
        decision = director.select({"semantic_role": slide["semantic_role"], "scientific_stage": slide["stage"], "asset_count": len(slide["placements"]), "evidence_count": len(slide["bindings"]["evidence_refs"]), "experiment_count": len(plan_layer["experiment_refs"]), "result_count": len(plan_layer["result_refs"]), "target_language": "zh-TW", "text_units": len(slide["content"]["body"]), "density_estimate": "high"})
        plan = {"schema_version": "2.0.0", "layout_plan_id": "LP-" + slide["slide_id"][2:], "slide_id": slide["slide_id"], **decision, "native_template_layout": {"semantic_role": "content_academic", "layout_index": profile["semantic_roles"]["content_academic"]["layout_index"], "layout_path": profile["semantic_roles"]["content_academic"]["layout_path"], "master_path": profile["semantic_roles"]["content_academic"]["master_path"]}, "source_event_cursor": slide["source_cursor"], "created_at": CREATED_AT}
        registry.validate("layout-plan", plan)
        plans.append(plan)
        slide["placement_plan"] = plan["placement_plan"]
        slide["layout_plan_ref"] = plan["layout_plan_id"]
    _write(output_root / "layout-plans.json", plans); _write(output_root / "slide-specs.json", physical)

    deck = output_root / "acceptance-deck.pptx"
    PythonPptxAssembler().assemble(template, physical, deck, project_context=context)
    audit = audit_pptx(deck, template, profile, physical); _write(output_root / "structural-audit.json", audit)
    manifest = _manifest(physical, output_root, profile, deck, h02_cursor); _write(output_root / "MASTER-PHASE2.manifest.json", manifest)
    master = master_projection(h02_state, source_cursor=h02_cursor); meeting = meeting_projection(h02_state, source_cursor=h02_cursor, current_layer_id="H002")
    _write(output_root / "master-projection.json", master); _write(output_root / "meeting-projection.json", meeting)

    professor_profile = {"profile_id": "PROF-SYNTH-001", "version": "2.0.0", "primary_language": "zh-TW", "rules": {"hypothesis_problem_separate": True, "fishbone_every_layer": True, "integrated_discussion_after_results": True}}
    professor_projection = {**meeting, "layers": list(h02_state["hypothesis_layers"].values()), "slides": physical}
    professor = run_professor_qa_v2(professor_profile, professor_projection); _write(output_root / "professor-qa.json", professor)
    history_findings = validate_hypothesis_history(h02_state)
    scientific = {"status": "pass" if not history_findings else "fail", "executed_checks": ["phase2_schema_validation", "ledger_hash_replay", "cursor_isolation", "hypothesis_derivation", "fishbone_revision_immutability", "experiment_metadata", "synthetic_evidence_labeling", "plot_source_hashes"], "findings": [finding.__dict__ for finding in history_findings], "evidence": {"h01_cursor": h01_cursor, "h02_cursor": h02_cursor, "h01_fishbone_sha256": fb1_hash, "h01_replay_sha256": _sha(rerender), "h02_fishbone_sha256": _sha(fb2), "contact_csv_sha256": _sha(FIXTURE_ROOT / "contact-pressure.csv"), "contact_script_sha256": _sha(FIXTURE_ROOT / "plot_contact_pressure.py"), "contact_svg_sha256": _sha(plot_dir / "H02_contact_pressure.svg")}}
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
    replayed = ledger.materialize(14) == json.loads((output_root / "materialized-h01.json").read_text(encoding="utf-8")) and ledger.materialize(26) == json.loads((output_root / "materialized-h02.json").read_text(encoding="utf-8"))
    scientific = json.loads((output_root / "scientific-provenance-qa.json").read_text(encoding="utf-8"))
    professor = json.loads((output_root / "professor-qa.json").read_text(encoding="utf-8"))
    audit = json.loads((output_root / "structural-audit.json").read_text(encoding="utf-8"))
    report = run_phase2_pipeline(schema_errors=errors, ledger_replayed=replayed, scientific=scientific, professor=professor, audit=audit, specs=specs, visual=render_evidence["visual"], render_evidence=render_evidence)
    _write(output_root / "qa-report.json", report)
    return report
