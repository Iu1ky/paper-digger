"""Phase-5a experiment execution: state machine, run lifecycle, and evidence bank.

The actual 3-mode execution (dry = run code via parallel subagents, wet = protocols,
theory = defer) is prompt-driven per skills/paper-digger-experiment/SKILL.md. This
module owns the deterministic state: experiment status transitions, run-dir
scaffolding, the evidence bank, and verification records.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .state import load_state, save_state

VALID_STATUSES = ("planned", "running", "awaiting_verification", "verified", "refuted")
_EXPERIMENTS_DIR = "05_experiments"
_MAX_METRIC_KEYS = 12
_MAX_METRIC_STRING = 160


def _summarize_metric(value: Any, depth: int = 0) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return (
            value
            if len(value) <= _MAX_METRIC_STRING
            else f"{value[: _MAX_METRIC_STRING - 1]}…"
        )
    if isinstance(value, dict):
        if depth >= 2:
            return {"type": "object", "keys": len(value)}
        items = list(value.items())
        summary = {
            str(key): _summarize_metric(item, depth + 1)
            for key, item in items[:_MAX_METRIC_KEYS]
        }
        if len(items) > _MAX_METRIC_KEYS:
            summary["_omitted_keys"] = len(items) - _MAX_METRIC_KEYS
        return summary
    if isinstance(value, (list, tuple)):
        if len(value) <= 6 and all(
            item is None or isinstance(item, (bool, int, float, str)) for item in value
        ):
            return [_summarize_metric(item, depth + 1) for item in value]
        return {"type": "list", "items": len(value)}
    return _summarize_metric(str(value), depth)


def set_experiment_status(
    state: dict[str, Any], exp_id: str, status: str
) -> dict[str, Any]:
    """Return a new state with experiment `exp_id`'s status set. Immutable; validates.

    Raises ValueError on an invalid status or an unknown experiment id.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r} (valid: {VALID_STATUSES})")
    experiments = state.get("experiments", [])
    if not any(e.get("id") == exp_id for e in experiments):
        raise ValueError(f"unknown experiment id {exp_id!r}")
    new_experiments = [
        {**e, "status": status} if e.get("id") == exp_id else e for e in experiments
    ]
    return {**state, "experiments": new_experiments}


def _run_dir(workspace: str | Path, exp_id: str) -> Path:
    """Return (creating if needed) the run dir `05_experiments/runs/<exp_id>/`."""
    run_dir = Path(workspace) / _EXPERIMENTS_DIR / "runs" / exp_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def start_run(
    workspace: str | Path, exp_id: str, now: str | None = None
) -> dict[str, Any]:
    """Mark experiment `exp_id` running and create its run dir. Returns new state."""
    ws = Path(workspace)
    _run_dir(ws, exp_id)
    new_state = set_experiment_status(load_state(ws), exp_id, "running")
    save_state(ws, new_state, now=now)
    return new_state


def record_run(
    workspace: str | Path,
    exp_id: str,
    result: dict[str, Any],
    now: str | None = None,
) -> dict[str, Any]:
    """Record a run result (→ `result.md` + append `evidence_bank.md`); status → awaiting_verification.

    `result` = {command, metrics, success, notes}. Returns new state.
    """
    ws = Path(workspace)
    run_dir = _run_dir(ws, exp_id)
    success = bool(result.get("success"))
    command = str(result.get("command", "")).replace("\n", " ")
    metrics = result.get("metrics", {})
    raw_metrics = json.dumps(
        metrics, ensure_ascii=False, indent=2, sort_keys=True
    ).encode("utf-8")
    metrics_path = run_dir / "metrics.json"
    metrics_path.write_bytes(raw_metrics + b"\n")
    metrics_sha256 = hashlib.sha256(raw_metrics + b"\n").hexdigest()
    metrics_summary = _summarize_metric(metrics)
    metrics_json = json.dumps(metrics_summary, ensure_ascii=False, sort_keys=True)
    notes = str(result.get("notes", ""))
    run_dir.joinpath("result.md").write_text(
        (
            f"# Run: {exp_id}\n\n"
            f"- success: {success}\n"
            f"- command: `{command}`\n"
            f"- metrics_summary: {metrics_json}\n"
            "- metrics_artifact: `metrics.json`\n"
            f"- metrics_sha256: `{metrics_sha256}`\n\n"
            f"{notes}\n"
        ),
        encoding="utf-8",
    )
    # Append-mode so concurrent record_run() calls (parallel subagents) don't clobber.
    bank = ws / _EXPERIMENTS_DIR / "evidence_bank.md"
    if not bank.exists():
        bank.write_text("# Evidence bank\n\n", encoding="utf-8")
    entry = (
        f"- {exp_id}: success={success} metrics={metrics_json} "
        f"metrics_artifact=`runs/{exp_id}/metrics.json` "
        f"metrics_sha256=`{metrics_sha256}`"
    ) + (f" @ {now}" if now else "")
    with bank.open("a", encoding="utf-8") as bank_file:
        bank_file.write(f"{entry}\n")
    new_state = set_experiment_status(load_state(ws), exp_id, "awaiting_verification")
    save_state(ws, new_state, now=now)
    return new_state


def record_verification(
    workspace: str | Path,
    exp_id: str,
    verdict: dict[str, Any],
    now: str | None = None,
) -> dict[str, Any]:
    """Record an adversarial verification verdict; status → verified | refuted.

    `verdict` = {verified: bool, reason: str}. Returns new state.
    """
    ws = Path(workspace)
    run_dir = _run_dir(ws, exp_id)
    verified = bool(verdict.get("verified"))
    reason = str(verdict.get("reason", "")).replace("\n", " ")
    run_dir.joinpath("verification.md").write_text(
        f"# Verification: {exp_id}\n\n- verified: {verified}\n- reason: {reason}\n",
        encoding="utf-8",
    )
    status = "verified" if verified else "refuted"
    new_state = set_experiment_status(load_state(ws), exp_id, status)
    save_state(ws, new_state, now=now)
    return new_state
