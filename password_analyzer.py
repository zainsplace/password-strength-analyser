#!/usr/bin/env python3

import math
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

GUESSES_PER_SECOND = 10_000
MAX_ANALYSED_LENGTH = 64
REFERENCE_YEAR = date.today().year

LEVEL_THRESHOLDS = (
    (1e15, "Very Strong"),
    (1e12, "Strong"),
    (1e9, "Medium"),
    (1e6, "Weak"),
)

LEET = {
    "@": "a", "4": "a", "8": "b", "3": "e", "6": "g", "9": "g", "1": "il",
    "!": "i", "|": "il", "0": "o", "$": "s", "5": "s", "7": "t", "+": "t",
}

KEYBOARD_ROWS = (
    ("`1234567890-=", "~!@#$%^&*()_+", 0.0),
    ("qwertyuiop[]\\", "QWERTYUIOP{}|", 1.5),
    ("asdfghjkl;'", 'ASDFGHJKL:"', 1.75),
    ("zxcvbnm,./", "ZXCVBNM<>?", 2.25),
)


def _build_keyboard():
    position = {}
    shifted = set()
    for row, (plain, shift, offset) in enumerate(KEYBOARD_ROWS):
        for index, (lower, upper) in enumerate(zip(plain, shift)):
            position[lower] = (row, index + offset)
            position[upper] = (row, index + offset)
            shifted.add(upper)
    return position, shifted


KEY_POSITION, SHIFTED_KEYS = _build_keyboard()
PLAIN_KEYS = [key for row in KEYBOARD_ROWS for key in row[0]]


def _key_step(a: str, b: str):
    if a not in KEY_POSITION or b not in KEY_POSITION:
        return None
    (row_a, x_a), (row_b, x_b) = KEY_POSITION[a], KEY_POSITION[b]
    rows, across = row_b - row_a, x_b - x_a
    if rows == 0 and abs(across) == 1 or abs(rows) == 1 and abs(across) < 1:
        return rows, across > 0
    return None


KEY_COUNT = len(PLAIN_KEYS)
AVERAGE_DEGREE = sum(
    sum(_key_step(key, other) is not None for other in PLAIN_KEYS) for key in PLAIN_KEYS
) / KEY_COUNT


@dataclass(frozen=True)
class Match:
    kind: str
    start: int
    end: int
    token: str
    guesses: float
    word: str = ""


@dataclass(frozen=True)
class Estimate:
    guesses: float
    matches: list = field(default_factory=list)


@dataclass(frozen=True)
class Assessment:
    strength: str
    guesses: float
    bits: float
    matches: list
    feedback: list


def load_common_passwords(path):
    ranked = {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip().lower()
                if word and word not in ranked:
                    ranked[word] = len(ranked) + 1
    except FileNotFoundError:
        pass
    return ranked


def _variations(flags) -> int:
    marked = sum(flags)
    plain = len(flags) - marked
    if marked == 0:
        return 1
    if plain == 0 or marked == 1 and (flags[0] or flags[-1]):
        return 2
    return sum(math.comb(len(flags), k) for k in range(1, min(marked, plain) + 1))


def _case_variations(token: str) -> int:
    return _variations([c.isupper() for c in token if c.isalpha()])


def _dictionary_matches(text: str, ranked: dict):
    prefixes = {word[:size] for word in ranked for size in range(1, len(word) + 1)}
    lower = text.lower()
    for start in range(len(text)):
        variants = [("", 0)]
        for end in range(start + 1, len(text) + 1):
            char = lower[end - 1]
            options = [(char, 0)] + [(letter, 1) for letter in LEET.get(char, "")]
            variants = [
                (so_far + option, subs + cost)
                for so_far, subs in variants
                for option, cost in options
                if so_far + option in prefixes
            ]
            if not variants:
                break
            if end - start < 3:
                continue
            token = text[start:end]
            found = [
                (ranked[word] * _case_variations(token) * 2 ** subs, word)
                for word, subs in variants
                if word in ranked
            ]
            if found:
                guesses, word = min(found)
                yield Match("dictionary", start, end, token, guesses, word)


def _keyboard_guesses(token: str) -> float:
    steps = [_key_step(a, b) for a, b in zip(token, token[1:])]
    turns = 1 + sum(1 for a, b in zip(steps, steps[1:]) if a != b)
    guesses = 0.0
    for length in range(2, len(token) + 1):
        for used in range(1, min(turns, length - 1) + 1):
            guesses += math.comb(length - 1, used - 1) * KEY_COUNT * AVERAGE_DEGREE ** used
    return guesses * _variations([c in SHIFTED_KEYS for c in token])


def _keyboard_matches(text: str):
    for start in range(len(text) - 2):
        end = start + 1
        while end < len(text) and _key_step(text[end - 1], text[end]) is not None:
            end += 1
            if end - start >= 3:
                token = text[start:end]
                yield Match("keyboard", start, end, token, _keyboard_guesses(token))


def _sequence_class(c: str):
    for low, high in (("a", "z"), ("A", "Z"), ("0", "9")):
        if low <= c <= high:
            return low
    return None


def _sequence_matches(text: str):
    for start in range(len(text) - 2):
        kind = _sequence_class(text[start])
        delta = ord(text[start + 1]) - ord(text[start])
        if kind is None or abs(delta) != 1:
            continue
        end = start + 1
        while (
            end < len(text)
            and _sequence_class(text[end]) == kind
            and ord(text[end]) - ord(text[end - 1]) == delta
        ):
            end += 1
            if end - start >= 3:
                token = text[start:end]
                base = 4 if token[0] in "aAzZ019" else 10 if kind == "0" else 26
                if delta < 0:
                    base *= 2
                yield Match("sequence", start, end, token, base * len(token))


def _year_matches(text: str):
    for found in re.finditer(r"(?=((?:19|20)\d\d))", text):
        start = found.start()
        token = found.group(1)
        guesses = max(abs(int(token) - REFERENCE_YEAR), 20)
        yield Match("year", start, start + 4, token, guesses)


def _repeat_matches(text: str, ranked: dict):
    unit_guesses = {}
    for start in range(len(text)):
        for size in range(1, (len(text) - start) // 2 + 1):
            unit = text[start:start + size]
            if (unit + unit).find(unit, 1) < size:
                continue
            count = 1
            while text[start + size * count:start + size * (count + 1)] == unit:
                count += 1
            if count >= 2 and size * count >= 3:
                if unit not in unit_guesses:
                    unit_guesses[unit] = _estimate(unit, ranked).guesses
                end = start + size * count
                yield Match("repeat", start, end, text[start:end], unit_guesses[unit] * count, unit)


def _cardinality(c: str) -> int:
    if "a" <= c <= "z" or "A" <= c <= "Z":
        return 26
    if "0" <= c <= "9":
        return 10
    if " " <= c <= "~":
        return 33
    return 100


def _bruteforce_matches(text: str):
    for start in range(len(text)):
        guesses = 1
        for end in range(start + 1, len(text) + 1):
            guesses *= _cardinality(text[end - 1])
            yield Match("bruteforce", start, end, text[start:end], guesses)


def _estimate(text: str, ranked: dict) -> Estimate:
    length = len(text)
    if length == 0:
        return Estimate(1, [])
    by_end = [[] for _ in range(length + 1)]
    for finder in (
        _dictionary_matches(text, ranked),
        _keyboard_matches(text),
        _sequence_matches(text),
        _year_matches(text),
        _repeat_matches(text, ranked),
        _bruteforce_matches(text),
    ):
        for match in finder:
            by_end[match.end].append(match)
    best = [{} for _ in range(length + 1)]
    best[0][0] = (1, [])
    for end in range(1, length + 1):
        for match in by_end[end]:
            guesses = match.guesses
            if match.end - match.start < length:
                guesses = max(guesses, 10 if len(match.token) == 1 else 50)
            for count, (product, chosen) in best[match.start].items():
                candidate = product * guesses
                current = best[end].get(count + 1)
                if current is None or candidate < current[0]:
                    best[end][count + 1] = (candidate, chosen + [match])
    guesses, matches = min(
        ((product * math.factorial(count), chosen) for count, (product, chosen) in best[length].items()),
        key=lambda option: option[0],
    )
    return Estimate(guesses, matches)


def estimate_guesses(password: str, common_passwords=None) -> Estimate:
    return _estimate(password[:MAX_ANALYSED_LENGTH], common_passwords or {})


def _strength(guesses: float) -> str:
    for minimum, label in LEVEL_THRESHOLDS:
        if guesses >= minimum:
            return label
    return "Very Weak"


def _duration(seconds: float) -> str:
    for size, unit, plural in (
        (3_155_760_000, "century", "centuries"), (31_557_600, "year", "years"),
        (86_400, "day", "days"), (3_600, "hour", "hours"), (60, "minute", "minutes"),
        (1, "second", "seconds"),
    ):
        if seconds >= size:
            amount = round(seconds / size)
            if plural == "centuries" and amount > 100:
                return "more than 100 centuries"
            return f"about {amount} {unit if amount == 1 else plural}"
    return "under a second"


def _describe(match: Match):
    if match.kind == "dictionary":
        if match.token.lower() == match.word:
            return f"'{match.token}' is on the common-passwords list."
        return f"'{match.token}' is the common password '{match.word}' with look-alike substitutions."
    if match.kind == "keyboard":
        return f"'{match.token}' is a keyboard pattern."
    if match.kind == "sequence":
        return f"'{match.token}' is an alphabetical or numeric sequence."
    if match.kind == "year":
        return f"'{match.token}' looks like a year."
    if match.kind == "repeat":
        return f"'{match.token}' is '{match.word}' repeated."
    return None


def check_password_strength(password: str, common_passwords=None) -> Assessment:
    estimate = estimate_guesses(password, common_passwords)
    strength = _strength(estimate.guesses)
    bits = math.log2(estimate.guesses)
    feedback = [text for text in map(_describe, estimate.matches) if text]
    feedback.append(f"Estimated guesses to crack: {estimate.guesses:.2g} (about {bits:.0f} bits).")
    feedback.append(
        f"Offline attack at {GUESSES_PER_SECOND:,} guesses per second: "
        f"{_duration(estimate.guesses / GUESSES_PER_SECOND)}."
    )
    if strength in ("Very Weak", "Weak", "Medium"):
        if len(feedback) > 2:
            feedback.append("Predictable patterns are tried first; a few random words beat clever substitutions.")
        else:
            feedback.append("Make it longer: each extra random character multiplies the guesses needed.")
    return Assessment(strength, estimate.guesses, bits, estimate.matches, feedback)


def main():
    if len(sys.argv) >= 2:
        common_file = sys.argv[1]
    else:
        common_file = Path(__file__).parent / "common_passwords.txt"
    common = load_common_passwords(common_file)

    try:
        password = input("Please enter your password: ")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(1)

    result = check_password_strength(password, common)

    print(f"Password: {password}")
    print(f"Strength: {result.strength}")
    print("Details:")
    for item in result.feedback:
        print(f"- {item}")


if __name__ == "__main__":
    main()
