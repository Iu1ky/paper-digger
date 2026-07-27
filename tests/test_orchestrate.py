import pytest
from paper_digger.orchestrate import (
    advance_phase,
    mark_template_verified,
    template_gate_status,
)
from paper_digger.state import load_state
from paper_digger.venue import confirm_venue
from paper_digger.workspace import scaffold


def test_advance_phase_increments_and_updates_roadmap(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    state = advance_phase(ws, now="t1")
    assert state["phase"] == 1
    assert load_state(ws)["phase"] == 1
    roadmap = (ws / "ROADMAP.md").read_text(encoding="utf-8")
    phase1_line = next(ln for ln in roadmap.splitlines() if "方向" in ln)
    assert "▶" in phase1_line


def test_advance_phase_to_explicit_target(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    assert advance_phase(ws, to_phase=5, now="t1")["phase"] == 5


def test_advance_phase_out_of_range_raises(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    with pytest.raises(ValueError):
        advance_phase(ws, to_phase=99)


def test_advance_phase_appends_log(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    advance_phase(ws, now="t1")
    assert "phase 0 → 1" in (ws / "log.md").read_text(encoding="utf-8")


def test_template_gate_no_template_is_ready():
    status = template_gate_status({"venue": {"template": {"available": False}}})
    assert status["ready"] is True


def test_template_gate_unverified_is_blocked():
    status = template_gate_status(
        {"venue": {"template": {"available": True, "verified": False}}}
    )
    assert status["ready"] is False


def test_template_gate_verified_is_ready():
    status = template_gate_status(
        {"venue": {"template": {"available": True, "verified": True}}}
    )
    assert status["ready"] is True


def test_mark_template_verified_sets_flag_and_creates_dir(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    confirm_venue(
        ws,
        {
            "name": "KBS",
            "template": {
                "available": True,
                "url": "u",
                "format": "latex",
                "verified": False,
            },
        },
        now="t1",
    )
    state = mark_template_verified(ws, now="t2")
    assert state["venue"]["template"]["verified"] is True
    assert (ws / "06_manuscript" / "template").is_dir()
    assert load_state(ws)["venue"]["template"]["verified"] is True
