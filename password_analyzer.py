#!/usr/bin/env python3
"""
Password Strength Analyzer
A simple tool to evaluate the strength of a password based on common security criteria.
"""

import re
import sys

def check_password_strength(password):
    """
    Evaluates the strength of a password.

    Criteria:
    - Length: At least 8 characters
    - Uppercase letter
    - Lowercase letter
    - Digit
    - Special character

    Returns:
    - Strength score (0-5)
    - Feedback message
    """
    score = 0
    feedback = []

    # Check length
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long.")

    # Check for uppercase
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Include at least one uppercase letter.")

    # Check for lowercase
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Include at least one lowercase letter.")

    # Check for digit
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Include at least one digit.")

    # Check for special character
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Include at least one special character (e.g., !@#$%^&*).")

    # Determine strength level
    if score == 5:
        strength = "Very Strong"
    elif score == 4:
        strength = "Strong"
    elif score == 3:
        strength = "Medium"
    elif score == 2:
        strength = "Weak"
    else:
        strength = "Very Weak"

    return score, strength, feedback

def main():
    if len(sys.argv) != 2:
        print("Usage: python password_analyzer.py <password>")
        sys.exit(1)

    password = sys.argv[1]
    score, strength, feedback = check_password_strength(password)

    print(f"Password: {password}")
    print(f"Strength: {strength} (Score: {score}/5)")

    if feedback:
        print("Suggestions to improve:")
        for item in feedback:
            print(f"- {item}")
    else:
        print("Your password is strong!")

if __name__ == "__main__":
    main()