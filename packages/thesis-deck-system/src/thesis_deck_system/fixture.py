"""Load the committed synthetic project as one referentially checked bundle."""
from pathlib import Path
import hashlib
import yaml
from .contracts import SchemaRegistry

def load_fixture(root: Path) -> dict:
    root = Path(root)
    def many(folder, suffix=".yaml"):
        return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((root / folder).glob(f"*{suffix}"))]
    blocks = [yaml.safe_load((root / "block.yaml").read_text(encoding="utf-8"))]
    claims = yaml.safe_load((root / "claims.yaml").read_text(encoding="utf-8"))
    if not isinstance(claims, list): claims = [claims]
    actions = yaml.safe_load((root / "actions.yaml").read_text(encoding="utf-8"))
    if not isinstance(actions, list): actions = [actions]
    profile = yaml.safe_load((root / "professor-profile.yaml").read_text(encoding="utf-8"))
    stages = many("stages")
    evidence = many("evidence")
    decisions = many("decisions")
    decisions = [{"schema_version":"1.0.0","decision_id":d["decision_id"],"timestamp":d["created_at"],"actor":{"type":"person","id":"researcher"},"decision_type":"research_gate","subject_refs":["B001"],"choice":d["choice"],"alternatives":[],"rationale":d["rationale"],"evidence_refs":d["evidence_refs"],"provenance":"synthetic_fixture"} for d in decisions]
    assets = [{"schema_version":"1.0.0","asset_id":"A001","asset_type":"data_plot","title":"Synthetic positional plot","evidence_role":"synthetic_test_evidence","source_evidence":["E001"],"path":"thesis-deck-system/artifacts/phase1/plots/B001_defect_density.svg","preview_path":"thesis-deck-system/artifacts/phase1/plots/B001_defect_density.png","mime_type":"image/svg+xml","sha256":"0"*64,"editable":True,"generator":{"kind":"matplotlib"},"transform_chain":[],"provenance":"synthetic_fixture","status":"approved"}]
    bundle = {"research_blocks": blocks, "claims": claims, "actions": actions, "stages": stages, "evidence_cards": evidence, "decisions": decisions, "professor_profiles": [profile], "assets": assets, "meeting_projection": {"prior_commitment_ids": ["NS001"], "included_action_ids": ["NS001"]}, "history_reachable_block_ids": ["B001"]}
    registry = SchemaRegistry(root.parents[1] / "schemas")
    findings = registry.validate_bundle(bundle)
    if findings: raise ValueError("fixture validation failed: " + "; ".join(f.rule_id for f in findings))
    refs = blocks[0]["stage_refs"]
    stage_ids = {s["stage_id"] for s in stages}
    for sid in list(refs.values()):
        if sid not in stage_ids and sid != "NS001": raise ValueError(f"missing stage {sid}")
    evidence_ids = {e["evidence_id"] for e in evidence}
    for s in stages:
        for eid in s.get("evidence_refs", []):
            if eid not in evidence_ids: raise ValueError(f"missing evidence {eid}")
    return bundle

def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
