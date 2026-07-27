import json

import pytest
from paper_digger.experiment import (
    VALID_STATUSES,
    record_run,
    record_verification,
    set_experiment_status,
    start_run,
)
from paper_digger.plan import confirm_plan
from paper_digger.workspace import scaffold


def _state():
    return {
        "experiments": [
            {"id": "a", "mode": "dry", "is_min_validation": True, "status": "planned"},
            {"id": "b", "mode": "dry", "is_min_validation": False, "status": "planned"},
        ]
    }


def test_valid_statuses():
    assert VALID_STATUSES == (
        "planned",
        "running",
        "awaiting_verification",
        "verified",
        "refuted",
    )


def test_set_status_updates_only_target_and_is_immutable():
    s = _state()
    new = set_experiment_status(s, "a", "running")
    assert next(e for e in new["experiments"] if e["id"] == "a")["status"] == "running"
    assert next(e for e in new["experiments"] if e["id"] == "b")["status"] == "planned"
    assert s["experiments"][0]["status"] == "planned"


def test_set_status_invalid_status_raises():
    with pytest.raises(ValueError):
        set_experiment_status(_state(), "a", "bogus")


def test_set_status_unknown_id_raises():
    with pytest.raises(ValueError):
        set_experiment_status(_state(), "ghost", "running")


def _seed(ws):
    exps = [
        {
            "id": "mvp",
            "question": "core?",
            "mode": "dry",
            "success_criteria": "acc>0.8",
            "deps": [],
            "is_min_validation": True,
        },
        {
            "id": "full",
            "question": "scale?",
            "mode": "dry",
            "success_criteria": "beats baseline",
            "deps": ["mvp"],
            "is_min_validation": False,
        },
    ]
    confirm_plan(ws, exps, now="t0")


def _status(state, exp_id):
    return next(e for e in state["experiments"] if e["id"] == exp_id)["status"]


def test_start_run_sets_running_and_creates_dir(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    _seed(ws)
    state = start_run(ws, "mvp", now="t1")
    assert _status(state, "mvp") == "running"
    assert (ws / "05_experiments" / "runs" / "mvp").is_dir()


def test_record_run_writes_result_and_evidence_bank(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    _seed(ws)
    start_run(ws, "mvp", now="t1")
    state = record_run(
        ws,
        "mvp",
        {
            "command": "python train.py",
            "metrics": {"acc": 0.83},
            "success": True,
            "notes": "ok",
        },
        now="t2",
    )
    assert _status(state, "mvp") == "awaiting_verification"
    assert (ws / "05_experiments" / "runs" / "mvp" / "result.md").exists()
    bank = (ws / "05_experiments" / "evidence_bank.md").read_text(encoding="utf-8")
    assert "mvp" in bank and "0.83" in bank


def test_record_run_keeps_large_metrics_out_of_context_files(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    _seed(ws)
    start_run(ws, "mvp", now="t1")
    record_run(
        ws,
        "mvp",
        {
            "command": "python train.py",
            "metrics": {"loss_curve": list(range(1000)), "acc": 0.83},
            "success": True,
            "notes": "ok",
        },
        now="t2",
    )

    run_dir = ws / "05_experiments" / "runs" / "mvp"
    raw_metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    assert raw_metrics["loss_curve"][-1] == 999

    result = (run_dir / "result.md").read_text(encoding="utf-8")
    bank = (ws / "05_experiments" / "evidence_bank.md").read_text(encoding="utf-8")
    assert '"items": 1000' in result
    assert '"items": 1000' in bank
    assert "metrics_sha256" in result
    assert "metrics_sha256" in bank
    assert len(result) < 1500
    assert len(bank) < 1000


def test_record_verification_verified(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    _seed(ws)
    start_run(ws, "mvp")
    record_run(ws, "mvp", {"command": "c", "metrics": {}, "success": True})
    state = record_verification(
        ws, "mvp", {"verified": True, "reason": "reproduced"}, now="t3"
    )
    assert _status(state, "mvp") == "verified"
    assert (ws / "05_experiments" / "runs" / "mvp" / "verification.md").exists()


def test_record_verification_refuted(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    _seed(ws)
    start_run(ws, "mvp")
    record_run(ws, "mvp", {"command": "c", "metrics": {}, "success": True})
    state = record_verification(ws, "mvp", {"verified": False, "reason": "data leak"})
    assert _status(state, "mvp") == "refuted"
