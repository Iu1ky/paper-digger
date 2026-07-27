#!/usr/bin/env python3
"""Validate Paper Digger's cross-agent release contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "paper-digger"
SKILLS = PLUGIN / "skills"
EXPECTED_SKILLS = {
    "paper-digger",
    "paper-digger-ideate",
    "paper-digger-venue",
    "paper-digger-plan",
    "paper-digger-experiment",
    "paper-digger-theory",
    "paper-digger-evaluate",
}
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)#]+)(?:#[^)]+)?\)")


def fail(message: str) -> None:
    raise SystemExit(f"release check failed: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: {exc}")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} does not start with YAML frontmatter")
    try:
        raw, body = text[4:].split("\n---\n", 1)
    except ValueError:
        fail(f"{path.relative_to(ROOT)} has unterminated frontmatter")
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            fail(f"{path.relative_to(ROOT)} has unsupported multiline frontmatter")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, body


def check_skills() -> None:
    found = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
    if found != EXPECTED_SKILLS:
        fail(
            f"skill set mismatch: expected {sorted(EXPECTED_SKILLS)}, got {sorted(found)}"
        )

    for name in sorted(found):
        skill_dir = SKILLS / name
        fields, body = parse_frontmatter(skill_dir / "SKILL.md")
        if set(fields) != {"name", "description"}:
            fail(f"{name}: frontmatter must contain only name and description")
        if fields["name"] != name:
            fail(f"{name}: frontmatter name does not match directory")
        if not fields["description"].startswith("Use when"):
            fail(f"{name}: description must begin with 'Use when'")
        if len(fields["description"]) > 300:
            fail(f"{name}: description exceeds the 300-character token budget")
        if len(body.splitlines()) > 500:
            fail(f"{name}: SKILL.md exceeds 500 lines")

        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.is_file():
            fail(f"{name}: agents/openai.yaml is missing")
        openai_text = openai_yaml.read_text(encoding="utf-8")
        prompt_match = re.search(
            r'^\s*default_prompt:\s*"([^"]+)"\s*$', openai_text, re.MULTILINE
        )
        if not prompt_match or f"${name}" not in prompt_match.group(1):
            fail(f"{name}: default_prompt must explicitly mention ${name}")
        short_match = re.search(
            r'^\s*short_description:\s*"([^"]+)"\s*$', openai_text, re.MULTILINE
        )
        if not short_match or not 25 <= len(short_match.group(1)) <= 64:
            fail(f"{name}: short_description must be 25-64 characters")

        for target in LINK_RE.findall((skill_dir / "SKILL.md").read_text("utf-8")):
            if not (skill_dir / target).resolve().is_file():
                fail(f"{name}: broken relative link {target}")

    main_text = (SKILLS / "paper-digger" / "SKILL.md").read_text(encoding="utf-8")
    if "docs/specs/" in main_text or "WebSearch/WebFetch" in main_text:
        fail("main skill still contains a repository-only or host-specific reference")
    main_fields, _ = parse_frontmatter(SKILLS / "paper-digger" / "SKILL.md")
    collision_terms = ("idea发掘", "选题", "选刊", "实验编排", "理论推导")
    if any(term in main_fields["description"] for term in collision_terms):
        fail("main skill description overlaps a phase-specific trigger")
    for token in ("lean", "standard", "deep", "--full"):
        if token not in main_text:
            fail(f"main skill is missing context-budget token {token!r}")


def check_manifests() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = project["project"]["version"]
    codex = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
    claude = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
    gemini = load_json(PLUGIN / "gemini-extension.json")
    manifests = {"Codex": codex, "Claude": claude, "Gemini": gemini}
    for product, manifest in manifests.items():
        if manifest.get("name") != "paper-digger":
            fail(f"{product} manifest name mismatch")
        if manifest.get("version") != version:
            fail(f"{product} manifest version does not match pyproject")
        if not manifest.get("description"):
            fail(f"{product} manifest has no description")

    required_interface = {
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "websiteURL",
        "privacyPolicyURL",
        "termsOfServiceURL",
        "defaultPrompt",
    }
    missing_interface = required_interface - set(codex.get("interface", {}))
    if missing_interface:
        fail(f"Codex interface is missing {sorted(missing_interface)}")
    if len(codex["interface"]["defaultPrompt"]) != 3:
        fail("Codex interface must include exactly three starter prompts")

    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    for market in (codex_market, claude_market):
        entry = market["plugins"][0]
        if entry["name"] != "paper-digger":
            fail("marketplace entry name mismatch")
        if entry.get("version", version) != version:
            fail("marketplace version mismatch")

    codex_source = codex_market["plugins"][0]["source"]["path"]
    if not (ROOT / codex_source).resolve().samefile(PLUGIN):
        fail("Codex marketplace source does not resolve to the canonical plugin")
    claude_source = claude_market["plugins"][0]["source"]
    if not (ROOT / claude_source).resolve().samefile(PLUGIN):
        fail("Claude marketplace source does not resolve to the canonical plugin")

    if not (PLUGIN / "agents" / "paper-digger.md").is_file():
        fail("portable research-agent definition is missing")
    return version


def check_runtime() -> None:
    runner = SKILLS / "paper-digger" / "scripts" / "pd.py"
    completed = subprocess.run(
        [sys.executable, str(runner), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if (
        completed.returncode != 0
        or "paper-digger orchestrator CLI" not in completed.stdout
    ):
        fail(f"bundled runtime smoke failed: {completed.stderr.strip()}")


def check_release_materials() -> None:
    for name in (
        "README.md",
        "LICENSE",
        "PRIVACY.md",
        "TERMS.md",
        "SECURITY.md",
        "PUBLISHING.md",
    ):
        if not (ROOT / name).is_file():
            fail(f"{name} is missing")

    cases = load_json(ROOT / "release" / "activation-cases.json")
    positive = cases.get("positive", [])
    if len(positive) < 7 or len(cases.get("negative", [])) < 3:
        fail("activation cases need at least seven positive and three negative prompts")
    covered = {case.get("expected_skill") for case in positive}
    if covered != EXPECTED_SKILLS:
        fail("activation cases must cover every portable skill exactly by name")

    forbidden = re.compile(r"\b(?:TODO|FIXME|CHANGEME)\b|\[TODO:", re.IGNORECASE)
    for path in PLUGIN.rglob("*"):
        if (
            path.is_file()
            and path.suffix in {".md", ".json", ".py", ".yaml"}
            and forbidden.search(path.read_text(encoding="utf-8"))
        ):
            fail(f"placeholder found in {path.relative_to(ROOT)}")


def main() -> int:
    check_skills()
    version = check_manifests()
    check_runtime()
    check_release_materials()
    print(
        f"release check passed: Paper Digger {version}, "
        f"{len(EXPECTED_SKILLS)} portable skills"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
