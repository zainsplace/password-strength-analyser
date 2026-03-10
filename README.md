# Password Strength Analyzer

A simple Python tool to evaluate the strength of passwords based on common security criteria.

## Features

- Checks password length (minimum 8 characters)
- Verifies presence of uppercase and lowercase letters
- Ensures digits and special characters are included
- Provides a strength score and improvement suggestions

## Disclaimer

This tool is for educational purposes only. It does not guarantee password security against all threats. Always use strong, unique passwords and consider using a password manager.

## Installation

1. Ensure Python 3 is installed on your system.
2. Download or clone this repository.

## Usage

Run the script from the command line:

```bash
python password_analyzer.py "YourPasswordHere"
```

Example:

```bash
python password_analyzer.py "P@ssw0rd123"
```

Output:

```
Password: P@ssw0rd123
Strength: Very Strong (Score: 5/5)
Your password is strong!
```

## Contributing

Feel free to submit issues or pull requests to improve this tool.

## License

This project is licensed under the MIT License - see the LICENSE file for details.