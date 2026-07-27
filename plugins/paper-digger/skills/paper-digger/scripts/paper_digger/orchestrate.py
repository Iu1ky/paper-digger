"""Orchestration glue: phase advancement + the Phase-6 template gate.

Per-phase delegation is prompt-driven by the portable paper-digger skill.
This module owns the
deterministic state transitions the orchestrator relies on.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .roadmap import PHASES
from .roadmap import render as render_roadmap
from .state import load_state, save_state

_MAX_PHASE = max(phase["id"] for phase in PHASES)


def advance_phase(
    workspace: str | Path,
    to_phase: int | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Advance `state.phase` (to the next phase, or to `to_phase`); re-render ROADMAP; log.

    Returns the new state. Does not mutate the loaded state. Raises ValueError if the
    target is outside [0, _MAX_PHASE].
    """
    ws = Path(workspace)
    state = load_state(ws)
    current = state.get("phase", 0)
    target = current + 1 if to_phase is None else to_phase
    if not (0 <= target <= _MAX_PHASE):
        raise ValueError(f"phase {target} out of range [0, {_MAX_PHASE}]")
    new_state = {**state, "phase": target}
    save_state(ws, new_state, now=now)
    (ws / "ROADMAP.md").write_text(render_roadmap(new_state), encoding="utf-8")

    log = ws / "log.md"
    entry = f"- phase {current} → {target}" + (f" @ {now}" if now else "")
    existing = log.read_text(encoding="utf-8") if log.exists() else "# Log\n\n"
    log.write_text(f"{existing}{entry}\n", encoding="utf-8")
    return new_state


def template_gate_status(state: dict[str, Any]) -> dict[str, Any]:
    """Whether Phase-6 drafting may begin, derived from `state.venue.template`.

    Ready when there is no official template (use venue guidelines) OR the official
    template has been acquired and verified. Otherwise blocked.
    """
    template = state.get("venue", {}).get("template", {})
    if not template.get("available", False):
        return {
            "ready": True,
            "reason": "no official template; use venue formatting guidelines",
        }
    if template.get("verified", False):
        return {"ready": True, "reason": "official template acquired and verified"}
    return {
        "ready": False,
        "reason": "official template exists but is not yet fetched/verified",
    }


def mark_template_verified(
    workspace: str | Path, now: str | None = None
) -> dict[str, Any]:
    """Set `state.venue.template.verified = True` and create `06_manuscript/template/`.

    Returns the new state. Does not mutate the loaded state.
    """
    ws = Path(workspace)
    state = load_state(ws)
    venue = state.get("venue", {})
    new_template = {**venue.get("template", {}), "verified": True}
    new_venue = {**venue, "template": new_template}
    new_state = {**state, "venue": new_venue}
    (ws / "06_manuscript" / "template").mkdir(parents=True, exist_ok=True)
    save_state(ws, new_state, now=now)
    return new_state
