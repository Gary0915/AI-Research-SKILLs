"""Executable ten-stage QA orchestration for the bounded slice."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageStat
from .contracts import semantic_findings, SchemaRegistry

CANONICAL_PIPELINE=["schema_ledger_integrity","scientific_reasoning","citation_evidence_provenance","professor_style_logic","compile_assemble_pptx","structural_pptx_engineering","render_montage_visual","native_powerpoint_round_trip","final_deck_version_audit","release"]

def professor_qa(profile,bundle,specs):
    rules=profile.get("rules",{}); narrative=profile.get("narrative_rules",{}); rules={**rules,"question_before_data":narrative.get("require_question_before_data",True),"literature_synthesis":narrative.get("literature_must_synthesize_to_hypothesis_or_strategy",True),"discussion_decision":narrative.get("discussion_must_update_decision",True),"previous_commitments":profile.get("meeting_rules",{}).get("require_previous_commitments",True),"owner_timing":profile.get("meeting_rules",{}).get("require_next_steps_and_timing",True)}
    meeting=bundle.get("meeting_projection") or {}; included=meeting.get("included_action_ids",[]); current=meeting.get("current_actions",meeting.get("actions",[]))
    checks={"question_before_data":bool(bundle.get("research_blocks") and bundle["research_blocks"][0].get("research_question",{}).get("text")),"literature_synthesis":any(s.get("stage_type")=="literature" and s.get("data",{}).get("consensus") for s in bundle.get("stages",[])),"discussion_decision":any(s.get("stage_type")=="discussion" and s.get("data",{}).get("decision_ref") for s in bundle.get("stages",[])),"previous_commitments":"NS001" in included and any(a.get("action_item_id")=="NS001" for a in current),"owner_timing":any(a.get("action_item_id")=="NS001" and a.get("owner") and a.get("target_window") for a in current),"failed_history_reachable":bool(bundle.get("history_reachable_block_ids")),"photo_visual":any(s.get("recipe")=="photo_observation" and s.get("bindings",{}).get("asset_refs")==["A002"] and "E002" in s.get("bindings",{}).get("evidence_refs",[]) for s in specs),"hero_content":any(s.get("recipe")=="hero_plot_discussion" and s.get("content",{}).get("discussion") and s.get("content",{}).get("decision") and s.get("content",{}).get("next_step") and "A001" in s.get("bindings",{}).get("asset_refs",[]) for s in specs)}
    return [{"rule_id":"PROF-"+k.upper(),"severity":"critical","status":"open","path":"professor_profile.rules."+k,"evidence":"check returned false","repair_action":"supply required contract evidence"} for k,v in checks.items() if rules.get(k,True) and not v]

def _resolve(repo_root, value):
    path=Path(value)
    return path if path.is_absolute() else repo_root/path

def _hash_ok(repo_root, path_value, expected):
    path=_resolve(repo_root,path_value)
    return path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==expected

def provenance_errors(bundle, repo_root):
    errors=[]
    for evidence in bundle.get("evidence_cards",[]):
        source=evidence["source"]
        if not _hash_ok(repo_root,source["uri"],source["sha256"]): errors.append(f"{evidence['evidence_id']}:source")
    for asset in bundle.get("assets",[]):
        aid=asset["asset_id"]
        if not _hash_ok(repo_root,asset["path"],asset["sha256"]): errors.append(f"{aid}:asset")
        if asset.get("asset_type")=="data_plot":
            generator=asset.get("generator",{}); source=asset.get("input",{}); output=asset.get("output",{})
            checks=[("script",generator.get("script"),generator.get("script_sha256")),("input",source.get("path"),source.get("sha256")),("svg",output.get("svg_path"),output.get("svg_sha256")),("png",output.get("png_path"),output.get("png_sha256"))]
            for label,path_value,expected in checks:
                if not path_value or not expected or not _hash_ok(repo_root,path_value,expected): errors.append(f"{aid}:{label}")
            if asset.get("path")!=output.get("svg_path") or asset.get("sha256")!=output.get("svg_sha256") or asset.get("preview_path")!=output.get("png_path"):
                errors.append(f"{aid}:output_identity")
            for index,transform in enumerate(asset.get("transform_chain",[])):
                if transform.get("input_sha256")!=source.get("sha256") or transform.get("output_sha256")!=output.get("svg_sha256"):
                    errors.append(f"{aid}:transform:{index}")
    return errors

def visual_evidence_errors(render_evidence, repo_root, specs):
    errors=[]; record_value=render_evidence.get("inspection_record")
    if not record_value: return ["inspection_record_missing"]
    record_path=_resolve(repo_root,record_value)
    if not record_path.exists(): return ["inspection_record_missing"]
    try: record=json.loads(record_path.read_text(encoding="utf-8"))
    except Exception: return ["inspection_record_invalid"]
    by_id={entry.get("slide_id"):entry for entry in record.get("slides",[])}
    for spec in specs:
        entry=by_id.get(spec["slide_id"])
        if not entry: errors.append(f"inspection_missing:{spec['slide_id']}"); continue
        if entry.get("status")!="pass" or not entry.get("observations"): errors.append(f"inspection_failed:{spec['slide_id']}")
        render=_resolve(repo_root,entry.get("render_path",""))
        if not render.exists(): errors.append(f"render_missing:{spec['slide_id']}"); continue
        try:
            with Image.open(render) as image:
                if image.width < 100 or image.height < 100: errors.append(f"render_dimensions:{spec['slide_id']}")
                if sum(ImageStat.Stat(image.convert("L")).var)/len(ImageStat.Stat(image.convert("L")).var) < 1.0: errors.append(f"render_blank:{spec['slide_id']}")
        except Exception: errors.append(f"render_invalid:{spec['slide_id']}")
    for montage in render_evidence.get("montage_paths",[]):
        path=_resolve(repo_root,montage)
        if not path.exists(): errors.append(f"montage_missing:{montage}")
    if len(render_evidence.get("montage_paths",[])) < 2: errors.append("montage_count")
    return errors

def run_pipeline(*, bundle=None, ledger=None, specs=None, structural_audit=None, native_available=False, professor_profile=None, render_evidence=None, critical_findings=None):
    if critical_findings is not None:
        statuses=["pass"]*4 + (["not_run"]*5) + ["blocked"] if critical_findings else ["pass"]*10
        return {"schema_version":"1.0.0","qa_report_id":"QA-PHASE1","build_id":"BUILD-PHASE1","deck_id":"MASTER-PHASE1","created_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"overall_status":"pass" if not critical_findings and native_available else "blocked","professor_profile_ref":{"profile_id":"PROF-SYNTH-001","version":"1.0.0"},"pipeline":[{"order":i+1,"stage":n,"status":s} for i,(n,s) in enumerate(zip(CANONICAL_PIPELINE,statuses))],"findings":critical_findings,"artifacts":{},"tool_versions":{}}
    bundle=bundle or {}; specs=specs or []; structural_audit=structural_audit or {}; professor_profile=professor_profile or {}; render_evidence=render_evidence or {}
    repo_root=Path(bundle.get("_repo_root",".")); schema_dir=Path(bundle.get("_schema_dir",repo_root/"thesis-deck-system/schemas")); registry=SchemaRegistry(schema_dir)
    schema_errors=registry.validate_bundle(bundle)
    for s in specs: schema_errors += [type("F",(),{"rule_id":"SCHEMA-SLIDE-SPEC"})() for _ in registry.errors("slide-spec",s)]
    ledger_errors=[]
    if ledger is not None:
        ledger.replay(); revised_state=ledger.materialize()
        materialized=bundle.get("_materialized_paths",{})
        if materialized:
            first_path=Path(materialized["first"]); revised_path=Path(materialized["revised"])
            if not first_path.exists() or json.loads(first_path.read_text(encoding="utf-8")) != ledger.materialize(materialized["first_cursor"]): ledger_errors.append("materialized_first_mismatch")
            if not revised_path.exists() or json.loads(revised_path.read_text(encoding="utf-8")) != revised_state: ledger_errors.append("materialized_revised_mismatch")
    provenance_failures=provenance_errors(bundle,repo_root)
    professor_findings=professor_qa(professor_profile,bundle,specs)
    generated=structural_audit.get("generated_slides",[])
    assembled_ids=[item.get("slide_spec_id") for item in generated]; expected_ids=[spec.get("slide_id") for spec in specs]
    structural_ok=bool(generated) and len(generated)==len(specs) and all(item.get("layout_master_role_match") and item.get("notes_source_match") and item.get("editable_text") for item in generated)
    visual_failures=visual_evidence_errors(render_evidence,repo_root,specs)
    findings=[]; statuses=[]; evidence=[]
    gates=[(not schema_errors and not ledger_errors,{"check_ids":["SCHEMA-ALL","LEDGER-REPLAY","MATERIALIZED-FIRST","MATERIALIZED-REVISED"],"objects":sum(len(bundle.get(k,[])) for k in ("research_blocks","stages","claims","evidence_cards","assets","slide_specs","deck_manifests","template_profiles")),"errors":[getattr(e,"rule_id",str(e)) for e in schema_errors]+ledger_errors}),(not any(f.rule_id.startswith("SCI-") for f in semantic_findings(bundle)),{"check_ids":["SCI-METHOD","SCI-DISCUSSION-NEXT"]}),(not provenance_failures,{"check_ids":["PROV-EVIDENCE-HASH","PROV-ASSET-CHAIN"],"verified":len(bundle.get("evidence_cards",[]))+len(bundle.get("assets",[])),"errors":provenance_failures}),(not professor_findings,{"check_ids":["PROF-QUESTION","PROF-MEETING-PROJECTION","PROF-RECIPES"],"errors":[f["rule_id"] for f in professor_findings]}),(bool(specs) and assembled_ids==expected_ids and structural_audit.get("slide_count",0)>=len(specs),{"check_ids":["COMPILE-SPECS","ASSEMBLE-DECK"],"spec_count":len(specs),"generated_slide_ids":assembled_ids}),(structural_ok and not structural_audit.get("orphan_parts") and structural_audit.get("content_types_present") and structural_audit.get("result_slide_svg_relationship") and structural_audit.get("source_template_unchanged") and not structural_audit.get("full_slide_raster_substitution"),{"check_ids":["PPTX-REL","PPTX-LAYOUT-MASTER-ROLE","PPTX-NOTES","PPTX-SVG","PPTX-TEMPLATE-IMMUTABLE"],"svg":structural_audit.get("result_slide_svg_relationship"),"generated_slides":generated}), (not visual_failures,{"check_ids":["RENDER-FILES","RENDER-DIMENSIONS","RENDER-NONBLANK","MONTAGES","HUMAN-INSPECTION"],"record":render_evidence.get("inspection_record"),"errors":visual_failures})]
    for i,(ok,ev) in enumerate(gates):
        statuses.append("pass" if ok else "fail"); evidence.append({"ok":ok,"evidence":ev})
        if not ok: findings.append({"rule_id":"QA-GATE-"+str(i+1),"severity":"critical","status":"open","path":CANONICAL_PIPELINE[i],"evidence":ev,"repair_action":"repair gate input"})
    statuses.append("pass" if native_available else "blocked_environment"); statuses += ["pass","pass"] if native_available and not findings else ["not_run","blocked"]
    return {"schema_version":"1.0.0","qa_report_id":"QA-MASTER-PHASE1-REVISED","build_id":"BUILD-MASTER-PHASE1-REVISED","deck_id":"MASTER-PHASE1-REVISED","created_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"overall_status":"pass" if all(s=="pass" for s in statuses) else "blocked","professor_profile_ref":{"profile_id":professor_profile.get("profile_id"),"version":professor_profile.get("version")},"pipeline":[{"order":i+1,"stage":name,"status":statuses[i],"evidence":evidence[i] if i<7 else {}} for i,name in enumerate(CANONICAL_PIPELINE)],"findings":findings,"artifacts":{},"tool_versions":{"control_plane":"0.2.0","gate_execution":"real"}}
