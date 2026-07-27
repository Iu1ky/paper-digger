"""Research-time value and integrity evaluation — the 4-node red-team.

Deterministic helpers only. The adversarial judgement itself is performed by
subagents at runtime per skills/paper-digger-evaluate/SKILL.md; this module
aggregates their per-lens verdicts into a node verdict, renders the report,
and records it into the workspace + state.json.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import load_state, save_state

VERDICTS = ("GREEN", "YELLOW", "RED")
_SEVERITY = {"GREEN": 0, "YELLOW": 1, "RED": 2}

# Axis A = value/quality; Axis B = integrity / cognitive-failure.
AXIS_A = ("A1_value", "A2_novelty", "A3_logic", "A4_level", "A5_evidence")
AXIS_B = (
    "B1_fabrication",
    "B2_method_fiction",
    "B3_citation_hallucination",
    "B4_fixed_thinking",
)


def aggregate(lens_verdicts: list[dict[str, Any]]) -> dict[str, Any]:
    """Combine per-lens verdicts into a node verdict (conservative worst-of).

    Each lens verdict dict: {"lens": str, "axis": "A"|"B",
    "verdict": "GREEN"|"YELLOW"|"RED", "must_fix": [str], "rationale": str}.
    Overall = worst severity across lenses. Any Axis-B (integrity) lens at RED
    sets `blocking_integrity`. `must_fix` = union over all non-GREEN lenses.
    """
    if not lens_verdicts:
        raise ValueError("no lens verdicts to aggregate")
    overall = "GREEN"
    must_fix: list[str] = []
    blocking_integrity = False
    for lv in lens_verdicts:
        verdict = lv["verdict"]
        if verdict not in _SEVERITY:
            raise ValueError(f"invalid verdict: {verdict!r}")
        if _SEVERITY[verdict] > _SEVERITY[overall]:
            overall = verdict
        if lv.get("axis") == "B" and verdict == "RED":
            blocking_integrity = True
        if verdict != "GREEN":
            must_fix.extend(lv.get("must_fix", []))
    return {
        "verdict": overall,
        "must_fix": must_fix,
        "blocking_integrity": blocking_integrity,
    }


# Per-node emphasis (drives the SKILL.md prompt). Node 4 = full audit.
NODE_FOCUS: dict[int, tuple[str, ...]] = {
    1: ("A1_value", "A2_novelty", "B4_fixed_thinking"),
    2: ("A5_evidence", "B1_fabrication", "B2_method_fiction"),
    3: ("A3_logic", "A4_level", "B1_fabrication", "B3_citation_hallucination"),
    4: AXIS_A + AXIS_B,
}


def render_report(
    node: int, lens_verdicts: list[dict[str, Any]], summary: dict[str, Any]
) -> str:
    """Render the `eval_node<N>.md` report content."""
    lines = [
        f"# 评价节点 {node} — verdict: {summary['verdict']}",
        "",
        f"- blocking_integrity: {summary['blocking_integrity']}",
        "",
        "| lens | axis | verdict | rationale |",
        "|---|---|---|---|",
    ]
    for lv in lens_verdicts:
        rationale = str(lv.get("rationale", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {lv.get('lens', '')} | {lv.get('axis', '')} | {lv['verdict']} | {rationale} |"
        )
    lines.append("")
    lines.append("## 必修项 (must_fix)")
    if summary["must_fix"]:
        lines.extend(f"- {item}" for item in summary["must_fix"])
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def record(
    workspace: str | Path,
    node: int,
    lens_verdicts: list[dict[str, Any]],
    now: str | None = None,
) -> dict[str, Any]:
    """Aggregate, write `08_evaluation/eval_node<N>.md`, append to state.evaluations[].

    Returns the aggregated summary. Does not mutate inputs or the loaded state
    (builds a new state dict before saving).
    """
    summary = aggregate(lens_verdicts)
    ws = Path(workspace)
    report_dir = ws / "08_evaluation"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"eval_node{node}.md").write_text(
        render_report(node, lens_verdicts, summary), encoding="utf-8"
    )
    entry: dict[str, Any] = {
        "node": node,
        "verdict": summary["verdict"],
        "must_fix": summary["must_fix"],
        "blocking_integrity": summary["blocking_integrity"],
    }
    if now is not None:
        entry["at"] = now
    state = load_state(ws)
    new_state = {**state, "evaluations": [*state.get("evaluations", []), entry]}
    save_state(ws, new_state, now=now)
    return summary
