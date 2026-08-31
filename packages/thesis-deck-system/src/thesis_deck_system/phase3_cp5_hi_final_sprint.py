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


class NativeCompilationError(ValueError):
    """Raised when an H-stage compilation boundary is violated."""


@dataclass(frozen=True)
class ScientificSvgNativeCompiler:
    """Internal plan compiler placeholder; it deliberately cannot write PPTX."""

    compiler_id: str = "TDS-SVG-NATIVE-COMPILER-001"
    compiler_version: str = "1.0.0"


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
