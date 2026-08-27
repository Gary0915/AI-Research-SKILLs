from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]


def _module(name: str):
    try:
        return importlib.import_module(f"thesis_deck_system.{name}")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Phase 2 module is missing: {exc}")


def test_private_alias_resolution_is_explicit_and_never_synthetic_fallback(tmp_path: Path):
    private = _module("private_fixtures")
    fixture = tmp_path / "template.pptx"
    fixture.write_bytes(b"private-test-fixture")
    locator = private.PrivateFixtureLocator(explicit={"template_primary_1": fixture})
    record = locator.resolve("template_primary_1")
    assert record.path == fixture
    assert record.sha256 == hashlib.sha256(fixture.read_bytes()).hexdigest()
    assert record.alias_uri == "private://template_primary_1"
    with pytest.raises(private.BlockedFixtureError, match="layout_exemplar_2"):
        locator.resolve("layout_exemplar_2")


def test_project_context_does_not_depend_on_template_parent_depth(tmp_path: Path):
    context = _module("context")
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    ctx = context.ProjectContext(repo_root=ROOT)
    expected = ROOT / "thesis-deck-system" / "schemas"
    assert ctx.resolve_repo_path("thesis-deck-system/schemas") == expected
    assert ctx.canonical_path(expected) == "thesis-deck-system/schemas"


def test_fishbone_revisions_are_immutable_and_focus_is_visible(tmp_path: Path):
    fishbone = _module("fishbone")
    rev1 = {
        "fishbone_id": "FB001", "revision": 1,
        "branches": [
            {"branch_id": "FB-MATERIAL", "label": "材料", "parent_ref": None, "status": "completed"},
            {"branch_id": "FB-MATERIAL-HYDRATION", "label": "含水梯度", "parent_ref": "FB-MATERIAL", "status": "current"},
            {"branch_id": "FB-ELECTRODE", "label": "電極", "parent_ref": None, "status": "future"},
        ],
    }
    rev2 = {
        "fishbone_id": "FB001", "revision": 2, "supersedes_revision": 1,
        "branches": rev1["branches"] + [{"branch_id": "FB-ELECTRODE-CONTACT", "label": "接觸", "parent_ref": "FB-ELECTRODE", "status": "current"}],
    }
    before = json.dumps(rev1, sort_keys=True, ensure_ascii=False)
    first_svg = fishbone.render_fishbone_svg(rev1, ["FB-MATERIAL-HYDRATION"], "H01", tmp_path / "rev1.svg")
    second_svg = fishbone.render_fishbone_svg(rev2, ["FB-ELECTRODE-CONTACT"], "H02", tmp_path / "rev2.svg")
    assert json.dumps(rev1, sort_keys=True, ensure_ascii=False) == before
    assert "FB-MATERIAL-HYDRATION" in first_svg.read_text(encoding="utf-8")
    assert "FB-ELECTRODE-CONTACT" not in first_svg.read_text(encoding="utf-8")
    assert "FB-ELECTRODE-CONTACT" in second_svg.read_text(encoding="utf-8")
    assert "CURRENT / H02" in second_svg.read_text(encoding="utf-8")


def test_fishbone_rejects_unknown_focus_branch(tmp_path: Path):
    fishbone = _module("fishbone")
    revision = {"fishbone_id": "FB001", "revision": 1, "branches": [{"branch_id": "FB-MATERIAL", "label": "材料", "parent_ref": None, "status": "future"}]}
    with pytest.raises(ValueError, match="focus branch"):
        fishbone.render_fishbone_svg(revision, ["FB-NOT-THERE"], "H01", tmp_path / "bad.svg")
