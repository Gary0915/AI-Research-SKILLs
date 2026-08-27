from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]


def test_required_skill_routes_and_handoffs_are_deterministic():
    routing = yaml.safe_load((ROOT / "thesis-deck-system/skill-routing.yaml").read_text(encoding="utf-8"))
    required = {"thesis-deck-router", "scientific-method-planner", "hypothesis-layer-planner", "master-deck-ledger", "fishbone-director", "layout-director", "professor-qa"}
    assert {item for item in required if (ROOT / "thesis-deck-system/skills" / item / "SKILL.md").is_file()} == required
    routes = routing["routes"]
    assert routes["更新這週 Group Meeting"]["top_level"] == "thesis-deck-router"
    assert routes["審核這份簡報"]["handoff"] == ["professor-qa"]
    for route in routes.values():
        assert route["top_level"] == "thesis-deck-router"
        assert route["handoff"]
        assert route["handoff"][-1] == "professor-qa"
