import pytest
from paper_digger.ideate import (
    NFIF_WEIGHTS,
    confirm_idea,
    rank_ideas,
    save_idea_cards,
    score_idea,
)
from paper_digger.state import load_state
from paper_digger.workspace import scaffold


def test_weights_sum_to_one_and_cover_nfif():
    assert round(sum(NFIF_WEIGHTS.values()), 6) == 1.0
    assert set(NFIF_WEIGHTS) == {"novelty", "feasibility", "impact", "fit"}


def test_score_idea_extremes():
    assert score_idea({"novelty": 5, "feasibility": 5, "impact": 5, "fit": 5}) == 5.0
    assert score_idea({"novelty": 0, "feasibility": 0, "impact": 0, "fit": 0}) == 0.0


def test_score_idea_missing_criterion_raises():
    with pytest.raises(ValueError):
        score_idea({"novelty": 3, "feasibility": 3, "impact": 3})


def test_score_idea_out_of_range_raises():
    with pytest.raises(ValueError):
        score_idea({"novelty": 6, "feasibility": 3, "impact": 3, "fit": 3})


def test_rank_ideas_sorts_desc_and_adds_nfif():
    cards = [
        {
            "id": "low",
            "scores": {"novelty": 1, "feasibility": 1, "impact": 1, "fit": 1},
        },
        {
            "id": "high",
            "scores": {"novelty": 5, "feasibility": 5, "impact": 5, "fit": 5},
        },
    ]
    ranked = rank_ideas(cards)
    assert [c["id"] for c in ranked] == ["high", "low"]
    assert ranked[0]["nfif"] == 5.0
    assert "nfif" in ranked[1]


def test_rank_ideas_does_not_mutate_input():
    cards = [
        {"id": "a", "scores": {"novelty": 2, "feasibility": 2, "impact": 2, "fit": 2}}
    ]
    rank_ideas(cards)
    assert "nfif" not in cards[0]


def test_save_idea_cards_writes_ranked_table(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    cards = [
        {
            "id": "a",
            "one_liner": "idea A",
            "scores": {"novelty": 2, "feasibility": 2, "impact": 2, "fit": 2},
        },
        {
            "id": "b",
            "one_liner": "idea B",
            "scores": {"novelty": 5, "feasibility": 5, "impact": 5, "fit": 5},
        },
    ]
    path = save_idea_cards(ws, cards)
    assert path == ws / "01_ideation" / "idea_cards.md"
    text = path.read_text(encoding="utf-8")
    assert text.index("| 1 | b |") < text.index("| 2 | a |")


def test_confirm_idea_sets_decision_and_writes_file(tmp_path):
    ws = scaffold(tmp_path, "demo", now="2026-06-02T00:00:00Z", env={})
    new_state = confirm_idea(
        ws, "b", summary="the chosen idea", now="2026-06-03T00:00:00Z"
    )
    assert new_state["decisions"]["idea"] == "b"
    confirmed = ws / "01_ideation" / "confirmed_idea.md"
    assert confirmed.exists()
    assert "b" in confirmed.read_text(encoding="utf-8")
    assert load_state(ws)["decisions"]["idea"] == "b"
