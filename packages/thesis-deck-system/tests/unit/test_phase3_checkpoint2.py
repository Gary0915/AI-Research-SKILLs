"""Synthetic-first RED tests for Phase 3 Checkpoint 2."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

import pytest
from pptx import Presentation

from thesis_deck_system.contracts import SchemaRegistry
from thesis_deck_system.phase3_checkpoint2 import (
    Checkpoint2PolicyViolation,
    Checkpoint2Run,
    LocalPrivateAliasResolver,
    build_checkpoint2,
    sanitize_body_descriptor,
    sanitize_shell_descriptor,
    validate_checkpoint2_qa,
)
from thesis_deck_system.phase3_contracts import (
    canonical_observation_catalogs,
    validate_observation_visual_binding,
)
from thesis_deck_system.phase3_privacy import RepositoryPrivacyScanner
from thesis_deck_system.phase3_privacy import LEGACY_EXCEPTION_PATH, LEGACY_EXCEPTION_BLOB_SHA


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "thesis-deck-system" / "schemas"
SHA = "a" * 64
ALIASES = (
    "private://template_primary_1",
    "private://layout_exemplar_2",
    "private://template_primary_3",
)


def _synthetic_pptx(path: Path) -> Path:
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    slide.shapes.add_textbox(914400, 914400, 3657600, 914400)
    slide.shapes.add_shape(1, 914400, 2286000, 2743200, 1371600)
    presentation.save(path)
    return path


def _evidence(evidence_id: str, kind: str, *, verified: str = "verified") -> dict:
    return {
        "schema_version": "1.0.0", "evidence_id": evidence_id, "kind": kind,
        "title": "Synthetic evidence", "provenance": "synthetic_test_only",
        "source": {"source_id": "S001", "uri": "fixtures/synthetic.json", "sha256": SHA},
        "claim_support_refs": [], "claim_contradict_refs": [], "scope": {},
        "verification": {"status": verified},
    }


def _plot(evidence_id: str) -> dict:
    return {
        "schema_version": "3.0.0", "figure_output_id": "FOM001", "figure_id": "FIG001",
        "figure_type": "scientific_plot", "primary_artifact_kind": "svg_vector",
        "renderer": "synthetic_renderer", "source_spec_sha256": SHA,
        "provenance_refs": [evidence_id], "style_profile_ref": "VSP001",
        "evidence_status": "empirical", "primary_artifact": {
            "path": "artifacts/phase3/synthetic.svg", "sha256": SHA,
            "data_provenance_refs": [evidence_id],
        }, "output_part_lineage": ["generated"],
    }


def _binding(evidence_id: str = "E001") -> dict:
    return {
        "observation_id": "OBS001", "empirical_evidence_required": True,
        "observation_evidence_ref": evidence_id, "observation_output_ref": "FOM001",
        "evidence_refs": [evidence_id], "auxiliary_visuals": [],
    }


def _alias_mapping(tmp_path: Path) -> dict[str, Path]:
    return {alias: _synthetic_pptx(tmp_path / f"fixture-{index}.pptx") for index, alias in enumerate(ALIASES, 1)}


def test_repository_wide_scan_blocks_ordinary_tracked_source_canary(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "ordinary.py").write_text("value = 'D:/SYNTHETIC_PRIVATE_ROOT/secret.pptx'", encoding="utf-8")
    subprocess.run(["git", "add", "ordinary.py"], cwd=tmp_path, check=True)
    findings = RepositoryPrivacyScanner(private_root_signatures=["SYNTHETIC_PRIVATE_ROOT"]).scan_repository(tmp_path)
    assert {item.classification for item in findings} >= {"absolute_path"}
    assert all("SYNTHETIC_PRIVATE_ROOT" not in str(item) for item in findings)


def _legacy_basename_tokens() -> list[str]:
    text = subprocess.check_output(["git", "show", f"HEAD:{LEGACY_EXCEPTION_PATH}"], cwd=ROOT, text=True, encoding="utf-8")
    section = text.split("## D3-2 — Private exemplar roles remain asymmetric", 1)[1].split("\n## ", 1)[0]
    return sorted(set(__import__("re").findall(r"[A-Za-z0-9_ -]+\.pptx", section, __import__("re").I)))


def test_exact_reviewed_legacy_occurrence_is_recorded_not_silently_suppressed():
    tokens = _legacy_basename_tokens()
    findings, exceptions = RepositoryPrivacyScanner(forbidden_basenames=tokens).scan_repository_with_legacy_exception(ROOT, forbidden_basenames=tokens)
    assert not [item for item in findings if item.location == LEGACY_EXCEPTION_PATH]
    assert exceptions == [{"exception_id": "CP2-PRE-1-LEGACY-D3-2", "repository_relative_path": LEGACY_EXCEPTION_PATH, "reviewed_blob_sha": LEGACY_EXCEPTION_BLOB_SHA, "privacy_rule_id": "forbidden_private_basename", "status": "applied_legacy_exception"}]
    assert all(token not in str(exception) for token in tokens for exception in exceptions)


def test_changed_legacy_blob_invalidates_exception(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "thesis-deck-system" / "reviews").mkdir(parents=True)
    target = tmp_path / LEGACY_EXCEPTION_PATH
    target.write_text("## D3-2 — Private exemplar roles remain asymmetric\nlegacy.pptx\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=test@example.invalid", "-c", "user.name=test", "commit", "-qm", "fixture"], cwd=tmp_path, check=True)
    target.write_text("## D3-2 — Private exemplar roles remain asymmetric\nlegacy.pptx\nchanged\n", encoding="utf-8")
    findings, exceptions = RepositoryPrivacyScanner(forbidden_basenames=["legacy.pptx"]).scan_repository_with_legacy_exception(tmp_path, forbidden_basenames=["legacy.pptx"])
    assert not exceptions
    assert any(item.classification == "forbidden_private_basename" for item in findings)


def test_legacy_file_with_absolute_path_or_extra_basename_is_not_exempted(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "thesis-deck-system" / "reviews").mkdir(parents=True)
    target = tmp_path / LEGACY_EXCEPTION_PATH
    target.write_text("## D3-2 — Private exemplar roles remain asymmetric\nlegacy.pptx\nD:/PRIVATE_ROOT_CANARY/file.pptx\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=test@example.invalid", "-c", "user.name=test", "commit", "-qm", "fixture"], cwd=tmp_path, check=True)
    findings, exceptions = RepositoryPrivacyScanner(private_root_signatures=["PRIVATE_ROOT_CANARY"], forbidden_basenames=["legacy.pptx", "extra.pptx"]).scan_repository_with_legacy_exception(tmp_path, forbidden_basenames=["legacy.pptx", "extra.pptx"])
    assert not exceptions
    assert findings


@pytest.mark.parametrize("kind", ["synthetic_measurement", "synthetic_observation", "simulation_output"])
def test_production_observation_rejects_synthetic_and_simulation_evidence(kind: str):
    registry = SchemaRegistry(SCHEMAS, include_phase3=True)
    catalog = canonical_observation_catalogs(registry, [_evidence("E001", kind)], [_plot("E001")])
    assert "P3-OBSERVATION-PRODUCTION-EMPIRICAL-POLICY" in validate_observation_visual_binding(
        _binding(), catalog=catalog, evidence_policy="production"
    )


def test_fixture_mode_preserves_synthetic_observation_test_support():
    registry = SchemaRegistry(SCHEMAS, include_phase3=True)
    catalog = canonical_observation_catalogs(registry, [_evidence("E001", "synthetic_measurement", verified="synthetic_test_only")], [_plot("E001")])
    assert validate_observation_visual_binding(_binding(), catalog=catalog, evidence_policy="fixture") == []


def test_alias_resolver_accepts_only_three_stable_aliases_and_local_mapping(tmp_path: Path):
    resolver = LocalPrivateAliasResolver(_alias_mapping(tmp_path), private_root=tmp_path / "raw")
    assert resolver.resolve(ALIASES[0]).alias_uri == ALIASES[0]
    with pytest.raises(Checkpoint2PolicyViolation):
        resolver.resolve("D:/arbitrary.pptx")
    with pytest.raises(Checkpoint2PolicyViolation):
        resolver.resolve("private://unrecognized")


def test_source_session_is_recorded_before_open_and_derives_hash_slide_count(tmp_path: Path):
    run = Checkpoint2Run.start(pre_open_passed=True, private_root=tmp_path / "raw")
    resolver = LocalPrivateAliasResolver(_alias_mapping(tmp_path), private_root=tmp_path / "raw", execution=run)
    session = resolver.resolve(ALIASES[0]).open_read_only()
    profile = session.profile_structurally("shell")
    assert run.evidence.authorized_source_sessions == 1
    assert profile["source_sha256"] == hashlib.sha256((tmp_path / "fixture-1.pptx").read_bytes()).hexdigest()
    assert profile["slide_count"] == 1


def test_malformed_package_is_blocked_before_structural_profile(tmp_path: Path):
    bad = tmp_path / "bad.pptx"
    bad.write_bytes(b"not an ooxml zip")
    resolver = LocalPrivateAliasResolver({ALIASES[0]: bad, ALIASES[1]: bad, ALIASES[2]: bad}, private_root=tmp_path / "raw")
    with pytest.raises(Checkpoint2PolicyViolation):
        resolver.resolve(ALIASES[0]).open_read_only()


def test_profiler_is_read_only_and_structural_without_render(tmp_path: Path):
    mapping = _alias_mapping(tmp_path)
    before = hashlib.sha256(mapping[ALIASES[1]].read_bytes()).hexdigest()
    profile = LocalPrivateAliasResolver(mapping, private_root=tmp_path / "raw").resolve(ALIASES[1]).open_read_only().profile_structurally("body")
    after = hashlib.sha256(mapping[ALIASES[1]].read_bytes()).hexdigest()
    assert before == after
    assert profile["slide_count"] == 1
    assert profile["render_count"] == 0
    assert all("text" not in str(value).casefold() for value in profile.get("forbidden_exports", {}).values())


def test_sanitizers_fail_closed_and_block_exemplar_two_shell_contamination():
    shell = {"alias_uri": ALIASES[0], "source_sha256": SHA, "profile_id": "SHELL001", "slide_size": {"width": 13.333, "height": 7.5}, "master_count": 1, "layout_count": 1, "shell_primitives": [], "slide_count": 1}
    assert sanitize_shell_descriptor(shell)["profile_id"] == "SHELL001"
    with pytest.raises(Checkpoint2PolicyViolation):
        sanitize_shell_descriptor({**shell, "private_text": "forbidden"})
    body = {"alias_uri": ALIASES[1], "source_sha256": SHA, "profile_id": "BODY001", "slide_size": {"width": 13.333, "height": 7.5}, "slide_count": 1, "candidate_families": [], "body_measurements": []}
    assert sanitize_body_descriptor(body)["profile_id"] == "BODY001"
    with pytest.raises(Checkpoint2PolicyViolation):
        sanitize_body_descriptor({**body, "shell_primitives": []})


def test_private_unapproved_provider_creates_no_render_and_blocks_review(tmp_path: Path):
    run = Checkpoint2Run.start(pre_open_passed=True, private_root=tmp_path / "raw")
    assert run.private_render_review({"image_capable": True, "approved_for_private_exemplars": False}) == "blocked_visual_review"
    assert run.evidence.private_renders_created == 0


def test_approved_synthetic_provider_records_render_delete_lifecycle(tmp_path: Path):
    run = Checkpoint2Run.start(pre_open_passed=True, private_root=tmp_path / "raw")
    assert run.private_render_review({"image_capable": True, "approved_for_private_exemplars": True, "private_content_allowed": True, "hash_binding_supported": True, "egress_mode": "local_only", "retention_class": "ephemeral", "supported_input_forms": ["local_private_handle"]}) == "reviewed_ephemerally"
    assert (run.evidence.private_renders_created, run.evidence.private_renders_deleted, run.evidence.private_renders_retained) == (1, 1, 0)


def test_checkpoint_two_qa_rejects_literal_status_or_retained_render(tmp_path: Path):
    run = Checkpoint2Run.start(pre_open_passed=True, private_root=tmp_path / "raw")
    run.evidence.record_pre_open_gate("CP2-PRE-1", "pass")
    run.evidence.record_pre_open_gate("CP2-PRE-2", "pass")
    run.evidence.private_renders_created = 1
    run.evidence.private_renders_retained = 1
    record = run.qa_record()
    assert record["aggregate_status"] == "fail"
    record["aggregate_status"] = "pass"
    assert "CP2-QA-AGGREGATE-NONDERIVED" in validate_checkpoint2_qa(record)


def test_checkpoint_two_build_produces_only_sanitized_descriptors(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    qa = build_checkpoint2(repository_root=ROOT, local_aliases=_alias_mapping(tmp_path), private_root=tmp_path / "raw", artifact_root=artifact_root)
    assert qa["aggregate_status"] == "pass"
    assert {path.name for path in artifact_root.iterdir()} == {
        "sanitized-exemplar-manifest.json", "sanitized-shell-structural-descriptors.json",
        "sanitized-body-structural-descriptors.json", "checkpoint-2-qa.json",
    }
