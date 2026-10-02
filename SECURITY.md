# Security Policy

LastLight-Voice is early-stage software. Please report security-sensitive issues privately through GitHub's security reporting features when available rather than publishing exploit details in a public issue.

Areas of particular interest include:

- unsafe subprocess execution;
- path traversal or unsafe temporary-file handling;
- unexpected network access;
- malicious or malformed future model/voice-pack files;
- command injection;
- unsafe archive handling.

The project aims to avoid `shell=True`, silent downloads, and runtime network dependencies. These design goals reduce attack surface but are not a security guarantee.
