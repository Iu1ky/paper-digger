"""End-to-end dry-run: walk the whole pipeline through the deterministic helpers,
asserting the state machine composes coherently from init to finalize."""

from paper_digger.evaluate import record as record_eval
from paper_digger.experiment import record_run, record_verification, start_run
from paper_digger.ideate import confirm_idea
from paper_digger.loop import (
    loop_back_to_experiments,
    needs_more_experiments,
    record_review_round,
)
from paper_digger.orchestrate import (
    advance_phase,
    mark_template_verified,
    template_gate_status,
)
from paper_digger.plan import confirm_plan
from paper_digger.state import load_state
from paper_digger.theory import record_validation, save_derivation
from paper_digger.venue import confirm_venue
from paper_digger.workspace import scaffold


def test_full_pipeline_dry_run(tmp_path):
    ws = scaffold(tmp_path, "e2e", field_="ML", now="t0", env={})

    # Phase 1 — ideate + node ①
    confirm_idea(ws, "idea-A", summary="the idea", now="t1")
    record_eval(
        ws,
        1,
        [
            {
                "lens": "novelty",
                "axis": "A",
                "verdict": "GREEN",
                "must_fix": [],
                "rationale": "",
            }
        ],
        now="t1",
    )
    advance_phase(ws, to_phase=1, now="t1")

    # Phase 2 — venue (official template, not yet verified)
    confirm_venue(
        ws,
        {
            "name": "KBS",
            "type": "journal",
            "template": {
                "available": True,
                "url": "u",
                "format": "latex",
                "verified": False,
            },
        },
        now="t2",
    )
    advance_phase(ws, to_phase=2, now="t2")

    # Phase 3 — literature deep-dive is prompt-driven (delegated to deep-research /
    # paper-spine-research); no deterministic helper to call, so the dry-run skips it.

    # Phase 4 — plan (one minimal-validation experiment)
    confirm_plan(
        ws,
        [
            {
                "id": "mvp",
                "question": "core?",
                "mode": "dry",
                "success_criteria": "acc>0.8",
                "deps": [],
                "is_min_validation": True,
            }
        ],
        now="t4",
    )
    advance_phase(ws, to_phase=4, now="t4")

    # Phase 5a — experiment (min-validation) + node ②
    advance_phase(ws, to_phase=5, now="t5")
    start_run(ws, "mvp", now="t5")
    record_run(
        ws,
        "mvp",
        {
            "command": "python t.py",
            "metrics": {"acc": 0.85},
            "success": True,
            "notes": "ok",
        },
        now="t5",
    )
    record_verification(ws, "mvp", {"verified": True, "reason": "reproduced"}, now="t5")
    record_eval(
        ws,
        2,
        [
            {
                "lens": "forensics",
                "axis": "B",
                "verdict": "GREEN",
                "must_fix": [],
                "rationale": "",
            }
        ],
        now="t5",
    )

    # Phase 5b — theory
    save_derivation(
        ws,
        [{"id": "a1", "statement": "X convex"}],
        [{"id": "s1", "statement": "A", "justification": "j", "status": "proven"}],
    )
    record_validation(
        ws, [{"check": "numeric", "passed": True, "notes": "ok"}], now="t5"
    )

    # Phase 6 — template gate: blocked until verified
    assert template_gate_status(load_state(ws))["ready"] is False
    mark_template_verified(ws, now="t6")
    assert template_gate_status(load_state(ws))["ready"] is True
    advance_phase(ws, to_phase=6, now="t6")

    # Phase 8 → 9 — first review: major revision → loop back to Phase 5
    advance_phase(ws, to_phase=8, now="t8")
    advance_phase(ws, to_phase=9, now="t9")
    st = record_review_round(ws, "major_revision", notes="add an ablation", now="t9")
    assert st["loops"]["review"] == 1
    assert needs_more_experiments("major_revision") is True
    loop_back_to_experiments(ws, now="t9")
    assert load_state(ws)["phase"] == 5

    # Second review round: minor revision → no loop-back → finalize
    advance_phase(ws, to_phase=9, now="t10")
    record_review_round(ws, "minor_revision", now="t10")
    assert needs_more_experiments("minor_revision") is False
    advance_phase(ws, to_phase=10, now="t10")

    final = load_state(ws)
    assert final["phase"] == 10
    assert final["decisions"]["idea"] == "idea-A"
    assert final["decisions"]["venue"] == "KBS"
    assert final["decisions"]["plan_approved"] is True
    assert final["venue"]["template"]["verified"] is True
    assert final["loops"]["review"] == 2
    assert len(final["evaluations"]) == 2
    assert any(
        e["id"] == "mvp" and e["status"] == "verified" for e in final["experiments"]
    )
