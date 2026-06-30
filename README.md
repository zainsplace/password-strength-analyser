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

## Disclaimer

For educational purposes only. Always use strong, unique passwords and a password manager.

## License

MIT License - see the LICENSE file for details.
