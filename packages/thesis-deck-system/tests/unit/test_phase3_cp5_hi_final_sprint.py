"""CP5-H/I final-sprint contracts, starting with H0 preflight."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_h0_backend_uniqueness_and_environment_probe_are_execution_owned(tmp_path: Path):
    from thesis_deck_system.phase3_cp5_hi_final_sprint import (
        ScientificSvgNativeCompiler,
        audit_single_pptx_backend,
        probe_native_environment,
    )

    audit = audit_single_pptx_backend(ROOT)
    environment = probe_native_environment()

    assert audit["status"] == "pass"
    assert audit["public_pptx_backends"] == ["PythonPptxAssembler"]
    assert audit["compiler_pptx_writer_methods"] == []
    assert audit["template_scientific_slide_assembly_bypasses"] == []
    assert audit["bypass_count"] == 0
    assert environment["python_pptx_version"]
    assert environment["native_powerpoint_status"] in {"available", "blocked_environment"}
    assert environment["host_pptx_renderer_status"] in {"available", "blocked_environment"}
    assert not hasattr(ScientificSvgNativeCompiler, "save_pptx")
    assert not hasattr(ScientificSvgNativeCompiler, "export_pptx")


def test_h0_artifacts_are_schema_closed_and_bind_real_audit_facts(tmp_path: Path):
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5_hi_final_sprint import build_h0_artifacts

    artifacts = build_h0_artifacts(ROOT, tmp_path)
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5hi=True)

    assert artifacts["backend_uniqueness"]["status"] == "pass"
    assert artifacts["execution_evidence"]["private_alias_resolution_attempts"] == 0
    assert registry.errors("cp5-hi-backend-uniqueness-audit", artifacts["backend_uniqueness"]) == []
    assert registry.errors("cp5-hi-execution-evidence", artifacts["execution_evidence"]) == []
