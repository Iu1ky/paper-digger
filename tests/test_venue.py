import pytest
from paper_digger.state import load_state
from paper_digger.venue import (
    FIT_WEIGHTS,
    confirm_venue,
    rank_venues,
    save_venue_analysis,
    score_venue_fit,
)
from paper_digger.workspace import scaffold


def test_weights_sum_to_one_and_cover_criteria():
    assert round(sum(FIT_WEIGHTS.values()), 6) == 1.0
    assert set(FIT_WEIGHTS) == {"scope", "tier", "timeline", "readiness"}


def test_score_venue_fit_extremes():
    assert (
        score_venue_fit({"scope": 5, "tier": 5, "timeline": 5, "readiness": 5}) == 5.0
    )
    assert (
        score_venue_fit({"scope": 0, "tier": 0, "timeline": 0, "readiness": 0}) == 0.0
    )


def test_score_venue_fit_missing_criterion_raises():
    with pytest.raises(ValueError):
        score_venue_fit({"scope": 3, "tier": 3, "timeline": 3})


def test_score_venue_fit_out_of_range_raises():
    with pytest.raises(ValueError):
        score_venue_fit({"scope": 9, "tier": 3, "timeline": 3, "readiness": 3})


def test_rank_venues_sorts_desc_and_adds_fit():
    cands = [
        {
            "name": "WeakConf",
            "scores": {"scope": 1, "tier": 1, "timeline": 1, "readiness": 1},
        },
        {
            "name": "StrongJournal",
            "scores": {"scope": 5, "tier": 5, "timeline": 5, "readiness": 5},
        },
    ]
    ranked = rank_venues(cands)
    assert [c["name"] for c in ranked] == ["StrongJournal", "WeakConf"]
    assert ranked[0]["fit"] == 5.0
    assert "fit" in ranked[1]


def test_rank_venues_does_not_mutate_input():
    cands = [
        {"name": "X", "scores": {"scope": 2, "tier": 2, "timeline": 2, "readiness": 2}}
    ]
    rank_venues(cands)
    assert "fit" not in cands[0]


def test_save_venue_analysis_writes_ranked_table(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    cands = [
        {
            "name": "WeakConf",
            "scores": {"scope": 1, "tier": 1, "timeline": 1, "readiness": 1},
            "template": {"available": False},
        },
        {
            "name": "StrongJournal",
            "scores": {"scope": 5, "tier": 5, "timeline": 5, "readiness": 5},
            "template": {"available": True},
            "deadline": "rolling",
        },
    ]
    path = save_venue_analysis(ws, cands)
    assert path == ws / "02_venue" / "venue_analysis.md"
    text = path.read_text(encoding="utf-8")
    assert text.index("| 1 | StrongJournal |") < text.index("| 2 | WeakConf |")
    assert "yes" in text


def test_confirm_venue_persists_name_and_template(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    venue = {
        "name": "KBS",
        "type": "journal",
        "template": {
            "available": True,
            "url": "https://example.com/kbs.zip",
            "format": "latex",
            "verified": False,
        },
    }
    new_state = confirm_venue(ws, venue, now="2026-06-03T00:00:00Z")
    assert new_state["decisions"]["venue"] == "KBS"
    assert new_state["venue"]["template"]["available"] is True
    assert new_state["venue"]["template"]["format"] == "latex"
    confirmed = ws / "02_venue" / "confirmed_venue.md"
    assert confirmed.exists()
    assert "KBS" in confirmed.read_text(encoding="utf-8")
    reloaded = load_state(ws)
    assert reloaded["venue"]["name"] == "KBS"
    assert reloaded["decisions"]["venue"] == "KBS"


def test_confirm_venue_requires_name(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    with pytest.raises(ValueError):
        confirm_venue(ws, {"template": {"available": False}})


def test_confirm_venue_defaults_template_when_absent(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    new_state = confirm_venue(ws, {"name": "SomeWorkshop"}, now="2026-06-03T00:00:00Z")
    assert new_state["venue"]["template"]["available"] is False
