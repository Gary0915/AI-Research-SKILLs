"""Synthetic native PowerPoint template creation and OpenXML profiling."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from pptx import Presentation
from pptx.util import Inches


NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def create_synthetic_template(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.5)
    title_layout = prs.slide_layouts[0]
    content_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(title_layout)
    slide.shapes.title.text = "Synthetic Native Template"
    slide.placeholders[1].text = "Redistributable test fixture — not laboratory data"
    slide = prs.slides.add_slide(content_layout)
    slide.shapes.title.text = "Representative content layout"
    slide.placeholders[1].text = "Native title/content placeholders"
    prs.save(path)
    return path


def profile_template(path: Path, output_path: Path) -> dict:
    prs = Presentation(path)
    masters = []
    layouts = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        for name in sorted(n for n in names if n.startswith("ppt/slideMasters/slideMaster") and n.endswith(".xml")):
            root = ET.fromstring(archive.read(name))
            masters.append({"path": name, "name": Path(name).stem, "relationship_ids": sorted({element.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id") for element in root.iter() if element.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")})})
        for name in sorted(n for n in names if n.startswith("ppt/slideLayouts/slideLayout") and n.endswith(".xml")):
            root = ET.fromstring(archive.read(name))
            placeholders = []
            for shape in root.findall(".//p:sp", NS):
                ph = shape.find(".//p:ph", NS)
                if ph is not None:
                    placeholders.append({"type": ph.attrib.get("type", "body"), "idx": ph.attrib.get("idx", "0")})
            layouts.append({"path": name, "name": Path(name).stem, "placeholders": placeholders})
        theme_fonts = []
        theme_colors = []
        theme_names = sorted(n for n in names if n.startswith("ppt/theme/") and n.endswith(".xml"))
        if theme_names:
            root = ET.fromstring(archive.read(theme_names[0]))
            theme_fonts = [node.attrib.get("typeface") for node in root.findall(".//a:latin", NS) if node.attrib.get("typeface")]
            theme_colors = [node.tag.rsplit("}", 1)[-1] for node in root.findall(".//a:clrScheme/*", NS)]
    profile = {"schema_version": "1.0.0", "profile_id": "TP-SYNTH-001", "version": "1.0.0", "source_path": path.as_posix(), "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "slide_size": {"width_emu": prs.slide_width, "height_emu": prs.slide_height, "aspect_ratio": "16:9"}, "masters": masters, "layouts": layouts, "theme": {"major_fonts": theme_fonts[:1], "minor_fonts": theme_fonts[1:2], "colors": theme_colors}, "semantic_roles": {"photo_observation": {"layout_name_contains": "slideLayout2", "required_placeholders": ["title", "body"]}, "hero_plot_discussion": {"layout_name_contains": "slideLayout1", "required_placeholders": ["title", "body"]}}, "created_at": "2026-08-27T00:00:00Z"}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return profile
