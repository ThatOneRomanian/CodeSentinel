# CodeSentinel Sample Project

This project contains fake credentials, insecure configurations, and various security anti-patterns for testing CodeSentinel scanner functionality.

**WARNING**: This project contains intentionally insecure code and fake credentials for testing purposes only. Do not use in production.

## Test Cases Included

- Hardcoded API keys and tokens
- Database connection strings with credentials
- Private keys and certificates
- Insecure configurations
- Various file types for language detection testing

## Usage

```bash
# Scan this project with CodeSentinel
codesentinel scan . --format json
codesentinel scan . --format markdown
```

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.