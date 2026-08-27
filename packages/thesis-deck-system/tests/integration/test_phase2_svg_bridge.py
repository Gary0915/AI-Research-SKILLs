from __future__ import annotations

import copy
import json
from pathlib import Path

from PIL import Image

from thesis_deck_system.context import ProjectContext
from thesis_deck_system.pptx import PythonPptxAssembler, audit_pptx
from thesis_deck_system.template import create_synthetic_template, profile_template


def _svg(path: Path, color: str) -> None:
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="240"><rect width="400" height="240" fill="{color}"/></svg>', encoding="utf-8")
    Image.new("RGB", (400, 240), color).save(path.with_suffix(".png"))


def _spec(slide_id: str, asset_id: str, svg_path: str) -> dict:
    return {
        "slide_id": slide_id, "native_layout_role": "content_academic", "recipe": "result_single",
        "semantic_role": "result_single", "title": {"text": slide_id},
        "content": {"body": "Synthetic scientific result"},
        "placements": [{"slot": "primary_figure", "asset_id": asset_id, "asset_path": svg_path}],
        "speaker_notes": {"source_refs": ["E101"], "text": "Synthetic fixture"},
    }


def test_svg_bridge_targets_each_owning_slide_after_reordering(tmp_path: Path):
    template = create_synthetic_template(tmp_path / "template.pptx")
    profile = profile_template(template, tmp_path / "template-profile.json")
    role = copy.deepcopy(profile["semantic_roles"]["photo_observation"])
    profile["semantic_roles"]["content_academic"] = role
    (tmp_path / "template-profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    first = tmp_path / "A901.svg"; second = tmp_path / "A902.svg"
    _svg(first, "#336699"); _svg(second, "#993333")
    context = ProjectContext(repo_root=tmp_path)
    specs = [_spec("S-H001-RESULT-01", "A901", "A901.svg"), _spec("S-H002-RESULT-01", "A902", "A902.svg")]
    output = tmp_path / "multi-svg.pptx"
    PythonPptxAssembler().assemble(template, list(reversed(specs)), output, project_context=context)
    audit = audit_pptx(output, template, profile, list(reversed(specs)))
    by_spec = {item["slide_spec_id"]: item for item in audit["generated_slides"]}
    assert by_spec["S-H001-RESULT-01"]["svg_asset_relationships"][0]["asset_id"] == "A901"
    assert by_spec["S-H002-RESULT-01"]["svg_asset_relationships"][0]["asset_id"] == "A902"
    assert all(item["referenced_in_slide"] for generated in by_spec.values() for item in generated["svg_asset_relationships"])
