"""Single Phase 1 Python PPTX backend and structural audit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import posixpath

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
        for spec in slide_specs:
            layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(layout)
            slide.shapes.title.text = spec["title"]["text"]
            if spec["recipe"] == "hero_plot_discussion" and spec["placements"] and spec["placements"][0].get("asset_path"):
                body = slide.shapes.add_textbox(Inches(0.7), Inches(2.0), Inches(4.0), Inches(2.0))
                body.text = f"Claim: {', '.join(spec['bindings']['claim_refs'])}\nEvidence: {', '.join(spec['bindings']['evidence_refs'])}"
                slide.shapes.add_picture(spec["placements"][0]["asset_path"], Inches(5.3), Inches(1.7), width=Inches(7.2), height=Inches(4.0))
            else:
                body = slide.placeholders[1] if len(slide.placeholders) > 1 else slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(3))
                body.text = f"Synthetic fixture • {spec['recipe']}\nClaim: {', '.join(spec['bindings']['claim_refs'])}\nEvidence: {', '.join(spec['bindings']['evidence_refs'])}"
            notes = slide.notes_slide.notes_text_frame
            notes.text = "[Sources]\nSynthetic fixture: E001\n[/Sources]"
        prs.save(output_path)
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
    return {"slide_count": len(prs.slides), "slide_xml_count": len(slide_names), "has_editable_text": any(shape.has_text_frame and shape.text for slide in prs.slides for shape in slide.shapes), "orphan_parts": orphan_parts, "xml_parts": len(xml_names), "masters": len(prs.slide_masters), "layouts": len(prs.slide_layouts)}
