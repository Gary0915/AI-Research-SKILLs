"""CP5-H/I single-backend preflight and native-compiler boundary.

This module intentionally owns no presentation-package writer.  It records the
preflight facts that later H/I stages must bind before compiling approved
Scientific SVG into an assembler-consumed plan.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
from typing import Any
from hashlib import sha256
from xml.etree import ElementTree as ET


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
