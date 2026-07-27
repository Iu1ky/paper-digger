"""Phase-4 research planning: matrix validation and dependency ordering.

The scientific content (which hypotheses/experiments) is decided prompt-driven per
skills/paper-digger-plan/SKILL.md. This module validates the experiment matrix,
computes a dependency-respecting execution order, persists the plan, and seeds
state.experiments (the hand-off to paper-digger-experiment).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import load_state, save_state

MODES = ("dry", "wet", "theory")
_REQUIRED_FIELDS = ("id", "question", "mode", "success_criteria")


def validate_matrix(experiments: list[dict[str, Any]]) -> None:
    """Validate the experiment matrix; raise ValueError on any problem.

    Rules: non-empty; unique ids; each has id/question/mode/success_criteria;
    mode in MODES; deps reference existing ids; exactly one is_min_validation.
    """
    if not experiments:
        raise ValueError("experiment matrix is empty")
    # Required fields + mode first, so a missing `id` reports as a missing field
    # (not a misleading "duplicate ids" from collected None values).
    for exp in experiments:
        missing = [f for f in _REQUIRED_FIELDS if f not in exp]
        if missing:
            raise ValueError(
                f"experiment {exp.get('id')!r} missing fields: {sorted(missing)}"
            )
        if exp["mode"] not in MODES:
            raise ValueError(
                f"experiment {exp['id']!r} has invalid mode {exp['mode']!r}"
            )
    ids = [exp["id"] for exp in experiments]  # all present after the loop above
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate experiment ids")
    id_set = set(ids)
    for exp in experiments:
        for dep in exp.get("deps", []):
            if dep not in id_set:
                raise ValueError(f"experiment {exp['id']!r} depends on unknown {dep!r}")
    min_count = sum(1 for e in experiments if e.get("is_min_validation"))
    if min_count != 1:
        raise ValueError(
            f"exactly one experiment must be is_min_validation (got {min_count})"
        )


def minimal_validation(experiments: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the single designated minimal-validation (kill-early) experiment."""
    validate_matrix(experiments)
    return next(e for e in experiments if e.get("is_min_validation"))


def dependency_order(experiments: list[dict[str, Any]]) -> list[str]:
    """Return experiment ids in a dependency-respecting order (Kahn's algorithm).

    Ties among ready nodes are broken by input order (deterministic). Raises
    ValueError on a dependency cycle.
    """
    validate_matrix(experiments)
    deps = {e["id"]: list(e.get("deps", [])) for e in experiments}
    order_index = {e["id"]: i for i, e in enumerate(experiments)}
    satisfied: set[str] = set()
    remaining = [e["id"] for e in experiments]
    result: list[str] = []
    while remaining:
        ready = [eid for eid in remaining if all(d in satisfied for d in deps[eid])]
        if not ready:
            raise ValueError("dependency cycle in experiment matrix")
        nxt = min(ready, key=lambda eid: order_index[eid])
        result.append(nxt)
        satisfied.add(nxt)
        remaining.remove(nxt)
    return result


def save_plan(
    workspace: str | Path,
    hypotheses: list[str],
    experiments: list[dict[str, Any]],
) -> Path:
    """Write `04_plan/research_plan.md` (hypotheses + matrix table + exec order); return path."""
    validate_matrix(experiments)
    order = dependency_order(experiments)
    lines = ["# Research plan", "", "## Hypotheses", ""]
    if hypotheses:
        lines.extend(f"- {h}" for h in hypotheses)
    else:
        lines.append("- (none)")
    lines += [
        "",
        "## Experiment matrix",
        "",
        "| id | mode | min? | deps | question |",
        "|---|---|---|---|---|",
    ]
    for exp in experiments:
        min_mark = "✓" if exp.get("is_min_validation") else ""
        deps = ",".join(exp.get("deps", []))
        question = str(exp.get("question", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {exp['id']} | {exp['mode']} | {min_mark} | {deps} | {question} |"
        )
    lines += ["", "## Execution order", "", " → ".join(order), ""]
    out_dir = Path(workspace) / "04_plan"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "research_plan.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def confirm_plan(
    workspace: str | Path,
    experiments: list[dict[str, Any]],
    now: str | None = None,
) -> dict[str, Any]:
    """Seed `state.experiments` (status="planned") and set `state.decisions.plan_approved`.

    Returns the new state. Does not mutate the loaded state.
    """
    validate_matrix(experiments)
    seeded = [
        {
            "id": exp["id"],
            "mode": exp["mode"],
            "is_min_validation": bool(exp.get("is_min_validation")),
            "status": "planned",
        }
        for exp in experiments
    ]
    ws = Path(workspace)
    state = load_state(ws)
    new_decisions = {**state.get("decisions", {}), "plan_approved": True}
    new_state = {**state, "experiments": seeded, "decisions": new_decisions}
    save_state(ws, new_state, now=now)
    return new_state
