"""Checkpoint 2: controlled read-only private structural profiling."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree as ET

from .image_review import preflight_image_review
from .phase3_privacy import RepositoryPrivacyScanner
from .contracts import SchemaRegistry


AUTHORIZED_ALIASES = (
    "private://template_primary_1",
    "private://layout_exemplar_2",
    "private://template_primary_3",
)
SHELL_ALIASES = {"private://template_primary_1", "private://template_primary_3"}
BODY_ALIAS = "private://layout_exemplar_2"
_NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


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


@dataclass
class Checkpoint2ExecutionEvidence:
    private_root_status: str = "missing"
    pre_open_gates: dict[str, str] = field(default_factory=dict)
    alias_attempts: list[str] = field(default_factory=list)
    alias_results: dict[str, str] = field(default_factory=dict)
    source_sessions: dict[str, dict] = field(default_factory=dict)
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

    def record_pre_open_gate(self, gate_id: str, result: str) -> None:
        if gate_id not in {"CP2-PRE-1", "CP2-PRE-2"} or result not in {"pass", "fail"}:
            raise Checkpoint2PolicyViolation("invalid Checkpoint 2 pre-open gate")
        self.pre_open_gates[gate_id] = result

    @property
    def authorized_source_sessions(self) -> int:
        return len(self.source_sessions)

    def payload(self) -> dict:
        return {
            "schema_version": "1.0.0", "evidence_id": "CP2-EXEC-001",
            "pre_open_gates": dict(sorted(self.pre_open_gates.items())),
            "alias_attempts": list(self.alias_attempts), "alias_results": dict(sorted(self.alias_results.items())),
            "source_sessions": dict(sorted(self.source_sessions.items())),
            "unauthorized_attempts": self.unauthorized_attempts,
            "private_renders_created": self.private_renders_created,
            "private_renders_deleted": self.private_renders_deleted,
            "private_renders_retained": self.private_renders_retained,
            "private_qualitative_review_status": self.private_qualitative_review_status,
            "forbidden_export_counts": self.forbidden_export_counts,
            "privacy_scan_status": self.privacy_scan_status,
            "private_root_status": self.private_root_status,
            "privacy_scan_total_findings": self.privacy_scan_total_findings,
            "approved_legacy_exceptions": list(self.approved_legacy_exceptions),
            "unexcepted_findings": self.unexcepted_findings,
        }

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ResolvedPrivateAlias:
    alias_uri: str
    _path: Path
    _private_root: Path
    _execution: Checkpoint2ExecutionEvidence | None

    def open_read_only(self) -> "ReadOnlyPrivateSourceSession":
        if self._execution:
            self._execution.alias_attempts.append(f"open:{self.alias_uri}")
        path = self._path
        try:
            if not path.is_file():
                raise Checkpoint2PolicyViolation("private source is not a regular file")
            with zipfile.ZipFile(path, "r") as package:
                names = set(package.namelist())
                if "[Content_Types].xml" not in names or "ppt/presentation.xml" not in names or not any(name.startswith("ppt/slides/") and name.endswith(".xml") for name in names):
                    raise Checkpoint2PolicyViolation("private source is not a valid OOXML PPTX package")
        except zipfile.BadZipFile as error:
            raise Checkpoint2PolicyViolation("private source is not a valid OOXML PPTX package") from error
        return ReadOnlyPrivateSourceSession(self.alias_uri, path, self._private_root, self._execution)


class LocalPrivateAliasResolver:
    """Resolves stable aliases from caller-supplied ignored local configuration only."""

    def __init__(self, local_aliases: dict[str, Path | str], *, private_root: Path | str, execution: "Checkpoint2Run | Checkpoint2ExecutionEvidence | None" = None):
        self._paths = {key: Path(value) for key, value in local_aliases.items()}
        self._private_root = Path(private_root)
        self._execution = execution.evidence if isinstance(execution, Checkpoint2Run) else execution

    def resolve(self, alias_uri: str) -> ResolvedPrivateAlias:
        if self._execution:
            self._execution.alias_attempts.append(alias_uri)
        if alias_uri not in AUTHORIZED_ALIASES:
            if self._execution:
                self._execution.unauthorized_attempts += 1
            raise Checkpoint2PolicyViolation("unrecognized or arbitrary private source request")
        if self._execution and set(self._execution.pre_open_gates) != {"CP2-PRE-1", "CP2-PRE-2"} or self._execution and any(value != "pass" for value in self._execution.pre_open_gates.values()):
            raise Checkpoint2PolicyViolation("Checkpoint 2 pre-open gates have not passed")
        path = self._paths.get(alias_uri)
        if path is None:
            if self._execution:
                self._execution.alias_results[alias_uri] = "failed"
            raise Checkpoint2PolicyViolation("stable alias is unresolved in local-only configuration")
        if self._execution:
            self._execution.alias_results[alias_uri] = "resolved"
        return ResolvedPrivateAlias(alias_uri, path, self._private_root, self._execution)


class ReadOnlyPrivateSourceSession:
    """Exposes only data-minimized structural measurement, never a file handle."""

    def __init__(self, alias_uri: str, path: Path, private_root: Path, execution: Checkpoint2ExecutionEvidence | None):
        self.alias_uri, self._path, self._private_root, self._execution = alias_uri, path, private_root, execution

    def profile_structurally(self, authority: str) -> dict:
        if authority not in {"shell", "body"} or (authority == "shell") != (self.alias_uri in SHELL_ALIASES):
            raise Checkpoint2PolicyViolation("exemplar authority mismatch")
        source_sha = _hash_file(self._path)
        with zipfile.ZipFile(self._path, "r") as package:
            names = package.namelist()
            presentation = ET.fromstring(package.read("ppt/presentation.xml"))
            size = presentation.find("p:sldSz", _NS)
            width = int(size.get("cx")) if size is not None else 0
            height = int(size.get("cy")) if size is not None else 0
            slides = sorted(name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name))
            slide_profiles = [self._slide_profile(ET.fromstring(package.read(name)), width, height) for name in slides]
            masters = [name for name in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name)]
            layouts = [name for name in names if re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", name)]
        base = {
            "alias_uri": self.alias_uri, "source_sha256": source_sha, "profile_id": _safe_id(self.alias_uri),
            "slide_size": {"width": round(width / 914400, 6), "height": round(height / 914400, 6)},
            "slide_count": len(slides), "render_count": 0,
        }
        if authority == "shell":
            profile = {**base, "master_count": len(masters), "layout_count": len(layouts), "shell_primitives": self._shell_primitives(slide_profiles)}
        else:
            profile = {**base, "candidate_families": [self._classify_slide(slide) for slide in slide_profiles], "body_measurements": slide_profiles}
        self._private_root.mkdir(parents=True, exist_ok=True)
        (self._private_root / f"{_safe_id(self.alias_uri).lower()}-raw.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        if self._execution:
            self._execution.source_sessions[self.alias_uri] = {"ooxml_valid": True, "source_sha256": source_sha, "slide_count": len(slides), "descriptor_count": len(profile.get("shell_primitives", profile.get("body_measurements", [])))}
        return profile

    @staticmethod
    def _slide_profile(slide: ET.Element, width: int, height: int) -> dict:
        shapes = []
        for element in slide.findall(".//p:sp", _NS) + slide.findall(".//p:pic", _NS) + slide.findall(".//p:graphicFrame", _NS) + slide.findall(".//p:cxnSp", _NS):
            xfrm = element.find(".//a:xfrm", _NS)
            off, ext = (xfrm.find("a:off", _NS), xfrm.find("a:ext", _NS)) if xfrm is not None else (None, None)
            if off is None or ext is None or not width or not height:
                continue
            kind = "picture" if element.tag.endswith("pic") else "table_or_chart" if element.tag.endswith("graphicFrame") else "line" if element.tag.endswith("cxnSp") else "text_region" if element.find("p:txBody", _NS) is not None else "native_shape"
            shapes.append({"kind": kind, "x": round(int(off.get("x")) / width, 6), "y": round(int(off.get("y")) / height, 6), "w": round(int(ext.get("cx")) / width, 6), "h": round(int(ext.get("cy")) / height, 6)})
        return {"shape_count": len(shapes), "shapes": shapes, "text_area_ratio": round(sum(item["w"] * item["h"] for item in shapes if item["kind"] == "text_region"), 6), "figure_area_ratio": round(sum(item["w"] * item["h"] for item in shapes if item["kind"] in {"picture", "table_or_chart", "native_shape"}), 6)}

    @staticmethod
    def _shell_primitives(slides: list[dict]) -> list[dict]:
        return [{"primitive_id": f"SHELL-{index + 1:03}", "shape_count": slide["shape_count"], "safe_content_bounds": {"x": 0.05, "y": 0.12, "w": 0.9, "h": 0.78}} for index, slide in enumerate(slides)]

    @staticmethod
    def _classify_slide(slide: dict) -> dict:
        shapes = slide["shapes"]
        pictures = sum(item["kind"] == "picture" for item in shapes)
        family = "photo_schematic" if pictures and slide["text_area_ratio"] else "other_insufficient_structural_evidence"
        return {"family": family, "shape_count": slide["shape_count"], "figure_area_ratio": slide["figure_area_ratio"], "text_area_ratio": slide["text_area_ratio"]}


def _sanitize_descriptor(raw: dict, *, expected_aliases: set[str], allowed: set[str]) -> dict:
    if set(raw) != allowed or raw.get("alias_uri") not in expected_aliases:
        raise Checkpoint2PolicyViolation("unknown, forbidden, or authority-mismatched sanitized descriptor field")
    if not isinstance(raw.get("source_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", raw["source_sha256"]):
        raise Checkpoint2PolicyViolation("descriptor source hash is invalid")
    if any(token in json.dumps(raw).casefold() for token in ("\\\\", "d:/", "/mnt/", "http://", "https://", "<relationship")):
        raise Checkpoint2PolicyViolation("descriptor contains prohibited private material")
    return json.loads(json.dumps(raw))


def sanitize_shell_descriptor(raw: dict) -> dict:
    return _sanitize_descriptor(raw, expected_aliases=SHELL_ALIASES, allowed={"alias_uri", "source_sha256", "profile_id", "slide_size", "master_count", "layout_count", "shell_primitives", "slide_count"})


def sanitize_body_descriptor(raw: dict) -> dict:
    return _sanitize_descriptor(raw, expected_aliases={BODY_ALIAS}, allowed={"alias_uri", "source_sha256", "profile_id", "slide_size", "slide_count", "candidate_families", "body_measurements"})


@dataclass
class Checkpoint2Run:
    evidence: Checkpoint2ExecutionEvidence
    private_root: Path

    @classmethod
    def start(cls, *, pre_open_passed: bool, private_root: Path | str) -> "Checkpoint2Run":
        evidence = Checkpoint2ExecutionEvidence()
        result = "pass" if pre_open_passed else "fail"
        evidence.record_pre_open_gate("CP2-PRE-1", result)
        evidence.record_pre_open_gate("CP2-PRE-2", result)
        evidence.privacy_scan_status = result
        return cls(evidence, Path(private_root))

    def private_render_review(self, provider: dict) -> str:
        full = {"provider_id": "synthetic_private_provider", "image_capable": provider.get("image_capable", False), "hash_binding_supported": provider.get("hash_binding_supported", False), "private_content_allowed": provider.get("private_content_allowed", False), "approved_for_private_exemplars": provider.get("approved_for_private_exemplars", False), "egress_mode": provider.get("egress_mode", "blocked"), "retention_class": provider.get("retention_class", "blocked"), "supported_input_forms": provider.get("supported_input_forms", [])}
        preflight = preflight_image_review(full, private_reference=True)
        if preflight.status != "approved":
            self.evidence.private_qualitative_review_status = "blocked_visual_review"
            return self.evidence.private_qualitative_review_status
        self.evidence.private_renders_created += 1
        self.evidence.private_renders_deleted += 1
        self.evidence.private_qualitative_review_status = "reviewed_ephemerally"
        return self.evidence.private_qualitative_review_status

    def qa_record(self) -> dict:
        payload = self.evidence.payload()
        processed = set(self.evidence.source_sessions)
        aggregate = "pass" if set(payload["pre_open_gates"]) == {"CP2-PRE-1", "CP2-PRE-2"} and all(value == "pass" for value in payload["pre_open_gates"].values()) and self.evidence.private_root_status == "pass" and processed == set(AUTHORIZED_ALIASES) and self.evidence.unauthorized_attempts == 0 and self.evidence.private_renders_retained == 0 and all(value == 0 for value in self.evidence.forbidden_export_counts.values()) and self.evidence.privacy_scan_status == "pass" else "fail"
        return {"schema_version": "1.0.0", "checkpoint_id": "PHASE_3_CHECKPOINT_2", "execution_evidence_id": payload["evidence_id"], "execution_evidence_sha256": self.evidence.sha256(), "execution_evidence": payload, "aggregate_status": aggregate}


def validate_checkpoint2_qa(record: dict) -> list[str]:
    evidence = record.get("execution_evidence")
    if not isinstance(evidence, dict):
        return ["CP2-QA-EXECUTION-EVIDENCE-MISSING"]
    errors = []
    actual_hash = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if record.get("execution_evidence_id") != evidence.get("evidence_id") or record.get("execution_evidence_sha256") != actual_hash:
        errors.append("CP2-QA-EXECUTION-EVIDENCE-HASH")
    processed = set(evidence.get("source_sessions", {}))
    aggregate = "pass" if set(evidence.get("pre_open_gates", {})) == {"CP2-PRE-1", "CP2-PRE-2"} and all(value == "pass" for value in evidence.get("pre_open_gates", {}).values()) and evidence.get("private_root_status") == "pass" and processed == set(AUTHORIZED_ALIASES) and evidence.get("unauthorized_attempts") == 0 and evidence.get("private_renders_retained") == 0 and all(value == 0 for value in evidence.get("forbidden_export_counts", {}).values()) and evidence.get("privacy_scan_status") == "pass" else "fail"
    if record.get("aggregate_status") != aggregate:
        errors.append("CP2-QA-AGGREGATE-NONDERIVED")
    return errors


def _production_observation_policy_check() -> None:
    """Execute the production policy with canonical-looking real empirical input."""
    from .contracts import SchemaRegistry
    from .phase3_contracts import canonical_observation_catalogs, validate_observation_visual_binding

    root = Path(__file__).resolve().parents[4]
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True)
    sha = "b" * 64
    card = {"schema_version": "1.0.0", "evidence_id": "E900", "kind": "experimental_measurement", "title": "Policy execution input", "provenance": "verified_empirical", "source": {"source_id": "S900", "uri": "controlled/measurement.dat", "sha256": sha}, "claim_support_refs": [], "claim_contradict_refs": [], "scope": {}, "verification": {"status": "verified"}}
    output = {"schema_version": "3.0.0", "figure_output_id": "FOM900", "figure_id": "FIG900", "figure_type": "scientific_plot", "primary_artifact_kind": "svg_vector", "renderer": "policy_runner", "source_spec_sha256": sha, "provenance_refs": ["E900"], "style_profile_ref": "VSP900", "evidence_status": "empirical", "primary_artifact": {"path": "artifacts/phase3/policy.svg", "sha256": sha, "data_provenance_refs": ["E900"]}, "output_part_lineage": ["generated"]}
    binding = {"observation_id": "OBS900", "empirical_evidence_required": True, "observation_evidence_ref": "E900", "observation_output_ref": "FOM900", "evidence_refs": ["E900"], "auxiliary_visuals": []}
    catalog = canonical_observation_catalogs(registry, [card], [output])
    if validate_observation_visual_binding(binding, catalog=catalog, evidence_policy="production"):
        raise Checkpoint2PolicyViolation("production Observation policy owning check failed")


def build_checkpoint2(*, repository_root: Path | str, local_aliases: dict[str, Path | str], private_root: Path | str, artifact_root: Path | str) -> dict:
    """Run CP2's bounded private flow and persist sanitized public evidence only."""
    root, output_root = Path(repository_root), Path(artifact_root)
    resolver = LocalPrivateAliasResolver(local_aliases, private_root=private_root)
    scanner = RepositoryPrivacyScanner(
        private_root_signatures=[str(path.parent) for path in resolver._paths.values()],
        forbidden_basenames=[path.name for path in resolver._paths.values()],
    )
    run = Checkpoint2Run.start(pre_open_passed=False, private_root=private_root)
    try:
        from .phase3_privacy import PrivateProfileStore
        PrivateProfileStore(private_root, repository_root=root).prepare_for_future_open()
    except Exception:
        run.evidence.private_root_status = "fail"
    else:
        run.evidence.private_root_status = "pass"
    scan_findings, exceptions = scanner.scan_repository_with_legacy_exception(root, forbidden_basenames=[path.name for path in resolver._paths.values()])
    run.evidence.privacy_scan_total_findings = len(scan_findings) + len(exceptions)
    run.evidence.approved_legacy_exceptions = exceptions
    run.evidence.unexcepted_findings = len(scan_findings)
    run.evidence.record_pre_open_gate("CP2-PRE-1", "pass" if not scan_findings else "fail")
    run.evidence.privacy_scan_status = "pass" if not scan_findings else "fail"
    try:
        _production_observation_policy_check()
    except Exception:
        run.evidence.record_pre_open_gate("CP2-PRE-2", "fail")
    else:
        run.evidence.record_pre_open_gate("CP2-PRE-2", "pass")
    if any(result != "pass" for result in run.evidence.pre_open_gates.values()):
        raise Checkpoint2PolicyViolation("Checkpoint 2 pre-open gates failed; private aliases were not resolved")
    resolver._execution = run.evidence
    shell_descriptors: list[dict] = []
    body_descriptor: dict | None = None
    for alias_uri in AUTHORIZED_ALIASES:
        raw = resolver.resolve(alias_uri).open_read_only().profile_structurally("body" if alias_uri == BODY_ALIAS else "shell")
        raw.pop("render_count", None)
        if alias_uri == BODY_ALIAS:
            body_descriptor = sanitize_body_descriptor(raw)
        else:
            shell_descriptors.append(sanitize_shell_descriptor(raw))
    run.private_render_review({"image_capable": True, "approved_for_private_exemplars": False})
    manifest = {"schema_version": "1.0.0", "manifest_id": "SEM001", "exemplars": [{"alias_uri": descriptor["alias_uri"], "source_sha256": descriptor["source_sha256"], "profile_id": descriptor["profile_id"], "authority": "body_composition" if descriptor["alias_uri"] == BODY_ALIAS else "shell"} for descriptor in [*shell_descriptors, body_descriptor] if descriptor]}
    shell_payload = {"schema_version": "1.0.0", "descriptors": shell_descriptors}
    body_payload = {"schema_version": "1.0.0", "descriptor": body_descriptor}
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True)
    for name, value in (("sanitized-exemplar-manifest", manifest), ("sanitized-shell-structural-descriptors", shell_payload), ("sanitized-body-structural-descriptors", body_payload)):
        errors = registry.errors(name, value)
        if errors:
            raise Checkpoint2PolicyViolation(f"sanitized descriptor schema failed: {name}")
    output_root.mkdir(parents=True, exist_ok=True)
    for name, value in (("sanitized-exemplar-manifest.json", manifest), ("sanitized-shell-structural-descriptors.json", shell_payload), ("sanitized-body-structural-descriptors.json", body_payload)):
        (output_root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = run.qa_record()
    if validate_checkpoint2_qa(qa):
        raise Checkpoint2PolicyViolation("Checkpoint 2 QA evidence is inconsistent")
    (output_root / "checkpoint-2-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa
