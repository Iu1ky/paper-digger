#!/usr/bin/env python3
"""Install all Paper Digger skills with GitHub CLI's host-aware installer."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
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
SKILL_PREFIX = "plugins/paper-digger/skills"
_TRANSIENT_MARKERS = (
    "connection reset",
    "connection refused",
    "connection timed out",
    "context deadline exceeded",
    "http 502",
    "http 503",
    "http 504",
    "service unavailable",
    "temporary failure",
    "tls handshake timeout",
    "unexpected eof",
)


def _skill_selector(skill: str) -> str:
    """Return an exact repository path to avoid repeated tree-wide discovery."""
    return f"{SKILL_PREFIX}/{skill}"


def _is_transient_failure(message: str) -> bool:
    lowered = message.lower()
    return any(marker in lowered for marker in _TRANSIENT_MARKERS)


def _build_install_command(
    *,
    gh: str,
    source: str,
    skill: str,
    agent: str,
    scope: str,
    from_local: bool,
    force: bool,
    pin: str | None,
) -> list[str]:
    command = [
        gh,
        "skill",
        "install",
        source,
        _skill_selector(skill),
        "--agent",
        agent,
        "--scope",
        scope,
    ]
    if from_local:
        command.append("--from-local")
    elif pin:
        command.extend(("--pin", pin))
    if force:
        command.append("--force")
    return command


def _capture(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def _resolve_pin(gh: str, repository: str, requested: str | None) -> str:
    if requested:
        return requested

    release = _capture(
        [
            gh,
            "release",
            "view",
            "--repo",
            repository,
            "--json",
            "tagName",
            "--jq",
            ".tagName",
        ]
    )
    if release.returncode == 0 and release.stdout.strip():
        return release.stdout.strip()

    head = _capture(
        [
            gh,
            "api",
            f"repos/{repository}/commits/HEAD",
            "--jq",
            ".sha",
        ]
    )
    if head.returncode == 0 and head.stdout.strip():
        return head.stdout.strip()

    details = (head.stderr or release.stderr).strip()
    raise RuntimeError(
        f"could not resolve a release tag or HEAD commit for {repository}: {details}"
    )


def _run_install(command: list[str], cwd: Path, attempts: int = 6) -> None:
    for attempt in range(1, attempts + 1):
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            if completed.stdout:
                print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, end="", file=sys.stderr)
            return
        message = f"{completed.stdout}\n{completed.stderr}"
        if attempt < attempts and _is_transient_failure(message):
            delay = min(2 ** (attempt - 1), 8)
            print(
                f"Transient GitHub failure; retrying in {delay}s "
                f"({attempt + 1}/{attempts})...",
                file=sys.stderr,
            )
            time.sleep(delay)
            continue
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        raise subprocess.CalledProcessError(completed.returncode, command)


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
        "--pin",
        help=(
            "Install every skill from one tag or commit. For remote installs, "
            "the latest release (or HEAD) is resolved once when omitted."
        ),
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
    if args.from_local and args.pin:
        parser.error("--pin cannot be combined with --from-local")

    probe = subprocess.run(
        [gh, "skill", "--help"], text=True, capture_output=True, check=False
    )
    if probe.returncode != 0:
        parser.error("the installed GitHub CLI does not provide 'gh skill'")

    source = str(ROOT) if args.from_local else args.repository
    try:
        pin = None if args.from_local else _resolve_pin(gh, args.repository, args.pin)
    except RuntimeError as exc:
        parser.error(str(exc))
    if pin:
        print(f"Using one pinned ref for all skills: {pin}")

    for skill in SKILLS:
        command = _build_install_command(
            gh=gh,
            source=source,
            skill=skill,
            agent=args.agent,
            scope=args.scope,
            from_local=args.from_local,
            force=args.force,
            pin=pin,
        )
        try:
            _run_install(command, args.project_dir)
        except subprocess.CalledProcessError as exc:
            print(
                f"Installation failed for {skill} (exit {exc.returncode}).",
                file=sys.stderr,
            )
            return exc.returncode

    print(
        f"Installed {len(SKILLS)} Paper Digger skills from {source}"
        f"{f'@{pin}' if pin else ''} "
        f"for {args.agent} ({args.scope})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
