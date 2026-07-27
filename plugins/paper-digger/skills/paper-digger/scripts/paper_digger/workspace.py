"""Scaffold a Paper Digger research workspace inside a project root.

Layout is numbered + self-documenting so it reads clearly (设计规范 §7).
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .capabilities import detect
from .roadmap import render as render_roadmap
from .state import default_state, save_state

WORKSPACE_DIRNAME = "paper-digger"

WORKSPACE_DIRS: dict[str, str] = {
    "00_profile": "研究者画像、约束、能力探测",
    "01_ideation": "direction_scan, idea_cards, confirmed_idea",
    "02_venue": "venue_analysis, confirmed_venue, template/(官方模版)",
    "03_literature": "deep-research / paper-spine-research 产物、gap map",
    "04_plan": "research_plan, experiment_matrix(含最小验证), dependency_graph",
    "05_experiments": "runs/<id>/, evidence_bank, verification_report",
    "05_theory": "derivations, assumptions_ledger, validation",
    "06_manuscript": "template/ + 指向 PaperSpine paper_rewriting_output/",
    "07_reviews": "审稿报告, response-to-reviewers",
    "08_evaluation": "eval_node1..4.md(价值&诚信 verdict)",
    "artifacts": "最终交付:PDF / DOCX / PPTX",
}


def _readme(project: str, state: dict) -> str:
    caps = ", ".join(k for k, v in state.get("capabilities", {}).items() if v)
    lines = [
        f"# paper-digger 工作区 — {project}",
        "",
        "由 paper-digger 自动维护。导览见下;主计划见 `ROADMAP.md`;状态见 `state.json`。",
        "",
        f"- 当前阶段: {state.get('phase', 0)}",
        f"- 可用能力: {caps or '(none)'}",
        "",
        "## 目录",
        "",
    ]
    for name, purpose in WORKSPACE_DIRS.items():
        lines.append(f"- `{name}/` — {purpose}")
    lines.append("")
    return "\n".join(lines)


def scaffold(
    project_root: str | Path,
    project: str,
    field_: str = "",
    now: str | None = None,
    env: Mapping[str, str] | None = None,
    effort: str = "standard",
) -> Path:
    ws = Path(project_root) / WORKSPACE_DIRNAME
    ws.mkdir(parents=True, exist_ok=True)
    for name, purpose in WORKSPACE_DIRS.items():
        d = ws / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(f"# {name}\n\n{purpose}\n", encoding="utf-8")

    state = default_state(project, str(ws), field_, now=now, effort=effort)
    state["capabilities"] = detect(env=env)
    save_state(ws, state, now=now)

    (ws / "ROADMAP.md").write_text(render_roadmap(state), encoding="utf-8")
    (ws / "README.md").write_text(_readme(project, state), encoding="utf-8")
    (ws / "log.md").write_text(
        f"# Log — {project}\n\n- init (phase 0)\n", encoding="utf-8"
    )
    return ws
