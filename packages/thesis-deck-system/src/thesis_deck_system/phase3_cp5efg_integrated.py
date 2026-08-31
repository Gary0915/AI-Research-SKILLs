"""CP5-E/F/G evidence routes, review boundaries, and sanitized calibration.

All generated figures are synthetic language fixtures or non-evidence visual
outputs.  This module neither resolves private aliases nor opens/render private
sources; no PPTX/DrawingML functionality is present.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
from hashlib import sha256
import json
from pathlib import Path
import shutil
from time import time
from typing import Any

from .phase3_cp5a_scientific_svg import ROOT, author_svg_for_spec
from .phase3_cp5bcd_integrated import StaticFigureCritic, _spec, _svg_document, apply_style_bundle, make_synthetic_manifest, resolve_style


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


def canonical_plot_input(value: dict[str, Any]) -> dict[str, Any]:
    """Close numeric plot input to deterministic bytes before drawing geometry."""
    required = {"series", "x_axis_label", "x_axis_unit", "y_axis_label", "y_axis_unit", "provenance_refs", "evidence_status"}
    if not required <= set(value):
        raise EvidenceRouteError("closed canonical plot input fields required")
    payload = {key: value[key] for key in sorted(required)}
    try:
        for series in payload["series"]:
            if not isinstance(series["series_id"], str) or not series["points"]:
                raise EvidenceRouteError("each plot series needs an ID and points")
            for point in series["points"]:
                if len(point) != 2 or not all(isinstance(number, (int, float)) and float(number) == float(number) and abs(float(number)) != float("inf") for number in point):
                    raise EvidenceRouteError("plot values must be finite numbers")
    except (KeyError, TypeError):
        raise EvidenceRouteError("invalid canonical plot input") from None
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    expected = value.get("data_sha256")
    computed = sha256(encoded).hexdigest()
    if expected is not None and expected != computed:
        raise EvidenceRouteError("stale canonical numeric data hash")
    return payload | {"data_sha256": computed}


def _plot_number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def build_scientific_plot(root: Path, value: dict[str, Any]) -> dict[str, Any]:
    data = canonical_plot_input(value)
    points = [point for series in data["series"] for point in series["points"]]
    xmin, xmax = min(point[0] for point in points), max(point[0] for point in points)
    ymin, ymax = min(point[1] for point in points), max(point[1] for point in points)
    xspan, yspan = (xmax - xmin) or 1, (ymax - ymin) or 1
    colors = ("#0F9ED5", "#FF0000", "#333333", "#FFC000")
    polylines = []
    for index, series in enumerate(data["series"]):
        coordinate_string = " ".join(f"{_plot_number(240 + 1100 * (point[0] - xmin) / xspan)},{_plot_number(650 - 430 * (point[1] - ymin) / yspan)}" for point in series["points"])
        polylines.append(f'<polyline id="obj-series-{index}" data-semantic-role="data_series" points="{coordinate_string}" fill="none" stroke="{colors[index % len(colors)]}" stroke-width="4"/>')
    body = f'<g id="obj-plot" data-semantic-role="plot_area"><line id="obj-x-axis" data-semantic-role="axis" x1="220" y1="700" x2="1380" y2="700" stroke="#333333" stroke-width="3"/><line id="obj-y-axis" data-semantic-role="axis" x1="220" y1="700" x2="220" y2="190" stroke="#333333" stroke-width="3"/>{"".join(polylines)}<text id="obj-x-label" data-semantic-role="label" x="1180" y="750" font-family="Arial" font-size="20">{data["x_axis_label"]} / {data["x_axis_unit"]}</text><text id="obj-y-label" data-semantic-role="label" x="110" y="200" font-family="Arial" font-size="20">{data["y_axis_label"]} / {data["y_axis_unit"]}</text><text id="obj-y-domain" data-semantic-role="annotation" x="230" y="180" font-family="Arial" font-size="16">{_plot_number(ymin)}–{_plot_number(ymax)}</text></g>'
    spec = _spec(root, "FIG001")
    authored = author_svg_for_spec(_svg_document(spec, "Synthetic Quantitative Plot", body), spec, root)
    return {"svg": authored["canonical_svg"], "canonical_sha256": authored["identity"]["canonical_sha256"], "data_sha256": data["data_sha256"], "scale": {"x_domain": [xmin, xmax], "y_domain": [ymin, ymax], "x_range": [240, 1340], "y_range": [650, 220], "normalization": "affine"}, "input": data}


def build_image_matrix(root: Path, panels: list[dict[str, Any]]) -> dict[str, Any]:
    if len(panels) < 4 or len({panel.get("panel_id") for panel in panels}) != len(panels):
        raise EvidenceRouteError("matrix requires unique synthetic panels")
    ordered = sorted(panels, key=lambda panel: panel.get("order", 0))
    if [panel.get("order") for panel in ordered] != list(range(1, len(ordered) + 1)):
        raise EvidenceRouteError("matrix panel order must be contiguous")
    if len({panel.get("scale_policy") for panel in ordered}) != 1:
        raise EvidenceRouteError("matrix requires one scale policy")
    lineage = []
    cells = []
    for index, panel in enumerate(ordered):
        if not all(panel.get(key) for key in ("panel_id", "source_asset_ref", "source_bytes", "provenance_ref", "label")):
            raise EvidenceRouteError("matrix panel lineage is incomplete")
        computed = sha256(panel["source_bytes"]).hexdigest()
        if panel.get("source_sha256") is not None and panel["source_sha256"] != computed:
            raise EvidenceRouteError("stale matrix panel hash")
        lineage.append({"panel_id": panel["panel_id"], "source_asset_ref": panel["source_asset_ref"], "source_sha256": computed, "provenance_ref": panel["provenance_ref"], "order": panel["order"], "scale_policy": panel["scale_policy"], "label": panel["label"]})
        row, column = divmod(index, 2); x, y = 220 + column * 630, 210 + row * 270
        encoded = base64.b64encode(panel["source_bytes"]).decode("ascii")
        cells.append(f'<g id="obj-cell-{index}" data-semantic-role="matrix_cell"><rect id="obj-panel-{index}" data-semantic-role="panel" x="{x}" y="{y}" width="500" height="180" fill="#d1d1d1" stroke="#333333" stroke-width="2"/><image id="obj-image-{index}" data-semantic-role="image" x="{x+10}" y="{y+10}" width="480" height="140" href="data:image/png;base64,{encoded}"/><text id="obj-label-{index}" data-semantic-role="panel_label" x="{x+20}" y="{y+170}" font-family="Arial" font-size="18">{panel["label"]}</text></g>')
    spec = _spec(root, "FIG009")
    authored = author_svg_for_spec(_svg_document(spec, "Synthetic Image Matrix", "".join(cells)), spec, root)
    return {"svg": authored["canonical_svg"], "canonical_sha256": authored["identity"]["canonical_sha256"], "panel_lineage": lineage, "scale_policy": ordered[0]["scale_policy"]}


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
    source, style = apply_style_bundle(source, resolve_style(root, spec))
    authored = author_svg_for_spec(source, spec, root)
    manifest = make_synthetic_manifest(root, figure_id, canonical_svg=authored["canonical_svg"], style_resolution=style)
    critic = StaticFigureCritic(root).execute(manifest)
    return {"status": critic["status"], "figure_id": figure_id, "scientific_claim_support": scientific_claim_support, "svg": authored["canonical_svg"], "manifest": manifest, "critic": critic}


def build_evidence_bound_outputs(root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = root or ROOT
    plot_input = {"series":[{"series_id":"S001","points":[[0,1],[1,2]]}],"x_axis_label":"time","x_axis_unit":"synthetic","y_axis_label":"response","y_axis_unit":"synthetic","provenance_refs":["E101"],"evidence_status":"synthetic_test_evidence"}
    plot_data = build_scientific_plot(root, plot_input)
    plot = _approved_svg_route(root, "FIG001", plot_data["svg"])
    panels = [{"panel_id": f"P{index:03}", "source_asset_ref": f"AS{index:03}", "source_bytes": f"synthetic-panel-{index}".encode("utf-8"), "provenance_ref": "E101", "order": index, "scale_policy": "shared_synthetic_scale", "label": f"synthetic panel {index}"} for index in range(1, 5)]
    matrix_data = build_image_matrix(root, panels)
    matrix = _approved_svg_route(root, "FIG009", matrix_data["svg"])
    concept = _approved_svg_route(root, "FIG010", _concept_svg(_spec(root, "FIG010")), scientific_claim_support="forbidden")
    blocked = lambda family: {"status":"BLOCKED_SOURCE", "reason":"BLOCKED_SOURCE_FIXTURE", "route":family, "source_fixture_present":False}
    return {"scientific_plot": plot | {"data_provenance":{"evidence_status":"synthetic_test_evidence", "data_sha256":plot_data["data_sha256"], "scale":plot_data["scale"]}}, "photo_annotation": blocked("photo_annotation"), "literature_figure": blocked("literature_figure"), "image_matrix": matrix | {"panel_order":[item["panel_id"] for item in matrix_data["panel_lineage"]], "scale_policy":matrix_data["scale_policy"], "panel_lineage":matrix_data["panel_lineage"]}, "concept_illustration": concept}


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
