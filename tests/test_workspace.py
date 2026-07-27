from paper_digger.state import load_state
from paper_digger.workspace import WORKSPACE_DIRS, scaffold


def test_scaffold_creates_numbered_dirs_with_readmes(tmp_path):
    ws = scaffold(tmp_path, "demo", field_="ML", now="2026-06-02T00:00:00Z", env={})
    assert ws == tmp_path / "paper-digger"
    for name in WORKSPACE_DIRS:
        assert (ws / name).is_dir()
        assert (ws / name / "README.md").exists()


def test_scaffold_writes_core_files(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    assert (ws / "state.json").exists()
    assert (ws / "ROADMAP.md").exists()
    assert (ws / "README.md").exists()
    assert (ws / "log.md").exists()


def test_scaffold_state_records_workspace_and_caps(tmp_path):
    ws = scaffold(
        tmp_path, "demo", now="2026-06-02T00:00:00Z", env={"EXA_API_KEY": "x"}
    )
    state = load_state(ws)
    assert state["workspace"] == str(ws)
    assert state["capabilities"]["websearch"] is None
    assert state["capabilities"]["exa"] is True


def test_scaffold_is_idempotent(tmp_path):
    scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
