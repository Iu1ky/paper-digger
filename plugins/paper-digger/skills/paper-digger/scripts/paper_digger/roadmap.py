"""The flow-level master plan (ROADMAP.md), owned by the orchestrator.

Distinct from 04_plan/research_plan.md (the science-level plan owned by
paper-digger-plan). This answers "how the whole project proceeds".
"""

from __future__ import annotations

from typing import Any

PHASES: list[dict[str, Any]] = [
    {
        "id": 0,
        "name": "立项 + 统筹",
        "skill": "paper-digger (orchestrator)",
        "gate": None,
    },
    {
        "id": 1,
        "name": "方向 + idea 发掘 + 确定",
        "skill": "paper-digger-ideate",
        "gate": "选 idea + 评价节点①",
    },
    {
        "id": 2,
        "name": "确认目标期刊/会议",
        "skill": "paper-digger-venue",
        "gate": "选定 venue",
    },
    {
        "id": 3,
        "name": "文献深挖",
        "skill": "deep-research / paper-spine-research",
        "gate": None,
    },
    {"id": 4, "name": "安排计划", "skill": "paper-digger-plan", "gate": "批准计划"},
    {
        "id": 5,
        "name": "实验执行 + 理论推导",
        "skill": "paper-digger-experiment / -theory",
        "gate": "评价节点②③④",
    },
    {
        "id": 6,
        "name": "撰写初稿",
        "skill": "paper-spine-build / academic-paper (+模版闸门)",
        "gate": None,
    },
    {"id": 7, "name": "润色文字", "skill": "nature-polishing", "gate": None},
    {
        "id": 8,
        "name": "模拟严苛审稿",
        "skill": "academic-paper-reviewer",
        "gate": "审稿决定",
    },
    {
        "id": 9,
        "name": "返回修改打磨",
        "skill": "ars-revision / paper-spine-rewrite",
        "gate": "每轮修改",
    },
    {
        "id": 10,
        "name": "定稿 + 传播",
        "skill": "ars-format-convert / paper-spine-latex / ...",
        "gate": None,
    },
]


def render(state: dict[str, Any]) -> str:
    current = state.get("phase", 0)
    project = state.get("project", "")
    lines = [
        f"# ROADMAP — {project}",
        "",
        "> 流程级主计划(orchestrator 维护)。`▶` = 当前阶段。",
        "> 评价节点①②③④ 由 paper-digger-evaluate 触发(研究期红队)。",
        "",
        "| | # | 阶段 | 负责 skill | 闸门 |",
        "|---|---|---|---|---|",
    ]
    for p in PHASES:
        marker = "▶" if p["id"] == current else ""
        gate = p["gate"] or ""
        lines.append(f"| {marker} | {p['id']} | {p['name']} | {p['skill']} | {gate} |")
    lines.append("")
    return "\n".join(lines)
