"""The machine-readable ``state.json`` model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATE_FILENAME = "state.json"
EFFORT_MODES = ("lean", "standard", "deep")


def default_state(
    project: str,
    workspace: str,
    field_: str = "",
    now: str | None = None,
    effort: str = "standard",
) -> dict[str, Any]:
    """Return a fresh state dict. `now` is an ISO timestamp injected by the caller."""
    if effort not in EFFORT_MODES:
        raise ValueError(f"invalid effort {effort!r} (valid: {EFFORT_MODES})")
    state: dict[str, Any] = {
        "project": project,
        "workspace": workspace,
        "field": field_,
        "phase": 0,
        "status": "in_progress",
        "effort": effort,
        "decisions": {},
        "venue": {},
        "experiments": [],
        "evaluations": [],
        "loops": {"review": 0},
        "checkpoints": [],
        "capabilities": {},
        "delegated": {},
    }
    if now is not None:
        state["created"] = now
    return state


def load_state(workspace: str | Path) -> dict[str, Any]:
    path = Path(workspace) / STATE_FILENAME
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(
    workspace: str | Path, state: dict[str, Any], now: str | None = None
) -> None:
    """Write state to disk. Does NOT mutate `state`; writes a copy with `updated` set."""
    to_write = dict(state)
    if now is not None:
        to_write["updated"] = now
    path = Path(workspace) / STATE_FILENAME
    path.write_text(
        json.dumps(to_write, indent=2, ensure_ascii=False), encoding="utf-8"
    )
