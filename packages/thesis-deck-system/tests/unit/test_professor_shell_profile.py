"""Professor-shell authority tests for the visual-calibration sprint."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_shell_profile_uses_sanitized_measurements_and_marks_unmeasured_bounds_as_system_owned(tmp_path: Path):
    from thesis_deck_system.professor_shell import (
        audit_professor_shell_template,
        build_professor_shell_profile,
    )
    from thesis_deck_system.template import create_sanitized_native_template

    profile = build_professor_shell_profile(ROOT)
    template = create_sanitized_native_template(tmp_path / "shell.pptx", shell_profile=profile)
    audit = audit_professor_shell_template(template, profile)

    assert profile["shell_profile_id"] == "PSP-001"
    assert profile["canvas"]["evidence_level"] == "measured_sanitized"
    assert profile["title_safe_region"]["evidence_level"] == "measured_sanitized"
    assert profile["body_content_safe_region"]["evidence_level"] == "synthetic_system_owned"
    assert profile["body_content_safe_region"]["fidelity_status"] == "insufficient_evidence"
    assert profile["footer_region"]["evidence_level"] == "measured_sanitized"
    assert profile["page_number_region"]["evidence_level"] == "measured_sanitized"
    assert audit["shell_profile_to_pptx_mismatch_count"] == 0
    assert audit["unsupported_claimed_shell_feature_count"] == 0


def test_shell_profile_is_closed_and_registered():
    from thesis_deck_system.contracts import SchemaRegistry
    from thesis_deck_system.professor_shell import build_professor_shell_profile

    profile = build_professor_shell_profile(ROOT)
    registry = SchemaRegistry(
        ROOT / "thesis-deck-system" / "schemas",
        schema_names=("professor-shell-profile",),
    )

    assert registry.errors("professor-shell-profile", profile) == []
    profile["canvas"]["unexpected"] = True
    assert registry.errors("professor-shell-profile", profile)


def test_shell_artifact_writer_persists_profile_and_reverse_audit(tmp_path: Path):
    from thesis_deck_system.professor_shell import write_professor_shell_artifacts

    outputs = write_professor_shell_artifacts(ROOT, tmp_path)

    assert outputs["profile"].is_file()
    assert outputs["template"].is_file()
    assert outputs["audit"].is_file()
