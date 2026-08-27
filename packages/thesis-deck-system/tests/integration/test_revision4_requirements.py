import copy
import json
from pathlib import Path

from thesis_deck_system.build import ARTIFACTS, PROJECT, ROOT, build
import thesis_deck_system.contracts as contracts
from thesis_deck_system.contracts import SchemaRegistry
from thesis_deck_system.fixture import load_fixture
from thesis_deck_system.ledger import Ledger
from thesis_deck_system.qa import run_pipeline


SCHEMA_DIR = ROOT / "thesis-deck-system/schemas"


def _read(name: str):
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_real_block_revision_event_separates_first_and_revised_materializations():
    build()
    ledger = Ledger.load(ARTIFACTS / "ledger-events.json")
    first = _read("materialized-first.json")
    revised = _read("materialized-revised.json")
    first_cursor = _read("MASTER-PHASE1-FIRST.manifest.json")["source_event_cursor"]
    revised_cursor = _read("MASTER-PHASE1-REVISED.manifest.json")["source_event_cursor"]
    revision_events = [event for event in ledger.replay() if event.event_type == "block_revised"]

    assert first["blocks"]["B001"]["revision"] == 1
    assert revised["blocks"]["B001"]["revision"] == 2
    assert len(revision_events) == 1
    assert first_cursor < revision_events[0].cursor <= revised_cursor
    assert ledger.materialize(first_cursor) == first
    assert ledger.materialize(revised_cursor) == revised


def test_each_block_revision_is_graph_closed_and_temporal_bindings_reject_future_refs():
    build()
    ledger = Ledger.load(ARTIFACTS / "ledger-events.json")
    bundle = load_fixture(PROJECT)
    bundle["assets"] = [_read("plots/A001.asset.json"), _read("plots/A002.asset.json")]
    first_specs = _read("slide-specs-first.json")
    revised_specs = _read("slide-specs-revised.json")
    manifests = [_read("MASTER-PHASE1-FIRST.manifest.json"), _read("MASTER-PHASE1-REVISED.manifest.json")]
    reports = [_read("qa-report-first.json"), _read("qa-report-revised.json")]

    assert contracts.validate_temporal_bindings(bundle, ledger, first_specs + revised_specs, manifests, reports) == []
    first = ledger.materialize(manifests[0]["source_event_cursor"])["blocks"]["B001"]
    revised = ledger.materialize(manifests[1]["source_event_cursor"])["blocks"]["B001"]
    assert {"E001", "E002", "E003"} <= set(first["evidence_refs"])
    assert {"A001", "A002"} <= set(first["asset_refs"])
    assert first["decision_refs"] == ["D001"]
    assert {"D001", "D002"} <= set(revised["decision_refs"])

    future_spec = copy.deepcopy(first_specs)
    future_spec[1]["block_refs"][0]["revision"] = 2
    future_spec[1]["bindings"]["decision_refs"] = ["D002"]
    findings = contracts.validate_temporal_bindings(bundle, ledger, future_spec, [manifests[0]], reports)
    assert {finding.rule_id for finding in findings} >= {"TEMPORAL-BLOCK-REVISION-MISMATCH", "TEMPORAL-DECISION-UNREACHABLE"}

    future_action = copy.deepcopy(first_specs)
    future_action[0]["bindings"]["action_refs"] = ["NS999"]
    assert "TEMPORAL-ACTION-UNREACHABLE" in {
        finding.rule_id for finding in contracts.validate_temporal_bindings(bundle, ledger, future_action, [], reports)
    }

    wrong_manifest = copy.deepcopy(manifests[1])
    wrong_manifest["slides"][0]["block_ref"]["revision"] = 1
    assert "TEMPORAL-BLOCK-REVISION-MISMATCH" in {
        finding.rule_id for finding in contracts.validate_temporal_bindings(bundle, ledger, revised_specs, [wrong_manifest], reports)
    }


def test_all_twelve_schemas_explicitly_type_patterns_formats_and_reject_numeric_ids_dates():
    registry = SchemaRegistry(SCHEMA_DIR)
    assert len(registry.names) == 12

    def walk(node, path="$", errors=None):
        errors = [] if errors is None else errors
        if isinstance(node, dict):
            if "pattern" in node and node.get("type") != "string":
                errors.append(f"{path}:pattern")
            if node.get("format") in {"date", "date-time"} and node.get("type") != "string":
                errors.append(f"{path}:format")
            for key, value in node.items():
                walk(value, f"{path}/{key}", errors)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}/{index}", errors)
        return errors

    for name in registry.names:
        schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
        assert walk(schema) == [], name

    bundle = load_fixture(PROJECT)
    cases = [
        ("research-block", bundle["research_blocks"][0], ("block_id",), 1),
        ("research-block", bundle["research_blocks"][0], ("research_question", "question_id"), 1),
        ("research-block", bundle["research_blocks"][0], ("created_at",), 1),
        ("claim", bundle["claims"][0], ("claim_id",), 1),
        ("evidence-card", bundle["evidence_cards"][0], ("evidence_id",), 1),
        ("next-step", bundle["actions"][0], ("action_item_id",), 1),
        ("decision-event", bundle["decisions"][0], ("decision_id",), 1),
        ("scientific-stage", bundle["stages"][0], ("updated_at",), 1),
    ]
    for schema_name, original, keys, value in cases:
        bad = copy.deepcopy(original)
        target = bad
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        assert registry.errors(schema_name, bad), (schema_name, keys)


def test_manifest_qa_scope_is_per_build_and_mismatch_is_rejected():
    build()
    ledger = Ledger.load(ARTIFACTS / "ledger-events.json")
    bundle = load_fixture(PROJECT)
    first_manifest = _read("MASTER-PHASE1-FIRST.manifest.json")
    revised_manifest = _read("MASTER-PHASE1-REVISED.manifest.json")
    first_qa = _read("qa-report-first.json")
    revised_qa = _read("qa-report-revised.json")

    assert first_manifest["qa_report_refs"] == ["QA-MASTER-PHASE1-FIRST"]
    assert revised_manifest["qa_report_refs"] == ["QA-MASTER-PHASE1-REVISED"]
    assert (first_qa["qa_report_id"], first_qa["build_id"], first_qa["deck_id"]) == (
        "QA-MASTER-PHASE1-FIRST", "BUILD-MASTER-PHASE1-FIRST", "MASTER-PHASE1-FIRST"
    )
    assert (revised_qa["qa_report_id"], revised_qa["build_id"], revised_qa["deck_id"]) == (
        "QA-MASTER-PHASE1-REVISED", "BUILD-MASTER-PHASE1-REVISED", "MASTER-PHASE1-REVISED"
    )
    assert first_qa["artifacts"]["source_cursor"] == first_manifest["source_event_cursor"]
    assert first_qa["artifacts"]["materialized_state"].endswith("materialized-first.json")
    assert revised_qa["artifacts"]["source_cursor"] == revised_manifest["source_event_cursor"]
    assert revised_qa["artifacts"]["materialized_state"].endswith("materialized-revised.json")

    bad = copy.deepcopy(first_manifest)
    bad["qa_report_refs"] = ["QA-MASTER-PHASE1-REVISED"]
    findings = contracts.validate_temporal_bindings(
        bundle, ledger, _read("slide-specs-first.json"), [bad], [first_qa, revised_qa]
    )
    assert "QA-SCOPE-MISMATCH" in {finding.rule_id for finding in findings}


def test_critical_findings_compatibility_path_cannot_certify_unexecuted_gates():
    report = run_pipeline(critical_findings=[], native_available=True)
    assert report["overall_status"] != "pass"
    assert all(stage["status"] != "pass" for stage in report["pipeline"][:7])
    assert report["tool_versions"]["gate_execution"] == "not_executed"


def test_canonical_phase1_json_yaml_contains_no_machine_absolute_paths():
    roots = [ROOT / "thesis-deck-system/examples/synthetic-project", ARTIFACTS]
    forbidden = []

    def scan(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                scan(item, f"{path}/{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                scan(item, f"{path}/{index}")
        elif isinstance(value, str):
            if len(value) >= 3 and value[1:3] in {":/", ":\\"}:
                forbidden.append((path, value))
            if value.startswith(("/", "\\\\")):
                forbidden.append((path, value))

    for root in roots:
        for path in sorted([*root.rglob("*.json"), *root.rglob("*.yaml")]):
            raw = path.read_text(encoding="utf-8")
            value = json.loads(raw) if path.suffix == ".json" else __import__("yaml").safe_load(raw)
            scan(value, path.relative_to(ROOT).as_posix())
    assert forbidden == []
