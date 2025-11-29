# CodeSentinel

[![Version](https://img.shields.io/badge/version-v0.2.0--internal-blue.svg)](https://github.com/ThatOneRomanian/codesentinel)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

A local-first security scanner for developers and students. Private development version - all scanning happens locally with no mandatory external dependencies.

> © 2025 Andrei Antonescu. All rights reserved.
> Proprietary – not licensed for public redistribution.

## 90-Second Quickstart

Get started with CodeSentinel in 3 commands:

```bash
# 1. Install from source
pip install -e .

# 2. Basic security scan
codesentinel scan sample-project/

# 3. AI-powered scan (if configured)
DEEPSEEK_API_KEY=your_key codesentinel scan sample-project/ --ai
```

## What CodeSentinel Does

- **Secret Detection**: Find API keys, tokens, passwords, and other sensitive data
- **Configuration Vulnerabilities**: Detect insecure settings and misconfigurations  
- **Local-First Operation**: Works completely offline with no external dependencies
- **Multiple Output Formats**: Markdown and JSON reporting for different use cases
- **CI/CD Ready**: Exit codes and machine-readable output for automation
- **Extensible Rules**: Customizable rule system for specific security needs
- **AI Explainer Mode**: Bring-your-own-LLM security analysis and remediation guidance

## What CodeSentinel Does NOT Do Yet

- **Full SAST**: Not a complete static application security testing tool
- **Dependency Scanning**: Doesn't analyze package dependencies or supply chain
- **Cloud Service**: No mandatory cloud connectivity or data uploads
- **GUI Interface**: Currently command-line only (GUI planned for Phase 3)
- **Advanced Analysis**: Limited to configured rule packs (expanding in future)

## Overview

CodeSentinel is a security scanning tool that detects secrets and insecure configurations in your codebase. Built with a local-first philosophy, it runs entirely offline without requiring any cloud services or internet connection. Currently in private development.

## Features

- **Secret Detection**: Find API keys, tokens, passwords, and other sensitive data
- **Configuration Vulnerabilities**: Detect insecure settings and misconfigurations
- **Local-First Operation**: Works completely offline with no external dependencies
- **Multiple Output Formats**: Markdown and JSON reporting for different use cases
- **CI/CD Ready**: Exit codes and machine-readable output for automation
- **Extensible Rules**: Customizable rule system for specific security needs
- **AI Explainer Mode**: Bring-your-own-LLM security analysis and remediation guidance

## Installation

### From Source

```bash
# Clone the repository
git clone <private-repository-url>
cd codesentinel

# Install in development mode
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

## Refined AI Explainer Mode

CodeSentinel's AI features follow a strict local-first, BYO-LLM philosophy:

### DeepSeek Configuration

```bash
# Set your DeepSeek API key
export DEEPSEEK_API_KEY=your_api_key_here

# Run AI-powered security analysis
codesentinel scan . --ai --llm-provider deepseek
```

### AI Fallback Behavior

When no API key is configured:
- AI features gracefully fall back to standard scanning
- No errors or interruptions to the scanning process
- All core security detection continues to work
- User receives clear notification about missing configuration

### Available LLM Providers

- `deepseek` - DeepSeek API (default, most cost-effective)
- `openai` - OpenAI API (alternative option)
- `local_ollama` - Local Ollama models (fully offline)

## Usage

### Basic Commands

```bash
# Show version information
codesentinel version

# Scan current directory (default: markdown format)
codesentinel scan .

# Scan specific directory
codesentinel scan /path/to/project

# Scan single file
codesentinel scan config.py

# Generate JSON output
codesentinel scan . --format json

# Enable AI explanations (Phase 2)
codesentinel scan . --ai

# Enable AI explanations with specific provider
codesentinel scan . --ai --llm-provider deepseek

# Generate detailed explanations for findings
codesentinel scan . --explain
```

### Example Output

**Markdown Format:**
```markdown
# CodeSentinel Security Scan Report

## Scan Summary
- **Total Findings**: 2
- **High Severity**: 1
- **Medium Severity**: 1
- **Low Severity**: 0

## High Severity Findings

### Finding 1
- **Rule**: hardcoded-api-key
- **File**: `config.py`
- **Line**: 15
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  api_key = "AKIAIOSFODNN7EXAMPLE"
  ```
```

**JSON Format (with AI enhancements):**
```json
{
  "scan_summary": {
    "total_findings": 2,
    "by_severity": {
      "high": 1,
      "medium": 1,
      "low": 0
    }
  },
  "findings": [
    {
      "rule_id": "hardcoded-api-key",
      "file_path": "config.py",
      "line": 15,
      "severity": "high",
      "excerpt": "api_key = \"AKIAIOSFODNN7EXAMPLE\"",
      "confidence": 0.8,
      "cwe_id": "CWE-798",
      "remediation": "Rotate the exposed AWS access key immediately...",
      "risk_score": 8.5,
      "references": ["https://cwe.mitre.org/data/definitions/798.html"]
    }
  ]
}
```

### Exit Codes

- `0`: No security issues found
- `1`: Security issues detected
- `2`: Runtime error occurred

## Project Structure

```
codesentinel/
├── src/
│   └── sentinel/
│       ├── cli/           # Command-line interface
│       ├── scanner/       # File scanning and rule engine
│       ├── rules/         # Security rules and patterns
│       ├── reporting/     # Output formatting (Markdown/JSON)
│       ├── utils/         # Utility functions (entropy, patterns)
│       └── llm/           # AI explainer mode (Phase 2)
│           ├── provider.py     # LLM provider abstraction
│           ├── explainer.py    # Explanation engine
│           └── prompts/        # AI prompt templates
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── memory-bank/          # Project context and decisions
├── sample-project/       # Test project with fake credentials
├── pyproject.toml        # Project configuration
└── README.md
```

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
- Generic API Keys and Tokens

### Configuration Vulnerabilities
- Hardcoded Database Credentials
- Hardcoded API Keys and Tokens
- Insecure Connection Strings
- Plaintext Credentials in Configuration
### Rule Packs and Validation

CodeSentinel uses a modular rule pack system with strict validation:

- **Plugin Architecture**: Rules are dynamically loaded from rule packs
- **Validation**: All rules are validated for required attributes (id, description, severity, apply method)
- **Abstract Class Protection**: The engine safely handles abstract classes and protocols
- **Error Resilience**: Invalid rules are skipped with detailed logging
- **Backward Compatibility**: Existing rules continue to work without modification

**Available Rule Packs:**
- **Core Rules**: Secret detection and configuration vulnerabilities
- **Docker Security**: Future rule pack for container security
- **GitHub Actions**: Future rule pack for CI/CD security
- **JavaScript Supply Chain**: Future rule pack for npm/dependency security

**Rule Validation Features:**
- Prevents abstract class instantiation errors
- Validates required attributes and methods
- Checks for non-empty rule metadata
- Handles import errors gracefully
- Maintains engine stability with invalid rules

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

# Linting
flake8 src tests
```

### Internal Development Process

1. Create a feature branch
2. Make your changes following the project patterns
3. Add tests for new functionality
4. Ensure all tests pass
5. Update memory bank documentation
6. Submit for internal review

### Code Standards

- **Python 3.8+** compatibility
- **Type hints** for all public functions
- **Google-style docstrings** with Args/Returns/Raises
- **Black** formatting with 88 character line length
- **Absolute imports** for module clarity
- **Comprehensive test coverage** with pytest

## Philosophy

CodeSentinel is built on three core principles:

1. **Local-First**: All scanning happens on your machine with no data sent to external services
2. **User-Controlled**: You decide if and when CodeSentinel connects to any external APIs or cloud services
3. **Sustainable Licensing**: During private development CodeSentinel is proprietary; pricing and licensing for any public release will be decided once the product is mature

## Memory Bank Development

This project uses a memory bank system to maintain context and decision history. Key files:

- `memory-bank/productContext.md`: High-level project goals and architecture
- `memory-bank/systemPatterns.md`: Development patterns and standards
- `memory-bank/decisionLog.md`: Architectural decisions and rationale
- `memory-bank/activeContext.md`: Current focus and recent changes
- `memory-bank/progress.md`: Task tracking and milestones

## License

This project is currently proprietary and not licensed for public redistribution. All rights reserved.

© 2025 Andrei Antonescu. All rights reserved.

## Support

Internal use only.

## Roadmap

### ✅ Phase 1: CLI MVP (Completed)
- ✅ Core scanning engine with file walker
- ✅ Secret and configuration detection rules
- ✅ Markdown and JSON reporting formats
- ✅ Plugin-style rule architecture
- ✅ Comprehensive test suite
- ✅ Packaging and installation system

### ✅ Phase 2: AI Explainer Mode (Completed)
- ✅ Bring-your-own-LLM architecture
- ✅ LLM provider abstraction layer
- ✅ Explanation engine with prompt templates
- ✅ Enhanced finding data structure (CWE, risk_score, references)
- ✅ CLI integration with --ai and --explain flags
- ✅ Comprehensive test coverage for all components
- ✅ DeepSeek integration with graceful fallback

### 📋 Phase 3: GUI
- 📋 Cross-platform desktop application
- 📋 Real-time scanning visualization
- 📋 Interactive results dashboard

### 🔮 Phase 4: Cloud Dashboard (Optional)
- 🔮 Team collaboration features
- 🔮 Historical trend analysis
- 🔮 Compliance reporting