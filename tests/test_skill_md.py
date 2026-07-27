from pathlib import Path

SKILL = (
    Path(__file__).parent.parent
    / "plugins"
    / "paper-digger"
    / "skills"
    / "paper-digger"
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


def test_frontmatter_has_name_and_trigger_description():
    fm = _frontmatter(SKILL.read_text(encoding="utf-8"))
    assert fm.get("name") == "paper-digger"
    desc = fm.get("description", "")
    assert desc.startswith(
        "Use when"
    ), "description must be trigger-only, starting with 'Use when'"
    assert len(desc) <= 1024
    assert "resume" in desc.lower()
    for phase_specific_trigger in (
        "idea发掘",
        "选题",
        "选刊",
        "实验编排",
        "理论推导",
    ):
        assert phase_specific_trigger not in desc


def test_body_references_portable_pd_init_and_roadmap():
    body = SKILL.read_text(encoding="utf-8")
    assert "scripts/pd.py init" in body
    assert "ROADMAP.md" in body
    assert "checkpoint" in body.lower()


def test_body_has_dispatch_table_and_template_gate():
    body = SKILL.read_text(encoding="utf-8")
    assert "scripts/pd.py advance" in body
    assert "scripts/pd.py gate" in body
    assert "模版闸门" in body
    assert "references/delegation.md" in body
    assert "不要求" in body


def test_body_has_revision_loop_section():
    body = SKILL.read_text(encoding="utf-8")
    assert "record_review_round" in body
    assert "loop_back_to_experiments" in body
    assert "修改循环" in body


def test_body_has_context_and_effort_budget_rules():
    body = SKILL.read_text(encoding="utf-8")
    assert "lean" in body and "standard" in body and "deep" in body
    assert "--full" in body
    assert "递归" in body
