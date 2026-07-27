import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "install_skills.py"
SPEC = importlib.util.spec_from_file_location("install_skills", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
install_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install_skills)

_build_install_command = install_skills._build_install_command
_is_transient_failure = install_skills._is_transient_failure
_skill_selector = install_skills._skill_selector


def test_remote_install_command_uses_exact_path_and_one_resolved_pin():
    command = _build_install_command(
        gh="/usr/bin/gh",
        source="Iu1ky/paper-digger",
        skill="paper-digger-evaluate",
        agent="cursor",
        scope="project",
        from_local=False,
        force=False,
        pin="v0.1.1",
    )
    assert command == [
        "/usr/bin/gh",
        "skill",
        "install",
        "Iu1ky/paper-digger",
        "plugins/paper-digger/skills/paper-digger-evaluate",
        "--agent",
        "cursor",
        "--scope",
        "project",
        "--pin",
        "v0.1.1",
    ]


def test_local_install_command_has_no_remote_pin():
    command = _build_install_command(
        gh="gh",
        source="/tmp/paper-digger",
        skill="paper-digger",
        agent="universal",
        scope="user",
        from_local=True,
        force=True,
        pin=None,
    )
    assert "--from-local" in command
    assert "--force" in command
    assert "--pin" not in command


def test_skill_selector_uses_exact_repository_path():
    assert (
        _skill_selector("paper-digger-theory")
        == "plugins/paper-digger/skills/paper-digger-theory"
    )


def test_only_network_like_failures_are_retried():
    assert _is_transient_failure("read: connection reset by peer")
    assert _is_transient_failure("HTTP 503 Service Unavailable")
    assert not _is_transient_failure("unknown skill name")
