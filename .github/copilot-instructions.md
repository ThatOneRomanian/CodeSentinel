# GitHub Copilot & AI Agent Guidelines for CodeSentinel

This file provides comprehensive guidance for AI agents (GitHub Copilot, Copilot Extensions, and custom AI agents) working with the CodeSentinel codebase.

---

## Project Overview

**Project**: CodeSentinel v0.2.0 (MIT Open-Source)
**Purpose**: AI-powered security scanning engine for detecting secrets, misconfigurations, and vulnerabilities in codebases
**Architecture**: Python 3.8+ with src-layout pattern and modular plugin architecture
**Status**: Phase 3 (API Freeze) - Ready for GUI development

### Key Milestones
- ✅ Phase 1: Core scanning engine (File Walker + Rule Engine + Reporting)
- ✅ Phase 2: AI integration (LLM explanations with safety layers)
- ✅ Phase 2.5: Rule hardening (provider-aware classification, deduplication)
- ✅ Phase 2.7: Structure-aware rule packs (GitHub Actions, Dockerfile, Terraform, JS supply chain)
- ✅ Phase 3: API freeze (Stable interface for GUI development)

---

## Architecture at a Glance

```
CodeSentinel v0.2.0 (MIT License)
├── src/sentinel/                    # Main package
│   ├── cli/                        # CLI interface (argparse)
│   ├── scanner/                    # Core scanning engine
│   │   ├── engine.py              # Rule engine + deduplication
│   │   └── walker.py              # File traversal
│   ├── rules/                      # Plugin rule architecture
│   │   ├── base.py                # Rule protocol & Finding dataclass
│   │   ├── secrets.py             # Secret detection rules
│   │   ├── configs.py             # Config vulnerability rules
│   │   ├── severity.py            # Precedence-based severity
│   │   ├── token_types.py         # Provider-aware classification
│   │   ├── docker/                # Dockerfile security rules
│   │   ├── gh_actions/            # GitHub Actions security rules
│   │   ├── js_supply_chain/       # JavaScript supply chain rules
│   │   └── terraform/             # Terraform IaC security rules
│   ├── llm/                        # AI integration (Phase 2)
│   │   ├── provider.py            # LLM provider abstraction
│   │   ├── explainer.py           # Explanation engine with batching
│   │   ├── safety.py              # Input/output sanitization
│   │   ├── validation.py          # Output validation
│   │   ├── cache.py               # Result caching with TTL
│   │   └── prompts/               # JSON prompt templates
│   ├── api/                        # Frozen API (Phase 3)
│   │   ├── scan_service.py        # LOCKED ScanService interface
│   │   ├── models.py              # Enhanced data models
│   │   ├── events.py              # Real-time event streaming
│   │   └── config_manager.py      # Shared configuration
│   ├── reporting/                  # Output formatters
│   │   ├── markdown.py            # Markdown reporter
│   │   └── json_report.py         # JSON reporter
│   └── utils/                      # Helper utilities
├── tests/                          # Comprehensive test suite (236+ tests)
│   ├── unit/                       # Component-level tests
│   └── integration/                # Full workflow tests
├── docs/                           # User documentation
│   ├── ARCHITECTURE.md            # System design
│   ├── phase3-spec.md             # GUI requirements
│   ├── phase2.7-rule-pack-design.md
│   └── api-freeze-spec.md         # Frozen API contract
└── memory-bank/                    # AI context (this session)
    ├── activeContext.md           # Current project status
    ├── systemPatterns.md          # Architectural patterns
    ├── progress.md                # Task tracking
    ├── productContext.md          # Licensing & positioning
    └── decisionLog.md             # Key architecture decisions
```

---

## Core Systems

### 1. Rule System (Plugin Architecture)

**Pattern**: Dynamic discovery via `RuleLoader` - NO REGISTRY REQUIRED

```python
# Each rule module exports a rule_set: list[type[Rule]]
# src/sentinel/rules/secrets.py
rule_set = [
    AWSKeyRule,
    AzureConnectionStringRule,
    GitHubTokenRule,
    # ... etc
]

# src/sentinel/scanner/engine.py
loader = RuleLoader()
all_rules = loader.load_rules()  # Auto-discovers all modules
```

**Key Constraint**: Rules are discovered by introspecting module attributes for classes implementing the `Rule` protocol. Modules must export `rule_set: list[type[Rule]]`.

**Precedence Hierarchy** (for deduplication - 67.8% reduction in duplicates):
1. **Provider-Specific** (100) - AWS, Azure, GCP, Stripe tokens
2. **Misconfiguration** (90) - API keys in config files
3. **Exposed Secrets** (85) - Hardcoded passwords
4. **Development Artifacts** (50) - Test keys, CI keys
5. **Specialized Misconfiguration** (65) - IaC/DevOps-specific
6. **Generic Tokens** (10) - Fallback for unknown tokens

### 2. Token Classification (Provider-Aware)

**Module**: `src/sentinel/rules/token_types.py`

Classifies tokens with provider awareness to avoid over-matching:
- AWS tokens (access key format, region hints)
- Azure tokens (connection string format)
- GCP tokens (JSON structure)
- Stripe tokens (sk_live_, pk_live_ prefixes)
- Generic tokens (fallback)

**Purpose**: Eliminates 12+ collision cases where Azure rules would over-match AWS credentials.

### 3. Deduplication Engine

**Module**: `src/sentinel/scanner/engine.py` - `Engine.execute()` method

**Algorithm**: 
1. Scan all files with all rules → multiple findings per issue
2. Group findings by location (file + line + column)
3. For each group, select highest-precedence finding
4. Return deduplicated findings

**Result**: Sample project reduced from 152 → 49 findings (67.8% reduction)

### 4. LLM Integration (BYOL - Bring Your Own LLM)

**Design**: Provider abstraction with no required external dependencies

```python
# src/sentinel/llm/provider.py
class LLMProvider(ABC):
    @abstractmethod
    async def explain(self, finding: Finding) -> str:
        pass

# Implementation: DeepSeekProvider
class DeepSeekProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key  # From DEEPSEEK_API_KEY env var
```

**Safety Layers**:
- **Input sanitization** (`safety.py`): Escape finding content
- **Output validation** (`validation.py`): Structure checking + fallbacks
- **Caching** (`cache.py`): TTL-based result reuse
- **Batching** (`explainer.py`): Efficient bulk processing

**Configuration**: Environment variables (DEEPSEEK_API_KEY, LLM_CACHE_DIR, etc.)

### 5. Phase 3 Frozen API

**Module**: `src/sentinel/api/scan_service.py`

**LOCKED Contract** - DO NOT MODIFY public signatures:

```python
class ScanService:
    def scan_directory(self, path: str, config: SharedConfig) -> ScanResult:
        """Frozen interface for GUI"""
    
    def scan_with_progress(self, path: str, config: SharedConfig) -> AsyncIterator[ScanEvent]:
        """Real-time event streaming"""
    
    def explain_finding(self, finding: EnhancedFinding) -> str:
        """AI explanation"""
    
    # ... 6 more frozen methods
```

**Why Frozen?**: GUI development can proceed in parallel without worrying about breaking changes.

---

## Developer Workflows

### Adding a New Rule

```python
# 1. Create rule class in src/sentinel/rules/secrets.py (or new module)
from dataclasses import dataclass
from src.sentinel.rules.base import Rule, Finding

@dataclass
class MyNewSecretRule(Rule):
    """Detect my new secret pattern"""
    name = "MyNewSecret"
    description = "Detects my custom secret format"
    severity = 75
    
    @classmethod
    def check(cls, content: str, filepath: str) -> list[Finding]:
        # Implement pattern detection
        findings = []
        for match in re.finditer(r'my-pattern', content):
            findings.append(Finding(
                rule_name=cls.name,
                finding_type="Secret",
                severity=cls.severity,
                location=(...),
                evidence=match.group(),
            ))
        return findings

# 2. Add to rule_set export
rule_set = [
    AWSKeyRule,
    MyNewSecretRule,  # ← Add here
    # ...
]

# 3. Test with pytest
# tests/unit/test_my_new_rule.py
def test_my_new_secret_detection():
    assert MyNewSecretRule.check("my-pattern-123", "test.py")

# 4. Run full test suite to verify deduplication
pytest tests/
```

### Extending Rule Pack (e.g., Terraform)

```python
# src/sentinel/rules/terraform/__init__.py
from src.sentinel.rules.terraform.security_rules import rule_set

# src/sentinel/rules/terraform/security_rules.py
class TerraformUnencryptedEBSRule(Rule):
    """Detect unencrypted EBS volumes in Terraform"""
    # Implement HCL parsing and detection

rule_set = [TerraformUnencryptedEBSRule, ...]
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_rule_engine.py -v

# With coverage
pytest tests/ --cov=src/sentinel --cov-report=html

# Integration tests only
pytest tests/integration/ -v

# Run dogfooding runner (validates against real projects)
python tools/dogfood_runner.py --scan-target /path/to/repo
```

### Manual Testing

```bash
# CLI scanning
python -m sentinel.cli.main scan /path/to/project --format json

# With AI explanations
python -m sentinel.cli.main scan /path/to/project --format markdown --explain

# Configuration
DEEPSEEK_API_KEY=sk-xxx python -m sentinel.cli.main scan ...
```

### Code Style & Quality

**Standards**:
- **Line length**: 88 (Black formatter)
- **Type hints**: Required for all functions
- **Docstrings**: Google-style for public APIs
- **Imports**: Absolute imports, `from src.sentinel.module import ...`
- **Tests**: All public functions must have tests

**Tools**:
```bash
# Format code
black src/ tests/ --line-length 88

# Sort imports
isort src/ tests/

# Type check
pyright src/sentinel

# Linting
pylint src/sentinel
```

---

## Integration Points & Key Files

### For Feature Development

| Task | File |
|------|------|
| Add new rules | [src/sentinel/rules/](src/sentinel/rules/) |
| Modify API | [src/sentinel/api/scan_service.py](src/sentinel/api/scan_service.py) |
| Update CLI | [src/sentinel/cli/main.py](src/sentinel/cli/main.py) |
| Fix scanning | [src/sentinel/scanner/engine.py](src/sentinel/scanner/engine.py) |
| Enhance AI | [src/sentinel/llm/](src/sentinel/llm/) |
| Add formatters | [src/sentinel/reporting/](src/sentinel/reporting/) |

### For Understanding

| Topic | File |
|-------|------|
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| API Freeze | [docs/api-freeze-spec.md](docs/api-freeze-spec.md) |
| Rule Packs | [docs/phase2.7-rule-pack-design.md](docs/phase2.7-rule-pack-design.md) |
| GUI Requirements | [docs/phase3-spec.md](docs/phase3-spec.md) |
| Rule Hardening | [docs/rule-hardening-notes.md](docs/rule-hardening-notes.md) |

---

## Quick Reference: Important Constraints

1. **ScanService API is FROZEN** - Do not change public method signatures
2. **Rule discovery is automatic** - Modules must export `rule_set` list
3. **No external dependencies** - Core scanning only uses standard library
4. **AI is optional** - Scanning works without LLM providers
5. **Deduplication is mandatory** - All findings go through precedence engine
6. **Type hints required** - All public functions must have type annotations
7. **Tests must pass** - 236+ tests must remain passing (0.2.0 baseline)
8. **MIT License** - All contributions must comply with MIT terms

---

## Memory Bank Context (for this AI session)

This codebase includes a `memory-bank/` directory for preserving project context across AI sessions:
- [activeContext.md](memory-bank/activeContext.md) - Current status & recent changes
- [systemPatterns.md](memory-bank/systemPatterns.md) - Recurring architectural patterns
- [progress.md](memory-bank/progress.md) - Task tracking and phase completion
- [productContext.md](memory-bank/productContext.md) - Licensing & positioning
- [decisionLog.md](memory-bank/decisionLog.md) - Key architectural decisions

These files should be updated when significant changes are made to the project.

---

## Getting Help

1. **Architecture questions**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Rule system questions**: See [docs/phase2.7-rule-pack-design.md](docs/phase2.7-rule-pack-design.md) + rule examples in [src/sentinel/rules/](src/sentinel/rules/)
3. **API questions**: See [docs/api-freeze-spec.md](docs/api-freeze-spec.md)
4. **Development questions**: See this file's Developer Workflows section
5. **Project history**: See [memory-bank/](memory-bank/) files

---

## Summary

CodeSentinel is a mature, Phase 3-ready security scanning platform with:
- ✅ Stable, frozen API for GUI development
- ✅ Plugin-based extensible rule system (zero-registration discovery)
- ✅ Provider-aware token classification (67.8% duplicate reduction)
- ✅ Optional AI integration with safety layers
- ✅ Comprehensive test coverage (236+ tests)
- ✅ Production-ready structure and documentation
- ✅ MIT open-source licensing

For any task in this codebase, prioritize:
1. **Maintaining the frozen API** (Phase 3 requirement)
2. **Keeping tests passing** (zero regressions)
3. **Following established patterns** (Rule discovery, deduplication, safety layers)
4. **Updating memory bank** (for continuity across sessions)
5. **Professional code quality** (type hints, docstrings, tests)

---

Generated: December 2024
Updated: Latest session
For questions: Refer to memory-bank/ and docs/ directories
