from pathlib import Path

SKILL = (
    Path(__file__).parent.parent
    / "plugins"
    / "paper-digger"
    / "skills"
    / "paper-digger-experiment"
    / "SKILL.md"
)


def _frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = text.index("\n---", 4)
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def test_skill_md_exists():
    assert SKILL.exists()


def test_frontmatter_trigger_description():
    fm = _frontmatter(SKILL.read_text(encoding="utf-8"))
    assert fm.get("name") == "paper-digger-experiment"
    desc = fm.get("description", "")
    assert desc.startswith("Use when")
    assert len(desc) <= 1024


def test_body_covers_modes_nodes_and_helpers():
    body = SKILL.read_text(encoding="utf-8")
    assert "dry" in body and "wet" in body and "theory" in body
    assert "节点②" in body or "node=2" in body
    assert "record_run" in body and "record_verification" in body
    assert "evidence" in body.lower()
    assert "最小验证" in body
