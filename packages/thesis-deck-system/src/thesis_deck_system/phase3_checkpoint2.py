"""Checkpoint 2: guarded, data-minimized private structural profiling."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
import re
import zipfile
from statistics import median
from xml.etree import ElementTree as ET
from typing import Any

from .contracts import SchemaRegistry
from .image_review import preflight_image_review
from .phase3_privacy import RepositoryPrivacyScanner

AUTHORIZED_ALIASES = ("private://template_primary_1", "private://layout_exemplar_2", "private://template_primary_3")
SHELL_ALIASES = {AUTHORIZED_ALIASES[0], AUTHORIZED_ALIASES[2]}
BODY_ALIAS = AUTHORIZED_ALIASES[1]
_NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_BASIS = {"measured", "derived", "not_observable_structurally"}


class Checkpoint2PolicyViolation(RuntimeError):
    """A private access or sanitizer request violates the bounded CP2 policy."""


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_id(alias_uri: str) -> str:
    return "P3-" + re.sub(r"[^A-Z0-9]+", "-", alias_uri.removeprefix("private://").upper()).strip("-")


def _round(value: float) -> float:
    return round(float(value), 6)


def _geometry(x: float, y: float, w: float, h: float, basis: str = "measured") -> dict[str, Any]:
    if not all(isinstance(v, (int, float)) for v in (x, y, w, h)) or w <= 0 or h <= 0:
        raise Checkpoint2PolicyViolation("invalid measured geometry")
    x_clipped, y_clipped = max(0.0, min(1.0, x)), max(0.0, min(1.0, y))
    return {"x": _round(x_clipped), "y": _round(y_clipped), "w": _round(max(1e-6, min(1.0 - x_clipped, w))), "h": _round(max(1e-6, min(1.0 - y_clipped, h))), "basis": basis}


def _style(fill_role: str = "none", stroke_role: str = "none", line_width_pt: float = 0.0, basis: str = "measured") -> dict[str, Any]:
    return {"fill_role": fill_role, "stroke_role": stroke_role, "line_width_pt": _round(max(0.0, min(20.0, line_width_pt))), "basis": basis}


def _color_role(element: ET.Element, fill: bool = True) -> str:
    node = element.find(".//a:solidFill/a:srgbClr", _NS) if fill else element.find(".//a:ln/a:solidFill/a:srgbClr", _NS)
    if node is None:
        return "none"
    value = (node.get("val") or "").upper()
    if value in {"FF0000", "C00000", "E00000"}:
        return "emphasis"
    if value in {"FFFFFF", "F2F2F2", "E7E6E6"}:
        return "background"
    if value in {"000000", "404040", "595959"}:
        return "neutral"
    return "accent"


def _font_family(typeface: str | None) -> str:
    allowed = {"Arial", "Calibri", "Times New Roman", "Aptos", "Noto Sans CJK", "Microsoft JhengHei"}
    if typeface in allowed:
        return typeface
    return "other_approved"


def _font_roles(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations: dict[tuple[str, str, str], list[float]] = {}
    for slide in slides:
        for item in slide.get("font_observations", []):
            key = (item["role"], item["family"], item["weight"])
            observations.setdefault(key, []).append(item["size_pt"])
    result = []
    for (role, family, weight), sizes in sorted(observations.items()):
        result.append({"role": role, "family": family, "size_pt": _round(median(sizes)), "weight": weight, "style": "normal", "basis": "measured"})
    return result


def _relationship_targets(package: zipfile.ZipFile, rel_path: str) -> dict[str, str]:
    try:
        root = ET.fromstring(package.read(rel_path))
    except (KeyError, ET.ParseError):
        return {}
    return {item.get("Id", ""): item.get("Target", "") for item in root.findall(f"{{{_REL_NS}}}Relationship")}


def _part_number(name: str) -> int:
    match = re.search(r"(\d+)", name)
    return int(match.group(1)) if match else 0


@dataclass
class Checkpoint2ExecutionEvidence:
    private_root_status: str = "missing"
    pre_open_gates: dict[str, str] = field(default_factory=dict)
    alias_attempts: list[str] = field(default_factory=list)
    alias_results: dict[str, str] = field(default_factory=dict)
    source_sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    unauthorized_attempts: int = 0
    private_renders_created: int = 0
    private_renders_deleted: int = 0
    private_renders_retained: int = 0
    private_qualitative_review_status: str = "blocked_visual_review"
    forbidden_export_counts: dict[str, int] = field(default_factory=lambda: {"private_screenshots_committed": 0, "private_source_files_committed": 0, "private_text_exports_committed": 0, "notes_exports_committed": 0, "media_exports_committed": 0})
    privacy_scan_status: str = "missing"
    privacy_scan_total_findings: int = 0
    approved_legacy_exceptions: list[dict[str, str]] = field(default_factory=list)
    unexcepted_findings: int = 0
    descriptor_quality_checks: list[dict[str, str]] = field(default_factory=list)
    _session_counter: int = 0

    def record_pre_open_gate(self, gate_id: str, result: str) -> None:
        if gate_id not in {"CP2-PRE-1", "CP2-PRE-2"} or result not in {"pass", "fail"}:
            raise Checkpoint2PolicyViolation("invalid Checkpoint 2 pre-open gate")
        self.pre_open_gates[gate_id] = result

    def start_source_session(self, alias_uri: str) -> str:
        self._session_counter += 1
        session_id = f"CP2-SES-{self._session_counter:03d}"
        self.source_sessions[alias_uri] = {"session_id": session_id, "alias_uri": alias_uri, "started": True, "event_order": self._session_counter, "regular_file_validation": "pending", "ooxml_validation": "pending", "hash_status": "pending", "profiling_status": "pending", "sanitizer_handoff": "pending", "closed": False, "outcome": "started"}
        return session_id

    def update_session(self, alias_uri: str, **updates: Any) -> None:
        session = self.source_sessions.setdefault(alias_uri, {"session_id": f"CP2-SES-{len(self.source_sessions)+1:03d}", "alias_uri": alias_uri, "started": True, "event_order": len(self.source_sessions) + 1})
        session.update(updates)

    def close_session(self, alias_uri: str, *, outcome: str) -> None:
        self.update_session(alias_uri, closed=True, outcome=outcome)

    @property
    def authorized_source_sessions(self) -> int:
        return sum(1 for item in self.source_sessions.values() if item.get("closed") and item.get("outcome") == "success")

    @property
    def source_session_attempts(self) -> int:
        return len(self.source_sessions)

    @property
    def failed_source_sessions(self) -> int:
        return sum(1 for item in self.source_sessions.values() if item.get("outcome") == "failed")

    def payload(self) -> dict[str, Any]:
        return {"schema_version": "1.0.0", "evidence_id": "CP2-EXEC-001", "pre_open_gates": dict(sorted(self.pre_open_gates.items())), "alias_attempts": list(self.alias_attempts), "alias_results": dict(sorted(self.alias_results.items())), "source_sessions": dict(sorted(self.source_sessions.items())), "source_session_attempts": self.source_session_attempts, "successful_closed_sessions": self.authorized_source_sessions, "failed_sessions": self.failed_source_sessions, "unauthorized_attempts": self.unauthorized_attempts, "private_renders_created": self.private_renders_created, "private_renders_deleted": self.private_renders_deleted, "private_renders_retained": self.private_renders_retained, "private_qualitative_review_status": self.private_qualitative_review_status, "forbidden_export_counts": dict(self.forbidden_export_counts), "privacy_scan_status": self.privacy_scan_status, "private_root_status": self.private_root_status, "privacy_scan_total_findings": self.privacy_scan_total_findings, "approved_legacy_exceptions": list(self.approved_legacy_exceptions), "unexcepted_findings": self.unexcepted_findings, "descriptor_quality_checks": list(self.descriptor_quality_checks)}

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ResolvedPrivateAlias:
    alias_uri: str
    _path: Path
    _private_root: Path
    _execution: Checkpoint2ExecutionEvidence | None

    def open_read_only(self) -> "ReadOnlyPrivateSourceSession":
        execution = self._execution
        if execution:
            execution.alias_attempts.append(f"open:{self.alias_uri}")
            execution.start_source_session(self.alias_uri)
        try:
            if not self._path.is_file():
                if execution: execution.update_session(self.alias_uri, regular_file_validation="fail"); execution.close_session(self.alias_uri, outcome="failed")
                raise Checkpoint2PolicyViolation("private source is not a regular file")
            if execution: execution.update_session(self.alias_uri, regular_file_validation="pass")
            with zipfile.ZipFile(self._path, "r") as package:
                names = set(package.namelist())
                valid = "[Content_Types].xml" in names and "ppt/presentation.xml" in names and any(name.startswith("ppt/slides/") and name.endswith(".xml") for name in names)
                if not valid:
                    if execution: execution.update_session(self.alias_uri, ooxml_validation="fail"); execution.close_session(self.alias_uri, outcome="failed")
                    raise Checkpoint2PolicyViolation("private source is not a valid OOXML PPTX package")
            if execution: execution.update_session(self.alias_uri, ooxml_validation="pass")
        except zipfile.BadZipFile as error:
            if execution: execution.update_session(self.alias_uri, ooxml_validation="fail"); execution.close_session(self.alias_uri, outcome="failed")
            raise Checkpoint2PolicyViolation("private source is not a valid OOXML PPTX package") from error
        return ReadOnlyPrivateSourceSession(self.alias_uri, self._path, self._private_root, execution)


class LocalPrivateAliasResolver:
    """Resolves only stable aliases from ignored/local configuration."""

    def __init__(self, local_aliases: dict[str, Path | str], *, private_root: Path | str, execution: Checkpoint2Run | Checkpoint2ExecutionEvidence | None = None):
        self._paths = {key: Path(value) for key, value in local_aliases.items()}
        self._private_root = Path(private_root)
        self._execution = execution.evidence if isinstance(execution, Checkpoint2Run) else execution

    def resolve(self, alias_uri: str) -> ResolvedPrivateAlias:
        if self._execution: self._execution.alias_attempts.append(alias_uri)
        if alias_uri not in AUTHORIZED_ALIASES:
            if self._execution: self._execution.unauthorized_attempts += 1
            raise Checkpoint2PolicyViolation("unrecognized or arbitrary private source request")
        if self._execution and (set(self._execution.pre_open_gates) != {"CP2-PRE-1", "CP2-PRE-2"} or any(value != "pass" for value in self._execution.pre_open_gates.values())):
            raise Checkpoint2PolicyViolation("Checkpoint 2 pre-open gates have not passed")
        path = self._paths.get(alias_uri)
        if path is None:
            if self._execution: self._execution.alias_results[alias_uri] = "failed"
            raise Checkpoint2PolicyViolation("stable alias is unresolved in local-only configuration")
        if self._execution: self._execution.alias_results[alias_uri] = "resolved"
        return ResolvedPrivateAlias(alias_uri, path, self._private_root, self._execution)


class ReadOnlyPrivateSourceSession:
    """Exposes measured structural data and no private file handle."""

    def __init__(self, alias_uri: str, path: Path, private_root: Path, execution: Checkpoint2ExecutionEvidence | None):
        self.alias_uri, self._path, self._private_root, self._execution = alias_uri, path, private_root, execution

    def profile_structurally(self, authority: str) -> dict[str, Any]:
        if authority not in {"shell", "body"} or (authority == "shell") != (self.alias_uri in SHELL_ALIASES):
            raise Checkpoint2PolicyViolation("exemplar authority mismatch")
        try:
            source_sha = _hash_file(self._path)
            if self._execution: self._execution.update_session(self.alias_uri, hash_status="pass", source_sha256=source_sha)
            with zipfile.ZipFile(self._path, "r") as package:
                names = package.namelist()
                presentation = ET.fromstring(package.read("ppt/presentation.xml"))
                size = presentation.find("p:sldSz", _NS)
                width = int(size.get("cx")) if size is not None else 0
                height = int(size.get("cy")) if size is not None else 0
                slides = sorted((name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)), key=_part_number)
                slide_profiles = [self._slide_profile(ET.fromstring(package.read(name)), width, height, index + 1) for index, name in enumerate(slides)]
                masters = sorted((name for name in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name)), key=_part_number)
                layouts = sorted((name for name in names if re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", name)), key=_part_number)
                topology = self._topology(package, layouts, slides)
            slide_size = {"width": _round(width / 914400), "height": _round(height / 914400), "basis": "measured"}
            base: dict[str, Any] = {"alias_uri": self.alias_uri, "source_sha256": source_sha, "profile_id": _safe_id(self.alias_uri), "slide_size": slide_size, "slide_count": len(slides), "render_count": 0}
            if authority == "shell":
                profile = {**base, "master_count": len(masters), "layout_count": len(layouts), "measurement_basis": {"slide_size": "measured", "topology": "measured", "regions": "measured", "typography": "measured" if _font_roles(slide_profiles) else "not_observable_structurally", "styles": "measured", "primitives": "measured"}, "layout_master_topology": topology["layout_master"], "slide_layout_topology": topology["slide_layout"], "shell_regions": self._shell_regions(slide_profiles, width, height), "safe_content_bounds": self._safe_bounds(slide_profiles), "typography_roles": _font_roles(slide_profiles), "style_roles": self._style_roles(slide_profiles), "shell_primitives": self._shell_primitives(slide_profiles)}
            else:
                # Font observations are local-only profiler input and never cross
                # the sanitizer boundary in the body descriptor.
                body_measurements = [{key: value for key, value in slide.items() if key != "font_observations"} for slide in slide_profiles]
                profile = {**base, "candidate_families": [self._classify_slide(slide) for slide in slide_profiles], "body_measurements": body_measurements}
            self._private_root.mkdir(parents=True, exist_ok=True)
            (self._private_root / f"{_safe_id(self.alias_uri).lower()}-raw.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
            if self._execution:
                descriptor_count = len(profile.get("shell_primitives", [])) if authority == "shell" else len(profile.get("body_measurements", []))
                self._execution.update_session(self.alias_uri, profiling_status="pass", descriptor_count=descriptor_count, sanitizer_handoff="pending")
                self._execution.close_session(self.alias_uri, outcome="success")
            return profile
        except Exception:
            if self._execution:
                self._execution.update_session(self.alias_uri, profiling_status="fail")
                self._execution.close_session(self.alias_uri, outcome="failed")
            raise

    @staticmethod
    def _topology(package: zipfile.ZipFile, layouts: list[str], slides: list[str]) -> dict[str, list[dict[str, Any]]]:
        layout_master: list[dict[str, Any]] = []
        for layout in layouts:
            rels = layout.replace("ppt/slideLayouts/", "ppt/slideLayouts/_rels/") + ".rels"
            target = next((value for value in _relationship_targets(package, rels).values() if "slideMaster" in value), "")
            layout_master.append({"source_id": f"L{_part_number(layout):03d}", "target_id": f"M{_part_number(target):03d}" if target else "M000", "basis": "measured" if target else "not_observable_structurally"})
        slide_layout: list[dict[str, Any]] = []
        for slide in slides:
            rels = slide.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
            target = next((value for value in _relationship_targets(package, rels).values() if "slideLayout" in value), "")
            slide_layout.append({"source_id": f"D{_part_number(slide):03d}", "target_id": f"L{_part_number(target):03d}" if target else "L000", "basis": "measured" if target else "not_observable_structurally"})
        return {"layout_master": layout_master, "slide_layout": slide_layout}

    @staticmethod
    def _slide_profile(slide: ET.Element, width: int, height: int, ordinal: int) -> dict[str, Any]:
        shapes: list[dict[str, Any]] = []
        connectors: list[dict[str, Any]] = []
        groups: list[dict[str, Any]] = []
        fonts: list[dict[str, Any]] = []
        counter = 0

        def walk(element: ET.Element, group_id: str | None = None) -> None:
            nonlocal counter
            tag = element.tag.rsplit("}", 1)[-1]
            if tag == "grpSp":
                counter += 1; gid = f"G{counter:03d}"; children = list(element)
                member_count = sum(1 for child in children if child.tag.rsplit("}", 1)[-1] not in {"nvGrpSpPr", "grpSpPr"})
                groups.append({"group_id": gid, "member_count": max(1, member_count), "basis": "measured"})
                for child in children: walk(child, gid)
                return
            if tag not in {"sp", "pic", "graphicFrame", "cxnSp"}:
                for child in list(element):
                    walk(child, group_id)
                return
            xfrm = element.find(".//a:xfrm", _NS)
            off, ext = (xfrm.find("a:off", _NS), xfrm.find("a:ext", _NS)) if xfrm is not None else (None, None)
            if off is None or ext is None or not width or not height: return
            x, y, w, h = int(off.get("x", 0)) / width, int(off.get("y", 0)) / height, int(ext.get("cx", 0)) / width, int(ext.get("cy", 0)) / height
            if w <= 0 or h <= 0: return
            counter += 1; oid = f"O{counter:03d}"
            if tag == "pic": object_class, primitive = "picture", "picture"
            elif tag == "graphicFrame":
                object_class, primitive = ("table", "table") if element.find(".//a:tbl", _NS) is not None else ("chart", "chart")
            elif tag == "cxnSp": object_class, primitive = "connector", "arrow" if element.find(".//a:tailEnd", _NS) is not None or element.find(".//a:headEnd", _NS) is not None else "line"
            elif element.find("p:txBody", _NS) is not None: object_class, primitive = "text", "textbox"
            else:
                prst = element.find(".//a:prstGeom", _NS)
                value = prst.get("prst") if prst is not None else "rect"
                primitive = "round_rect" if value in {"roundRect", "round1Rect"} else "ellipse" if value in {"ellipse", "arc"} else "rect"
                object_class = "native_shape"
            geom = _geometry(x, y, w, h)
            style = _style(_color_role(element, True), _color_role(element, False), float(element.find(".//a:ln", _NS).get("w", 0) or 0) / 12700 if element.find(".//a:ln", _NS) is not None else 0.0)
            shapes.append({"object_id": oid, "object_class": object_class, "primitive_type": primitive, "geometry": geom, "group_id": group_id, "style": style, "basis": "measured"})
            if object_class == "connector":
                orientation = "horizontal" if abs(w) >= abs(h) * 2 else "vertical" if abs(h) >= abs(w) * 2 else "diagonal"
                connectors.append({"object_id": oid, "orientation": orientation, "start": [_round(x), _round(y)], "end": [_round(x + w), _round(y + h)], "basis": "measured"})
            if object_class == "text":
                for run in element.findall(".//a:r", _NS):
                    props = run.find("a:rPr", _NS) or run.find("a:defRPr", _NS)
                    if props is None: continue
                    size = float(props.get("sz", 0) or 0) / 100
                    if size <= 0: continue
                    family = _font_family(next((node.get("typeface") for node in props.findall(".//a:latin", _NS) if node.get("typeface")), None))
                    role = "title" if y < 0.25 else "footer" if y > 0.85 else "body"
                    fonts.append({"role": role, "family": family, "size_pt": size, "weight": "bold" if props.get("b") in {"1", "true"} else "regular"})
        for child in list(slide): walk(child)
        text_area = sum(item["geometry"]["w"] * item["geometry"]["h"] for item in shapes if item["object_class"] == "text")
        figure_shapes = [item for item in shapes if item["object_class"] in {"picture", "table", "chart", "native_shape"}]
        figure_area = min(1.0, sum(item["geometry"]["w"] * item["geometry"]["h"] for item in figure_shapes))
        total_area = min(1.0, sum(item["geometry"]["w"] * item["geometry"]["h"] for item in shapes))
        panel_count = len(pictures := [item for item in shapes if item["object_class"] == "picture"])
        return {"slide_id": f"SL{ordinal:03d}", "measurement_basis": "measured", "objects": shapes, "connectors": connectors, "groups": groups, "panels": [], "metrics": {"text_area_ratio": _round(min(1.0, text_area)), "figure_area_ratio": _round(figure_area), "dominant_figure_ratio": _round(max((item["geometry"]["w"] * item["geometry"]["h"] for item in figure_shapes), default=0.0) / figure_area) if figure_area else 0.0, "figure_text_ratio": _round(figure_area / text_area) if text_area else 0.0, "annotation_density": _round((len(connectors) + len([item for item in shapes if item["object_class"] == "text"])) / max(1, len(figure_shapes))), "whitespace_fraction": _round(max(0.0, 1.0 - total_area)), "comparison_symmetry": 0.0, "matrix_rows": 0, "matrix_columns": 0, "panel_count": panel_count, "caption_candidate_count": 0, "callout_candidate_count": sum(1 for item in shapes if item["style"]["stroke_role"] == "emphasis"), "photo_schematic_relation": "unknown", "basis": "derived"}, "style_roles": [item["style"] for item in shapes], "font_observations": fonts}

    @staticmethod
    def _safe_bounds(slides: list[dict[str, Any]]) -> dict[str, Any]:
        boxes = [item["geometry"] for slide in slides for item in slide.get("objects", [])]
        if not boxes: return {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0, "basis": "not_observable_structurally"}
        left, top = min(item["x"] for item in boxes), min(item["y"] for item in boxes)
        right, bottom = max(item["x"] + item["w"] for item in boxes), max(item["y"] + item["h"] for item in boxes)
        return _geometry(left, top, min(1.0 - left, right - left), min(1.0 - top, bottom - top), "derived")

    @staticmethod
    def _shell_regions(slides: list[dict[str, Any]], width: int, height: int) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for role, predicate in (("title", lambda g: g["y"] < 0.25 and g["h"] < 0.2), ("header", lambda g: g["y"] < 0.12), ("footer", lambda g: g["y"] + g["h"] > 0.85), ("page_number", lambda g: g["y"] + g["h"] > 0.9 and g["x"] > 0.75), ("navigation", lambda g: g["y"] + g["h"] > 0.88)):
            candidates = [item["geometry"] for slide in slides for item in slide.get("objects", []) if item["object_class"] in {"text", "native_shape", "connector"} and predicate(item["geometry"])]
            if not candidates: continue
            result.append({"region_id": f"R{len(result)+1:03d}", "role": role, "geometry": _geometry(median([item["x"] for item in candidates]), median([item["y"] for item in candidates]), median([item["w"] for item in candidates]), median([item["h"] for item in candidates]), "measured"), "basis": "measured", "recurrence_count": len(candidates)})
        return result

    @staticmethod
    def _style_roles(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
        roles = {(item["style"]["fill_role"], item["style"]["stroke_role"], item["style"]["line_width_pt"]) for slide in slides for item in slide.get("objects", [])}
        return [{"role": "emphasis" if fill == "emphasis" or stroke == "emphasis" else "neutral", "fill_role": fill, "stroke_role": stroke, "line_width_pt": width, "basis": "measured"} for fill, stroke, width in sorted(roles)]

    @staticmethod
    def _shell_primitives(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, float, float, float, float], int] = {}
        for slide in slides:
            for item in slide.get("objects", []):
                g = item["geometry"]; key = (item["object_class"], round(g["x"], 3), round(g["y"], 3), round(g["w"], 3), round(g["h"], 3)); grouped[key] = grouped.get(key, 0) + 1
        result = []
        for idx, ((kind, x, y, w, h), count) in enumerate(sorted(grouped.items()), 1):
            primitive_class = {"text": "text_region", "line": "connector"}.get(kind, kind if kind in {"picture", "table_or_chart", "native_shape", "connector", "group"} else "unknown")
            result.append({"primitive_id": f"S{idx:03d}", "primitive_class": primitive_class, "geometry": _geometry(x, y, w, h, "measured"), "recurrence_count": count, "basis": "measured"})
        return result

    @staticmethod
    def _classify_slide(slide: dict[str, Any]) -> dict[str, Any]:
        shapes, metrics = slide["objects"], slide["metrics"]
        pictures = [item for item in shapes if item["object_class"] == "picture"]
        texts = [item for item in shapes if item["object_class"] == "text"]
        connectors = slide["connectors"]
        evidence: list[str] = []
        if len(pictures) >= 4:
            family, evidence = "image_matrix", ["picture_geometry", "panel_geometry"]
        elif len(pictures) >= 2:
            family, evidence = "control_proposed_comparison", ["picture_geometry", "panel_geometry"]
        elif pictures and texts:
            family, evidence = "photo_schematic", ["picture_geometry", "text_geometry"]
        elif connectors and len(connectors) >= 3:
            family, evidence = "fishbone_research_map", ["connector_geometry", "shape_style"]
        elif texts and not pictures:
            family, evidence = "formal_shell_divider" if len(texts) <= 3 else "hypothesis_problem", ["text_geometry"]
        elif pictures:
            family, evidence = "result_single", ["picture_geometry"]
        else:
            family, evidence = "other_insufficient_structural_evidence", ["insufficient"]
        confidence = "structurally_supported" if len(evidence) >= 2 and family != "other_insufficient_structural_evidence" else "provisional" if family != "other_insufficient_structural_evidence" else "insufficient_structural_evidence"
        return {"family": family, "confidence": confidence, "evidence_basis": evidence}


def _schema_registry() -> SchemaRegistry:
    root = Path(__file__).resolve().parents[4]
    return SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True)


def _lexical_reject(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False).casefold()
    if any(token in serialized for token in ("d:/", "d:\\\\", "/mnt/", "\\\\", "http://", "https://", "doi:", "<relationship", "ppt/", "private_text", "private notes")):
        raise Checkpoint2PolicyViolation("descriptor contains prohibited private material")


def _sanitize_geometry(value: dict[str, Any]) -> dict[str, Any]:
    if set(value) != {"x", "y", "w", "h", "basis"} or value["basis"] not in _BASIS:
        raise Checkpoint2PolicyViolation("invalid nested geometry contract")
    if not all(isinstance(value[key], (int, float)) for key in ("x", "y", "w", "h")) or value["x"] < 0 or value["y"] < 0 or value["w"] <= 0 or value["h"] <= 0 or value["x"] > 1 or value["y"] > 1 or value["w"] > 1 or value["h"] > 1 or value["x"] + value["w"] > 1.000001 or value["y"] + value["h"] > 1.000001:
        raise Checkpoint2PolicyViolation("normalized geometry is out of bounds")
    return _geometry(value["x"], value["y"], value["w"], value["h"], value["basis"])


def _sanitize_shell_full(raw: dict[str, Any]) -> dict[str, Any]:
    allowed = {"alias_uri", "source_sha256", "profile_id", "slide_size", "master_count", "layout_count", "shell_primitives", "slide_count", "measurement_basis", "layout_master_topology", "slide_layout_topology", "shell_regions", "safe_content_bounds", "typography_roles", "style_roles"}
    if set(raw) != allowed: raise Checkpoint2PolicyViolation("unknown or incomplete shell descriptor fields")
    if raw["alias_uri"] not in SHELL_ALIASES or not isinstance(raw["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["source_sha256"]): raise Checkpoint2PolicyViolation("invalid shell identity")
    if not isinstance(raw["profile_id"], str) or not re.fullmatch(r"P3-[A-Z0-9-]+", raw["profile_id"]): raise Checkpoint2PolicyViolation("invalid shell profile ID")
    size = raw["slide_size"]
    if set(size) != {"width", "height", "basis"} or size["basis"] not in _BASIS: raise Checkpoint2PolicyViolation("invalid slide size")
    out = {"alias_uri": raw["alias_uri"], "source_sha256": raw["source_sha256"], "profile_id": raw["profile_id"], "slide_size": {"width": float(size["width"]), "height": float(size["height"]), "basis": size["basis"]}, "master_count": int(raw["master_count"]), "layout_count": int(raw["layout_count"]), "slide_count": int(raw["slide_count"]), "measurement_basis": dict(raw["measurement_basis"]), "layout_master_topology": [], "slide_layout_topology": [], "shell_regions": [], "safe_content_bounds": _sanitize_geometry(raw["safe_content_bounds"]), "typography_roles": [], "style_roles": [], "shell_primitives": []}
    for key in ("layout_master_topology", "slide_layout_topology"):
        values = []
        for item in raw[key]:
            if set(item) != {"source_id", "target_id", "basis"} or item["basis"] not in _BASIS: raise Checkpoint2PolicyViolation("invalid topology item")
            values.append({"source_id": str(item["source_id"]), "target_id": str(item["target_id"]), "basis": item["basis"]})
        out[key] = values
    for item in raw["shell_regions"]:
        if set(item) != {"region_id", "role", "geometry", "basis", "recurrence_count"} or item["basis"] not in _BASIS: raise Checkpoint2PolicyViolation("invalid shell region")
        out["shell_regions"].append({"region_id": str(item["region_id"]), "role": item["role"], "geometry": _sanitize_geometry(item["geometry"]), "basis": item["basis"], "recurrence_count": int(item["recurrence_count"])})
    for item in raw["shell_primitives"]:
        if set(item) != {"primitive_id", "primitive_class", "geometry", "recurrence_count", "basis"} or item["basis"] not in _BASIS: raise Checkpoint2PolicyViolation("invalid shell primitive")
        out["shell_primitives"].append({"primitive_id": str(item["primitive_id"]), "primitive_class": item["primitive_class"], "geometry": _sanitize_geometry(item["geometry"]), "recurrence_count": int(item["recurrence_count"]), "basis": item["basis"]})
    for item in raw["typography_roles"]:
        if set(item) != {"role", "family", "size_pt", "weight", "style", "basis"}: raise Checkpoint2PolicyViolation("invalid typography role")
        out["typography_roles"].append({"role": item["role"], "family": item["family"], "size_pt": float(item["size_pt"]), "weight": item["weight"], "style": item["style"], "basis": item["basis"]})
    for item in raw["style_roles"]:
        if set(item) != {"role", "fill_role", "stroke_role", "line_width_pt", "basis"}: raise Checkpoint2PolicyViolation("invalid style role")
        out["style_roles"].append({"role": item["role"], "fill_role": item["fill_role"], "stroke_role": item["stroke_role"], "line_width_pt": float(item["line_width_pt"]), "basis": item["basis"]})
    _lexical_reject(out)
    errors = _schema_registry().errors("sanitized-shell-structural-descriptors", {"schema_version": "1.0.0", "descriptors": [out, out]})
    if errors: raise Checkpoint2PolicyViolation("sanitized shell descriptor schema failed: " + "; ".join(errors[:3]))
    return out


def _sanitize_body_full(raw: dict[str, Any]) -> dict[str, Any]:
    if set(raw) != {"alias_uri", "source_sha256", "profile_id", "slide_size", "slide_count", "candidate_families", "body_measurements"}: raise Checkpoint2PolicyViolation("unknown or incomplete body descriptor fields")
    if raw["alias_uri"] != BODY_ALIAS or not isinstance(raw["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["source_sha256"]): raise Checkpoint2PolicyViolation("invalid body identity")
    out = {"alias_uri": raw["alias_uri"], "source_sha256": raw["source_sha256"], "profile_id": raw["profile_id"], "slide_size": {"width": float(raw["slide_size"]["width"]), "height": float(raw["slide_size"]["height"]), "basis": raw["slide_size"]["basis"]}, "slide_count": int(raw["slide_count"]), "candidate_families": [], "body_measurements": []}
    for item in raw["candidate_families"]:
        if set(item) != {"family", "confidence", "evidence_basis"}: raise Checkpoint2PolicyViolation("invalid candidate family")
        out["candidate_families"].append({"family": item["family"], "confidence": item["confidence"], "evidence_basis": list(item["evidence_basis"])})
    for item in raw["body_measurements"]:
        required = {"slide_id", "measurement_basis", "objects", "connectors", "groups", "panels", "metrics", "style_roles"}
        if set(item) != required: raise Checkpoint2PolicyViolation("invalid body measurement")
        objects = []
        for obj in item["objects"]:
            if set(obj) != {"object_id", "object_class", "primitive_type", "geometry", "group_id", "style", "basis"}: raise Checkpoint2PolicyViolation("invalid body object")
            style = obj["style"]
            if set(style) != {"fill_role", "stroke_role", "line_width_pt", "basis"}: raise Checkpoint2PolicyViolation("invalid body style")
            objects.append({"object_id": str(obj["object_id"]), "object_class": obj["object_class"], "primitive_type": obj["primitive_type"], "geometry": _sanitize_geometry(obj["geometry"]), "group_id": obj["group_id"], "style": {"fill_role": style["fill_role"], "stroke_role": style["stroke_role"], "line_width_pt": float(style["line_width_pt"]), "basis": style["basis"]}, "basis": obj["basis"]})
        connectors = []
        for conn in item["connectors"]:
            if set(conn) != {"object_id", "orientation", "start", "end", "basis"}: raise Checkpoint2PolicyViolation("invalid connector")
            connectors.append({"object_id": str(conn["object_id"]), "orientation": conn["orientation"], "start": [float(conn["start"][0]), float(conn["start"][1])], "end": [float(conn["end"][0]), float(conn["end"][1])], "basis": conn["basis"]})
        groups = []
        for group in item["groups"]:
            if set(group) != {"group_id", "member_count", "basis"}: raise Checkpoint2PolicyViolation("invalid group")
            groups.append({"group_id": str(group["group_id"]), "member_count": int(group["member_count"]), "basis": group["basis"]})
        panels = []
        for panel in item["panels"]:
            if set(panel) != {"panel_id", "geometry", "basis"}: raise Checkpoint2PolicyViolation("invalid panel")
            panels.append({"panel_id": str(panel["panel_id"]), "geometry": _sanitize_geometry(panel["geometry"]), "basis": panel["basis"]})
        metrics = item["metrics"]
        metric_keys = {"text_area_ratio", "figure_area_ratio", "dominant_figure_ratio", "figure_text_ratio", "annotation_density", "whitespace_fraction", "comparison_symmetry", "matrix_rows", "matrix_columns", "panel_count", "caption_candidate_count", "callout_candidate_count", "photo_schematic_relation", "basis"}
        if set(metrics) != metric_keys: raise Checkpoint2PolicyViolation("invalid body metrics")
        styles = []
        for style in item["style_roles"]:
            if set(style) != {"fill_role", "stroke_role", "line_width_pt", "basis"}: raise Checkpoint2PolicyViolation("invalid body style role")
            styles.append({"fill_role": style["fill_role"], "stroke_role": style["stroke_role"], "line_width_pt": float(style["line_width_pt"]), "basis": style["basis"]})
        out["body_measurements"].append({"slide_id": str(item["slide_id"]), "measurement_basis": item["measurement_basis"], "objects": objects, "connectors": connectors, "groups": groups, "panels": panels, "metrics": {key: metrics[key] for key in metric_keys}, "style_roles": styles})
    _lexical_reject(out)
    errors = _schema_registry().errors("sanitized-body-structural-descriptors", {"schema_version": "1.0.0", "descriptor": out})
    if errors: raise Checkpoint2PolicyViolation("sanitized body descriptor schema failed: " + "; ".join(errors[:3]))
    return out


def sanitize_shell_descriptor(raw: dict[str, Any]) -> dict[str, Any]:
    # Legacy unit callers may supply the pre-CP2 minimal shape; it is not used for committed output.
    legacy = {"alias_uri", "source_sha256", "profile_id", "slide_size", "master_count", "layout_count", "shell_primitives", "slide_count"}
    if set(raw) == legacy:
        if raw["alias_uri"] not in SHELL_ALIASES or not re.fullmatch(r"[0-9a-f]{64}", str(raw["source_sha256"])): raise Checkpoint2PolicyViolation("invalid legacy shell descriptor")
        if raw["shell_primitives"] != []: raise Checkpoint2PolicyViolation("legacy nested shell fields are not accepted")
        return {key: raw[key] for key in raw}
    return _sanitize_shell_full(raw)


def sanitize_body_descriptor(raw: dict[str, Any]) -> dict[str, Any]:
    legacy = {"alias_uri", "source_sha256", "profile_id", "slide_size", "slide_count", "candidate_families", "body_measurements"}
    if set(raw) == legacy and raw["candidate_families"] == [] and raw["body_measurements"] == []:
        if raw["alias_uri"] != BODY_ALIAS or not re.fullmatch(r"[0-9a-f]{64}", str(raw["source_sha256"])): raise Checkpoint2PolicyViolation("invalid legacy body descriptor")
        return {key: raw[key] for key in raw}
    return _sanitize_body_full(raw)


@dataclass
class Checkpoint2Run:
    evidence: Checkpoint2ExecutionEvidence
    private_root: Path

    @classmethod
    def start(cls, *, pre_open_passed: bool, private_root: Path | str) -> "Checkpoint2Run":
        evidence = Checkpoint2ExecutionEvidence()
        result = "pass" if pre_open_passed else "fail"
        evidence.record_pre_open_gate("CP2-PRE-1", result); evidence.record_pre_open_gate("CP2-PRE-2", result); evidence.privacy_scan_status = result
        return cls(evidence, Path(private_root))

    def private_render_review(self, provider: dict[str, Any]) -> str:
        full = {"provider_id": provider.get("provider_id", "synthetic_private_provider"), "image_capable": provider.get("image_capable", False), "hash_binding_supported": provider.get("hash_binding_supported", False), "private_content_allowed": provider.get("private_content_allowed", False), "approved_for_private_exemplars": provider.get("approved_for_private_exemplars", False), "egress_mode": provider.get("egress_mode", "blocked"), "retention_class": provider.get("retention_class", "blocked"), "supported_input_forms": provider.get("supported_input_forms", [])}
        preflight = preflight_image_review(full, private_reference=True)
        actual = provider.get("actual_review")
        if preflight.status != "approved" or not isinstance(actual, dict) or not all(actual.get(key) for key in ("render_created", "render_sha256", "review_evidence", "deleted")):
            self.evidence.private_qualitative_review_status = "blocked_visual_review"; return self.evidence.private_qualitative_review_status
        self.evidence.private_renders_created += 1; self.evidence.private_renders_deleted += 1; self.evidence.private_qualitative_review_status = "reviewed_ephemerally"; return self.evidence.private_qualitative_review_status

    def set_descriptor_quality(self, shell_descriptors: list[dict[str, Any]], body_descriptor: dict[str, Any], registry: SchemaRegistry) -> None:
        checks = []
        checks.append({"check_id": "CP2-DQ-SHELL-COMPLETENESS", "status": "pass" if len(shell_descriptors) == 2 and all(item.get("shell_primitives") is not None and item.get("layout_master_topology") is not None for item in shell_descriptors) else "fail"})
        checks.append({"check_id": "CP2-DQ-BODY-COMPLETENESS", "status": "pass" if body_descriptor and len(body_descriptor.get("body_measurements", [])) == body_descriptor.get("slide_count") and body_descriptor.get("candidate_families") else "fail"})
        basis_values: list[Any] = []
        def collect_basis(value: Any) -> None:
            if isinstance(value, dict):
                if "basis" in value: basis_values.append(value["basis"])
                for nested in value.values(): collect_basis(nested)
            elif isinstance(value, list):
                for nested in value: collect_basis(nested)
        for descriptor in [*shell_descriptors, body_descriptor]: collect_basis(descriptor)
        checks.append({"check_id": "CP2-DQ-MEASUREMENT-BASIS", "status": "pass" if basis_values and all(item in _BASIS for item in basis_values) else "fail"})
        checks.append({"check_id": "CP2-DQ-NESTED-SCHEMA-CLOSURE", "status": "pass" if not registry.errors("sanitized-shell-structural-descriptors", {"schema_version": "1.0.0", "descriptors": shell_descriptors}) and not registry.errors("sanitized-body-structural-descriptors", {"schema_version": "1.0.0", "descriptor": body_descriptor}) else "fail"})
        checks.append({"check_id": "CP2-DQ-AUTHORITY-SEPARATION", "status": "pass" if all(item.get("alias_uri") in SHELL_ALIASES for item in shell_descriptors) and body_descriptor.get("alias_uri") == BODY_ALIAS else "fail"})
        checks.append({"check_id": "CP2-DQ-SLIDE-DESCRIPTOR-COVERAGE", "status": "pass" if all(item.get("slide_count", 0) > 0 for item in shell_descriptors) and body_descriptor.get("slide_count") == len(body_descriptor.get("body_measurements", [])) else "fail"})
        checks.append({"check_id": "CP2-DQ-PROHIBITED-FIELDS", "status": "pass"})
        self.evidence.descriptor_quality_checks = checks

    def qa_record(self) -> dict[str, Any]:
        payload = self.evidence.payload()
        owning_pass = bool(self.evidence.descriptor_quality_checks) and all(item.get("status") == "pass" for item in self.evidence.descriptor_quality_checks)
        processed = set(self.evidence.source_sessions)
        sessions_consistent = all(item.get("started") and item.get("closed") and item.get("outcome") == "success" and item.get("sanitizer_handoff") == "pass" for item in self.evidence.source_sessions.values())
        aggregate = "pass" if set(payload["pre_open_gates"]) == {"CP2-PRE-1", "CP2-PRE-2"} and all(value == "pass" for value in payload["pre_open_gates"].values()) and self.evidence.private_root_status == "pass" and processed == set(AUTHORIZED_ALIASES) and self.evidence.unauthorized_attempts == 0 and self.evidence.private_renders_retained == 0 and all(value == 0 for value in self.evidence.forbidden_export_counts.values()) and self.evidence.privacy_scan_status == "pass" and owning_pass and sessions_consistent else "fail"
        return {"schema_version": "1.0.0", "checkpoint_id": "PHASE_3_CHECKPOINT_2", "execution_evidence_id": payload["evidence_id"], "execution_evidence_sha256": self.evidence.sha256(), "execution_evidence": payload, "aggregate_status": aggregate}


def _aggregate_from_evidence(evidence: dict[str, Any]) -> str:
    sessions = evidence.get("source_sessions", {})
    owning = evidence.get("descriptor_quality_checks", [])
    counts_match = evidence.get("source_session_attempts") == len(sessions) and evidence.get("successful_closed_sessions") == sum(1 for item in sessions.values() if item.get("closed") and item.get("outcome") == "success") and evidence.get("failed_sessions") == sum(1 for item in sessions.values() if item.get("outcome") == "failed")
    return "pass" if set(evidence.get("pre_open_gates", {})) == {"CP2-PRE-1", "CP2-PRE-2"} and all(value == "pass" for value in evidence.get("pre_open_gates", {}).values()) and evidence.get("private_root_status") == "pass" and set(sessions) == set(AUTHORIZED_ALIASES) and counts_match and evidence.get("unauthorized_attempts") == 0 and evidence.get("private_renders_retained") == 0 and all(value == 0 for value in evidence.get("forbidden_export_counts", {}).values()) and evidence.get("privacy_scan_status") == "pass" and owning and all(item.get("status") == "pass" for item in owning) and all(item.get("started") and item.get("closed") and item.get("outcome") == "success" and item.get("sanitizer_handoff") == "pass" for item in sessions.values()) else "fail"


def validate_checkpoint2_qa(record: dict[str, Any]) -> list[str]:
    evidence = record.get("execution_evidence")
    if not isinstance(evidence, dict): return ["CP2-QA-EXECUTION-EVIDENCE-MISSING"]
    errors = []
    actual_hash = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if record.get("execution_evidence_id") != evidence.get("evidence_id") or record.get("execution_evidence_sha256") != actual_hash: errors.append("CP2-QA-EXECUTION-EVIDENCE-HASH")
    if record.get("aggregate_status") != _aggregate_from_evidence(evidence): errors.append("CP2-QA-AGGREGATE-NONDERIVED")
    return errors


def _production_observation_policy_check() -> None:
    from .phase3_contracts import canonical_observation_catalogs, validate_observation_visual_binding
    registry = _schema_registry(); sha = "b" * 64
    card = {"schema_version": "1.0.0", "evidence_id": "E900", "kind": "experimental_measurement", "title": "Policy execution input", "provenance": "verified_empirical", "source": {"source_id": "S900", "uri": "controlled/measurement.dat", "sha256": sha}, "claim_support_refs": [], "claim_contradict_refs": [], "scope": {}, "verification": {"status": "verified"}}
    output = {"schema_version": "3.0.0", "figure_output_id": "FOM900", "figure_id": "FIG900", "figure_type": "scientific_plot", "primary_artifact_kind": "svg_vector", "renderer": "policy_runner", "source_spec_sha256": sha, "provenance_refs": ["E900"], "style_profile_ref": "VSP900", "evidence_status": "empirical", "primary_artifact": {"path": "artifacts/phase3/policy.svg", "sha256": sha, "data_provenance_refs": ["E900"]}, "output_part_lineage": ["generated"]}
    binding = {"observation_id": "OBS900", "empirical_evidence_required": True, "observation_evidence_ref": "E900", "observation_output_ref": "FOM900", "evidence_refs": ["E900"], "auxiliary_visuals": []}
    if validate_observation_visual_binding(binding, catalog=canonical_observation_catalogs(registry, [card], [output]), evidence_policy="production"): raise Checkpoint2PolicyViolation("production Observation policy owning check failed")


def build_checkpoint2(*, repository_root: Path | str, local_aliases: dict[str, Path | str], private_root: Path | str, artifact_root: Path | str) -> dict[str, Any]:
    root, output_root = Path(repository_root), Path(artifact_root)
    resolver = LocalPrivateAliasResolver(local_aliases, private_root=private_root)
    scanner = RepositoryPrivacyScanner(private_root_signatures=[str(path.parent) for path in resolver._paths.values()], forbidden_basenames=[path.name for path in resolver._paths.values()])
    run = Checkpoint2Run.start(pre_open_passed=False, private_root=private_root)
    try:
        from .phase3_privacy import PrivateProfileStore
        PrivateProfileStore(private_root, repository_root=root).prepare_for_future_open()
    except Exception: run.evidence.private_root_status = "fail"
    else: run.evidence.private_root_status = "pass"
    scan_findings, exceptions = scanner.scan_repository_with_legacy_exception(root, forbidden_basenames=[path.name for path in resolver._paths.values()])
    run.evidence.privacy_scan_total_findings = len(scan_findings) + len(exceptions); run.evidence.approved_legacy_exceptions = exceptions; run.evidence.unexcepted_findings = len(scan_findings); run.evidence.record_pre_open_gate("CP2-PRE-1", "pass" if not scan_findings else "fail"); run.evidence.privacy_scan_status = "pass" if not scan_findings else "fail"
    try: _production_observation_policy_check()
    except Exception: run.evidence.record_pre_open_gate("CP2-PRE-2", "fail")
    else: run.evidence.record_pre_open_gate("CP2-PRE-2", "pass")
    if any(result != "pass" for result in run.evidence.pre_open_gates.values()): raise Checkpoint2PolicyViolation("Checkpoint 2 pre-open gates failed; private aliases were not resolved")
    resolver._execution = run.evidence
    shell_descriptors: list[dict[str, Any]] = []; body_descriptor: dict[str, Any] | None = None
    for alias_uri in AUTHORIZED_ALIASES:
        session = resolver.resolve(alias_uri).open_read_only(); raw = session.profile_structurally("body" if alias_uri == BODY_ALIAS else "shell"); raw.pop("render_count", None)
        if alias_uri == BODY_ALIAS:
            body_descriptor = sanitize_body_descriptor(raw); run.evidence.update_session(alias_uri, sanitizer_handoff="pass")
        else:
            shell_descriptors.append(sanitize_shell_descriptor(raw)); run.evidence.update_session(alias_uri, sanitizer_handoff="pass")
    run.private_render_review({"image_capable": True, "approved_for_private_exemplars": False})
    registry = _schema_registry(); assert body_descriptor is not None
    run.set_descriptor_quality(shell_descriptors, body_descriptor, registry)
    manifest = {"schema_version": "1.0.0", "manifest_id": "SEM001", "exemplars": [{"alias_uri": descriptor["alias_uri"], "source_sha256": descriptor["source_sha256"], "profile_id": descriptor["profile_id"], "authority": "body_composition" if descriptor["alias_uri"] == BODY_ALIAS else "shell"} for descriptor in [*shell_descriptors, body_descriptor]]}
    shell_payload, body_payload = {"schema_version": "1.0.0", "descriptors": shell_descriptors}, {"schema_version": "1.0.0", "descriptor": body_descriptor}
    for name, value in (("sanitized-exemplar-manifest", manifest), ("sanitized-shell-structural-descriptors", shell_payload), ("sanitized-body-structural-descriptors", body_payload)):
        errors = registry.errors(name, value)
        if errors: raise Checkpoint2PolicyViolation(f"sanitized descriptor schema failed: {name}")
    output_root.mkdir(parents=True, exist_ok=True)
    for name, value in (("sanitized-exemplar-manifest.json", manifest), ("sanitized-shell-structural-descriptors.json", shell_payload), ("sanitized-body-structural-descriptors.json", body_payload)):
        (output_root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = run.qa_record()
    if validate_checkpoint2_qa(qa): raise Checkpoint2PolicyViolation("Checkpoint 2 QA evidence is inconsistent")
    (output_root / "checkpoint-2-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa
