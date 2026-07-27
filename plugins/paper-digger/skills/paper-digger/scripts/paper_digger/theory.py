"""Phase-5b theory derivation: step validation and persistence.

The derivation itself (assumptions, lemmas, proofs) is prompt-driven per
skills/paper-digger-theory/SKILL.md (parallel subagents explore routes; a
verifier does numerical/counterexample checks). This module enforces that every
step is either `proven` or explicitly `conjecture`, surfaces the open
conjectures, and persists the derivation + ledger + validation to 05_theory/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

STEP_STATUS = ("proven", "conjecture")
_THEORY_DIR = "05_theory"
_REQUIRED_STEP_FIELDS = ("id", "statement", "justification", "status")


def validate_derivation(steps: list[dict[str, Any]]) -> None:
    """Validate derivation steps; raise ValueError on any problem.

    No hand-waving: every step needs id/statement/justification/status with status
    in STEP_STATUS (proven|conjecture). Ids must be unique. Non-empty.
    """
    if not steps:
        raise ValueError("derivation has no steps")
    for step in steps:
        missing = [f for f in _REQUIRED_STEP_FIELDS if f not in step]
        if missing:
            raise ValueError(
                f"step {step.get('id')!r} missing fields: {sorted(missing)}"
            )
        if step["status"] not in STEP_STATUS:
            raise ValueError(
                f"step {step['id']!r} has invalid status {step['status']!r} "
                f"(no hand-waving: use one of {STEP_STATUS})"
            )
    ids = [s["id"] for s in steps]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate step ids")


def unproven_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the `conjecture` steps — the gaps still to close or flag as unproven."""
    validate_derivation(steps)
    return [s for s in steps if s["status"] == "conjecture"]


def save_derivation(
    workspace: str | Path,
    assumptions: list[dict[str, Any]],
    steps: list[dict[str, Any]],
) -> Path:
    """Write `05_theory/assumptions_ledger.md` + `05_theory/derivations.md`; return the derivation path."""
    validate_derivation(steps)
    out_dir = Path(workspace) / _THEORY_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    ledger_lines = ["# Assumptions ledger", ""]
    for assumption in assumptions:
        statement = str(assumption.get("statement", "")).replace("\n", " ")
        ledger_lines.append(f"- [{assumption.get('id', '')}] {statement}")
    out_dir.joinpath("assumptions_ledger.md").write_text(
        "\n".join(ledger_lines) + "\n", encoding="utf-8"
    )

    deriv_lines = [
        "# Derivation",
        "",
        "| id | status | statement | justification |",
        "|---|---|---|---|",
    ]
    for step in steps:
        statement = str(step["statement"]).replace("|", "\\|").replace("\n", " ")
        justification = (
            str(step["justification"]).replace("|", "\\|").replace("\n", " ")
        )
        deriv_lines.append(
            f"| {step['id']} | {step['status']} | {statement} | {justification} |"
        )
    open_conjectures = [
        s for s in steps if s["status"] == "conjecture"
    ]  # steps already validated above
    if open_conjectures:
        ids = ", ".join(s["id"] for s in open_conjectures)
        deriv_lines += [
            "",
            f"> ⚠️ {len(open_conjectures)} open conjecture(s) (unproven): {ids}",
        ]
    path = out_dir / "derivations.md"
    path.write_text("\n".join(deriv_lines) + "\n", encoding="utf-8")
    return path


def record_validation(
    workspace: str | Path,
    validations: list[dict[str, Any]],
    now: str | None = None,
) -> Path:
    """Write `05_theory/validation.md` (numerical/counterexample/limit checks); return its path."""
    out_dir = Path(workspace) / _THEORY_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Validation", "", "| check | passed | notes |", "|---|---|---|"]
    for v in validations:
        check = str(v.get("check", "")).replace("|", "\\|").replace("\n", " ")
        notes = str(v.get("notes", "")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {check} | {bool(v.get('passed'))} | {notes} |")
    if now is not None:
        lines += ["", f"_recorded @ {now}_"]
    path = out_dir / "validation.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
