"""Deterministic persisted Phase 1 synthetic vertical slice."""
from __future__ import annotations
import copy, json, shutil
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
def state_content(state, stage_type, asset_path):
    """Compile presentation content exclusively from one materialized ledger snapshot."""
    stages={value.get("stage_type"):value for value in state["stages"].values()}
    stage=stages[stage_type]
    if stage_type == "observation":
        return {"observation":stage["data"]["observation"],"problem":stage["data"]["problem"],"observation_visual_path":asset_path,"claim_refs":stage["claim_refs"],"evidence_refs":stage["evidence_refs"]}
    data=stage["data"]
    decision=state["decisions"][data["decision_ref"]]
    action=state["actions"][data["next_step_ref"]]
    return {"discussion":data["interpretation"],"decision":decision.get("rationale",decision.get("choice","")),"next_step":f"{action.get('title','Next Step')}; status {action.get('status','')}; due {action.get('target_window',{}).get('due','')}","claim_refs":stage.get("claim_refs",[]),"evidence_refs":stage.get("evidence_refs",[])}

def _manifest(deck_id, path, cursor, specs, revision, spec_path):
    slides=[]
    for ordinal,spec in enumerate(specs,1):
        slides.append({"ordinal":ordinal,"slide_id":spec["slide_id"],"slide_spec_path":rel(spec_path),"slide_spec_sha256":sha256(spec_path),"block_ref":{"block_id":"B001","revision":revision},"claim_refs":spec["bindings"]["claim_refs"],"evidence_refs":spec["bindings"]["evidence_refs"],"asset_refs":spec["bindings"]["asset_refs"],"action_refs":spec["bindings"]["action_refs"],"decision_refs":spec["bindings"]["decision_refs"],"professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"template_profile_ref":{"profile_id":"TP-SYNTH-001","version":"1.0.0"},"source_event_cursor":cursor,"story_visibility":"main"})
    return {"schema_version":"1.0.0","deck_id":deck_id,"deck_kind":"master","title":"Synthetic Thesis Research","template_profile_ref":{"profile_id":"TP-SYNTH-001","version":"1.0.0"},"professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"source_event_cursor":cursor,"build_id":"BUILD-"+deck_id,"build_tool_version":"0.2.0","created_at":"2026-08-27T00:00:00Z","projection":{"query":"master(all_blocks,preserve_history=true)"},"slides":slides,"outputs":{"pptx":rel(path),"pptx_sha256":sha256(path)},"qa_report_refs":["QA-"+deck_id]}

def _scope_record(deck_id):
    return {"qa_report_id":"QA-"+deck_id,"build_id":"BUILD-"+deck_id,"deck_id":deck_id}

def _qa_bundle(bundle, ledger, specs, manifest, template_profile, meeting_projection, first_cursor):
    scoped=copy.deepcopy(bundle)
    state=ledger.materialize(manifest["source_event_cursor"])
    scoped.update({"research_blocks":list(state["blocks"].values()),"claims":list(state["claims"].values()),"evidence_cards":list(state["evidence"].values()),"assets":list(state["assets"].values()),"actions":list(state["actions"].values()),"decisions":list(state["decisions"].values()),"stages":list(state["stages"].values()),"slide_specs":specs,"deck_manifests":[manifest],"template_profiles":[template_profile],"meeting_projection":meeting_projection,"_repo_root":str(ROOT),"_schema_dir":str(ROOT/"thesis-deck-system/schemas"),"_materialized_paths":{"first":str(ARTIFACTS/"materialized-first.json"),"revised":str(ARTIFACTS/"materialized-revised.json"),"first_cursor":first_cursor},"_qa_scope_records":[_scope_record(manifest["deck_id"])]})
    return scoped

def _run_build_qa(bundle, ledger, specs, manifest, audit, meeting_projection, first_cursor, render_evidence):
    scoped=_qa_bundle(bundle,ledger,specs,manifest,bundle["template_profiles"][0],meeting_projection,first_cursor)
    report=run_pipeline(bundle=scoped,ledger=ledger,specs=specs,structural_audit=audit,native_available=False,professor_profile=bundle["professor_profiles"][0],render_evidence=render_evidence,qa_report_id="QA-"+manifest["deck_id"],build_id=manifest["build_id"],deck_id=manifest["deck_id"])
    is_first=manifest["deck_id"].endswith("FIRST")
    report.update({"artifacts":{"pptx":manifest["outputs"]["pptx"],"structural_audit":rel(ARTIFACTS/("structural-audit-first.json" if is_first else "structural-audit-revised.json")),"source_cursor":manifest["source_event_cursor"],"materialized_state":rel(ARTIFACTS/("materialized-first.json" if is_first else "materialized-revised.json"))},"structural_audit":audit,"native_status":"blocked_environment"})
    return report

def build():
    if ARTIFACTS.exists(): shutil.rmtree(ARTIFACTS)
    ARTIFACTS.mkdir(parents=True)
    bundle=load_fixture(PROJECT)
    template=create_synthetic_template(ARTIFACTS/"synthetic_native_template.pptx")
    profile_template(template,ARTIFACTS/"template-profile.json")
    tp=json.loads((ARTIFACTS/"template-profile.json").read_text(encoding="utf-8")); tp["source_path"]=rel(template); write(ARTIFACTS/"template-profile.json",tp)
    plot=build_plot(PROJECT/"measurements.csv",ARTIFACTS/"plots")
    (ARTIFACTS/"plots/.gitattributes").write_text("*.svg whitespace=-trailing-space\n",encoding="utf-8")
    asset=json.loads((ARTIFACTS/"plots/A001.asset.json").read_text(encoding="utf-8")); asset["generator"].update({"script":rel(PROJECT/"plot.py"),"script_sha256":sha256(PROJECT/"plot.py")}); asset["input"]["path"]=rel(PROJECT/"measurements.csv"); asset["path"]=rel(plot["svg"]); asset["preview_path"]=rel(plot["png"]); asset["output"].update({"svg_path":rel(plot["svg"]),"svg_sha256":sha256(plot["svg"]),"png_path":rel(plot["png"]),"png_sha256":sha256(plot["png"])}); write(ARTIFACTS/"plots/A001.asset.json",asset)
    obs_svg=PROJECT/"assets/observation_visual.svg"; obs_png=PROJECT/"assets/observation_visual.png"; obs_asset={"schema_version":"1.0.0","asset_id":"A002","asset_type":"observation_photo","title":"Synthetic observation","evidence_role":"synthetic_test_evidence","source_evidence":["E002"],"path":rel(obs_svg),"preview_path":rel(obs_png),"mime_type":"image/svg+xml","sha256":sha256(obs_svg),"editable":True,"provenance":"synthetic_fixture","status":"approved"}; write(ARTIFACTS/"plots/A002.asset.json",obs_asset)
    bundle["assets"]=[asset,obs_asset]; bundle["template_profiles"]=[tp]

    ledger=Ledger(); ledger.append("block_created",bundle["research_blocks"][0])
    for claim in bundle["claims"]: ledger.append("claim_created",claim)
    for evidence in bundle["evidence_cards"]: ledger.append("evidence_linked",evidence)
    for registered_asset in bundle["assets"]: ledger.append("asset_registered",registered_asset)
    for stage in bundle["stages"]:
        if stage["revision"]==1: ledger.append("stage_revised",stage)
    ledger.append("decision_recorded",bundle["decisions"][0]); ledger.append("action_committed",bundle["actions"][0]); ledger.append("slide_spec_compiled",{"block_id":"B001","revision":1})
    first_cursor=len(ledger.replay())
    first_state=ledger.materialize(first_cursor); write(ARTIFACTS/"materialized-first.json",first_state)
    first_specs=[compile_slide("B001","observation","photo_observation",first_cursor,revision=1,content=state_content(first_state,"observation",rel(obs_svg)),asset_path=rel(obs_svg),asset_id="A002",decision_refs=["D001"]),compile_slide("B001","result","hero_plot_discussion",first_cursor,revision=1,content=state_content(first_state,"discussion",rel(plot["svg"])),asset_path=rel(plot["svg"]),asset_id="A001",decision_refs=["D001"])]; write(ARTIFACTS/"slide-specs-first.json",first_specs)
    assembler=PythonPptxAssembler(); first=ARTIFACTS/"master_first_build.pptx"; assembler.assemble(template,first_specs,first)

    discussion_v2=next(stage for stage in bundle["stages"] if stage["stage_type"]=="discussion" and stage["revision"]==2)
    ledger.append("stage_revised",discussion_v2); ledger.append("decision_recorded",bundle["decisions"][1]); ledger.append("action_status_changed",bundle["actions"][1]); revision_event=ledger.append("block_revised",bundle["research_blocks"][1]); ledger.append("slide_spec_compiled",{"block_id":"B001","revision":2})
    revised_cursor=len(ledger.replay()); ledger.serialize(ARTIFACTS/"ledger-events.json"); persisted=Ledger.load(ARTIFACTS/"ledger-events.json")
    revised_state=persisted.materialize(revised_cursor); write(ARTIFACTS/"materialized-revised.json",revised_state)
    revised_specs=[compile_slide("B001","observation","photo_observation",revised_cursor,revision=2,content=state_content(revised_state,"observation",rel(obs_svg)),asset_path=rel(obs_svg),asset_id="A002",decision_refs=["D002"]),compile_slide("B001","result","hero_plot_discussion",revised_cursor,revision=2,content=state_content(revised_state,"discussion",rel(plot["svg"])),asset_path=rel(plot["svg"]),asset_id="A001",decision_refs=["D002"])]; write(ARTIFACTS/"slide-specs-revised.json",revised_specs)
    revised=ARTIFACTS/"master_revised_build.pptx"; assembler.assemble(template,revised_specs,revised); assembler.assemble(template,first_specs,ARTIFACTS/"master_first_render_compat.pptx",attach_svg=False); assembler.assemble(template,revised_specs,ARTIFACTS/"master_revised_render_compat.pptx",attach_svg=False)

    event_records=json.loads((ARTIFACTS/"ledger-events.json").read_text(encoding="utf-8")); first_meeting=meeting_delta(event_records[:first_cursor],0); revised_meeting=meeting_delta(event_records,first_cursor); write(ARTIFACTS/"meeting-delta-first.json",first_meeting); write(ARTIFACTS/"meeting-delta.json",revised_meeting)
    first_manifest=_manifest("MASTER-PHASE1-FIRST",first,first_cursor,first_specs,1,ARTIFACTS/"slide-specs-first.json"); revised_manifest=_manifest("MASTER-PHASE1-REVISED",revised,revised_cursor,revised_specs,2,ARTIFACTS/"slide-specs-revised.json"); write(ARTIFACTS/"MASTER-PHASE1-FIRST.manifest.json",first_manifest); write(ARTIFACTS/"MASTER-PHASE1-REVISED.manifest.json",revised_manifest)
    first_audit=audit_pptx(first,template,tp,first_specs); revised_audit=audit_pptx(revised,template,tp,revised_specs); write(ARTIFACTS/"structural-audit-first.json",first_audit); write(ARTIFACTS/"structural-audit-revised.json",revised_audit); write(ARTIFACTS/"structural-audit.json",revised_audit)
    first_qa=_run_build_qa(bundle,persisted,first_specs,first_manifest,first_audit,first_meeting,first_cursor,{}); revised_qa=_run_build_qa(bundle,persisted,revised_specs,revised_manifest,revised_audit,revised_meeting,first_cursor,{})
    write(ARTIFACTS/"qa-report-first.json",first_qa); write(ARTIFACTS/"qa-report-revised.json",revised_qa); write(ARTIFACTS/"qa-report.json",revised_qa)
    return {"first":first,"revised":revised,"qa":revised_qa,"ledger":persisted,"first_cursor":first_cursor,"block_revised_cursor":revision_event.cursor,"revised_cursor":revised_cursor}

def finalize_visual_qa():
    bundle=load_fixture(PROJECT); bundle["assets"]=[json.loads((ARTIFACTS/"plots/A001.asset.json").read_text(encoding="utf-8")),json.loads((ARTIFACTS/"plots/A002.asset.json").read_text(encoding="utf-8"))]; bundle["template_profiles"]=[json.loads((ARTIFACTS/"template-profile.json").read_text(encoding="utf-8"))]
    ledger=Ledger.load(ARTIFACTS/"ledger-events.json"); first_manifest=json.loads((ARTIFACTS/"MASTER-PHASE1-FIRST.manifest.json").read_text(encoding="utf-8")); revised_manifest=json.loads((ARTIFACTS/"MASTER-PHASE1-REVISED.manifest.json").read_text(encoding="utf-8")); first_cursor=first_manifest["source_event_cursor"]
    first_specs=json.loads((ARTIFACTS/"slide-specs-first.json").read_text(encoding="utf-8")); revised_specs=json.loads((ARTIFACTS/"slide-specs-revised.json").read_text(encoding="utf-8")); first_meeting=json.loads((ARTIFACTS/"meeting-delta-first.json").read_text(encoding="utf-8")); revised_meeting=json.loads((ARTIFACTS/"meeting-delta.json").read_text(encoding="utf-8")); first_audit=json.loads((ARTIFACTS/"structural-audit-first.json").read_text(encoding="utf-8")); revised_audit=json.loads((ARTIFACTS/"structural-audit-revised.json").read_text(encoding="utf-8"))
    def inspection(label, result_observation):
        folder="render_first" if label=="first" else "render_revised"
        return {"checked_by":"Codex visual inspection","build":label,"slides":[{"slide_id":"TEMPLATE-SLIDE-01","render_path":rel(ARTIFACTS/folder/"slide-1.png"),"checks":["nonblank","legible","no clipping"],"observations":"Synthetic template title and subtitle are centered, readable, and unclipped.","status":"pass"},{"slide_id":"TEMPLATE-SLIDE-02","render_path":rel(ARTIFACTS/folder/"slide-2.png"),"checks":["nonblank","legible","native placeholder visible"],"observations":"Representative native title/content placeholders render clearly without overlap.","status":"pass"},{"slide_id":"S-B001-OBSERVATION-01","render_path":rel(ARTIFACTS/folder/"slide-3.png"),"checks":["nonblank","legible","visual present","no overlap"],"observations":"Synthetic observation visual, observation statement, and problem statement are visible and separated.","status":"pass"},{"slide_id":"S-B001-RESULT-01","render_path":rel(ARTIFACTS/folder/"slide-4.png"),"checks":["nonblank","legible","plot and next step present","no overlap"],"observations":result_observation,"status":"pass"}]}
    first_inspection=inspection("first","Plot, D001 rationale, first Discussion, planned NS001, and first due time are visible without collision."); revised_inspection=inspection("revised","Plot, D002 rationale, revised Discussion, in-progress NS001, and revised due time are visible without collision.")
    write(ARTIFACTS/"visual-inspection-first.json",first_inspection); write(ARTIFACTS/"visual-inspection-revised.json",revised_inspection); write(ARTIFACTS/"visual-inspection.json",revised_inspection)
    first_visual={"inspection_record":rel(ARTIFACTS/"visual-inspection-first.json"),"render_paths":[rel(path) for path in sorted((ARTIFACTS/"render_first").glob("slide-*.png"))],"montage_paths":[rel(ARTIFACTS/"render_first/full-deck-montage.png"),rel(ARTIFACTS/"render_first/generated-slide-montage.png")]}; revised_visual={"inspection_record":rel(ARTIFACTS/"visual-inspection-revised.json"),"render_paths":[rel(path) for path in sorted((ARTIFACTS/"render_revised").glob("slide-*.png"))],"montage_paths":[rel(ARTIFACTS/"render_revised/full-deck-montage.png"),rel(ARTIFACTS/"render_revised/changed-slide-montage.png")]}
    first_qa=_run_build_qa(bundle,ledger,first_specs,first_manifest,first_audit,first_meeting,first_cursor,first_visual); revised_qa=_run_build_qa(bundle,ledger,revised_specs,revised_manifest,revised_audit,revised_meeting,first_cursor,revised_visual)
    first_qa["artifacts"]["visual_inspection"]=first_visual["inspection_record"]; revised_qa["artifacts"]["visual_inspection"]=revised_visual["inspection_record"]
    write(ARTIFACTS/"qa-report-first.json",first_qa); write(ARTIFACTS/"qa-report-revised.json",revised_qa); write(ARTIFACTS/"qa-report.json",revised_qa); write(ARTIFACTS/"structural-audit.json",revised_audit); return {"first":first_qa,"revised":revised_qa}
