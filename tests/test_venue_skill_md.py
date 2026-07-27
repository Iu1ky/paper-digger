from pathlib import Path

SKILL = (
    Path(__file__).parent.parent
    / "plugins"
    / "paper-digger"
    / "skills"
    / "paper-digger-venue"
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
    assert fm.get("name") == "paper-digger-venue"
    desc = fm.get("description", "")
    assert desc.startswith("Use when")
    assert len(desc) <= 1024


def test_body_covers_fit_template_and_confirm():
    body = SKILL.read_text(encoding="utf-8")
    assert "confirm_venue" in body
    assert "模版" in body
    assert "checkpoint" in body.lower()
    assert "scope" in body.lower()
