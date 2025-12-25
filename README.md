# CodeSentinel

[![Version](https://img.shields.io/badge/version-v0.2.0-blue.svg)](https://github.com/ThatOneRomanian/codesentinel)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![GitHub Stars](https://img.shields.io/github/stars/ThatOneRomanian/codesentinel?style=social)](https://github.com/ThatOneRomanian/codesentinel/stargazers)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/ThatOneRomanian?logo=github&style=flat)](https://github.com/sponsors/ThatOneRomanian)

A local-first security scanner for developers and students. All scanning happens locally with no mandatory external dependencies.

> © 2025 Andrei Antonescu. Released under the MIT License.

## 90-Second Quickstart

Get started with CodeSentinel in 3 commands:

```bash
# 1. Install from PyPI
pip install codesentinel

# 2. Basic security scan
codesentinel scan sample-project/

# 3. AI-powered scan (if configured)
DEEPSEEK_API_KEY=your_key codesentinel scan sample-project/ --ai
```

## What CodeSentinel Does

- **Secret Detection**: Find API keys, tokens, passwords, and other sensitive data
- **Configuration Vulnerabilities**: Detect insecure settings and misconfigurations
- **Specialized Misconfiguration Scanning**: Structure-aware analysis of IaC, CI/CD, and Containers (Phase 2.7)
- **Local-First Operation**: Works completely offline with no external dependencies
- **Multiple Output Formats**: Markdown and JSON reporting for different use cases
- **CI/CD Ready**: Exit codes and machine-readable output for automation
- **Extensible Rules**: Customizable rule system for specific security needs
- **AI Explainer Mode**: Bring-your-own-LLM security analysis and remediation guidance
- **Provider-Aware Detection**: Intelligent deduplication with provider-specific precedence (Phase 2.5)
- **Reduced Noise**: 67.8% duplicate reduction through advanced token classification

## Phase 3 GUI Development

Phase 3 GUI is now in development! For early access to the web-based interface:

```bash
# Quick start (2 minutes)
./setup-gui.sh

# Terminal 1: Backend API
python -m sentinel.api.fastapi_bridge

# Terminal 2: Frontend
cd gui && npm run dev

# Open http://localhost:3000
```

See [QUICK_START.md](QUICK_START.md) for fast setup and [docs/GUI_DEVELOPMENT.md](docs/GUI_DEVELOPMENT.md) for full documentation.

## What CodeSentinel Does NOT Do Yet

- **Full SAST**: Not a complete static application security testing tool
- **Advanced Analysis**: Limited to configured rule packs (expanding in future)
- **Cloud Service**: No mandatory cloud connectivity or data uploads

## Overview

CodeSentinel is a security scanning tool that detects secrets, insecure configurations, and structural misconfigurations in your codebase. Built with a local-first philosophy, it runs entirely offline without requiring any cloud services or internet connection.

## Features

- **Secret Detection**: Find API keys, tokens, passwords, and other sensitive data
- **Configuration Vulnerabilities**: Detect insecure settings and misconfigurations
- **Structure-Aware Scanning (New)**: Specialized rule packs for:
    - **Containers**: Dockerfile security best practices (e.g., USER root, hardcoded secrets)
    - **CI/CD**: GitHub Actions workflow misconfigurations (e.g., overly permissive tokens)
    - **IaC**: Terraform security policies (e.g., public S3 buckets, unencrypted state)
    - **Supply Chain**: NodeJS malicious scripts and permissive dependency versions
- **Local-First Operation**: Works completely offline with no external dependencies
- **Multiple Output Formats**: Markdown and JSON reporting for different use cases
- **CI/CD Ready**: Exit codes and machine-readable output for automation
- **Extensible Rules**: Customizable rule system for specific security needs
- **AI Explainer Mode**: Bring-your-own-LLM security analysis and remediation guidance
- **Provider-Aware Secret Detection**: Intelligent classification of tokens by provider (AWS, Azure, GCP, etc.)
- **Advanced Deduplication**: 67.8% duplicate reduction with precedence-based finding selection
- **Reduced False Positives**: Token type classification prevents rule collisions and over-matching

## Installation

### From PyPI

```bash
pip install codesentinel
```

### From Source

```bash
# Clone the repository
git clone https://github.com/ThatOneRomanian/codesentinel.git
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
│       │   ├── token_types.py  # Token classification (Phase 2.5)
│       │   ├── secrets.py      # Secret detection rules
│       │   ├── configs.py      # Configuration vulnerability rules
│       │   ├── docker/         # Dockerfile security rules (Phase 2.7)
│       │   ├── gh_actions/     # GitHub Actions security rules (Phase 2.7)
│       │   ├── js_supply_chain/ # NodeJS supply chain rules (Phase 2.7)
│       │   └── terraform/      # Terraform IaC security rules (Phase 2.7)
│       ├── reporting/     # Output formatting (Markdown/JSON)
│       ├── utils/         # Utility functions (entropy, patterns, parsers)
│       └── llm/           # AI explainer mode (Phase 2)
│           ├── provider.py     # LLM provider abstraction
│           ├── explainer.py    # Explanation engine
│           └── prompts/        # AI prompt templates
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
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

### Specialized Misconfiguration Rules (Phase 2.7)
- **Container Security**: Detects `USER root`, hardcoded secrets in `ENV`.
- **CI/CD Security**: Detects overly permissive GITHUB_TOKEN scope, insecure output commands.
- **Supply Chain**: Detects malicious `package.json` scripts, wildcard dependencies.
- **IaC Security**: Detects publicly exposed S3 buckets, unencrypted Terraform remote state.

### Rule Packs and Validation

CodeSentinel uses a modular rule pack system with strict validation:

- **Plugin Architecture**: Rules are dynamically loaded from rule packs
- **Validation**: All rules are validated for required attributes (id, description, severity, apply method)
- **Abstract Class Protection**: The engine safely handles abstract classes and protocols
- **Error Resilience**: Invalid rules are skipped with detailed logging
- **Backward Compatibility**: Existing rules continue to work without modification

**Available Rule Packs:**
- **Core Rules**: Secret detection and generic configuration vulnerabilities
- **Docker Security**: Container security rules
- **GitHub Actions**: CI/CD security rules
- **JS Supply Chain**: NodeJS dependency security rules
- **Terraform IaC**: Infrastructure-as-Code security rules

**Rule Validation Features:**
- Prevents abstract class instantiation errors
- Validates required attributes and methods
- Checks for non-empty rule metadata
- Handles import errors gracefully
- Maintains engine stability with invalid rules

## Phase 2.5 Rule Hardening Improvements

### Provider-Aware Secret Detection with De-duplication

CodeSentinel now includes advanced token classification and deduplication logic to reduce noise and improve accuracy:

**Key Improvements:**
- **67.8% duplicate reduction**: Sample project findings reduced from 152+ to 49 unique findings
- **Provider-aware classification**: Tokens are classified by provider (AWS, Azure, GCP, Stripe, etc.)
- **Precedence model**: Provider-specific tokens receive highest priority in deduplication
- **Rule collision resolution**: 12 tokens previously triggering 3+ rules now produce single finding
- **Enhanced JWT/PEM detection**: Improved detection of partially obfuscated tokens

**Technical Implementation:**
- **Token Type Classification**: New [`token_types.py`](src/sentinel/rules/token_types.py) module for provider-aware classification
- **Deduplication Engine**: Enhanced Rule Engine with precedence-based finding selection
- **Precedence Hierarchy**: Provider-specific (100) > OAuth tokens (90) > generic API keys (80) > specialized misconfigurations (65) > high-entropy strings (70) > generic configuration rules (60)
- **Backward Compatibility**: Zero breaking changes to existing API and functionality

**Validation Results:**
- **Sample Project**: 49 findings vs 152+ previously (67.8% reduction)
- **Azure Rule Fixes**: Resolved over-matching issues in Azure secret detection
- **Performance**: Consistent runtime with enhanced accuracy
- **Test Coverage**: 236/236 tests passing with comprehensive deduplication testing

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ThatOneRomanian/codesentinel.git
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

### Code Standards

- **Python 3.8+** compatibility
- **Type hints** for all public functions
- **Google-style docstrings** with Args/Returns/Raises
- **Black** formatting with 88 character line length
- **Absolute imports** for module clarity
- **Comprehensive test coverage** with pytest

## Dogfooding Runner

CodeSentinel includes an automated dogfooding runner for systematic testing and validation of the scanner across multiple scenarios. This development tool helps ensure consistent performance and quality.

### Usage

```bash
# Basic dogfooding run against sample project
python tools/dogfood_runner.py --target ./sample-project

# Run with AI scenarios enabled (requires DEEPSEEK_API_KEY)
python tools/dogfood_runner.py --target ./sample-project --ai

# Run with custom output directory and verbose logging
python tools/dogfood_runner.py --target ./sample-project --out-dir ./my-results --verbose

# Run with specific timeout per scenario
python tools/dogfood_runner.py --target ./sample-project --timeout 600
```

### Scenarios

The dogfooding runner executes 7 scenarios:

1. **S1**: Baseline Markdown Scan - `codesentinel scan TARGET --format markdown`
2. **S2**: JSON Format Scan - `codesentinel scan TARGET --format json`
3. **S3**: JSON + CI Mode Scan - `codesentinel scan TARGET --ci --format json`
4. **S4**: AI + JSON Scan - `codesentinel scan TARGET --ai --llm-provider PROVIDER --format json` (conditional)
5. **S5**: AI + Markdown Scan - `codesentinel scan TARGET --ai --llm-provider PROVIDER --format markdown` (conditional)
6. **S6**: Single File Scan - `codesentinel scan FILE --format markdown`
7. **S7**: Scan with Gitignore Patterns - `codesentinel scan TARGET --format json`

### Output Structure

```
dogfood-results/
├── sample-project-20241129_123456/
│   ├── summary.md                 # Comprehensive run summary
│   ├── metadata.json              # Run metadata and configuration
│   ├── scenario1/                 # S1: Baseline markdown
│   │   ├── command.txt            # Exact command executed
│   │   ├── output.md              # Scan output
│   │   ├── exit_code.txt          # Exit code
│   │   └── runtime.txt            # Execution time
│   ├── scenario2/                 # S2: JSON format
│   │   ├── command.txt
│   │   ├── output.json
│   │   ├── exit_code.txt
│   │   └── runtime.txt
│   └── ... (scenario directories 3-7)
└── latest -> sample-project-20241129_123456/  # Symlink to latest run
```

### Features

- **Dependency-Free**: Uses only Python standard library
- **Comprehensive Logging**: Detailed execution logs with timestamps
- **Error Handling**: Graceful failure with scenario isolation
- **Performance Tracking**: Runtime and exit code monitoring
- **Structured Output**: Consistent directory hierarchy with metadata
- **AI Integration**: Conditional AI scenario execution

### Notes

- This is a development tool only, not intended for production use
- Output directories are automatically excluded via `.gitignore`
- AI scenarios require `DEEPSEEK_API_KEY` environment variable
- Results are timestamped for easy comparison across runs

## Philosophy

CodeSentinel is built on three core principles:

1. **Local-First**: All scanning happens on your machine with no data sent to external services
2. **User-Controlled**: You decide if and when CodeSentinel connects to any external APIs or cloud services
3. **Open Source**: CodeSentinel is released under the MIT license, making it freely available for anyone to use, modify, and contribute to

## Contributing

We welcome contributions from the community! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

### Ways to Contribute

- Report bugs and suggest features through [GitHub Issues](https://github.com/ThatOneRomanian/codesentinel/issues)
- Improve documentation
- Add new security rules
- Enhance existing functionality
- Add support for new languages or frameworks
- Help with testing and quality assurance

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Community Support

Get help and connect with other users:

- [GitHub Issues](https://github.com/ThatOneRomanian/codesentinel/issues) for bug reports and feature requests
- [GitHub Discussions](https://github.com/ThatOneRomanian/codesentinel/discussions) for questions and community discussions
- [Stack Overflow](https://stackoverflow.com/questions/tagged/codesentinel) with the `codesentinel` tag

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

### 📖 Quick Links
- **[Documentation Index](docs/README.md)** - Complete navigation guide to all documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and component overview
- **[Specifications](docs/specs/)** - Phase specifications and requirements
  - Phase 1: Core scanning engine
  - Phase 2: AI integration
  - Phase 2 Finalization: Completion details
  - Phase 3: GUI development and API freeze
- **[API Documentation](docs/api/api-freeze-spec.md)** - Frozen API contract for GUI development
- **[Design Documents](docs/design/)** - In-depth design analysis and solutions
  - Phase 2.6 Gap Analysis: Rule blindspots in real-world repos
  - Phase 2.6 Validation Report: Testing against sample projects
  - Phase 2.7 Rule Pack Design: Structure-aware scanning specifications
- **[Implementation Guides](docs/guides/)** - Developer guides and technical notes
  - Rule Hardening: Advanced deduplication patterns
  - Dogfooding Experiment Plan: Automated testing strategy

### 📂 Documentation Structure
```
docs/
├── README.md                    # Documentation index (start here!)
├── ARCHITECTURE.md              # System design overview
├── specs/                       # Phase specifications
├── api/                         # API documentation
├── design/                      # Design documents & analysis
├── guides/                      # Implementation guides
└── examples/                    # Sample outputs
```

### For Contributors
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards
- **[Security Policy](SECURITY.md)** - Vulnerability reporting
- **[AI Guidelines](.github/copilot-instructions.md)** - For AI-assisted development

## Support the Project

If you find CodeSentinel useful, consider supporting its development:

- ⭐ Star the project on GitHub
- 🐞 Report bugs and contribute fixes
- 📚 Improve documentation
- 💻 Contribute code and new features
- 💖 [Sponsor the project](https://github.com/sponsors/ThatOneRomanian) through GitHub Sponsors

## Acknowledgments

We'd like to thank all contributors who have helped make CodeSentinel better, as well as the open-source security community whose tools and research have inspired this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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

### ✅ Phase 2.5: Rule Hardening (Completed)
- ✅ Provider-aware token classification system
- ✅ Advanced deduplication with precedence model
- ✅ 67.8% duplicate reduction in sample project
- ✅ Azure rule over-matching resolution
- ✅ Enhanced JWT/PEM detection and partial obfuscation handling
- ✅ Comprehensive dogfooding validation
- ✅ Zero breaking changes to existing API

### ✅ Phase 2.7: Rule Pack Expansion (Completed)
- ✅ Implemented Structure-Aware Parsers (Dockerfile, YAML, HCL)
- ✅ Implemented GitHub Actions Security Rule Pack
- ✅ Implemented Dockerfile Security Rule Pack
- ✅ Implemented NodeJS Supply Chain Rule Pack
- ✅ Implemented Terraform IaC Security Rule Pack
- ✅ Integrated new rules with Specialized Misconfiguration Precedence (65)
- ✅ Maintained Zero breaking changes to existing API

### 📋 Phase 3: GUI
- 📋 Cross-platform desktop application
- 📋 Real-time scanning visualization
- 📋 Interactive results dashboard

### 🔮 Phase 4: Cloud Dashboard (Optional)
- 🔮 Team collaboration features
- 🔮 Historical trend analysis
- 🔮 Compliance reporting