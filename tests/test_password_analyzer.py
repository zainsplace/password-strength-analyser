import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from password_analyzer import (
    check_password_strength,
    estimate_guesses,
    load_common_passwords,
)

COMMON = load_common_passwords(Path(__file__).resolve().parents[1] / "common_passwords.txt")

LEVELS = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]


def rating(password):
    return LEVELS.index(check_password_strength(password, COMMON).strength)


def kinds(password):
    return {match.kind for match in estimate_guesses(password, COMMON).matches}


@pytest.mark.parametrize(
    "password",
    ["P@ssw0rd", "Password1!", "Qwertyuiop123!", "password", "12345678",
     "abcdefghijklmnopqrstuvwxyz", "aaaaaaaaaaaaaaaa", "Summer2024!"],
)
def test_canonical_weak_passwords_rate_weak_or_worse(password):
    assert rating(password) <= LEVELS.index("Weak")


def test_long_passphrase_rates_very_strong():
    assert rating("correct horse battery staple") == LEVELS.index("Very Strong")


def test_long_random_password_rates_very_strong():
    assert rating("Zx!9mK#pQ2@nR5$v") == LEVELS.index("Very Strong")


def test_stacked_keyboard_walks_are_not_rated_strong():
    assert rating("1qaz2wsx3edc4rfv!Q") <= LEVELS.index("Medium")


def test_empty_password_is_one_guess():
    assert estimate_guesses("", COMMON).guesses == 1
    assert check_password_strength("", COMMON).strength == "Very Weak"


def test_common_passwords_keep_their_rank():
    assert COMMON["123456"] == 1
    assert COMMON["password"] == 2


def test_leetspeak_is_folded_back_to_the_dictionary_word():
    matches = estimate_guesses("P@ssw0rd", COMMON).matches
    assert [(m.kind, m.word) for m in matches] == [("dictionary", "password")]


def test_capitalisation_costs_the_attacker_little():
    lower = estimate_guesses("password", COMMON).guesses
    capital = estimate_guesses("Password", COMMON).guesses
    assert lower < capital <= lower * 2


def test_keyboard_walk_is_detected():
    assert kinds("zxcvfr") == {"keyboard"}


def test_shifted_keyboard_walk_is_detected():
    assert kinds("^&*()_+") == {"keyboard"}


def test_ascending_and_descending_sequences_are_detected():
    assert kinds("lmnopq") == {"sequence"}
    assert kinds("hgfedc") == {"sequence"}


def test_repeated_unit_is_detected():
    assert kinds("xkqxkqxkq") == {"repeat"}


@pytest.mark.parametrize("password", ["1" * 64, "a" * 64, "ab" * 32])
def test_long_repetitive_password_is_analysed_quickly(password):
    started = time.perf_counter()
    assert check_password_strength(password, COMMON).strength == "Very Weak"
    assert time.perf_counter() - started < 2


def test_crack_time_uses_singular_units():
    feedback = " ".join(check_password_strength("Qwertyuiop123!", COMMON).feedback)
    assert "about 1 hour." in feedback


def test_year_is_detected():
    assert "year" in kinds("kqzv1987")


def test_random_characters_fall_back_to_brute_force():
    assert kinds("Zx!9mK#pQ2@nR5$v") == {"bruteforce"}


def test_each_extra_random_character_multiplies_the_guesses():
    shorter = estimate_guesses("Zx!9mK#p", COMMON).guesses
    longer = estimate_guesses("Zx!9mK#pQ", COMMON).guesses
    assert longer >= shorter * 10


def test_feedback_names_the_pattern_that_weakened_the_password():
    feedback = " ".join(check_password_strength("Qwertyuiop123!", COMMON).feedback)
    assert "keyboard pattern" in feedback


def test_feedback_never_asks_for_composition_rules():
    feedback = " ".join(check_password_strength("correct horse battery staple", COMMON).feedback)
    assert "uppercase" not in feedback
    assert "digit" not in feedback


def test_estimate_is_reported_in_feedback():
    feedback = " ".join(check_password_strength("anything", COMMON).feedback)
    assert "guesses" in feedback
