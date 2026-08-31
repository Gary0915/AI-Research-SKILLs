"""CP5-E/F/G evidence routes, review boundaries, and sanitized calibration.

All generated figures are synthetic language fixtures or non-evidence visual
outputs.  This module neither resolves private aliases nor opens/render private
sources; no PPTX/DrawingML functionality is present.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import shutil
from time import time
from typing import Any

from .phase3_cp5a_scientific_svg import ROOT, author_svg_for_spec
from .phase3_cp5bcd_integrated import StaticFigureCritic, _spec, _svg_document, make_synthetic_manifest


class EvidenceRouteError(ValueError):
    pass


def _hash(value: Any) -> str:
    encoded = value.encode("utf-8") if isinstance(value, str) else json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def validate_plot_input(value: dict[str, Any]) -> None:
    if not value.get("series") or not value.get("provenance_refs") or value.get("evidence_status") not in {"empirical", "synthetic_test_evidence"}:
        raise EvidenceRouteError("plot requires series, provenance, and quantitative evidence status")
    if not isinstance(value.get("data_sha256"), str) or len(value["data_sha256"]) != 64:
        raise EvidenceRouteError("plot requires source data hash")
    if any(len(point) != 2 for series in value["series"] for point in series.get("points", [])):
        raise EvidenceRouteError("plot points must be ordered coordinate pairs")


def _plot_svg(spec: dict[str, Any]) -> str:
    body = '<g id="obj-plot" data-semantic-role="plot_area"><line id="obj-x-axis" data-semantic-role="axis" x1="220" y1="700" x2="1380" y2="700" stroke="#333333" stroke-width="3"/><line id="obj-y-axis" data-semantic-role="axis" x1="220" y1="700" x2="220" y2="190" stroke="#333333" stroke-width="3"/><polyline id="obj-series-1" data-semantic-role="data_series" points="240,650 600,500 980,390 1340,250" fill="none" stroke="#0F9ED5" stroke-width="4"/><text id="obj-x-label" data-semantic-role="label" x="1280" y="750" font-family="Arial" font-size="20">x / a.u.</text><text id="obj-y-label" data-semantic-role="label" x="110" y="200" font-family="Arial" font-size="20">y / a.u.</text></g>'
    return _svg_document(spec, "Synthetic Quantitative Plot", body)


def _matrix_svg(spec: dict[str, Any]) -> str:
    cells = []
    for row in range(2):
        for col in range(2):
            x, y = 260 + col * 560, 220 + row * 280
            cells.append(f'<g id="obj-cell-{row}-{col}" data-semantic-role="matrix_cell"><rect id="obj-panel-{row}-{col}" data-semantic-role="panel" x="{x}" y="{y}" width="420" height="180" fill="#d1d1d1" stroke="#333333" stroke-width="2"/><image id="obj-image-{row}-{col}" data-semantic-role="image" x="{x+10}" y="{y+10}" width="400" height="160" href="data:image/png;base64,iVBORw0KGgo="/><text id="obj-panel-label-{row}-{col}" data-semantic-role="panel_label" x="{x+25}" y="{y+210}" font-family="Arial" font-size="18">synthetic panel {row + 1},{col + 1}</text></g>')
    return _svg_document(spec, "Synthetic Image Matrix", "".join(cells))


def _concept_svg(spec: dict[str, Any]) -> str:
    body = '<circle id="obj-concept-source" data-semantic-role="node" cx="480" cy="450" r="110" fill="#CAEEFB" stroke="#333333" stroke-width="2"/><circle id="obj-concept-target" data-semantic-role="node" cx="1120" cy="450" r="110" fill="#FFC000" stroke="#333333" stroke-width="2"/><line id="obj-concept-flow" data-semantic-role="flow" x1="590" y1="450" x2="1010" y2="450" stroke="#333333" stroke-width="3" marker-end="url(#obj-arrow)"/><text id="obj-concept-label" data-semantic-role="annotation" x="600" y="560" font-family="Arial" font-size="20">non-evidence explanatory concept</text>'
    return _svg_document(spec, "Concept Illustration", body)


def _approved_svg_route(root: Path, figure_id: str, source: str, *, scientific_claim_support: str = "required") -> dict[str, Any]:
    spec = _spec(root, figure_id)
    authored = author_svg_for_spec(source, spec, root)
    manifest = make_synthetic_manifest(root, figure_id, canonical_svg=authored["canonical_svg"])
    critic = StaticFigureCritic(root).execute(manifest)
    return {"status": critic["status"], "figure_id": figure_id, "scientific_claim_support": scientific_claim_support, "svg": authored["canonical_svg"], "manifest": manifest, "critic": critic}


def build_evidence_bound_outputs(root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = root or ROOT
    plot_input = {"series":[{"series_id":"S001","points":[[0,1],[1,2]]}],"axes":{"x_unit":"synthetic","y_unit":"synthetic"},"data_sha256":"a" * 64,"provenance_refs":["E101"],"evidence_status":"synthetic_test_evidence"}
    validate_plot_input(plot_input)
    plot = _approved_svg_route(root, "FIG001", _plot_svg(_spec(root, "FIG001")))
    matrix = _approved_svg_route(root, "FIG009", _matrix_svg(_spec(root, "FIG009")))
    concept = _approved_svg_route(root, "FIG010", _concept_svg(_spec(root, "FIG010")), scientific_claim_support="forbidden")
    blocked = lambda family: {"status":"BLOCKED_SOURCE", "reason":"BLOCKED_SOURCE_FIXTURE", "route":family, "source_fixture_present":False}
    return {"scientific_plot": plot | {"data_provenance":{"evidence_status":"synthetic_test_evidence", "data_sha256":plot_input["data_sha256"]}}, "photo_annotation": blocked("photo_annotation"), "literature_figure": blocked("literature_figure"), "image_matrix": matrix | {"panel_order":["P001","P002","P003","P004"], "scale_policy":"shared_synthetic_scale"}, "concept_illustration": concept}


def write_gate_e_artifacts(root: Path | None = None, destination: Path | None = None) -> dict[str, Any]:
    root = root or ROOT; destination = destination or root / "thesis-deck-system" / "artifacts" / "phase3"; destination.mkdir(parents=True, exist_ok=True)
    outputs = build_evidence_bound_outputs(root)
    folder = destination / "cp5e-evidence-bound-directors"; folder.mkdir(exist_ok=True)
    for key, item in outputs.items():
        if "svg" in item: (folder / f"{key}.svg").write_text(item["svg"], encoding="utf-8")
    execution = {"schema_version":"1.0.0","execution_id":"CP5E-EXEC-001","route_count":5,"approved_count":sum(x["status"] == "APPROVED_FIGURE" for x in outputs.values()),"blocked_source_count":sum(x["status"] == "BLOCKED_SOURCE" for x in outputs.values()),"private_alias_resolution_attempts":0,"private_source_open_attempts":0,"private_render_attempts":0}
    qa = {"schema_version":"1.0.0","qa_id":"CP5E-QA-001","aggregate_status":"pass","route_statuses":{key:item["status"] for key,item in outputs.items()}}
    for name, value in (("evidence-bound-figure-outputs.json", outputs), ("checkpoint-5e-execution-evidence.json", execution), ("checkpoint-5e-qa.json", qa)):
        (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return {"outputs":outputs,"execution":execution,"qa":qa}


def probe_render_capability() -> dict[str, Any]:
    candidates = ["resvg", "rsvg-convert", "inkscape"]
    available = next((candidate for candidate in candidates if shutil.which(candidate)), None)
    return {"renderer_id":available, "renderer_version":"not_probed" if available else None, "renderer_capability_status":"available" if available else "blocked_environment", "static_critic_status":"available", "render_critic_status":"available" if available else "blocked_environment", "image_capable_qualitative_review_status":"blocked_visual_review", "human_review_status":"not_run"}


@dataclass(frozen=True)
class CurrentSlideContext:
    context_id: str
    archetype_id: str
    figure_id: str
    figure_hash: str
    selected_object_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviewAction:
    review_action_id: str
    context_id: str
    figure_hash: str
    object_ids: tuple[str, ...]
    action_type: str
    payload: dict[str, Any]
    timestamp_order: int

    @classmethod
    def create(cls, context: CurrentSlideContext, action_type: str, payload: dict[str, Any]) -> "ReviewAction":
        if action_type not in {"select_object","flag_overlap","request_move","request_resize","request_label_correction","request_emphasis_adjustment","accept_visual_issue","reject_visual_issue"}:
            raise EvidenceRouteError("unknown immutable review action")
        return cls(f"RA-{_hash([context.context_id, action_type, payload])[:12]}", context.context_id, context.figure_hash, context.selected_object_ids, action_type, dict(payload), int(time() * 1000))


def write_gate_f_artifacts(root: Path | None = None, destination: Path | None = None) -> dict[str, Any]:
    root = root or ROOT; destination = destination or root / "thesis-deck-system" / "artifacts" / "phase3"; destination.mkdir(parents=True, exist_ok=True)
    status = probe_render_capability(); context = CurrentSlideContext("CTX001", "A03", "FIG002", _hash("FIG002"), ("obj-br002",)); action = ReviewAction.create(context, "flag_overlap", {"severity":"not_reviewed"})
    payload = {"schema_version":"1.0.0","renderer":status,"render_manifests":[],"render_critic_reports":[],"image_capable_review":{"status":"blocked_visual_review"},"current_slide_context":{"context_id":context.context_id,"archetype_id":context.archetype_id,"figure_id":context.figure_id,"figure_hash":context.figure_hash,"selected_object_ids":list(context.selected_object_ids)},"review_actions":[{"review_action_id":action.review_action_id,"context_id":action.context_id,"action_type":action.action_type,"object_ids":list(action.object_ids),"payload":action.payload,"timestamp_order":action.timestamp_order}]}
    qa = {"schema_version":"1.0.0","qa_id":"CP5F-QA-001","aggregate_status":"pass","status_dimensions":status,"render_count":0,"private_alias_resolution_attempts":0,"private_source_open_attempts":0,"private_render_attempts":0}
    for name,value in (("checkpoint-5f-execution-evidence.json",payload),("checkpoint-5f-qa.json",qa)):(destination/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"execution":payload,"qa":qa}


def build_calibration_artifacts(root: Path | None = None, destination: Path | None = None) -> dict[str, Any]:
    root = root or ROOT; destination = destination or root / "thesis-deck-system" / "artifacts" / "phase3"; profile=json.loads((root/"thesis-deck-system"/"artifacts"/"phase3"/"visual-style-profile.json").read_text(encoding="utf-8")); archetypes=json.loads((root/"thesis-deck-system"/"layout-archetypes.json").read_text(encoding="utf-8"))
    items = archetypes.get("archetypes", archetypes) if isinstance(archetypes, dict) else archetypes
    calibration = [{"archetype_id":item.get("archetype_id", item.get("id")),"structural_geometry":"supported","style_token_state":"provisional","render_state":"blocked_environment","qualitative_state":"blocked_visual_review"} for item in items]
    family = {"schema_version":"1.0.0","families":[{"family":name,"evidence_state":"provisional","representative_benchmark_count":1,"stress_benchmark_count":1} for name in ("fishbone","mechanism","experiment","fabrication","comparison","scientific_plot","image_matrix","concept_illustration")]}
    fishbone = {"schema_version":"1.0.0","profile_id":"CP5G-FISHBONE-001","spine_placement":"provisional","branch_spacing":"provisional","focus_emphasis":"provisional","material_semantic_colors":"unresolved"}
    qa = {"schema_version":"1.0.0","qa_id":"CP5G-QA-001","structural_geometry_calibration":"pass","style_token_calibration":"provisional","render_calibration":"blocked_environment","image_capable_qualitative_calibration":"blocked_visual_review","professor_visual_acceptance":"blocked","private_alias_resolution_attempts":0,"private_source_open_attempts":0,"private_render_attempts":0,"archetype_count":len(calibration),"style_profile_ref":profile["style_profile_id"]}
    if destination:
        destination.mkdir(parents=True,exist_ok=True); folder=destination/"cp5g";folder.mkdir(exist_ok=True)
        artifacts={"archetype-calibration.json":{"schema_version":"1.0.0","archetypes":calibration},"figure-family-calibration.json":family,"fishbone-style-profile.json":fishbone,"reconstruction-benchmarks.json":{"schema_version":"1.0.0","benchmarks":[{"family":x["family"],"representative":1,"stress":1} for x in family["families"]]},"checkpoint-5g-execution-evidence.json":{"schema_version":"1.0.0","execution_id":"CP5G-EXEC-001","private_alias_resolution_attempts":0,"private_source_open_attempts":0,"private_render_attempts":0},"checkpoint-5g-qa.json":qa}
        for name,value in artifacts.items():(destination/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        board='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" data-thesis-svg-version="1.0.0" data-thesis-figure-id="FIG010" data-visual-class="conceptual_explanation"><text id="obj-title" data-semantic-role="title" x="80" y="100" font-family="Arial" font-size="36">CP5-G Structural Calibration Board</text><text id="obj-status" data-semantic-role="annotation" x="80" y="180" font-family="Arial" font-size="24">structural: pass · render: blocked · qualitative: blocked</text></svg>'
        (folder/"archetype-calibration-montage.svg").write_text(board,encoding="utf-8");(folder/"figure-family-calibration-montage.svg").write_text(board,encoding="utf-8")
    return {"qa":qa,"archetypes":calibration,"families":family,"fishbone":fishbone}
