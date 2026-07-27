from pathlib import Path

SKILL = (
    Path(__file__).parent.parent
    / "plugins"
    / "paper-digger"
    / "skills"
    / "paper-digger-evaluate"
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
    assert fm.get("name") == "paper-digger-evaluate"
    desc = fm.get("description", "")
    assert desc.startswith("Use when")
    assert len(desc) <= 1024


def test_body_covers_axes_nodes_and_verdict():
    body = SKILL.read_text(encoding="utf-8")
    assert "Axis A" in body and "Axis B" in body
    for token in ["伪造", "方法虚构", "引用幻觉", "思维固定"]:
        assert token in body
    assert "节点" in body
    assert "GREEN" in body and "YELLOW" in body and "RED" in body
    assert "evaluate.record" in body or "paper_digger.evaluate" in body
