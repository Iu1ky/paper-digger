import pytest
from paper_digger.evaluate import (
    AXIS_A,
    AXIS_B,
    NODE_FOCUS,
    VERDICTS,
    aggregate,
    record,
    render_report,
)
from paper_digger.state import load_state
from paper_digger.workspace import scaffold


def _lv(lens, axis, verdict, must_fix=None):
    return {
        "lens": lens,
        "axis": axis,
        "verdict": verdict,
        "must_fix": must_fix or [],
        "rationale": "",
    }


def test_axes_are_disjoint_and_nonempty():
    assert set(AXIS_A).isdisjoint(AXIS_B)
    assert AXIS_A and AXIS_B
    assert VERDICTS == ("GREEN", "YELLOW", "RED")


def test_empty_raises():
    with pytest.raises(ValueError):
        aggregate([])


def test_all_green():
    out = aggregate([_lv("novelty", "A", "GREEN"), _lv("integrity", "B", "GREEN")])
    assert out["verdict"] == "GREEN"
    assert out["must_fix"] == []
    assert out["blocking_integrity"] is False


def test_worst_of_severity():
    out = aggregate(
        [_lv("a", "A", "GREEN"), _lv("b", "A", "YELLOW"), _lv("c", "A", "GREEN")]
    )
    assert out["verdict"] == "YELLOW"


def test_axis_a_red_is_red_but_not_blocking():
    out = aggregate([_lv("value", "A", "RED")])
    assert out["verdict"] == "RED"
    assert out["blocking_integrity"] is False


def test_axis_b_red_sets_blocking_integrity():
    out = aggregate([_lv("fabrication", "B", "RED", ["re-run experiment with seeds"])])
    assert out["verdict"] == "RED"
    assert out["blocking_integrity"] is True
    assert out["must_fix"] == ["re-run experiment with seeds"]


def test_must_fix_unions_non_green_lenses():
    out = aggregate(
        [
            _lv("a", "A", "YELLOW", ["fix logic gap"]),
            _lv("b", "B", "RED", ["verify citation X"]),
            _lv("c", "A", "GREEN", ["ignored because green"]),
        ]
    )
    assert out["must_fix"] == ["fix logic gap", "verify citation X"]


def test_invalid_verdict_raises():
    with pytest.raises(ValueError):
        aggregate([_lv("a", "A", "MAYBE")])


def test_node_focus_has_four_nodes_and_full_node4():
    assert set(NODE_FOCUS) == {1, 2, 3, 4}
    assert tuple(NODE_FOCUS[4]) == AXIS_A + AXIS_B  # node 4 = full audit
    valid = set(AXIS_A) | set(AXIS_B)
    for dims in NODE_FOCUS.values():
        assert set(dims) <= valid


def test_render_report_contains_verdict_table_and_mustfix():
    lenses = [
        {
            "lens": "novelty-skeptic",
            "axis": "A",
            "verdict": "YELLOW",
            "must_fix": [],
            "rationale": "incremental",
        },
        {
            "lens": "integrity-forensics",
            "axis": "B",
            "verdict": "GREEN",
            "must_fix": [],
            "rationale": "ok",
        },
    ]
    summary = {
        "verdict": "YELLOW",
        "must_fix": ["sharpen the novelty claim"],
        "blocking_integrity": False,
    }
    out = render_report(2, lenses, summary)
    assert "评价节点 2" in out
    assert "YELLOW" in out
    assert "novelty-skeptic" in out
    assert "sharpen the novelty claim" in out


def test_render_report_empty_mustfix_shows_none():
    summary = {"verdict": "GREEN", "must_fix": [], "blocking_integrity": False}
    out = render_report(
        1, [{"lens": "x", "axis": "A", "verdict": "GREEN", "rationale": ""}], summary
    )
    assert "(none)" in out


def test_record_writes_report_and_appends_state(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    lenses = [
        {
            "lens": "fabrication",
            "axis": "B",
            "verdict": "RED",
            "must_fix": ["re-run with seeds"],
            "rationale": "no logs",
        },
    ]
    summary = record(ws, 2, lenses, now="2026-06-03T00:00:00Z")

    assert summary["verdict"] == "RED"
    assert summary["blocking_integrity"] is True

    report = ws / "08_evaluation" / "eval_node2.md"
    assert report.exists()
    assert "评价节点 2" in report.read_text(encoding="utf-8")

    state = load_state(ws)
    assert len(state["evaluations"]) == 1
    entry = state["evaluations"][0]
    assert entry["node"] == 2
    assert entry["verdict"] == "RED"
    assert entry["blocking_integrity"] is True
    assert entry["at"] == "2026-06-03T00:00:00Z"


def test_record_does_not_clobber_prior_evaluations(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    record(
        ws,
        1,
        [{"lens": "v", "axis": "A", "verdict": "GREEN", "rationale": ""}],
        now="t1",
    )
    record(
        ws,
        2,
        [
            {
                "lens": "v",
                "axis": "A",
                "verdict": "YELLOW",
                "must_fix": ["x"],
                "rationale": "",
            }
        ],
        now="t2",
    )
    state = load_state(ws)
    assert [e["node"] for e in state["evaluations"]] == [1, 2]
