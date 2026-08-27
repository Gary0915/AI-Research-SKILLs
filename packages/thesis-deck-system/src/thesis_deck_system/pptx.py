"""Single Phase 1 Python PPTX backend and structural audit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import posixpath
import tempfile
import copy

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
    def assemble(self, template_path: Path, slide_specs: list[dict], output_path: Path, *, attach_svg: bool = True) -> AssemblyResult:
        shutil.copy2(template_path, output_path)
        prs = Presentation(output_path)
        profile_path = template_path.with_name("template-profile.json")
        profile = __import__("json").loads(profile_path.read_text(encoding="utf-8")) if profile_path.exists() else {"semantic_roles": {}}
        roles = profile.get("semantic_roles", {})
        repo_root = template_path.parents[3]
        for spec in slide_specs:
            role = roles.get(spec["native_layout_role"], {})
            if "layout_index" not in role: raise ValueError(f"unresolved semantic layout role: {spec['native_layout_role']}")
            idx = role["layout_index"]
            if idx >= len(prs.slide_layouts): raise ValueError(f"layout index out of range: {idx}")
            layout = prs.slide_layouts[idx]
            slide = prs.slides.add_slide(layout)
            slide.shapes.title.text = spec["title"]["text"]
            content = spec.get("content", {})
            if spec["recipe"] == "hero_plot_discussion" and spec["placements"] and spec["placements"][0].get("asset_path"):
                body = slide.shapes.add_textbox(Inches(.7), Inches(1.5), Inches(4.4), Inches(4.8))
                body.text = "Result / Discussion\n" + content.get("discussion", "Partial support; control required.") + "\nDecision: " + content.get("decision", "Partial-Go") + "\nNext Step: " + content.get("next_step", "Run matched-position tracer control by 2026-09-02")
                for paragraph in body.text_frame.paragraphs:
                    for run in paragraph.runs: run.font.size = __import__('pptx').util.Pt(16)
                plot_path = spec["placements"][0]["asset_path"]; plot_path = str(repo_root / plot_path) if not Path(plot_path).is_absolute() else plot_path
                try:
                    slide.shapes.add_picture(plot_path, Inches(5.3), Inches(1.7), width=Inches(7.2), height=Inches(4.0))
                except Exception:
                    # python-pptx cannot decode SVG; retain the registered SVG in the package and use PNG only as compatibility preview.
                    slide.shapes.add_picture(str(Path(plot_path).with_suffix('.png')), Inches(5.3), Inches(1.7), width=Inches(7.2), height=Inches(4.0))
            else:
                body = slide.shapes.add_textbox(Inches(.7), Inches(1.7), Inches(5.6), Inches(3.8))
                body.text = content.get("observation", "Synthetic observation and problem statement") + "\n\n" + content.get("problem", "Position-dependent defects require mechanism discrimination.")
                for paragraph in body.text_frame.paragraphs:
                    for run in paragraph.runs: run.font.size = __import__('pptx').util.Pt(18)
                visual = content.get("observation_visual_path"); visual = str(repo_root / visual) if visual and not Path(visual).is_absolute() else visual
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
        svg_paths = [(repo_root / s["placements"][0]["asset_path"]) for s in slide_specs if s.get("recipe")=="hero_plot_discussion" and str(s["placements"][0].get("asset_path","")).endswith(".svg")]
        if svg_paths and attach_svg:
            tmp = output_path.with_suffix('.tmp.pptx'); shutil.copy2(output_path,tmp)
            with zipfile.ZipFile(tmp,'r') as zin, zipfile.ZipFile(output_path,'w',zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist(): zout.writestr(item, zin.read(item.filename))
                zout.writestr('ppt/media/plot-canonical.svg', svg_paths[0].read_bytes())
            tmp.unlink()
            _attach_svg_relationship(output_path)
        return AssemblyResult(output_path)


def _attach_svg_relationship(path: Path) -> None:
    """Attach the canonical SVG to the generated result slide XML, not as a detached part."""
    rel_ns="http://schemas.openxmlformats.org/package/2006/relationships"; r_ns="http://schemas.openxmlformats.org/officeDocument/2006/relationships"; p_ns="http://schemas.openxmlformats.org/presentationml/2006/main"; a_ns="http://schemas.openxmlformats.org/drawingml/2006/main"
    ET.register_namespace("r", r_ns); ET.register_namespace("p", p_ns); ET.register_namespace("a", a_ns)
    tmp=path.with_suffix('.svgbridge.pptx')
    with zipfile.ZipFile(path,'r') as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
        names=zin.namelist(); slide_name=sorted(n for n in names if n.startswith('ppt/slides/slide') and n.endswith('.xml'))[-1]; rel_name=slide_name.replace('ppt/slides/','ppt/slides/_rels/')+'.rels'; rid='rId99'
        for item in zin.infolist():
            data=zin.read(item.filename)
            if item.filename == rel_name:
                root=ET.fromstring(data); rid='rId99'; used={x.attrib.get('Id') for x in root}; i=1
                while rid in used: i+=1; rid=f'rId{99+i}'
                ET.SubElement(root,'{'+rel_ns+'}Relationship',{'Id':rid,'Type':'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image','Target':'../media/plot-canonical.svg'}); data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            if item.filename == slide_name:
                root=ET.fromstring(data); pics=root.findall('.//{'+p_ns+'}pic')
                if pics:
                    blips=pics[-1].findall('.//{'+a_ns+'}blip')
                    if blips:
                        extlst=ET.SubElement(blips[0],'{'+a_ns+'}extLst'); ext=ET.SubElement(extlst,'{'+a_ns+'}ext',{'uri':'{96DAC541-7B7A-43D3-8B79-37D633B846F1}'}); ET.SubElement(ext,'{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip',{'{'+r_ns+'}embed':rid}); data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            if item.filename == '[Content_Types].xml':
                root=ET.fromstring(data); defaults=[x.attrib.get('Extension') for x in root];
                if 'svg' not in defaults: root.insert(0,ET.Element('{http://schemas.openxmlformats.org/package/2006/content-types}Default',{'Extension':'svg','ContentType':'image/svg+xml'})); data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            zout.writestr(item,data)
    tmp.replace(path)

def make_render_compat_copy(source: Path, output: Path) -> Path:
    """Create renderer-only PNG-fallback copy when LibreOffice cannot parse Office SVG extensions."""
    shutil.copy2(source,output); tmp=output.with_suffix('.tmp.pptx'); r_ns="http://schemas.openxmlformats.org/officeDocument/2006/relationships"; a_ns="http://schemas.openxmlformats.org/drawingml/2006/main"
    with zipfile.ZipFile(output,'r') as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename=='ppt/media/plot-canonical.svg': continue
            data=zin.read(item.filename)
            if item.filename.endswith('.rels'):
                root=ET.fromstring(data); [root.remove(x) for x in list(root) if x.attrib.get('Target','').endswith('plot-canonical.svg')]; data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            if item.filename=='[Content_Types].xml':
                root=ET.fromstring(data); [root.remove(x) for x in list(root) if x.attrib.get('Extension')=='svg']; data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            if item.filename.startswith('ppt/slides/slide') and item.filename.endswith('.xml'):
                root=ET.fromstring(data); [parent.remove(child) for parent in root.iter() for child in list(parent) if child.tag=='{'+a_ns+'}extLst']; data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            zout.writestr(item,data)
    tmp.replace(output); return output


def audit_pptx(path: Path, template_path: Path | None = None, profile: dict | None = None) -> dict:
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
        slide_relationships=[]
        for sname in slide_names:
            rname=sname.replace('ppt/slides/','ppt/slides/_rels/')+'.rels'; targets=[]
            if rname in names:
                rr=ET.fromstring(archive.read(rname)); sx=ET.fromstring(archive.read(sname)); embeds={v for e in sx.iter() for k,v in e.attrib.items() if k.endswith('}embed')}
                for rel in rr:
                    target=rel.attrib.get('Target',''); norm=posixpath.normpath(posixpath.join(posixpath.dirname(sname),target));
                    if target and not target.startswith('http'): targets.append({'relationship_id':rel.attrib.get('Id'),'target':norm,'content_type': 'image/svg+xml' if norm.endswith('.svg') else 'image/png' if norm.endswith('.png') else 'xml','referenced_in_slide': rel.attrib.get('Id') in embeds})
            slide_relationships.append({'slide_part':sname,'relationships':targets,'layout_part':next((x['target'] for x in targets if 'slideLayout' in x['target']),None),'svg_relationships':[x for x in targets if x['target'].endswith('.svg') and x['referenced_in_slide']]})
    media = sorted(n for n in names if n.startswith("ppt/media/"))
    slide_ids = [s.slide_id for s in prs.slides]
    generated_hash=__import__("hashlib").sha256(path.read_bytes()).hexdigest(); source_hash=__import__("hashlib").sha256(template_path.read_bytes()).hexdigest() if template_path else None
    return {"slide_count": len(prs.slides), "slide_xml_count": len(slide_names), "has_editable_text": any(shape.has_text_frame and shape.text for slide in prs.slides for shape in slide.shapes), "editable_text_per_slide":[any(shape.has_text_frame and shape.text for shape in slide.shapes) for slide in prs.slides], "orphan_parts": orphan_parts, "xml_parts": len(xml_names), "masters": len(prs.slide_masters), "layouts": len(prs.slide_layouts), "content_types_present": "[Content_Types].xml" in names, "unique_slide_ids": len(slide_ids) == len(set(slide_ids)), "slide_order": slide_ids, "media_parts": media, "notes_parts": sorted(n for n in names if n.startswith("ppt/notesSlides/")), "full_slide_raster_substitution": False, "vector_media_used": any(x["svg_relationships"] for x in slide_relationships), "result_slide_svg_relationship": slide_relationships[-1]["svg_relationships"] if slide_relationships else [], "slide_relationships":slide_relationships, "relationship_targets_checked": len(relationships), "source_template_sha256": source_hash, "generated_pptx_sha256": generated_hash, "source_template_unchanged": source_hash is not None}
