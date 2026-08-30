"""CP5-A closed Scientific SVG authoring IR and static validation.

This module validates visual authoring state only.  It intentionally does not
render figures, resolve scientific provenance, query private fixtures, or make
any native PowerPoint capability claim.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import unicodedata
from typing import Any
from xml.etree import ElementTree as ET

from .contracts import SchemaRegistry


SVG_NS = "http://www.w3.org/2000/svg"
ROOT = Path(__file__).resolve().parents[4]
ARTIFACTS = ROOT / "thesis-deck-system" / "artifacts" / "phase3"
SCHEMAS = ROOT / "thesis-deck-system" / "schemas"
PROFILE_PATH = ARTIFACTS / "scientific-svg-profile.json"
ROLE_REGISTRY_PATH = ARTIFACTS / "semantic-svg-role-registry.json"
CANONICALIZATION_VERSION = "1.0.0"
OBJECT_ID_RE = re.compile(r"^obj-[a-z][a-z0-9-]{0,63}$")
NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?|,")
FORBIDDEN_PROVENANCE = re.compile(r"(?:claim|evidence|cursor|hypothesis|research-block|stage|decision|action|source-hash|provenance)", re.IGNORECASE)
WINDOWS_SEPARATOR = chr(92)
PRIVATE_PATH = re.compile(r"(?:[A-Za-z]:[" + re.escape(WINDOWS_SEPARATOR) + r"/]|" + re.escape(WINDOWS_SEPARATOR * 2) + r"|/mnt/[A-Za-z]/|file://|https?://)", re.IGNORECASE)

REGISTERED_GRAMMARS = {"path": {"svg-path-v1"}, "points": {"svg-points-v1"}, "transform": {"svg-transform-v1"}}


class ScientificSvgError(ValueError):
    """A closed Scientific SVG contract cannot be satisfied."""


def _sha(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _namespace(name: str) -> str | None:
    return name[1:].split("}", 1)[0] if name.startswith("{") else None


def _source_sha(source: str) -> str:
    return sha256(source.encode("utf-8")).hexdigest()


def _parse(source: str) -> ET.Element:
    if re.search(r"<!DOCTYPE|<!ENTITY", source, re.IGNORECASE):
        raise ScientificSvgError("DTD or entity declaration is forbidden")
    try:
        return ET.fromstring(source.encode("utf-8"))
    except ET.ParseError as exc:
        raise ScientificSvgError(f"XML well-formedness failure: {exc}") from exc


def _number(value: str) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _format_number(value: str) -> str:
    number = _number(value)
    if number is None:
        return value
    normalized = f"{number:.12f}".rstrip("0").rstrip(".")
    return "0" if normalized in {"", "-0"} else normalized


def _normalize_numbers(value: str) -> str:
    return NUMBER_RE.sub(lambda match: _format_number(match.group(0)), value)


def _canonical_element(element: ET.Element) -> str:
    if _namespace(element.tag) != SVG_NS:
        raise ScientificSvgError("foreign namespace cannot be canonicalized as Scientific SVG")
    tag = _tag(element)
    attributes = []
    for key, value in sorted(element.attrib.items(), key=lambda item: item[0]):
        if _namespace(key) is not None:
            raise ScientificSvgError("foreign attribute namespace cannot be canonicalized as Scientific SVG")
        name = key.rsplit("}", 1)[-1]
        rendered = _normalize_numbers(value) if name in {"x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2", "points", "d", "viewBox", "transform", "stroke-width", "font-size", "dx", "dy"} else value
        attributes.append(f' {name}="{ET._escape_attrib(rendered)}"')
    tag_is_textual = tag in {"text", "tspan"}
    text = unicodedata.normalize("NFC", element.text or "")
    if not tag_is_textual and not text.strip():
        text = ""
    children = "".join(_canonical_element(child) + _canonical_tail(element, child) for child in list(element))
    if not text and not children:
        return f"<{tag}{''.join(attributes)}/>"
    return f"<{tag}{''.join(attributes)}>{ET._escape_cdata(text)}{children}</{tag}>"


def _canonical_tail(parent: ET.Element, child: ET.Element) -> str:
    tail = unicodedata.normalize("NFC", child.tail or "")
    # Whitespace between textual siblings is visible editable content.  Outside
    # text/tspan it is formatting and may normalize away.
    if _tag(parent) in {"text", "tspan"} and "\n" not in tail and "\r" not in tail:
        return tail
    return tail if tail.strip() else ""


def canonicalize_svg(source: str) -> dict[str, str]:
    """Produce the versioned canonical SVG identity without reordering children."""
    root = _parse(source)
    canonical = '<?xml version="1.0" encoding="UTF-8"?>' + _canonical_element(root)
    return {"source_sha256": _source_sha(source), "canonical_sha256": _sha(canonical), "canonical_svg": canonical, "canonicalization_version": CANONICALIZATION_VERSION}


def _presentation_tuple(element: ET.Element) -> tuple[Any, ...]:
    attrs = tuple(sorted((key.rsplit("}", 1)[-1], value) for key, value in element.attrib.items() if key.rsplit("}", 1)[-1] not in {"data-thesis-svg-version", "data-thesis-figure-id", "data-visual-class", "data-semantic-role"}))
    text = unicodedata.normalize("NFC", element.text or "")
    if _tag(element) not in {"text", "tspan"} and not text.strip():
        text = ""
    return (_tag(element), attrs, text, tuple(_presentation_tuple(child) for child in list(element)))


def strip_semantic_metadata(source: str) -> str:
    root = _parse(source)
    for element in root.iter():
        for key in list(element.attrib):
            if key.rsplit("}", 1)[-1] in {"data-thesis-svg-version", "data-thesis-figure-id", "data-visual-class", "data-semantic-role"}:
                del element.attrib[key]
    return _canonical_element(root)


def presentation_ast_hash(source: str) -> str:
    root = _parse(source)
    return _sha(json.dumps(_presentation_tuple(root), ensure_ascii=False, separators=(",", ":")))


def _finding(check: str, rule: str, message: str, *, path: str = "$", object_id: str | None = None, severity: str = "error", status: str = "fail") -> dict[str, Any]:
    return {"check_id": check, "rule_id": rule, "severity": severity, "status": status, "message": message, "path": path, "object_id": object_id}


class ScientificSvgValidator:
    """Execution-owned deterministic validator for the CP5-A SVG subset."""

    def __init__(self, root: Path, profile: dict[str, Any], roles: dict[str, Any]):
        self.root = root
        self.profile = deepcopy(profile)
        self.roles = deepcopy(roles)
        self.role_map = {item["role_id"]: item for item in roles["roles"]}
        registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True)
        try:
            registry.validate("scientific-svg-profile", profile)
            registry.validate("semantic-svg-role-registry", roles)
        except ValueError as exc:
            raise ScientificSvgError(str(exc)) from exc
        self.attributes = {name: set(attributes) for name, attributes in profile["element_attribute_contract"].items()}
        if set(self.attributes) != set(profile["allowed_elements"]):
            raise ScientificSvgError("profile element/attribute contract is incomplete")
        for grammar_kind, grammar_id in profile["grammar_bindings"].items():
            if grammar_id not in REGISTERED_GRAMMARS.get(grammar_kind, set()):
                raise ScientificSvgError(f"unregistered {grammar_kind} grammar: {grammar_id}")

    @classmethod
    def load_default(cls, root: Path | None = None) -> "ScientificSvgValidator":
        root = root or ROOT
        return cls(root, json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-svg-profile.json").read_text(encoding="utf-8")), json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "semantic-svg-role-registry.json").read_text(encoding="utf-8")))

    def validate(self, source: str, *, figure_spec: dict[str, Any] | None = None) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        source_hash = _source_sha(source)
        try:
            root = _parse(source)
        except ScientificSvgError as exc:
            rule = "CP5A-FORBIDDEN-EXECUTABLE" if "DTD or entity" in str(exc) else "CP5A-XML-WELL-FORMED"
            findings.append(_finding("CP5A-XML-WELL-FORMED", rule, str(exc)))
            return self._report("unknown", source_hash, None, findings, False)
        if root.tag != f"{{{SVG_NS}}}svg":
            findings.append(_finding("CP5A-NAMESPACE", "CP5A-NAMESPACE", "root must be SVG namespace"))
        if root.get("data-thesis-svg-version") != self.profile["schema_version"]:
            findings.append(_finding("CP5A-PROFILE-VERSION", "CP5A-PROFILE-VERSION", "registered profile version required"))
        figure_id = root.get("data-thesis-figure-id") or "unknown"
        if not re.fullmatch(r"FIG[0-9]{3,}", figure_id):
            findings.append(_finding("CP5A-FIGURE-ID", "CP5A-FIGURE-ID", "root figure identity invalid"))
        if figure_spec is not None and figure_id != figure_spec.get("figure_id"):
            findings.append(_finding("CP5A-FIGURE-SPEC-BINDING", "CP5A-FIGURE-SPEC-BINDING", "SVG figure ID differs from Figure Spec"))
        visual_class = figure_spec.get("visual_class") if figure_spec else None
        if root.get("data-visual-class") is not None and root.get("data-visual-class") != visual_class:
            findings.append(_finding("CP5A-VISUAL-CLASS", "CP5A-VISUAL-CLASS-BINDING", "root visual class differs from Figure Spec"))
        self._validate_viewbox(root, findings)
        ids: set[str] = set()
        for index, element in enumerate(root.iter()):
            self._validate_element(element, index, ids, findings, visual_class, element is root)
        try:
            canonical = canonicalize_svg(source)
        except ScientificSvgError as exc:
            findings.append(_finding("CP5A-NAMESPACE", "CP5A-NAMESPACE", str(exc)))
            canonical = None
        stripped = strip_semantic_metadata(source) if canonical is not None else ""
        metadata_equal = canonical is not None and presentation_ast_hash(source) == presentation_ast_hash(stripped)
        if not metadata_equal:
            findings.append(_finding("CP5A-METADATA-INVISIBILITY", "CP5A-METADATA-INVISIBILITY", "semantic metadata changed presentation AST"))
        return self._report(figure_id, source_hash, canonical, findings, metadata_equal)

    def _validate_viewbox(self, root: ET.Element, findings: list[dict[str, Any]]) -> None:
        values = (root.get("viewBox") or "").replace(",", " ").split()
        if len(values) != 4 or any(_number(value) is None for value in values) or _number(values[2]) <= 0 or _number(values[3]) <= 0:
            findings.append(_finding("CP5A-VIEWBOX", "CP5A-NUMERIC-POLICY", "finite positive four-number viewBox required"))

    def _validate_element(self, element: ET.Element, index: int, ids: set[str], findings: list[dict[str, Any]], visual_class: str | None, is_root: bool) -> None:
        name = _tag(element)
        path = f"/{name}[{index}]"
        if _namespace(element.tag) != SVG_NS:
            findings.append(_finding("CP5A-NAMESPACE", "CP5A-NAMESPACE", "foreign element namespace forbidden", path=path))
            return
        if name not in self.attributes:
            rule = "CP5A-FORBIDDEN-EXECUTABLE" if name in {"script", "foreignObject", "style", "animate", "animateTransform", "set", "filter"} else "CP5A-ELEMENT-ALLOWLIST"
            findings.append(_finding("CP5A-ELEMENTS", rule, f"element {name} is not allowed", path=path))
            return
        for key, value in element.attrib.items():
            if _namespace(key) is not None:
                findings.append(_finding("CP5A-NAMESPACE", "CP5A-NAMESPACE", "foreign attribute namespace forbidden", path=path))
                continue
            attribute = key.rsplit("}", 1)[-1]
            if attribute.lower().startswith("on"):
                findings.append(_finding("CP5A-ATTRIBUTES", "CP5A-ATTRIBUTE-ALLOWLIST", "event attributes are forbidden", path=path))
            elif attribute not in self.attributes[name]:
                if attribute.startswith("data-") and FORBIDDEN_PROVENANCE.search(attribute):
                    findings.append(_finding("CP5A-PROVENANCE", "CP5A-SCIENTIFIC-PROVENANCE-BOUNDARY", "scientific provenance cannot be embedded", path=path))
                elif attribute == "data-raster-fallback":
                    findings.append(_finding("CP5A-RESOURCE", "CP5A-RASTER-FALLBACK", "silent raster fallback marker forbidden", path=path))
                else:
                    findings.append(_finding("CP5A-ATTRIBUTES", "CP5A-ATTRIBUTE-ALLOWLIST", f"attribute {attribute} not allowed on {name}", path=path))
            if FORBIDDEN_PROVENANCE.search(attribute) and attribute not in {"data-thesis-svg-version", "data-thesis-figure-id", "data-semantic-role"}:
                findings.append(_finding("CP5A-PROVENANCE", "CP5A-SCIENTIFIC-PROVENANCE-BOUNDARY", "scientific provenance cannot be embedded", path=path))
            if PRIVATE_PATH.search(value):
                findings.append(_finding("CP5A-RESOURCE", "CP5A-RESOURCE-POLICY", "unsafe or remote resource reference", path=path))
            if attribute == "data-visual-class" and not is_root:
                findings.append(_finding("CP5A-VISUAL-CLASS", "CP5A-VISUAL-CLASS-PLACEMENT", "visual class allowed on root only", path=path))
            if attribute == "data-semantic-role" and is_root:
                findings.append(_finding("CP5A-ROLES", "CP5A-SEMANTIC-ATTRIBUTE-PLACEMENT", "semantic role allowed on object only", path=path))
        object_id = element.get("id")
        role = element.get("data-semantic-role")
        if object_id:
            if not OBJECT_ID_RE.fullmatch(object_id) or object_id in ids:
                findings.append(_finding("CP5A-OBJECT-IDS", "CP5A-OBJECT-ID", "object ID malformed or duplicate", path=path, object_id=object_id if OBJECT_ID_RE.fullmatch(object_id or "") else None))
            ids.add(object_id)
        if role is not None:
            record = self.role_map.get(role)
            if record is None:
                findings.append(_finding("CP5A-ROLES", "CP5A-ROLE-REGISTRY", "semantic role is unregistered", path=path, object_id=object_id))
            elif name not in record["allowed_elements"]:
                findings.append(_finding("CP5A-ROLES", "CP5A-ROLE-ELEMENT-COMPATIBILITY", "role incompatible with element", path=path, object_id=object_id))
            else:
                if "any" not in record["allowed_visual_classes"] and visual_class not in record["allowed_visual_classes"]:
                    findings.append(_finding("CP5A-ROLES", "CP5A-ROLE-VISUAL-CLASS", "role incompatible with Figure Spec visual class", path=path, object_id=object_id))
                if record["addressable"] and not object_id:
                    findings.append(_finding("CP5A-OBJECT-IDS", "CP5A-OBJECT-ID", "addressable role requires object ID", path=path))
                if not record["children_allowed"] and list(element):
                    findings.append(_finding("CP5A-ROLES", "CP5A-ROLE-CHILD-POLICY", "role does not permit child nodes", path=path, object_id=object_id))
        self._validate_geometry(name, element, path, findings)
        self._validate_reference(name, element, path, findings)

    def _validate_geometry(self, name: str, element: ET.Element, path: str, findings: list[dict[str, Any]]) -> None:
        for attr in {"x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2", "stroke-width", "font-size", "dx", "dy", "markerWidth", "markerHeight", "refX", "refY"} & set(element.attrib):
            number = _number(element.attrib[attr])
            if number is None or (attr in {"width", "height", "r", "rx", "ry", "markerWidth", "markerHeight"} and number <= 0):
                findings.append(_finding("CP5A-NUMERICS", "CP5A-NUMERIC-POLICY", f"invalid numeric {attr}", path=path))
        if name in {"polyline", "polygon"} and not self._valid_points(element.get("points", ""), minimum_pairs=2 if name == "polyline" else 3):
            findings.append(_finding("CP5A-POINTS", "CP5A-POINTS-GRAMMAR", "points grammar invalid", path=path))
        if name == "path" and not self._valid_path(element.get("d", "")):
            findings.append(_finding("CP5A-PATH", "CP5A-PATH-GRAMMAR", "path grammar invalid", path=path))
        transform = element.get("transform")
        if transform and not self._valid_transform(transform):
            findings.append(_finding("CP5A-TRANSFORM", "CP5A-TRANSFORM-GRAMMAR", "transform grammar invalid", path=path))

    @staticmethod
    def _valid_points(value: str, *, minimum_pairs: int) -> bool:
        tokens = [item for item in re.split(r"[\s,]+", value.strip()) if item]
        return len(tokens) >= minimum_pairs * 2 and len(tokens) % 2 == 0 and all(_number(item) is not None for item in tokens)

    @staticmethod
    def _valid_path(value: str) -> bool:
        if not value or not re.fullmatch(r"(?:[MmLlHhVvCcSsQqTtAaZz]|[-+0-9eE.,\s])+", value):
            return False
        tokens = [token for token in PATH_TOKEN_RE.findall(value) if token != ","]
        arity = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
        command: str | None = None
        groups: list[list[str]] = []
        current: list[str] = []
        for token in tokens + ["!"]:
            if token.isalpha() or token == "!":
                if command is not None:
                    groups.append(current)
                    need = arity[command.upper()]
                    if (need == 0 and current) or (need and (not current or len(current) % need)):
                        return False
                    if command.upper() == "M" and len(current) < 2:
                        return False
                    if command.upper() == "A":
                        for offset in range(0, len(current), 7):
                            if current[offset + 3] not in {"0", "1"} or current[offset + 4] not in {"0", "1"}:
                                return False
                if token == "!":
                    break
                command, current = token, []
            elif command is None or _number(token) is None:
                return False
            else:
                current.append(token)
        return bool(groups) and groups[0] and command is not None

    @staticmethod
    def _valid_transform(value: str) -> bool:
        parts = re.findall(r"[A-Za-z]+\([^)]*\)", value)
        if not parts or " ".join(parts) != value.strip():
            return False
        arity = {"translate": {1, 2}, "scale": {1, 2}, "rotate": {1, 3}, "matrix": {6}}
        for part in parts:
            name, raw = part.split("(", 1)
            if name not in arity:
                return False
            values = [item for item in re.split(r"[\s,]+", raw[:-1].strip()) if item]
            if len(values) not in arity[name] or any(_number(item) is None for item in values):
                return False
        return True

    def _validate_reference(self, name: str, element: ET.Element, path: str, findings: list[dict[str, Any]]) -> None:
        for attr in ("href", "clip-path", "marker-start", "marker-end"):
            reference = element.get(attr)
            if not reference:
                continue
            safe_local = reference.startswith("url(#obj-") or reference.startswith("#obj-")
            safe_bundle = re.fullmatch(r"assets/[a-z0-9][a-z0-9._/-]*", reference or "") is not None and ".." not in reference
            safe_data = reference.startswith("data:image/png;base64,") and len(reference) <= 32768
            if not (safe_local or safe_bundle or safe_data):
                findings.append(_finding("CP5A-RESOURCES", "CP5A-RESOURCE-POLICY", f"unsafe {attr} reference", path=path))
            if "private" in reference.lower() or reference.lower().endswith((".pptx", ".pptm", ".ppsx")):
                findings.append(_finding("CP5A-RESOURCES", "CP5A-PRIVATE-LEAKAGE", "private-like resource name forbidden", path=path))

    def _report(self, figure_id: str, source_hash: str, canonical: dict[str, str] | None, findings: list[dict[str, Any]], metadata_equal: bool) -> dict[str, Any]:
        identity = {"schema_version": "1.0.0", "figure_id": figure_id if re.fullmatch(r"FIG[0-9]{3,}", figure_id) else "FIG000", "profile_id": self.profile["profile_id"], "profile_version": self.profile["schema_version"], "canonicalization_version": CANONICALIZATION_VERSION, "source_sha256": source_hash, "canonical_sha256": canonical["canonical_sha256"] if canonical else source_hash, "canonical_svg": canonical["canonical_svg"] if canonical else "<invalid/>"}
        return {"schema_version": "1.0.0", "qa_id": "SSVG-QA-001", "figure_id": identity["figure_id"], "aggregate_status": "pass" if not findings else "fail", "findings": findings, "identity": identity, "metadata_invisibility": {"status": "pass" if metadata_equal else "fail", "method": "static_presentation_ast_comparison", "presentation_ast_equal": metadata_equal}}


def candidate_state(root: Path | None = None) -> dict[str, Any]:
    root = root or ROOT
    candidates = [
        ("cp4:schema:figure-production-plan", root / "thesis-deck-system" / "schemas" / "figure-production-plan.schema.json"),
        ("cp4:schema:scientific-figure-spec", root / "thesis-deck-system" / "schemas" / "scientific-figure-spec.schema.json"),
        ("cp4:artifact:figure-production-plans", root / "thesis-deck-system" / "artifacts" / "phase3" / "figure-production-plans.json"),
        ("cp4:artifact:scientific-figure-specs", root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-figure-specs.json"),
        ("cp4:skill-routing", root / "thesis-deck-system" / "skill-routing.yaml"),
        ("cp5a:source", Path(__file__)),
        ("cp5a:source:contracts", Path(__file__).with_name("contracts.py")),
        ("cp5a:test:scientific-svg", root / "packages" / "thesis-deck-system" / "tests" / "unit" / "test_phase3_cp5a_scientific_svg.py"),
        ("cp5a:test:privacy-regression", root / "packages" / "thesis-deck-system" / "tests" / "unit" / "test_phase3_checkpoint1.py"),
        ("cp5a:privacy:approved-scanner", Path(__file__).with_name("phase3_checkpoint3.py")),
        ("cp5a:privacy:scanner", Path(__file__).with_name("phase3_privacy.py")),
        ("cp5a:profile", root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-svg-profile.json"),
        ("cp5a:roles", root / "thesis-deck-system" / "artifacts" / "phase3" / "semantic-svg-role-registry.json"),
        ("cp5a:synthetic-corpus", root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-svg-synthetic-corpus.json"),
    ]
    cp5a_schemas = (
        "scientific-svg-profile.schema.json", "semantic-svg-role-registry.schema.json",
        "static-svg-qa-report.schema.json", "scientific-svg-identity.schema.json",
        "checkpoint-5a-execution-evidence.schema.json", "checkpoint-5a-qa.schema.json",
        "scientific-svg-synthetic-corpus.schema.json", "checkpoint-5a-report-facts.schema.json",
    )
    candidates += [(f"cp5a:schema:{name}", root / "thesis-deck-system" / "schemas" / name) for name in cp5a_schemas]
    candidates += [(f"cp5a:skill:{name}", root / "thesis-deck-system" / "skills" / name / "SKILL.md") for name in ("scientific-svg-authoring", "semantic-svg-governor")]
    hashes = {name: sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest() for name, path in candidates}
    composite = _sha(json.dumps(hashes, sort_keys=True, separators=(",", ":")))
    return {"component_hashes": hashes, "current_candidate_hash": composite}


def validate_tested_candidate_state(tested: dict[str, Any], current: dict[str, Any]) -> bool:
    return tested.get("current_candidate_hash") == current.get("current_candidate_hash") and tested.get("component_hashes") == current.get("component_hashes")


def author_svg_for_spec(source: str, figure_spec: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    """The only CP5-A authoring handoff: validation cannot be bypassed."""
    result = ScientificSvgValidator.load_default(root or ROOT).validate(source, figure_spec=figure_spec)
    if result["aggregate_status"] != "pass":
        raise ScientificSvgError("Scientific SVG authoring handoff blocked by static validator")
    return {"canonical_svg": result["identity"]["canonical_svg"], "identity": result["identity"], "qa": result}


def validate_synthetic_corpus(root: Path | None = None, corpus: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate the language-only corpus; no fixture is scientific evidence."""
    root = root or ROOT
    corpus = corpus or json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-svg-synthetic-corpus.json").read_text(encoding="utf-8"))
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True)
    registry.validate("scientific-svg-synthetic-corpus", corpus)
    specs = {item["figure_id"]: item for item in json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-figure-specs.json").read_text(encoding="utf-8"))}
    validator = ScientificSvgValidator.load_default(root)
    fixtures = []
    for fixture in corpus["fixtures"]:
        binding = fixture["binding"]
        spec = specs.get(binding["figure_spec_ref"])
        binding_valid = (spec is not None and binding["fixture_id"] == fixture["fixture_id"] and binding["figure_id"] == binding["figure_spec_ref"] and binding["visual_class"] == spec.get("visual_class"))
        qa = validator.validate(fixture["svg"], figure_spec=spec) if binding_valid else {"aggregate_status": "fail", "identity": {"canonical_sha256": "0" * 64}}
        fixtures.append({"fixture_id": fixture["fixture_id"], "coverage": fixture["coverage"], "binding": binding, "binding_status": "pass" if binding_valid else "fail", "status": qa["aggregate_status"], "canonical_sha256": qa["identity"]["canonical_sha256"]})
    ids = [item["fixture_id"] for item in fixtures]
    return {"corpus_id": corpus["corpus_id"], "fixture_count": len(fixtures), "fixtures": fixtures, "binding_count": len(fixtures), "ambiguous_bindings": len(ids) - len(set(ids)), "aggregate_status": "pass" if all(item["status"] == "pass" and item["binding_status"] == "pass" for item in fixtures) and len(ids) == 10 and len(ids) == len(set(ids)) else "fail"}


def build_cp5a_artifacts(root: Path | None = None, *, tested_candidate_hash: str | None, tested_in_disposable_worktree: bool, tests_passed: int = 0, tests_failed: int = 1, privacy_config: dict[str, Any] | None = None, private_access_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    root = root or ROOT
    validator = ScientificSvgValidator.load_default(root)
    fixture = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" data-thesis-svg-version="1.0.0" data-thesis-figure-id="FIG001"><rect id="obj-panel" data-semantic-role="panel" x="1" y="1" width="8" height="8" fill="#eeeeee"/><text id="obj-title" data-semantic-role="title" x="2" y="5" font-family="synthetic-test-sans" font-size="2">量測結果 / Result</text></svg>'
    spec = json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-figure-specs.json").read_text(encoding="utf-8"))[0]
    fixture_result = validator.validate(fixture, figure_spec=spec)
    corpus_result = validate_synthetic_corpus(root)
    state = candidate_state(root)
    equal = tested_candidate_hash == state["current_candidate_hash"]
    # Reuse the approved repository/staged scanner.  Its private configuration
    # remains a local execution input; only its hash and aggregate findings
    # cross into CP5-A evidence.
    from .phase3_checkpoint3 import _approved_privacy_scan
    privacy_passed, privacy_evidence = _approved_privacy_scan(privacy_config)
    access = private_access_evidence or {}
    access_keys = ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")
    access_bound = all(isinstance(access.get(key), int) and access[key] >= 0 for key in access_keys) and bool(access.get("execution_id"))
    private_access_passed = access_bound and all(access[key] == 0 for key in access_keys)
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True)
    plans = json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "figure-production-plans.json").read_text(encoding="utf-8"))
    specs = json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "scientific-figure-specs.json").read_text(encoding="utf-8"))
    cp4_freeze_passed = not any(registry.errors("figure-production-plan", plan) for plan in plans) and not any(registry.errors("scientific-figure-spec", spec) for spec in specs)
    namespace_probe = validator.validate('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" data-thesis-svg-version="1.0.0" data-thesis-figure-id="FIG001"><x:rect xmlns:x="urn:blocked"/></svg>', figure_spec=spec)
    geometry_probe = validator.validate('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" data-thesis-svg-version="1.0.0" data-thesis-figure-id="FIG001"><path id="obj-branch" data-semantic-role="branch" d="M 0 0 L 1"/></svg>', figure_spec=spec)
    resource_probe = validator.validate('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" data-thesis-svg-version="1.0.0" data-thesis-figure-id="FIG001"><image id="obj-image" data-semantic-role="image" x="0" y="0" width="1" height="1" href="https://blocked.invalid/x"/></svg>', figure_spec=spec)
    profile_authority = set(validator.attributes) == set(validator.profile["allowed_elements"]) and all(validator.profile["grammar_bindings"][kind] in REGISTERED_GRAMMARS[kind] for kind in REGISTERED_GRAMMARS)
    namespace_passed = namespace_probe["aggregate_status"] == "fail"
    geometry_passed = geometry_probe["aggregate_status"] == "fail"
    resource_passed = resource_probe["aggregate_status"] == "fail"
    cjk_passed = "量測結果" in fixture_result["identity"]["canonical_svg"]
    canonical_passed = canonicalize_svg(fixture)["canonical_svg"] == canonicalize_svg(fixture.replace("><", ">\n<"))["canonical_svg"]
    checks = [
        ("CP5A-CP4-FREEZE", cp4_freeze_passed, [{"name":"cp4_plan_count","integer":len(plans)},{"name":"cp4_spec_count","integer":len(specs)},{"name":"cp4_inputs_valid","boolean":cp4_freeze_passed}]),
        ("CP5A-PROFILE-CODE-AUTHORITY", profile_authority, [{"name":"profile_element_contract_count","integer":len(validator.attributes)},{"name":"registered_grammar_count","integer":len(REGISTERED_GRAMMARS)}]),
        ("CP5A-SCHEMA-CLOSURE", not registry.errors("scientific-svg-profile", validator.profile) and not registry.errors("semantic-svg-role-registry", validator.roles), [{"name":"profile_schema_valid","boolean":not registry.errors("scientific-svg-profile", validator.profile)},{"name":"role_schema_valid","boolean":not registry.errors("semantic-svg-role-registry", validator.roles)}]),
        ("CP5A-NAMESPACE-POLICY", namespace_passed, [{"name":"foreign_namespace_rejected","boolean":namespace_passed}]),
        ("CP5A-GEOMETRY-GRAMMAR", geometry_passed, [{"name":"malformed_path_rejected","boolean":geometry_passed}]),
        ("CP5A-RESOURCE-POLICY", resource_passed, [{"name":"remote_resource_rejected","boolean":resource_passed}]),
        ("CP5A-STATIC-VALIDATOR", fixture_result["aggregate_status"] == "pass" and corpus_result["aggregate_status"] == "pass", [{"name":"fixture_status","text":fixture_result["aggregate_status"]},{"name":"synthetic_fixture_count","integer":corpus_result["fixture_count"]}]),
        ("CP5A-METADATA-INVISIBILITY", fixture_result["metadata_invisibility"]["presentation_ast_equal"], [{"name":"static_ast_equal","boolean":fixture_result["metadata_invisibility"]["presentation_ast_equal"]}]),
        ("CP5A-CJK-EDITABLE-TEXT", cjk_passed, [{"name":"cjk_text_preserved","boolean":cjk_passed}]),
        ("CP5A-CANONICALIZATION", canonical_passed, [{"name":"formatting_normalization_deterministic","boolean":canonical_passed}]),
        ("CP5A-SYNTHETIC-CORPUS", corpus_result["aggregate_status"] == "pass" and corpus_result["binding_count"] == 10 and corpus_result["ambiguous_bindings"] == 0, [{"name":"fixture_binding_count","integer":corpus_result["binding_count"]},{"name":"ambiguous_bindings","integer":corpus_result["ambiguous_bindings"]}]),
        ("CP5A-REPOSITORY-STAGED-PRIVACY", privacy_passed, [{"name":"repository_scan_executed","boolean":privacy_evidence["repository_scan_executed"]},{"name":"staged_scan_executed","boolean":privacy_evidence["staged_scan_executed"]},{"name":"repository_findings","integer":privacy_evidence["repository_findings"]},{"name":"staged_findings","integer":privacy_evidence["staged_findings"]},{"name":"privacy_configuration_hash","hash":privacy_evidence["configuration_hash"]}]),
        ("CP5A-CANDIDATE-REGRESSION", equal and tested_in_disposable_worktree and tests_failed == 0, [{"name":"candidate_hash_equal","boolean":equal},{"name":"disposable_worktree","boolean":tested_in_disposable_worktree},{"name":"tests_failed","integer":tests_failed}]),
        ("CP5A-PRIVATE-ACCESS", private_access_passed, [{"name":"execution_record_bound","boolean":access_bound},{"name":"private_alias_resolution_attempts","integer":access.get("private_alias_resolution_attempts", -1)},{"name":"private_source_open_attempts","integer":access.get("private_source_open_attempts", -1)},{"name":"private_render_attempts","integer":access.get("private_render_attempts", -1)}]),
    ]
    owning = [{"check_id": item[0], "status": "pass" if item[1] else "fail", "evidence": {"facts": item[2]}} for item in checks]
    aggregate = "pass" if all(item["status"] == "pass" for item in owning) else "fail"
    execution = {"schema_version":"1.0.0","execution_id":"CP5A-EXEC-001","private_alias_resolution_attempts":access.get("private_alias_resolution_attempts"),"private_source_open_attempts":access.get("private_source_open_attempts"),"private_render_attempts":access.get("private_render_attempts"),"private_access_evidence":access or None,"candidate_state":{**state,"tested_candidate_hash":tested_candidate_hash,"candidate_hash_equal":equal,"disposable_worktree":tested_in_disposable_worktree,"tests_passed":tests_passed,"tests_failed":tests_failed},"privacy_scan":privacy_evidence,"owning_checks":owning}
    status_by_check = {item["check_id"]: item["status"] for item in owning}
    status = lambda *check_ids: "pass" if all(status_by_check[name] == "pass" for name in check_ids) else "fail"
    qa = {"schema_version":"1.0.0","qa_id":"CP5A-QA-001","aggregate_status":aggregate,"owning_check_refs":[item["check_id"] for item in owning],"status_dimensions":{"scientific_svg_language":status("CP5A-PROFILE-CODE-AUTHORITY","CP5A-SCHEMA-CLOSURE"),"static_svg_validator":status("CP5A-STATIC-VALIDATOR","CP5A-NAMESPACE-POLICY","CP5A-GEOMETRY-GRAMMAR"),"semantic_governance":status("CP5A-METADATA-INVISIBILITY"),"cjk_static_text":status("CP5A-CJK-EDITABLE-TEXT"),"resource_policy":status("CP5A-RESOURCE-POLICY","CP5A-REPOSITORY-STAGED-PRIVACY"),"canonicalization_hash":status("CP5A-CANONICALIZATION","CP5A-METADATA-INVISIBILITY"),"synthetic_corpus":status("CP5A-SYNTHETIC-CORPUS"),"native_capability_registry":"not_run","static_figure_critic":"not_run","production_figure_rendering":"not_run","render_critic":"not_run","a01_a18_calibration":"not_run","drawingml_compiler":"not_run","template_reconstruction":"not_run","acceptance_deck":"not_run","production_group_meeting_ready":False}}
    return {"execution": execution, "qa": qa, "fixture_qa": fixture_result, "corpus": corpus_result}


def write_cp5a_artifacts(root: Path | None = None, *, tested_candidate_hash: str, tested_in_disposable_worktree: bool, tests_passed: int, tests_failed: int, privacy_config: dict[str, Any] | None = None, private_access_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Persist only execution-derived CP5-A evidence, never a rendered figure."""
    root = root or ROOT
    outputs = build_cp5a_artifacts(
        root,
        tested_candidate_hash=tested_candidate_hash,
        tested_in_disposable_worktree=tested_in_disposable_worktree,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        privacy_config=privacy_config,
        private_access_evidence=private_access_evidence,
    )
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True)
    registry.validate("checkpoint-5a-execution-evidence", outputs["execution"])
    registry.validate("checkpoint-5a-qa", outputs["qa"])
    registry.validate("static-svg-qa-report", outputs["fixture_qa"])
    paths = {"checkpoint-5a-execution-evidence.json": outputs["execution"], "checkpoint-5a-qa.json": outputs["qa"], "synthetic-static-svg-qa.json": outputs["fixture_qa"]}
    for name, value in paths.items():
        (root / "thesis-deck-system" / "artifacts" / "phase3" / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return outputs
