"""Checkpoint 2: guarded, data-minimized private structural profiling."""

from __future__ import annotations

import hashlib
import json
import posixpath
from dataclasses import dataclass, field
from pathlib import Path
import re
import unicodedata
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
_SOURCE_SCOPES = {"slide_master", "slide_layout", "theme", "slide_body", "slide_content", "slide_recurrence_derived", "not_observable_structurally"}
_COLOR_TOKENS = {"accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "dk1", "dk2", "lt1", "lt2", "hlink", "folhlink"}
_SAFE_FONT_NAMES = {"Arial", "Calibri", "Times New Roman", "Aptos", "Noto Sans CJK", "Microsoft JhengHei", "Yu Gothic", "Meiryo", "Segoe UI", "Cambria", "Georgia", "微軟正黑體"}
_FONT_TOKEN_SCRIPTS = {"lt": "latin", "ea": "east_asian", "cs": "complex_script"}
_SCRIPT_ROLES = ("latin", "east_asian", "complex_script", "unspecified")
_SUPPLEMENTAL_THEME_SCRIPT_CODES = {
    "Arab", "Armn", "Beng", "Cans", "Cher", "Deva", "Ethi", "Geor",
    "Gujr", "Guru", "Hang", "Hans", "Hant", "Hebr", "Jpan", "Khmr",
    "Knda", "Laoo", "Mlym", "Mymr", "Orya", "Sinh", "Taml", "Telu",
    "Thai", "Tibt", "Yiii",
}


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


def _compose_transform(parent: dict[str, Any], child: dict[str, Any]) -> tuple[float, float, float, float]:
    """Map a child transform through a group transform into absolute EMUs.

    DrawingML groups define child coordinates in ``chOff/chExt`` rather than
    slide coordinates.  This small, side-effect-free helper is deliberately
    shared by group traversal and its round-trip geometry tests.
    """
    px, py = parent["off"]
    pw, ph = parent["ext"]
    cx, cy = parent["ch_off"]
    cw, ch = parent["ch_ext"]
    if cw <= 0 or ch <= 0:
        raise Checkpoint2PolicyViolation("invalid group child transform")
    sx, sy = pw / cw, ph / ch
    ox, oy, ow, oh = *child["off"], *child["ext"]
    if parent.get("flip_h"):
        ox = cx + cw - (ox - cx) - ow
    if parent.get("flip_v"):
        oy = cy + ch - (oy - cy) - oh
    return (px + (ox - cx) * sx, py + (oy - cy) * sy, ow * sx, oh * sy)


def _rotation_state(transform: dict[str, Any] | None) -> dict[str, Any]:
    """Return an explicit truth state for DrawingML rotation.

    Rotation is intentionally excluded from geometry composition in this
    checkpoint.  A rotated item therefore remains visible in the local raw
    profile but cannot be consumed as measured positional evidence.
    """
    raw = float((transform or {}).get("rot", 0) or 0)
    degrees = _round(raw / 600000.0)
    if abs(degrees) > 1e-9:
        return {"rotation_status": "unsupported", "rotation_deg": degrees, "geometry_eligible": False}
    return {"rotation_status": "none", "rotation_deg": 0.0, "geometry_eligible": True}


def _connector_semantics(x: float, y: float, w: float, h: float, *, flip_h: bool, flip_v: bool, head_arrow: str, tail_arrow: str) -> dict[str, Any]:
    """Return directed endpoints from DrawingML end markers and flips."""
    start, end = [x, y], [x + w, y + h]
    if flip_h:
        start[0], end[0] = end[0], start[0]
    if flip_v:
        start[1], end[1] = end[1], start[1]
    head = head_arrow if head_arrow != "none" else "none"
    tail = tail_arrow if tail_arrow != "none" else "none"
    if tail != "none" and head == "none":
        start, end = end, start
    directedness = "directed" if head != "none" or tail != "none" else "plain"
    return {"start": [_round(start[0]), _round(start[1])], "end": [_round(end[0]), _round(end[1])], "head_arrow": head, "tail_arrow": tail, "directedness": directedness}


def _metric_observation(value: float | int | str | None, *, basis: str, evidence_ids: list[str]) -> dict[str, Any]:
    if basis not in _BASIS:
        raise Checkpoint2PolicyViolation("invalid metric basis")
    if value is None or (basis == "derived" and not evidence_ids):
        return {"value": None, "basis": "not_observable_structurally", "evidence_state": "unavailable", "supporting_object_ids": []}
    return {"value": value, "basis": basis, "evidence_state": "derived" if basis == "derived" else "measured", "supporting_object_ids": list(evidence_ids)}


def _union_area(items: list[dict[str, Any]]) -> float:
    """Exact rectangle-union area in normalized slide coordinates."""
    edges = sorted({edge for item in items for edge in (item["geometry"]["x"], item["geometry"]["x"] + item["geometry"]["w"])})
    area = 0.0
    for left, right in zip(edges, edges[1:]):
        intervals = sorted((item["geometry"]["y"], item["geometry"]["y"] + item["geometry"]["h"]) for item in items if item["geometry"]["x"] < right and item["geometry"]["x"] + item["geometry"]["w"] > left)
        covered, end = 0.0, -1.0
        for top, bottom in intervals:
            if bottom > end:
                covered += max(0.0, bottom - max(top, end)); end = max(end, bottom)
        area += (right - left) * covered
    return _round(min(1.0, area))


def _classify_structural_family(*, objects: list[dict[str, Any]], connectors: list[dict[str, Any]], metrics: dict[str, Any], groups: list[dict[str, Any]]) -> dict[str, Any]:
    """Conservative family inference; counts alone are never a signature."""
    objects = [item for item in objects if item.get("geometry_eligible", True)]
    connectors = [item for item in connectors if item.get("geometry_eligible", True)]
    pictures = [item for item in objects if item.get("object_class") == "picture"]
    xs = sorted(item["geometry"]["x"] for item in pictures if "geometry" in item)
    ys = sorted(item["geometry"]["y"] for item in pictures if "geometry" in item)
    ids = [item.get("object_id", "") for item in pictures]
    matrix = len(pictures) >= 4 and len({round(y, 2) for y in ys}) >= 2 and len({round(x, 2) for x in xs}) >= 2
    comparison = len(pictures) == 2 and bool(groups) and abs(pictures[0]["geometry"]["w"] - pictures[1]["geometry"]["w"]) <= 0.03 and abs(pictures[0]["geometry"]["h"] - pictures[1]["geometry"]["h"]) <= 0.03 and abs(pictures[0]["geometry"]["x"] - pictures[1]["geometry"]["x"]) > 0.2
    spine = [item for item in connectors if item.get("orientation") == "horizontal"]
    branches = [item for item in connectors if item.get("orientation") in {"vertical", "diagonal"}]
    fishbone = bool(spine and len(branches) >= 2 and groups)
    if matrix:
        return {"family": "image_matrix", "confidence": "structurally_supported", "evidence_basis": ["matrix_grid", *ids]}
    if comparison:
        return {"family": "control_proposed_comparison", "confidence": "structurally_supported", "evidence_basis": ["comparison_pair", *ids]}
    if fishbone:
        return {"family": "fishbone_research_map", "confidence": "provisional", "evidence_basis": ["spine_branch_signature", *[item.get("object_id", "") for item in connectors]]}
    if pictures:
        return {"family": "result_single", "confidence": "provisional", "evidence_basis": ["picture_geometry", ids[0]]}
    return {"family": "other_insufficient_structural_evidence", "confidence": "insufficient_structural_evidence", "evidence_basis": ["insufficient"]}


def _body_binding_fingerprint(candidate: dict[str, Any], measurement: dict[str, Any]) -> str:
    """Hash the sanitized structural identity used to bind a candidate to a slide.

    The fingerprint intentionally excludes all private text/media and does not
    use array position or slide-local object IDs as a global identity.
    """
    geometry = lambda item: {key: item.get("geometry", {}).get(key) for key in ("x", "y", "w", "h")}
    structural = {
        "candidate_id": candidate["candidate_id"],
        "bound_slide_id": candidate["bound_slide_id"],
        "family": candidate["family"],
        "confidence": candidate["confidence"],
        "evidence_basis": sorted(candidate["evidence_basis"]),
        "measurement": {
            "slide_id": measurement["slide_id"],
            "objects": sorted(
                ({"object_id": item.get("object_id"), "object_class": item.get("object_class"), "primitive_type": item.get("primitive_type"), "geometry": geometry(item)} for item in measurement.get("objects", [])),
                key=lambda item: (str(item["object_id"]), str(item["object_class"])),
            ),
            "connectors": sorted(
                ({"object_id": item.get("object_id"), "orientation": item.get("orientation"), "start": item.get("start"), "end": item.get("end"), "head_arrow": item.get("head_arrow"), "tail_arrow": item.get("tail_arrow") } for item in measurement.get("connectors", [])),
                key=lambda item: str(item["object_id"]),
            ),
            "panels": sorted(({"panel_id": item.get("panel_id"), "geometry": geometry(item)} for item in measurement.get("panels", [])), key=lambda item: str(item["panel_id"])),
            "metrics": {key: {"value": value.get("value"), "basis": value.get("basis"), "evidence_state": value.get("evidence_state")} for key, value in sorted(measurement.get("metrics", {}).items())},
        },
    }
    return hashlib.sha256(json.dumps(structural, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _geometry(x: float, y: float, w: float, h: float, basis: str = "measured") -> dict[str, Any]:
    if not all(isinstance(v, (int, float)) for v in (x, y, w, h)) or w <= 0 or h <= 0:
        raise Checkpoint2PolicyViolation("invalid measured geometry")
    x_clipped, y_clipped = max(0.0, min(1.0, x)), max(0.0, min(1.0, y))
    return {"x": _round(x_clipped), "y": _round(y_clipped), "w": _round(max(1e-6, min(1.0 - x_clipped, w))), "h": _round(max(1e-6, min(1.0 - y_clipped, h))), "basis": basis}


def _style(fill_role: str = "none", stroke_role: str = "none", line_width_pt: float = 0.0, basis: str = "measured", *, fill_color: dict[str, Any] | None = None, stroke_color: dict[str, Any] | None = None, source_scope: str = "not_observable_structurally") -> dict[str, Any]:
    return {
        "role": "emphasis" if fill_role == "emphasis" or stroke_role == "emphasis" else "neutral",
        "fill_role": fill_role,
        "stroke_role": stroke_role,
        "line_width_pt": _round(max(0.0, min(20.0, line_width_pt))),
        "basis": basis,
        "source_scope": source_scope,
        "fill_color_evidence": fill_color or _unknown_color("fill", basis),
        "stroke_color_evidence": stroke_color or _unknown_color("stroke", basis),
    }


def _unknown_color(source_kind: str, basis: str = "not_observable_structurally", *, theme_profile_id: str | None = None) -> dict[str, Any]:
    return {
        "source_kind": "unknown" if source_kind != "none" else "none",
        "direct_rgb": None,
        "theme_token": None,
        "resolved_rgb": None,
        "tint": None,
        "shade": None,
        "lum_mod": None,
        "lum_off": None,
        "transform_status": "unresolved",
        "theme_profile_id": theme_profile_id,
        "source_scope": "not_observable_structurally",
        "basis": basis,
    }


def _color_evidence(element: ET.Element, fill: bool = True, theme_palette: dict[str, str] | None = None, *, source_scope: str = "slide_recurrence_derived", theme_profile_id: str | None = None) -> dict[str, Any]:
    """Extract reconstructable but privacy-safe DrawingML color evidence."""
    theme_palette = theme_palette or {}
    solid = element.find(".//a:solidFill", _NS) if fill else element.find(".//a:ln/a:solidFill", _NS)
    no_fill = element.find(".//a:noFill", _NS) if fill else element.find(".//a:ln/a:noFill", _NS)
    if solid is None:
        if no_fill is not None:
            evidence = _unknown_color("none", theme_profile_id=theme_profile_id)
            evidence.update({"source_kind": "none", "transform_status": "supported", "source_scope": source_scope, "basis": "measured"})
            return evidence
        return _unknown_color("unknown", theme_profile_id=theme_profile_id)
    direct = solid.find("a:srgbClr", _NS)
    scheme = solid.find("a:schemeClr", _NS)
    if direct is not None:
        source_kind = "direct_rgb"
        direct_rgb = (direct.get("val") or "").upper()
        token = None
        resolved = direct_rgb if re.fullmatch(r"[0-9A-F]{6}", direct_rgb) else None
        color_node = direct
    elif scheme is not None:
        token = (scheme.get("val") or "").lower()
        if token not in _COLOR_TOKENS:
            token = None
        source_kind = "theme_role" if token else "unknown"
        direct_rgb = None
        resolved = theme_palette.get(token) if token else None
        color_node = scheme
    else:
        return _unknown_color("unknown", theme_profile_id=theme_profile_id)
    transform_names = {"tint", "shade", "lumMod", "lumOff"}
    unsupported = [child.tag.rsplit("}", 1)[-1] for child in list(color_node) if child.tag.rsplit("}", 1)[-1] not in transform_names]
    values: dict[str, float | None] = {}
    for name in transform_names:
        node = color_node.find(f"a:{name}", _NS)
        values[name] = _round(float(node.get("val")) / 100000.0) if node is not None and node.get("val") is not None else None
    return {
        "source_kind": source_kind,
        "direct_rgb": direct_rgb,
        "theme_token": token,
        "resolved_rgb": resolved,
        "tint": values["tint"],
        "shade": values["shade"],
        "lum_mod": values["lumMod"],
        "lum_off": values["lumOff"],
        "transform_status": "unsupported" if unsupported else "supported",
        "theme_profile_id": theme_profile_id,
        "source_scope": source_scope,
        "basis": "measured",
    }


def _color_role(element: ET.Element, fill: bool = True) -> str:
    container = element.find(".//a:solidFill", _NS) if fill else element.find(".//a:ln/a:solidFill", _NS)
    no_style = element.find(".//a:noFill", _NS) if fill else element.find(".//a:ln/a:noFill", _NS)
    if container is None:
        return "none" if no_style is not None else "unknown"
    node = container.find("a:srgbClr", _NS)
    scheme = container.find("a:schemeClr", _NS)
    if scheme is not None:
        token = (scheme.get("val") or "unknown").lower()
        return f"theme:{token}" if token in {"accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "dk1", "dk2", "lt1", "lt2", "hlink", "folhlink"} else "unknown"
    if node is None:
        return "unknown"
    value = (node.get("val") or "").upper()
    if value in {"FF0000", "C00000", "E00000"}:
        return "emphasis"
    if value in {"FFFFFF", "F2F2F2", "E7E6E6"}:
        return "background"
    if value in {"000000", "404040", "595959"}:
        return "neutral"
    return "accent"


def _theme_font_token(typeface: str | None) -> tuple[str, str] | None:
    """Map DrawingML major/minor theme-font tokens to controlled evidence."""
    if not isinstance(typeface, str):
        return None
    match = re.fullmatch(r"\+(mj|mn)-(lt|ea|cs)", typeface.casefold())
    if not match:
        return None
    return ("major" if match.group(1) == "mj" else "minor", _FONT_TOKEN_SCRIPTS[match.group(2)])


def _safe_font_name(candidate: str) -> bool:
    """Allow compact typeface labels, including safe Unicode, but never paths/data."""
    if not candidate or len(candidate) > 64 or any(ord(char) < 32 for char in candidate):
        return False
    lowered = candidate.casefold()
    if any(token in lowered for token in ("private", "secret", "pptx", "http", "www.", "doi:", "\\", "/", ":", "<", ">")):
        return False
    # Typeface labels are letters/digits plus a deliberately small punctuation set.
    return all(char.isalnum() or char in " ._-()" or unicodedata.category(char).startswith("L") for char in candidate)


def _font_family(typeface: str | None) -> str:
    """Preserve exact safe typefaces; reject unsafe/private-looking names."""
    if not isinstance(typeface, str) or not typeface:
        return "unknown"
    candidate = typeface.strip()
    if candidate in _SAFE_FONT_NAMES or _safe_font_name(candidate):
        return candidate
    return "unknown"


def resolve_theme_color(token: str, *, master_id: str, master_theme: dict[str, str], theme_profiles: dict[str, dict[str, Any]]) -> str | None:
    """Resolve a token only through the observation's bound Master → Theme edge."""
    theme_id = master_theme.get(master_id)
    if token not in _COLOR_TOKENS or theme_id not in theme_profiles:
        return None
    palette = theme_profiles[theme_id].get("palette", {})
    value = palette.get(token)
    return value.upper() if isinstance(value, str) and re.fullmatch(r"[0-9A-Fa-f]{6}", value) else None


def resolve_descriptor_theme_color(token: str, *, profile_id: str, theme_profile_id: str, descriptor_theme_profiles: dict[str, dict[str, dict[str, Any]]]) -> str | None:
    """Resolve a theme token through a descriptor-qualified identity only.

    Theme IDs are intentionally local to a sanitized descriptor.  ``T001`` in
    two distinct exemplars must never be treated as one global palette.
    """
    profile = descriptor_theme_profiles.get(profile_id, {}).get(theme_profile_id)
    if token not in _COLOR_TOKENS or not isinstance(profile, dict):
        return None
    palette = profile.get("palette", {})
    value = palette.get(token) if isinstance(palette, dict) else None
    return value.upper() if isinstance(value, str) and re.fullmatch(r"[0-9A-Fa-f]{6}", value) else None


def resolve_active_descriptor_theme_color(token: str, *, profile_id: str, theme_profile_id: str, descriptor_theme_profiles: dict[str, dict[str, dict[str, Any]]]) -> str | None:
    """Resolve only a topology-reachable theme for future professor grammar.

    Theme IDs are local to a descriptor, and a package-resident orphan theme is
    audit/reference metadata rather than visual-authority evidence.
    """
    profile = descriptor_theme_profiles.get(profile_id, {}).get(theme_profile_id)
    if not isinstance(profile, dict) or profile.get("usage_state") != "referenced":
        return None
    return resolve_descriptor_theme_color(
        token,
        profile_id=profile_id,
        theme_profile_id=theme_profile_id,
        descriptor_theme_profiles=descriptor_theme_profiles,
    )


def typography_resolution_counts(observations: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Count every persisted script observation exactly once by evidence state."""
    scripts = _SCRIPT_ROLES
    states = ("explicit_font", "theme_font_resolved", "theme_font_unresolved", "inherited_unresolved", "unknown")
    counts = {script: {state: 0 for state in states} for script in scripts}
    for observation in observations:
        script, state = observation.get("script_role"), observation.get("font_evidence_state")
        if script not in counts or state not in counts[script]:
            raise Checkpoint2PolicyViolation("invalid persisted typography observation")
        counts[script][state] += 1
    return counts


def _font_roles(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations: dict[tuple[str, str, str, str, str, str, str, str], list[float]] = {}
    for slide in slides:
        for item in slide.get("font_observations", []):
            key = (item["role"], item["family"], item["weight"], item.get("style", "normal"), item.get("source_scope", "not_observable_structurally"), item.get("theme_font_role") or "none", item.get("script_role", "unspecified"), item.get("font_evidence_state", "unknown"))
            observations.setdefault(key, []).append(item["size_pt"])
    result = []
    for (role, family, weight, style, source_scope, theme_font_role, script_role, evidence_state), sizes in sorted(observations.items()):
        result.append({"role": role, "family": family, "theme_font_role": None if theme_font_role == "none" else theme_font_role, "script_role": script_role, "font_evidence_state": evidence_state, "size_pt": _round(median(sizes)), "weight": weight, "style": style, "basis": "measured", "source_scope": source_scope})
    return result


def _theme_profiles(package: zipfile.ZipFile, names: list[str]) -> dict[str, dict[str, Any]]:
    """Build local-only theme profiles without relying on package order at use time."""
    profiles: dict[str, dict[str, Any]] = {}
    for name in sorted((item for item in names if re.fullmatch(r"ppt/theme/theme\d+\.xml", item)), key=_part_number):
        try:
            root = ET.fromstring(package.read(name))
        except (KeyError, ET.ParseError):
            continue
        scheme = root.find(".//a:clrScheme", _NS)
        if scheme is None:
            continue
        palette: dict[str, str] = {}
        for child in list(scheme):
            token = child.tag.rsplit("}", 1)[-1].lower()
            if token not in _COLOR_TOKENS:
                continue
            value = child.find("a:srgbClr", _NS)
            if value is None:
                value = child.find("a:sysClr", _NS)
            rgb = (value.get("lastClr") if value is not None and value.tag.rsplit("}", 1)[-1] == "sysClr" else value.get("val") if value is not None else None)
            if rgb and re.fullmatch(r"[0-9A-Fa-f]{6}", rgb):
                palette[token] = rgb.upper()
        font_scheme: dict[str, dict[str, str]] = {}
        supplemental_fonts: list[dict[str, str]] = []
        for family_role, element_name in (("major", "majorFont"), ("minor", "minorFont")):
            font_element = root.find(f".//a:{element_name}", _NS)
            scripts: dict[str, str] = {}
            if font_element is not None:
                for script, node_name in (("latin", "latin"), ("east_asian", "ea"), ("complex_script", "cs")):
                    node = font_element.find(f"a:{node_name}", _NS)
                    family = _font_family(node.get("typeface") if node is not None else None)
                    if family != "unknown":
                        scripts[script] = family
                for node in font_element.findall("a:font", _NS):
                    code, family = node.get("script"), _font_family(node.get("typeface"))
                    if code in _SUPPLEMENTAL_THEME_SCRIPT_CODES and family != "unknown":
                        supplemental_fonts.append({"theme_font_role": family_role, "script_code": code, "family": family})
            font_scheme[family_role] = scripts
        profiles[name] = {
            "theme_profile_id": f"T{len(profiles)+1:03d}",
            "palette": palette,
            "font_scheme": font_scheme,
            "supplemental_fonts": sorted(supplemental_fonts, key=lambda item: (item["theme_font_role"], item["script_code"], item["family"])),
        }
    return profiles


def classify_theme_usage(
    theme_profiles: list[dict[str, Any]],
    *,
    master_theme_topology: list[dict[str, Any]],
    slide_theme_topology: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Construct per-theme reachability evidence from actual topology only."""
    by_id = {profile.get("theme_profile_id"): profile for profile in theme_profiles}
    if len(by_id) != len(theme_profiles) or any(not re.fullmatch(r"T[0-9]{3,}", str(key)) for key in by_id):
        raise Checkpoint2PolicyViolation("invalid descriptor-local theme identity")
    master_support: dict[str, set[str]] = {theme_id: set() for theme_id in by_id}
    slide_support: dict[str, set[str]] = {theme_id: set() for theme_id in by_id}
    for edge in master_theme_topology:
        if edge.get("basis") != "measured":
            continue
        target, source = edge.get("target_id"), edge.get("source_id")
        if target not in by_id or not isinstance(source, str) or not re.fullmatch(r"M[0-9]{3,}", source):
            raise Checkpoint2PolicyViolation("unknown Master theme topology target")
        master_support[target].add(source)
    for edge in slide_theme_topology:
        if edge.get("basis") != "measured":
            continue
        target, source = edge.get("target_id"), edge.get("source_id")
        if target not in by_id or not isinstance(source, str) or not re.fullmatch(r"(?:SL|D)[0-9]{3,}", source):
            raise Checkpoint2PolicyViolation("unknown slide theme topology target")
        slide_support[target].add(source)
    result = []
    for theme_id in sorted(by_id):
        profile = by_id[theme_id]
        referenced = bool(master_support[theme_id] or slide_support[theme_id])
        usage_state = "referenced" if referenced else "unreferenced"
        authority_state = "active_professor_style" if referenced else "reference_only"
        supplemental = []
        for item in profile.get("supplemental_fonts", []):
            if not isinstance(item, dict):
                raise Checkpoint2PolicyViolation("invalid supplemental theme font record")
            supplemental.append({
                "theme_font_role": item.get("theme_font_role"),
                "script_code": item.get("script_code"),
                "family": item.get("family"),
                "authority_state": authority_state,
            })
        result.append({
            "theme_profile_id": theme_id,
            "usage_state": usage_state,
            "authority_state": authority_state,
            "supporting_master_ids": sorted(master_support[theme_id]),
            "supporting_slide_ids": sorted(slide_support[theme_id]),
            "palette": profile.get("palette", []),
            "font_scheme": profile.get("font_scheme", {}),
            "supplemental_fonts": supplemental,
        })
    return result


def _theme_descriptor_profiles(
    profiles_by_part: dict[str, dict[str, Any]],
    *,
    master_theme_topology: list[dict[str, Any]],
    slide_theme_topology: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert local OOXML theme profiles into typed, reachability-aware input."""
    themes = [
        {
            "theme_profile_id": profile["theme_profile_id"],
            "palette": [
                {"theme_token": key, "resolved_rgb": value, "basis": "measured", "source_scope": "theme"}
                for key, value in sorted(profile["palette"].items())
            ],
            "font_scheme": profile["font_scheme"],
            "supplemental_fonts": profile["supplemental_fonts"],
        }
        for profile in profiles_by_part.values()
    ]
    return classify_theme_usage(
        themes,
        master_theme_topology=master_theme_topology,
        slide_theme_topology=slide_theme_topology,
    )


def _theme_palette(package: zipfile.ZipFile, names: list[str]) -> dict[str, str]:
    """Legacy synthetic helper only; production paths bind individual themes."""
    profiles = _theme_profiles(package, names)
    return next((profile["palette"] for profile in profiles.values()), {})


def _relative_part(base: str, target: str) -> str:
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def _master_theme_topology(package: zipfile.ZipFile, masters: list[str], profiles: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    topology: list[dict[str, Any]] = []
    for master in masters:
        rels = master.replace("ppt/slideMasters/", "ppt/slideMasters/_rels/") + ".rels"
        targets = _relationship_targets(package, rels)
        target = next((value for value in targets.values() if "theme" in value), "")
        theme_part = _relative_part(master, target) if target else ""
        profile = profiles.get(theme_part)
        topology.append({"source_id": f"M{_part_number(master):03d}", "target_id": profile["theme_profile_id"] if profile else "T000", "basis": "measured" if profile else "not_observable_structurally", "source_scope": "slide_master"})
    return topology


def _theme_style_roles(package: zipfile.ZipFile, names: list[str], theme_palette: dict[str, str]) -> list[dict[str, Any]]:
    """Expose only controlled theme role tokens; raw theme XML stays local."""
    roles: list[dict[str, Any]] = []
    allowed = _COLOR_TOKENS
    for name in sorted((item for item in names if re.fullmatch(r"ppt/theme/theme\d+\.xml", item)), key=_part_number):
        try:
            root = ET.fromstring(package.read(name))
        except (KeyError, ET.ParseError):
            continue
        scheme = root.find(".//a:clrScheme", _NS)
        if scheme is None:
            continue
        for child in list(scheme):
            token = child.tag.rsplit("}", 1)[-1]
            if token not in allowed:
                continue
            role = f"theme:{token.lower()}"
            color = {"source_kind": "theme_role", "direct_rgb": None, "theme_token": token.lower(), "resolved_rgb": theme_palette.get(token.lower()), "tint": None, "shade": None, "lum_mod": None, "lum_off": None, "transform_status": "supported" if token.lower() in theme_palette else "unresolved", "source_scope": "theme", "basis": "measured"}
            roles.append({"role": "neutral" if token.lower() in {"dk1", "lt1", "dk2", "lt2"} else "accent", "fill_role": role, "stroke_role": role, "line_width_pt": 0.0, "basis": "measured", "source_scope": "theme", "fill_color_evidence": color, "stroke_color_evidence": color})
    return roles


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
    typography_resolution_counts: dict[str, dict[str, int]] = field(default_factory=dict)
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
        return {"schema_version": "1.0.0", "evidence_id": "CP2-EXEC-001", "pre_open_gates": dict(sorted(self.pre_open_gates.items())), "alias_attempts": list(self.alias_attempts), "alias_results": dict(sorted(self.alias_results.items())), "source_sessions": dict(sorted(self.source_sessions.items())), "source_session_attempts": self.source_session_attempts, "successful_closed_sessions": self.authorized_source_sessions, "failed_sessions": self.failed_source_sessions, "unauthorized_attempts": self.unauthorized_attempts, "private_renders_created": self.private_renders_created, "private_renders_deleted": self.private_renders_deleted, "private_renders_retained": self.private_renders_retained, "private_qualitative_review_status": self.private_qualitative_review_status, "forbidden_export_counts": dict(self.forbidden_export_counts), "privacy_scan_status": self.privacy_scan_status, "private_root_status": self.private_root_status, "privacy_scan_total_findings": self.privacy_scan_total_findings, "approved_legacy_exceptions": list(self.approved_legacy_exceptions), "unexcepted_findings": self.unexcepted_findings, "typography_resolution_counts": self.typography_resolution_counts, "descriptor_quality_checks": list(self.descriptor_quality_checks)}

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
                masters = sorted((name for name in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name)), key=_part_number)
                layouts = sorted((name for name in names if re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", name)), key=_part_number)
                theme_profiles_by_part = _theme_profiles(package, names)
                master_theme_topology = _master_theme_topology(package, masters, theme_profiles_by_part)
                topology = self._topology(package, layouts, slides)
                layout_master = {edge["source_id"]: edge["target_id"] for edge in topology["layout_master"]}
                slide_layout = {edge["source_id"]: edge["target_id"] for edge in topology["slide_layout"]}
                master_theme = {edge["source_id"]: edge["target_id"] for edge in master_theme_topology}
                theme_profiles_by_id = {profile["theme_profile_id"]: profile for profile in theme_profiles_by_part.values()}
                slide_profiles = [self._slide_profile(ET.fromstring(package.read(name)), width, height, index + 1, source_scope="slide_body", theme_palette=theme_profiles_by_id.get(master_theme.get(layout_master.get(slide_layout.get(f"D{index + 1:03d}", ""), ""), ""), {}).get("palette", {}), theme_profile_id=master_theme.get(layout_master.get(slide_layout.get(f"D{index + 1:03d}", ""), "")), theme_font_scheme=theme_profiles_by_id.get(master_theme.get(layout_master.get(slide_layout.get(f"D{index + 1:03d}", ""), ""), ""), {}).get("font_scheme", {})) for index, name in enumerate(slides)]
                slide_theme_topology = [{"source_id": f"SL{index + 1:03d}", "target_id": master_theme.get(layout_master.get(slide_layout.get(f"D{index + 1:03d}", ""), ""), "T000"), "basis": "measured" if master_theme.get(layout_master.get(slide_layout.get(f"D{index + 1:03d}", ""), "")) else "not_observable_structurally", "source_scope": "slide_body"} for index in range(len(slides))]
                master_xml = [package.read(name) for name in masters]
                layout_xml = [package.read(name) for name in layouts]
            slide_size = {"width": _round(width / 914400), "height": _round(height / 914400), "basis": "measured"}
            base: dict[str, Any] = {"alias_uri": self.alias_uri, "source_sha256": source_sha, "profile_id": _safe_id(self.alias_uri), "slide_size": slide_size, "slide_count": len(slides), "render_count": 0}
            if authority == "shell":
                master_profiles = [self._slide_profile(ET.fromstring(value), width, height, index + 1, source_scope="slide_master", theme_palette=theme_profiles_by_id.get(master_theme.get(f"M{index + 1:03d}"), {}).get("palette", {}), theme_profile_id=master_theme.get(f"M{index + 1:03d}"), theme_font_scheme=theme_profiles_by_id.get(master_theme.get(f"M{index + 1:03d}"), {}).get("font_scheme", {})) for index, value in enumerate(master_xml)]
                layout_profiles = [self._slide_profile(ET.fromstring(value), width, height, index + 1, source_scope="slide_layout", theme_palette=theme_profiles_by_id.get(master_theme.get(layout_master.get(f"L{index + 1:03d}", ""), ""), {}).get("palette", {}), theme_profile_id=master_theme.get(layout_master.get(f"L{index + 1:03d}", "")), theme_font_scheme=theme_profiles_by_id.get(master_theme.get(layout_master.get(f"L{index + 1:03d}", ""), ""), {}).get("font_scheme", {})) for index, value in enumerate(layout_xml)]
                shell_profiles = [*master_profiles, *layout_profiles]
                typography = _font_roles(shell_profiles)
                profile = {**base, "master_count": len(masters), "layout_count": len(layouts), "measurement_basis": {"slide_size": "measured", "topology": "measured", "regions": "measured" if shell_profiles else "not_observable_structurally", "typography": "measured" if typography else "not_observable_structurally", "styles": "measured" if shell_profiles else "not_observable_structurally", "primitives": "measured" if shell_profiles else "not_observable_structurally", "placeholders": "measured" if any(profile.get("placeholders") for profile in shell_profiles) else "not_observable_structurally"}, "layout_master_topology": topology["layout_master"], "slide_layout_topology": topology["slide_layout"], "master_theme_topology": master_theme_topology, "shell_regions": self._shell_regions(shell_profiles, width, height), "safe_content_bounds": self._safe_bounds(shell_profiles), "typography_roles": typography, "style_roles": self._style_roles(shell_profiles), "shell_primitives": self._shell_primitives(shell_profiles), "placeholder_measurements": [placeholder for profile in shell_profiles for placeholder in profile.get("placeholders", [])], "theme_profiles": _theme_descriptor_profiles(theme_profiles_by_part, master_theme_topology=master_theme_topology, slide_theme_topology=[])}
            else:
                # Font observations are local-only profiler input and never cross
                # the sanitizer boundary in the body descriptor.
                body_measurements = []
                for slide in slide_profiles:
                    measurement = {key: value for key, value in slide.items() if key not in {"font_observations", "placeholders", "source_container_id", "source_scope"}}
                    measurement["objects"] = [{key: value for key, value in obj.items() if key not in {"source_container_id", "placeholder_type"}} for obj in measurement.get("objects", [])]
                    measurement["typography_observations"] = list(slide.get("typography_observations", []))
                    body_measurements.append(measurement)
                candidates = []
                for index, (slide, measurement) in enumerate(zip(slide_profiles, body_measurements), start=1):
                    candidate = self._classify_slide(slide)
                    candidate["candidate_id"] = f"BC{index:03d}"
                    candidate["bound_slide_id"] = measurement["slide_id"]
                    candidate["binding_fingerprint"] = _body_binding_fingerprint(candidate, measurement)
                    candidates.append(candidate)
                profile = {**base, "candidate_families": candidates, "body_measurements": body_measurements, "theme_profiles": _theme_descriptor_profiles(theme_profiles_by_part, master_theme_topology=[], slide_theme_topology=slide_theme_topology), "slide_theme_topology": slide_theme_topology}
            self._private_root.mkdir(parents=True, exist_ok=True)
            (self._private_root / f"{_safe_id(self.alias_uri).lower()}-raw.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
            if self._execution:
                descriptor_count = len(profile.get("shell_primitives", [])) if authority == "shell" else len(profile.get("body_measurements", []))
                self._execution.update_session(self.alias_uri, profiling_status="pass", descriptor_count=descriptor_count, sanitizer_handoff="pending")
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
            layout_master.append({"source_id": f"L{_part_number(layout):03d}", "target_id": f"M{_part_number(target):03d}" if target else "M000", "basis": "measured" if target else "not_observable_structurally", "source_scope": "slide_layout"})
        slide_layout: list[dict[str, Any]] = []
        for slide in slides:
            rels = slide.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
            target = next((value for value in _relationship_targets(package, rels).values() if "slideLayout" in value), "")
            slide_layout.append({"source_id": f"D{_part_number(slide):03d}", "target_id": f"L{_part_number(target):03d}" if target else "L000", "basis": "measured" if target else "not_observable_structurally", "source_scope": "slide_recurrence_derived"})
        return {"layout_master": layout_master, "slide_layout": slide_layout}

    @staticmethod
    def _slide_profile(slide: ET.Element, width: int, height: int, ordinal: int, source_scope: str = "slide_recurrence_derived", theme_palette: dict[str, str] | None = None, theme_profile_id: str | None = None, theme_font_scheme: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
        shapes: list[dict[str, Any]] = []
        connectors: list[dict[str, Any]] = []
        groups: list[dict[str, Any]] = []
        fonts: list[dict[str, Any]] = []
        placeholders: list[dict[str, Any]] = []
        counter = 0

        def transform_of(element: ET.Element) -> dict[str, Any] | None:
            xfrm = element.find(".//a:xfrm", _NS)
            if xfrm is None:
                return None
            off, ext = xfrm.find("a:off", _NS), xfrm.find("a:ext", _NS)
            if off is None or ext is None:
                return None
            ch_off, ch_ext = xfrm.find("a:chOff", _NS), xfrm.find("a:chExt", _NS)
            return {"off": [float(off.get("x", 0)), float(off.get("y", 0))], "ext": [float(ext.get("cx", 0)), float(ext.get("cy", 0))], "ch_off": [float(ch_off.get("x", 0)) if ch_off is not None else 0.0, float(ch_off.get("y", 0)) if ch_off is not None else 0.0], "ch_ext": [float(ch_ext.get("cx", 0)) if ch_ext is not None else float(ext.get("cx", 0)), float(ch_ext.get("cy", 0)) if ch_ext is not None else float(ext.get("cy", 0))], "flip_h": xfrm.get("flipH") in {"1", "true"}, "flip_v": xfrm.get("flipV") in {"1", "true"}, "rot": float(xfrm.get("rot", 0) or 0)}

        def walk(element: ET.Element, group_id: str | None = None, parent_transform: dict[str, Any] | None = None) -> None:
            nonlocal counter
            tag = element.tag.rsplit("}", 1)[-1]
            if tag == "grpSp":
                counter += 1; gid = f"G{counter:03d}"; children = list(element)
                member_count = sum(1 for child in children if child.tag.rsplit("}", 1)[-1] not in {"nvGrpSpPr", "grpSpPr"})
                group_transform = transform_of(element)
                composed = _compose_transform(parent_transform, group_transform) if parent_transform is not None and group_transform else None
                absolute_group = group_transform if parent_transform is None else ({"off": list(composed[0:2]), "ext": list(composed[2:4]), "ch_off": [0.0, 0.0], "ch_ext": list(composed[2:4]), "flip_h": False, "flip_v": False, "rot": group_transform.get("rot", 0) + parent_transform.get("rot", 0)} if group_transform and composed else None)
                rotation = _rotation_state(group_transform)
                if parent_transform and parent_transform.get("rot", 0):
                    rotation = {"rotation_status": "unsupported", "rotation_deg": _round((group_transform.get("rot", 0) + parent_transform.get("rot", 0)) / 600000.0), "geometry_eligible": False}
                groups.append({"group_id": gid, "member_count": max(1, member_count), "basis": "measured" if rotation["geometry_eligible"] else "not_observable_structurally", "source_scope": source_scope, **rotation})
                for child in children: walk(child, gid, absolute_group)
                return
            if tag not in {"sp", "pic", "graphicFrame", "cxnSp"}:
                for child in list(element):
                    walk(child, group_id, parent_transform)
                return
            raw_transform = transform_of(element)
            if raw_transform is None or not width or not height: return
            rotation = _rotation_state(raw_transform)
            if parent_transform and parent_transform.get("rot", 0):
                rotation = {"rotation_status": "unsupported", "rotation_deg": _round((raw_transform.get("rot", 0) + parent_transform.get("rot", 0)) / 600000.0), "geometry_eligible": False}
            if parent_transform is not None:
                abs_x, abs_y, abs_w, abs_h = _compose_transform(parent_transform, raw_transform)
            else:
                abs_x, abs_y = raw_transform["off"]
                abs_w, abs_h = raw_transform["ext"]
            x, y, w, h = abs_x / width, abs_y / height, abs_w / width, abs_h / height
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
            geom = _geometry(x, y, w, h, "measured" if rotation["geometry_eligible"] else "not_observable_structurally")
            placeholder = element.find(".//p:ph", _NS)
            placeholder_type_value: str | None = None
            if placeholder is not None:
                placeholder_type = (placeholder.get("type") or "obj").lower()
                allowed_placeholder_types = {"title", "ctrtitle", "subTitle", "body", "obj", "dt", "ftr", "sldNum", "hdr"}
                normalized_type = "subtitle" if placeholder_type == "subtitle" else placeholder_type
                if normalized_type not in {"title", "ctrtitle", "subtitle", "body", "obj", "dt", "ftr", "sldnum", "hdr"}:
                    normalized_type = "unknown"
                placeholder_type_value = normalized_type
                placeholders.append({"placeholder_id": f"PH{len(placeholders)+1:03d}", "placeholder_type": normalized_type, "geometry": geom, "basis": "measured" if rotation["geometry_eligible"] else "not_observable_structurally", "source_scope": source_scope, "source_container_id": f"{source_scope[6:7].upper()}{ordinal:03d}" if source_scope in {"slide_master", "slide_layout"} else None})
            style = _style(_color_role(element, True), _color_role(element, False), float(element.find(".//a:ln", _NS).get("w", 0) or 0) / 12700 if element.find(".//a:ln", _NS) is not None else 0.0, "measured" if rotation["geometry_eligible"] else "not_observable_structurally", fill_color=_color_evidence(element, True, theme_palette, source_scope=source_scope, theme_profile_id=theme_profile_id), stroke_color=_color_evidence(element, False, theme_palette, source_scope=source_scope, theme_profile_id=theme_profile_id), source_scope=source_scope)
            shapes.append({"object_id": oid, "object_class": object_class, "primitive_type": primitive, "geometry": geom, "group_id": group_id, "style": style, "basis": "measured" if rotation["geometry_eligible"] else "not_observable_structurally", "source_scope": source_scope, "source_container_id": f"{source_scope[6:7].upper()}{ordinal:03d}" if source_scope in {"slide_master", "slide_layout"} else None, "placeholder_type": placeholder_type_value, **rotation})
            if object_class == "connector":
                orientation = "horizontal" if abs(w) >= abs(h) * 2 else "vertical" if abs(h) >= abs(w) * 2 else "diagonal"
                head = element.find(".//a:headEnd", _NS); tail = element.find(".//a:tailEnd", _NS)
                semantics = _connector_semantics(x, y, w, h, flip_h=raw_transform["flip_h"], flip_v=raw_transform["flip_v"], head_arrow=(head.get("type", "triangle") if head is not None else "none"), tail_arrow=(tail.get("type", "triangle") if tail is not None else "none"))
                connectors.append({"object_id": oid, "orientation": orientation, **semantics, "flip_h": raw_transform["flip_h"], "flip_v": raw_transform["flip_v"], "basis": "measured" if rotation["geometry_eligible"] else "not_observable_structurally", "source_scope": source_scope, **rotation})
            if object_class == "text":
                for run in element.findall(".//a:r", _NS):
                    props = run.find("a:rPr", _NS)
                    if props is None:
                        props = run.find("a:defRPr", _NS)
                    if props is None: continue
                    size = float(props.get("sz", 0) or 0) / 100
                    if size <= 0: continue
                    role = "title" if y < 0.20 else "unknown" if y > 0.88 else "body"
                    role_confidence = "structurally_supported" if y < 0.20 else "unknown" if y > 0.88 else "provisional"
                    font_nodes = (("latin", "latin"), ("east_asian", "ea"), ("complex_script", "cs"))
                    present_nodes = [(script, props.find(f"a:{node_name}", _NS)) for script, node_name in font_nodes]
                    present_nodes = [(script, node) for script, node in present_nodes if node is not None and node.get("typeface")]
                    # A run can carry independent Latin, East-Asian, and complex
                    # script evidence.  Preserve each direct child exactly once;
                    # never let the first script node suppress the others.
                    # No direct script node is not evidence for Latin.  Preserve
                    # the unresolved inheritance truth with an explicit, finite
                    # script state rather than fabricating a resolver input.
                    candidates = present_nodes or [("unspecified", None)]
                    for script_role, node in candidates:
                        typeface = node.get("typeface") if node is not None else None
                        theme = _theme_font_token(typeface)
                        resolved_theme_family = (theme_font_scheme or {}).get(theme[0], {}).get(theme[1]) if theme else None
                        family = _font_family(typeface) if theme is None else _font_family(resolved_theme_family)
                        evidence_state = "theme_font_resolved" if theme and family != "unknown" else "theme_font_unresolved" if theme else "explicit_font" if family != "unknown" else "inherited_unresolved"
                        fonts.append({"observation_id": f"T{ordinal:03d}{len(fonts)+1:03d}", "role": role, "role_confidence": role_confidence, "family": family, "theme_font_role": theme[0] if theme else None, "script_role": theme[1] if theme else script_role, "font_evidence_state": evidence_state, "size_pt": size, "weight": "bold" if props.get("b") in {"1", "true"} else "regular", "style": "italic" if props.get("i") in {"1", "true"} else "normal", "source_scope": source_scope, "basis": "measured", "supporting_object_id": oid})
        for child in list(slide): walk(child)
        eligible_shapes = [item for item in shapes if item.get("geometry_eligible", True)]
        text_shapes = [item for item in eligible_shapes if item["object_class"] == "text"]
        text_area = _union_area(text_shapes)
        figure_shapes = [item for item in eligible_shapes if item["object_class"] in {"picture", "table", "chart", "native_shape"}]
        figure_area = _union_area(figure_shapes)
        total_area = _union_area(eligible_shapes)
        pictures = [item for item in eligible_shapes if item["object_class"] == "picture"]
        same_size_pairs = [(a, b) for index, a in enumerate(pictures) for b in pictures[index + 1:] if abs(a["geometry"]["w"] - b["geometry"]["w"]) <= 0.03 and abs(a["geometry"]["h"] - b["geometry"]["h"]) <= 0.03]
        aligned_rows = sorted({round(item["geometry"]["y"], 2) for item in pictures})
        aligned_cols = sorted({round(item["geometry"]["x"], 2) for item in pictures})
        grid_signature = len(pictures) >= 4 and len(aligned_rows) >= 2 and len(aligned_cols) >= 2 and len(aligned_rows) * len(aligned_cols) == len(pictures)
        panels = [{"panel_id": f"P{index:03d}", "geometry": item["geometry"], "basis": "derived"} for index, item in enumerate(pictures, 1) if grid_signature or same_size_pairs]
        matrix_rows = len(aligned_rows) if grid_signature else None
        matrix_columns = len(aligned_cols) if grid_signature else None
        caption_ids = [text["object_id"] for text in text_shapes if any(text["geometry"]["y"] >= fig["geometry"]["y"] + fig["geometry"]["h"] and text["geometry"]["y"] - (fig["geometry"]["y"] + fig["geometry"]["h"]) <= 0.06 for fig in figure_shapes)]
        vector_regions = [item for item in eligible_shapes if item["object_class"] in {"native_shape", "table", "chart"}]
        relation = "adjacent" if pictures and vector_regions else "separate" if pictures and not vector_regions else None
        metric_ids = [item["object_id"] for item in figure_shapes]
        metrics = {"text_area_ratio": _metric_observation(text_area, basis="derived", evidence_ids=[item["object_id"] for item in text_shapes]), "figure_area_ratio": _metric_observation(figure_area, basis="derived", evidence_ids=metric_ids), "dominant_figure_ratio": _metric_observation(_round(max((item["geometry"]["w"] * item["geometry"]["h"] for item in figure_shapes), default=0.0) / figure_area) if figure_area else None, basis="derived" if figure_area else "not_observable_structurally", evidence_ids=metric_ids), "figure_text_ratio": _metric_observation(_round(figure_area / text_area) if text_area else None, basis="derived" if text_area else "not_observable_structurally", evidence_ids=metric_ids if text_area else []), "annotation_density": _metric_observation(_round((len(connectors) + len(text_shapes)) / max(1, len(figure_shapes))), basis="derived", evidence_ids=[item["object_id"] for item in connectors] + [item["object_id"] for item in text_shapes]), "whitespace_fraction": _metric_observation(_round(max(0.0, 1.0 - total_area)), basis="derived", evidence_ids=[item["object_id"] for item in eligible_shapes]), "comparison_symmetry": _metric_observation(_round(1.0 - abs(same_size_pairs[0][0]["geometry"]["w"] - same_size_pairs[0][1]["geometry"]["w"])) if same_size_pairs else None, basis="derived" if same_size_pairs else "not_observable_structurally", evidence_ids=[item["object_id"] for pair in same_size_pairs[:1] for item in pair]), "matrix_rows": _metric_observation(matrix_rows, basis="derived" if matrix_rows else "not_observable_structurally", evidence_ids=[item["object_id"] for item in pictures] if matrix_rows else []), "matrix_columns": _metric_observation(matrix_columns, basis="derived" if matrix_columns else "not_observable_structurally", evidence_ids=[item["object_id"] for item in pictures] if matrix_columns else []), "panel_count": _metric_observation(len(panels) if panels else None, basis="derived" if panels else "not_observable_structurally", evidence_ids=[item["panel_id"] for item in panels]), "caption_candidate_count": _metric_observation(len(caption_ids) if caption_ids else None, basis="derived" if caption_ids else "not_observable_structurally", evidence_ids=caption_ids), "callout_candidate_count": _metric_observation(sum(1 for item in eligible_shapes if item["style"]["stroke_role"] == "emphasis") or None, basis="derived" if any(item["style"]["stroke_role"] == "emphasis" for item in eligible_shapes) else "not_observable_structurally", evidence_ids=[item["object_id"] for item in eligible_shapes if item["style"]["stroke_role"] == "emphasis"]), "photo_schematic_relation": _metric_observation(relation, basis="derived" if relation else "not_observable_structurally", evidence_ids=metric_ids if relation else [])}
        source_container_id = f"{source_scope[6:7].upper()}{ordinal:03d}" if source_scope in {"slide_master", "slide_layout"} else None
        return {"slide_id": f"SL{ordinal:03d}", "source_scope": source_scope, "source_container_id": source_container_id, "measurement_basis": "measured", "objects": shapes, "connectors": connectors, "groups": groups, "panels": panels, "metrics": metrics, "style_roles": [item["style"] for item in shapes], "font_observations": fonts, "typography_observations": fonts, "placeholders": placeholders}

    @staticmethod
    def _safe_bounds(slides: list[dict[str, Any]]) -> dict[str, Any]:
        # Master/layout geometry identifies exclusions, not a guaranteed content
        # rectangle.  Do not promote a full-slide fallback to measured evidence.
        content = [item["geometry"] for slide in slides for item in slide.get("objects", []) if item.get("placeholder_type") in {"body", "obj"} and item.get("geometry_eligible", True)]
        if not content:
            return {"value": None, "basis": "not_observable_structurally", "source_scope": "not_observable_structurally", "evidence_ids": []}
        left = max(item["x"] for item in content)
        top = max(item["y"] for item in content)
        right = min(item["x"] + item["w"] for item in content)
        bottom = min(item["y"] + item["h"] for item in content)
        if right <= left or bottom <= top:
            return {"value": None, "basis": "not_observable_structurally", "source_scope": "not_observable_structurally", "evidence_ids": []}
        scopes = {item.get("source_scope") for slide in slides for item in slide.get("objects", []) if item.get("placeholder_type") in {"body", "obj"} and item.get("source_scope") in {"slide_master", "slide_layout"}}
        source_scope = next(iter(scopes)) if len(scopes) == 1 else "not_observable_structurally"
        if source_scope == "not_observable_structurally":
            return {"value": None, "basis": "not_observable_structurally", "source_scope": source_scope, "evidence_ids": []}
        return {"value": _geometry(left, top, right - left, bottom - top, "derived"), "basis": "derived", "source_scope": source_scope, "evidence_ids": ["content_placeholders"]}

    @staticmethod
    def _shell_regions(slides: list[dict[str, Any]], width: int, height: int) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        placeholder_roles = {"title": "title", "ctrtitle": "title", "subtitle": "subtitle", "ftr": "footer", "sldnum": "page_number", "hdr": "header", "dt": "date_time"}
        by_role: dict[str, list[dict[str, Any]]] = {}
        for slide in slides:
            for item in slide.get("objects", []):
                role = placeholder_roles.get(item.get("placeholder_type", ""))
                if role:
                    by_role.setdefault(role, []).append(item)
        if not by_role:
            # Geometry-only fallback is mutually exclusive and explicitly marked.
            for slide in slides:
                for item in slide.get("objects", []):
                    g = item["geometry"]
                    role = "title" if g["y"] < 0.25 and g["h"] < 0.2 else "footer" if g["y"] + g["h"] > 0.85 else None
                    if role:
                        by_role.setdefault(role, []).append(item)
        for role, items in sorted(by_role.items()):
            evidence = "placeholder_semantic" if any(item.get("placeholder_type") for item in items) else "geometry_fallback"
            support_by_scope = []
            for scope in sorted({item.get("source_scope") for item in items if item.get("source_scope") in {"slide_master", "slide_layout"}}):
                scoped_items = [item for item in items if item.get("source_scope") == scope]
                containers = {item.get("source_container_id") for item in scoped_items if item.get("source_container_id")}
                eligible = {slide.get("source_container_id") for slide in slides if slide.get("source_scope") == scope and slide.get("source_container_id")}
                support_by_scope.append({"source_scope": scope, "occurrence_count": len(scoped_items), "source_container_count": len(containers), "eligible_container_count": len(eligible), "coverage_ratio": _round(len(containers) / len(eligible)) if eligible else 0.0, "supporting_source_ids": sorted(containers)})
            result.append({"region_id": f"R{len(result)+1:03d}", "role": role, "geometry": _geometry(median([item["geometry"]["x"] for item in items]), median([item["geometry"]["y"] for item in items]), median([item["geometry"]["w"] for item in items]), median([item["geometry"]["h"] for item in items]), "measured"), "basis": "measured", "support_by_scope": support_by_scope, "role_evidence": evidence})
        return result

    @staticmethod
    def _style_roles(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
        roles = {(json.dumps(item["style"], sort_keys=True), item.get("source_scope", "not_observable_structurally")) for slide in slides for item in slide.get("objects", [])}
        result = []
        for encoded, source_scope in sorted(roles):
            style = json.loads(encoded)
            result.append({"role": "emphasis" if style["fill_role"] == "emphasis" or style["stroke_role"] == "emphasis" else "neutral", **style, "source_scope": source_scope})
        return result

    @staticmethod
    def _shell_primitives(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, float, float, float, float, str], dict[str, Any]] = {}
        for slide in slides:
            for item in slide.get("objects", []):
                if item["object_class"] in {"picture", "connector"}:
                    continue
                if not item.get("geometry_eligible", True):
                    continue
                g = item["geometry"]; key = (item["object_class"], round(g["x"], 3), round(g["y"], 3), round(g["w"], 3), round(g["h"], 3), item.get("source_scope", "not_observable_structurally")); grouped.setdefault(key, {"occurrences": 0, "containers": set()}); grouped[key]["occurrences"] += 1; grouped[key]["containers"].add(item.get("source_container_id"))
        result = []
        for idx, ((kind, x, y, w, h, source_scope), info) in enumerate(sorted(grouped.items()), 1):
            count, containers = info["occurrences"], {item for item in info["containers"] if item}
            primitive_class = {"text": "text_region", "line": "connector"}.get(kind, kind if kind in {"picture", "table_or_chart", "native_shape", "connector", "group"} else "unknown")
            if count < 1:
                continue
            result.append({"primitive_id": f"S{idx:03d}", "primitive_class": primitive_class, "geometry": _geometry(x, y, w, h, "measured"), "occurrence_count": count, "source_container_count": len(containers), "eligible_container_count": len({slide.get("source_container_id") for slide in slides if slide.get("source_container_id")}), "coverage_ratio": _round(len(containers) / max(1, len({slide.get("source_container_id") for slide in slides if slide.get("source_container_id")}))), "supporting_source_ids": sorted(containers), "basis": "measured", "source_scope": source_scope, "role_evidence": "source_container_recurrence"})
        return result

    @staticmethod
    def _classify_slide(slide: dict[str, Any]) -> dict[str, Any]:
        return _classify_structural_family(objects=slide["objects"], connectors=slide["connectors"], metrics=slide["metrics"], groups=slide["groups"])


def _shell_regions(slides: list[dict[str, Any]], width: int, height: int) -> list[dict[str, Any]]:
    """Module-level resolver hook used by structural QA and unit tests."""
    return ReadOnlyPrivateSourceSession._shell_regions(slides, width, height)


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


def _sanitize_color_evidence(value: dict[str, Any]) -> dict[str, Any]:
    required = {"source_kind", "direct_rgb", "theme_token", "resolved_rgb", "tint", "shade", "lum_mod", "lum_off", "transform_status", "theme_profile_id", "source_scope", "basis"}
    if set(value) != required or value["source_kind"] not in {"none", "direct_rgb", "theme_role", "unknown"} or value["transform_status"] not in {"supported", "unsupported", "unresolved"} or value["source_scope"] not in _SOURCE_SCOPES or value["basis"] not in _BASIS:
        raise Checkpoint2PolicyViolation("invalid color reconstruction evidence")
    for key in ("direct_rgb", "resolved_rgb"):
        if value[key] is not None and (not isinstance(value[key], str) or not re.fullmatch(r"[0-9A-Fa-f]{6}", value[key])):
            raise Checkpoint2PolicyViolation("invalid sanitized RGB")
    if value["theme_token"] is not None and value["theme_token"] not in _COLOR_TOKENS:
        raise Checkpoint2PolicyViolation("invalid theme token")
    if value["theme_profile_id"] is not None and (not isinstance(value["theme_profile_id"], str) or not re.fullmatch(r"T[0-9]{3,}", value["theme_profile_id"])):
        raise Checkpoint2PolicyViolation("invalid theme profile identity")
    return {key: value[key] for key in sorted(required)}


def _sanitize_font_observation(value: dict[str, Any], *, shell: bool = False) -> dict[str, Any]:
    required = {"role", "family", "theme_font_role", "script_role", "font_evidence_state", "size_pt", "weight", "style", "basis", "source_scope"}
    if not shell:
        required |= {"observation_id", "role_confidence", "supporting_object_id"}
    if set(value) != required or value["source_scope"] not in _SOURCE_SCOPES or value["basis"] not in _BASIS or value["weight"] not in {"regular", "bold", "unknown"} or value["style"] not in {"normal", "italic", "unknown"}:
        raise Checkpoint2PolicyViolation("invalid typography observation")
    family = value["family"]
    if not isinstance(family, str) or family == "other_approved" or (family != "unknown" and not _safe_font_name(family)):
        raise Checkpoint2PolicyViolation("unsafe font family")
    if value["theme_font_role"] is not None and value["theme_font_role"] not in {"major", "minor"}:
        raise Checkpoint2PolicyViolation("invalid theme font role")
    if value["script_role"] not in _SCRIPT_ROLES or value["font_evidence_state"] not in {"explicit_font", "theme_font_resolved", "theme_font_unresolved", "inherited_unresolved", "unknown"}:
        raise Checkpoint2PolicyViolation("invalid typography provenance")
    if value["script_role"] == "unspecified" and (value["theme_font_role"] is not None or value["font_evidence_state"] != "inherited_unresolved" or family != "unknown"):
        raise Checkpoint2PolicyViolation("unspecified script evidence must remain inherited and unresolved")
    if not isinstance(value["size_pt"], (int, float)) or value["size_pt"] <= 0 or value["size_pt"] > 200:
        raise Checkpoint2PolicyViolation("invalid font size")
    if not shell and (value["role_confidence"] not in {"structurally_supported", "provisional", "unknown"} or not re.fullmatch(r"O[0-9]{3,}", str(value["supporting_object_id"])) or not re.fullmatch(r"T[0-9]{3,}", str(value["observation_id"]))):
        raise Checkpoint2PolicyViolation("invalid body typography evidence")
    return {key: value[key] for key in sorted(required)}


def _sanitize_theme_profile(item: dict[str, Any]) -> dict[str, Any]:
    """Construct a closed, descriptor-local theme record from controlled data."""
    required = {"theme_profile_id", "usage_state", "authority_state", "supporting_master_ids", "supporting_slide_ids", "palette", "font_scheme", "supplemental_fonts"}
    if set(item) != required or not re.fullmatch(r"T[0-9]{3,}", str(item["theme_profile_id"])) or not isinstance(item["palette"], list) or not isinstance(item["font_scheme"], dict) or not isinstance(item["supplemental_fonts"], list):
        raise Checkpoint2PolicyViolation("invalid sanitized theme profile")
    referenced = bool(item["supporting_master_ids"] or item["supporting_slide_ids"])
    usage_state = "referenced" if referenced else "unreferenced"
    authority_state = "active_professor_style" if referenced else "reference_only"
    if item["usage_state"] != usage_state or item["authority_state"] != authority_state:
        raise Checkpoint2PolicyViolation("theme usage is not topology-derived")
    if any(not re.fullmatch(r"M[0-9]{3,}", str(value)) for value in item["supporting_master_ids"]) or any(not re.fullmatch(r"(?:SL|D)[0-9]{3,}", str(value)) for value in item["supporting_slide_ids"]):
        raise Checkpoint2PolicyViolation("invalid theme usage support")
    palette = []
    for color in item["palette"]:
        if set(color) != {"theme_token", "resolved_rgb", "basis", "source_scope"} or color["theme_token"] not in _COLOR_TOKENS or not re.fullmatch(r"[0-9A-Fa-f]{6}", str(color["resolved_rgb"])) or color["basis"] not in _BASIS or color["source_scope"] != "theme":
            raise Checkpoint2PolicyViolation("invalid theme palette evidence")
        palette.append({"theme_token": color["theme_token"], "resolved_rgb": color["resolved_rgb"].upper(), "basis": color["basis"], "source_scope": "theme"})
    if set(item["font_scheme"]) != {"major", "minor"}:
        raise Checkpoint2PolicyViolation("invalid theme font scheme")
    scheme: dict[str, dict[str, str]] = {}
    for role, scripts in item["font_scheme"].items():
        if not isinstance(scripts, dict) or not set(scripts).issubset({"latin", "east_asian", "complex_script"}) or any(not _safe_font_name(value) for value in scripts.values()):
            raise Checkpoint2PolicyViolation("invalid theme font scheme font")
        scheme[role] = {key: scripts[key] for key in sorted(scripts)}
    supplemental = []
    for value in item["supplemental_fonts"]:
        if set(value) != {"theme_font_role", "script_code", "family", "authority_state"} or value["theme_font_role"] not in {"major", "minor"} or value["script_code"] not in _SUPPLEMENTAL_THEME_SCRIPT_CODES or not _safe_font_name(value["family"]) or value["authority_state"] != authority_state:
            raise Checkpoint2PolicyViolation("invalid supplemental theme font")
        supplemental.append({"theme_font_role": value["theme_font_role"], "script_code": value["script_code"], "family": value["family"], "authority_state": authority_state})
    return {
        "theme_profile_id": item["theme_profile_id"],
        "usage_state": usage_state,
        "authority_state": authority_state,
        "supporting_master_ids": sorted(item["supporting_master_ids"]),
        "supporting_slide_ids": sorted(item["supporting_slide_ids"]),
        "palette": sorted(palette, key=lambda value: value["theme_token"]),
        "font_scheme": {role: scheme[role] for role in sorted(scheme)},
        "supplemental_fonts": sorted(supplemental, key=lambda value: (value["theme_font_role"], value["script_code"], value["family"])),
    }


def _sanitize_shell_full(raw: dict[str, Any]) -> dict[str, Any]:
    allowed = {"alias_uri", "source_sha256", "profile_id", "slide_size", "master_count", "layout_count", "shell_primitives", "slide_count", "measurement_basis", "layout_master_topology", "slide_layout_topology", "master_theme_topology", "shell_regions", "safe_content_bounds", "typography_roles", "style_roles", "placeholder_measurements", "theme_profiles"}
    if set(raw) != allowed: raise Checkpoint2PolicyViolation("unknown or incomplete shell descriptor fields")
    if raw["alias_uri"] not in SHELL_ALIASES or not isinstance(raw["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["source_sha256"]): raise Checkpoint2PolicyViolation("invalid shell identity")
    if not isinstance(raw["profile_id"], str) or not re.fullmatch(r"P3-[A-Z0-9-]+", raw["profile_id"]): raise Checkpoint2PolicyViolation("invalid shell profile ID")
    size = raw["slide_size"]
    if set(size) != {"width", "height", "basis"} or size["basis"] not in _BASIS: raise Checkpoint2PolicyViolation("invalid slide size")
    safe = raw["safe_content_bounds"]
    if set(safe) != {"value", "basis", "source_scope", "evidence_ids"} or safe["basis"] not in _BASIS or safe["source_scope"] not in _SOURCE_SCOPES:
        raise Checkpoint2PolicyViolation("invalid safe content bounds")
    safe_value = None if safe["value"] is None else _sanitize_geometry(safe["value"])
    basis = raw["measurement_basis"]
    basis_keys = {"slide_size", "topology", "regions", "typography", "styles", "primitives", "placeholders"}
    if set(basis) != basis_keys or any(value not in _BASIS for value in basis.values()): raise Checkpoint2PolicyViolation("invalid shell measurement basis")
    out = {"alias_uri": raw["alias_uri"], "source_sha256": raw["source_sha256"], "profile_id": raw["profile_id"], "slide_size": {"width": float(size["width"]), "height": float(size["height"]), "basis": size["basis"]}, "master_count": int(raw["master_count"]), "layout_count": int(raw["layout_count"]), "slide_count": int(raw["slide_count"]), "measurement_basis": {key: basis[key] for key in sorted(basis_keys)}, "layout_master_topology": [], "slide_layout_topology": [], "master_theme_topology": [], "shell_regions": [], "safe_content_bounds": {"value": safe_value, "basis": safe["basis"], "source_scope": safe["source_scope"], "evidence_ids": list(safe["evidence_ids"])}, "typography_roles": [], "style_roles": [], "shell_primitives": [], "placeholder_measurements": [], "theme_profiles": []}
    for key in ("layout_master_topology", "slide_layout_topology", "master_theme_topology"):
        values = []
        for item in raw[key]:
            if set(item) != {"source_id", "target_id", "basis", "source_scope"} or item["basis"] not in _BASIS or item["source_scope"] not in _SOURCE_SCOPES: raise Checkpoint2PolicyViolation("invalid topology item")
            values.append({"source_id": str(item["source_id"]), "target_id": str(item["target_id"]), "basis": item["basis"], "source_scope": item["source_scope"]})
        out[key] = values
    for item in raw["shell_regions"]:
        expected = {"region_id", "role", "geometry", "basis", "support_by_scope", "role_evidence"}
        if set(item) != expected or item["basis"] not in _BASIS or not isinstance(item["support_by_scope"], list): raise Checkpoint2PolicyViolation("invalid shell region")
        support = []
        for scoped in item["support_by_scope"]:
            if set(scoped) != {"source_scope", "occurrence_count", "source_container_count", "eligible_container_count", "coverage_ratio", "supporting_source_ids"} or scoped["source_scope"] not in {"slide_master", "slide_layout"}: raise Checkpoint2PolicyViolation("invalid scope-aware shell support")
            if scoped["occurrence_count"] < scoped["source_container_count"] or scoped["source_container_count"] > scoped["eligible_container_count"] or not 0 <= scoped["coverage_ratio"] <= 1 or abs(scoped["coverage_ratio"] - scoped["source_container_count"] / max(1, scoped["eligible_container_count"])) > 1e-6: raise Checkpoint2PolicyViolation("invalid scope-aware shell recurrence arithmetic")
            support.append({"source_scope": scoped["source_scope"], "occurrence_count": int(scoped["occurrence_count"]), "source_container_count": int(scoped["source_container_count"]), "eligible_container_count": int(scoped["eligible_container_count"]), "coverage_ratio": float(scoped["coverage_ratio"]), "supporting_source_ids": sorted(str(value) for value in scoped["supporting_source_ids"])})
        out["shell_regions"].append({"region_id": str(item["region_id"]), "role": item["role"], "geometry": _sanitize_geometry(item["geometry"]), "basis": item["basis"], "support_by_scope": sorted(support, key=lambda value: value["source_scope"]), "role_evidence": item["role_evidence"]})
    for item in raw["shell_primitives"]:
        expected = {"primitive_id", "primitive_class", "geometry", "occurrence_count", "source_container_count", "eligible_container_count", "coverage_ratio", "supporting_source_ids", "basis", "source_scope", "role_evidence"}
        if set(item) != expected or item["basis"] not in _BASIS or item["source_scope"] not in _SOURCE_SCOPES: raise Checkpoint2PolicyViolation("invalid shell primitive")
        if item["occurrence_count"] < item["source_container_count"] or item["source_container_count"] > item["eligible_container_count"] or not 0 <= item["coverage_ratio"] <= 1: raise Checkpoint2PolicyViolation("invalid primitive recurrence arithmetic")
        out["shell_primitives"].append({"primitive_id": str(item["primitive_id"]), "primitive_class": item["primitive_class"], "geometry": _sanitize_geometry(item["geometry"]), "occurrence_count": int(item["occurrence_count"]), "source_container_count": int(item["source_container_count"]), "eligible_container_count": int(item["eligible_container_count"]), "coverage_ratio": float(item["coverage_ratio"]), "supporting_source_ids": [str(value) for value in item["supporting_source_ids"]], "basis": item["basis"], "source_scope": item["source_scope"], "role_evidence": item["role_evidence"]})
    for item in raw["typography_roles"]:
        out["typography_roles"].append(_sanitize_font_observation(item, shell=True))
    for item in raw["style_roles"]:
        expected = {"role", "fill_role", "stroke_role", "line_width_pt", "basis", "source_scope", "fill_color_evidence", "stroke_color_evidence"}
        if set(item) != expected: raise Checkpoint2PolicyViolation("invalid style role")
        out["style_roles"].append({"role": item["role"], "fill_role": item["fill_role"], "stroke_role": item["stroke_role"], "line_width_pt": float(item["line_width_pt"]), "basis": item["basis"], "source_scope": item["source_scope"], "fill_color_evidence": _sanitize_color_evidence(item["fill_color_evidence"]), "stroke_color_evidence": _sanitize_color_evidence(item["stroke_color_evidence"])})
    for item in raw["placeholder_measurements"]:
        if set(item) != {"placeholder_id", "placeholder_type", "geometry", "basis", "source_scope", "source_container_id"} or item["source_scope"] not in _SOURCE_SCOPES or item["basis"] not in _BASIS:
            raise Checkpoint2PolicyViolation("invalid placeholder measurement")
        out["placeholder_measurements"].append({"placeholder_id": str(item["placeholder_id"]), "placeholder_type": item["placeholder_type"], "geometry": _sanitize_geometry(item["geometry"]), "basis": item["basis"], "source_scope": item["source_scope"], "source_container_id": item["source_container_id"]})
    for item in raw["theme_profiles"]:
        out["theme_profiles"].append(_sanitize_theme_profile(item))
    _lexical_reject(out)
    errors = _schema_registry().errors("sanitized-shell-structural-descriptors", {"schema_version": "1.0.0", "descriptors": [out, out]})
    if errors: raise Checkpoint2PolicyViolation("sanitized shell descriptor schema failed: " + "; ".join(errors[:3]))
    return out


def _sanitize_body_full(raw: dict[str, Any]) -> dict[str, Any]:
    if set(raw) != {"alias_uri", "source_sha256", "profile_id", "slide_size", "slide_count", "candidate_families", "body_measurements", "theme_profiles", "slide_theme_topology"}: raise Checkpoint2PolicyViolation("unknown or incomplete body descriptor fields")
    if raw["alias_uri"] != BODY_ALIAS or not isinstance(raw["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["source_sha256"]): raise Checkpoint2PolicyViolation("invalid body identity")
    out = {"alias_uri": raw["alias_uri"], "source_sha256": raw["source_sha256"], "profile_id": raw["profile_id"], "slide_size": {"width": float(raw["slide_size"]["width"]), "height": float(raw["slide_size"]["height"]), "basis": raw["slide_size"]["basis"]}, "slide_count": int(raw["slide_count"]), "candidate_families": [], "body_measurements": [], "theme_profiles": [], "slide_theme_topology": []}
    for item in raw["candidate_families"]:
        if set(item) != {"candidate_id", "bound_slide_id", "binding_fingerprint", "family", "confidence", "evidence_basis"}: raise Checkpoint2PolicyViolation("invalid candidate family")
        if not re.fullmatch(r"BC[0-9]{3,}", str(item["candidate_id"])) or not re.fullmatch(r"SL[0-9]{3,}", str(item["bound_slide_id"])) or not re.fullmatch(r"[0-9a-f]{64}", str(item["binding_fingerprint"])): raise Checkpoint2PolicyViolation("invalid candidate binding identity")
        out["candidate_families"].append({"candidate_id": str(item["candidate_id"]), "bound_slide_id": str(item["bound_slide_id"]), "binding_fingerprint": str(item["binding_fingerprint"]), "family": item["family"], "confidence": item["confidence"], "evidence_basis": list(item["evidence_basis"])})
    for item in raw["body_measurements"]:
        required = {"slide_id", "measurement_basis", "objects", "connectors", "groups", "panels", "metrics", "style_roles", "typography_observations"}
        if set(item) != required: raise Checkpoint2PolicyViolation("invalid body measurement")
        objects = []
        for obj in item["objects"]:
            expected_obj = {"object_id", "object_class", "primitive_type", "geometry", "group_id", "style", "basis", "source_scope", "rotation_status", "rotation_deg", "geometry_eligible"}
            if set(obj) != expected_obj or obj["source_scope"] not in _SOURCE_SCOPES: raise Checkpoint2PolicyViolation("invalid body object")
            style = obj["style"]
            expected_style = {"role", "fill_role", "stroke_role", "line_width_pt", "basis", "source_scope", "fill_color_evidence", "stroke_color_evidence"}
            if set(style) != expected_style: raise Checkpoint2PolicyViolation("invalid body style")
            objects.append({"object_id": str(obj["object_id"]), "object_class": obj["object_class"], "primitive_type": obj["primitive_type"], "geometry": _sanitize_geometry(obj["geometry"]), "group_id": obj["group_id"], "style": {"role": style["role"], "fill_role": style["fill_role"], "stroke_role": style["stroke_role"], "line_width_pt": float(style["line_width_pt"]), "basis": style["basis"], "source_scope": style["source_scope"], "fill_color_evidence": _sanitize_color_evidence(style["fill_color_evidence"]), "stroke_color_evidence": _sanitize_color_evidence(style["stroke_color_evidence"])}, "basis": obj["basis"], "source_scope": obj["source_scope"], "rotation_status": obj["rotation_status"], "rotation_deg": float(obj["rotation_deg"]), "geometry_eligible": bool(obj["geometry_eligible"])})
        connectors = []
        for conn in item["connectors"]:
            expected = {"object_id", "orientation", "start", "end", "head_arrow", "tail_arrow", "directedness", "flip_h", "flip_v", "basis", "source_scope", "rotation_status", "rotation_deg", "geometry_eligible"}
            if set(conn) != expected or conn["source_scope"] not in _SOURCE_SCOPES: raise Checkpoint2PolicyViolation("invalid connector")
            connectors.append({"object_id": str(conn["object_id"]), "orientation": conn["orientation"], "start": [float(conn["start"][0]), float(conn["start"][1])], "end": [float(conn["end"][0]), float(conn["end"][1])], "head_arrow": conn["head_arrow"], "tail_arrow": conn["tail_arrow"], "directedness": conn["directedness"], "flip_h": bool(conn["flip_h"]), "flip_v": bool(conn["flip_v"]), "basis": conn["basis"], "source_scope": conn["source_scope"], "rotation_status": conn["rotation_status"], "rotation_deg": float(conn["rotation_deg"]), "geometry_eligible": bool(conn["geometry_eligible"])})
        groups = []
        for group in item["groups"]:
            if set(group) != {"group_id", "member_count", "basis", "source_scope", "rotation_status", "rotation_deg", "geometry_eligible"}: raise Checkpoint2PolicyViolation("invalid group")
            groups.append({"group_id": str(group["group_id"]), "member_count": int(group["member_count"]), "basis": group["basis"], "source_scope": group["source_scope"], "rotation_status": group["rotation_status"], "rotation_deg": float(group["rotation_deg"]), "geometry_eligible": bool(group["geometry_eligible"])})
        panels = []
        for panel in item["panels"]:
            if set(panel) != {"panel_id", "geometry", "basis"}: raise Checkpoint2PolicyViolation("invalid panel")
            panels.append({"panel_id": str(panel["panel_id"]), "geometry": _sanitize_geometry(panel["geometry"]), "basis": panel["basis"]})
        metrics = item["metrics"]
        metric_keys = {"text_area_ratio", "figure_area_ratio", "dominant_figure_ratio", "figure_text_ratio", "annotation_density", "whitespace_fraction", "comparison_symmetry", "matrix_rows", "matrix_columns", "panel_count", "caption_candidate_count", "callout_candidate_count", "photo_schematic_relation"}
        if set(metrics) != metric_keys: raise Checkpoint2PolicyViolation("invalid body metrics")
        for observation in metrics.values():
            if set(observation) != {"value", "basis", "evidence_state", "supporting_object_ids"} or observation["basis"] not in _BASIS or observation["evidence_state"] not in {"measured", "derived", "unavailable"}:
                raise Checkpoint2PolicyViolation("invalid metric observation")
            if observation["basis"] == "derived" and (observation["value"] is None or not observation["supporting_object_ids"]):
                raise Checkpoint2PolicyViolation("derived metric lacks measurement evidence")
        styles = []
        for style in item["style_roles"]:
            if set(style) != {"role", "fill_role", "stroke_role", "line_width_pt", "basis", "source_scope", "fill_color_evidence", "stroke_color_evidence"}: raise Checkpoint2PolicyViolation("invalid body style role")
            styles.append({"role": style["role"], "fill_role": style["fill_role"], "stroke_role": style["stroke_role"], "line_width_pt": float(style["line_width_pt"]), "basis": style["basis"], "source_scope": style["source_scope"], "fill_color_evidence": _sanitize_color_evidence(style["fill_color_evidence"]), "stroke_color_evidence": _sanitize_color_evidence(style["stroke_color_evidence"])})
        typography = [_sanitize_font_observation(value, shell=False) for value in item["typography_observations"]]
        out["body_measurements"].append({"slide_id": str(item["slide_id"]), "measurement_basis": item["measurement_basis"], "objects": objects, "connectors": connectors, "groups": groups, "panels": panels, "metrics": {key: metrics[key] for key in metric_keys}, "style_roles": styles, "typography_observations": typography})
    if len({item["candidate_id"] for item in out["candidate_families"]}) != len(out["candidate_families"]) or len({item["bound_slide_id"] for item in out["candidate_families"]}) != len(out["candidate_families"]): raise Checkpoint2PolicyViolation("ambiguous candidate binding identity")
    measurements_by_slide = {item["slide_id"]: item for item in out["body_measurements"]}
    if len(measurements_by_slide) != len(out["body_measurements"]): raise Checkpoint2PolicyViolation("duplicate body measurement slide identity")
    for candidate in out["candidate_families"]:
        measurement = measurements_by_slide.get(candidate["bound_slide_id"])
        if measurement is None or candidate["binding_fingerprint"] != _body_binding_fingerprint(candidate, measurement): raise Checkpoint2PolicyViolation("candidate binding fingerprint mismatch")
    for item in raw["theme_profiles"]:
        out["theme_profiles"].append(_sanitize_theme_profile(item))
    profile_ids = {item["theme_profile_id"] for item in out["theme_profiles"]}
    for edge in raw["slide_theme_topology"]:
        if set(edge) != {"source_id", "target_id", "basis", "source_scope"} or not re.fullmatch(r"SL[0-9]{3,}", str(edge["source_id"])) or edge["source_scope"] != "slide_body" or edge["basis"] not in _BASIS or (edge["basis"] == "measured" and edge["target_id"] not in profile_ids): raise Checkpoint2PolicyViolation("invalid body slide theme topology")
        out["slide_theme_topology"].append({key: edge[key] for key in ("source_id", "target_id", "basis", "source_scope")})
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
        payload = {"shell": shell_descriptors, "body": body_descriptor}
        forbidden = RepositoryPrivacyScanner().scan_mapping(payload, location="sanitized_descriptor_payload")
        checks.append({"check_id": "CP2-DQ-PROHIBITED-FIELDS", "status": "pass" if not forbidden else "fail"})
        scopes = [support.get("source_scope") for descriptor in shell_descriptors for region in descriptor.get("shell_regions", []) for support in region.get("support_by_scope", [])]
        scopes += [item.get("source_scope") for descriptor in shell_descriptors for section in (descriptor.get("shell_primitives", []), descriptor.get("style_roles", [])) for item in section]
        checks.append({"check_id": "CP2-DQ-SHELL-SOURCE-SCOPE", "status": "pass" if scopes and all(scope in _SOURCE_SCOPES for scope in scopes) else "fail"})
        observations = [observation for measurement in body_descriptor.get("body_measurements", []) for observation in measurement.get("metrics", {}).values()]
        checks.append({"check_id": "CP2-DQ-METRIC-OBSERVATIONS", "status": "pass" if observations and all(not (item.get("basis") == "derived" and (item.get("value") is None or not item.get("supporting_object_ids"))) for item in observations) else "fail"})
        checks.append({"check_id": "CP2-DQ-FAMILY-EVIDENCE", "status": "pass" if all(item.get("confidence") != "structurally_supported" or len(item.get("evidence_basis", [])) >= 2 for item in body_descriptor.get("candidate_families", [])) else "fail"})
        shell_regions = [region for descriptor in shell_descriptors for region in descriptor.get("shell_regions", [])]
        role_unique = all(len({region.get("role") for region in descriptor.get("shell_regions", [])}) == len(descriptor.get("shell_regions", [])) for descriptor in shell_descriptors)
        recurrence_ok = all(region.get("support_by_scope") and all(support.get("occurrence_count", 0) >= support.get("source_container_count", 0) <= support.get("eligible_container_count", 0) and abs(support.get("coverage_ratio", -1) - support.get("source_container_count", 0) / max(1, support.get("eligible_container_count", 0))) < 1e-6 for support in region.get("support_by_scope", [])) for region in shell_regions)
        checks.append({"check_id": "CP2-DQ-SHELL-ROLE-CONSISTENCY", "status": "pass" if role_unique else "fail"})
        checks.append({"check_id": "CP2-DQ-SHELL-RECURRENCE", "status": "pass" if recurrence_ok else "fail"})
        date_time_ok = all(region.get("role") != "navigation" or region.get("role_evidence") != "placeholder_semantic" for descriptor in shell_descriptors for region in descriptor.get("shell_regions", [])) and all(placeholder.get("placeholder_type") != "dt" or any(region.get("role") == "date_time" for region in descriptor.get("shell_regions", [])) for descriptor in shell_descriptors for placeholder in descriptor.get("placeholder_measurements", []))
        checks.append({"check_id": "CP2-DQ-PLACEHOLDER-SEMANTICS", "status": "pass" if date_time_ok else "fail"})
        scope_support_ok = all(region.get("support_by_scope") and len({support.get("source_scope") for support in region.get("support_by_scope", [])}) == len(region.get("support_by_scope", [])) for region in shell_regions)
        checks.append({"check_id": "CP2-DQ-SCOPE-AWARE-SUPPORT", "status": "pass" if scope_support_ok else "fail"})
        primitives = [primitive for descriptor in shell_descriptors for primitive in descriptor.get("shell_primitives", [])]
        primitive_recurrence = all(item.get("occurrence_count", 0) >= item.get("source_container_count", 0) <= item.get("eligible_container_count", 0) and abs(item.get("coverage_ratio", -1) - item.get("source_container_count", 0) / max(1, item.get("eligible_container_count", 0))) < 1e-6 for item in primitives)
        checks.append({"check_id": "CP2-DQ-CONTAINER-COVERAGE", "status": "pass" if primitive_recurrence else "fail"})
        colors = [style.get(key) for descriptor in shell_descriptors for style in descriptor.get("style_roles", []) for key in ("fill_color_evidence", "stroke_color_evidence")]
        colors += [style.get(key) for measurement in body_descriptor.get("body_measurements", []) for style in measurement.get("style_roles", []) for key in ("fill_color_evidence", "stroke_color_evidence")]
        color_ok = bool(colors) and all(item.get("transform_status") in {"supported", "unsupported", "unresolved"} and item.get("basis") in _BASIS and item.get("source_scope") in _SOURCE_SCOPES for item in colors)
        checks.append({"check_id": "CP2-DQ-COLOR-RECONSTRUCTION", "status": "pass" if color_ok else "fail"})
        all_descriptors = [*shell_descriptors, body_descriptor]
        descriptor_theme_profiles = {
            descriptor.get("profile_id"): {
                profile.get("theme_profile_id"): {entry.get("theme_token"): entry.get("resolved_rgb") for entry in profile.get("palette", [])}
                for profile in descriptor.get("theme_profiles", [])
            }
            for descriptor in all_descriptors
        }
        master_theme_edges = [(descriptor.get("profile_id"), edge) for descriptor in shell_descriptors for edge in descriptor.get("master_theme_topology", [])]
        topology_ok = bool(descriptor_theme_profiles) and all(profile_id in descriptor_theme_profiles and edge.get("source_id", "").startswith("M") and edge.get("target_id") in descriptor_theme_profiles[profile_id] for profile_id, edge in master_theme_edges)
        checks.append({"check_id": "CP2-DQ-MASTER-THEME-TOPOLOGY", "status": "pass" if topology_ok else "fail"})
        shell_colors = [(descriptor.get("profile_id"), style.get(key)) for descriptor in shell_descriptors for style in descriptor.get("style_roles", []) for key in ("fill_color_evidence", "stroke_color_evidence")]
        binding_ok = all(color.get("theme_token") is None or (color.get("theme_profile_id") in descriptor_theme_profiles.get(profile_id, {}) and descriptor_theme_profiles[profile_id][color["theme_profile_id"]].get(color["theme_token"]) == color.get("resolved_rgb")) for profile_id, color in shell_colors)
        checks.append({"check_id": "CP2-DQ-THEME-BOUND-COLOR", "status": "pass" if binding_ok else "fail"})
        fonts = [font for descriptor in shell_descriptors for font in descriptor.get("typography_roles", [])]
        body_fonts = [font for measurement in body_descriptor.get("body_measurements", []) for font in measurement.get("typography_observations", [])]
        font_states = ("explicit_font", "theme_font_resolved", "theme_font_unresolved", "inherited_unresolved", "unknown")
        self.evidence.typography_resolution_counts = typography_resolution_counts([*fonts, *body_fonts])
        meaningful_fonts = [font for font in [*fonts, *body_fonts] if font.get("font_evidence_state") in {"explicit_font", "theme_font_resolved"} and font.get("family") not in {None, "unknown", "other_approved"}]
        all_fonts = [*fonts, *body_fonts]
        font_ok = (not all_fonts or bool(meaningful_fonts)) and all(font.get("basis") in _BASIS and font.get("source_scope") in _SOURCE_SCOPES and font.get("script_role") in _SCRIPT_ROLES for font in meaningful_fonts)
        checks.append({"check_id": "CP2-DQ-FONT-FIDELITY", "status": "pass" if font_ok else "fail"})
        checks.append({"check_id": "CP2-DQ-TYPOGRAPHY-EVIDENCE-STATES", "status": "pass" if all(sum(values.values()) >= 0 for values in self.evidence.typography_resolution_counts.values()) and (not all_fonts or bool(meaningful_fonts)) else "fail"})
        body_observation_ids = [font.get("observation_id") for font in body_fonts]
        per_script_ok = len(body_observation_ids) == len(set(body_observation_ids)) and all(font.get("script_role") in _SCRIPT_ROLES and (font.get("script_role") != "unspecified" or (font.get("family") == "unknown" and font.get("theme_font_role") is None and font.get("font_evidence_state") == "inherited_unresolved")) and (font.get("theme_font_role") is None or font.get("font_evidence_state") in {"theme_font_resolved", "theme_font_unresolved"}) for font in all_fonts)
        checks.append({"check_id": "CP2-DQ-PER-SCRIPT-TYPOGRAPHY", "status": "pass" if per_script_ok else "fail"})
        checks.append({"check_id": "CP2-DQ-SCRIPT-TRUTH", "status": "pass" if per_script_ok else "fail"})
        reconciliation_ok = sum(sum(states.values()) for states in self.evidence.typography_resolution_counts.values()) == len(all_fonts)
        checks.append({"check_id": "CP2-DQ-TYPOGRAPHY-COUNT-RECONCILIATION", "status": "pass" if reconciliation_ok else "fail"})
        supplemental_ok = all(
            item.get("theme_font_role") in {"major", "minor"}
            and item.get("script_code") in _SUPPLEMENTAL_THEME_SCRIPT_CODES
            and _safe_font_name(item.get("family", ""))
            for descriptor in all_descriptors
            for profile in descriptor.get("theme_profiles", [])
            for item in profile.get("supplemental_fonts", [])
        )
        checks.append({"check_id": "CP2-DQ-SUPPLEMENTAL-THEME-FONT-CLOSURE", "status": "pass" if supplemental_ok else "fail"})
        local_theme_identity_ok = all(
            len(themes) == len(set(themes))
            for themes in (list(profiles) for profiles in descriptor_theme_profiles.values())
        ) and all(
            edge.get("target_id") in descriptor_theme_profiles.get(descriptor.get("profile_id"), {})
            for descriptor in all_descriptors
            for edge in descriptor.get("slide_theme_topology", [])
            if edge.get("basis") == "measured"
        )
        checks.append({"check_id": "CP2-DQ-DESCRIPTOR-LOCAL-THEME-IDENTITY", "status": "pass" if local_theme_identity_ok else "fail"})
        theme_reachability_ok = True
        active_theme_count = 0
        for descriptor in all_descriptors:
            themes = {profile.get("theme_profile_id"): profile for profile in descriptor.get("theme_profiles", [])}
            master_edges = descriptor.get("master_theme_topology", [])
            slide_edges = descriptor.get("slide_theme_topology", [])
            for edge in [*master_edges, *slide_edges]:
                if edge.get("basis") == "measured" and edge.get("target_id") not in themes:
                    theme_reachability_ok = False
            master_support = {theme_id: sorted(edge.get("source_id") for edge in master_edges if edge.get("basis") == "measured" and edge.get("target_id") == theme_id) for theme_id in themes}
            slide_support = {theme_id: sorted(edge.get("source_id") for edge in slide_edges if edge.get("basis") == "measured" and edge.get("target_id") == theme_id) for theme_id in themes}
            for theme_id, profile in themes.items():
                referenced = bool(master_support[theme_id] or slide_support[theme_id])
                expected_usage = "referenced" if referenced else "unreferenced"
                expected_authority = "active_professor_style" if referenced else "reference_only"
                if profile.get("usage_state") != expected_usage or profile.get("authority_state") != expected_authority or profile.get("supporting_master_ids") != master_support[theme_id] or profile.get("supporting_slide_ids") != slide_support[theme_id]:
                    theme_reachability_ok = False
                if any(item.get("authority_state") != expected_authority for item in profile.get("supplemental_fonts", [])):
                    theme_reachability_ok = False
                active_theme_count += int(referenced)
        checks.append({"check_id": "CP2-DQ-THEME-REACHABILITY", "status": "pass" if theme_reachability_ok else "fail"})
        checks.append({"check_id": "CP2-DQ-ACTIVE-THEME-CLASSIFICATION", "status": "pass" if theme_reachability_ok and active_theme_count > 0 else "fail"})
        checks.append({"check_id": "CP2-DQ-SUPPLEMENTAL-FONT-AUTHORITY", "status": "pass" if theme_reachability_ok else "fail"})
        rotation_ok = all((obj.get("rotation_status") == "unsupported") == (not obj.get("geometry_eligible", True)) and (obj.get("rotation_status") != "unsupported" or obj.get("geometry", {}).get("basis") != "measured") for measurement in body_descriptor.get("body_measurements", []) for obj in [*measurement.get("objects", []), *measurement.get("connectors", [])] + measurement.get("groups", []))
        checks.append({"check_id": "CP2-DQ-ROTATION-TRUTH", "status": "pass" if rotation_ok else "fail"})
        typography_ok = all("typography_observations" in measurement and all(font.get("source_scope") in {"slide_body", "slide_content"} for font in measurement.get("typography_observations", [])) for measurement in body_descriptor.get("body_measurements", []))
        checks.append({"check_id": "CP2-DQ-BODY-TYPOGRAPHY", "status": "pass" if typography_ok else "fail"})
        group_geometry_ok = all(-0.000001 <= coordinate <= 1.000001 for measurement in body_descriptor.get("body_measurements", []) for obj in measurement.get("objects", []) for coordinate in (obj["geometry"]["x"], obj["geometry"]["y"], obj["geometry"]["x"] + obj["geometry"]["w"], obj["geometry"]["y"] + obj["geometry"]["h"]))
        checks.append({"check_id": "CP2-DQ-GROUP-GEOMETRY", "status": "pass" if group_geometry_ok else "fail"})
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
        try:
            session = resolver.resolve(alias_uri).open_read_only(); raw = session.profile_structurally("body" if alias_uri == BODY_ALIAS else "shell"); raw.pop("render_count", None)
            if alias_uri == BODY_ALIAS:
                body_descriptor = sanitize_body_descriptor(raw)
            else:
                shell_descriptors.append(sanitize_shell_descriptor(raw))
            run.evidence.update_session(alias_uri, sanitizer_handoff="pass")
            run.evidence.close_session(alias_uri, outcome="success")
        except Exception:
            if alias_uri in run.evidence.source_sessions:
                run.evidence.update_session(alias_uri, sanitizer_handoff="fail")
                run.evidence.close_session(alias_uri, outcome="failed")
            raise
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
    if registry.errors("checkpoint-2-qa", qa): raise Checkpoint2PolicyViolation("Checkpoint 2 QA schema failed")
    (output_root / "checkpoint-2-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa
