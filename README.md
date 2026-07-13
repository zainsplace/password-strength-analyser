# Password Strength Analyzer

A simple Python tool that evaluates password strength using common security criteria and Shannon entropy.

## Features

- Minimum 8 characters, uppercase, lowercase, digit, and special character checks
- Shannon entropy estimation (bits)
- Optional common-passwords list check
- Score-based rating (Very Weak → Very Strong), with entropy able to reduce the rating by at most one level

## Usage

```bash
python password_analyzer.py [common_passwords_file]
```

## Example Output

```
Please enter your password: Zx!9mK#pQ2@nR5$v
Password: Zx!9mK#pQ2@nR5$v
Strength: Very Strong (Score: 5/5)
Details:
- Estimated entropy: 64.0 bits.
```

```
Please enter your password: hello
Password: hello
Strength: Very Weak (Score: 1/5)
Details:
- Password should be at least 8 characters long.
- Include at least one uppercase letter.
- Include at least one digit.
- Include at least one special character (e.g., !@#$%^&*).
- Estimated entropy: 9.6 bits.
```

## How the Rating Works

The score counts how many of the five composition checks pass. Scores 0-1
map to Very Weak, then each extra point moves the rating up one level.

Shannon entropy acts as a sanity check on top of the score: a password that
passes the composition checks but has repetitive content can be dragged down
by one level, though never boosted. The entropy boundaries (28, 36, 45 and
60 bits) follow the commonly used crack-resistance scale where anything
under 28 bits is trivially guessable, 28-35 bits resists only casual
guessing, 36-59 bits is reasonable for online accounts, and 60+ bits holds
up against offline attacks.

## Disclaimer

For educational purposes only. Always use strong, unique passwords and a password manager.

## License

MIT License - see the LICENSE file for details.
