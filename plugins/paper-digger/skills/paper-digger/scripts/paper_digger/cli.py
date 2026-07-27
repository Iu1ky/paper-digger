"""Portable ``pd`` CLI wiring over the Paper Digger runtime."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from .orchestrate import advance_phase, mark_template_verified, template_gate_status
from .roadmap import PHASES
from .roadmap import render as render_roadmap
from .state import EFFORT_MODES, STATE_FILENAME, load_state
from .workspace import WORKSPACE_DIRNAME, scaffold

_CONTEXT_PATHS = {
    0: ("00_profile/",),
    1: ("00_profile/", "01_ideation/"),
    2: ("01_ideation/confirmed_idea.md", "02_venue/"),
    3: (
        "01_ideation/confirmed_idea.md",
        "02_venue/confirmed_venue.md",
        "03_literature/",
    ),
    4: (
        "01_ideation/confirmed_idea.md",
        "02_venue/confirmed_venue.md",
        "03_literature/",
        "04_plan/",
    ),
    5: (
        "04_plan/research_plan.md",
        "05_experiments/evidence_bank.md",
        "05_theory/validation.md",
        "08_evaluation/",
    ),
    6: (
        "02_venue/confirmed_venue.md",
        "05_experiments/evidence_bank.md",
        "05_theory/validation.md",
        "06_manuscript/",
    ),
    7: ("05_experiments/evidence_bank.md", "06_manuscript/"),
    8: ("05_experiments/evidence_bank.md", "06_manuscript/", "07_reviews/"),
    9: (
        "05_experiments/evidence_bank.md",
        "06_manuscript/",
        "07_reviews/",
    ),
    10: ("06_manuscript/", "07_reviews/", "artifacts/"),
}


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cmd_init(args: argparse.Namespace) -> int:
    ws = scaffold(
        args.root,
        args.project,
        field_=args.field or "",
        now=_now(),
        effort=args.effort,
    )
    print(f"Initialized paper-digger workspace for '{args.project}' at {ws}")
    print(render_roadmap(load_state(ws)))
    return 0


def _one_line(value: object, limit: int = 80) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def _compact_decisions(state: dict) -> str:
    decisions = state.get("decisions", {})
    if not decisions:
        return "(none)"
    preferred = [key for key in ("idea", "venue", "plan_approved") if key in decisions]
    selected = preferred + [key for key in decisions if key not in preferred]
    selected = selected[:4]
    summary = "; ".join(f"{key}={_one_line(decisions[key])}" for key in selected)
    remaining = len(decisions) - len(selected)
    return f"{summary}; +{remaining} more" if remaining else summary


def _render_compact_status(state: dict) -> str:
    phase_id = int(state.get("phase", 0))
    phase = next((item for item in PHASES if item["id"] == phase_id), None)
    phase_name = phase["name"] if phase else "unknown"
    route = phase["skill"] if phase else "unknown"
    lines = [
        (
            f"Project: {state.get('project', '')} | phase {phase_id} ({phase_name}) "
            f"| status {state.get('status', '')} | effort {state.get('effort', 'standard')}"
        ),
        f"Route: {route}",
        f"Decisions: {_compact_decisions(state)}",
    ]
    if phase and phase.get("gate"):
        lines.append(f"Gate: {phase['gate']}")

    experiments = state.get("experiments", [])
    if experiments:
        counts = Counter(str(item.get("status", "unknown")) for item in experiments)
        lines.append(
            "Experiments: "
            + ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
        )

    evaluations = state.get("evaluations", [])
    if evaluations:
        latest = evaluations[-1]
        lines.append(
            "Latest evaluation: "
            f"node {latest.get('node', '?')} {latest.get('verdict', 'unknown')}; "
            f"blocking_integrity={latest.get('blocking_integrity', False)}"
        )

    context_paths = ("state.json", *_CONTEXT_PATHS.get(phase_id, ("ROADMAP.md",)))
    lines.append("Context paths: " + ", ".join(context_paths))
    lines.append(
        "Read these paths selectively; do not scan runs/logs recursively. "
        "Use `pd status --full` only when the complete roadmap or decision text is needed."
    )
    return "\n".join(lines)


def _cmd_status(args: argparse.Namespace) -> int:
    ws = Path(args.root) / WORKSPACE_DIRNAME
    if not (ws / STATE_FILENAME).exists():
        print(f"No workspace found at {ws}. Run `pd init` first.", file=sys.stderr)
        return 1
    state = load_state(ws)
    if not args.full:
        print(_render_compact_status(state))
        return 0
    print(
        f"Project: {state['project']}  |  phase {state['phase']}  |  "
        f"status {state['status']}  |  effort {state.get('effort', 'standard')}"
    )
    decided = (
        ", ".join(f"{k}={v}" for k, v in state.get("decisions", {}).items()) or "(none)"
    )
    print(f"Decisions: {decided}")
    print(render_roadmap(state))
    return 0


def _cmd_advance(args: argparse.Namespace) -> int:
    ws = Path(args.root) / WORKSPACE_DIRNAME
    if not (ws / STATE_FILENAME).exists():
        print(f"No workspace found at {ws}. Run `pd init` first.", file=sys.stderr)
        return 1
    try:
        state = advance_phase(ws, to_phase=args.to, now=_now())
    except ValueError as exc:
        print(f"Cannot advance: {exc}", file=sys.stderr)
        return 1
    print(f"Advanced to phase {state['phase']}")
    print(render_roadmap(state))
    return 0


def _cmd_gate(args: argparse.Namespace) -> int:
    ws = Path(args.root) / WORKSPACE_DIRNAME
    if not (ws / STATE_FILENAME).exists():
        print(f"No workspace found at {ws}. Run `pd init` first.", file=sys.stderr)
        return 1
    state = mark_template_verified(ws, now=_now()) if args.verify else load_state(ws)
    status = template_gate_status(state)
    label = "READY" if status["ready"] else "BLOCKED"
    print(f"Template gate: {label} — {status['reason']}")
    return 0 if status["ready"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pd", description="paper-digger orchestrator CLI"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser(
        "init", help="scaffold a research workspace in the project root"
    )
    p_init.add_argument("--project", required=True)
    p_init.add_argument("--field", default="")
    p_init.add_argument("--effort", choices=EFFORT_MODES, default="standard")
    p_init.add_argument("--root", default=".")
    p_init.set_defaults(func=_cmd_init)

    p_status = sub.add_parser(
        "status", help="resume with a compact current-phase context"
    )
    p_status.add_argument(
        "--full",
        action="store_true",
        help="show all decisions and the complete roadmap",
    )
    p_status.add_argument("--root", default=".")
    p_status.set_defaults(func=_cmd_status)

    p_advance = sub.add_parser(
        "advance", help="advance to the next phase (or --to N) and refresh ROADMAP"
    )
    p_advance.add_argument("--to", type=int, default=None)
    p_advance.add_argument("--root", default=".")
    p_advance.set_defaults(func=_cmd_advance)

    p_gate = sub.add_parser(
        "gate", help="check the Phase-6 template gate (--verify to mark verified)"
    )
    p_gate.add_argument("--verify", action="store_true")
    p_gate.add_argument("--root", default=".")
    p_gate.set_defaults(func=_cmd_gate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
