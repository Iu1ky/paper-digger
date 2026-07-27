import pytest
from paper_digger.theory import (
    STEP_STATUS,
    record_validation,
    save_derivation,
    unproven_steps,
    validate_derivation,
)
from paper_digger.workspace import scaffold


def _step(id_, status="proven"):
    return {
        "id": id_,
        "statement": f"stmt-{id_}",
        "justification": "because",
        "status": status,
    }


def test_step_status_values():
    assert STEP_STATUS == ("proven", "conjecture")


def test_valid_derivation_passes():
    validate_derivation([_step("s1"), _step("s2", "conjecture")])  # no raise


def test_empty_derivation_raises():
    with pytest.raises(ValueError):
        validate_derivation([])


def test_missing_field_raises():
    with pytest.raises(ValueError):
        validate_derivation(
            [{"id": "s1", "status": "proven"}]
        )  # no statement/justification


def test_invalid_status_is_hand_waving_and_raises():
    with pytest.raises(ValueError):
        validate_derivation(
            [{"id": "s1", "statement": "x", "justification": "y", "status": "obvious"}]
        )


def test_duplicate_step_ids_raise():
    with pytest.raises(ValueError):
        validate_derivation([_step("s1"), _step("s1")])


def test_unproven_steps_returns_only_conjectures():
    steps = [_step("s1"), _step("s2", "conjecture"), _step("s3", "conjecture")]
    assert [s["id"] for s in unproven_steps(steps)] == ["s2", "s3"]


def test_save_derivation_writes_ledger_and_derivation(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    steps = [
        {
            "id": "s1",
            "statement": "A implies B",
            "justification": "by lemma 1",
            "status": "proven",
        },
        {
            "id": "s2",
            "statement": "B implies C",
            "justification": "open",
            "status": "conjecture",
        },
    ]
    path = save_derivation(ws, [{"id": "a1", "statement": "X is convex"}], steps)
    assert path == ws / "05_theory" / "derivations.md"
    assert (ws / "05_theory" / "assumptions_ledger.md").exists()
    dtext = path.read_text(encoding="utf-8")
    assert "s1" in dtext and "s2" in dtext
    assert "conjecture" in dtext  # status column
    assert (
        "open conjecture" in dtext
    )  # ⚠️ warning block surfaces the unproven step (s2)
    assert "X is convex" in (ws / "05_theory" / "assumptions_ledger.md").read_text(
        encoding="utf-8"
    )


def test_record_validation_writes_file(tmp_path):
    ws = scaffold(tmp_path, "demo", now="t0", env={})
    path = record_validation(
        ws,
        [{"check": "numerical sanity", "passed": True, "notes": "matches sim"}],
        now="t1",
    )
    assert path == ws / "05_theory" / "validation.md"
    text = path.read_text(encoding="utf-8")
    assert "numerical sanity" in text
    assert "_recorded @ t1_" in text  # the optional `now` footer
