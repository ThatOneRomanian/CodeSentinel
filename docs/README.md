# CodeSentinel Documentation

Welcome to the CodeSentinel documentation. This directory contains comprehensive information about the project architecture, specifications, APIs, and development guides.

## Quick Navigation

### 📐 Architecture & Overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and component relationships

### 📋 Phase Specifications
Phase specifications describe the requirements and features for each development phase:

- **[phase1-spec.md](specs/phase1-spec.md)** - Phase 1: Core scanning engine (File Walker, Rule Engine, Reporting)
- **[phase2-spec.md](specs/phase2-spec.md)** - Phase 2: AI integration (LLM Explainer Mode)
- **[phase2-finalization.md](specs/phase2-finalization.md)** - Phase 2: Completion details and achievements
- **[phase3-spec.md](specs/phase3-spec.md)** - Phase 3: GUI development with frozen API

### 🔌 API & Integration
- **[api-freeze-spec.md](api/api-freeze-spec.md)** - Phase 3 Frozen API Contract (LOCKED for GUI development)

### 🎯 Design Documents
Design documents detail specific problem analysis and solution architecture:

- **[phase2.6-gap-analysis.md](design/phase2.6-gap-analysis.md)** - Analysis of rule blindspots in real-world repositories
- **[phase2.6-validation-report.md](design/phase2.6-validation-report.md)** - Validation results against six sample projects
- **[phase2.7-rule-pack-design.md](design/phase2.7-rule-pack-design.md)** - Structure-aware rule packs (GitHub Actions, Dockerfile, Terraform, JS)

### 📚 Implementation Guides
- **[rule-hardening-notes.md](guides/rule-hardening-notes.md)** - Rule system enhancements and deduplication patterns
- **[dogfooding-experiment-plan.md](guides/dogfooding-experiment-plan.md)** - Automated testing strategy and validation

### 📂 Examples
- **[examples/](examples/)** - Sample outputs and reference implementations

## Project Phases at a Glance

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ Complete | Core scanning engine with File Walker, Rule Engine, and Reporting |
| **Phase 2** | ✅ Complete | AI-powered explanations with LLM integration and safety layers |
| **Phase 2.5** | ✅ Complete | Rule hardening with provider-aware classification (67.8% deduplication) |
| **Phase 2.7** | ✅ Complete | Structure-aware rule packs (GitHub Actions, Docker, Terraform, JS supply chain) |
| **Phase 3** | ✅ Complete | Frozen API for GUI development with real-time event streaming |

## Key Systems

### Rule System (Plugin Architecture)
- Dynamic rule discovery via `RuleLoader` - no registry required
- Rules export via `rule_set: list[type[Rule]]` in each module
- Deduplication engine with 6-tier precedence hierarchy
- Provider-aware token classification (AWS, Azure, GCP, Stripe)

### LLM Integration (BYOL - Bring Your Own LLM)
- Optional AI explanations (scanning works without LLM)
- Safety layers: input sanitization, output validation, caching
- Batch processing for efficiency
- DeepSeek provider implementation with environment variable configuration

### Phase 3 Frozen API
- `ScanService` interface locked for GUI development
- Real-time event streaming via `ScanEvent` objects
- Enhanced finding data model for GUI display
- Comprehensive error handling with domain-specific exceptions

## Getting Started

1. **Quick Start**: See [README.md](../README.md) for installation and usage
2. **Architecture**: Start with [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
3. **Development**: Read relevant phase spec based on your work area
4. **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines

## File Organization

```
docs/
├── README.md                           # This file - documentation index
├── ARCHITECTURE.md                     # System design and components
├── examples/                           # Sample outputs and references
├── specs/                              # Phase specifications
│   ├── phase1-spec.md
│   ├── phase2-spec.md
│   ├── phase2-finalization.md
│   └── phase3-spec.md
├── api/                                # API documentation
│   └── api-freeze-spec.md
├── design/                             # Design documents & analysis
│   ├── phase2.6-gap-analysis.md
│   ├── phase2.6-validation-report.md
│   └── phase2.7-rule-pack-design.md
└── guides/                             # Implementation guides
    ├── rule-hardening-notes.md
    └── dogfooding-experiment-plan.md
```

## Key Constraints

1. **Frozen API** - ScanService interface cannot change (GUI development in progress)
2. **Test Suite** - All 236+ tests must remain passing
3. **Type Hints** - Required on all public functions
4. **MIT License** - All contributions must comply
5. **No External Dependencies** - Core scanning uses only standard library

## Questions?

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Rules**: See [design/phase2.7-rule-pack-design.md](design/phase2.7-rule-pack-design.md)
- **API**: See [api/api-freeze-spec.md](api/api-freeze-spec.md)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **AI Guidelines**: See [.github/copilot-instructions.md](../.github/copilot-instructions.md)

---

**Last Updated**: December 2024  
**Version**: 0.2.0  
**Status**: Production-Ready
