"""Render and inspect the Phase 2 acceptance deck without changing its PPTX backend."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw

from .context import ProjectContext
from .pptx import PythonPptxAssembler
from .qa2 import run_visual_qa_v2
from .pptx import audit_pptx


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def _montage(paths: list[Path], output: Path) -> None:
    tiles: list[Image.Image] = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((640, 360))
        tile = Image.new("RGB", (660, 400), "white")
        tile.paste(image, ((660 - image.width) // 2, 16))
        ImageDraw.Draw(tile).text((12, 376), path.name, fill="black")
        tiles.append(tile)
    montage = Image.new("RGB", (1320, ((len(tiles) + 1) // 2) * 400), "#e4e7ec")
    for index, tile in enumerate(tiles):
        montage.paste(tile, ((index % 2) * 660, (index // 2) * 400))
    montage.save(output)


def render_phase2(output_root: Path) -> dict:
    """Render every slide through LibreOffice and persist executed visual QA evidence."""
    output_root = Path(output_root)
    deck = output_root / "acceptance-deck.pptx"
    specs = json.loads((output_root / "slide-specs.json").read_text(encoding="utf-8"))
    render_dir = output_root / "render"
    render_dir.mkdir(exist_ok=True)
    compat = output_root / "acceptance-deck-render-compat.pptx"
    # Use the same registered assembler with its raster fallbacks for the
    # renderer-only copy; the acceptance deck itself retains SVG OpenXML links.
    PythonPptxAssembler().assemble(output_root / "synthetic-template.pptx", specs, compat, attach_svg=False, project_context=ProjectContext(output_root))
    native_soffice = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
    soffice = str(native_soffice) if native_soffice.is_file() else shutil.which("soffice")
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        raise RuntimeError("render prerequisites unavailable: soffice and pdftoppm are required")
    conversion = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(render_dir), str(compat)], capture_output=True, text=True)
    if conversion.returncode:
        raise RuntimeError(f"LibreOffice render failed: {conversion.stderr or conversion.stdout}")
    pdf = render_dir / "acceptance-deck-render-compat.pdf"
    subprocess.run([pdftoppm, "-png", "-r", "144", str(pdf), str(render_dir / "slide")], check=True, capture_output=True, text=True)
    all_renders = sorted(render_dir.glob("slide-*.png"), key=lambda item: int(item.stem.rsplit("-", 1)[1]))
    if len(all_renders) < len(specs):
        raise RuntimeError(f"rendered slide count mismatch: {len(all_renders)} < {len(specs)}")
    # The synthetic template contributes two native exemplar slides before the
    # 18 generated specs. They are included in the full montage, while QA maps
    # the final generated pages one-to-one to their Slide Specs.
    renders = all_renders[-len(specs):]
    render_paths = {spec["slide_id"]: path for spec, path in zip(specs, renders)}
    # LibreOffice/Poppler produces a 1921×1080 raster from a 13.333" slide at
    # 144 DPI; this fixed renderer output is verified for every generated page.
    structural_audit = json.loads((output_root / "structural-audit.json").read_text(encoding="utf-8"))
    visual = run_visual_qa_v2(specs, render_paths, expected_size=(1921, 1080), structural_audit=structural_audit)
    observation_by_id = {item["slide_id"]: item for item in visual.get("slide_observations", [])}
    inspections = []
    for spec in specs:
        inspections.append({"slide_id": spec["slide_id"], "render_path": render_paths[spec["slide_id"]].relative_to(output_root).as_posix(), "checks": visual["executed_checks"], "observations": observation_by_id.get(spec["slide_id"], {}), "status": "pass" if not any(item["path"] == spec["slide_id"] for item in visual["findings"]) else "fail"})
    inspection = {"inspection_schema_version": "1.0.0", "checked_by": "Codex Phase 2 render QA", "status": "pass" if visual["status"] == "pass" else "fail", "slides": inspections, "visual_qa": visual}
    _write(output_root / "visual-inspection.json", inspection)
    persisted_inspection = json.loads((output_root / "visual-inspection.json").read_text(encoding="utf-8"))
    inspection_valid = len(persisted_inspection.get("slides", [])) == len(specs) and all(item.get("status") == "pass" and Path(output_root / item.get("render_path", "")).is_file() and isinstance(item.get("observations"), dict) and item["observations"].get("dominant_visual") for item in persisted_inspection["slides"])
    if not inspection_valid:
        raise RuntimeError("persisted visual inspection record failed validation")
    _montage(all_renders, render_dir / "full-deck-montage.png")
    changed = [render_paths[spec["slide_id"]] for spec in specs if spec.get("hypothesis_layer_ref") == "H002"]
    _montage(changed, render_dir / "h02-changed-slide-montage.png")
    fishbones = [render_paths[spec["slide_id"]] for spec in specs if spec.get("semantic_role") == "fishbone_locator"]
    _montage(fishbones, render_dir / "fishbone-comparison-montage.png")
    transitions = [render_paths[spec["slide_id"]] for spec in specs if spec.get("semantic_role") == "hypothesis_transition"]
    _montage(transitions, render_dir / "transition-montage.png")
    visual["inspection_record_valid"] = inspection_valid
    return {"visual": visual, "render_paths": [path.relative_to(output_root).as_posix() for path in renders], "all_render_paths": [path.relative_to(output_root).as_posix() for path in all_renders], "inspection": "visual-inspection.json", "inspection_record_valid": inspection_valid, "montages": ["render/full-deck-montage.png", "render/h02-changed-slide-montage.png", "render/fishbone-comparison-montage.png", "render/transition-montage.png"]}
