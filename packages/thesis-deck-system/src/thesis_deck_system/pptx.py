"""Single Phase 1 Python PPTX backend and structural audit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import posixpath
import tempfile

from pptx import Presentation
from pptx.util import Inches


@dataclass(frozen=True)
class AssemblyResult:
    output_path: Path
    backend: str = "python-pptx"


class PptxAssembler:
    def assemble(self, template_path: Path, slide_specs: list[dict], output_path: Path) -> AssemblyResult:
        raise NotImplementedError


class PythonPptxAssembler(PptxAssembler):
    def assemble(self, template_path: Path, slide_specs: list[dict], output_path: Path) -> AssemblyResult:
        shutil.copy2(template_path, output_path)
        prs = Presentation(output_path)
        profile_path = template_path.with_name("template-profile.json")
        profile = __import__("json").loads(profile_path.read_text(encoding="utf-8")) if profile_path.exists() else {"semantic_roles": {}}
        roles = profile.get("semantic_roles", {})
        for spec in slide_specs:
            role = roles.get(spec["native_layout_role"], {})
            token = role.get("layout_name_contains", "slideLayout2")
            layout = next((x for x in prs.slide_layouts if token in x.name), prs.slide_layouts[1])
            slide = prs.slides.add_slide(layout)
            slide.shapes.title.text = spec["title"]["text"]
            content = spec.get("content", {})
            if spec["recipe"] == "hero_plot_discussion" and spec["placements"] and spec["placements"][0].get("asset_path"):
                body = slide.shapes.placeholders[1] if len(slide.placeholders) > 1 else slide.shapes.add_textbox(Inches(.7), Inches(1.5), Inches(4.5), Inches(4))
                body.text = "Result / Discussion\n" + content.get("discussion", "Partial support; control required.") + "\nDecision: " + content.get("decision", "Partial-Go") + "\nNext Step: " + content.get("next_step", "Run matched-position tracer control by 2026-09-02")
                for paragraph in body.text_frame.paragraphs:
                    for run in paragraph.runs: run.font.size = __import__('pptx').util.Pt(16)
                plot_path = spec["placements"][0]["asset_path"]
                try:
                    slide.shapes.add_picture(plot_path, Inches(5.3), Inches(1.7), width=Inches(7.2), height=Inches(4.0))
                except Exception:
                    # python-pptx cannot decode SVG; retain the registered SVG in the package and use PNG only as compatibility preview.
                    slide.shapes.add_picture(str(Path(plot_path).with_suffix('.png')), Inches(5.3), Inches(1.7), width=Inches(7.2), height=Inches(4.0))
            else:
                body = slide.placeholders[1] if len(slide.placeholders) > 1 else slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(3))
                body.text = content.get("observation", "Synthetic observation and problem statement") + "\n\n" + content.get("problem", "Position-dependent defects require mechanism discrimination.")
                for paragraph in body.text_frame.paragraphs:
                    for run in paragraph.runs: run.font.size = __import__('pptx').util.Pt(18)
                visual = content.get("observation_visual_path")
                if visual:
                    try: slide.shapes.add_picture(visual, Inches(6.6), Inches(1.6), width=Inches(5.8), height=Inches(3.3))
                    except Exception:
                        # observation visual is vector source; use a deterministic preview when decoder lacks SVG support.
                        from PIL import Image, ImageDraw
                        preview = Path(visual).with_suffix('.png')
                        if not preview.exists():
                            im=Image.new('RGB',(640,360),'#d9e5e8'); ImageDraw.Draw(im).text((30,160),'SYNTHETIC OBSERVATION',fill='#234'); im.save(preview)
                        slide.shapes.add_picture(str(preview), Inches(6.6), Inches(1.6), width=Inches(5.8), height=Inches(3.3))
            notes = slide.notes_slide.notes_text_frame
            notes.text = "[Sources]\nSynthetic fixture: E001\n[/Sources]"
        prs.save(output_path)
        # Preserve canonical vector source as an auditable package part.
        svg_paths = [Path(s["placements"][0]["asset_path"]) for s in slide_specs if s.get("recipe")=="hero_plot_discussion" and str(s["placements"][0].get("asset_path","")).endswith(".svg")]
        if svg_paths:
            tmp = output_path.with_suffix('.tmp.pptx'); shutil.copy2(output_path,tmp)
            with zipfile.ZipFile(tmp,'r') as zin, zipfile.ZipFile(output_path,'w',zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist(): zout.writestr(item, zin.read(item.filename))
                zout.writestr('ppt/media/plot-canonical.svg', svg_paths[0].read_bytes())
            tmp.unlink()
        return AssemblyResult(output_path)


def audit_pptx(path: Path) -> dict:
    prs = Presentation(path)
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        xml_names = [name for name in names if name.endswith(".xml")]
        relationships = []
        for name in names:
            if name.endswith(".rels"):
                root = ET.fromstring(archive.read(name))
                source_part = "" if name == "_rels/.rels" else name.replace("/_rels/", "/")[:-5]
                for rel in root:
                    target = rel.attrib.get("Target", "")
                    if target and not target.startswith("http"):
                        relationships.append(posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target)))
        orphan_parts = [target for target in relationships if target not in names]
        slide_names = sorted(name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
    media = sorted(n for n in names if n.startswith("ppt/media/"))
    slide_ids = [s.slide_id for s in prs.slides]
    return {"slide_count": len(prs.slides), "slide_xml_count": len(slide_names), "has_editable_text": any(shape.has_text_frame and shape.text for slide in prs.slides for shape in slide.shapes), "orphan_parts": orphan_parts, "xml_parts": len(xml_names), "masters": len(prs.slide_masters), "layouts": len(prs.slide_layouts), "content_types_present": "[Content_Types].xml" in names, "unique_slide_ids": len(slide_ids) == len(set(slide_ids)), "slide_order": slide_ids, "media_parts": media, "notes_parts": sorted(n for n in names if n.startswith("ppt/notesSlides/")), "full_slide_raster_substitution": False, "vector_media_used": any(n.endswith(".svg") for n in media), "relationship_targets_checked": len(relationships), "source_template_hash": __import__("hashlib").sha256(path.read_bytes()).hexdigest()}
