#!/usr/bin/env python3
"""Install all Paper Digger skills with GitHub CLI's host-aware installer."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "paper-digger",
    "paper-digger-ideate",
    "paper-digger-venue",
    "paper-digger-plan",
    "paper-digger-experiment",
    "paper-digger-theory",
    "paper-digger-evaluate",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Install all seven Paper Digger skills for a supported agent host. "
            "GitHub CLI 2.90+ is required."
        )
    )
    parser.add_argument(
        "--agent",
        default="universal",
        help=(
            "Host name accepted by 'gh skill install', such as codex, "
            "claude-code, cursor, github-copilot, gemini-cli, opencode, "
            "windsurf, cline, roo, continue, or universal"
        ),
    )
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--repository",
        default="Iu1ky/paper-digger",
        help="GitHub OWNER/REPO source (default: Iu1ky/paper-digger)",
    )
    parser.add_argument(
        "--from-local",
        action="store_true",
        help="Install from this checkout instead of the tagged GitHub release",
    )
    args = parser.parse_args()

    gh = shutil.which("gh")
    if gh is None:
        parser.error("GitHub CLI 2.90+ with 'gh skill' is required")
    if not args.project_dir.is_dir():
        parser.error(f"project directory does not exist: {args.project_dir}")

    probe = subprocess.run(
        [gh, "skill", "--help"], text=True, capture_output=True, check=False
    )
    if probe.returncode != 0:
        parser.error("the installed GitHub CLI does not provide 'gh skill'")

    source = str(ROOT) if args.from_local else args.repository
    common = ["--agent", args.agent, "--scope", args.scope]
    if args.from_local:
        common.append("--from-local")
    if args.force:
        common.append("--force")
    for skill in SKILLS:
        subprocess.run(
            [gh, "skill", "install", source, skill, *common],
            cwd=args.project_dir,
            check=True,
        )

    print(
        f"Installed {len(SKILLS)} Paper Digger skills from {source} "
        f"for {args.agent} ({args.scope})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
