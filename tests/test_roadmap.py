from paper_digger.roadmap import PHASES, render


def test_phases_cover_zero_to_ten():
    ids = [p["id"] for p in PHASES]
    assert ids[0] == 0
    assert 10 in ids
    for p in PHASES:
        assert set(p) >= {"id", "name", "skill", "gate"}


def test_render_marks_current_phase():
    out = render({"phase": 2, "project": "demo"})
    assert "# ROADMAP" in out
    assert "demo" in out
    current_line = next(ln for ln in out.splitlines() if "确认目标期刊" in ln)
    assert "▶" in current_line
    idea_line = next(ln for ln in out.splitlines() if "idea 发掘" in ln)
    assert "▶" not in idea_line


def test_render_lists_evaluation_gates():
    out = render({"phase": 0, "project": "demo"})
    assert "评价节点" in out
