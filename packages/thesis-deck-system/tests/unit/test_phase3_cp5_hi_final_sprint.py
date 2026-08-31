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


def test_h1_compiler_requires_reverified_handle_and_returns_deterministic_native_plan():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.phase3_cp5_hi_final_sprint import NativeCompilationError, ScientificSvgNativeCompiler
    from thesis_deck_system.phase3_cp5bcd_integrated import build_representative_director_output, reverify_approved_figure

    produced = build_representative_director_output(ROOT, "mechanism")
    handle = reverify_approved_figure(produced["manifest"], produced["critic"]["report"], produced["critic"]["approval"], ROOT)
    compiler = ScientificSvgNativeCompiler()

    plan = compiler.compile(handle, produced["manifest"], produced["svg"], target_box={"left": 1.0, "top": 1.2, "width": 8.0, "height": 4.5})
    repeat = compiler.compile(handle, produced["manifest"], produced["svg"], target_box={"left": 1.0, "top": 1.2, "width": 8.0, "height": 4.5})

    assert plan["schema_version"] == "1.0.0"
    assert plan["figure_id"] == handle.figure_id
    assert plan["plan_sha256"] == repeat["plan_sha256"]
    assert plan["objects"]
    assert all(item["outcome"] in {"DRAWINGML_EMITTED", "SVG_VECTOR_FALLBACK", "BLOCKED_UNSUPPORTED", "BLOCKED_UNKNOWN_MAPPING"} for item in plan["objects"])
    assert any(item["text"] for item in plan["objects"] if item["shape_kind"] == "text")
    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5hi=True)
    assert registry.errors("native-figure-compilation-plan", plan) == []
    with __import__("pytest").raises(NativeCompilationError):
        compiler.compile({}, produced["manifest"], produced["svg"], target_box={"left": 1.0, "top": 1.2, "width": 8.0, "height": 4.5})


def test_h1_artifacts_cover_all_registered_features_and_approved_figure_representatives(tmp_path: Path):
    from thesis_deck_system.phase3_cp5_hi_final_sprint import build_h1_artifacts

    result = build_h1_artifacts(ROOT, tmp_path)

    assert result["mapping_manifest"]["unmapped_feature_count"] == 0
    assert result["mapping_manifest"]["feature_count"] >= 30
    assert len(result["plans"]) == 8
    assert all(plan["approved_figure"]["manifest_id"] for plan in result["plans"])
    assert (tmp_path / "native-figure-compilation-plans.json").exists()
