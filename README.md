# CodeSentinel

A local-first security scanner for developers and students. Private development version - all scanning happens locally with no mandatory external dependencies.

## Overview

CodeSentinel is a security scanning tool that detects secrets and insecure configurations in your codebase. Built with a local-first philosophy, it runs entirely offline without requiring any cloud services or internet connection. Currently in private development.

## Features

- **Secret Detection**: Find API keys, tokens, passwords, and other sensitive data
- **Configuration Vulnerabilities**: Detect insecure settings and misconfigurations
- **Local-First Operation**: Works completely offline with no external dependencies
- **Multiple Output Formats**: Markdown and JSON reporting for different use cases
- **CI/CD Ready**: Exit codes and machine-readable output for automation
- **Extensible Rules**: Customizable rule system for specific security needs

## Installation

### From Source

```bash
git clone <private-repository-url>
cd codesentinel
pip install -e .
```

<!-- ### Using pip

```bash
pip install codesentinel
``` -->

## Quick Start

Scan a directory for security issues:

```bash
codesentinel scan /path/to/your/code
```

Generate JSON output for CI/CD integration:

```bash
codesentinel scan /path/to/your/code --format json --ci
```

## Usage

### Basic Scanning

```bash
# Scan current directory
codesentinel scan .

# Scan specific directory
codesentinel scan /path/to/project

# Scan single file
codesentinel scan config.py
```

### Advanced Options

```bash
# Generate JSON output
codesentinel scan . --format json

# Exclude patterns
codesentinel scan . --exclude "*.log" --exclude "tmp/*"

# CI mode (JSON only, strict exit codes)
codesentinel scan . --ci

# Show entropy scores
codesentinel scan . --show-entropy

# Exit with code 1 when issues found
codesentinel scan . --exit-on-findings

# Verbose logging
codesentinel scan . --verbose
```

### Exit Codes

- `0`: No security issues found
- `1`: Security issues detected
- `2`: Runtime error occurred
- `3`: Invalid arguments provided

## Project Structure

```
codesentinel/
├── src/
│   └── sentinel/
│       ├── cli/           # Command-line interface
│       ├── scanner/       # File scanning and rule engine
│       ├── rules/         # Security rules and patterns
│       ├── reporting/     # Output formatting
│       └── utils/         # Utility functions
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── memory-bank/          # Project context and decisions
├── pyproject.toml        # Project configuration
└── README.md
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone <private-repository-url>
cd codesentinel

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src
```

### Internal Development

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit for internal review

## Security Rules

### Secret Detection
- AWS Access Keys and Secret Keys
- GCP API Keys and Service Account Tokens
- Azure Secrets and Connection Strings
- Stripe API Keys
- JWT Tokens and Signing Secrets
- Private Keys (RSA, DSA, EC, OpenSSH)
- Hardcoded Passwords
- High-Entropy Strings
- API Keys in Environment Files

### Configuration Vulnerabilities
- DEBUG Mode Enabled (Flask/Django)
- Binding to All Interfaces (0.0.0.0)
- Weak Cryptographic Algorithms (MD5, SHA1)
- Default Credentials
- Missing Environment Variable Usage
- Unsecured TLS/SSL Configurations
- Insecure Configuration Literals

## Philosophy

CodeSentinel is built on three core principles:

1. **Local-First**: All scanning happens on your machine with no data sent to external services
2. **User-Controlled**: You decide if and when CodeSentinel connects to any external APIs or cloud services
3. **Sustainable Licensing**: During private development CodeSentinel is proprietary; pricing and licensing for any public release will be decided once the product is mature

## License

This project is currently proprietary and not licensed for public redistribution. All rights reserved.

## Support

<!-- - Documentation: [docs.codesentinel.dev](https://docs.codesentinel.dev)
- Issues: [GitHub Issues](https://github.com/codesentinel/codesentinel/issues)
- Discussions: [GitHub Discussions](https://github.com/codesentinel/codesentinel/discussions) -->
Internal use only.

## Roadmap

### Phase 1: CLI MVP (Current)
- Core scanning engine
- Secret and configuration detection
- Markdown and JSON reporting
- Basic rule system

### Phase 2: AI Explainer Mode
- Bring-your-own-LLM architecture
- Context-aware security explanations
- Risk assessment and prioritization

### Phase 3: GUI
- Cross-platform desktop application
- Real-time scanning visualization
- Interactive results dashboard

### Phase 4: Cloud Dashboard (Optional)
- Team collaboration features
- Historical trend analysis
- Compliance reporting