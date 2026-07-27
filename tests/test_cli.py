from paper_digger.cli import main
from paper_digger.state import load_state, save_state
from paper_digger.venue import confirm_venue
from paper_digger.workspace import WORKSPACE_DIRNAME


def test_init_scaffolds_and_returns_zero(tmp_path, capsys):
    rc = main(["init", "--project", "demo", "--field", "ML", "--root", str(tmp_path)])
    assert rc == 0
    assert (tmp_path / "paper-digger" / "state.json").exists()
    out = capsys.readouterr().out
    assert "demo" in out
    assert "paper-digger" in out


def test_status_reports_phase(tmp_path, capsys):
    main(["init", "--project", "demo", "--root", str(tmp_path)])
    capsys.readouterr()  # clear
    rc = main(["status", "--root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "phase 0" in out.lower()
    assert "effort standard" in out.lower()


def test_status_is_compact_even_with_long_decisions(tmp_path, capsys):
    main(["init", "--project", "demo", "--root", str(tmp_path)])
    ws = tmp_path / WORKSPACE_DIRNAME
    state = load_state(ws)
    state["decisions"] = {
        "idea": "compact-idea",
        "long_audit": "sensitive-detail-" * 500,
    }
    save_state(ws, state)
    capsys.readouterr()

    assert main(["status", "--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "compact-idea" in out
    assert len(out) < 2000
    assert ("sensitive-detail-" * 10) not in out
    assert "--full" in out


def test_status_full_preserves_complete_decisions_and_roadmap(tmp_path, capsys):
    main(["init", "--project", "demo", "--root", str(tmp_path)])
    ws = tmp_path / WORKSPACE_DIRNAME
    state = load_state(ws)
    state["decisions"] = {"audit": "full-detail-" * 50}
    save_state(ws, state)
    capsys.readouterr()

    assert main(["status", "--full", "--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "full-detail-" * 50 in out
    assert "# ROADMAP" in out


def test_init_accepts_effort_mode(tmp_path, capsys):
    assert (
        main(
            [
                "init",
                "--project",
                "demo",
                "--effort",
                "lean",
                "--root",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert load_state(tmp_path / WORKSPACE_DIRNAME)["effort"] == "lean"


def test_status_without_init_errors(tmp_path, capsys):
    rc = main(["status", "--root", str(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "no workspace" in err.lower()


def test_advance_cli_increments_phase(tmp_path, capsys):
    main(["init", "--project", "demo", "--root", str(tmp_path)])
    capsys.readouterr()
    rc = main(["advance", "--root", str(tmp_path)])
    assert rc == 0
    assert load_state(tmp_path / WORKSPACE_DIRNAME)["phase"] == 1
    assert "phase 1" in capsys.readouterr().out.lower()


def test_gate_cli_blocked_then_verified(tmp_path, capsys):
    main(["init", "--project", "demo", "--root", str(tmp_path)])
    confirm_venue(
        tmp_path / WORKSPACE_DIRNAME,
        {"name": "KBS", "template": {"available": True, "verified": False}},
    )
    capsys.readouterr()
    assert main(["gate", "--root", str(tmp_path)]) == 1
    capsys.readouterr()
    assert main(["gate", "--verify", "--root", str(tmp_path)]) == 0


def test_advance_cli_out_of_range_errors(tmp_path, capsys):
    main(["init", "--project", "demo", "--root", str(tmp_path)])
    capsys.readouterr()
    rc = main(["advance", "--to", "99", "--root", str(tmp_path)])
    assert rc == 1
    assert "cannot advance" in capsys.readouterr().err.lower()
