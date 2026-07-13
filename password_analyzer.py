#!/usr/bin/env python3

import re
import sys
import math
from collections import Counter
from pathlib import Path


def shannon_entropy(password: str) -> float:
    if not password:
        return 0.0
    counts = Counter(password)
    length = len(password)
    entropy_per_symbol = 0.0
    for count in counts.values():
        p = count / length
        entropy_per_symbol -= p * math.log2(p)
    return entropy_per_symbol * length


def load_common_passwords(path: str):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


SCORE_LEVELS = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4}

ENTROPY_LEVEL_THRESHOLDS = (
    (60.0, 4),
    (45.0, 3),
    (36.0, 2),
    (28.0, 1),
)


def _score_to_level(score: int) -> int:
    return SCORE_LEVELS[min(score, max(SCORE_LEVELS))]


def _entropy_to_level(bits: float) -> int:
    for minimum_bits, level in ENTROPY_LEVEL_THRESHOLDS:
        if bits >= minimum_bits:
            return level
    return 0


def _level_to_label(level: int) -> str:
    return {
        4: "Very Strong",
        3: "Strong",
        2: "Medium",
        1: "Weak",
        0: "Very Weak",
    }[level]


def check_password_strength(password: str, common_passwords=None):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long.")

    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Include at least one uppercase letter.")

    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Include at least one lowercase letter.")

    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Include at least one digit.")

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Include at least one special character (e.g., !@#$%^&*).")

    entropy_bits = shannon_entropy(password)

    in_common = False
    if common_passwords:
        if password in common_passwords:
            in_common = True
            feedback.append("This password is in the common-passwords list.")

    if in_common:
        final_level = 0
    else:
        score_level = _score_to_level(score)
        entropy_level = _entropy_to_level(entropy_bits)
        lowest_level_entropy_may_impose = score_level - 1
        final_level = min(score_level, max(entropy_level, lowest_level_entropy_may_impose))

    strength = _level_to_label(final_level)

    feedback.append(f"Estimated entropy: {entropy_bits:.1f} bits.")

    return score, strength, feedback


def main():
    common_file = None
    common_set = set()
    if len(sys.argv) >= 2:
        common_file = sys.argv[1]
    else:
        default_path = Path(__file__).parent / 'common_passwords.txt'
        if default_path.exists():
            common_file = str(default_path)

    if common_file:
        common_set = load_common_passwords(common_file)

    try:
        password = input("Please enter your password: ")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(1)

    score, strength, feedback = check_password_strength(password, common_set)

    print(f"Password: {password}")
    print(f"Strength: {strength} (Score: {score}/5)")

    if feedback:
        print("Details:")
        for item in feedback:
            print(f"- {item}")
    else:
        print("Your password is strong!")


if __name__ == "__main__":
    main()
