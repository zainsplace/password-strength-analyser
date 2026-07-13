import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from password_analyzer import (
    _entropy_to_level,
    _score_to_level,
    check_password_strength,
    shannon_entropy,
)


def test_entropy_of_empty_password_is_zero():
    assert shannon_entropy("") == 0.0


def test_entropy_of_repeated_character_is_zero():
    assert shannon_entropy("aaaaaaaa") == 0.0


def test_entropy_grows_with_character_variety():
    assert shannon_entropy("abcdefgh") > shannon_entropy("aaaabbbb")


def test_score_levels_map_every_score():
    assert [_score_to_level(score) for score in range(6)] == [0, 0, 1, 2, 3, 4]


def test_score_above_maximum_is_clamped():
    assert _score_to_level(9) == 4


@pytest.mark.parametrize(
    ("bits", "level"),
    [(0, 0), (27.9, 0), (28, 1), (36, 2), (45, 3), (59.9, 3), (60, 4), (120, 4)],
)
def test_entropy_thresholds(bits, level):
    assert _entropy_to_level(bits) == level


def test_strong_password_rates_very_strong():
    score, strength, _ = check_password_strength("Zx!9mK#pQ2@nR5$v")
    assert score == 5
    assert strength == "Very Strong"


def test_missing_character_classes_produce_feedback():
    score, strength, feedback = check_password_strength("hello")
    assert score == 1
    assert strength == "Very Weak"
    joined = " ".join(feedback)
    assert "8 characters" in joined
    assert "uppercase" in joined
    assert "digit" in joined
    assert "special character" in joined


def test_low_entropy_reduces_rating_by_one_level():
    score, strength, _ = check_password_strength("Aa1!Aa1!")
    assert score == 5
    assert strength == "Strong"


def test_common_password_forces_very_weak():
    common = {"Zx!9mK#pQ2@nR5$v"}
    score, strength, feedback = check_password_strength("Zx!9mK#pQ2@nR5$v", common)
    assert strength == "Very Weak"
    assert any("common-passwords" in item for item in feedback)


def test_entropy_estimate_always_reported():
    _, _, feedback = check_password_strength("anything")
    assert any("entropy" in item.lower() for item in feedback)
