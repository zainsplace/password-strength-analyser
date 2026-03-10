#!/usr/bin/env python3

import re
import sys

def check_password_strength(password):

    score = 0
    feedback = []

    if len(password) >= 6:
        score += 1
    else:
        feedback.append("Password should be at least 6 characters long.")

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