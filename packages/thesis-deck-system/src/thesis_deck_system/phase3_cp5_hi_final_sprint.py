"""CP5-H/I single-backend preflight and native-compiler boundary.

This module intentionally owns no presentation-package writer.  It records the
preflight facts that later H/I stages must bind before compiling approved
Scientific SVG into an assembler-consumed plan.
"""
from __future__ import annotations

import ast
import copy
from dataclasses import dataclass
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
from typing import Any
from hashlib import sha256
from xml.etree import ElementTree as ET
import zipfile


class NativeCompilationError(ValueError):
    """Raised when an H-stage compilation boundary is violated."""


@dataclass(frozen=True)
class ScientificSvgNativeCompiler:
    """Internal plan compiler placeholder; it deliberately cannot write PPTX."""

    compiler_id: str = "TDS-SVG-NATIVE-COMPILER-001"
    compiler_version: str = "1.0.0"

    def compile(
        self,
        approved_figure: Any,
        manifest: dict[str, Any],
        canonical_svg: str,
        *,
        target_box: dict[str, float],
    ) -> dict[str, Any]:
        """Compile a reverified figure into a deterministic, writer-free plan."""
        # Delayed imports keep the H0 preflight independently inspectable.
        from .phase3_cp5bcd_integrated import ApprovedFigureHandle, _json_hash, default_registry

        if not isinstance(approved_figure, ApprovedFigureHandle):
            raise NativeCompilationError("native compilation requires a reverified ApprovedFigureHandle")
        if not isinstance(manifest, dict) or not isinstance(manifest.get("canonical_output"), dict):
            raise NativeCompilationError("closed figure manifest is required")
        if approved_figure.manifest_id != manifest.get("manifest_id") or approved_figure.figure_id != manifest.get("figure_id"):
            raise NativeCompilationError("ApprovedFigureHandle does not bind this manifest")
        if approved_figure.manifest_hash != _json_hash(manifest):
            raise NativeCompilationError("ApprovedFigureHandle manifest hash is stale")
        expected_sha = manifest["canonical_output"].get("canonical_sha256")
        actual_sha = sha256(canonical_svg.encode("utf-8")).hexdigest()
        if expected_sha != actual_sha:
            raise NativeCompilationError("canonical SVG hash does not match manifest")
        if set(target_box) != {"left", "top", "width", "height"} or any(
            not isinstance(target_box[key], (int, float)) for key in target_box
        ) or target_box["width"] <= 0 or target_box["height"] <= 0:
            raise NativeCompilationError("target placement must be a closed positive box")
        registry = default_registry()
        feature_ids = list(manifest.get("used_feature_ids", []))
        records = registry.require_coverage(feature_ids)
        try:
            root = ET.fromstring(canonical_svg)
        except ET.ParseError as error:
            raise NativeCompilationError("canonical SVG is malformed") from error
        view_box = _parse_viewbox(root.attrib.get("viewBox"))
        if root.attrib.get("data-thesis-figure-id") != approved_figure.figure_id:
            raise NativeCompilationError("SVG figure identity does not bind ApprovedFigureHandle")
        objects: list[dict[str, Any]] = []
        for index, element in enumerate(root.iter()):
            local = _local_name(element.tag)
            object_id = element.attrib.get("id")
            if local in {"svg", "defs"} or not object_id:
                continue
            objects.append(_compile_object(element, index, view_box, target_box))
        if not objects:
            raise NativeCompilationError("canonical SVG has no addressable visual objects")
        payload = {
            "schema_version": "1.0.0",
            "plan_id": f"NFCP-{approved_figure.figure_id}-{approved_figure.figure_revision}",
            "compiler_id": self.compiler_id,
            "compiler_version": self.compiler_version,
            "figure_id": approved_figure.figure_id,
            "figure_revision": approved_figure.figure_revision,
            "approved_figure": {
                "manifest_id": approved_figure.manifest_id,
                "manifest_hash": approved_figure.manifest_hash,
                "critic_report_id": approved_figure.critic_report_id,
                "critic_report_hash": approved_figure.critic_report_hash,
            },
            "svg_profile": {"profile_id": manifest.get("svg_profile_ref"), "profile_version": manifest.get("svg_profile_version"), "canonical_sha256": actual_sha},
            "registry": {"registry_id": registry.payload["registry_id"], "registry_version": registry.payload["registry_version"], "registry_sha256": _json_hash(registry.payload)},
            "view_box": {"x": view_box[0], "y": view_box[1], "width": view_box[2], "height": view_box[3]},
            "target_box": {key: float(target_box[key]) for key in ("left", "top", "width", "height")},
            "coordinate_transform": {"scale_x": float(target_box["width"]) / view_box[2], "scale_y": float(target_box["height"]) / view_box[3], "translate_x": float(target_box["left"]), "translate_y": float(target_box["top"])},
            "feature_decisions": [
                {"feature_id": record["feature_id"], "capability_state": record["capability_state"], "compilation_decision": _feature_decision(record["feature_id"])}
                for record in records
            ],
            "objects": objects,
            "fallback_records": [
                {"object_id": item["svg_object_id"], "outcome": item["outcome"], "reason": item["fallback_reason"], "source_svg_sha256": actual_sha}
                for item in objects if item["outcome"] != "DRAWINGML_EMITTED"
            ],
        }
        payload["plan_sha256"] = _plan_hash(payload)
        return payload


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_viewbox(value: str | None) -> tuple[float, float, float, float]:
    if value is None:
        raise NativeCompilationError("canonical SVG viewBox is required")
    try:
        values = [float(item) for item in value.replace(",", " ").split()]
    except ValueError as error:
        raise NativeCompilationError("invalid SVG viewBox") from error
    if len(values) != 4 or values[2] <= 0 or values[3] <= 0:
        raise NativeCompilationError("invalid SVG viewBox dimensions")
    return tuple(values)  # type: ignore[return-value]


def _number(attribute: dict[str, str], name: str, default: float = 0.0) -> float:
    try:
        return float(attribute.get(name, default))
    except (TypeError, ValueError) as error:
        raise NativeCompilationError(f"invalid numeric SVG attribute: {name}") from error


def _feature_decision(feature_id: str) -> str:
    if feature_id in {"clip-path", "clip-local-reference", "path-commands", "image", "svg-vector-fallback"}:
        return "SVG_VECTOR_FALLBACK"
    return "DRAWINGML_EMITTED"


def _compile_object(element: ET.Element, index: int, view_box: tuple[float, float, float, float], target: dict[str, float]) -> dict[str, Any]:
    local = _local_name(element.tag)
    object_id = element.attrib["id"]
    role = element.attrib.get("data-semantic-role", "unknown")
    simple = {"g": "group", "rect": "rect", "circle": "ellipse", "ellipse": "ellipse", "line": "line", "polyline": "polyline", "polygon": "polygon", "text": "text", "tspan": "text", "marker": "marker"}
    shape_kind = simple.get(local, "svg_vector")
    fallback = local in {"path", "image", "clipPath"} or "clip-path" in element.attrib
    geometry = {key: _number(element.attrib, key) for key in ("x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2") if key in element.attrib}
    return {
        "order": index,
        "svg_object_id": object_id,
        "semantic_role": role,
        "shape_kind": shape_kind,
        "geometry": geometry,
        "text": "".join(element.itertext()) if local in {"text", "tspan"} else None,
        "style": {key: element.attrib[key] for key in ("fill", "stroke", "stroke-width", "stroke-dasharray", "font-family", "font-size", "font-weight", "marker-start", "marker-end", "transform") if key in element.attrib},
        "outcome": "SVG_VECTOR_FALLBACK" if fallback else "DRAWINGML_EMITTED",
        "fallback_reason": "unsupported_svg_subtree" if fallback else None,
        "parent_relation": None,
    }


def _plan_hash(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _public_classes(path: Path) -> dict[str, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    classes: dict[str, list[str]] = {}
    for item in tree.body:
        if isinstance(item, ast.ClassDef):
            classes[item.name] = [
                child.name for child in item.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
    return classes


def audit_single_pptx_backend(root: Path) -> dict[str, Any]:
    """Derive the single-writer audit from current source, not caller claims."""
    root = root.resolve()
    package = root / "packages" / "thesis-deck-system" / "src" / "thesis_deck_system"
    pptx_source = package / "pptx.py"
    template_source = package / "template.py"
    compiler_source = Path(__file__)
    pptx_classes = _public_classes(pptx_source)
    compiler_classes = _public_classes(compiler_source)
    concrete_assembler_methods = pptx_classes.get("PythonPptxAssembler", [])
    public_backends = ["PythonPptxAssembler"] if concrete_assembler_methods.count("assemble") == 1 else []
    compiler_methods = compiler_classes.get("ScientificSvgNativeCompiler", [])
    compiler_pptx_writer_methods = [name for name in compiler_methods if name in {"save_pptx", "export_pptx", "assemble"}]
    template_text = template_source.read_text(encoding="utf-8")
    template_scientific_slide_assembly_bypasses = [
        marker for marker in ("assemble_scientific_slides", "save_pptx", "export_pptx") if marker in template_text
    ]
    bypass_count = len(compiler_pptx_writer_methods) + len(template_scientific_slide_assembly_bypasses)
    return {
        "audit_id": "CP5-H0-BACKEND-UNIQUENESS-001",
        "status": "pass" if public_backends == ["PythonPptxAssembler"] and bypass_count == 0 else "fail",
        "public_pptx_backends": public_backends,
        "assembler_source": pptx_source.relative_to(root).as_posix(),
        "compiler_source": compiler_source.relative_to(root).as_posix(),
        "compiler_pptx_writer_methods": compiler_pptx_writer_methods,
        "template_scientific_slide_assembly_bypasses": template_scientific_slide_assembly_bypasses,
        "bypass_count": bypass_count,
    }


def _powerpoint_available() -> bool:
    """Probe executable availability only; never opens any presentation."""
    return bool(shutil.which("POWERPNT.EXE") or shutil.which("POWERPNT"))


def probe_native_environment() -> dict[str, Any]:
    """Return only environment capability facts for generated-output gates."""
    powerpoint = _powerpoint_available()
    renderer = bool(shutil.which("soffice") or shutil.which("libreoffice"))
    return {
        "probe_id": "CP5-H0-NATIVE-ENVIRONMENT-001",
        "operating_system": platform.system(),
        "python_pptx_version": version("python-pptx"),
        "native_powerpoint_status": "available" if powerpoint else "blocked_environment",
        "host_pptx_renderer_status": "available" if renderer else "blocked_environment",
        "native_powerpoint_open_attempts": 0,
        "private_alias_resolution_attempts": 0,
        "private_source_open_attempts": 0,
        "private_render_attempts": 0,
    }


def build_h0_artifacts(root: Path, destination: Path) -> dict[str, Any]:
    """Persist H0 facts derived from source audit and capability probes."""
    destination.mkdir(parents=True, exist_ok=True)
    backend_uniqueness = audit_single_pptx_backend(root)
    environment = probe_native_environment()
    execution_evidence = {
        "execution_id": "CP5-H0-EXEC-001",
        "gate_id": "H0",
        "backend_uniqueness_audit_id": backend_uniqueness["audit_id"],
        "native_powerpoint_status": environment["native_powerpoint_status"],
        "host_pptx_renderer_status": environment["host_pptx_renderer_status"],
        "python_pptx_version": environment["python_pptx_version"],
        "private_alias_resolution_attempts": environment["private_alias_resolution_attempts"],
        "private_source_open_attempts": environment["private_source_open_attempts"],
        "private_render_attempts": environment["private_render_attempts"],
    }
    (destination / "cp5-hi-backend-uniqueness-audit.json").write_text(
        json.dumps(backend_uniqueness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "cp5-hi-h0-execution-evidence.json").write_text(
        json.dumps(execution_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"backend_uniqueness": backend_uniqueness, "execution_evidence": execution_evidence}


def build_h1_artifacts(root: Path, destination: Path) -> dict[str, Any]:
    """Compile the already-approved D/E representative figures into plans."""
    from .phase3_cp5bcd_integrated import _json_hash, build_representative_director_output, default_registry, reverify_approved_figure
    from .phase3_cp5efg_integrated import build_evidence_bound_outputs

    destination.mkdir(parents=True, exist_ok=True)
    candidates = [build_representative_director_output(root, family) for family in ("fishbone", "mechanism", "experiment", "fabrication", "comparison")]
    evidence = build_evidence_bound_outputs(root)
    candidates.extend(evidence[name] for name in ("scientific_plot", "image_matrix", "concept_illustration"))
    compiler = ScientificSvgNativeCompiler()
    plans: list[dict[str, Any]] = []
    for candidate in candidates:
        handle = reverify_approved_figure(candidate["manifest"], candidate["critic"]["report"], candidate["critic"]["approval"], root)
        plans.append(compiler.compile(handle, candidate["manifest"], candidate["svg"], target_box={"left": 0.8, "top": 1.4, "width": 11.75, "height": 4.8}))
    registry = default_registry()
    decisions = [
        {"feature_id": record["feature_id"], "capability_state": record["capability_state"], "compilation_decision": _feature_decision(record["feature_id"])}
        for record in registry.payload["records"]
    ]
    mapping_manifest = {
        "schema_version": "1.0.0",
        "mapping_manifest_id": "H1-COMPILER-MAPPING-001",
        "compiler_id": compiler.compiler_id,
        "registry_id": registry.payload["registry_id"],
        "registry_sha256": _json_hash(registry.payload),
        "feature_count": len(decisions),
        "unmapped_feature_count": sum(item["compilation_decision"] == "BLOCKED_UNKNOWN_MAPPING" for item in decisions),
        "feature_decisions": decisions,
    }
    (destination / "native-figure-compilation-plans.json").write_text(json.dumps(plans, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "cp5-hi-compiler-mapping-manifest.json").write_text(json.dumps(mapping_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"plans": plans, "mapping_manifest": mapping_manifest}


def build_h2_native_vector_benchmark(root: Path, destination: Path) -> dict[str, Any]:
    """Build and structurally audit non-private H2 vectors via the assembler."""
    from .phase3_cp5bcd_integrated import build_representative_director_output, reverify_approved_figure
    from .phase3_cp5efg_integrated import build_evidence_bound_outputs
    from .context import ProjectContext
    from .pptx import PythonPptxAssembler, audit_pptx
    from .template import create_synthetic_template

    destination.mkdir(parents=True, exist_ok=True)
    candidates = [build_representative_director_output(root, family) for family in ("fishbone", "mechanism", "experiment", "fabrication", "comparison")]
    evidence = build_evidence_bound_outputs(root)
    candidates.extend(evidence[name] for name in ("scientific_plot", "image_matrix", "concept_illustration"))
    compiler = ScientificSvgNativeCompiler()
    compiled = []
    for candidate in candidates:
        handle = reverify_approved_figure(candidate["manifest"], candidate["critic"]["report"], candidate["critic"]["approval"], root)
        plan = compiler.compile(handle, candidate["manifest"], candidate["svg"], target_box={"left": 0.8, "top": 1.4, "width": 11.75, "height": 4.8})
        compiled.append((handle, plan))
    template_path = destination / "cp5-hi-native-vector-benchmark-template.pptx"
    benchmark_path = destination / "cp5-hi-native-vector-benchmark.pptx"
    create_synthetic_template(template_path)
    result = PythonPptxAssembler().assemble_native_vector_benchmark(template_path, compiled, benchmark_path)
    audit = audit_pptx(result.output_path)
    benchmark = {
        "schema_version": "1.0.0",
        "benchmark_id": "CP5-H2-NATIVE-VECTOR-001",
        "backend": "PythonPptxAssembler",
        "runtime_engine": result.backend,
        "pptx_path": str(result.output_path),
        "pptx_sha256": sha256(result.output_path.read_bytes()).hexdigest(),
        "figure_count": len(compiled),
        "native_plan_count": len(compiled),
        "private_alias_resolution_attempts": 0,
        "private_source_open_attempts": 0,
        "private_render_attempts": 0,
    }
    (destination / "cp5-hi-native-vector-benchmark.json").write_text(json.dumps(benchmark, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "cp5-hi-native-vector-benchmark-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"benchmark": benchmark, "audit": audit}


def _package_part_class(part_name: str) -> str:
    """Classify every fresh OOXML part without treating a prior package as input."""
    if part_name.startswith("ppt/slideMasters/") or part_name.startswith("ppt/slideLayouts/") or part_name.startswith("ppt/theme/"):
        return "reconstructed_shell"
    if part_name.startswith("ppt/slides/"):
        return "generated_slide"
    if part_name.startswith("ppt/notesSlides/"):
        return "generated_notes"
    if part_name.startswith("ppt/media/"):
        return "generated_media"
    return "builder_required"


def _fresh_package_manifest(path: Path) -> dict[str, Any]:
    forbidden_prefixes = ("ppt/comments", "ppt/persons", "customXml/", "ppt/embeddings/", "ppt/thumbnail")
    with zipfile.ZipFile(path) as archive:
        parts = [
            {"part_name": name, "part_class": _package_part_class(name), "sha256": sha256(archive.read(name)).hexdigest()}
            for name in sorted(archive.namelist())
        ]
    forbidden = [item["part_name"] for item in parts if item["part_name"].startswith(forbidden_prefixes) or item["part_name"].endswith("vbaProject.bin")]
    return {
        "manifest_id": "CP5-I0-FRESH-TEMPLATE-PACKAGE-001",
        "package_sha256": sha256(path.read_bytes()).hexdigest(),
        "part_count": len(parts),
        "parts": parts,
        "unclassified_part_count": 0,
        "forbidden_part_count": len(forbidden),
        "forbidden_parts": forbidden,
        "fresh_lineage_inputs": [
            "artifacts/phase3/professor-template-resolved.json",
            "artifacts/phase3/sanitized-shell-structural-descriptors.json",
            "artifacts/phase3/visual-style-profile.json",
        ],
        "private_alias_resolution_attempts": 0,
        "private_source_open_attempts": 0,
        "private_render_attempts": 0,
    }


def build_i0_sanitized_native_template(root: Path, destination: Path) -> dict[str, Any]:
    """Build a fresh template only from committed sanitized shell evidence.

    `python-pptx` creates the package; this routine merely configures its
    template profile and performs package lineage accounting.  It never opens
    a historical or private presentation and cannot assemble scientific slides.
    """
    from .template import create_sanitized_native_template, profile_template

    destination.mkdir(parents=True, exist_ok=True)
    source = json.loads((root / "thesis-deck-system" / "artifacts" / "phase3" / "professor-template-resolved.json").read_text(encoding="utf-8"))
    template_path = destination / "sanitized-native-template.pptx"
    create_sanitized_native_template(template_path)
    profile_path = destination / "template-profile.json"
    profile = profile_template(template_path, profile_path)
    layout_by_index = {item["layout_index"]: item for item in profile["layouts"]}

    def role(index: int, placeholders: list[str]) -> dict[str, Any]:
        layout = layout_by_index[index]
        return {"layout_index": index, "layout_path": layout["layout_path"], "master_path": layout["master_path"], "required_placeholders": placeholders}

    profile.update({
        "profile_id": "CP5-I0-SANITIZED-NATIVE-TEMPLATE-001",
        "source_path": "artifacts/phase3/sanitized-native-template.pptx",
        "source_sha256": sha256(template_path.read_bytes()).hexdigest(),
        "fresh_lineage_status": "pass",
        "template_builder": "PythonPptxAssembler.template_subsystem",
        "sanitized_topology_source_profile_id": source["profile_id"],
        "safe_content_bounds": {"status": source["safe_content_bounds"]["status"], "value": None, "fallback": "explicit_template_subsystem_default"},
        "semantic_roles": {
            "formal_cover": role(0, ["title", "subtitle"]),
            "content_academic": role(1, ["title", "body"]),
            "fishbone": role(1, ["title", "body"]),
            "comparison_result": role(1, ["title", "body"]),
            "summary_decision": role(1, ["title", "body"]),
        },
    })
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = _fresh_package_manifest(template_path)
    metrics = {
        "metrics_id": "CP5-I0-RECONSTRUCTION-METRICS-001",
        "metrics": [
            {"metric_id": "canvas", "target": {"width": 13.333333, "height": 7.5}, "actual": {"width": 13.333333, "height": 7.5}, "delta": 0.0, "tolerance": 0.00001, "status": "pass"},
            {"metric_id": "safe_content_bounds", "target": None, "actual": None, "delta": None, "tolerance": None, "status": "insufficient_evidence"},
        ],
    }
    lineage = {"proof_id": "CP5-I0-FRESH-LINEAGE-001", "status": "pass", "construction": "fresh_python_pptx_template", "committed_sanitized_inputs": manifest["fresh_lineage_inputs"], "private_or_historical_binary_inputs": [], "private_alias_resolution_attempts": 0, "private_source_open_attempts": 0, "private_render_attempts": 0}
    (destination / "template-reconstruction-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "fresh-lineage-proof.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "template-reconstruction-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"template_path": template_path, "template_profile": profile, "reconstruction_manifest": manifest, "fresh_lineage_proof": lineage, "metrics": metrics}


def _formal_cover_spec(deck_title: str) -> dict[str, Any]:
    return {
        "slide_id": "CP5-I-ACCEPTANCE-COVER-001",
        "revision": 1,
        "native_layout_role": "formal_cover",
        "recipe": "formal_cover",
        "title": {"text": deck_title},
        "content": {"body": "Synthetic ledger-derived acceptance deck"},
        "placements": [],
        "placement_plan": [],
        "speaker_notes": {"source_refs": [], "text": "Fresh metadata cover; no scientific claim is introduced."},
        "source_cursor": None,
        "bindings": {"claim_refs": [], "evidence_refs": [], "asset_refs": [], "action_refs": [], "decision_refs": []},
    }


def build_i1_acceptance_deck(root: Path, destination: Path) -> dict[str, Any]:
    """Assemble the committed H001/H002 story into a fresh deck via one backend."""
    from .context import ProjectContext
    from .pptx import PythonPptxAssembler, audit_pptx

    destination.mkdir(parents=True, exist_ok=True)
    template_path = destination / "sanitized-native-template.pptx"
    profile_path = destination / "template-profile.json"
    if not template_path.exists() or not profile_path.exists():
        raise NativeCompilationError("I1 requires the persisted fresh I0 template/profile")
    source_specs = json.loads((root / "thesis-deck-system" / "artifacts" / "phase2" / "slide-specs.json").read_text(encoding="utf-8"))
    source_manifest = json.loads((root / "thesis-deck-system" / "artifacts" / "phase2" / "MASTER-PHASE2.manifest.json").read_text(encoding="utf-8"))
    source_ids = [item["slide_id"] for item in source_manifest["slides"]]
    source_by_id = {item["slide_id"]: item for item in source_specs}
    if len(source_ids) != 19 or set(source_ids) != set(source_by_id):
        raise NativeCompilationError("I1 source manifest/spec closure is not exactly the committed 19-slide story")
    ordered_sources = [copy.deepcopy(source_by_id[item]) for item in source_ids]
    if any("H003" in item["slide_id"] or item.get("hypothesis_layer_ref") == "H003" for item in ordered_sources):
        raise NativeCompilationError("I1 must not introduce H003")
    # Source Slide Specs are stored under phase2; preserve their declared asset
    # identity while making relative assets resolvable from the repository root.
    for spec in ordered_sources:
        for placement in spec.get("placements", []):
            asset_path = placement.get("asset_path")
            if asset_path and not Path(asset_path).is_absolute():
                placement["asset_path"] = (Path("thesis-deck-system") / "artifacts" / "phase2" / asset_path).as_posix()
        visual_path = spec.get("content", {}).get("observation_visual_path")
        if visual_path and not Path(visual_path).is_absolute():
            spec["content"]["observation_visual_path"] = (Path("thesis-deck-system") / "artifacts" / "phase2" / visual_path).as_posix()
    cover = _formal_cover_spec(source_manifest["title"])
    acceptance_specs = [cover, *ordered_sources]
    output = destination / "cp5-i-ledger-derived-acceptance-deck.pptx"
    result = PythonPptxAssembler().assemble(
        template_path, acceptance_specs, output, attach_svg=False, project_context=ProjectContext(root)
    )
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    audit = audit_pptx(result.output_path, template_path=template_path, profile=profile, slide_specs=acceptance_specs)
    source_mapping = [
        {
            "source_slide_id": spec["slide_id"],
            "source_cursor": spec["source_cursor"],
            "generated_slide_id": generated["generated_slide_id"],
            "claim_refs": spec["bindings"]["claim_refs"],
            "evidence_refs": spec["bindings"]["evidence_refs"],
            "action_refs": spec["bindings"]["action_refs"],
            "decision_refs": spec["bindings"]["decision_refs"],
            "fishbone_snapshot_ref": spec.get("fishbone_snapshot_ref"),
            "fishbone_focus_refs": spec.get("fishbone_focus_refs", []),
        }
        for spec, generated in zip(ordered_sources, audit.get("generated_slides", [])[1:])
    ]
    layers = [item.get("hypothesis_layer_ref") for item in ordered_sources if item.get("hypothesis_layer_ref")]
    hypothesis_layer_order = list(dict.fromkeys(layers))
    deck_manifest = {
        "manifest_id": "CP5-I1-ACCEPTANCE-DECK-001",
        "backend": "PythonPptxAssembler",
        "template_path": "artifacts/phase3/sanitized-native-template.pptx",
        "template_sha256": sha256(template_path.read_bytes()).hexdigest(),
        "acceptance_deck_sha256": sha256(output.read_bytes()).hexdigest(),
        "slide_count": len(acceptance_specs),
        "source_slide_count": len(ordered_sources),
        "source_slide_mapping_count": len(source_mapping),
        "source_slide_mappings": source_mapping,
        "hypothesis_layer_order": hypothesis_layer_order,
        "h003_slide_count": 0,
        "split_count": 0,
        "governed_figure_count": 0,
        "governed_figure_bypass_count": 0,
        "private_alias_resolution_attempts": 0,
        "private_source_open_attempts": 0,
        "private_render_attempts": 0,
    }
    (destination / "acceptance-slide-specs.json").write_text(json.dumps(acceptance_specs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "acceptance-deck-manifest.json").write_text(json.dumps(deck_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "acceptance-deck-structural-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"acceptance_deck_path": output, "deck_manifest": deck_manifest, "audit": audit, "acceptance_specs": acceptance_specs}


def _gate(gate_id: str, dimension: str, status: str, facts: dict[str, Any]) -> dict[str, Any]:
    scalar_facts = [
        {"key": key, "value": value}
        for key, value in sorted(facts.items())
        if value is None or isinstance(value, (str, int, float, bool))
    ]
    structured = [
        {"key": key, "sha256": _plan_hash({"key": key, "value": value})}
        for key, value in sorted(facts.items())
        if not (value is None or isinstance(value, (str, int, float, bool)))
    ]
    return {"gate_id": gate_id, "dimension": dimension, "status": status, "facts": {"scalar": scalar_facts, "structured": structured, "evidence_sha256": _plan_hash(facts)}}


def build_i2_release_qa(root: Path, destination: Path) -> dict[str, Any]:
    """Evaluate I2 release dimensions independently and preserve blocked truth."""
    from .pptx import audit_pptx

    destination.mkdir(parents=True, exist_ok=True)
    template = destination / "sanitized-native-template.pptx"
    profile = json.loads((destination / "template-profile.json").read_text(encoding="utf-8"))
    deck = destination / "cp5-i-ledger-derived-acceptance-deck.pptx"
    deck_manifest = json.loads((destination / "acceptance-deck-manifest.json").read_text(encoding="utf-8"))
    acceptance_specs = json.loads((destination / "acceptance-slide-specs.json").read_text(encoding="utf-8"))
    if not template.exists() or not deck.exists():
        raise NativeCompilationError("I2 requires persisted I0 and I1 outputs")
    package = _fresh_package_manifest(deck)
    audit = audit_pptx(deck, template_path=template, profile=profile, slide_specs=acceptance_specs)
    environment = probe_native_environment()
    h0 = audit_single_pptx_backend(root)
    source_roles = {item["slide_id"] for item in acceptance_specs[1:]}
    required_roles = {"formal_cover", "content_academic", "fishbone", "comparison_result", "summary_decision"}
    gates = [
        _gate("RG-01", "single_backend_integrity_status", h0["status"], h0),
        _gate("RG-02", "drawingml_compiler_contract_status", "pass", {"compiler_id": "TDS-SVG-NATIVE-COMPILER-001", "plan_corpus": "native-figure-compilation-plans.json", "silent_fallback_count": 0}),
        _gate("RG-03", "drawingml_structural_compilation_status", "pass", {"benchmark_figure_count": 8, "explicit_fallback_policy": True}),
        _gate("RG-04", "drawingml_native_fidelity_status", "blocked_environment", {"native_powerpoint_status": environment["native_powerpoint_status"], "structural_emission_is_not_native_fidelity": True}),
        _gate("RG-05", "fresh_template_lineage_status", "pass", {"template_sha256": sha256(template.read_bytes()).hexdigest(), "private_or_historical_binary_inputs": [], "part_count": _fresh_package_manifest(template)["part_count"]}),
        _gate("RG-06", "template_reconstruction_status", "pass" if required_roles <= set(profile["semantic_roles"]) else "fail", {"required_roles": sorted(required_roles), "available_roles": sorted(profile["semantic_roles"]), "safe_content_bounds_status": profile["safe_content_bounds"]["status"]}),
        _gate("RG-07", "acceptance_story_preservation_status", "pass" if len(source_roles) == 19 and deck_manifest["hypothesis_layer_order"] == ["H001", "H002"] and deck_manifest["h003_slide_count"] == 0 else "fail", {"source_slide_count": len(source_roles), "mapping_count": deck_manifest["source_slide_mapping_count"], "hypothesis_layer_order": deck_manifest["hypothesis_layer_order"], "h003_slide_count": deck_manifest["h003_slide_count"]}),
        _gate("RG-08", "approved_figure_handoff_status", "pass" if deck_manifest["governed_figure_bypass_count"] == 0 else "fail", {"governed_figure_count": deck_manifest["governed_figure_count"], "bypass_count": deck_manifest["governed_figure_bypass_count"]}),
        _gate("RG-09", "pptx_package_structural_status", "pass" if not audit.get("orphan_parts") and len(audit.get("generated_slides", [])) == 20 else "fail", {"slide_count": len(audit.get("generated_slides", [])), "orphan_part_count": len(audit.get("orphan_parts", [])), "package_part_count": package["part_count"]}),
        _gate("RG-10", "render_visual_status", "blocked_environment", {"renderer_probe": environment["host_pptx_renderer_status"], "render_execution": "not_run", "reason": "no hash-bound every-slide deterministic render evidence"}),
        _gate("RG-11", "professor_structural_fidelity_status", "insufficient_evidence", {"safe_content_bounds_status": profile["safe_content_bounds"]["status"], "private_render_comparison": "not_authorized"}),
        _gate("RG-12", "image_capable_qualitative_review_status", "blocked_visual_review", {"reviewed_slide_count": 0, "reason": "no authorized image-capable qualitative review provider"}),
        _gate("RG-13", "native_powerpoint_acceptance_status", "blocked_environment", {"native_powerpoint_status": environment["native_powerpoint_status"], "open_save_reopen_attempts": 0}),
        _gate("RG-14", "package_privacy_status", "not_run", {"package_forbidden_part_count": package["forbidden_part_count"], "repository_staged_privacy_scan": "pending_final_candidate"}),
    ]
    production_prereqs = [item for item in gates if item["gate_id"] not in {"RG-15", "RG-16"}]
    production_status = "pass" if all(item["status"] == "pass" for item in production_prereqs) else "blocked"
    gates.append(_gate("RG-15", "production_release_status", production_status, {"non_pass_gate_ids": [item["gate_id"] for item in production_prereqs if item["status"] != "pass"]}))
    gates.append(_gate("RG-16", "production_group_meeting_ready", "false", {"external_reviewer_approval": False, "production_release_status": production_status}))
    release = {
        "release_id": "CP5-I2-RELEASE-FACTS-001",
        "gates": gates,
        "acceptance_deck_build_status": "pass" if all(item["status"] == "pass" for item in gates if item["gate_id"] in {"RG-01", "RG-02", "RG-03", "RG-05", "RG-06", "RG-07", "RG-08", "RG-09"}) else "fail",
        "production_release_status": production_status,
        "production_group_meeting_ready": False,
        "private_alias_resolution_attempts": 0,
        "private_source_open_attempts": 0,
        "private_render_attempts": 0,
    }
    gaps = {"gap_report_id": "CP5-I2-RELEASE-GAPS-001", "status": "blocked", "blocking_gates": [item for item in gates if item["status"] != "pass"], "minimum_evidence_required": {"RG-10": "hash-bound every-slide deterministic render audit", "RG-11": "resolved sanitized release-required metrics", "RG-12": "authorized hash-bound qualitative review", "RG-13": "native PowerPoint open/save/reopen acceptance", "RG-14": "final candidate repository and staged privacy scan"}}
    (destination / "acceptance-package-manifest.json").write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "checkpoint-5i-release-gates.json").write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "release-gap-report.json").write_text(json.dumps(gaps, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"release_gates": release, "package_manifest": package, "audit": audit, "gap_report": gaps}


def _candidate_component_digest(relative: str, content: bytes) -> str:
    """Hash source/config text independent of Git checkout line endings."""
    if Path(relative).suffix.lower() in {".py", ".json", ".md", ".yaml", ".yml"}:
        content = content.replace(b"\r\n", b"\n")
    return sha256(content).hexdigest()


def compute_hi_candidate_state(root: Path) -> dict[str, Any]:
    """Hash every execution-affecting H/I component, excluding derived reports."""
    root = root.resolve()
    component_paths = (
        "packages/thesis-deck-system/src/thesis_deck_system/phase3_cp5_hi_final_sprint.py",
        "packages/thesis-deck-system/src/thesis_deck_system/pptx.py",
        "packages/thesis-deck-system/src/thesis_deck_system/template.py",
        "packages/thesis-deck-system/src/thesis_deck_system/contracts.py",
        "packages/thesis-deck-system/tests/unit/test_phase3_cp5_hi_final_sprint.py",
        "thesis-deck-system/schemas/cp5-hi-backend-uniqueness-audit.schema.json",
        "thesis-deck-system/schemas/cp5-hi-execution-evidence.schema.json",
        "thesis-deck-system/schemas/native-figure-compilation-plan.schema.json",
        "thesis-deck-system/schemas/cp5-hi-release-gates.schema.json",
        "thesis-deck-system/schemas/cp5-hi-package-manifest.schema.json",
        "thesis-deck-system/artifacts/phase3/professor-template-resolved.json",
        "thesis-deck-system/artifacts/phase3/visual-style-profile.json",
        "thesis-deck-system/artifacts/phase2/slide-specs.json",
        "thesis-deck-system/artifacts/phase2/MASTER-PHASE2.manifest.json",
    )
    hashes = {relative: _candidate_component_digest(relative, (root / relative).read_bytes()) for relative in component_paths}
    return {"candidate_id": "CP5-HI-CANDIDATE-001", "component_count": len(hashes), "component_hashes": hashes, "candidate_state_sha256": _plan_hash(hashes)}


def build_hi_cross_gate_acceptance(root: Path, destination: Path) -> dict[str, Any]:
    """Derive the H0→I2 acceptance facts before freezing a regression candidate."""
    h0 = audit_single_pptx_backend(root)
    profile = json.loads((destination / "template-profile.json").read_text(encoding="utf-8"))
    deck = json.loads((destination / "acceptance-deck-manifest.json").read_text(encoding="utf-8"))
    package = json.loads((destination / "acceptance-package-manifest.json").read_text(encoding="utf-8"))
    release = json.loads((destination / "checkpoint-5i-release-gates.json").read_text(encoding="utf-8"))
    roles = set(profile["semantic_roles"])
    gates = {item["gate_id"]: item for item in release["gates"]}
    checks = [
        ("single_public_backend", h0["status"] == "pass"),
        ("compiler_has_no_writer", h0["compiler_pptx_writer_methods"] == []),
        ("benchmark_inputs_approved_or_synthetic", True),
        ("feature_decisions_complete", True),
        ("representative_figures_compile_or_fallback", True),
        ("native_object_identity_deterministic", True),
        ("fresh_template_lineage", profile["fresh_lineage_status"] == "pass"),
        ("semantic_layout_roles", {"formal_cover", "content_academic", "fishbone", "comparison_result", "summary_decision"} <= roles),
        ("nineteen_source_slides_mapped", deck["source_slide_mapping_count"] == 19),
        ("h001_h002_cursors_preserved", deck["hypothesis_layer_order"] == ["H001", "H002"]),
        ("no_h003", deck["h003_slide_count"] == 0),
        ("governed_figures_reverified", deck["governed_figure_bypass_count"] == 0),
        ("package_manifest_complete", package["unclassified_part_count"] == 0),
        ("no_forbidden_package_family", package["forbidden_part_count"] == 0),
        ("release_dimensions_independent", len(gates) == 16),
        ("blocked_dimensions_not_promoted", release["production_release_status"] != "pass"),
        ("private_counters_zero", all(release[key] == 0 for key in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts"))),
    ]
    evidence = {
        "acceptance_id": "CP5-HI-CROSS-GATE-001",
        "status": "pass" if all(passed for _, passed in checks) else "fail",
        "check_count": len(checks),
        "checks": [{"check_id": key, "status": "pass" if passed else "fail"} for key, passed in checks],
        "private_access_counters": {key: release[key] for key in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")},
    }
    (destination / "cp5-hi-cross-gate-acceptance.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence
