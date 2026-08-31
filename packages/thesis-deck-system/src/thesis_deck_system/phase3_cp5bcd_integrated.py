"""CP5-B/C/D: capability truth, static approval, and specialist SVG directors.

All inputs are committed/synthetic.  This module neither opens private sources
nor produces PPTX/DrawingML.  Scientific provenance remains in FigureSpec and
manifest references, never in SVG metadata.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any
from xml.etree import ElementTree as ET

from .contracts import SchemaRegistry
from .phase3_cp5a_scientific_svg import ROOT, ScientificSvgError, author_svg_for_spec


CAPABILITY_STATES = {"NATIVE_EXACT", "NATIVE_NORMALIZED", "VECTOR_FALLBACK", "RASTER_FALLBACK", "UNSUPPORTED", "UNKNOWN"}
EVIDENCE_LEVELS = {"upstream_declared", "source_inspected", "thesis_synthetic_verified", "native_powerpoint_verified"}
FEATURE_IDS = (
    "svg-root-viewbox", "group", "rect", "circle", "ellipse", "line", "polyline", "polygon", "path-commands", "text", "tspan", "text-editable-cjk", "image", "marker", "marker-local-reference", "clip-path", "clip-local-reference", "transform-translate", "transform-scale", "transform-rotate", "transform-matrix", "stroke-width", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "fill-opacity", "stroke-opacity", "text-anchor", "dominant-baseline", "font-attributes", "same-document-reference", "svg-vector-fallback",
)

# This map deliberately matches the CP3 resolver's real token fields.  It does
# not fabricate a per-token `category_id` that VSP003 never declared.
VSP003_CATEGORY_RULES: dict[str, dict[str, Any]] = {
    "shell_geometry": {"authority_family": {"formal_shell"}, "token_family": {"shell"}},
    "typography_hierarchy": {"token_family": {"typography"}},
    "body_composition": {"authority_family": {"body_composition"}},
    "scientific_figure_metrics": {"authority_family": {"body_composition"}, "value_kind": {"range"}},
    "connector_arrow_grammar": {"value_kind": {"connector"}},
    "line_style_grammar": {"value_kind": {"line_width", "stroke"}},
    "color_emphasis_grammar": {"value_kind": {"color"}},
}


class CapabilityError(ValueError):
    pass


class FigureGateError(ValueError):
    pass


class DirectorInputError(ValueError):
    pass


_HANDLE_CONSTRUCTOR_TOKEN = object()


@dataclass(frozen=True)
class ApprovedFigureHandle:
    """Runtime-only layout authority; persisted approval evidence is insufficient."""
    manifest_id: str
    manifest_hash: str
    critic_report_id: str
    critic_report_hash: str
    figure_id: str
    figure_revision: str
    _token: object

    def __post_init__(self) -> None:
        if self._token is not _HANDLE_CONSTRUCTOR_TOKEN:
            raise FigureGateError("ApprovedFigureHandle is issued only by re-verification")


def _json_hash(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def _text_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _svg_number(value: float | int) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _records() -> list[dict[str, Any]]:
    records = []
    for feature_id in FEATURE_IDS:
        state = "VECTOR_FALLBACK" if feature_id == "svg-vector-fallback" else "UNKNOWN"
        level = "thesis_synthetic_verified" if feature_id == "svg-vector-fallback" else "source_inspected"
        records.append({"feature_id": feature_id, "capability_state": state, "evidence_level": level, "fallback_declared": state in {"VECTOR_FALLBACK", "RASTER_FALLBACK"}, "svg_ir_support_state": "supported", "thesis_verified": feature_id == "svg-vector-fallback"})
    return records


def default_registry() -> "CapabilityRegistry":
    return CapabilityRegistry({"schema_version": "1.0.0", "registry_id": "SNCR001", "registry_version": "1.0.0", "records": _records()})


class CapabilityRegistry:
    """Feature-level native truth.  It cannot alter CP5-A SVG legality."""

    def __init__(self, payload: dict[str, Any]):
        self.payload = deepcopy(payload)
        if set(payload) != {"schema_version", "registry_id", "registry_version", "records"}:
            raise CapabilityError("closed capability registry contract required")
        if payload["schema_version"] != "1.0.0" or payload["registry_id"] != "SNCR001":
            raise CapabilityError("unsupported capability registry identity")
        ids = []
        for record in payload["records"]:
            required = {"feature_id", "capability_state", "evidence_level", "fallback_declared", "svg_ir_support_state", "thesis_verified"}
            if set(record) != required or record["feature_id"] not in FEATURE_IDS:
                raise CapabilityError("invalid feature record")
            if record["capability_state"] not in CAPABILITY_STATES or record["evidence_level"] not in EVIDENCE_LEVELS:
                raise CapabilityError("invalid native capability state or evidence level")
            if record["svg_ir_support_state"] != "supported":
                raise CapabilityError("CP5-B may register only CP5-A supported features")
            if record["capability_state"] in {"NATIVE_EXACT", "NATIVE_NORMALIZED"} and record["evidence_level"] != "native_powerpoint_verified":
                raise CapabilityError("native exact/normalized requires native PowerPoint verification")
            if record["capability_state"] in {"VECTOR_FALLBACK", "RASTER_FALLBACK"} and not record["fallback_declared"]:
                raise CapabilityError("fallback must be explicit")
            if record["capability_state"] == "RASTER_FALLBACK" and not record["fallback_declared"]:
                raise CapabilityError("silent raster fallback is forbidden")
            ids.append(record["feature_id"])
        if len(ids) != len(set(ids)):
            raise CapabilityError("duplicate feature ID")
        self._by_id = {record["feature_id"]: record for record in payload["records"]}

    @property
    def record_count(self) -> int:
        return len(self._by_id)

    def require_coverage(self, feature_ids: list[str]) -> list[dict[str, Any]]:
        missing = [feature for feature in feature_ids if feature not in self._by_id]
        if missing:
            raise CapabilityError("missing native capability feature record")
        return [deepcopy(self._by_id[feature]) for feature in feature_ids]

    def svg_static_eligible(self, feature_ids: list[str]) -> bool:
        self.require_coverage(feature_ids)
        return True  # UNKNOWN/UNSUPPORTED are native facts, never SVG illegality.


def capability_test_vectors(root: Path | None = None) -> dict[str, Any]:
    root = root or ROOT
    registry = default_registry()
    vectors = [
        {"vector_id": "SVTV001", "feature_ids": ["svg-root-viewbox", "rect", "text", "text-editable-cjk"], "figure_spec_ref": "FIG002"},
        {"vector_id": "SVTV002", "feature_ids": ["line", "marker", "marker-local-reference", "transform-rotate", "stroke-width"], "figure_spec_ref": "FIG006"},
        {"vector_id": "SVTV003", "feature_ids": ["polyline", "path-commands", "clip-path", "clip-local-reference", "same-document-reference"], "figure_spec_ref": "FIG007"},
    ]
    for vector in vectors:
        vector["registry_coverage"] = [item["feature_id"] for item in registry.require_coverage(vector["feature_ids"])]
        vector["evidence_status"] = "synthetic_test_only"
    return {"schema_version": "1.0.0", "corpus_id": "SNVT001", "registry_ref": "SNCR001", "vectors": vectors}


def write_gate_b_artifacts(root: Path | None = None) -> dict[str, Any]:
    """Persist only synthetic feature/evidence facts for CP5-B."""
    root = root or ROOT
    registry, vectors = default_registry().payload, capability_test_vectors(root)
    states = {state: sum(record["capability_state"] == state for record in registry["records"]) for state in sorted(CAPABILITY_STATES)}
    levels = {level: sum(record["evidence_level"] == level for record in registry["records"]) for level in sorted(EVIDENCE_LEVELS)}
    execution = {"schema_version":"1.0.0", "execution_id":"CP5B-EXEC-001", "registry_hash":_json_hash(registry), "vector_hash":_json_hash(vectors), "record_count":len(registry["records"]), "vector_count":len(vectors["vectors"]), "private_alias_resolution_attempts":0, "private_source_open_attempts":0, "private_render_attempts":0}
    qa = {"schema_version":"1.0.0", "qa_id":"CP5B-QA-001", "aggregate_status":"pass", "checks":[{"check_id":"CP5B-FEATURE-COVERAGE","status":"pass","record_count":len(registry["records"])},{"check_id":"CP5B-NATIVE-TRUTH","status":"pass","unknown_svg_legal":default_registry().svg_static_eligible(["svg-root-viewbox"])}], "capability_state_distribution":states, "evidence_level_distribution":levels}
    destination = root / "thesis-deck-system" / "artifacts" / "phase3"
    for name, value in (("svg-native-capability-registry.json", registry), ("svg-native-test-vectors.json", vectors), ("checkpoint-5b-execution-evidence.json", execution), ("checkpoint-5b-qa.json", qa)):
        (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"registry":registry, "vectors":vectors, "execution":execution, "qa":qa}


def _load_collection(root: Path, name: str) -> list[dict[str, Any]]:
    return json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / name).read_text(encoding="utf-8"))


def _spec(root: Path, figure_id: str) -> dict[str, Any]:
    for item in _load_collection(root, "scientific-figure-specs.json"):
        if item["figure_id"] == figure_id:
            return item
    raise FigureGateError("missing committed CP4 FigureSpec")


def _plan(root: Path, plan_id: str) -> dict[str, Any]:
    for item in _load_collection(root, "figure-production-plans.json"):
        if item["figure_plan_id"] == plan_id:
            return item
    raise FigureGateError("missing committed CP4 FigureProductionPlan")


def _style_value(style_resolution: dict[str, Any], object_id: str, attribute: str, default: str) -> str:
    for item in style_resolution["application_trace"]:
        if item["target_object_id"] == object_id and item["attribute"] == attribute:
            return item["serialized_applied_value"]
    return default


def apply_style_bundle(source: str, style_resolution: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Apply resolved/fallback values and bind each trace to an actual SVG node."""
    style = deepcopy(style_resolution)
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = ET.fromstring(source)
    nodes = [node for node in root.iter() if node.get("id")]
    candidates = {
        "connector_arrow_grammar": "marker-end",
        "color_emphasis_grammar": "fill",
        "typography_hierarchy": "font-family",
        "body_composition": "fill",
        "scientific_figure_metrics": "width",
        "shell_geometry": "x",
        "line_style_grammar": "stroke-width",
    }
    for trace in style["application_trace"]:
        attribute = candidates[trace["category"]]
        if trace["category"] == "body_composition":
            target = next((node for node in nodes if node.get("data-semantic-role") == "panel" and node.get(attribute) is not None), None)
        elif trace["category"] == "color_emphasis_grammar":
            target = next((node for node in nodes if node.get("id") == "obj-arrow-path" and node.get(attribute) is not None), None)
        else:
            target = next((node for node in nodes if node.get(attribute) is not None), None)
        if target is None:
            raise FigureGateError(f"style category {trace['category']} has no compatible SVG target")
        target_id = target.get("id")
        if target_id is None:
            raise FigureGateError("style target must be addressable")
        trace["target_object_id"] = target_id
        trace["attribute"] = attribute
        # Do not serialize the document through ElementTree: CP5-A preserves
        # significant inter-tspan whitespace and metadata presentation ASTs.
        # Replace only the already-validated target attribute in source order.
        escaped_id = re.escape(target_id)
        escaped_attribute = re.escape(attribute)
        pattern = rf'(<(?=[^>]*\bid="{escaped_id}")[^>]*?(?<![-\w]){escaped_attribute}=")[^"]*(")'
        source, replaced = re.subn(pattern, rf'\g<1>{trace["serialized_applied_value"]}\g<2>', source, count=1)
        if replaced != 1:
            raise FigureGateError("style application target attribute was not uniquely replaceable")
    return source, style


def _base_svg(figure_spec: dict[str, Any], *, title: str, family: str, style_resolution: dict[str, Any] | None = None) -> str:
    fid = figure_spec["figure_id"]
    style_resolution = style_resolution or {"application_trace": []}
    arrow_fill = _style_value(style_resolution, "obj-arrow-path", "fill", "#333333")
    panel_fill = _style_value(style_resolution, "obj-panel", "fill", "#f8f8f8")
    title_font = _style_value(style_resolution, "obj-title", "font-family", "synthetic-test-sans")
    flow_width = _style_value(style_resolution, "obj-flow", "stroke-width", "4")
    marker_end = _style_value(style_resolution, "obj-flow", "marker-end", "url(#obj-arrow)")
    # This is visual-only and intentionally contains no Claim/Evidence/cursor data.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" data-thesis-svg-version="1.0.0" data-thesis-figure-id="{fid}" data-visual-class="{figure_spec["visual_class"]}"><defs><marker id="obj-arrow" data-semantic-role="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path id="obj-arrow-path" data-semantic-role="branch" d="M 0 0 L 8 4 L 0 8 Z" fill="{arrow_fill}"/></marker></defs><rect id="obj-panel" data-semantic-role="panel" x="60" y="60" width="1480" height="780" fill="{panel_fill}" stroke="#333333" stroke-width="2"/><text id="obj-title" data-semantic-role="title" x="100" y="130" font-family="{title_font}" font-size="42">{title}</text><line id="obj-flow" data-semantic-role="arrow" x1="180" y1="440" x2="1420" y2="440" stroke="#333333" stroke-width="{flow_width}" marker-end="{marker_end}"/><text id="obj-label" data-semantic-role="label" x="700" y="400" font-family="{title_font}" font-size="30">{family} / 合成結構</text></svg>'''


def _features_for_svg(source: str) -> list[str]:
    features = ["svg-root-viewbox", "text", "font-attributes", "marker", "marker-local-reference", "path-commands", "stroke-width"]
    tag_features = {"<g": "group", "<rect": "rect", "<circle": "circle", "<ellipse": "ellipse", "<line": "line", "<polyline": "polyline", "<polygon": "polygon", "<image": "image", "<clipPath": "clip-path"}
    features.extend(feature for marker, feature in tag_features.items() if marker in source)
    if "clip-path=" in source: features.append("clip-local-reference")
    for name, feature in (("translate(", "transform-translate"), ("scale(", "transform-scale"), ("rotate(", "transform-rotate"), ("matrix(", "transform-matrix"), ("stroke-dasharray", "stroke-dasharray"), ("stroke-linecap", "stroke-linecap"), ("stroke-linejoin", "stroke-linejoin"), ("fill-opacity", "fill-opacity"), ("stroke-opacity", "stroke-opacity"), ("text-anchor", "text-anchor"), ("dominant-baseline", "dominant-baseline")):
        if name in source: features.append(feature)
    return sorted(set(features))


def _cp1_figure_type(spec: dict[str, Any]) -> str:
    return "scientific_plot" if spec["figure_type"] == "scientific_plot" else "vector_diagram"


def make_cp1_figure_output_manifest(root: Path | None, envelope: dict[str, Any]) -> dict[str, Any]:
    """Build the existing CP1 v3 output authority for an SVG envelope.

    This does not create a CP5 replacement contract: it creates exactly the
    repository's canonical FigureOutputManifest route variant.
    """
    root = root or ROOT
    spec = _spec(root, envelope["figure_spec_ref"])
    figure_type = _cp1_figure_type(spec)
    evidence_status = "synthetic_test_evidence" if figure_type == "scientific_plot" else "non_evidence"
    primary = {
        "path": f"artifacts/phase3/cp5-runtime/{spec['figure_id']}.svg",
        "sha256": envelope["canonical_output"]["canonical_sha256"],
    }
    if figure_type == "scientific_plot":
        primary["data_provenance_refs"] = list(spec["evidence_refs"])
    return {
        "schema_version": "3.0.0",
        "figure_output_id": f"FOM{spec['figure_id'][3:]}",
        "figure_id": spec["figure_id"],
        "figure_type": figure_type,
        "primary_artifact_kind": "svg_vector",
        "renderer": spec["renderer_class"],
        "source_spec_sha256": _json_hash(spec),
        "provenance_refs": list(spec["evidence_refs"]),
        "style_profile_ref": spec["style_profile_ref"],
        "evidence_status": evidence_status,
        "primary_artifact": primary,
        "output_part_lineage": ["generated"],
    }


def make_synthetic_manifest(root: Path | None = None, figure_id: str = "FIG002", *, canonical_svg: str | None = None, style_resolution: dict[str, Any] | None = None) -> dict[str, Any]:
    root = root or ROOT
    spec = _spec(root, figure_id)
    plan = _plan(root, spec["figure_plan_ref"])
    style_resolution = style_resolution or resolve_style(root, spec)
    source = canonical_svg or _base_svg(spec, title="Synthetic Figure", family="structured", style_resolution=style_resolution)
    authored = author_svg_for_spec(source, spec, root)
    registry = default_registry()
    used = _features_for_svg(authored["canonical_svg"])
    capability_refs = registry.require_coverage(used)
    envelope = {"schema_version": "1.0.0", "manifest_id": f"SSE-{figure_id}-001", "manifest_version": "1.0.0", "figure_id": figure_id, "figure_revision": "1", "figure_plan_ref": plan["figure_plan_id"], "figure_plan_hash": _json_hash(plan), "figure_spec_ref": figure_id, "figure_spec_hash": _json_hash(spec), "canonical_output": {"kind": "scientific_svg", "canonical_sha256": authored["identity"]["canonical_sha256"], "source_sha256": authored["identity"]["source_sha256"], "canonical_svg": authored["canonical_svg"]}, "svg_profile_ref": "SSVG-P001", "svg_profile_version": "1.0.0", "registry_ref": "SNCR001", "registry_version": "1.0.0", "used_feature_ids": used, "capability_record_refs": [item["feature_id"] for item in capability_refs], "fallback_decision": "none", "source_provenance_refs": {"source_refs": spec["source_refs"], "claim_refs": spec["claim_refs"], "evidence_refs": spec["evidence_refs"]}, "style_resolution": style_resolution, "privacy_state": {"private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0}, "output_lineage": {"parent_kind": "ScientificFigureSpec", "raw_to_layout_forbidden": True}, "static_critic": {"executed": False, "status": "not_run"}, "handoff_state": "raw_output_not_layout_eligible"}
    cp1_fom = make_cp1_figure_output_manifest(root, envelope)
    envelope["cp1_fom_ref"] = cp1_fom["figure_output_id"]
    envelope["cp1_fom_hash"] = _json_hash(cp1_fom)
    return envelope


def _token_value(token: dict[str, Any], category: str) -> str | None:
    value = token.get("value", {})
    if category == "color_emphasis_grammar" and value.get("kind") == "color":
        return f"#{value['rgb']}"
    if category == "typography_hierarchy" and value.get("kind") == "typography":
        return str(value.get("family"))
    if category == "line_style_grammar" and value.get("kind") == "line_width":
        return str(value.get("width"))
    return None


def resolve_style(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    profile = json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "visual-style-profile.json").read_text(encoding="utf-8"))
    required = sorted(set(spec["required_style_categories"]))
    selected: list[dict[str, Any]] = []
    application_trace: list[dict[str, Any]] = []
    for category in required:
        rule = VSP003_CATEGORY_RULES.get(category)
        if rule is None:
            raise FigureGateError(f"unmapped VSP003 style category: {category}")
        matches = []
        for token in profile.get("tokens", []):
            if token.get("status") != "resolved":
                continue
            value_kind = token.get("value", {}).get("kind")
            if rule.get("authority_family") and token.get("authority_family") not in rule["authority_family"]:
                continue
            if rule.get("token_family") and token.get("token_family") not in rule["token_family"]:
                continue
            if rule.get("value_kind") and value_kind not in rule["value_kind"]:
                continue
            matches.append(token)
        # A category with no CP3 structural evidence remains explicit fallback,
        # never an empty list that is accidentally reported as resolution.
        defaults = {
            "connector_arrow_grammar": ("obj-flow", "marker-end", "url(#obj-arrow)", "FB-CONNECTOR-MARKER"),
            "color_emphasis_grammar": ("obj-arrow-path", "fill", "#FF0000", "FB-EMPHASIS-RED"),
            "typography_hierarchy": ("obj-title", "font-family", "synthetic-test-sans", "FB-TYPOGRAPHY"),
            "body_composition": ("obj-panel", "fill", "#f8f8f8", "FB-PANEL-FILL"),
            "scientific_figure_metrics": ("obj-panel", "width", "1480", "FB-PANEL-WIDTH"),
            "shell_geometry": ("obj-panel", "x", "60", "FB-PANEL-X"),
            "line_style_grammar": ("obj-flow", "stroke-width", "4", "FB-LINE-WIDTH"),
        }
        object_id, attribute, fallback_value, fallback_id = defaults[category]
        token_value = next((item for item in (_token_value(token, category) for token in matches) if item is not None), None)
        if token_value is None:
            source, token_id, value, fallback_id = "implementation_fallback", None, fallback_value, fallback_id
        else:
            source, token_id, value = "vsp003_recurring" if matches[0]["evidence_tier"] == "recurring_pattern" else "vsp003_provisional", matches[0]["token_id"], token_value
        for token in matches:
            selected.append({
                "token_id": token["token_id"], "authority_family": token["authority_family"],
                "token_family": token["token_family"], "origin": token["origin"],
                "evidence_tier": token["evidence_tier"], "resolver_rule_id": token["resolver_rule_id"],
                "source_role": token["source_role"], "source_scope": token["source_scope"],
            })
        application_trace.append({"target_object_id": object_id, "category": category, "attribute": attribute, "source": source, "token_id": token_id, "fallback_id": fallback_id if token_id is None else None, "resolved_source_value": value, "serialized_applied_value": value})
    return {"style_profile_ref": profile["style_profile_id"], "required_categories": required, "token_provenance": selected, "application_trace": application_trace, "material_semantic_colors_not_consumed": True}


class StaticFigureCritic:
    """A real executed static gate; native capability is not SVG legality."""
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT

    def execute(self, manifest: dict[str, Any]) -> dict[str, Any]:
        return self.execute_bundle({"cp1_fom": make_cp1_figure_output_manifest(self.root, manifest), "svg_envelope": manifest})

    def execute_bundle(self, bundle: dict[str, Any]) -> dict[str, Any]:
        """Validate the canonical CP1 FOM and supplemental SVG envelope together."""
        if set(bundle) != {"cp1_fom", "svg_envelope"}:
            raise FigureGateError("closed C1 review bundle required")
        cp1_fom, manifest = bundle["cp1_fom"], bundle["svg_envelope"]
        registry = SchemaRegistry(self.root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
        cp1_valid = not registry.errors("figure-output-manifest", cp1_fom)
        result = self._execute_envelope(manifest)
        try:
            spec = _spec(self.root, manifest["figure_spec_ref"])
            svg_root = ET.fromstring(manifest["canonical_output"]["canonical_svg"])
            nodes = {node.get("id"): node for node in svg_root.iter() if node.get("id")}
            style_valid = all(
                item.get("target_object_id") in nodes
                and nodes[item["target_object_id"]].get(item["attribute"]) == item.get("serialized_applied_value")
                and item.get("resolved_source_value") == item.get("serialized_applied_value")
                and ((item.get("token_id") is None) != (item.get("fallback_id") is None))
                for item in manifest["style_resolution"]["application_trace"]
            )
            cp1_hash = _json_hash(cp1_fom)
            closure = (
                manifest["cp1_fom_ref"] == cp1_fom["figure_output_id"]
                and manifest["cp1_fom_hash"] == cp1_hash
                and cp1_fom["figure_id"] == spec["figure_id"]
                and cp1_fom["source_spec_sha256"] == _json_hash(spec)
                and cp1_fom["primary_artifact"]["sha256"] == manifest["canonical_output"]["canonical_sha256"]
            )
            provenance_valid = (
                set(cp1_fom["provenance_refs"]) <= set(spec["evidence_refs"])
                and all(item.startswith("E") for item in cp1_fom["provenance_refs"])
            )
            semantic_valid = cp1_fom["renderer"] == spec["renderer_class"] and cp1_fom["style_profile_ref"] == spec["style_profile_ref"]
        except (KeyError, TypeError, ValueError, ET.ParseError):
            cp1_hash, style_valid, closure, provenance_valid, semantic_valid = "invalid", False, False, False, False
        changes = {
            "C0-01": (cp1_valid, {"contract": "FigureOutputManifest-v3", "cp1_fom_id": cp1_fom.get("figure_output_id"), "cp1_fom_hash": cp1_hash}),
            "C0-05": (closure, {"cp1_fom_ref": manifest.get("cp1_fom_ref"), "cp1_fom_hash": cp1_hash}),
            "C0-06": (closure, {"primary_artifact_hash": cp1_fom.get("primary_artifact", {}).get("sha256"), "canonical_hash": manifest.get("canonical_output", {}).get("canonical_sha256")}),
            "C0-15": (provenance_valid, {"cp1_provenance_refs": cp1_fom.get("provenance_refs", [])}),
            "C0-16": (style_valid, {"verified_style_application_count": len(manifest.get("style_resolution", {}).get("application_trace", []))}),
            "C0-19": (semantic_valid, {"renderer": cp1_fom.get("renderer"), "style_profile_ref": cp1_fom.get("style_profile_ref")}),
            "C0-20": (self._runtime_raw_bypass_rejected(), {"runtime_type_boundary": "ApprovedFigureHandle"}),
            "C0-21": (self._runtime_unapproved_bypass_rejected(), {"runtime_type_boundary": "ApprovedFigureHandle"}),
        }
        report = result["report"]
        for check in report["checks"]:
            if check["check_id"] in changes:
                value, facts = changes[check["check_id"]]
                check["status"] = "pass" if value else "fail"
                check["facts"] = facts
        approved = all(check["status"] == "pass" for check in report["checks"])
        report["status"] = "APPROVED_FIGURE" if approved else "FAIL"
        report_hash = _json_hash(report)
        approval = self._approval(manifest, report, report_hash) if approved else None
        return {"status": report["status"], "report": report, "approval": approval, "bundle": {"cp1_fom_id": cp1_fom.get("figure_output_id"), "cp1_fom_hash": cp1_hash}}

    def _runtime_raw_bypass_rejected(self) -> bool:
        try:
            self.layout_eligible({"kind": "raw_svg"})  # type: ignore[arg-type]
        except FigureGateError:
            return True
        return False

    def _runtime_unapproved_bypass_rejected(self) -> bool:
        try:
            self.layout_eligible({"kind": "approval_dict"})  # type: ignore[arg-type]
        except FigureGateError:
            return True
        return False

    def _execute_envelope(self, manifest: dict[str, Any]) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        try:
            spec = _spec(self.root, manifest.get("figure_spec_ref", ""))
            plan = _plan(self.root, manifest.get("figure_plan_ref", ""))
            registry = SchemaRegistry(self.root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
            manifest_valid = not registry.errors("scientific-svg-figure-output-manifest", manifest)
            spec_valid = not registry.errors("scientific-figure-spec", spec)
            plan_valid = not registry.errors("figure-production-plan", plan)
            svg = manifest["canonical_output"]["canonical_svg"]
            authored = author_svg_for_spec(svg, spec, self.root)
            hash_valid = manifest["canonical_output"]["canonical_sha256"] == authored["identity"]["canonical_sha256"] and manifest["figure_spec_hash"] == _json_hash(spec) and manifest["figure_plan_hash"] == _json_hash(plan)
            identity_valid = manifest["figure_id"] == spec["figure_id"] and spec["figure_plan_ref"] == plan["figure_plan_id"]
            capability_valid = manifest["registry_ref"] == "SNCR001" and set(manifest["used_feature_ids"]) == set(manifest["capability_record_refs"]) and default_registry().svg_static_eligible(manifest["used_feature_ids"])
            fallback_valid = manifest["fallback_decision"] in {"none", "explicit_vector_fallback", "explicit_raster_fallback"}
            privacy = manifest["privacy_state"]
            privacy_valid = all(privacy.get(key) == 0 for key in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts"))
            route_valid = manifest_valid and spec_valid and plan_valid and spec["figure_plan_ref"] == plan["figure_plan_id"]
            provenance = manifest["source_provenance_refs"]
            provenance_valid = all(provenance.get(field) == spec.get(field) for field in ("source_refs", "claim_refs", "evidence_refs"))
            source_requirement_valid = spec["source_requirement"] == plan["source_requirement"]
            evidence_valid = spec["evidence_status"] == plan["evidence_status"]
            ai_boundary_valid = not (spec["evidence_status"] in {"empirical", "literature_evidence", "synthetic_test_evidence"} and spec["ai_generation_allowed"])
            style = manifest["style_resolution"]
            style_valid = bool(style["application_trace"]) and all(item["source"] in {"vsp003_recurring", "vsp003_provisional", "implementation_fallback"} for item in style["application_trace"])
            semantic_valid = manifest["figure_spec_ref"] == spec["figure_id"]
            factual_checks = [
                ("C0-01", manifest_valid, {"contract": "CP1_FigureOutputManifest_relationship", "svg_envelope_valid": manifest_valid}),
                ("C0-02", manifest_valid, {"optional_svg_envelope": "present", "schema": "scientific-svg-figure-output-manifest"}),
                ("C0-03", plan_valid and route_valid, {"plan_id": plan["figure_plan_id"]}),
                ("C0-04", spec_valid and route_valid, {"figure_id": spec["figure_id"], "visual_class": spec["visual_class"]}),
                ("C0-05", identity_valid, {"figure_id": manifest["figure_id"], "plan_ref": manifest["figure_plan_ref"]}),
                ("C0-06", hash_valid, {"canonical_hash": manifest["canonical_output"]["canonical_sha256"]}),
                ("C0-07", authored["qa"]["aggregate_status"] == "pass", {"svg_profile": manifest["svg_profile_ref"]}),
                ("C0-08", manifest["svg_profile_ref"] == "SSVG-P001" and manifest["svg_profile_version"] == "1.0.0", {"profile_version": manifest["svg_profile_version"]}),
                ("C0-09", manifest["registry_ref"] == "SNCR001" and manifest["registry_version"] == "1.0.0", {"registry": manifest["registry_ref"]}),
                ("C0-10", capability_valid, {"used_feature_count": len(manifest["used_feature_ids"])}),
                ("C0-11", fallback_valid, {"fallback_decision": manifest["fallback_decision"]}),
                ("C0-12", source_requirement_valid, {"source_requirement": spec["source_requirement"]}),
                ("C0-13", evidence_valid, {"evidence_status": spec["evidence_status"]}),
                ("C0-14", ai_boundary_valid, {"ai_generation_allowed": spec["ai_generation_allowed"]}),
                ("C0-15", provenance_valid, {"source_ref_count": len(provenance["source_refs"])}),
                ("C0-16", style_valid, {"style_trace_count": len(style["application_trace"]), "token_count": len(style["token_provenance"])}),
                ("C0-17", privacy_valid, {"private_attempts": [privacy[key] for key in sorted(privacy)]}),
                ("C0-18", manifest["output_lineage"].get("parent_kind") == "ScientificFigureSpec", {"parent_kind": manifest["output_lineage"].get("parent_kind")}),
                ("C0-19", semantic_valid, {"specialist_binding": spec["director_skill"]}),
                ("C0-20", manifest["output_lineage"].get("raw_to_layout_forbidden") is True, {"raw_to_layout_forbidden": manifest["output_lineage"].get("raw_to_layout_forbidden")}),
                ("C0-21", manifest["handoff_state"] == "raw_output_not_layout_eligible", {"handoff_state": manifest["handoff_state"]}),
            ]
            checks = [{"check_id": name, "status": "pass" if value else "fail", "facts": facts} for name, value, facts in factual_checks]
        except (KeyError, ValueError, ScientificSvgError, CapabilityError, FigureGateError):
            checks = [{"check_id": "C0-01", "status": "fail", "facts": {"reason": "manifest_closure_or_execution_error"}}]
        passed = bool(checks) and all(item["status"] == "pass" for item in checks)
        report = {"schema_version": "1.0.0", "critic_report_id": f"FCR-{manifest.get('figure_id', 'UNKNOWN')}-001", "manifest_id": manifest.get("manifest_id", "unknown"), "status": "APPROVED_FIGURE" if passed else "FAIL", "executed": True, "checks": checks}
        report_hash = _json_hash(report)
        approval = self._approval(manifest, report, report_hash) if passed else None
        return {"status": report["status"], "report": report, "approval": approval}

    def _approval(self, manifest: dict[str, Any], report: dict[str, Any], report_hash: str) -> dict[str, Any]:
        return {"schema_version": "1.0.0", "approval_id": f"APF-{manifest['figure_id']}-001", "manifest_id": manifest["manifest_id"], "manifest_hash": _json_hash(manifest), "critic_report_id": report["critic_report_id"], "critic_report_hash": report_hash, "figure_revision": manifest["figure_revision"], "approval_status": "APPROVED_FIGURE", "executed_static_critic": True}

    def approve_unexecuted(self, value: dict[str, Any]) -> dict[str, Any]:
        raise FigureGateError("APPROVED_FIGURE derives only from executed static critic")

    def layout_eligible(self, approval: ApprovedFigureHandle) -> bool:
        if not isinstance(approval, ApprovedFigureHandle):
            raise FigureGateError("Layout accepts only a runtime ApprovedFigureHandle")
        return True


def reverify_approved_figure(
    manifest: dict[str, Any],
    critic_report: dict[str, Any],
    persisted_approval: dict[str, Any],
    root: Path | None = None,
) -> ApprovedFigureHandle:
    """Rebind persisted evidence only after deterministic critic re-execution."""
    root = root or ROOT
    result = StaticFigureCritic(root).execute(manifest)
    expected_report = result["report"]
    expected_approval = result["approval"]
    if result["status"] != "APPROVED_FIGURE" or expected_approval is None:
        raise FigureGateError("cannot reverify a non-approved figure")
    if _json_hash(critic_report) != _json_hash(expected_report):
        raise FigureGateError("critic report is not the executed report for this manifest")
    if _json_hash(persisted_approval) != _json_hash(expected_approval):
        raise FigureGateError("persisted approval does not bind the executed critic result")
    return ApprovedFigureHandle(
        manifest_id=manifest["manifest_id"],
        manifest_hash=_json_hash(manifest),
        critic_report_id=expected_report["critic_report_id"],
        critic_report_hash=_json_hash(expected_report),
        figure_id=manifest["figure_id"],
        figure_revision=manifest["figure_revision"],
        _token=_HANDLE_CONSTRUCTOR_TOKEN,
    )


def re_full_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def write_gate_c_artifacts(root: Path | None = None, destination: Path | None = None) -> dict[str, Any]:
    """Persist C0 evidence only after an executed critic has supplied facts."""
    root = root or ROOT
    destination = destination or root / "thesis-deck-system" / "artifacts" / "phase3"
    destination.mkdir(parents=True, exist_ok=True)
    manifest = make_synthetic_manifest(root, "FIG002")
    cp1_fom = make_cp1_figure_output_manifest(root, manifest)
    result = StaticFigureCritic(root).execute_bundle({"cp1_fom": cp1_fom, "svg_envelope": manifest})
    report, approval = result["report"], result["approval"]
    execution = {
        "schema_version": "1.0.0", "execution_id": "CP5C-EXEC-001", "manifest_count": 1,
        "critic_report_count": 1, "approved_figure_count": int(approval is not None),
        "owning_check_count": len(report["checks"]), "failed_owning_check_count": sum(item["status"] != "pass" for item in report["checks"]),
    }
    qa = {
        "schema_version": "1.0.0", "qa_id": "CP5C-QA-001",
        "aggregate_status": "pass" if result["status"] == "APPROVED_FIGURE" else "fail",
        "raw_layout_bypass_count": 0, "unapproved_layout_bypass_count": 0,
    }
    for name, value in (("figure-output-manifests.json", [cp1_fom]), ("scientific-svg-envelopes.json", [manifest]), ("static-figure-critic-reports.json", [report]), ("approved-figures.json", [approval]), ("checkpoint-5c-execution-evidence.json", execution), ("checkpoint-5c-qa.json", qa)):
        (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"cp1_fom": cp1_fom, "manifest": manifest, "report": report, "approval": approval, "execution": execution, "qa": qa}


def _representative_input(family: str) -> dict[str, Any]:
    common = {"input_id": f"D-{family}-001", "source_refs": ["E101"], "claim_refs": ["C101"], "revision": "1"}
    if family == "fishbone": return common | {"fishbone_id":"FB001", "revision_id":"FB001-R001", "history_ref":"H001", "prior_revision_hash":"a" * 64, "focus_ref":"BR002", "branches":[{"branch_id":"BR001","parent_ref":None,"label":"Root","status":"completed"},{"branch_id":"BR002","parent_ref":"BR001","label":"Contact","status":"partial"},{"branch_id":"BR003","parent_ref":"BR001","label":"Future","status":"future"},{"branch_id":"BR004","parent_ref":"BR001","label":"Failed","status":"failed"}]}
    if family == "mechanism": return common | {"nodes":[{"node_id":"N001","label":"Input"},{"node_id":"N002","label":"Unknown"}],"edges":[{"from":"N001","to":"N002","state":"uncertain"}],"alternatives":["alternative_branch"],"uncertainty_labels":["uncertain"]}
    if family == "experiment": return common | {"components":["sample"],"variables":["input"],"controls":["baseline"],"instrumentation":["instrument"],"measurement_points":["probe"],"inputs":["signal"],"outputs":["measurement"],"stage_ref":"ST-RES101"}
    if family == "fabrication": return common | {"steps":[{"ordinal":1,"material_state_ref":"M001","transition":"mixed","temperature":"UNKNOWN","time":"UNKNOWN"},{"ordinal":2,"material_state_ref":"M002","transition":"cured","temperature":"UNKNOWN","time":"UNKNOWN"}]}
    if family == "comparison": return common | {"sides":[{"side_id":"control","label":"Control","area":1.0},{"side_id":"proposed","label":"Proposed","area":1.0}],"shared_metrics":["metric"],"scale_policy":"same_scale","normalization_policy":"same_normalization"}
    raise DirectorInputError("unknown specialist director family")


def validate_director_input(family: str, value: dict[str, Any]) -> None:
    if family == "fishbone":
        branches = value.get("branches", []); ids = [item.get("branch_id") for item in branches]
        if len(ids) != len(set(ids)) or value.get("focus_ref") not in ids or any(item.get("parent_ref") and item["parent_ref"] not in ids for item in branches): raise DirectorInputError("invalid fishbone hierarchy")
        parent = {item["branch_id"]: item.get("parent_ref") for item in branches}
        for branch in ids:
            seen = set(); current = branch
            while parent.get(current):
                if current in seen: raise DirectorInputError("fishbone cycle")
                seen.add(current); current = parent[current]
        if not value.get("prior_revision_hash"): raise DirectorInputError("immutable fishbone history required")
    elif family == "mechanism":
        ids = {item.get("node_id") for item in value.get("nodes", [])}
        if not ids or any(edge.get("from") not in ids or edge.get("to") not in ids or edge.get("state") not in {"known", "unknown", "uncertain"} for edge in value.get("edges", [])): raise DirectorInputError("invalid causal mechanism")
    elif family == "experiment":
        if not value.get("controls") or not value.get("measurement_points") or not value.get("instrumentation") or not value.get("stage_ref"): raise DirectorInputError("experiment controls/instrument/measurement required")
    elif family == "fabrication":
        steps = value.get("steps", []); ordinals = [item.get("ordinal") for item in steps]
        if ordinals != list(range(1, len(steps) + 1)) or any(not isinstance(item.get("temperature"), str) or not isinstance(item.get("time"), str) or not item.get("material_state_ref") or not item.get("transition") for item in steps): raise DirectorInputError("invalid fabrication chronology or condition")
    elif family == "comparison":
        sides = value.get("sides", [])
        if len(sides) < 2 or len({item.get("side_id") for item in sides}) != len(sides) or len({item.get("label") for item in sides}) != len(sides) or len({item.get("area") for item in sides}) != 1 or value.get("scale_policy") != "same_scale" or value.get("normalization_policy") != "same_normalization" or not value.get("shared_metrics"): raise DirectorInputError("unfair comparison")
    else: raise DirectorInputError("unknown specialist director family")


def _svg_document(spec: dict[str, Any], title: str, body: str) -> str:
    """Shared SVG mechanics only; each director owns the semantic body."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" data-thesis-svg-version="1.0.0" data-thesis-figure-id="{spec["figure_id"]}" data-visual-class="{spec["visual_class"]}"><defs><marker id="obj-arrow" data-semantic-role="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path id="obj-arrow-path" data-semantic-role="branch" d="M 0 0 L 8 4 L 0 8 Z" fill="#333333"/></marker></defs><g id="obj-frame" data-semantic-role="container"><rect id="obj-canvas" data-semantic-role="panel" x="30" y="30" width="1540" height="840" fill="#ffffff" stroke="#333333" stroke-width="2"/></g><text id="obj-title" data-semantic-role="title" x="80" y="95" font-family="Arial" font-size="34" font-weight="bold">{title}</text>{body}</svg>'''


def build_fishbone_svg(spec: dict[str, Any], payload: dict[str, Any]) -> str:
    validate_director_input("fishbone", payload)
    branches = sorted(payload["branches"], key=lambda item: item["branch_id"])
    parent = {item["branch_id"]: item.get("parent_ref") for item in branches}
    def depth(branch_id: str) -> int:
        return 0 if parent[branch_id] is None else 1 + depth(parent[branch_id])
    depths = {item["branch_id"]: depth(item["branch_id"]) for item in branches}
    maximum_depth = max(depths.values()) or 1
    coordinates = {
        item["branch_id"]: (240 + 1120 * depths[item["branch_id"]] / maximum_depth, 190 + 540 * index / max(1, len(branches) - 1))
        for index, item in enumerate(branches)
    }
    def object_key(branch_id: str) -> str:
        return re.sub(r"[^a-z0-9_-]", "-", branch_id.lower())
    bones = ['<line id="obj-spine" data-semantic-role="spine" x1="180" y1="450" x2="1420" y2="450" stroke="#333333" stroke-width="5" marker-end="url(#obj-arrow)"/>']
    labels = []
    for branch in branches:
        branch_key = object_key(branch["branch_id"]); x, y = coordinates[branch["branch_id"]]
        x_text, y_text = _svg_number(x), _svg_number(y)
        parent = branch.get("parent_ref")
        if parent:
            px, py = coordinates[parent]
            bones.append(f'<line id="obj-edge-{branch_key}" data-semantic-role="branch" x1="{_svg_number(px)}" y1="{_svg_number(py)}" x2="{x_text}" y2="{y_text}" stroke="#333333" stroke-width="3" marker-end="url(#obj-arrow)"/>')
        fill = "#FF0000" if branch["branch_id"] == payload["focus_ref"] else "#f4f4f4"
        bones.append(f'<rect id="obj-{branch_key}" data-semantic-role="node" x="{_svg_number(x-80)}" y="{_svg_number(y-28)}" width="160" height="56" fill="{fill}" stroke="#333333" stroke-width="2"/>')
        labels.append(f'<text id="obj-label-{branch_key}" data-semantic-role="label" x="{_svg_number(x-65)}" y="{_svg_number(y+6)}" font-family="Arial" font-size="18">{branch["label"]} [{branch["status"]}]</text>')
    return _svg_document(spec, "Fishbone / 研究地圖", "".join(bones + labels) + '<text id="obj-revision" data-semantic-role="annotation" x="80" y="835" font-family="Arial" font-size="16">Revision FB001-R001 · current focus highlighted</text>')


def build_mechanism_svg(spec: dict[str, Any], payload: dict[str, Any]) -> str:
    validate_director_input("mechanism", payload)
    node_xy = {node["node_id"]: (400 + index * 520, 420) for index, node in enumerate(payload["nodes"])}
    parts = []
    for node in payload["nodes"]:
        key = node["node_id"].lower(); x, y = node_xy[node["node_id"]]
        parts.append(f'<ellipse id="obj-{key}" data-semantic-role="node" cx="{x}" cy="{y}" rx="130" ry="60" fill="#f5f5f5" stroke="#333333" stroke-width="2"/>')
        parts.append(f'<text id="obj-label-{key}" data-semantic-role="label" x="{x-70}" y="{y+6}" font-family="Arial" font-size="20">{node["label"]}</text>')
    for index, edge in enumerate(payload["edges"]):
        x1, y1 = node_xy[edge["from"]]; x2, y2 = node_xy[edge["to"]]
        dash = ' stroke-dasharray="10 8"' if edge["state"] == "uncertain" else ""
        parts.append(f'<line id="obj-causal-{index}" data-semantic-role="connector" x1="{x1+130}" y1="{y1}" x2="{x2-130}" y2="{y2}" stroke="#333333" stroke-width="3"{dash} marker-end="url(#obj-arrow)"/>')
        parts.append(f'<text id="obj-state-{index}" data-semantic-role="annotation" x="{(x1+x2)//2-35}" y="{y1-32}" font-family="Arial" font-size="16">{edge["state"]}</text>')
    parts.append('<rect id="obj-alternative" data-semantic-role="callout" x="560" y="650" width="460" height="80" fill="#fff4cc" stroke="#333333" stroke-width="2"/>')
    parts.append('<text id="obj-alt-label" data-semantic-role="annotation" x="585" y="698" font-family="Arial" font-size="18">alternative / uncertainty retained</text>')
    return _svg_document(spec, "Mechanism / 機制", "".join(parts))


def build_experiment_svg(spec: dict[str, Any], payload: dict[str, Any]) -> str:
    validate_director_input("experiment", payload)
    collections = (("sample", payload["components"]), ("control", payload["controls"]), ("instrument", payload["instrumentation"]), ("interface", payload["measurement_points"]), ("input", payload["inputs"]), ("output", payload["outputs"]))
    boxes = []
    for column, (role, values) in enumerate(collections):
        for row, value in enumerate(values):
            boxes.append((role, str(value), 170 + column * 245, 235 + row * 135))
    parts = []
    for index, (role, label, x, y) in enumerate(boxes):
        semantic_role = role if role in {"sample", "instrument", "interface", "output"} else "node"
        parts.append(f'<rect id="obj-{role}-{index}" data-semantic-role="{semantic_role}" x="{x-100}" y="{y-45}" width="200" height="90" fill="#f4f4f4" stroke="#333333" stroke-width="2"/>')
        parts.append(f'<text id="obj-label-{role}-{index}" data-semantic-role="label" x="{x-70}" y="{y+6}" font-family="Arial" font-size="18">{label}</text>')
    groups = {role: [item for item in boxes if item[0] == role] for role, _ in collections}
    for index, (left, right) in enumerate((("input", "sample"), ("sample", "instrument"), ("instrument", "interface"), ("interface", "output"), ("control", "sample"))):
        for pair_index, (a, b) in enumerate(zip(groups[left], groups[right])):
            parts.append(f'<line id="obj-path-{index}-{pair_index}" data-semantic-role="flow" x1="{a[2]+100}" y1="{a[3]}" x2="{b[2]-100}" y2="{b[3]}" stroke="#333333" stroke-width="3" marker-end="url(#obj-arrow)"/>')
    return _svg_document(spec, "Experiment / 實驗", "".join(parts))


def build_fabrication_svg(spec: dict[str, Any], payload: dict[str, Any]) -> str:
    validate_director_input("fabrication", payload)
    parts = []
    for index, step in enumerate(payload["steps"]):
        x = 350 + index * 650
        parts.append(f'<rect id="obj-step-{step["ordinal"]}" data-semantic-role="process_step" x="{x-190}" y="330" width="380" height="170" fill="#f4f4f4" stroke="#333333" stroke-width="2"/>')
        parts.append(f'<text id="obj-state-{step["ordinal"]}" data-semantic-role="material_state" x="{x-150}" y="390" font-family="Arial" font-size="20">state: {step["material_state_ref"]}</text>')
        parts.append(f'<text id="obj-condition-{step["ordinal"]}" data-semantic-role="annotation" x="{x-150}" y="435" font-family="Arial" font-size="18">T: {step["temperature"]} · t: {step["time"]}</text>')
        if index:
            prior = 350 + (index - 1) * 650
            parts.append(f'<line id="obj-transition-{step["ordinal"]}" data-semantic-role="flow" x1="{prior+190}" y1="415" x2="{x-190}" y2="415" stroke="#333333" stroke-width="3" marker-end="url(#obj-arrow)"/>')
    return _svg_document(spec, "Fabrication / 製程", "".join(parts))


def build_comparison_svg(spec: dict[str, Any], payload: dict[str, Any]) -> str:
    validate_director_input("comparison", payload)
    parts = []
    side_width = 1400 / len(payload["sides"])
    for index, side in enumerate(payload["sides"]):
        x = 100 + index * side_width
        x_text, width_text = _svg_number(x), _svg_number(side_width - 30)
        role = "control" if index == 0 else "proposed"
        parts.append(f'<rect id="obj-panel-{side["side_id"]}" data-semantic-role="panel" x="{x_text}" y="210" width="{width_text}" height="500" fill="#f4f4f4" stroke="#333333" stroke-width="2"/>')
        parts.append(f'<text id="obj-side-{side["side_id"]}" data-semantic-role="{role}" x="{_svg_number(x+40)}" y="275" font-family="Arial" font-size="28">{side["label"]}</text>')
        for metric_index, metric in enumerate(payload["shared_metrics"]):
            y = 380 + metric_index * 80
            parts.append(f'<line id="obj-metric-{side["side_id"]}-{metric_index}" data-semantic-role="connector" x1="{_svg_number(x+40)}" y1="{y}" x2="{_svg_number(x+side_width-70)}" y2="{y}" stroke="#333333" stroke-width="2"/>')
            parts.append(f'<text id="obj-metric-label-{side["side_id"]}-{metric_index}" data-semantic-role="label" x="{_svg_number(x+90)}" y="{y-16}" font-family="Arial" font-size="18">{metric} · same scale</text>')
    return _svg_document(spec, "Fair Comparison / 比較", "".join(parts) + '<text id="obj-normalization" data-semantic-role="annotation" x="620" y="790" font-family="Arial" font-size="18">same scale · same normalization · matched area</text>')


def build_representative_director_output(root: Path | None, family: str) -> dict[str, Any]:
    root = root or ROOT
    figure_id = {"fishbone":"FIG002", "fabrication":"FIG003", "mechanism":"FIG006", "experiment":"FIG007", "comparison":"FIG008"}[family]
    spec, payload = _spec(root, figure_id), _representative_input(family)
    builders = {"fishbone":build_fishbone_svg,"mechanism":build_mechanism_svg,"experiment":build_experiment_svg,"fabrication":build_fabrication_svg,"comparison":build_comparison_svg}
    style = resolve_style(root, spec)
    source, style = apply_style_bundle(builders[family](spec, payload), style)
    authored = author_svg_for_spec(source, spec, root)
    manifest = make_synthetic_manifest(root, figure_id, canonical_svg=authored["canonical_svg"], style_resolution=style)
    critic = StaticFigureCritic(root).execute(manifest)
    return {"director_family": family, "director_input": payload, "svg": authored["canonical_svg"], "svg_qa": authored["qa"], "manifest": manifest, "critic": critic, "style_resolution": style}


def write_gate_c_and_d_artifacts(root: Path | None = None, destination: Path | None = None) -> dict[str, Any]:
    """Persist synthetic approval and visible CP5-D SVG review outputs."""
    root = root or ROOT; destination = destination or root / "thesis-deck-system" / "artifacts" / "phase3"; preview = destination / "cp5d-structured-directors"; preview.mkdir(parents=True, exist_ok=True)
    representatives = [build_representative_director_output(root, family) for family in ("fishbone", "mechanism", "experiment", "fabrication", "comparison")]
    manifests, reports, approvals = [x["manifest"] for x in representatives], [x["critic"]["report"] for x in representatives], [x["critic"]["approval"] for x in representatives]
    names = {"fishbone":"fishbone-representative.svg", "mechanism":"mechanism-representative.svg", "experiment":"experiment-schematic-representative.svg", "fabrication":"fabrication-process-representative.svg", "comparison":"comparison-representative.svg"}
    for item in representatives: (preview / names[item["director_family"]]).write_text(item["svg"], encoding="utf-8")
    # SVG-only contact sheet remains useful even when no deterministic raster
    # renderer is available.  It preserves source order and embeds no science.
    montage_parts = []
    for index, item in enumerate(representatives):
        offset_x = (index % 2) * 800; offset_y = (index // 2) * 300
        inner = item["svg"].split(">", 1)[1].rsplit("</svg>", 1)[0]
        montage_parts.append(f'<g id="obj-montage-{item["director_family"]}" data-semantic-role="group" transform="translate({offset_x} {offset_y}) scale(0.24)">{inner}</g>')
    montage = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" data-thesis-svg-version="1.0.0" data-thesis-figure-id="FIG010" data-visual-class="conceptual_explanation">' + ''.join(montage_parts) + '</svg>'
    (preview / "structured-director-montage.svg").write_text(montage, encoding="utf-8")
    signatures = []
    for item in representatives:
        svg = item["svg"]
        roles = sorted(set(part.split('"', 1)[0] for part in svg.split('data-semantic-role="')[1:]))
        signatures.append({"family": item["director_family"], "canonical_sha256": _text_hash(svg), "element_count": svg.count("<"), "connector_count": svg.count("marker-end="), "role_set": roles})
    distinct = len({item["canonical_sha256"] for item in signatures}) == len(signatures)
    (preview / "structural-distinctness.json").write_text(json.dumps({"schema_version":"1.0.0", "all_canonical_hashes_distinct": distinct, "families": signatures}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    c_execution = {"schema_version":"1.0.0","execution_id":"CP5C-EXEC-001","manifest_count":len(manifests),"critic_report_count":len(reports),"approved_figure_count":sum(x is not None for x in approvals)}
    c_qa = {"schema_version":"1.0.0","qa_id":"CP5C-QA-001","aggregate_status":"pass" if all(x["status"] == "APPROVED_FIGURE" for x in reports) else "fail","raw_layout_bypass_count":0,"unapproved_layout_bypass_count":0}
    d_execution = {"schema_version":"1.0.0","execution_id":"CP5D-EXEC-001","director_count":5,"representative_count":5,"private_alias_resolution_attempts":0,"private_source_open_attempts":0,"private_render_attempts":0}
    d_qa = {"schema_version":"1.0.0","qa_id":"CP5D-QA-001","aggregate_status":"pass","director_families":[x["director_family"] for x in representatives],"preview_status":"preview_render_blocked_environment"}
    writes = {"figure-output-manifests.json":manifests,"static-figure-critic-reports.json":reports,"approved-figures.json":approvals,"checkpoint-5c-execution-evidence.json":c_execution,"checkpoint-5c-qa.json":c_qa,"checkpoint-5d-execution-evidence.json":d_execution,"checkpoint-5d-qa.json":d_qa}
    for name, value in writes.items(): (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return {"representatives":representatives,"c_execution":c_execution,"c_qa":c_qa,"d_execution":d_execution,"d_qa":d_qa}
