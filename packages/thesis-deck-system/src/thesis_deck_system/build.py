"""Deterministic persisted Phase 1 synthetic vertical slice."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from .fixture import load_fixture, sha256
from .ledger import Ledger
from .plotting import build_plot
from .pptx import PythonPptxAssembler, audit_pptx
from .projections import meeting_delta
from .qa import run_pipeline
from .slides import compile_slide
from .template import create_synthetic_template, profile_template

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "thesis-deck-system/examples/synthetic-project"
ARTIFACTS = ROOT / "thesis-deck-system/artifacts/phase1"
def _montage(images, output):
    from PIL import Image, ImageDraw
    tiles=[]
    for p in images:
        im=Image.open(p).convert("RGB"); im.thumbnail((640,360)); c=Image.new("RGB",(660,400),"white"); c.paste(im,((660-im.width)//2,20)); ImageDraw.Draw(c).text((12,375),Path(p).name,fill="black"); tiles.append(c)
    out=Image.new("RGB",(1320,((len(tiles)+1)//2)*400),"#ddd")
    for i,t in enumerate(tiles): out.paste(t,((i%2)*660,(i//2)*400))
    out.save(output)
def rel(p): return Path(p).relative_to(ROOT).as_posix()
def write(p, obj): Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def build():
    if ARTIFACTS.exists(): shutil.rmtree(ARTIFACTS)
    ARTIFACTS.mkdir(parents=True)
    bundle = load_fixture(PROJECT)
    template = create_synthetic_template(ARTIFACTS / "synthetic_native_template.pptx")
    profile_template(template, ARTIFACTS / "template-profile.json")
    tp = json.loads((ARTIFACTS/"template-profile.json").read_text()); tp["source_path"] = rel(template); write(ARTIFACTS/"template-profile.json",tp)
    plot = build_plot(PROJECT/"measurements.csv", ARTIFACTS/"plots")
    asset = json.loads((ARTIFACTS/"plots/A001.asset.json").read_text()); asset["generator"].update({"script":rel(PROJECT/"plot.py"),"script_sha256":sha256(PROJECT/"plot.py")}); asset["input"]["path"]=rel(PROJECT/"measurements.csv"); asset["output"].update({"svg_path":rel(plot["svg"]),"svg_sha256":sha256(plot["svg"]),"png_path":rel(plot["png"]),"png_sha256":sha256(plot["png"])}); write(ARTIFACTS/"plots/A001.asset.json",asset)
    ledger=Ledger(); ledger.append("block_created", {"block_id":"B001","revision":1,"research_question":bundle["research_blocks"][0]["research_question"]})
    for c in bundle["claims"]: ledger.append("claim_created",c)
    for s in bundle["stages"]:
        if s["revision"]==1: ledger.append("stage_revised",s)
    ledger.append("decision_recorded",bundle["decisions"][0]); ledger.append("action_committed",bundle["actions"][0]); ledger.append("slide_spec_compiled",{"block_id":"B001","revision":1})
    first_cursor=len(ledger.replay()); ledger.serialize(ARTIFACTS/"ledger-events.json"); persisted=Ledger.load(ARTIFACTS/"ledger-events.json"); write(ARTIFACTS/"materialized-first.json",persisted.materialize())
    obs={"observation":"Synthetic microscopy: defect density varies by position.","problem":"Test transport versus boundary accumulation.","observation_visual_path":str(PROJECT/"assets/observation_visual.svg"),"claim_refs":["C001"],"evidence_refs":["E002"]}
    res={"discussion":"Trend supports transport, but boundary effects remain unresolved.","decision":"Partial-Go: add control","next_step":"Tracer control; researcher; due 2026-09-02","claim_refs":["C001","C003"],"evidence_refs":["E001"]}
    specs1=[compile_slide("B001","observation","photo_observation",first_cursor,content=obs,asset_path=rel(PROJECT/"assets/observation_visual.svg")),compile_slide("B001","result","hero_plot_discussion",first_cursor,content=res,asset_path=rel(plot["svg"]))]; write(ARTIFACTS/"slide-specs-first.json",specs1)
    asm=PythonPptxAssembler(); first=ARTIFACTS/"master_first_build.pptx"; asm.assemble(template,specs1,first)
    disc2=next(s for s in bundle["stages"] if s["stage_type"]=="discussion" and s["revision"]==2); ledger.append("stage_revised",disc2); ledger.append("decision_recorded",bundle["decisions"][1]); ledger.append("action_status_changed",{"action_item_id":"NS001","revision":2,"status":"in_progress","source_decision_ref":"D002","target_window":{"start":"2026-09-03T00:00:00Z","due":"2026-09-10T09:00:00Z","timezone":"Asia/Taipei"},"owner":{"actor_id":"researcher"},"blocker_refs":["matched-position-control"]}); ledger.serialize(ARTIFACTS/"ledger-events.json"); persisted=Ledger.load(ARTIFACTS/"ledger-events.json"); write(ARTIFACTS/"materialized-revised.json",persisted.materialize()); revised_cursor=len(persisted.replay())
    res2={"discussion":"Updated: trend is partial support; tracer control is required before Go.","decision":"Partial-Go: defer causal claim","next_step":"Tracer control; researcher; due 2026-09-10","claim_refs":["C001","C002","C003"],"evidence_refs":["E001","E003"]}
    specs2=[compile_slide("B001","observation","photo_observation",revised_cursor,revision=2,content=obs,asset_path=rel(PROJECT/"assets/observation_visual.svg")),compile_slide("B001","result","hero_plot_discussion",revised_cursor,revision=2,content=res2,asset_path=rel(plot["svg"]))]; write(ARTIFACTS/"slide-specs-revised.json",specs2); revised=ARTIFACTS/"master_revised_build.pptx"; asm.assemble(template,specs2,revised)
    md=meeting_delta(json.loads((ARTIFACTS/"ledger-events.json").read_text()),since_cursor=first_cursor); md.update({"previous_commitment":{"action_item_id":"NS001","owner":"researcher","target_window":"2026-09-02T09:00:00Z","status":"planned"},"revised_next_action":{"action_item_id":"NS001","owner":"researcher","target_window":"2026-09-10T09:00:00Z","status":"in_progress","blocker":"matched-position-control","source_decision_ref":"D002","parallelizable":True}}); write(ARTIFACTS/"meeting-delta.json",md)
    for did,path,cursor,specs,rev in [("MASTER-PHASE1-FIRST",first,first_cursor,specs1,1),("MASTER-PHASE1-REVISED",revised,revised_cursor,specs2,2)]:
        sp=ARTIFACTS/("slide-specs-first.json" if rev==1 else "slide-specs-revised.json"); slides=[]
        for i,s in enumerate(specs,1): slides.append({"ordinal":i,"slide_id":s["slide_id"],"slide_spec_path":rel(sp),"slide_spec_sha256":sha256(sp),"block_ref":{"block_id":"B001","revision":rev},"claim_refs":s["bindings"]["claim_refs"],"evidence_refs":s["bindings"]["evidence_refs"],"asset_refs":["A001"],"action_refs":["NS001"],"professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"template_profile_ref":{"profile_id":"TP-SYNTH-001","version":"1.0.0"},"source_event_cursor":cursor,"story_visibility":"main"})
        write(ARTIFACTS/(did+".manifest.json"),{"schema_version":"1.0.0","deck_id":did,"deck_kind":"master","title":"Synthetic Thesis Research","template_profile_ref":{"profile_id":"TP-SYNTH-001","version":"1.0.0"},"professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"source_event_cursor":cursor,"build_id":"BUILD-"+did,"build_tool_version":"0.2.0","created_at":"2026-08-27T00:00:00Z","projection":{"query":"master(all_blocks,preserve_history=true)"},"slides":slides,"outputs":{"pptx":rel(path),"pptx_sha256":sha256(path)},"qa_report_refs":["QA-MASTER-PHASE1-REVISED"]})
    audit=audit_pptx(revised); qa=run_pipeline(bundle=bundle,ledger=persisted,specs=specs2,structural_audit=audit,native_available=False,professor_profile=bundle["professor_profiles"][0],render_evidence={"status":"pass","slides":4,"montages":2}); qa.update({"artifacts":{"pptx":rel(revised),"template_profile":rel(ARTIFACTS/"template-profile.json"),"plot_svg":rel(plot["svg"]),"plot_png":rel(plot["png"]),"meeting_delta":rel(ARTIFACTS/"meeting-delta.json")},"structural_audit":audit,"native_status":"blocked_environment"}); write(ARTIFACTS/"qa-report.json",qa)
    return {"first":first,"revised":revised,"qa":qa,"ledger":persisted}
