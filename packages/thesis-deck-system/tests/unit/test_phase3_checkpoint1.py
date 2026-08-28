"""Synthetic-only Phase 3 Checkpoint 1 contract and privacy tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from thesis_deck_system.contracts import SchemaRegistry
from thesis_deck_system.concept_images import validate_concept_provider
from thesis_deck_system.image_review import preflight_image_review
from thesis_deck_system.phase3_contracts import (
    canonical_observation_catalogs,
    validate_fabrication_process,
    validate_observation_visual_binding,
    validate_skill_routing,
)
from thesis_deck_system.phase3_checkpoint import (
    Checkpoint1ExecutionEvidence,
    Checkpoint1PolicyViolation,
    build_checkpoint1_qa,
    checkpoint1_qa_record,
    execute_checkpoint1_owning_checks,
    validate_checkpoint1_qa,
    write_checkpoint1_qa,
)
from thesis_deck_system.phase3_privacy import (
    PrivacyViolation,
    PrivateProfileStore,
    RepositoryPrivacyScanner,
    sanitize_profile,
)


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = ROOT / "thesis-deck-system" / "schemas"
SHA = "a" * 64


def _registry() -> SchemaRegistry:
    return SchemaRegistry(SCHEMA_DIR, include_phase3=True)


def _provider(**changes: object) -> dict:
    value = {
        "provider_id": "synthetic_image_reviewer",
        "image_capable": True,
        "hash_binding_supported": True,
        "private_content_allowed": True,
        "approved_for_private_exemplars": True,
        "egress_mode": "local_only",
        "retention_class": "ephemeral",
        "supported_input_forms": ["repository_relative_path", "local_private_handle"],
    }
    value.update(changes)
    return value


def _figure_manifest(figure_type: str, artifact_kind: str, artifact: dict) -> dict:
    return {
        "schema_version": "3.0.0",
        "figure_output_id": "FOM001",
        "figure_id": "FIG001",
        "figure_type": figure_type,
        "primary_artifact_kind": artifact_kind,
        "renderer": "synthetic_renderer",
        "source_spec_sha256": SHA,
        "provenance_refs": ["E001"],
        "style_profile_ref": "VSP001",
        "evidence_status": (
            "empirical" if figure_type == "real_photo" else
            "literature_evidence" if figure_type == "literature_figure" else
            "synthetic_test_evidence" if figure_type == "scientific_plot" else
            "non_evidence"
        ),
        "primary_artifact": artifact,
        "output_part_lineage": [{
            "real_photo": "source_evidence",
            "literature_figure": "extracted_source",
            "native_shape_figure": "native_plan",
        }.get(figure_type, "generated")],
    }


def _evidence_card(evidence_id: str, kind: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "evidence_id": evidence_id,
        "kind": kind,
        "title": "Synthetic canonical evidence",
        "provenance": "synthetic_test_only",
        "source": {"source_id": "S001", "uri": "fixtures/synthetic.json", "sha256": SHA},
        "claim_support_refs": [],
        "claim_contradict_refs": [],
        "scope": {},
        "verification": {"status": "synthetic_test_only"},
    }


def _checkpoint_evidence(*, failed_check: str | None = None) -> Checkpoint1ExecutionEvidence:
    def check(check_id: str):
        if check_id == failed_check:
            raise RuntimeError("synthetic owner failure")
    return execute_checkpoint1_owning_checks({
        check_id: (lambda check_id=check_id: check(check_id))
        for check_id in Checkpoint1ExecutionEvidence.required_check_ids()
    })


def test_private_root_rejects_repo_root_and_symlink_before_any_source_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(PrivacyViolation, match="outside"):
        PrivateProfileStore(ROOT, repository_root=ROOT)
    redirect = tmp_path / "redirect"
    monkeypatch.setattr(Path, "is_symlink", lambda path: path.name == "redirect")
    with pytest.raises(PrivacyViolation, match="symlink"):
        PrivateProfileStore(redirect, repository_root=ROOT)


def test_private_root_requires_gitignore_and_untracked_status(tmp_path: Path):
    root = ROOT / ".phase3-test-unignored"
    with pytest.raises(PrivacyViolation, match="ignored"):
        PrivateProfileStore(root, repository_root=ROOT)


def test_ignored_private_root_is_valid_before_any_private_alias_operation():
    store = PrivateProfileStore(ROOT / ".private" / "phase3" / "synthetic-run", repository_root=ROOT)
    assert store.retention_policy() == {
        "root_kind": "ignored_local",
        "cleanup_required": True,
        "private_source_open_permitted": False,
    }
    prepared = store.prepare_for_future_open()
    assert prepared["writable"] is True


@pytest.mark.parametrize("payload", [
    {"path": "D:/PRIVATE_CANARY/slide.pptx"},
    {"note": "PRIVATE_TEXT_CANARY"},
    {"speaker_notes": "PRIVATE_NOTES_CANARY"},
    {"author": "PRIVATE_AUTHOR_CANARY"},
    {"company": "PRIVATE_COMPANY_CANARY"},
    {"media_name": "PRIVATE_MEDIA_CANARY"},
    {"relationship": "<Relationship Target='x'/>"},
    {"url": "https://private.example.test/record"},
])
def test_sanitizer_and_scanner_detect_synthetic_private_canaries(payload: dict):
    with pytest.raises(PrivacyViolation):
        sanitize_profile(payload)
    findings = RepositoryPrivacyScanner().scan_mapping(payload, location="synthetic.json")
    assert findings


def test_sanitizer_constructs_only_allowlisted_profile_fields_and_fails_unknown_keys():
    raw = {
        "alias_uri": "private://template_primary_1",
        "resolved_status": "resolved",
        "source_sha256": SHA,
        "sanitized_profile_id": "SP001",
        "slide_size": {"width": 13.333, "height": 7.5},
    }
    clean = sanitize_profile(raw)
    assert clean == raw
    with pytest.raises(PrivacyViolation, match="unknown"):
        sanitize_profile({**raw, "untyped_private_field": "nope"})


@pytest.mark.parametrize("leak", [
    "D:\\\\PRIVATE_ROOT_CANARY\\\\slide.pptx",
    "D:/PRIVATE_ROOT_CANARY/slide.pptx",
    "/mnt/d/PRIVATE_ROOT_CANARY/slide.pptx",
    "\\\\PRIVATE_SERVER_CANARY\\\\share\\\\slide.pptx",
])
def test_scanner_detects_windows_unc_and_wsl_private_path_forms_without_echoing_value(leak: str):
    findings = RepositoryPrivacyScanner(private_root_signatures=["PRIVATE_ROOT_CANARY", "PRIVATE_SERVER_CANARY"]).scan_mapping(
        {"nested": [leak]}, location="synthetic.json"
    )
    assert findings
    assert all(leak not in str(finding) for finding in findings)


@pytest.mark.parametrize("basename", ["PRIVATE_SOURCE_CANARY.pptx", "PRIVATE_RENDER_CANARY.png", "PRIVATE_MEDIA_CANARY.jpg"])
def test_scanner_detects_configured_private_basenames_without_echoing_value(basename: str):
    findings = RepositoryPrivacyScanner(forbidden_basenames=[basename]).scan_mapping(
        {"nested": [basename]}, location="synthetic.json"
    )
    assert findings
    assert all(basename not in str(finding) for finding in findings)


def test_scanner_detects_staged_private_pptx_and_render_candidates(tmp_path: Path):
    scanner = RepositoryPrivacyScanner()
    pptx = tmp_path / "PRIVATE_CANARY.pptx"
    render = tmp_path / "private-render.png"
    pptx.write_bytes(b"PK\x03\x04synthetic")
    render.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic")
    findings = scanner.scan_paths([pptx, render], location_root=tmp_path)
    assert {item.classification for item in findings} >= {"private_pptx_candidate", "private_render_candidate"}


def test_repository_scanner_checks_the_actual_staged_file_list(monkeypatch: pytest.MonkeyPatch):
    def staged_git(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, "synthetic/PRIVATE_CANARY.pptx\nsynthetic/private-render.png\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner().scan_staged(ROOT)
    assert {item.classification for item in findings} == {"private_pptx_candidate", "private_render_candidate"}


def test_repository_scanner_reads_staged_text_content(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    candidate = tmp_path / "candidate.py"
    candidate.write_text("PRIVATE_AUTHOR_CANARY", encoding="utf-8")

    def staged_git(args, **kwargs):
        if args[1] == "show":
            return subprocess.CompletedProcess(args, 0, "PRIVATE_AUTHOR_CANARY", "")
        return subprocess.CompletedProcess(args, 0, "candidate.py\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner().scan_staged(tmp_path)
    assert {item.classification for item in findings} == {"private_text_canary"}


def test_repository_scanner_reads_staged_blob_not_safe_worktree_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    candidate = tmp_path / "candidate.md"
    candidate.write_text("safe working tree", encoding="utf-8")

    def staged_git(args, **kwargs):
        if args[1:4] == ["diff", "--cached", "--name-only"]:
            return subprocess.CompletedProcess(args, 0, "candidate.md\n", "")
        if args[1] == "show":
            return subprocess.CompletedProcess(args, 0, "D:/PRIVATE_ROOT_CANARY/staged.pptx", "")
        return subprocess.CompletedProcess(args, 1, "", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner(private_root_signatures=["PRIVATE_ROOT_CANARY"]).scan_staged(tmp_path)
    assert {item.classification for item in findings} == {"absolute_path"}


def test_repository_scanner_reads_staged_blob_as_utf8(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    def staged_git(args, **kwargs):
        if args[1] == "show":
            assert kwargs["encoding"] == "utf-8"
            assert kwargs["errors"] == "strict"
            return subprocess.CompletedProcess(args, 0, "synthetic non-ASCII ✓", "")
        return subprocess.CompletedProcess(args, 0, "candidate.md\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    assert RepositoryPrivacyScanner().scan_staged(tmp_path) == []


def test_repository_scanner_applies_configured_basename_to_staged_candidate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    def staged_git(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, "synthetic/EXEMPLAR_CANARY.png\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner(forbidden_basenames=["EXEMPLAR_CANARY.png"]).scan_staged(tmp_path)
    assert {item.classification for item in findings} == {"forbidden_private_basename"}


def test_repository_scanner_applies_private_root_signature_to_staged_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    def staged_git(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, "PRIVATE_ROOT_CANARY/neutral.md\n", "")

    monkeypatch.setattr("thesis_deck_system.phase3_privacy.subprocess.run", staged_git)
    findings = RepositoryPrivacyScanner(private_root_signatures=["PRIVATE_ROOT_CANARY"]).scan_staged(tmp_path)
    assert {item.classification for item in findings} == {"configured_private_root"}


def test_private_image_review_requires_full_capability_authorization():
    approved = preflight_image_review(_provider(), private_reference=True)
    assert approved.status == "approved"
    blocked = preflight_image_review(_provider(approved_for_private_exemplars=False), private_reference=True)
    assert blocked.status == "blocked_visual_review"
    assert "private authorization" in blocked.reason


def test_private_image_review_requires_an_authorized_private_input_form():
    empty = preflight_image_review(_provider(supported_input_forms=[]), private_reference=True)
    wrong = preflight_image_review(_provider(supported_input_forms=["repository_relative_path"]), private_reference=True)
    assert empty.status == "blocked_visual_review"
    assert wrong.status == "blocked_visual_review"


def test_provider_contract_schemas_are_registered_and_fail_closed():
    registry = _registry()
    assert registry.errors("image-review-provider", _provider()) == []
    assert registry.errors("image-review-provider", {**_provider(), "vendor": "forbidden"})
    assert registry.errors("concept-image-provider", {"provider_id": "synthetic_concept_provider", "image_capable": True, "generation_provenance_required": True, "allowed_evidence_statuses": ["non_evidence"]}) == []


@pytest.mark.parametrize("changes", [
    {"retention_class": "persistent"},
    {"egress_mode": "external_network"},
    {"hash_binding_supported": False},
])
def test_private_image_review_rejects_retention_egress_and_hash_failures(changes: dict):
    result = preflight_image_review(_provider(**changes), private_reference=True)
    assert result.status == "blocked_visual_review"


def test_sanitized_only_image_review_cannot_certify_private_fidelity():
    result = preflight_image_review(_provider(approved_for_private_exemplars=False), private_reference=False)
    assert result.status == "approved_sanitized_only"
    assert result.professor_fidelity_status == "blocked_visual_review"


def test_concept_provider_is_abstract_and_non_evidence_only():
    assert validate_concept_provider({
        "provider_id": "synthetic_concept_provider",
        "image_capable": True,
        "generation_provenance_required": True,
        "allowed_evidence_statuses": ["non_evidence"],
    }) == []
    errors = validate_concept_provider({
        "provider_id": "synthetic_concept_provider",
        "image_capable": True,
        "generation_provenance_required": True,
        "allowed_evidence_statuses": ["empirical"],
    })
    assert "P3-CONCEPT-EVIDENCE-STATUS" in errors


def test_figure_output_variants_validate_their_real_primary_identity():
    registry = _registry()
    cases = [
        _figure_manifest("vector_diagram", "svg_vector", {"path": "artifacts/cp1/diagram.svg", "sha256": SHA}),
        _figure_manifest("scientific_plot", "pdf_vector", {"path": "artifacts/cp1/plot.pdf", "sha256": SHA, "data_provenance_refs": ["E001"]}),
        _figure_manifest("real_photo", "source_evidence_asset", {"asset_id": "A001", "source_sha256": SHA, "evidence_card_ref": "E001"}),
        _figure_manifest("literature_figure", "extracted_source_figure", {"asset_id": "A002", "source_sha256": SHA, "evidence_card_ref": "E001", "citation_ref": "E001"}),
        _figure_manifest("native_shape_figure", "native_shape_plan", {"plan_id": "NSP001", "geometry_manifest_path": "artifacts/cp1/native.json", "geometry_manifest_sha256": SHA}),
    ]
    for value in cases:
        assert registry.errors("figure-output-manifest", value) == []


def test_figure_plan_spec_critic_and_style_contracts_reject_untyped_payloads():
    registry = _registry()
    plan = {
        "schema_version": "3.0.0", "figure_id": "FIG001", "figure_type": "vector_diagram", "scientific_purpose": "synthetic process", "evidence_status": "non_evidence", "source_refs": [], "claim_refs": [], "hypothesis_layer_ref": "H001", "research_block_refs": ["B001"], "director_skill": "fabrication-process-director", "renderer": "vector_builder", "ai_allowed": False, "source_requirement": "structured_spec", "canonical_output_kind": "svg_vector", "required_qa": ["figure_critic"], "handoff_cursor": 1,
    }
    assert registry.errors("figure-production-plan", plan) == []
    assert registry.errors("figure-production-plan", {**plan, "unknown": True})
    critic = {"schema_version": "3.0.0", "report_id": "FCR001", "figure_id": "FIG001", "output_manifest_ref": "FOM001", "executed_checks": ["provenance"], "findings": [], "status": "APPROVED_FIGURE"}
    assert registry.errors("figure-critic-report", critic) == []
    style = {"schema_version": "3.0.0", "style_profile_id": "VSP001", "status": "synthetic_checkpoint", "token_provenance": [{"token_id": "synthetic", "source_role": "synthetic_checkpoint"}], "material_tokens": {}, "arrow_tokens": {}, "emphasis_tokens": {}, "annotation_tokens": {}}
    assert registry.errors("visual-style-profile", style) == []


def test_figure_output_rejects_cross_class_masquerading_and_nonvector_plot():
    registry = _registry()
    masked = _figure_manifest("real_photo", "svg_vector", {"path": "artifacts/cp1/fake.svg", "sha256": SHA})
    raster_plot = _figure_manifest("scientific_plot", "png_preview", {"path": "artifacts/cp1/plot.png", "sha256": SHA})
    assert registry.errors("figure-output-manifest", masked)
    assert registry.errors("figure-output-manifest", raster_plot)


def test_evidence_figure_lineage_cannot_claim_generated_output():
    registry = _registry()
    photo = _figure_manifest("real_photo", "source_evidence_asset", {"asset_id": "A001", "source_sha256": SHA, "evidence_card_ref": "E001"})
    literature = _figure_manifest("literature_figure", "extracted_source_figure", {"asset_id": "A002", "source_sha256": SHA, "evidence_card_ref": "E001", "citation_ref": "E001"})
    photo["output_part_lineage"] = ["generated"]
    literature["output_part_lineage"] = ["generated"]
    assert registry.errors("figure-output-manifest", photo)
    assert registry.errors("figure-output-manifest", literature)


def test_concept_figure_is_non_evidence_and_cannot_support_scientific_claims():
    registry = _registry()
    concept = _figure_manifest("concept_illustration", "generated_non_evidence_substrate", {"asset_id": "A003", "generation_provenance_ref": "GEN001"})
    concept["evidence_status"] = "non_evidence"
    assert registry.errors("figure-output-manifest", concept) == []
    concept["evidence_status"] = "empirical"
    assert registry.errors("figure-output-manifest", concept)


def test_concept_scientific_figure_spec_cannot_be_empirical_or_claim_supporting():
    registry = _registry()
    spec = {
        "schema_version": "3.0.0", "figure_id": "FIG001", "figure_type": "concept_illustration", "scientific_purpose": "synthetic context", "evidence_status": "non_evidence", "source_refs": [], "claim_refs": [], "hypothesis_layer_ref": "H001", "research_block_refs": ["B001"], "director_skill": "concept-illustration-director", "renderer": "concept_provider", "style_profile_ref": "VSP001", "canvas": {"width": 100, "height": 100}, "components": [], "connections": [], "annotations": [], "labels": [], "visual_states": [], "provenance": {"source_cursor": 1}, "output_targets": ["generated_non_evidence_substrate"], "qa_requirements": ["provenance"],
    }
    assert registry.errors("scientific-figure-spec", spec) == []
    assert registry.errors("scientific-figure-spec", {**spec, "evidence_status": "empirical"})
    assert registry.errors("scientific-figure-spec", {**spec, "claim_refs": ["C001"]})


def test_observation_requires_real_empirical_evidence_and_keeps_concepts_auxiliary():
    measurement = _evidence_card("E001", "synthetic_measurement")
    output = _figure_manifest("scientific_plot", "svg_vector", {"path": "artifacts/cp1/plot.svg", "sha256": SHA, "data_provenance_refs": ["E001"]})
    catalog = canonical_observation_catalogs(_registry(), [measurement], [output])
    valid = {
        "observation_id": "OBS001",
        "empirical_evidence_required": True,
        "observation_evidence_ref": "E001",
        "observation_output_ref": "FOM001",
        "evidence_refs": ["E001"],
        "auxiliary_visuals": [{"figure_id": "FIGC01", "figure_type": "concept_illustration", "evidence_status": "non_evidence"}],
    }
    assert validate_observation_visual_binding(valid, catalog=catalog) == []
    generated = {**valid, "observation_evidence_ref": "E002", "evidence_refs": ["E002"]}
    assert "P3-OBSERVATION-EMPIRICAL-EVIDENCE-MISSING" in validate_observation_visual_binding(generated, catalog=catalog)
    missing = {**valid, "observation_evidence_ref": None, "evidence_refs": []}
    assert "P3-OBSERVATION-EMPIRICAL-EVIDENCE-MISSING" in validate_observation_visual_binding(missing, catalog=catalog)
    assert _registry().errors("observation-visual-binding", valid) == []


@pytest.mark.parametrize("spoofed_origin", ["measurement", "experimental_photo", "source_derived_scientific_visual"])
def test_observation_rejects_generated_concept_even_when_origin_is_spoofed(spoofed_origin: str):
    generated = _evidence_card("E002", "generated_context")
    generated["origin"] = spoofed_origin
    concept = _figure_manifest("concept_illustration", "generated_non_evidence_substrate", {"asset_id": "A003", "generation_provenance_ref": "GEN001"})
    concept["provenance_refs"] = ["E002"]
    with pytest.raises(ValueError, match="canonical Evidence"):
        canonical_observation_catalogs(_registry(), [generated], [concept])


def test_observation_rejects_canonical_generated_concept_when_bound_as_empirical():
    generated = _evidence_card("E002", "generated_context")
    concept = _figure_manifest("concept_illustration", "generated_non_evidence_substrate", {"asset_id": "A003", "generation_provenance_ref": "GEN001"})
    concept["provenance_refs"] = ["E002"]
    catalog = canonical_observation_catalogs(_registry(), [generated], [concept])
    binding = {
        "observation_id": "OBS002", "empirical_evidence_required": True,
        "observation_evidence_ref": "E002", "observation_output_ref": "FOM001",
        "evidence_refs": ["E002"], "auxiliary_visuals": [],
    }
    assert "P3-OBSERVATION-GENERATED-AS-EVIDENCE" in validate_observation_visual_binding(binding, catalog=catalog)


def test_observation_accepts_canonical_real_photo_evidence_binding():
    photo = _evidence_card("E003", "observation_photo")
    output = _figure_manifest("real_photo", "source_evidence_asset", {"asset_id": "A003", "source_sha256": SHA, "evidence_card_ref": "E003"})
    output["provenance_refs"] = ["E003"]
    catalog = canonical_observation_catalogs(_registry(), [photo], [output])
    binding = {
        "observation_id": "OBS003", "empirical_evidence_required": True,
        "observation_evidence_ref": "E003", "observation_output_ref": "FOM001",
        "evidence_refs": ["E003"], "auxiliary_visuals": [],
    }
    assert validate_observation_visual_binding(binding, catalog=catalog) == []


def test_observation_rejects_manifest_that_lies_about_primary_artifact_evidence_binding():
    measurement = _evidence_card("E001", "synthetic_measurement")
    output = _figure_manifest("scientific_plot", "svg_vector", {"path": "artifacts/cp1/plot.svg", "sha256": SHA, "data_provenance_refs": ["E999"]})
    catalog = canonical_observation_catalogs(_registry(), [measurement], [output])
    binding = {
        "observation_id": "OBS001", "empirical_evidence_required": True,
        "observation_evidence_ref": "E001", "observation_output_ref": "FOM001",
        "evidence_refs": ["E001"], "auxiliary_visuals": [],
    }
    assert "P3-OBSERVATION-PROVENANCE-MISMATCH" in validate_observation_visual_binding(binding, catalog=catalog)


def test_fabrication_process_preserves_order_unknowns_and_provenance():
    valid = {
        "process_id": "FP001",
        "process_kind": "fabrication_process",
        "provenance_refs": ["E001"],
        "steps": [
            {"ordinal": 1, "operation": "mix", "material_refs": ["M001"], "state_before": "precursors", "state_after": "mixture", "conditions": {"temperature_c": "unknown", "duration_min": "unknown"}},
            {"ordinal": 2, "operation": "cure", "material_refs": ["M001"], "state_before": "mixture", "state_after": "gel", "conditions": {"temperature_c": 25, "duration_min": 60}},
        ],
    }
    assert validate_fabrication_process(valid) == []
    mutated = {**valid, "steps": [valid["steps"][1], valid["steps"][0]]}
    assert "P3-FABRICATION-ORDER" in validate_fabrication_process(mutated)
    no_provenance = {**valid, "provenance_refs": []}
    assert "P3-FABRICATION-PROVENANCE-MISSING" in validate_fabrication_process(no_provenance)
    assert _registry().errors("fabrication-process", valid) == []


def test_fabrication_contract_does_not_allow_mechanism_or_measurement_substitution():
    mechanism = {"process_id": "FP001", "process_kind": "mechanism_diagram", "provenance_refs": ["E001"], "steps": []}
    measurement = {"process_id": "FP001", "process_kind": "experiment_schematic", "provenance_refs": ["E001"], "steps": []}
    assert "P3-FABRICATION-KIND" in validate_fabrication_process(mechanism)
    assert "P3-FABRICATION-KIND" in validate_fabrication_process(measurement)


def test_skill_routing_requires_bounded_fabrication_specialist_not_mechanism_substitution():
    routing = {
        "schema_version": "3.0.0",
        "skills": [{
            "skill_id": "fabrication-process-director",
            "trigger": "fabrication_process",
            "output_contract": "fabrication-process",
            "forbidden_responsibilities": ["mechanism_explanation", "measurement_schematic"],
            "handoff": "figure-critic",
            "qa_owner": "provenance-qa",
        }],
        "routes": [{"request_kind": "fabrication_process", "skill_id": "fabrication-process-director", "next_skill_id": "figure-critic"}],
    }
    assert validate_skill_routing(routing) == []
    assert _registry().errors("skill-routing", routing) == []
    routing["routes"][0]["skill_id"] = "mechanism-diagram-director"
    assert "P3-SKILL-ROUTING-FABRICATION" in validate_skill_routing(routing)


def test_checkpoint_qa_contract_proves_zero_private_operations():
    with pytest.raises(ValueError, match="canonical owning builder"):
        checkpoint1_qa_record(_checkpoint_evidence())


def test_checkpoint_qa_writer_emits_only_schema_valid_nonprivate_evidence(tmp_path: Path):
    output = tmp_path / "checkpoint-qa.json"
    with pytest.raises(ValueError, match="canonical owning builder"):
        write_checkpoint1_qa(output, execution_evidence=_checkpoint_evidence())


def test_checkpoint_guard_records_alias_resolution_attempt_before_blocking():
    evidence = Checkpoint1ExecutionEvidence.start()
    with pytest.raises(Checkpoint1PolicyViolation, match="alias resolution"):
        evidence.reject_private_alias_resolution("SYNTHETIC_ALIAS")
    assert evidence.real_private_alias_resolution_attempts == 1
    assert evidence.private_source_open_attempts == 0


def test_checkpoint_guard_records_private_source_open_attempt_before_blocking():
    evidence = Checkpoint1ExecutionEvidence.start()
    with pytest.raises(Checkpoint1PolicyViolation, match="source open"):
        evidence.reject_private_source_open("SYNTHETIC_SOURCE")
    assert evidence.private_source_open_attempts == 1
    assert evidence.real_private_alias_resolution_attempts == 0


def test_private_store_entrypoints_record_before_checkpoint_one_blocks_any_alias_or_source_operation():
    store = PrivateProfileStore(ROOT / ".private" / "phase3" / "guarded", repository_root=ROOT)
    evidence = Checkpoint1ExecutionEvidence.start()
    with pytest.raises(Checkpoint1PolicyViolation):
        store.resolve_private_alias("SYNTHETIC_ALIAS", execution_evidence=evidence)
    with pytest.raises(Checkpoint1PolicyViolation):
        store.open_private_source("SYNTHETIC_SOURCE", execution_evidence=evidence)
    assert evidence.real_private_alias_resolution_attempts == 1
    assert evidence.private_source_open_attempts == 1


def test_checkpoint_record_derives_nonzero_attempts_and_fails_aggregate_status():
    evidence = _checkpoint_evidence()
    with pytest.raises(Checkpoint1PolicyViolation):
        evidence.reject_private_alias_resolution("SYNTHETIC_ALIAS")
    assert evidence.real_private_alias_resolution_attempts == 1
    with pytest.raises(ValueError, match="canonical owning builder"):
        checkpoint1_qa_record(evidence)


def test_checkpoint_record_rejects_attempt_kind_that_does_not_match_derived_counter():
    record = json.loads((ROOT / "thesis-deck-system" / "artifacts" / "phase3" / "checkpoint-1-qa.json").read_text(encoding="utf-8"))
    record["execution_evidence"]["attempt_kinds"].append("private_alias_resolution")
    record["execution_evidence_sha256"] = hashlib.sha256(json.dumps(record["execution_evidence"], sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assert "CP1-QA-ATTEMPT-EVENT-COUNT" in validate_checkpoint1_qa(record)


def test_checkpoint_record_cannot_promote_failed_owning_check_to_pass():
    evidence = _checkpoint_evidence(failed_check="CP1-OBSERVATION-EVIDENCE")
    assert evidence.owning_checks["CP1-OBSERVATION-EVIDENCE"] == "fail"
    with pytest.raises(ValueError, match="canonical owning builder"):
        checkpoint1_qa_record(evidence)


def test_manual_checkpoint_record_without_execution_evidence_is_rejected():
    fabricated = {
        "schema_version": "3.1.0", "checkpoint_id": "PHASE_3_CHECKPOINT_1",
        "private_source_open_attempts": 0, "real_private_alias_resolution_attempts": 0,
        "privacy_root_status": "pass", "sanitizer_scanner_status": "pass",
        "provider_authorization_status": "pass", "figure_contract_status": "pass",
        "observation_evidence_status": "pass", "fabrication_contract_status": "pass",
        "phase1_phase2_regression_status": "pass", "aggregate_status": "pass",
    }
    assert _registry().errors("checkpoint-qa", fabricated)
    assert validate_checkpoint1_qa(fabricated)


def test_checkpoint_writer_rejects_unsealed_evidence_without_executed_owning_checks():
    with pytest.raises(ValueError, match="sealed"):
        checkpoint1_qa_record(Checkpoint1ExecutionEvidence.start())


def test_checkpoint_writer_rejects_manual_pass_map_and_boolean_seal_bypass():
    evidence = Checkpoint1ExecutionEvidence.start()
    evidence._owning_checks = {check_id: "pass" for check_id in Checkpoint1ExecutionEvidence.required_check_ids()}
    evidence._sealed = True
    with pytest.raises(ValueError, match="sealed"):
        checkpoint1_qa_record(evidence)


def test_checkpoint_execution_records_actual_owning_check_result_not_caller_status_literal():
    evidence = execute_checkpoint1_owning_checks({
        check_id: (lambda: (_ for _ in ()).throw(RuntimeError("synthetic owner failure"))) if check_id == "CP1-FIGURE-CONTRACTS" else (lambda: None)
        for check_id in Checkpoint1ExecutionEvidence.required_check_ids()
    })
    assert evidence.owning_checks["CP1-FIGURE-CONTRACTS"] == "fail"
    with pytest.raises(ValueError, match="canonical owning builder"):
        checkpoint1_qa_record(evidence)


def test_checkpoint_builder_executes_its_own_nonprivate_controls_before_writing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    output = tmp_path / "checkpoint-qa.json"
    monkeypatch.setattr("thesis_deck_system.phase3_checkpoint._run_phase1_phase2_regression", lambda root: None)
    record = build_checkpoint1_qa(output, repository_root=ROOT)
    assert record["aggregate_status"] == "pass"
    assert validate_checkpoint1_qa(record) == []


def test_public_generic_executor_cannot_self_certify_canonical_pass_record():
    evidence = execute_checkpoint1_owning_checks({check_id: (lambda: None) for check_id in Checkpoint1ExecutionEvidence.required_check_ids()})
    with pytest.raises(ValueError, match="canonical owning builder"):
        checkpoint1_qa_record(evidence)
