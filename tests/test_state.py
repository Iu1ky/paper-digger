from paper_digger.state import STATE_FILENAME, default_state, load_state, save_state


def test_default_state_shape():
    s = default_state(
        "demo", "/tmp/demo/paper-digger", field_="ML", now="2026-06-02T00:00:00Z"
    )
    assert s["project"] == "demo"
    assert s["workspace"] == "/tmp/demo/paper-digger"
    assert s["field"] == "ML"
    assert s["phase"] == 0
    assert s["status"] == "in_progress"
    assert s["effort"] == "standard"
    assert s["created"] == "2026-06-02T00:00:00Z"
    assert s["decisions"] == {}
    assert s["experiments"] == []
    assert s["evaluations"] == []
    assert s["capabilities"] == {}


def test_default_state_rejects_unknown_effort():
    import pytest

    with pytest.raises(ValueError, match="effort"):
        default_state("demo", "/tmp/demo", effort="unbounded")


def test_save_does_not_mutate_input(tmp_path):
    s = default_state("demo", str(tmp_path), now="2026-06-02T00:00:00Z")
    save_state(tmp_path, s, now="2026-06-03T00:00:00Z")
    assert "updated" not in s  # input untouched (immutability)


def test_save_then_load_roundtrip(tmp_path):
    s = default_state("demo", str(tmp_path), now="2026-06-02T00:00:00Z")
    save_state(tmp_path, s, now="2026-06-03T00:00:00Z")
    assert (tmp_path / STATE_FILENAME).exists()
    loaded = load_state(tmp_path)
    assert loaded["project"] == "demo"
    assert loaded["updated"] == "2026-06-03T00:00:00Z"


def test_save_is_utf8_human_readable(tmp_path):
    s = default_state("演示", str(tmp_path))
    save_state(tmp_path, s)
    raw = (tmp_path / STATE_FILENAME).read_text(encoding="utf-8")
    assert "演示" in raw  # ensure_ascii=False
