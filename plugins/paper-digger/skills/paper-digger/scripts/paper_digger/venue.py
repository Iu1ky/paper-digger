"""Phase-2 venue selection helpers: fit scoring, ranking, and confirmation.

Venue analysis itself is prompt-driven (WebSearch/WebFetch of CFPs and author
guidelines per skills/paper-digger-venue/SKILL.md). This module scores/ranks
candidate venues and persists the confirmed venue + its official-template info
into the workspace + state.json.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import load_state, save_state

# Venue-fit criteria weights (sum to 1.0). Scope dominates. All higher = better.
FIT_WEIGHTS = {"scope": 0.40, "tier": 0.25, "timeline": 0.20, "readiness": 0.15}
_SCORE_MIN = 0.0
_SCORE_MAX = 5.0


def score_venue_fit(scores: dict[str, float]) -> float:
    """Weighted venue-fit score. `scores` maps scope/tier/timeline/readiness → [0, 5]."""
    missing = set(FIT_WEIGHTS) - set(scores)
    if missing:
        raise ValueError(f"missing fit criteria: {sorted(missing)}")
    total = 0.0
    for key, weight in FIT_WEIGHTS.items():
        value = scores[key]
        if not (_SCORE_MIN <= value <= _SCORE_MAX):
            raise ValueError(f"{key} score {value} out of range [0, 5]")
        total += value * weight
    return round(total, 3)


def rank_venues(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return candidates sorted by fit (desc), each with an added `fit` field.

    Does not mutate the input candidates. Stable for ties (preserves input order).
    """
    scored = [{**cand, "fit": score_venue_fit(cand["scores"])} for cand in candidates]
    return sorted(scored, key=lambda c: c["fit"], reverse=True)


def save_venue_analysis(
    workspace: str | Path, candidates: list[dict[str, Any]]
) -> Path:
    """Rank `candidates` by fit and write `02_venue/venue_analysis.md`; return its path."""
    ws = Path(workspace)
    ranked = rank_venues(candidates)
    lines = [
        "# Venue analysis (ranked by fit)",
        "",
        "| rank | venue | fit | template? | deadline |",
        "|---|---|---|---|---|",
    ]
    for i, cand in enumerate(ranked, start=1):
        name = str(cand.get("name", "")).replace("|", "\\|").replace("\n", " ")
        has_template = "yes" if cand.get("template", {}).get("available") else "no"
        deadline = str(cand.get("deadline", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i} | {name} | {cand['fit']} | {has_template} | {deadline} |")
    lines.append("")
    out_dir = ws / "02_venue"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "venue_analysis.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def confirm_venue(
    workspace: str | Path,
    venue: dict[str, Any],
    now: str | None = None,
) -> dict[str, Any]:
    """Write `02_venue/confirmed_venue.md` and persist the venue + template into state.

    `venue` must have a `name`; its `template` (default `{"available": False}`) is
    stored at `state.venue.template` for the Phase-6 template gate. Also sets
    `state.decisions.venue`. Returns the new state; does not mutate the loaded state.
    """
    if "name" not in venue:
        raise ValueError("venue must have a 'name'")
    template = dict(
        venue.get("template", {"available": False})
    )  # copy: don't alias caller's dict
    new_venue: dict[str, Any] = {"name": venue["name"], "template": template}
    if "type" in venue:
        new_venue["type"] = venue["type"]

    ws = Path(workspace)
    out_dir = ws / "02_venue"
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Confirmed venue: {venue['name']}",
        "",
        f"- type: {venue.get('type', '')}",
        f"- template available: {template.get('available', False)}",
        f"- template url: {template.get('url', '')}",
        f"- template format: {template.get('format', '')}",
        "",
    ]
    (out_dir / "confirmed_venue.md").write_text("\n".join(lines), encoding="utf-8")

    state = load_state(ws)
    new_decisions = {**state.get("decisions", {}), "venue": venue["name"]}
    new_state = {**state, "venue": new_venue, "decisions": new_decisions}
    save_state(ws, new_state, now=now)
    return new_state
