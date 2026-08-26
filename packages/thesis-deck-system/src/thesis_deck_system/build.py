"""End-to-end synthetic Phase 1 build and evidence generation."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

from .plotting import build_plot
from .pptx import PythonPptxAssembler, audit_pptx
from .projections import meeting_delta
from .qa import run_pipeline
from .slides import compile_slide
from .template import create_synthetic_template, profile_template


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "thesis-deck-system" / "examples" / "synthetic-project"
ARTIFACTS = ROOT / "thesis-deck-system" / "artifacts" / "phase1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _montage(images: list[Path], output: Path) -> None:
    from PIL import Image, ImageDraw
    thumbs = []
    for image in images:
        tile = Image.open(image).convert("RGB")
        tile.thumbnail((640, 360))
        canvas = Image.new("RGB", (660, 400), "white")
        canvas.paste(tile, ((660 - tile.width) // 2, 20))
        ImageDraw.Draw(canvas).text((12, 375), image.name, fill="black")
        thumbs.append(canvas)
    cols = 2
    montage = Image.new("RGB", (cols * 660, ((len(thumbs) + cols - 1) // cols) * 400), "#dddddd")
    for index, tile in enumerate(thumbs):
        montage.paste(tile, ((index % cols) * 660, (index // cols) * 400))
    output.parent.mkdir(parents=True, exist_ok=True)
    montage.save(output)


def build() -> dict:
    if ARTIFACTS.exists():
        shutil.rmtree(ARTIFACTS)
    ARTIFACTS.mkdir(parents=True)
    template = create_synthetic_template(ARTIFACTS / "synthetic_native_template.pptx")
    profile = profile_template(template, ARTIFACTS / "template-profile.json")
    plot = build_plot(PROJECT / "measurements.csv", ARTIFACTS / "plots")
    specs_first = [compile_slide("B001", "observation", "photo_observation", 4), compile_slide("B001", "result", "hero_plot_discussion", 4)]
    specs_first[1]["placements"][0]["asset_path"] = str(plot["png"])
    assembler = PythonPptxAssembler()
    first = ARTIFACTS / "master_first_build.pptx"
    assembler.assemble(template, specs_first, first)
    specs_revised = [compile_slide("B001", "observation", "photo_observation", 6), compile_slide("B001", "result", "hero_plot_discussion", 6, revision=2)]
    specs_revised[1]["placements"][0]["asset_path"] = str(plot["png"])
    revised = ARTIFACTS / "master_revised_build.pptx"
    assembler.assemble(template, specs_revised, revised)
    events = [
        {"cursor": 1, "event_type": "block_created", "payload": {"block_id": "B001", "revision": 1}},
        {"cursor": 2, "event_type": "action_committed", "payload": {"action_item_id": "NS001", "status": "planned", "owner": "researcher", "target_window": "2026-09-02", "source_decision_ref": "D001", "parallelizable": True, "workstream": "synthetic-microscopy"}},
        {"cursor": 3, "event_type": "decision_recorded", "payload": {"decision_id": "D001", "choice": "partial_go"}},
        {"cursor": 4, "event_type": "slide_spec_compiled", "payload": {"block_id": "B001", "revision": 1}},
        {"cursor": 5, "event_type": "stage_revised", "payload": {"block_id": "B001", "revision": 2}},
        {"cursor": 6, "event_type": "action_status_changed", "payload": {"action_item_id": "NS001", "status": "in_progress"}},
    ]
    (ARTIFACTS / "ledger-events.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    meeting = meeting_delta(events, since_cursor=4)
    (ARTIFACTS / "meeting-delta.json").write_text(json.dumps(meeting, indent=2), encoding="utf-8")
    manifests = []
    for deck_id, path, cursor, revision in [("MASTER-PHASE1-FIRST", first, 4, 1), ("MASTER-PHASE1-REVISED", revised, 6, 2)]:
        manifest = {"schema_version": "1.0.0", "deck_id": deck_id, "deck_kind": "master", "title": "Synthetic Thesis Research", "template_profile_ref": {"profile_id": profile["profile_id"], "version": profile["version"]}, "professor_profile_ref": {"profile_id": "PROF-SYNTH-001", "version": "1.0.0"}, "source_event_cursor": cursor, "build_id": f"BUILD-{deck_id}", "build_tool_version": "0.1.0", "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "projection": {"query": "master(all_blocks, preserve_history=true)"}, "slides": [{"ordinal": 1, "slide_id": spec["slide_id"], "spec_revision": spec["revision"], "story_visibility": "main"} for spec in (specs_first if revision == 1 else specs_revised)], "outputs": {"pptx": path.as_posix(), "pptx_sha256": _sha(path)}, "qa_report_refs": [f"QA-{deck_id}"]}
        manifest_path = ARTIFACTS / f"{deck_id}.manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        manifests.append(manifest)
    first_audit = audit_pptx(first)
    revised_audit = audit_pptx(revised)
    qa = run_pipeline(critical_findings=[], native_available=False)
    qa.update({"qa_report_id": "QA-MASTER-PHASE1-REVISED", "build_id": "BUILD-MASTER-PHASE1-REVISED", "deck_id": "MASTER-PHASE1-REVISED", "artifacts": {"pptx": revised.as_posix(), "template_profile": (ARTIFACTS / "template-profile.json").as_posix(), "plot_svg": plot["svg"].as_posix(), "plot_png": plot["png"].as_posix(), "meeting_delta": (ARTIFACTS / "meeting-delta.json").as_posix()}, "structural_audit": revised_audit, "native_status": "blocked_environment"})
    (ARTIFACTS / "qa-report.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    return {"template": template, "profile": profile, "plot": plot, "first": first, "revised": revised, "first_audit": first_audit, "revised_audit": revised_audit, "meeting": meeting, "qa": qa, "manifests": manifests}
