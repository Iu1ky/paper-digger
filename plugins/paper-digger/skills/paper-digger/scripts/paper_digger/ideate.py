"""Phase-1 ideation helpers: NFIF scoring, idea-card ranking, and confirmation.

Idea generation itself is prompt-driven (parallel adversarial subagents per
skills/paper-digger-ideate/SKILL.md). This module scores/ranks the resulting
idea cards and persists the confirmed choice into the workspace + state.json.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import load_state, save_state

# NFIF criteria weights (sum to 1.0). Impact and novelty dominate.
NFIF_WEIGHTS = {"novelty": 0.30, "feasibility": 0.20, "impact": 0.35, "fit": 0.15}
_SCORE_MIN = 0.0
_SCORE_MAX = 5.0


def score_idea(scores: dict[str, float]) -> float:
    """Weighted NFIF score. `scores` maps novelty/feasibility/impact/fit → [0, 5]."""
    missing = set(NFIF_WEIGHTS) - set(scores)
    if missing:
        raise ValueError(f"missing NFIF criteria: {sorted(missing)}")
    total = 0.0
    for key, weight in NFIF_WEIGHTS.items():
        value = scores[key]
        if not (_SCORE_MIN <= value <= _SCORE_MAX):
            raise ValueError(f"{key} score {value} out of range [0, 5]")
        total += value * weight
    return round(total, 3)


def rank_ideas(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return cards sorted by NFIF score (desc), each with an added `nfif` field.

    Does not mutate the input cards. Stable for ties (preserves input order).
    """
    scored = [{**card, "nfif": score_idea(card["scores"])} for card in cards]
    return sorted(scored, key=lambda c: c["nfif"], reverse=True)


def save_idea_cards(workspace: str | Path, cards: list[dict[str, Any]]) -> Path:
    """Rank `cards` by NFIF and write `01_ideation/idea_cards.md`; return its path."""
    ws = Path(workspace)
    ranked = rank_ideas(cards)
    lines = [
        "# Idea cards (ranked by NFIF)",
        "",
        "| rank | id | nfif | one-liner |",
        "|---|---|---|---|",
    ]
    for i, card in enumerate(ranked, start=1):
        one_liner = (
            str(card.get("one_liner", "")).replace("|", "\\|").replace("\n", " ")
        )
        lines.append(f"| {i} | {card.get('id', '')} | {card['nfif']} | {one_liner} |")
    lines.append("")
    out_dir = ws / "01_ideation"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "idea_cards.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def confirm_idea(
    workspace: str | Path,
    idea_id: str,
    summary: str = "",
    now: str | None = None,
) -> dict[str, Any]:
    """Write `01_ideation/confirmed_idea.md` and set `state.decisions.idea = idea_id`.

    Returns the new state. Does not mutate the loaded state (builds a new dict).
    """
    ws = Path(workspace)
    out_dir = ws / "01_ideation"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "confirmed_idea.md").write_text(
        f"# Confirmed idea: {idea_id}\n\n{summary}\n", encoding="utf-8"
    )
    state = load_state(ws)
    new_decisions = {**state.get("decisions", {}), "idea": idea_id}
    new_state = {**state, "decisions": new_decisions}
    save_state(ws, new_state, now=now)
    return new_state
