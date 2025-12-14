# Decision Log

This file records architectural and implementation decisions using a list format.
2025-11-26 14:42:40 - Memory Bank initialized with CodeSentinel project context.
2025-11-26 14:49:00 - Multi-phase development roadmap established

## Decision

Use Memory Bank pattern for project context management.

## Rationale

* Provides persistent context across sessions
* Helps maintain project vision and goals
* Supports multi-phase development tracking
* Enables better collaboration and knowledge transfer

## Implementation Details

* Created memory-bank directory with 5 core files
* Initialized with content from projectBrief.md
* Uses timestamp-based logging for all updates

## Decision

Adopt 4-phase development roadmap for CodeSentinel

## Rationale

* Clear progression from MVP to advanced features
* Each phase builds on previous capabilities
* Allows for incremental delivery and validation
* Maintains local-first philosophy while enabling optional cloud features

## Implementation Details

* Phase 1: CLI MVP (4-6 weeks) - Core security scanning
* Phase 2: AI Explainer Mode (3-4 weeks) - Intelligent analysis
* Phase 3: GUI (5-6 weeks) - User-friendly interface
* Phase 4: Cloud Dashboard (6-8 weeks) - Optional team collaboration
## Decision

Adopt the standardized project structure as defined in phase1-spec.md for Phase 1 implementation.

## Rationale

* Ensures consistency with the technical specification
* Provides clear separation of concerns with modular components
* Facilitates team collaboration and future extensibility
* Aligns with Python best practices and setuptools packaging

## Implementation Details

* Created exact directory structure as specified in phase1-spec.md
* Implemented empty Python modules with proper imports and docstrings
* Added __init__.py files to make all directories Python packages
* Configured pyproject.toml for setuptools with development dependencies
* Created comprehensive README.md with installation and usage instructions
* Validated structure against phase1-spec.md requirements

2025-11-27 01:44:00 - Phase 1 project skeleton completed and validated.

## Decision (Historical)

~~CodeSentinel is currently proprietary, developed privately, and future pricing/licensing will be determined later.~~
> Note: This decision was superseded by the MIT license decision on 2025-12-14.

## Rationale (Historical)

* Project was in early development phase
* Business model for potential public release was undecided
* Maintained flexibility for future licensing decisions
* Aligned with private development status at the time

## Implementation Details (Historical)

* Updated README.md to remove "free to use" messaging
* Changed license statement to proprietary
* Updated productContext.md to reflect undecided future licensing
* Removed references to public distribution channels
## Decision

Implement File Walker with comprehensive binary detection and .gitignore-style exclusions.

## Rationale

* Need robust file scanning that safely handles binary files and respects common exclusion patterns
* Performance considerations require both extension-based and content-based binary detection
* Hidden files should be excluded by default for security scanning context
* Clear error handling improves user experience and debugging

## Implementation Details

* Enhanced binary detection using both file extensions and content analysis (null bytes, non-text ratio)
* Implemented .gitignore-style pattern matching with fnmatch for flexible exclusions
* Added hidden file exclusion (files starting with .) by default
* Comprehensive error handling with custom exceptions for invalid paths and permissions
* Created 13 unit tests covering all major functionality with 100% pass rate
* Used pathlib for cross-platform compatibility and type hints for code clarity

2025-11-27 03:57:00 - File Walker implementation completed and tested.
## Decision

Implement Rule Engine with dynamic rule discovery and plugin-style architecture.

## Rationale

* Enables extensible security scanning without hardcoding rule names
* Supports future plugin architecture for custom rule sets
* Maintains separation between engine logic and specific rule implementations
* Follows open-closed principle for easy extension

## Implementation Details

* RuleLoader class dynamically discovers rule modules in src/sentinel/rules directory
* Uses Python's importlib and inspect modules for dynamic loading
* Validates Rule protocol compliance with required attributes (id, description, severity, apply method)
* run_rules function coordinates file processing and rule application
* Error handling isolates rule failures to prevent engine crashes
* Finding data structure normalized with rule_id, file_path, line, severity, excerpt, confidence

2025-11-27 05:20:00 - Rule Engine design and implementation completed.
## Decision

Use importlib.util for direct file-based module loading in RuleLoader to avoid package structure dependencies.

## Rationale

* Eliminates dependency on specific package structure (src.sentinel.rules vs sentinel.rules)
* Enables testing with temporary directories without installing packages
* More robust for dynamic rule discovery in various deployment scenarios
* Avoids issues with Python path configuration during testing

## Implementation Details

* Replaced importlib.import_module with importlib.util.spec_from_file_location and exec_module
* RuleLoader now loads modules directly from file paths instead of package names
* Maintains same Rule protocol validation and error handling
* Enables successful unit testing with temporary rule directories
* Preserves plugin-style architecture for future extensibility

2025-11-27 05:57:00 - Rule Engine import mechanism optimized for testing and deployment flexibility.
## Decision

Implement comprehensive secret and configuration vulnerability detection rules following the established Rule protocol.

## Rationale

* Need to fulfill Phase 1 requirements for detecting secrets and insecure configurations
* Must integrate seamlessly with existing Rule Engine architecture
* Requires robust pattern matching with appropriate confidence scoring
* Essential for providing actionable security findings to users

## Implementation Details

* Created 11 secret detection rules covering AWS, GCP, Azure, Stripe, JWT, private keys, passwords, OAuth tokens, and generic API keys
* Created 8 configuration vulnerability rules covering debug settings, weak crypto, insecure bindings, hardcoded credentials, TLS issues, development settings, exposed env vars, and insecure literals
* Implemented comprehensive unit tests (60 tests) covering all rule types and edge cases
* Used regex patterns combined with entropy analysis for secret detection
* Added comment skipping and false positive minimization in configuration rules
* All rules follow the established Rule protocol with proper severity levels and confidence scoring

2025-11-27 06:30:00 - Core rule modules design and implementation completed.
## Decision

Use function-based reporters instead of class-based architecture for Markdown and JSON reporting.

## Rationale

* Simpler API with single-purpose functions aligns better with the Phase 1 specification
* Eliminates unnecessary object instantiation for stateless operations
* More Pythonic approach for utility functions that don't require state
* Easier testing and mocking of individual functions
* Consistent with existing codebase patterns in rules and scanner modules

## Implementation Details

* Replaced MarkdownReporter class with generate_markdown_report function
* Replaced JSONReporter class with generate_json_report and generate_ci_report functions
* Maintained all functionality including proper Path object handling and edge case management
* Preserved comprehensive formatting and serialization capabilities
* Updated __init__.py exports to reflect new function-based API

2025-11-27 06:51:00 - Function-based reporter architecture implemented for consistency and simplicity.
## Decision
Implement argparse-based CLI with modular integration of existing components.

## Rationale
* Provides a unified command-line interface for users to access all CodeSentinel functionality
* Follows Python best practices for CLI tools with argparse
* Maintains separation of concerns by integrating existing File Walker, Rule Engine, and Reporting modules
* Enables CI/CD integration through proper exit codes and JSON output
* Supports both interactive use (Markdown reports) and automation (JSON/CI mode)

## Implementation Details
* Created `src/sentinel/cli/main.py` with argparse-based command structure
* Integrated File Walker for directory scanning with ignore patterns
* Integrated Rule Engine for security rule execution
* Integrated Reporting modules for Markdown and JSON output formats
* Implemented CI mode with exit code 1 for findings, 0 for clean scans
* Added comprehensive error handling for invalid paths, permission issues, and runtime errors
* Created 17 integration tests covering all CLI functionality and edge cases

2025-11-27 07:14:00 - CLI architecture implemented with modular integration and comprehensive testing.
2025-11-27 07:44:00 - Implemented Python packaging configuration with setuptools and proper CLI entry point.

## Decision

Use setuptools for packaging with src-layout and dependency-free design for Phase 1.

## Rationale

* Follows Python packaging best practices with modern pyproject.toml configuration
* Maintains dependency-free design for Phase 1 as specified in requirements
* Enables clean CLI entry point via [project.scripts] configuration
* Supports both development (editable) and production installations
* Provides proper version management with PEP 440 compliance

## Implementation Details

* Configured pyproject.toml with project metadata, authors, license, and classifiers
* Set version to 0.1.0 (PEP 440 compliant) in both pyproject.toml and __init__.py
* Defined CLI entry point: codesentinel = "sentinel.cli.main:main"
* Used setuptools package discovery with src/ directory layout
* Fixed import issues by converting relative imports to absolute imports in rule modules
* Verified installation with working CLI commands (scan, version, --help)
* Confirmed end-to-end functionality with successful scan producing 15,409 findings
## Decision

Perform comprehensive Phase 1 Repo Audit & Polish to enforce consistency and prepare for Phase 2 development.

## Rationale

* Need to ensure codebase consistency and adherence to established standards
* Required to fix accumulated technical debt and code quality issues
* Essential for maintaining professional codebase quality
* Preparation for Phase 2 development and potential team collaboration
* Documentation and packaging validation crucial for user experience

## Implementation Details

* Validated repository structure against systemPatterns and phase1-spec requirements
* Added copyright headers to all source files with proprietary licensing notice
* Fixed code quality issues (debug prints, type hints, import errors, inconsistent naming)
* Enhanced Finding dataclass with Phase 2 extensibility placeholders (CWE, remediation, tags)
* Updated README.md comprehensively with installation instructions, usage examples, and current status
* Verified packaging consistency (pyproject.toml version 0.1.0 matches __init__.py)
* Performed repo consistency scan (CRLF→LF conversion, trailing whitespace removal, EOF newlines)
* Tested installation and CLI functionality in externally managed environment

2025-11-27 08:56:00 - Comprehensive repository audit and polish decisions implemented.

## Decision

Enforce strict code quality standards and copyright headers across all source files.

## Rationale

* Professional codebase requires consistent documentation and licensing
* Copyright attribution maintained while enabling open-source collaboration
* Code quality standards prevent technical debt accumulation
* Consistent formatting improves maintainability and collaboration
* Preparation for potential open-source release or commercial licensing

## Implementation Details

* Updated copyright headers in all Python files from proprietary to MIT license format
* Enforced Google-style docstrings for all public functions
* Applied consistent type hints and absolute imports
* Removed debug prints and replaced with proper logging
* Fixed import errors and inconsistent variable naming
* Ensured all test files follow test_*.py pattern and import via installed package

2025-11-27 08:56:00 - Code quality standards and copyright enforcement implemented.
[2025-11-27 09:27:24] - Decision: Extended Finding dataclass with optional Phase 2 fields (cwe_id, category, tags, remediation, language) to support enhanced reporting without breaking existing functionality. Rationale: Backward compatibility while enabling future metadata-rich findings.
[2025-11-27 09:27:24] - Decision: Implemented lightweight language detection based on file extensions rather than content analysis. Rationale: Fast, dependency-free approach that provides sufficient context for Phase 2 features without performance overhead.
[2025-11-27 09:27:24] - Decision: Created rule pack scaffolding with __init__.py and README.md files for future expansion. Rationale: Plugin-style architecture allows for modular rule development and easy integration of supply chain, GitHub Actions, and Docker security scanning.
[2025-11-27 09:27:24] - Decision: Added numeric severity mapping (1-10 scale) alongside existing string severities. Rationale: Enables prioritization algorithms and quantitative analysis for Phase 2 dashboard features.
[2025-11-27 09:27:24] - Decision: Used TODO comment markers in rule modules instead of immediate implementation. Rationale: Allows for incremental Phase 2 development without disrupting current Phase 1 stability.
[2025-11-27 09:58:59] - Decision: Implemented LLM provider abstraction layer with placeholder implementations during Phase 2 bootstrap. Rationale: Establishes the architecture for bring-your-own-LLM functionality without requiring actual API integration during bootstrap, enabling incremental development.
[2025-11-27 09:58:59] - Decision: Created separate prompts directory with template files for different explanation types. Rationale: Separates prompt engineering from code logic, allows for easy modification and experimentation without code changes, and supports multiple languages and contexts.
[2025-11-27 09:58:59] - Decision: Extended Finding dataclass with risk_score and references fields for Phase 2. Rationale: Enables quantitative risk assessment and provides supporting documentation links, preparing for dashboard features and enhanced reporting.
[2025-11-27 09:58:59] - Decision: Implemented fail-safe AI enrichment that continues with original findings if explanation fails. Rationale: Ensures scanner reliability by preventing AI system failures from breaking core scanning functionality, maintaining Phase 1 stability.
[2025-11-27 09:58:59] - Decision: Used Union types for explanation engine return values to handle mixed data types. Rationale: Provides type safety while accommodating the flexible data structure needed for AI-generated content (strings, numbers, lists).
[2025-11-27 10:30:00] - Decision: Fixed abstract Rule class instantiation error in RuleLoader by changing _is_rule_class() method from OR to AND logic. Rationale: The original OR logic caused the abstract Rule protocol to be incorrectly identified as a rule class because it had some required attributes. The AND logic ensures a class must have all required attributes (id, description, severity, apply) to be considered a rule class. This prevents the engine from attempting to instantiate abstract classes and protocols.

[2025-11-27 10:30:00] - Decision: Enhanced RuleLoader validation with additional checks for non-empty rule attributes and proper method existence. Rationale: To ensure rule instances are fully valid and to prevent loading rules with empty or None values for critical attributes (id, description, severity). This improves the robustness of the rule engine and prevents runtime errors from malformed rules.

[2025-11-27 10:30:00] - Decision: Created comprehensive test suite for rule validation (test_rule_validation.py) covering abstract classes, invalid rules, and error scenarios. Rationale: To ensure the rule engine correctly handles edge cases and maintains backward compatibility. The tests cover the critical fixes and provide a safety net for future changes.

[2025-11-27 10:30:00] - Decision: Updated rules/__init__.py to remove abstract Rule protocol from __all__ exports. Rationale: The abstract Rule protocol is not meant to be instantiated and should not be exported as part of the public API. This change reinforces the intended use of the Rule protocol as an interface definition only.
[2025-11-27 19:59:00] - Decision: Implemented comprehensive AI safety layer with input sanitization, data filtering, and environment validation. Rationale: Essential for protecting against prompt injection, sensitive data exposure, and malicious input when integrating with external LLMs. Implementation: Created src/sentinel/llm/safety.py with sanitize_input(), filter_sensitive_data(), truncate_excerpt(), ensure_no_private_keys(), and SafetyLayer class.

[2025-11-27 19:59:00] - Decision: Redesigned prompt templates using JSON schema-based format. Rationale: Structured prompts enable better AI output consistency, validation, and maintainability. Implementation: Converted all text-based templates to JSON format with defined schemas for explanation, remediation, CWE mapping, and severity justification.

[2025-11-27 19:59:00] - Decision: Implemented output schema validation with fallback mechanisms. Rationale: Ensures AI-generated content meets quality and safety standards before integration. Implementation: Created src/sentinel/llm/validation.py with validate_ai_output(), validate_cwe_format(), validate_risk_score(), validate_references(), and OutputValidator class with fallback explanations.

[2025-11-27 19:59:00] - Decision: Added explanation batching to minimize LLM API calls. Rationale: Groups findings by rule type to generate one explanation per rule, significantly reducing costs and improving performance. Implementation: Enhanced ExplanationEngine with explain_batch() method that groups findings and applies per-rule merge logic.

[2025-11-27 19:59:00] - Decision: Implemented persistent AI caching layer with TTL support. Rationale: Avoids redundant LLM calls for identical findings and improves performance. Implementation: Created .cache/ directory structure and src/sentinel/llm/cache.py with AICache class, MD5-based key generation, and JSON file persistence.

[2025-11-27 19:59:00] - Decision: Enhanced rules with RuleMeta structure for richer metadata. Rationale: Provides structured metadata to support AI explanations without breaking existing functionality. Implementation: Added RuleMeta dataclass to src/sentinel/rules/base.py with category, CWE IDs, risk factors, detection methods, and explanation priorities.

[2025-11-27 19:59:00] - Decision: Created comprehensive test suite for all Phase 2 components. Rationale: Ensures reliability and maintainability of AI infrastructure. Implementation: Built 4 test files covering safety, validation, batching, and caching with 100+ test cases using pytest and mocks.
## [2025-11-28 01:50:00] - DeepSeek Integration Architecture Decisions

**Decision:** Implement real DeepSeekProvider with dependency-free HTTP client
- **Rationale:** Maintain project's dependency-free philosophy while enabling real AI integration
- **Implementation:** Used Python's built-in `urllib` instead of external libraries like `requests` or `httpx`
- **Benefits:** No additional dependencies, consistent with Phase 1 approach
- **Trade-offs:** More verbose error handling, but provides full control

**Decision:** Graceful fallback system for AI explanations
- **Rationale:** Ensure system remains functional even when API keys are not configured
- **Implementation:** Provider detection system that checks for configuration before making API calls
- **Benefits:** Backward compatibility maintained, users can try AI features without immediate setup
- **Trade-offs:** Slightly more complex provider interface

**Decision:** Environment variable-based configuration
- **Rationale:** Standard practice for API keys and configuration, avoids hardcoded secrets
- **Implementation:** DEEPSEEK_API_KEY and optional DEEPSEEK_BASE_URL environment variables
- **Benefits:** Secure, flexible, follows 12-factor app principles
- **Trade-offs:** Requires user setup, but well-documented

**Decision:** Comprehensive error handling and retry logic
- **Rationale:** Network operations are inherently unreliable, need robust error handling
- **Implementation:** Exponential backoff retry for transient errors, clear error messages
- **Benefits:** System resilience, user-friendly error reporting
- **Trade-offs:** More complex implementation, but essential for production use
## [2025-11-28 10:35:00] - Rule Architecture Integrity Audit Decisions

**Decision:** Implement consolidated rule export pattern across all rule modules
- **Rationale:** Eliminates abstract class instantiation risks and provides cleaner module exports
- **Implementation:** Updated [`configs.py`](src/sentinel/rules/configs.py:169) and [`secrets.py`](src/sentinel/rules/secrets.py:442) to export `rules` list with instantiated rule instances
- **Benefits:** Prevents RuleLoader from attempting to instantiate abstract classes, enables better validation

**Decision:** Remove abstract Rule protocol imports from concrete rule modules
- **Rationale:** Concrete rules should not depend on the abstract protocol definition
- **Implementation:** Removed `from sentinel.rules.base import Rule` from [`configs.py`](src/sentinel/rules/configs.py:15) and [`secrets.py`](src/sentinel/rules/secrets.py:16)
- **Benefits:** Prevents accidental protocol instantiation, reinforces interface segregation principle

**Decision:** Enhance RuleLoader with comprehensive abstract class detection
- **Rationale:** Need robust protection against abstract class instantiation in both legacy and consolidated export modes
- **Implementation:** Added `inspect.isabstract()` checks and protocol name detection in [`RuleLoader._is_valid_rule()`](src/sentinel/scanner/engine.py:164)
- **Benefits:** Future-proofs against abstract class instantiation regressions

**Decision:** Create comprehensive test suite for rule export patterns
- **Rationale:** Ensure architectural integrity through automated testing
- **Implementation:** Created [`test_rule_export_patterns.py`](tests/unit/test_rule_export_patterns.py) with 10 test cases covering all export scenarios
- **Benefits:** Provides safety net against future regressions, documents expected behavior

**Decision:** Maintain backward compatibility with legacy rule modules
- **Rationale:** Existing codebase and future development should work without breaking changes
- **Implementation:** RuleLoader supports both consolidated `rules` list and legacy class discovery with fallback
- **Benefits:** Smooth transition path, no immediate breaking changes required
## [2025-11-29 01:30:00] - Phase 2 Audit and Test Stabilization Decisions

**Decision:** Implement comprehensive Phase 2 audit covering all 9 parts
- **Rationale:** Ensure codebase consistency, eliminate placeholders, and prepare for Phase 3 development
- **Implementation:** Systematic audit of placeholders, AI infrastructure, rule system, CLI consistency, memory bank alignment, documentation, and test suite
- **Benefits:** Clean, production-ready codebase with no technical debt or inconsistencies

**Decision:** Fix all test failures and ensure 100% test suite pass rate
- **Rationale:** Essential for codebase stability and confidence in Phase 2 features
- **Implementation:** Fixed CLI test failures (help text, return codes, output expectations), rule system test failures (abstract class detection, protocol isolation), filetype detection test failures (env file detection), walker test failures (file inclusion logic, path handling), severity test failures (None handling, whitespace), and rule validation test failures (consolidated export patterns)
- **Benefits:** 236/236 tests passing, comprehensive test coverage (81% overall), reliable CI/CD pipeline

**Decision:** Remove all remaining placeholders and implement missing functionality
- **Rationale:** Eliminate technical debt and ensure all Phase 2 features are fully functional
- **Implementation:** Identified and resolved 38 placeholder instances including stub LLM provider code, incomplete prompt templates, empty rule modules, and commented-out code blocks
- **Benefits:** Production-ready AI explainer mode with no placeholder dependencies

**Decision:** Enhance AI infrastructure consistency and safety guarantees
- **Rationale:** Ensure robust, secure AI operations with proper validation and fallback mechanisms
- **Implementation:** Verified complete alignment of safety layer, prompt templates, validation layer, caching system, batching system, and provider architecture
- **Benefits:** Reliable AI explanations with comprehensive safety protections and graceful degradation

**Decision:** Maintain backward compatibility while fixing architectural issues
- **Rationale:** Ensure existing functionality remains intact while improving system robustness
- **Implementation:** Fixed abstract class instantiation in RuleLoader, enhanced rule export patterns, and maintained legacy rule module support
## [2025-11-29 02:23:00] - Phase 2 Finalization Decisions

**Decision:** Version bump to 0.2.0 for Phase 2 completion
- **Rationale:** Major feature addition (AI Explainer Mode) warrants minor version increment from 0.1.0 to 0.2.0
- **Implementation:** Updated [`pyproject.toml`](pyproject.toml:12) and [`src/sentinel/__init__.py`](src/sentinel/__init__.py:11) to version "0.2.0"
- **Benefits:** Clear version progression, semantic versioning compliance, milestone marking

**Decision:** Implement 90-second quickstart in README.md
- **Rationale:** Improve user onboarding with minimal friction and clear installation-to-scan workflow
- **Implementation:** Added condensed 3-command quickstart section at top of README.md
- **Benefits:** Faster time-to-value for new users, reduced setup complexity, improved documentation structure

**Decision:** Create comprehensive architecture documentation
- **Rationale:** Document system component relationships and data flow for future development and user understanding
- **Implementation:** Created [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) with system overview, core components, data flow, and design patterns
- **Benefits:** Better project understanding, easier onboarding for new contributors, architectural decision transparency

**Decision:** Establish golden workflows with sample outputs
- **Rationale:** Provide realistic examples of CodeSentinel output without exposing sensitive data
- **Implementation:** Created [`docs/examples/`](docs/examples/) directory with sample markdown and JSON reports based on sample-project scan results
- **Benefits:** User education, documentation completeness, realistic expectation setting

**Decision:** Add internal licensing and positioning notes
- **Rationale:** Clarify proprietary status and future commercialization options without making public commitments
- **Implementation:** Added business model section to [`memory-bank/productContext.md`](memory-bank/productContext.md) with current status and potential future models
- **Benefits:** Clear internal understanding of project status, strategic positioning for future decisions

**Decision:** Complete memory bank alignment for Phase 2 finalization
- **Rationale:** Ensure all memory bank files reflect current project state and Phase 2 completion
- **Implementation:** Updated all memory bank files (activeContext.md, progress.md, decisionLog.md, systemPatterns.md) with Phase 2 finalization status and decisions
- **Benefits:** Persistent project context, accurate historical record, preparation for Phase 3 development
- **Benefits:** Zero breaking changes, smooth transition for existing users and future development
## [2025-11-29 02:56:00] - Phase 3 API Freeze Architecture Decisions

**Decision:** Implement frozen API contract with strict backward compatibility guarantees
- **Rationale:** Provide stable interface for GUI development while maintaining existing CLI functionality without breaking changes
- **Implementation:** Created [`ScanService`](api-freeze-spec.md:185) class with frozen method signatures, optional parameters for new features, and semantic versioning enforcement
- **Benefits:** Stable GUI integration, zero breaking changes for CLI users, future-proof design

**Decision:** Extend Finding data model with GUI-specific metadata while maintaining backward compatibility
- **Rationale:** GUI requires richer metadata for display, interaction, and state management beyond basic security findings
- **Implementation:** [`EnhancedFinding`](api-freeze-spec.md:67) dataclass with optional fields for AI explanations, code context, resolution tracking, and user notes
- **Benefits:** Rich GUI display capabilities, persistent user state, enhanced user experience without breaking existing functionality

**Decision:** Implement real-time event streaming for progressive result delivery
- **Rationale:** Large scans require responsive progress updates and immediate finding display for good user experience
- **Implementation:** [`ScanEvent`](api-freeze-spec.md:397) system with WebSocket-compatible events and structured payloads for progress, findings, and completion
- **Benefits:** Responsive UI during long scans, memory efficiency, cancellation support, better user engagement

**Decision:** Create comprehensive error hierarchy with consistent error codes
- **Rationale:** GUI requires structured error handling with user-friendly messages and consistent error reporting
- **Implementation:** [`CodeSentinelError`](api-freeze-spec.md:445) base class with specialized subclasses and standardized error codes for all failure scenarios
- **Benefits:** Consistent error handling, actionable error messages, detailed debugging information, improved user experience

**Decision:** Design shared configuration model for GUI and CLI synchronization
- **Rationale:** Users expect consistent behavior and settings between GUI and CLI interfaces
- **Implementation:** [`SharedConfig`](api-freeze-spec.md:702) dataclass with platform-specific persistence and conflict resolution mechanisms
- **Benefits:** Unified user experience, configuration synchronization, reduced duplication, easier maintenance

**Decision:** Implement AI safety controller with privacy and security guarantees
- **Rationale:** AI operations require robust safety controls to prevent data exposure and ensure secure operation
- **Implementation:** [`AISafetyController`](api-freeze-spec.md:619) with input validation, content sanitization, and environment safety checks
- **Benefits:** Privacy protection, prompt injection prevention, graceful degradation, regulatory compliance

**Decision:** Use transparent backend module wrapping with enhanced functionality
- **Rationale:** Leverage existing backend functionality without modifications while adding GUI-specific enhancements
- **Implementation:** [`ScanServiceImplementation`](api-freeze-spec.md:518) wraps existing functions like [`walk_directory()`](src/sentinel/scanner/walker.py:36) and [`run_rules()`](src/sentinel/scanner/engine.py:271) with error handling and progress tracking
- **Benefits:** Zero breaking changes, enhanced functionality, consistent error handling, maintainable codebase
## Decision: Automated Dogfooding Runner Architecture

**Decision**: Implement a dependency-free dogfooding runner using only Python standard library with scenario-based execution and comprehensive logging.

**Rationale**: 
- Enables systematic validation of CodeSentinel v0.2.0 performance and quality
- Supports the dogfooding experiment plan requirements without adding external dependencies
- Provides structured output for analysis and comparison across multiple runs
- Maintains local-first philosophy with optional AI scenario support
- Facilitates Phase 3 GUI development planning with empirical data

**Implementation Details**:
- Location: [`tools/dogfood_runner.py`](tools/dogfood_runner.py)
- Dependencies: Standard library only (argparse, pathlib, subprocess, time, json, etc.)
- Scenarios: 5 core scenarios from dogfooding-experiment-plan.md + 2 additional scenarios
- Output: Structured directory hierarchy with timestamps, metadata, and comprehensive logging
- Error Handling: Graceful failure with scenario isolation and timeout protection
- Integration: Adds `dogfood-results/` to .gitignore and updates documentation

2025-11-29 04:16:00 - Implemented automated dogfooding runner design for systematic CodeSentinel validation
## 2025-11-29 06:55:30 - Dogfooding Runner JSON Parsing Architecture

**Decision:** Implemented robust JSON extraction with brace counting and multi-strategy findings counting for dogfooding runner.

**Context:** The dogfooding runner was incorrectly reporting 0 findings due to JSON parsing failures caused by log messages in codesentinel output. This required a robust solution that could handle log-contaminated output and various JSON structures.

**Options Considered:**
1. **Simple JSON.loads()** - Failed due to log message prefixes
2. **Regex-based extraction** - Too fragile for nested JSON structures  
3. **Brace counting with string escape handling** - Chosen solution

**Rationale:**
The brace counting approach provides:
- Resilience to log message prefixes and suffixes
- Proper handling of nested JSON structures
- String escape sequence awareness to avoid false brace counting
- Graceful degradation when JSON is malformed

**Implementation Details:**
- Enhanced `_extract_json_from_output()` with state machine for brace counting
- Multi-strategy counting: findings array, scan_summary, results array, top-level arrays
- Added `--debug-findings` flag for validation and comparison
- Comprehensive test coverage for edge cases

**Implications:**
- Dogfooding runner now provides accurate findings counts (152 in sample project)
- Enables reliable automated testing and performance regression detection
- Foundation for Phase 3 GUI integration and real-world repository validation
## 2025-11-30 02:48:45 - Phase 4 Finding Deduplication Implementation Complete

**Decision:** Implemented comprehensive finding deduplication logic in the rule engine to prevent multiple findings for the same token while maintaining precedence rules.

**Rationale:** 
- Phase 1 analysis identified 12 tokens triggering 3+ rules, causing excessive duplicate findings
- Current system lacked deduplication, causing noise in outputs and inflated finding counts
- Needed to implement provider-aware precedence to resolve rule collisions identified in Phase 2.5

**Implementation Details:**
- Extended [`run_rules()`](src/sentinel/scanner/engine.py:471) method to include deduplication via [`_deduplicate_findings()`](src/sentinel/scanner/engine.py:369)
- Implemented precedence model: provider-specific tokens (100) > OAuth tokens (90) > generic API keys (80) > high-entropy strings (70) > configuration rules (60)
- Used grouping key: (file_path, line_number, normalized_excerpt) for finding grouping
- Created comprehensive test suite ([`tests/unit/test_deduplication.py`](tests/unit/test_deduplication.py)) with 590 lines covering all scenarios
- Maintained full API stability and backward compatibility

**Benefits:**
- Reduced sample project findings from 152+ (with duplicates) to 50 unique findings
- Eliminated duplicate reporting for same tokens across multiple rules
- Preserved highest-precedence findings while removing redundant ones
- Maintained zero breaking changes to existing API and functionality
## [2025-11-30 17:01:00] - Phase 2.5 Rule Hardening Architecture Decisions

**Decision:** Implement provider-aware token classification system for intelligent deduplication

**Rationale:**
- Identified rule collisions where 12 tokens triggered 3+ rules, causing excessive duplicate findings
- Needed systematic approach to classify tokens by provider and type for intelligent deduplication
- Required precedence model to ensure highest-quality findings are preserved during deduplication

**Implementation Details:**
- Created [`token_types.py`](src/sentinel/rules/token_types.py) module with comprehensive token classification
- Implemented provider-specific classification (AWS, Azure, GCP, Stripe, generic, OAuth, high-entropy)
- Established precedence scoring: provider-specific (100) > OAuth tokens (90) > generic API keys (80) > high-entropy strings (70) > configuration rules (60)
- Integrated classification with existing rule system without breaking changes

**Benefits:**
- 67.8% duplicate reduction in sample project (152+ findings → 49 findings)
- Resolved Azure rule over-matching through provider-aware classification
- Maintained zero breaking changes to existing API and functionality
- Enhanced accuracy through intelligent precedence-based selection

**Decision:** Implement advanced deduplication with grouping by normalized token content

**Rationale:**
- Simple rule-based deduplication insufficient for complex token collisions
- Needed grouping mechanism that considers file context, line position, and normalized token content
- Required robust algorithm to handle edge cases while maintaining performance

**Implementation Details:**
- Enhanced Rule Engine with [`_deduplicate_findings()`](src/sentinel/scanner/engine.py:369) method
- Grouping key: (file_path, line_number, normalized_excerpt) for precise finding grouping
- O(n) complexity algorithm for efficient processing of large finding sets
- Comprehensive test coverage with 590 lines in [`test_deduplication.py`](tests/unit/test_deduplication.py)

**Benefits:**
- Eliminated duplicate reporting for same tokens across multiple rules
- Preserved highest-precedence findings while removing redundant ones
- Maintained performance consistency with enhanced accuracy
- Handled edge cases including partial obfuscation and token variations

**Decision:** Maintain full backward compatibility while enhancing rule engine capabilities

**Rationale:**
- Existing users and integrations depend on stable API behavior
- Phase 3 GUI development requires frozen API surface
- Zero breaking changes essential for production deployment confidence

**Implementation Details:**
- Additive architecture: deduplication added as optional enhancement to existing flow
- Preserved all existing API signatures and data structures
- Enhanced finding data without modifying core structure
- Comprehensive test suite ensures backward compatibility (236/236 tests passing)

**Benefits:**
- Zero breaking changes to existing CLI, scanning, and reporting functionality
- Smooth upgrade path for existing deployments
- Enhanced capabilities without requiring user configuration changes
- Production-ready stability with improved accuracy

**Decision:** Implement comprehensive dogfooding validation for rule hardening

**Rationale:**
- Required empirical validation of quantitative improvements
- Needed systematic testing across multiple scenarios and configurations
- Essential for confidence in production deployment

**Implementation Details:**
- Enhanced dogfooding runner with accurate findings counting (67.8% reduction validated)
- 7-scenario matrix covering all output formats and AI configurations
- Automated performance and accuracy validation
- Structured output for comparison across runs

**Benefits:**
- Empirical validation of 67.8% duplicate reduction
- Performance consistency verification
- Quality assurance for production deployment
- Foundation for future regression testing
## [2025-12-01 03:11:58] - Phase 2.7 Rule Pack Prioritization and Precedence Decision
 
**Decision:** Prioritize the development of four new, structure-aware rule packs (GitHub Actions, Dockerfile, JS Supply Chain, Terraform) for Phase 2.7.
 
**Rationale:**
- Phase 2.6 validation revealed critical functional blindspots in IaC, CI/CD, and SSC domains.
- Existing generic rules are insufficient for complex configuration misconfigurations requiring language/structure awareness (YAML, Dockerfile, HCL, JSON).
- Addressing these gaps is essential for CodeSentinel's transition from a secret scanner to a comprehensive security analysis tool.
 
**Implementation Details:**
- Defined 8 specific rules across the four new packs.
- Established a new `Specialized Misconfiguration` precedence level (65) for these rules, positioning them above generic configuration rules (60) but below generic high-entropy secrets (70) to ensure accurate deduplication and prioritization.
- This mandates a shift in scanning engine capability towards structure parsing in Phase 2.7 implementation.
## [2025-12-01 04:26:00] - Phase 2.7 Implementation Decisions

**Decision:** Implemented lightweight, dependency-free structure-aware parsing utilities (YAML, Dockerfile, HCL).
- **Rationale:** Necessary to support the new structure-aware rule packs (GHA, Docker, Terraform) without adding external project dependencies (PyYAML, python-hcl), maintaining the project's local-first philosophy.
- **Implementation Details:** Created [`src/sentinel/utils/parsers.py`](src/sentinel/utils/parsers.py) using `re` and `json` for simplified structural analysis.

**Decision:** Implemented Phase 2.7 specialized misconfiguration rule packs and integrated them into the Rule Engine.
- **Rationale:** To address critical blindspots identified in Phase 2.6 (IaC, CI/CD, SSC) and move CodeSentinel toward comprehensive security analysis.
- **Implementation Details:** Created four new rule packs (`docker/`, `gh_actions/`, `js_supply_chain/`, `terraform/`) using the defined precedence level of 65. Updated [`src/sentinel/rules/base.py`](src/sentinel/rules/base.py:115) to include `rule_precedence` in the `Finding` dataclass, and updated [`src/sentinel/scanner/engine.py`](src/sentinel/scanner/engine.py:272) to process this new field. All rules were implemented based on the [`phase2.7-rule-pack-design.md`](phase2.7-rule-pack-design.md) specification and passed respective unit tests.
[2025-12-01 05:36:00] - Decision: Implemented Phase 2.7 specialized misconfiguration rule packs and structure-aware parsers (Docker, GitHub Actions, JS package, Terraform) plus PyYAML dependency, ensuring precedence 65 and parser-powered context for each rule. Rationale: Address Phase 2.6 gap analysis, preserve backward compatibility, and support new dogfooding targets.

## [2025-12-14 00:30:00] - Decision: Transition to MIT Open-Source License

**Decision:** Transition CodeSentinel from proprietary software to MIT open-source license.

**Date:** December 14, 2025

**Rationale:**
- Enable community feedback and contributions to improve the project
- Create a sustainable development model with broader participation
- Align with local-first values by giving users complete freedom and transparency
- Increase adoption by removing licensing barriers
- Build trust through transparent security tooling

**Impact:**
- Opens project to community contributions and improvements
- Increases transparency in the security scanning process
- Allows wider adoption in both commercial and non-commercial contexts
- Creates potential for community-driven rule packs
- Establishes foundation for open governance model
- Shifts focus from proprietary business model to community-driven development

**Implementation Details:**
- Updated LICENSE file with MIT license text
- Updated all source file headers to MIT license format
- Added CONTRIBUTING.md, CODE_OF_CONDUCT.md, and SECURITY.md
- Removed all proprietary development language from documentation
- Updated memory-bank files to reflect open-source transition
- Maintained technical decisions and architecture while opening access
- Created public GitHub repository with clear contribution guidelines