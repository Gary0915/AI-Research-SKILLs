import copy
import json
from pathlib import Path

import pytest
from pptx import Presentation

from thesis_deck_system.build import ARTIFACTS, PROJECT, ROOT, build
from thesis_deck_system.contracts import SchemaRegistry
from thesis_deck_system.fixture import load_fixture
from thesis_deck_system.ledger import Ledger
from thesis_deck_system.pptx import PythonPptxAssembler, audit_pptx
from thesis_deck_system.qa import run_pipeline
from thesis_deck_system.slides import compile_slide
from thesis_deck_system.template import create_synthetic_template, profile_template


def _stage_status(report: dict, order: int) -> str:
    return report["pipeline"][order - 1]["status"]


def test_template_profile_runtime_index_matches_part_path_and_corruption_blocks(tmp_path: Path):
    template = create_synthetic_template(tmp_path / "template.pptx")
    profile_path = tmp_path / "template-profile.json"
    profile = profile_template(template, profile_path)
    prs = Presentation(template)

    assert [record["layout_path"] for record in profile["layouts"]] == [
        layout.part.partname.lstrip("/") for layout in prs.slide_layouts
    ]
    for index, record in enumerate(profile["layouts"]):
        assert record["layout_index"] == index

    spec = compile_slide("B001", "observation", "photo_observation", 1)
    broken = copy.deepcopy(profile)
    broken["semantic_roles"]["photo_observation"]["layout_path"] = "ppt/slideLayouts/slideLayout999.xml"
    profile_path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match="layout identity mismatch"):
        PythonPptxAssembler().assemble(template, [spec], tmp_path / "broken.pptx")
    broken = copy.deepcopy(profile)
    broken["semantic_roles"]["photo_observation"]["layout_index"] = 2
    profile_path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match="layout identity mismatch"):
        PythonPptxAssembler().assemble(template, [spec], tmp_path / "broken-index.pptx")


def test_build_compiles_first_and_revised_science_from_materialized_states():
    build()
    first_state = json.loads((ARTIFACTS / "materialized-first.json").read_text(encoding="utf-8"))
    revised_state = json.loads((ARTIFACTS / "materialized-revised.json").read_text(encoding="utf-8"))
    first_specs = json.loads((ARTIFACTS / "slide-specs-first.json").read_text(encoding="utf-8"))
    revised_specs = json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8"))

    assert first_specs[0]["content"]["observation"] == first_state["stages"]["ST-OBS"]["data"]["observation"]
    assert first_specs[1]["content"]["discussion"] == first_state["stages"]["ST-DISC"]["data"]["interpretation"]
    assert first_specs[1]["content"]["decision"] == first_state["decisions"]["D001"]["rationale"]
    assert revised_specs[1]["content"]["discussion"] == revised_state["stages"]["ST-DISC"]["data"]["interpretation"]
    assert revised_specs[1]["content"]["decision"] == revised_state["decisions"]["D002"]["rationale"]
    assert revised_specs[1]["content"]["decision"] != revised_state["decisions"]["D001"]["rationale"]
    assert "2026-09-10T09:00:00Z" in revised_specs[1]["content"]["next_step"]


def test_nested_contracts_reject_malformed_bindings_manifest_and_provenance():
    build()
    registry = SchemaRegistry(ROOT / "thesis-deck-system/schemas")
    spec = json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8"))[1]
    manifest = json.loads((ARTIFACTS / "MASTER-PHASE1-REVISED.manifest.json").read_text(encoding="utf-8"))
    asset = json.loads((ARTIFACTS / "plots/A001.asset.json").read_text(encoding="utf-8"))

    bad_spec = copy.deepcopy(spec)
    bad_spec["speaker_notes"]["source_refs"] = ["not-evidence"]
    assert registry.errors("slide-spec", bad_spec)
    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["slides"][0]["block_ref"] = {"block_id": "not-a-block", "revision": "one"}
    assert registry.errors("deck-manifest", bad_manifest)
    bad_asset = copy.deepcopy(asset)
    del bad_asset["generator"]["script_sha256"]
    assert registry.errors("asset-manifest", bad_asset)


def test_stage3_checks_nested_plot_provenance_and_stage4_uses_real_meeting_delta():
    build()
    bundle = load_fixture(PROJECT)
    bundle["assets"] = [json.loads((ARTIFACTS / f"plots/A00{i}.asset.json").read_text(encoding="utf-8")) for i in (1, 2)]
    bundle["slide_specs"] = json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8"))
    bundle["deck_manifests"] = [json.loads((ARTIFACTS / "MASTER-PHASE1-REVISED.manifest.json").read_text(encoding="utf-8"))]
    bundle["template_profiles"] = [json.loads((ARTIFACTS / "template-profile.json").read_text(encoding="utf-8"))]
    bundle["meeting_projection"] = json.loads((ARTIFACTS / "meeting-delta.json").read_text(encoding="utf-8"))
    bundle["_repo_root"] = str(ROOT)
    bundle["_schema_dir"] = str(ROOT / "thesis-deck-system/schemas")
    ledger = Ledger.load(ARTIFACTS / "ledger-events.json")
    audit = audit_pptx(ARTIFACTS / "master_revised_build.pptx", ARTIFACTS / "synthetic_native_template.pptx", bundle["template_profiles"][0])

    tampered = copy.deepcopy(bundle)
    tampered["assets"][0]["generator"]["script_sha256"] = "0" * 64
    report = run_pipeline(bundle=tampered, ledger=ledger, specs=tampered["slide_specs"], structural_audit=audit, professor_profile=tampered["professor_profiles"][0], render_evidence={})
    assert _stage_status(report, 3) == "fail"

    lost = copy.deepcopy(bundle)
    lost["meeting_projection"]["included_action_ids"] = []
    report = run_pipeline(bundle=lost, ledger=ledger, specs=lost["slide_specs"], structural_audit=audit, professor_profile=lost["professor_profiles"][0], render_evidence={})
    assert _stage_status(report, 4) == "fail"


def test_structural_audit_proves_layout_master_notes_and_real_template_immutability():
    build()
    profile = json.loads((ARTIFACTS / "template-profile.json").read_text(encoding="utf-8"))
    specs = json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8"))
    audit = audit_pptx(ARTIFACTS / "master_revised_build.pptx", ARTIFACTS / "synthetic_native_template.pptx", profile, specs)
    generated = audit["generated_slides"]

    assert len(generated) == 2
    assert all(item["layout_master_role_match"] for item in generated)
    assert generated[0]["expected_semantic_role"] == "photo_observation"
    assert generated[0]["note_source_refs"] == ["E002"]
    assert generated[1]["note_source_refs"] == ["E001", "E003"]
    assert audit["source_template_sha256_before"] == audit["source_template_sha256_after"]
    assert audit["source_template_unchanged"] is True


def test_stage7_validates_inspection_entries_images_and_montages(tmp_path: Path):
    build()
    bundle = load_fixture(PROJECT)
    bundle["_repo_root"] = str(ROOT)
    bundle["_schema_dir"] = str(ROOT / "thesis-deck-system/schemas")
    inspection = tmp_path / "inspection.json"
    inspection.write_text(json.dumps({"checked_by": "reviewer", "slides": []}), encoding="utf-8")
    report = run_pipeline(
        bundle=bundle,
        ledger=Ledger.load(ARTIFACTS / "ledger-events.json"),
        specs=json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8")),
        structural_audit={},
        professor_profile=bundle["professor_profiles"][0],
        render_evidence={"inspection_record": inspection.as_posix(), "render_paths": [], "montage_paths": []},
    )
    assert _stage_status(report, 7) == "fail"


def test_stage6_rejects_layout_or_notes_source_mismatch():
    build()
    bundle = load_fixture(PROJECT)
    bundle["assets"] = [json.loads((ARTIFACTS / f"plots/A00{i}.asset.json").read_text(encoding="utf-8")) for i in (1, 2)]
    specs = json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8"))
    profile = json.loads((ARTIFACTS / "template-profile.json").read_text(encoding="utf-8"))
    bundle.update({"slide_specs": specs, "template_profiles": [profile], "meeting_projection": json.loads((ARTIFACTS / "meeting-delta.json").read_text(encoding="utf-8")), "_repo_root": str(ROOT), "_schema_dir": str(ROOT / "thesis-deck-system/schemas")})
    audit = audit_pptx(ARTIFACTS / "master_revised_build.pptx", ARTIFACTS / "synthetic_native_template.pptx", profile, specs)

    for field in ("layout_master_role_match", "notes_source_match"):
        broken = copy.deepcopy(audit)
        broken["generated_slides"][0][field] = False
        report = run_pipeline(bundle=bundle, ledger=Ledger.load(ARTIFACTS / "ledger-events.json"), specs=specs, structural_audit=broken, professor_profile=bundle["professor_profiles"][0], render_evidence={})
        assert _stage_status(report, 6) == "fail"


def test_stage7_rejects_blank_render_failed_entry_and_missing_montage(tmp_path: Path):
    from PIL import Image, ImageDraw

    build()
    specs = json.loads((ARTIFACTS / "slide-specs-revised.json").read_text(encoding="utf-8"))
    bundle = load_fixture(PROJECT)
    bundle.update({"_repo_root": str(ROOT), "_schema_dir": str(ROOT / "thesis-deck-system/schemas")})
    valid = tmp_path / "valid.png"
    image = Image.new("RGB", (1280, 720), "white")
    ImageDraw.Draw(image).rectangle((100, 100, 600, 500), fill="navy")
    image.save(valid)
    blank = tmp_path / "blank.png"
    Image.new("RGB", (1280, 720), "white").save(blank)
    montage = tmp_path / "montage.png"
    image.save(montage)
    inspection = tmp_path / "inspection.json"

    def status(entries, montages):
        inspection.write_text(json.dumps({"checked_by": "reviewer", "slides": entries}), encoding="utf-8")
        report = run_pipeline(bundle=bundle, ledger=Ledger.load(ARTIFACTS / "ledger-events.json"), specs=specs, structural_audit={}, professor_profile=bundle["professor_profiles"][0], render_evidence={"inspection_record": inspection.as_posix(), "montage_paths": montages})
        return _stage_status(report, 7)

    entries = [{"slide_id": spec["slide_id"], "render_path": valid.as_posix(), "checks": ["visual"], "observations": "inspected", "status": "pass"} for spec in specs]
    broken = copy.deepcopy(entries); broken[0]["render_path"] = blank.as_posix()
    assert status(broken, [montage.as_posix(), montage.as_posix()]) == "fail"
    broken = copy.deepcopy(entries); broken[0]["status"] = "fail"
    assert status(broken, [montage.as_posix(), montage.as_posix()]) == "fail"
    assert status(entries, [montage.as_posix(), (tmp_path / "missing.png").as_posix()]) == "fail"
