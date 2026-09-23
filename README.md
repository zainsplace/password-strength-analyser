# Password Strength Analyzer

Estimates how many guesses an attacker needs to crack a password, then rates it
against a stated attack model. It looks for the patterns real cracking tools try
first: common passwords, look-alike substitutions, keyboard walks, sequences,
repeats and years.

## Why the first version was wrong

The first version of this tool scored passwords with Shannon entropy over their
characters plus composition rules (length, upper, lower, digit, symbol). That
measures how varied the characters are, not how guessable the password is. Here
is what it said about some well-known passwords, next to what the current
version says:

| Password | Old: entropy | Old rating | New: estimated guesses | New rating |
| --- | ---: | --- | ---: | --- |
| `P@ssw0rd` | 22.0 bits | Strong | 16 | Very Weak |
| `Password1!` | 31.2 bits | Strong | 3.3e3 | Very Weak |
| `Qwertyuiop123!` | 53.3 bits | Strong | 3.8e7 | Weak |
| `1qaz2wsx3edc4rfv!Q` | 75.1 bits | Very Strong | 5.4e11 | Medium |
| `correct horse battery staple` | 97.9 bits | Weak | 8.5e39 | Very Strong |
| `abcdefghijklmnopqrstuvwxyz` | 122.2 bits | Weak | 1.0e2 | Very Weak |
| `Zx!9mK#pQ2@nR5$v` | 64.0 bits | Very Strong | 6.4e21 | Very Strong |

The old approach rewarded short dictionary words with symbols swapped in and
punished long passphrases, which is the pattern NIST SP 800-63B moved away from
when it dropped composition rules. An attacker does not try `P@ssw0rd` as eight
random characters. They try `password` and then its common substitutions.

## How the estimate works

1. **Find every pattern in the password.** Each match gets a guess count:
   - Common passwords from `common_passwords.txt`, ranked by position in the
     list. Capital letters and look-alike substitutions (`@` for `a`, `0` for
     `o` and so on) multiply the rank by the number of variations an attacker
     would try.
   - Keyboard walks on a US QWERTY layout, including shifted keys. The count
     grows with length and with the number of turns in the walk.
   - Alphabetical and numeric sequences such as `abcdef` or `987654`.
   - Repeats such as `aaaa` or `abcabc`, costed as the repeated unit times the
     number of repeats.
   - Years from 1900 to 2099, costed by distance from the current year.
   - Brute force for anything else, at 26 guesses per letter, 10 per digit and
     33 per symbol.
2. **Pick the cheapest way to build the whole password from those matches.**
   Dynamic programming over the password finds the split that needs the fewest
   guesses in total. The total is multiplied by the number of ways those pieces
   can be ordered, so gluing patterns together is not free.
3. **Rate the result.** The scale assumes an offline attack on a slow password
   hash at 10,000 guesses per second:

| Rating | Guesses | Time at 10,000 guesses per second |
| --- | --- | --- |
| Very Weak | under 10^6 | under 2 minutes |
| Weak | 10^6 to 10^9 | under a day |
| Medium | 10^9 to 10^12 | under 3 years |
| Strong | 10^12 to 10^15 | under 3,000 years |
| Very Strong | 10^15 or more | longer |

The pattern-matching approach follows zxcvbn (Wheeler, USENIX Security 2016).
This is my own smaller implementation, written to understand how it works.

## Limitations

- **The dictionary is small.** `common_passwords.txt` holds about 100 entries and
  there is no English word list. `Tr0ub4dor&3` rates Strong because `troubador`
  is not in the dictionary, even though it is a single word with substitutions.
  Pass a bigger list as the first argument to improve this.
- **Passphrases score well because they are long, not because of the words.**
  `correct horse battery staple` is costed as 28 random characters. A real
  attacker combining dictionary words would need far fewer guesses than 10^39.
  Four random words from a 10,000-word list is closer to 10^16.
- **The attacker is assumed to know which patterns you used.** Picking the
  cheapest split is deliberately pessimistic, so estimates lean low for
  passwords made from several patterns.
- **US QWERTY only.** Walks on other layouts are costed as brute force.
- **Only the first 64 characters are analysed.** Characters after that are
  ignored, which can only make the estimate lower.

## Usage

```bash
python password_analyzer.py [common_passwords_file]
```

## Example Output

```
Please enter your password: Qwertyuiop123!
Password: Qwertyuiop123!
Strength: Weak
Details:
- 'Qwertyuiop' is a keyboard pattern.
- '123' is an alphabetical or numeric sequence.
- Estimated guesses to crack: 3.8e+07 (about 25 bits).
- Offline attack at 10,000 guesses per second: about 1 hour.
- Predictable patterns are tried first; a few random words beat clever substitutions.
```

```
Please enter your password: P@ssw0rd
Password: P@ssw0rd
Strength: Very Weak
Details:
- 'P@ssw0rd' is the common password 'password' with look-alike substitutions.
- Estimated guesses to crack: 16 (about 4 bits).
- Offline attack at 10,000 guesses per second: under a second.
- Predictable patterns are tried first; a few random words beat clever substitutions.
```

## Disclaimer

For educational purposes only. Always use strong, unique passwords and a password manager.

## License

MIT License - see the LICENSE file for details.
