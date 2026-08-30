"""CP5-A RED/GREEN contract tests for the closed Scientific SVG language."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
ARTIFACTS = ROOT / "thesis-deck-system" / "artifacts" / "phase3"


def _svg(body: str, *, figure_id: str = "FIG001", version: str = "1.0.0") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 90" data-thesis-svg-version="{version}" data-thesis-figure-id="{figure_id}">{body}</svg>'''


def _valid_svg() -> str:
    return _svg('''
      <defs><marker id="obj-arrow" data-semantic-role="arrow" markerWidth="6" markerHeight="6"><path d="M 0 0 L 6 3 L 0 6 z" fill="#333333"/></marker></defs>
      <g id="obj-container" data-semantic-role="container"><rect id="obj-panel" data-semantic-role="panel" x="8" y="8" width="64" height="34" fill="#eeeeee" stroke="#333333"/><text id="obj-title" data-semantic-role="title" x="12" y="20" font-family="synthetic-test-sans" font-size="8">水凝膠 / Hydrogel<tspan id="obj-label" data-semantic-role="label" dx="2">量測結果 / Result</tspan></text><line id="obj-flow" data-semantic-role="arrow" x1="72" y1="25" x2="110" y2="25" stroke="#333333" marker-end="url(#obj-arrow)"/></g>
      <g id="obj-plot" data-semantic-role="plot_area" transform="translate(4 4) rotate(0)"><polyline id="obj-series" data-semantic-role="data_series" points="0,60 20,44 44,50" fill="none" stroke="#336699"/><path id="obj-branch" data-semantic-role="branch" d="M 8 76 L 40 64" fill="none" stroke="#333333"/></g>
    ''')


def _spec() -> dict:
    import json

    return json.loads((ARTIFACTS / "scientific-figure-specs.json").read_text(encoding="utf-8"))[0]


def _validator():
    from thesis_deck_system.phase3_cp5a_scientific_svg import ScientificSvgValidator

    return ScientificSvgValidator.load_default(ROOT)


def test_valid_synthetic_svg_is_schema_bound_canonical_and_cjk_preserving():
    result = _validator().validate(_valid_svg(), figure_spec=_spec())
    assert result["aggregate_status"] == "pass"
    assert result["identity"]["figure_id"] == "FIG001"
    assert result["identity"]["source_sha256"] != result["identity"]["canonical_sha256"] or result["identity"]["canonical_svg"]
    assert "水凝膠 / Hydrogel" in result["identity"]["canonical_svg"]


@pytest.mark.parametrize(
    ("body", "rule"),
    [
        ("<unknown id='obj-x' data-semantic-role='node'/>", "CP5A-ELEMENT-ALLOWLIST"),
        ("<script id='obj-x' data-semantic-role='node'>x</script>", "CP5A-FORBIDDEN-EXECUTABLE"),
        ("<foreignObject id='obj-x' data-semantic-role='node'/>", "CP5A-FORBIDDEN-EXECUTABLE"),
        ("<rect id='obj-x' data-semantic-role='panel' x='0' y='0' width='1' height='1' onclick='x()'/>", "CP5A-ATTRIBUTE-ALLOWLIST"),
        ("<rect id='obj-x' data-semantic-role='panel' x='0' y='0' width='1' height='1' mystery='x'/>", "CP5A-ATTRIBUTE-ALLOWLIST"),
        ("<image id='obj-x' data-semantic-role='image' href='https://example.invalid/x.png'/>", "CP5A-RESOURCE-POLICY"),
        ("<image id='obj-x' data-semantic-role='image' href='../private.png'/>", "CP5A-RESOURCE-POLICY"),
        ("<image id='obj-x' data-semantic-role='image' href='C:/private/x.png'/>", "CP5A-RESOURCE-POLICY"),
        ("<rect id='obj-x' data-semantic-role='unknown_role' x='0' y='0' width='1' height='1'/>", "CP5A-ROLE-REGISTRY"),
        ("<rect id='obj-x' data-semantic-role='arrow' x='0' y='0' width='1' height='1'/>", "CP5A-ROLE-ELEMENT-COMPATIBILITY"),
    ],
)
def test_validator_fails_closed_for_element_attribute_resource_and_role_mutations(body: str, rule: str):
    result = _validator().validate(_svg(body), figure_spec=_spec())
    assert result["aggregate_status"] == "fail"
    assert rule in {finding["rule_id"] for finding in result["findings"]}


@pytest.mark.parametrize(
    ("svg", "rule"),
    [
        (_svg("<rect id='obj-x' data-semantic-role='panel' x='0' y='0' width='-1' height='1'/>", version=""), "CP5A-PROFILE-VERSION"),
        ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1' data-thesis-svg-version='1.0.0'><rect id='obj-x' data-semantic-role='panel' x='0' y='0' width='1' height='1'/></svg>", "CP5A-FIGURE-ID"),
        (_svg("<rect id='obj-x' data-semantic-role='panel' x='0' y='0' width='NaN' height='1'/>",), "CP5A-NUMERIC-POLICY"),
        (_svg("<path id='obj-x' data-semantic-role='branch' d='M malformed' fill='none'/>",), "CP5A-PATH-GRAMMAR"),
        (_svg("<polyline id='obj-x' data-semantic-role='branch' points='1,bad' fill='none'/>",), "CP5A-POINTS-GRAMMAR"),
        (_svg("<g id='obj-x' data-semantic-role='group' transform='skewX(3)'/>",), "CP5A-TRANSFORM-GRAMMAR"),
        (_svg("<g id='obj-x' data-semantic-role='group' data-claim-id='C101'/>",), "CP5A-SCIENTIFIC-PROVENANCE-BOUNDARY"),
        (_svg("<image id='obj-x' data-semantic-role='image' href='data:image/png;base64,AAAA' data-raster-fallback='silent'/>",), "CP5A-RASTER-FALLBACK"),
    ],
)
def test_validator_rejects_root_geometry_provenance_and_raster_mutations(svg: str, rule: str):
    result = _validator().validate(svg, figure_spec=_spec())
    assert result["aggregate_status"] == "fail"
    assert rule in {finding["rule_id"] for finding in result["findings"]}


def test_duplicate_or_malformed_ids_and_wrong_spec_binding_fail():
    duplicate = _svg("<rect id='obj-x' data-semantic-role='panel' x='0' y='0' width='1' height='1'/><circle id='obj-x' data-semantic-role='node' cx='2' cy='2' r='1'/>")
    malformed = _svg("<rect id='bad id' data-semantic-role='panel' x='0' y='0' width='1' height='1'/>")
    wrong_spec = _spec()
    wrong_spec["figure_id"] = "FIG002"
    assert "CP5A-OBJECT-ID" in {item["rule_id"] for item in _validator().validate(duplicate, figure_spec=_spec())["findings"]}
    assert "CP5A-OBJECT-ID" in {item["rule_id"] for item in _validator().validate(malformed, figure_spec=_spec())["findings"]}
    assert "CP5A-FIGURE-SPEC-BINDING" in {item["rule_id"] for item in _validator().validate(_valid_svg(), figure_spec=wrong_spec)["findings"]}


def test_canonicalization_preserves_source_order_ignores_safe_formatting_and_hashes_visible_mutation():
    from thesis_deck_system.phase3_cp5a_scientific_svg import canonicalize_svg

    first = canonicalize_svg(_valid_svg())
    formatted = canonicalize_svg(_valid_svg().replace("><", ">\n<"))
    changed = canonicalize_svg(_valid_svg().replace("width=\"64\"", "width=\"65\""))
    reordered = canonicalize_svg(_valid_svg().replace("<rect id=\"obj-panel\"", "<line id=\"obj-before\" data-semantic-role=\"connector\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"/> <rect id=\"obj-panel\""))
    assert first["canonical_sha256"] == formatted["canonical_sha256"]
    assert first["canonical_sha256"] != changed["canonical_sha256"]
    assert first["canonical_sha256"] != reordered["canonical_sha256"]


def test_metadata_invisibility_is_static_only_and_semantic_attribute_cannot_change_presentation_ast():
    from thesis_deck_system.phase3_cp5a_scientific_svg import presentation_ast_hash, strip_semantic_metadata

    source = _valid_svg()
    assert presentation_ast_hash(source) == presentation_ast_hash(strip_semantic_metadata(source))
    assert "static" in _validator().validate(source, figure_spec=_spec())["metadata_invisibility"]["method"]


def test_cp5a_schemas_are_closed_and_profile_registry_are_versioned():
    from thesis_deck_system.contracts import SchemaRegistry

    registry = SchemaRegistry(ROOT / "thesis-deck-system" / "schemas", include_phase3=True, include_cp5a=True)
    for name in ("scientific-svg-profile", "semantic-svg-role-registry", "static-svg-qa-report", "scientific-svg-identity", "checkpoint-5a-execution-evidence", "checkpoint-5a-qa"):
        assert name in registry.names
    profile = _validator().profile
    profile["unexpected"] = "fail"
    assert registry.errors("scientific-svg-profile", profile)


def test_skill_contracts_require_validator_and_forbid_scientific_provenance_ownership():
    for skill in ("scientific-svg-authoring", "semantic-svg-governor"):
        text = (ROOT / "thesis-deck-system" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert "validator" in text.lower()
        assert "Ledger" in text


def test_execution_evidence_is_candidate_hash_bound_and_private_safe():
    from thesis_deck_system.phase3_cp5a_scientific_svg import build_cp5a_artifacts

    outputs = build_cp5a_artifacts(ROOT, tested_candidate_hash=None, tested_in_disposable_worktree=False)
    assert outputs["qa"]["aggregate_status"] == "fail"
    assert outputs["execution"]["private_alias_resolution_attempts"] == 0
    assert outputs["execution"]["private_source_open_attempts"] == 0
    assert outputs["execution"]["private_render_attempts"] == 0


def test_execution_evidence_fails_closed_without_an_executed_privacy_boundary():
    from thesis_deck_system.phase3_cp5a_scientific_svg import build_cp5a_artifacts

    outputs = build_cp5a_artifacts(
        ROOT,
        tested_candidate_hash=None,
        tested_in_disposable_worktree=False,
        privacy_config=None,
    )
    checks = {item["check_id"]: item["status"] for item in outputs["execution"]["owning_checks"]}
    assert checks["CP5A-REPOSITORY-STAGED-PRIVACY"] == "fail"
    assert outputs["execution"]["privacy_scan"]["repository_scan_executed"] is False


def test_candidate_state_mutation_invalidates_tested_evidence():
    from thesis_deck_system.phase3_cp5a_scientific_svg import candidate_state, validate_tested_candidate_state

    state = candidate_state(ROOT)
    mutated = deepcopy(state)
    mutated["component_hashes"]["cp5a:synthetic"] = "0" * 64
    assert not validate_tested_candidate_state(mutated, state)


def test_candidate_state_binds_the_modified_contracts_module():
    """The tested hash must cover every CP5-A execution-affecting source file."""
    from thesis_deck_system.phase3_cp5a_scientific_svg import candidate_state

    state = candidate_state(ROOT)
    assert "cp5a:source:contracts" in state["component_hashes"]
    assert "cp5a:test:scientific-svg" in state["component_hashes"]
    assert "cp5a:privacy:approved-scanner" in state["component_hashes"]
    assert "cp5a:privacy:scanner" in state["component_hashes"]


def test_synthetic_corpus_exercises_ten_declared_language_families_and_every_fixture_validates():
    import json
    from thesis_deck_system.phase3_cp5a_scientific_svg import validate_synthetic_corpus

    corpus = json.loads((ARTIFACTS / "scientific-svg-synthetic-corpus.json").read_text(encoding="utf-8"))
    result = validate_synthetic_corpus(ROOT, corpus)
    assert result["aggregate_status"] == "pass"
    assert result["fixture_count"] == 10
    assert {item["fixture_id"] for item in result["fixtures"]} == {item["fixture_id"] for item in corpus["fixtures"]}


@pytest.mark.parametrize(
    ("svg", "expected_rule"),
    [
        ("<!DOCTYPE svg><svg xmlns='http://www.w3.org/2000/svg'/>", "CP5A-FORBIDDEN-EXECUTABLE"),
        (_svg("<image id='obj-image' data-semantic-role='image' href='\\\\server\\private.png'/>",), "CP5A-RESOURCE-POLICY"),
        (_svg("<image id='obj-image' data-semantic-role='image' href='/mnt/d/private.png'/>",), "CP5A-RESOURCE-POLICY"),
        (_svg("<rect id='obj-panel' data-semantic-role='panel' x='0' y='0' width='Infinity' height='1'/>",), "CP5A-NUMERIC-POLICY"),
        (_svg("<path id='obj-branch' data-semantic-role='branch' d='M 0 0 L 1' fill='none'/>",), "CP5A-PATH-GRAMMAR"),
        (_svg("<text id='obj-title' data-semantic-role='title' x='1' y='1'>水凝膠</text><path id='obj-replaced' data-semantic-role='title' d='M 0 0'/>",), "CP5A-ROLE-ELEMENT-COMPATIBILITY"),
        (_svg("<style>rect{fill:red}</style>",), "CP5A-FORBIDDEN-EXECUTABLE"),
        (_svg("<filter id='obj-filter' data-semantic-role='group'/>",), "CP5A-FORBIDDEN-EXECUTABLE"),
        (_svg("<image id='obj-image' data-semantic-role='image' href='assets/private-source.pptx'/>",), "CP5A-PRIVATE-LEAKAGE"),
    ],
)
def test_additional_security_and_language_mutations_fail_closed(svg: str, expected_rule: str):
    result = _validator().validate(svg, figure_spec=_spec())
    assert result["aggregate_status"] == "fail"
    assert expected_rule in {finding["rule_id"] for finding in result["findings"]}


def test_authoring_handoff_cannot_bypass_the_static_validator():
    from thesis_deck_system.phase3_cp5a_scientific_svg import ScientificSvgError, author_svg_for_spec

    with pytest.raises(ScientificSvgError):
        author_svg_for_spec(_svg("<script id='obj-x' data-semantic-role='node'>x</script>"), _spec(), ROOT)
    result = author_svg_for_spec(_valid_svg(), _spec(), ROOT)
    assert result["qa"]["aggregate_status"] == "pass"
