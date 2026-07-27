"""Phase-9 revision loop: review tracking and loop-back-to-experiments.

Delegation (academic-paper-reviewer / ars-revision / paper-spine-rewrite) is
prompt-driven per the orchestrator SKILL.md. This module owns the deterministic
loop state: the review-round counter, review records in 07_reviews/, and the
decision of whether a review verdict sends the project back to Phase 5.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .orchestrate import advance_phase
from .state import load_state, save_state

REVIEW_DECISIONS = ("accept", "minor_revision", "major_revision", "reject")
_REVIEWS_DIR = "07_reviews"
# Decisions that require returning to Phase 5 (more experiments) before re-review.
_LOOPBACK_DECISIONS = ("major_revision",)


def record_review_round(
    workspace: str | Path,
    decision: str,
    notes: str = "",
    now: str | None = None,
) -> dict[str, Any]:
    """Record one simulated-review round: increment `state.loops.review` and write
    `07_reviews/review_round_<n>.md`. Returns the new state. Does not mutate the loaded state.
    """
    if decision not in REVIEW_DECISIONS:
        raise ValueError(
            f"invalid review decision {decision!r} (valid: {REVIEW_DECISIONS})"
        )
    ws = Path(workspace)
    state = load_state(ws)
    loops = {**state.get("loops", {})}
    loops["review"] = loops.get("review", 0) + 1
    round_n = loops["review"]
    new_state = {**state, "loops": loops}

    out_dir = ws / _REVIEWS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_notes = str(notes).replace("\n", " ")
    out_dir.joinpath(f"review_round_{round_n}.md").write_text(
        f"# Review round {round_n}\n\n- decision: {decision}\n- notes: {safe_notes}\n",
        encoding="utf-8",
    )
    save_state(ws, new_state, now=now)
    return new_state


def needs_more_experiments(decision: str) -> bool:
    """Whether a review decision should loop back to Phase 5 for more experiments."""
    if decision not in REVIEW_DECISIONS:
        raise ValueError(
            f"invalid review decision {decision!r} (valid: {REVIEW_DECISIONS})"
        )
    return decision in _LOOPBACK_DECISIONS


def loop_back_to_experiments(
    workspace: str | Path, now: str | None = None
) -> dict[str, Any]:
    """Send the project back to Phase 5 (experiments) for another round; returns new state."""
    return advance_phase(workspace, to_phase=5, now=now)
