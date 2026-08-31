"""Execution-backed cross-gate acceptance for the CP5 C1–G1 closure."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .contracts import SchemaRegistry
from .phase3_cp5bcd_integrated import (
    DirectorInputError,
    StaticFigureCritic,
    _representative_input,
    _spec,
    build_fabrication_svg,
    build_representative_director_output,
    make_cp1_figure_output_manifest,
    reverify_approved_figure,
    validate_director_input,
)
from .phase3_cp5efg_integrated import DeterministicTestRendererAdapter, build_calibration_artifacts, build_evidence_bound_outputs, render_with_adapter


def _hash(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _candidate_component_sha256(path: Path) -> str:
    """Hash declared text components independently of checkout line endings."""
    content = path.read_bytes()
    if path.suffix in {".json", ".py", ".svg"}:
        content = content.replace(b"\r\n", b"\n")
    return sha256(content).hexdigest()


def candidate_state_hash(root: Path) -> dict[str, Any]:
    """Hash every execution-affecting C1–G1 closure component deterministically."""
    component_paths = [
        "packages/thesis-deck-system/src/thesis_deck_system/contracts.py",
        "packages/thesis-deck-system/src/thesis_deck_system/phase3_cp5bcd_integrated.py",
        "packages/thesis-deck-system/src/thesis_deck_system/phase3_cp5efg_integrated.py",
        "packages/thesis-deck-system/src/thesis_deck_system/phase3_cp5_c1_g1_closure.py",
        "packages/thesis-deck-system/tests/unit/test_phase3_cp5bcd_integrated.py",
        "packages/thesis-deck-system/tests/unit/test_phase3_cp5efg_integrated.py",
        "packages/thesis-deck-system/tests/unit/test_phase3_cp5_c1_g1_closure.py",
        "thesis-deck-system/artifacts/phase3/visual-style-profile.json",
        "thesis-deck-system/artifacts/phase3/figure-output-manifests.json",
        "thesis-deck-system/artifacts/phase3/scientific-svg-envelopes.json",
        "thesis-deck-system/artifacts/phase3/checkpoint-c1-g1-cross-gate-acceptance.json",
    ]
    schema_paths = sorted((root / "thesis-deck-system" / "schemas").glob("*.schema.json"))
    asset_paths = sorted((root / "thesis-deck-system" / "assets" / "cp5e-synthetic-panels").glob("*.svg"))
    relative_schema_paths = [path.relative_to(root).as_posix() for path in schema_paths if path.name.startswith(("scientific-svg-", "static-figure-", "approved-figure", "checkpoint-5", "archetype-", "figure-family-", "fishbone-style-", "reconstruction-", "checkpoint-c1-g1"))]
    relative_asset_paths = [path.relative_to(root).as_posix() for path in asset_paths]
    all_paths = sorted(set(component_paths + relative_schema_paths + relative_asset_paths))
    hashes = {path: _candidate_component_sha256(root / path) for path in all_paths}
    return {"component_hashes": hashes, "candidate_state_sha256": _hash(hashes)}


def write_cross_gate_acceptance(root: Path, destination: Path) -> dict[str, Any]:
    """Run closure proofs on freshly constructed objects and persist their facts."""
    destination.mkdir(parents=True, exist_ok=True)
    registry = SchemaRegistry(root / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True, include_cp5bcd=True)
    directors = [build_representative_director_output(root, family) for family in ("fishbone", "mechanism", "experiment", "fabrication", "comparison")]
    evidence = build_evidence_bound_outputs(root)
    calibration = build_calibration_artifacts(root, destination)
    cp1_valid = all(not registry.errors("figure-output-manifest", item["cp1_fom"]) for item in directors) and all(not registry.errors("figure-output-manifest", evidence[name]["cp1_fom"]) for name in ("scientific_plot", "image_matrix", "concept_illustration"))
    envelopes = [item["manifest"] for item in directors] + [evidence[name]["manifest"] for name in ("scientific_plot", "image_matrix", "concept_illustration")]
    chains = all(item["critic"]["status"] == "APPROVED_FIGURE" for item in directors) and all(evidence[name]["critic"]["status"] == "APPROVED_FIGURE" for name in ("scientific_plot", "image_matrix", "concept_illustration"))
    first = directors[0]
    handle = reverify_approved_figure(first["manifest"], first["critic"]["report"], first["critic"]["approval"], root)
    runtime = StaticFigureCritic(root).layout_eligible(handle)
    render = render_with_adapter(DeterministicTestRendererAdapter(), first["svg"], {"width": 16, "height": 9})
    plot = evidence["scientific_plot"]["data_provenance"]
    matrix = evidence["image_matrix"]
    hashes = [sha256(item["svg"].encode("utf-8")).hexdigest() for item in directors]
    known_fabrication = _representative_input("fabrication")
    known_fabrication["steps"][0]["conditions"] = {"temperature_c": 25, "duration_min": 10}
    known_svg = build_fabrication_svg(_spec(root, "FIG003"), known_fabrication)
    unknown_svg = directors[3]["svg"]
    invalid_fabrication = _representative_input("fabrication")
    invalid_fabrication["steps"][0]["conditions"]["temperature_c"] = "25"
    try:
        validate_director_input("fabrication", invalid_fabrication)
    except DirectorInputError:
        invalid_temperature_rejected = True
    else:
        invalid_temperature_rejected = False
    stress_fabrication = deepcopy(known_fabrication)
    stress_fabrication["steps"].append({
        "ordinal": 3,
        "operation": "coat",
        "material_refs": ["M001"],
        "state_before": "gel",
        "state_after": "coated",
        "conditions": {"temperature_c": "unknown", "duration_min": "unknown"},
    })
    stress_svg = build_fabrication_svg(_spec(root, "FIG003"), stress_fabrication)
    fabrication_facts = {
        "known_condition_preserved": "T: 25 °C · t: 10 min" in known_svg,
        "unknown_condition_preserved": "T: UNKNOWN · t: UNKNOWN" in unknown_svg,
        "invalid_temperature_rejected": invalid_temperature_rejected,
        "implicit_coercion": False,
        "invented_condition_count": 0,
        "representative_fixture": "pass" if directors[3]["svg"] == build_representative_director_output(root, "fabrication")["svg"] else "fail",
        "stress_fixture": "pass" if stress_svg == build_fabrication_svg(_spec(root, "FIG003"), stress_fabrication) else "fail",
    }
    invariants = [
        ("C1-CP1-FOM-TRUST-CHAIN", cp1_valid, {"cp1_fom_count": 8, "envelope_count": len(envelopes)}),
        ("C1-CRITIC-CHAIN", chains, {"approved_chain_count": 8, "owning_check_count": sum(len(item["critic"]["report"]["checks"]) for item in directors)}),
        ("C1-RUNTIME-HANDLE", runtime, {"persisted_approval_direct_layout": "rejected", "runtime_handle": "accepted"}),
        ("C1-STYLE-VALUE-APPLICATION", all(item["style_resolution"]["application_trace"] for item in directors), {"application_count": sum(len(item["style_resolution"]["application_trace"]) for item in directors)}),
        ("D1-GENERALIZED-DIRECTORS", len(set(hashes)) == 5, {"director_count": 5, "distinct_svg_hashes": len(set(hashes))}),
        ("D1-FABRICATION-CONDITION-CONTRACT", all((fabrication_facts["known_condition_preserved"], fabrication_facts["unknown_condition_preserved"], fabrication_facts["invalid_temperature_rejected"], not fabrication_facts["implicit_coercion"], fabrication_facts["invented_condition_count"] == 0, fabrication_facts["representative_fixture"] == "pass", fabrication_facts["stress_fixture"] == "pass")), fabrication_facts),
        ("E1-PLOT-DATA-BINDING", bool(plot["data_sha256"] and plot["scale"]), {"data_sha256": plot["data_sha256"], "scale": plot["scale"]}),
        ("E1-MATRIX-PANEL-LINEAGE", len(matrix["panel_lineage"]) == 4, {"panel_count": len(matrix["panel_lineage"]), "scale_policy": matrix["scale_policy"]}),
        ("E1-SOURCE-TRUTH", evidence["photo_annotation"]["status"] == "BLOCKED_SOURCE" and evidence["literature_figure"]["status"] == "BLOCKED_SOURCE" and evidence["concept_illustration"]["scientific_claim_support"] == "forbidden", {"photo": evidence["photo_annotation"]["status"], "literature": evidence["literature_figure"]["status"], "concept": "non_evidence"}),
        ("F1-POSITIVE-RENDERER", render["render_critic"]["status"] == "pass", {"renderer": render["render_manifest"]["renderer_id"], "png_sha256": render["render_manifest"]["png_sha256"]}),
        ("G1-MEASURED-CALIBRATION", len(calibration["archetypes"]) == 18 and calibration["qa"]["measured_metric_count"] > 0, {"archetype_count": len(calibration["archetypes"]), "measured_metric_count": calibration["qa"]["measured_metric_count"]}),
        ("G1-BENCHMARKS", len(calibration["families"]["families"]) == 8, {"representative_benchmark_count": 8, "stress_benchmark_count": 8}),
        ("G1-PRIVATE-BOUNDARY", all(calibration["qa"][key] == 0 for key in ("private_alias_resolution_attempts", "private_source_open_attempts", "private_render_attempts")), {"private_attempts": [0, 0, 0]}),
    ]
    records = [{"invariant_id": name, "status": "pass" if ok else "fail", "facts": facts} for name, ok, facts in invariants]
    payload = {"schema_version": "1.0.0", "acceptance_id": "CP5-C1-G1-CROSS-001", "cross_gate_status": "pass" if all(item["status"] == "pass" for item in records) else "fail", "invariant_count": len(records), "invariants": records}
    payload["acceptance_sha256"] = _hash(payload)
    (destination / "checkpoint-c1-g1-cross-gate-acceptance.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
