import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLUGIN = ROOT / "plugins" / "paper-digger"
SKILLS = PLUGIN / "skills"
EXPECTED = {
    "paper-digger",
    "paper-digger-ideate",
    "paper-digger-venue",
    "paper-digger-plan",
    "paper-digger-experiment",
    "paper-digger-theory",
    "paper-digger-evaluate",
}


def test_distribution_has_exactly_seven_self_describing_skills():
    assert {path.parent.name for path in SKILLS.glob("*/SKILL.md")} == EXPECTED
    for name in EXPECTED:
        text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
        assert f"name: {name}" in text
        metadata = (SKILLS / name / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        assert f"${name}" in metadata


def test_all_product_manifests_share_the_python_version():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]
    paths = (
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
        PLUGIN / "gemini-extension.json",
    )
    assert {
        json.loads(path.read_text(encoding="utf-8"))["version"] for path in paths
    } == {version}


def test_marketplaces_resolve_to_the_canonical_plugin():
    codex = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
    )
    claude = json.loads(
        (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    assert (ROOT / codex["plugins"][0]["source"]["path"]).resolve() == PLUGIN.resolve()
    assert (ROOT / claude["plugins"][0]["source"]).resolve() == PLUGIN.resolve()


def test_bundled_pd_runtime_runs_without_installing_the_package():
    runner = SKILLS / "paper-digger" / "scripts" / "pd.py"
    completed = subprocess.run(
        [sys.executable, str(runner), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "paper-digger orchestrator CLI" in completed.stdout


def test_release_activation_suite_has_positive_and_negative_cases():
    cases = json.loads(
        (ROOT / "release" / "activation-cases.json").read_text(encoding="utf-8")
    )
    assert len(cases["positive"]) >= 7
    assert len(cases["negative"]) >= 3
    assert {case["expected_skill"] for case in cases["positive"]} == EXPECTED
