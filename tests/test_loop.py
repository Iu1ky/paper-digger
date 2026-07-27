import pytest
from paper_digger.loop import (
    REVIEW_DECISIONS,
    loop_back_to_experiments,
    needs_more_experiments,
    record_review_round,
)
from paper_digger.state import load_state
from paper_digger.workspace import scaffold


def test_review_decisions():
    assert REVIEW_DECISIONS == ("accept", "minor_revision", "major_revision", "reject")


def test_record_review_round_increments_and_writes(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    state = record_review_round(ws, "major_revision", notes="add an ablation", now="t1")
    assert state["loops"]["review"] == 1
    rec = ws / "07_reviews" / "review_round_1.md"
    assert rec.exists()
    assert "major_revision" in rec.read_text(encoding="utf-8")
    state2 = record_review_round(ws, "minor_revision", now="t2")
    assert state2["loops"]["review"] == 2
    assert (ws / "07_reviews" / "review_round_2.md").exists()
    assert load_state(ws)["loops"]["review"] == 2


def test_record_review_round_rejects_invalid_decision(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    with pytest.raises(ValueError):
        record_review_round(ws, "looks_good")


def test_needs_more_experiments():
    assert needs_more_experiments("major_revision") is True
    assert needs_more_experiments("minor_revision") is False
    assert needs_more_experiments("accept") is False
    assert (
        needs_more_experiments("reject") is False
    )  # reject → human checkpoint, not auto-loopback
    with pytest.raises(ValueError):
        needs_more_experiments("bogus")


def test_loop_back_to_experiments_sets_phase_5(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    state = loop_back_to_experiments(ws, now="t1")
    assert state["phase"] == 5
    assert load_state(ws)["phase"] == 5
