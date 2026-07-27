import pytest
from paper_digger.plan import (
    MODES,
    confirm_plan,
    dependency_order,
    minimal_validation,
    save_plan,
    validate_matrix,
)
from paper_digger.state import load_state
from paper_digger.workspace import scaffold


def _exp(id_, mode="dry", min_val=False, deps=None):
    return {
        "id": id_,
        "question": f"q-{id_}",
        "mode": mode,
        "success_criteria": "p<0.05",
        "deps": deps or [],
        "is_min_validation": min_val,
    }


def test_modes():
    assert MODES == ("dry", "wet", "theory")


def test_valid_matrix_passes():
    validate_matrix([_exp("a", min_val=True), _exp("b", deps=["a"])])  # no raise


def test_empty_matrix_raises():
    with pytest.raises(ValueError):
        validate_matrix([])


def test_duplicate_ids_raise():
    with pytest.raises(ValueError):
        validate_matrix([_exp("a", min_val=True), _exp("a")])


def test_missing_required_field_raises():
    bad = {
        "id": "x",
        "mode": "dry",
        "is_min_validation": True,
    }  # no question / success_criteria
    with pytest.raises(ValueError):
        validate_matrix([bad])


def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        validate_matrix([_exp("a", mode="simulation", min_val=True)])


def test_unknown_dependency_raises():
    with pytest.raises(ValueError):
        validate_matrix([_exp("a", min_val=True, deps=["ghost"])])


def test_requires_exactly_one_minimal_validation():
    with pytest.raises(ValueError):
        validate_matrix([_exp("a"), _exp("b")])  # zero
    with pytest.raises(ValueError):
        validate_matrix([_exp("a", min_val=True), _exp("b", min_val=True)])  # two


def test_minimal_validation_returns_designated():
    exps = [_exp("a"), _exp("b", min_val=True)]
    assert minimal_validation(exps)["id"] == "b"


def test_missing_id_reports_missing_field_not_duplicate():
    bad = {
        "question": "q",
        "mode": "dry",
        "success_criteria": "c",
        "is_min_validation": True,
    }
    with pytest.raises(ValueError, match="missing fields"):
        validate_matrix([bad])


def test_dependency_order_respects_deps_and_input_order():
    exps = [_exp("c", deps=["a", "b"]), _exp("a", min_val=True), _exp("b", deps=["a"])]
    order = dependency_order(exps)
    assert order.index("a") < order.index("b") < order.index("c")


def test_dependency_order_detects_cycle():
    exps = [_exp("a", min_val=True, deps=["b"]), _exp("b", deps=["a"])]
    with pytest.raises(ValueError):
        dependency_order(exps)


def test_save_plan_writes_research_plan(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    exps = [_exp("a", min_val=True), _exp("b", deps=["a"])]
    path = save_plan(ws, ["H1: X improves Y"], exps)
    assert path == ws / "04_plan" / "research_plan.md"
    text = path.read_text(encoding="utf-8")
    assert "H1: X improves Y" in text
    assert "a" in text and "b" in text


def test_confirm_plan_seeds_state_experiments(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    exps = [_exp("a", min_val=True), _exp("b", deps=["a"])]
    new_state = confirm_plan(ws, exps, now="t1")
    assert new_state["decisions"]["plan_approved"] is True
    seeded = new_state["experiments"]
    assert [e["id"] for e in seeded] == ["a", "b"]
    assert all(e["status"] == "planned" for e in seeded)
    a = next(e for e in seeded if e["id"] == "a")
    assert a["is_min_validation"] is True and a["mode"] == "dry"
    assert load_state(ws)["experiments"][0]["id"] == "a"
