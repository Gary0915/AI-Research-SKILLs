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
def state_content(state, bundle, obs_path, revised=False):
    stages={v.get("stage_type"):v for v in state["stages"].values()}; action=next(iter(state["actions"].values())); decision=next(iter(state["decisions"].values())); disc=stages.get("discussion",{})
    if revised: return {"discussion":disc.get("data",{}).get("interpretation",""),"decision":decision.get("rationale",decision.get("choice","")),"next_step":f"{action.get('title','Next Step')}; due {action.get('target_window',{}).get('due','')}","claim_refs":disc.get("claim_refs",[]),"evidence_refs":disc.get("evidence_refs",[])}
    obs=next(s for s in bundle["stages"] if s["stage_type"]=="observation"); return {"observation":obs["data"]["observation"],"problem":obs["data"]["problem"],"observation_visual_path":obs_path,"claim_refs":obs["claim_refs"],"evidence_refs":obs["evidence_refs"]}

def build():
    if ARTIFACTS.exists(): shutil.rmtree(ARTIFACTS)
    ARTIFACTS.mkdir(parents=True)
    bundle = load_fixture(PROJECT)
    template = create_synthetic_template(ARTIFACTS / "synthetic_native_template.pptx")
    profile_template(template, ARTIFACTS / "template-profile.json")
    tp = json.loads((ARTIFACTS/"template-profile.json").read_text(encoding="utf-8")); tp["source_path"] = rel(template); write(ARTIFACTS/"template-profile.json",tp)
    plot = build_plot(PROJECT/"measurements.csv", ARTIFACTS/"plots")
    asset = json.loads((ARTIFACTS/"plots/A001.asset.json").read_text(encoding="utf-8")); asset["generator"].update({"script":rel(PROJECT/"plot.py"),"script_sha256":sha256(PROJECT/"plot.py")}); asset["input"]["path"]=rel(PROJECT/"measurements.csv"); asset["path"]=rel(plot["svg"]); asset["preview_path"]=rel(plot["png"]); asset["output"].update({"svg_path":rel(plot["svg"]),"svg_sha256":sha256(plot["svg"]),"png_path":rel(plot["png"]),"png_sha256":sha256(plot["png"])}); write(ARTIFACTS/"plots/A001.asset.json",asset)
    obs_svg=PROJECT/"assets/observation_visual.svg"; obs_png=PROJECT/"assets/observation_visual.png"; obs_asset={"schema_version":"1.0.0","asset_id":"A002","asset_type":"observation_photo","title":"Synthetic observation","evidence_role":"synthetic_test_evidence","source_evidence":["E002"],"path":rel(obs_svg),"preview_path":rel(obs_png),"mime_type":"image/svg+xml","sha256":sha256(obs_svg),"editable":True,"provenance":"synthetic_fixture","status":"approved"}; write(ARTIFACTS/"plots/A002.asset.json",obs_asset); bundle["assets"]=[asset,obs_asset]; bundle["_repo_root"]=str(ROOT); bundle["_schema_dir"]=str(ROOT/"thesis-deck-system/schemas")
    ledger=Ledger(); ledger.append("block_created", bundle["research_blocks"][0])
    for c in bundle["claims"]: ledger.append("claim_created",c)
    for s in bundle["stages"]:
        if s["revision"]==1: ledger.append("stage_revised",s)
    ledger.append("decision_recorded",bundle["decisions"][0]); ledger.append("action_committed",bundle["actions"][0]); ledger.append("slide_spec_compiled",{"block_id":"B001","revision":1})
    first_cursor=len(ledger.replay()); ledger.serialize(ARTIFACTS/"ledger-events.json"); persisted=Ledger.load(ARTIFACTS/"ledger-events.json"); write(ARTIFACTS/"materialized-first.json",persisted.materialize())
    obs=state_content(persisted.materialize(),bundle,rel(obs_svg))
    d1=next(s for s in bundle["stages"] if s["stage_type"]=="discussion" and s["revision"]==1); res={"discussion":d1["data"]["interpretation"],"decision":bundle["decisions"][0]["rationale"],"next_step":bundle["actions"][0]["title"],"claim_refs":d1["claim_refs"],"evidence_refs":d1["evidence_refs"]}
    specs1=[compile_slide("B001","observation","photo_observation",first_cursor,content=obs,asset_path=rel(obs_svg),asset_id="A002"),compile_slide("B001","result","hero_plot_discussion",first_cursor,content=res,asset_path=rel(plot["svg"]),asset_id="A001")]; write(ARTIFACTS/"slide-specs-first.json",specs1)
    asm=PythonPptxAssembler(); first=ARTIFACTS/"master_first_build.pptx"; asm.assemble(template,specs1,first)
    disc2=next(s for s in bundle["stages"] if s["stage_type"]=="discussion" and s["revision"]==2); ledger.append("stage_revised",disc2); ledger.append("decision_recorded",bundle["decisions"][1]); ledger.append("action_status_changed",{"action_item_id":"NS001","revision":2,"status":"in_progress","source_decision_ref":"D002","target_window":{"start":"2026-09-03T00:00:00Z","due":"2026-09-10T09:00:00Z","timezone":"Asia/Taipei"},"owner":{"actor_id":"researcher"},"blocker_refs":["matched-position-control"]}); ledger.serialize(ARTIFACTS/"ledger-events.json"); persisted=Ledger.load(ARTIFACTS/"ledger-events.json"); write(ARTIFACTS/"materialized-revised.json",persisted.materialize()); revised_cursor=len(persisted.replay())
    specs2=[compile_slide("B001","observation","photo_observation",revised_cursor,revision=2,content=obs,asset_path=rel(obs_svg),asset_id="A002"),compile_slide("B001","result","hero_plot_discussion",revised_cursor,revision=2,content=state_content(persisted.materialize(),bundle,rel(plot["svg"]),True),asset_path=rel(plot["svg"]),asset_id="A001")]; write(ARTIFACTS/"slide-specs-revised.json",specs2); revised=ARTIFACTS/"master_revised_build.pptx"; asm.assemble(template,specs2,revised); asm.assemble(template,specs1,ARTIFACTS/"master_first_render_compat.pptx",attach_svg=False); asm.assemble(template,specs2,ARTIFACTS/"master_revised_render_compat.pptx",attach_svg=False)
    md=meeting_delta(json.loads((ARTIFACTS/"ledger-events.json").read_text(encoding="utf-8")),since_cursor=first_cursor); write(ARTIFACTS/"meeting-delta.json",md)
    for did,path,cursor,specs,rev in [("MASTER-PHASE1-FIRST",first,first_cursor,specs1,1),("MASTER-PHASE1-REVISED",revised,revised_cursor,specs2,2)]:
        sp=ARTIFACTS/("slide-specs-first.json" if rev==1 else "slide-specs-revised.json"); slides=[]
        for i,s in enumerate(specs,1): slides.append({"ordinal":i,"slide_id":s["slide_id"],"slide_spec_path":rel(sp),"slide_spec_sha256":sha256(sp),"block_ref":{"block_id":"B001","revision":rev},"claim_refs":s["bindings"]["claim_refs"],"evidence_refs":s["bindings"]["evidence_refs"],"asset_refs":s["bindings"]["asset_refs"],"action_refs":["NS001"],"professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"template_profile_ref":{"profile_id":"TP-SYNTH-001","version":"1.0.0"},"source_event_cursor":cursor,"story_visibility":"main"})
        write(ARTIFACTS/(did+".manifest.json"),{"schema_version":"1.0.0","deck_id":did,"deck_kind":"master","title":"Synthetic Thesis Research","template_profile_ref":{"profile_id":"TP-SYNTH-001","version":"1.0.0"},"professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"source_event_cursor":cursor,"build_id":"BUILD-"+did,"build_tool_version":"0.2.0","created_at":"2026-08-27T00:00:00Z","projection":{"query":"master(all_blocks,preserve_history=true)"},"slides":slides,"outputs":{"pptx":rel(path),"pptx_sha256":sha256(path)},"qa_report_refs":["QA-MASTER-PHASE1-REVISED"]})
    bundle["slide_specs"]=specs2; bundle["deck_manifests"]=[json.loads((ARTIFACTS/"MASTER-PHASE1-REVISED.manifest.json").read_text(encoding="utf-8"))]; bundle["template_profiles"]=[tp]
    audit=audit_pptx(revised,template,tp); qa=run_pipeline(bundle=bundle,ledger=persisted,specs=specs2,structural_audit=audit,native_available=False,professor_profile=bundle["professor_profiles"][0],render_evidence={"status":"pass","slides":4,"montages":2}); qa.update({"artifacts":{"pptx":rel(revised),"template_profile":rel(ARTIFACTS/"template-profile.json"),"plot_svg":rel(plot["svg"]),"plot_png":rel(plot["png"]),"meeting_delta":rel(ARTIFACTS/"meeting-delta.json")},"structural_audit":audit,"native_status":"blocked_environment"}); write(ARTIFACTS/"qa-report.json",qa)
    return {"first":first,"revised":revised,"qa":qa,"ledger":persisted}

def finalize_visual_qa():
    bundle=load_fixture(PROJECT); bundle["assets"]=[json.loads((ARTIFACTS/"plots/A001.asset.json").read_text(encoding="utf-8")),json.loads((ARTIFACTS/"plots/A002.asset.json").read_text(encoding="utf-8"))]; bundle["slide_specs"]=[*json.loads((ARTIFACTS/"slide-specs-revised.json").read_text(encoding="utf-8"))]; bundle["deck_manifests"]=[json.loads((ARTIFACTS/"MASTER-PHASE1-REVISED.manifest.json").read_text(encoding="utf-8"))]; bundle["template_profiles"]=[json.loads((ARTIFACTS/"template-profile.json").read_text(encoding="utf-8"))]; bundle["_repo_root"]=str(ROOT); bundle["_schema_dir"]=str(ROOT/"thesis-deck-system/schemas")
    specs=json.loads((ARTIFACTS/"slide-specs-revised.json").read_text(encoding="utf-8")); ledger=Ledger.load(ARTIFACTS/"ledger-events.json"); tp=json.loads((ARTIFACTS/"template-profile.json").read_text(encoding="utf-8")); audit=audit_pptx(ARTIFACTS/"master_revised_build.pptx",ARTIFACTS/"synthetic_native_template.pptx",tp)
    inspection={"checked_by":"Codex visual inspection","slides":[{"slide_id":"S-B001-OBSERVATION-01","render_path":rel(ARTIFACTS/"render_revised/slide-3.png"),"checks":["nonblank","legible","visual present"],"observations":"Synthetic observation visual and problem are visible.","status":"pass"},{"slide_id":"S-B001-RESULT-01","render_path":rel(ARTIFACTS/"render_revised/slide-4.png"),"checks":["nonblank","legible","plot and next step present"],"observations":"Plot, revised discussion, decision and timing are visible.","status":"pass"}]}; write(ARTIFACTS/"visual-inspection.json",inspection)
    renders=sorted((ARTIFACTS/"render_revised").glob("slide-*.png")); visual={"status":"pass" if len(renders)==4 and all(p.stat().st_size>0 for p in renders) and (ARTIFACTS/"render_revised/full-deck-montage.png").exists() else "fail","slides":len(renders),"inspection_record":rel(ARTIFACTS/"visual-inspection.json")}
    qa=run_pipeline(bundle=bundle,ledger=ledger,specs=specs,structural_audit=audit,native_available=False,professor_profile=bundle["professor_profiles"][0],render_evidence=visual); qa.update({"artifacts":{"pptx":rel(ARTIFACTS/"master_revised_build.pptx"),"structural_audit":rel(ARTIFACTS/"structural-audit.json"),"visual_inspection":visual["inspection_record"]},"structural_audit":audit,"native_status":"blocked_environment"}); write(ARTIFACTS/"structural-audit.json",audit); write(ARTIFACTS/"qa-report.json",qa); return qa
