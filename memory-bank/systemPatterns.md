# System Patterns

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-11-26 14:42:40 - Memory Bank initialized with CodeSentinel project context.
2025-11-26 14:52:00 - Detailed project patterns and standards established

## Coding Patterns

* **Python 3.8+ Compatibility**: Ensure all code works with Python 3.8 and above
* **Type Hints**: Use type annotations for all function signatures and class attributes
* **Black Code Style**: Enforce consistent code formatting using Black
* **PEP 8 Compliance**: Follow Python style guide for naming and structure
* **Docstring Standards**: Use Google-style docstrings for all public functions and classes
* **Exception Handling**: Use specific exceptions with descriptive error messages
* **Configuration Management**: Use YAML/JSON for configuration with environment variable overrides
* **Plugin Architecture**: Extensible rule system with plugin support for scanning patterns

## Architectural Patterns

* **Local-First Philosophy**: All core functionality works without internet connection
* **Modular Design**: Separate core scanning from UI and cloud components
* **Configuration-Driven**: Behavior configurable without code changes
* **Cross-Platform Compatibility**: Support Windows, macOS, and Linux equally
* **Progressive Enhancement**: Core features in CLI, advanced features in GUI/Cloud
* **Phased Development**: Clear progression from MVP to advanced features
* **Memory Bank Pattern**: Persistent project context management across sessions
* **Standardized Project Structure**:
  ```
  /codesentinel
      /src
          /sentinel
              /cli
              /scanner
              /rules
              /reporting
              /utils
      /tests
          /unit
          /integration
      /docs
      /memory-bank
      pyproject.toml
      README.md
  ```

## Testing Patterns

* **Unit Test Coverage**: Aim for 80%+ test coverage for core components
* **Integration Tests**: Test full scanning workflows with sample codebases
* **Mock External Services**: Isolate tests from LLM APIs and cloud dependencies
* **Test Fixtures**: Use consistent test data and fixtures for reproducible tests
* **Performance Testing**: Benchmark scanning performance with large codebases
* **Security Testing**: Include tests for security vulnerabilities in the scanner itself

## Process Patterns

* **Public GitHub Repository**: Using public GitHub repository with proper .gitignore for Python + VS Code
* **Memory-Bank Driven Development**: Using memory-bank pattern for persistent project context and decision tracking
* **Open-Source Development Workflow**: Community-driven development with MIT licensing and public contributions
2025-11-27 05:21:00 - Rule Engine abstraction pattern implemented: Plugin-style rule system using dynamic module discovery and Rule protocol. RuleLoader discovers and validates rule modules at runtime, enabling extensible security scanning without hardcoded dependencies. Error handling isolates rule failures to maintain engine stability.
2025-11-27 05:57:00 - Enhanced Rule Engine testing pattern: Implemented inline mock rule definitions in unit tests to avoid import dependencies and package structure issues. This pattern enables robust testing of plugin architectures without requiring test packages to be installed, improving test isolation and reliability.
2025-11-27 06:31:00 - Standardized rule structure pattern implemented: All rules follow consistent Rule protocol with id, description, severity attributes and apply method. Rule modules export rule instances for dynamic loading. Comprehensive unit testing pattern established with 60/60 passing tests covering all rule types and edge cases.
## Reporting Patterns

* **Function-Based Reporter Design**: Use simple functions instead of classes for stateless reporting operations
* **Consistent Finding Handling**: Both reporters accept List[Finding] and handle Path objects by converting to strings
* **Comprehensive Error Handling**: Graceful handling of None values, missing line numbers, and serialization errors
* **Edge Case Management**: Proper truncation of long excerpts, confidence rounding, and Unicode handling
* **Dual Output Formats**: Human-readable Markdown for users and structured JSON for machine processing
* **CI-Optimized Output**: Separate generate_ci_report function for CI/CD systems with minimal metadata
* **Test-Driven Development**: Comprehensive unit tests covering all functionality and edge cases (33/33 passing)
* **Documentation Standards**: Google-style docstrings with type hints for all public functions

2025-11-27 06:51:00 - Reporting module patterns established: Function-based design with comprehensive error handling, dual output formats, and full test coverage.
## CLI Interface Patterns

* **Argparse-Based CLI**: Use argparse for command-line interface with subcommands for different operations
* **Modular Integration**: CLI integrates existing components (File Walker, Rule Engine, Reporting) without modifying their core logic
* **Exit Code Standards**: 
  - 0: Success, no findings (clean scan)
  - 1: Success, findings detected (CI mode)
  - 2: Runtime errors (invalid paths, permission issues, rule loading failures)
  - 130: User interrupt (Ctrl+C)
* **Output Format Flexibility**: Support both human-readable (Markdown) and machine-readable (JSON) formats
* **CI/CD Integration**: --ci flag forces JSON output and uses exit codes for automation
* **Error Handling**: Clear error messages for invalid paths, permission issues, and runtime errors
* **Empty Scan Handling**: Generate reports even for empty directories to maintain consistent user experience
* **Test-Driven Development**: Comprehensive integration tests covering all CLI functionality and edge cases

2025-11-27 07:15:00 - CLI interface patterns established: argparse-based design with modular integration, comprehensive error handling, dual output formats, and CI/CD compatibility.
2025-11-27 07:45:00 - Python packaging conventions and CLI entry-point standards established.

## Packaging Patterns

* **Setuptools Configuration**: Use modern pyproject.toml with [project] table for metadata and [tool.setuptools] for package discovery
* **src-Layout Structure**: Maintain source code in src/ directory with proper __init__.py files in all subpackages
* **PEP 440 Versioning**: Strict adherence to semantic versioning with proper version strings
* **Dependency-Free Design**: Phase 1 maintains zero external runtime dependencies as specified
* **CLI Entry Points**: Configure [project.scripts] for clean command-line interface access
* **Absolute Imports**: Use absolute imports (sentinel.module) instead of relative imports for packaging compatibility
* **Development Installation**: Support editable installations with pip install -e . for development workflow

## CLI Entry-Point Standards

* **Command Structure**: Use argparse with subcommands (scan, version) for clear user interface
* **Exit Code Convention**: Follow standard exit codes (0=success, 1=findings, 2=errors, 130=interrupt)
* **Output Format Flexibility**: Support both human-readable (Markdown) and machine-readable (JSON) formats
* **CI/CD Integration**: --ci flag enables automation-friendly behavior with strict exit codes
* **Help System**: Comprehensive --help documentation for all commands and options
## Repository Consistency Patterns

* **CRLF to LF Conversion**: All source files use Unix-style LF line endings for cross-platform compatibility
* **Trailing Whitespace Removal**: No trailing whitespace allowed in any source files
* **EOF Newlines**: All files end with a single newline character for POSIX compliance
* **Consistent Indentation**: 4-space indentation with no tabs across all Python files
* **Test File Naming**: All test files follow test_*.py pattern for pytest discovery
* **Copyright Headers**: All source files include consistent copyright header with proprietary licensing
* **Absolute Imports**: Test files import via installed package (sentinel.module) not relative imports

## Code Quality Enforcement Patterns

* **Google-Style Docstrings**: All public functions and classes include comprehensive Google-style docstrings
* **Type Hint Consistency**: All function signatures include complete type hints with Optional for nullable parameters
* **Debug Print Elimination**: Replace debug print statements with proper logging using Python's logging module
* **Import Error Prevention**: Ensure consistent function naming across modules (e.g., shannon_entropy vs calculate_entropy)
* **Variable Naming Consistency**: Follow PEP 8 naming conventions (snake_case for variables/functions, PascalCase for classes)
* **TODO Management**: Move implementation TODOs to memory-bank for tracking, remove commented-out code blocks
* **Severity Value Consistency**: Ensure all rules use consistent severity levels (low, medium, high, critical)

## Copyright and Licensing Patterns

* **MIT License Header Format**: All source files include standard MIT license header with copyright attribution
* **File Header Placement**: Copyright headers placed at top of file, before module docstring
* **Consistent Licensing**: Maintain MIT open-source licensing across all project components and contributions

2025-11-27 08:56:00 - Repository consistency, code quality, and copyright patterns established.
[2025-11-27 09:27:44] - Pattern: Future-Proofing Architecture - Extensible dataclass design with optional fields for backward compatibility while enabling new features.
[2025-11-27 09:27:44] - Pattern: Lightweight Language Detection - File extension-based language identification for performance and simplicity, supporting 40+ file types.
[2025-11-27 09:27:44] - Pattern: Rule Pack Modularity - Plugin-style rule architecture with __init__.py and README.md scaffolding for easy expansion.
[2025-11-27 09:27:44] - Pattern: Dual Severity System - Both string-based and numeric (1-10) severity mapping for flexible reporting and prioritization.
[2025-11-27 09:27:44] - Pattern: Phase Planning Markers - TODO comments in rule modules for incremental development without breaking existing functionality.
[2025-11-27 09:59:19] - Pattern: LLM Provider Abstraction - Abstract base class with multiple provider implementations (DeepSeek, OpenAI, LocalOllama) for bring-your-own-LLM architecture.
[2025-11-27 09:59:19] - Pattern: Template-Based Prompt Engineering - Separate prompt templates in dedicated directory with variable interpolation for different explanation types.
[2025-11-27 09:59:19] - Pattern: Fail-Safe AI Enrichment - Graceful degradation when AI systems fail, preserving core scanning functionality.
[2025-11-27 09:59:19] - Pattern: Union Type Flexibility - Using Union types for mixed data structures in AI-generated content while maintaining type safety.
[2025-11-27 09:59:19] - Pattern: Phase 2 Bootstrap Architecture - Placeholder implementations establish architecture without breaking existing functionality, enabling incremental development.
[2025-11-27 10:31:00] - Pattern: Abstract Class Protection in Rule Engine - RuleLoader uses AND logic instead of OR logic to identify rule classes, preventing abstract classes and protocols from being incorrectly instantiated. This ensures that only concrete rule implementations with all required attributes (id, description, severity, apply) are loaded.

[2025-11-27 10:31:00] - Pattern: Defensive Rule Validation - Enhanced RuleLoader validation includes checks for non-empty rule attributes (id, description, severity) and proper method existence, ensuring rule instances are fully valid before being added to the engine. This prevents runtime errors from malformed rules.

[2025-11-27 10:31:00] - Pattern: Comprehensive Rule Testing - Created dedicated test suite (test_rule_validation.py) covering abstract classes, invalid rules, import errors, and edge cases. This provides a safety net for rule engine changes and ensures backward compatibility.

[2025-11-27 10:31:00] - Pattern: Rule Protocol Isolation - The abstract Rule protocol is no longer exported in __all__ lists, reinforcing its role as an interface definition only and preventing accidental instantiation.
[2025-11-27 19:59:00] - Pattern: AI Safety Isolation Layer - Comprehensive input sanitization, data filtering, and environment validation to protect against prompt injection and sensitive data exposure. Uses regex patterns for injection detection, sensitive data redaction, and environment variable checks.

[2025-11-27 19:59:00] - Pattern: JSON Schema-Based Prompt Templates - Structured prompt design using JSON schemas for consistent AI output formatting. Includes system/user roles, required/optional fields, and validation rules for explanation, remediation, CWE mapping, and severity justification.

[2025-11-27 19:59:00] - Pattern: Output Validation with Fallback - Multi-layer validation of AI-generated content with automatic fallback explanations. Validates data types, formats, ranges, and safety before integration, ensuring system reliability even when AI fails.

[2025-11-27 19:59:00] - Pattern: Rule-Based Explanation Batching - Groups security findings by rule type to minimize LLM API calls. Uses one explanation per rule type with representative finding selection, significantly reducing costs while maintaining context.

[2025-11-27 19:59:00] - Pattern: Persistent Caching with TTL - MD5-based key generation with JSON file persistence and time-to-live expiration. Supports multiple cache types (explanations, prompts, CWE) with automatic cleanup of expired entries.

[2025-11-27 19:59:00] - Pattern: Rule Metadata Enrichment - Enhanced rule system with RuleMeta structure providing rich metadata for AI explanations. Includes CWE mapping, risk factors, detection methods, false positive rates, and explanation priorities.

[2025-11-27 19:59:00] - Pattern: Comprehensive AI Testing - Mock-based testing strategy covering safety, validation, batching, and caching. Uses pytest fixtures, parameterized tests, and edge case coverage for robust AI infrastructure testing.
## [2025-11-28 01:51:00] - AI Integration Patterns for Phase 2

**Pattern: Provider Abstraction with Graceful Fallback**
- **Description:** LLM provider interface with automatic detection of configuration state
- **Implementation:** `_is_configured()` method in providers, fallback to placeholder data
- **Usage:** ExplanationEngine checks provider state before making API calls
- **Benefits:** Seamless transition between placeholder and real AI, no breaking changes

**Pattern: Safety-First AI Processing**
- **Description:** Multi-layer safety system for AI operations
- **Implementation:** SafetyLayer with input sanitization, data filtering, environment validation
- **Usage:** All AI inputs pass through safety processing before being sent to providers
- **Benefits:** Prevents accidental exposure of sensitive data, maintains privacy

**Pattern: Template-Based Prompt Engineering**
- **Description:** Structured prompt templates with variable substitution
- **Implementation:** Template files in prompts/ directory with {{variable}} placeholders
- **Usage:** ExplanationEngine.populate_template() method for dynamic prompt generation
- **Benefits:** Consistent prompt structure, easy customization, separation of concerns

**Pattern: Batch Processing for Efficiency**
- **Description:** Group findings by rule type to minimize API calls
- **Implementation:** ExplanationEngine.explain_batch() method with rule-based grouping
- **Usage:** CLI uses batch processing when multiple findings of same type are found
- **Benefits:** Reduced API costs, faster processing, better user experience

**Pattern: Validation and Fallback System**
- **Description:** Multi-stage validation of AI outputs with automatic fallbacks
- **Implementation:** OutputValidator with schema validation and fallback generation
- **Usage:** All AI responses validated before being used in findings
- **Benefits:** Robust error handling, consistent output structure, graceful degradation
## [2025-11-28 10:35:00] - Rule Architecture Integrity Patterns

**Pattern: Consolidated Rule Export Pattern**
- **Description:** Rule modules must export a consolidated `rules` list containing instantiated rule instances
- **Implementation:** Each rule module defines a `rules = [Rule1(), Rule2(), ...]` list at the bottom
- **Usage:** RuleLoader prefers the `rules` list over legacy class discovery
- **Benefits:** Prevents abstract class instantiation, enables better validation, and provides cleaner module exports

**Pattern: Abstract Class Protection**
- **Description:** RuleLoader explicitly detects and skips abstract classes and protocols
- **Implementation:** Uses `inspect.isabstract()` and name-based protocol detection
- **Usage:** Prevents instantiation of abstract Rule protocol and ABC-derived classes
- **Benefits:** Eliminates abstract class instantiation errors, improves system stability

**Pattern: Rule Protocol Isolation**
- **Description:** The abstract Rule protocol is never imported in concrete rule modules
- **Implementation:** Rule modules import only `Finding` and `RuleMeta`, not the `Rule` protocol
- **Usage:** Concrete rules implement the protocol interface without inheriting from it
- **Benefits:** Prevents accidental abstract class instantiation, reinforces interface segregation

**Pattern: Rule Pack Scaffold Detection**
- **Description:** RuleLoader automatically skips empty rule pack scaffold directories
- **Implementation:** Detects directories with only README.md and empty __init__.py files
- **Usage:** Future-proofs the architecture by ignoring unimplemented rule packs
- **Benefits:** Prevents false errors from scaffold directories, enables incremental development
## [2025-11-29 01:30:00] - Phase 2 Audit and Stabilization Patterns

**Pattern: Comprehensive Phase Audit Process**
- **Description:** Systematic 9-part audit covering placeholders, infrastructure consistency, rule system, CLI, memory bank, documentation, and test suite
- **Implementation:** Methodical sweep for TODOs, FIXMEs, placeholders, stub code, and inconsistencies across all repository files
- **Usage:** Regular codebase health checks before major version releases
- **Benefits:** Ensures codebase consistency, eliminates technical debt, and prepares for next development phase

**Pattern: Test Suite Stabilization**
- **Description:** Systematic approach to fixing test failures with root cause analysis and targeted fixes
- **Implementation:** Identified and fixed CLI test failures (help text, return codes, output expectations), rule system test failures (abstract class detection, protocol isolation), filetype detection test failures (env file detection), walker test failures (file inclusion logic, path handling), severity test failures (None handling, whitespace), and rule validation test failures (consolidated export patterns)
- **Usage:** Maintain 100% test pass rate with comprehensive test coverage (81% overall)
- **Benefits:** Reliable CI/CD pipeline, confident code changes, production-ready stability

**Pattern: Placeholder Elimination Strategy**
- **Description:** Systematic identification and resolution of all placeholder code, stub implementations, and incomplete functionality
- **Implementation:** Searched for "TODO", "FIXME", "placeholder", "pass # placeholder", "raise NotImplementedError", empty rule modules, stub LLM provider code, stub metadata blocks, incomplete prompt templates, and commented-out code
- **Usage:** Codebase quality assurance and technical debt management
- **Benefits:** Production-ready code with no hidden dependencies or incomplete features

**Pattern: AI Infrastructure Consistency**
- **Description:** Ensure complete alignment across all AI components including safety layer, prompt templates, validation, caching, batching, and provider architecture
- **Implementation:** Verified safety layer (sanitize_input, truncate_excerpt, filter_sensitive_data, ensure_no_private_keys), prompt templates (JSON-schema-based patterns), validation layer (validate_ai_output, validate_cwe_format, validate_risk_score, validate_references), caching system (.cache directory, cache_get/cache_set, TTL behavior), batching system (explain_batch, rule-type grouping, fallback behavior), and provider architecture (DeepSeekProvider fully implemented, OpenAI/Ollama clearly marked as Phase 3 TODOs)
- **Usage:** Maintain robust, secure, and efficient AI operations
- **Benefits:** Reliable AI explanations with comprehensive safety protections and graceful degradation

**Pattern: Rule System Consistency Enforcement**
- **Description:** Ensure all rules follow consistent export patterns, avoid abstract class issues, and integrate properly with RuleLoader
- **Implementation:** Verified all rules export via rules = [...] lists, no abstract class or Rule protocol imports in rule modules, RuleLoader skip logic handles abstract classes, empty folders, invalid modules, and all rule pattern tests are passing
- **Usage:** Maintain extensible and stable rule architecture
- **Benefits:** Plugin-style rule system with zero abstract instantiation errors and clean module exports

**Pattern: CLI Consistency and Documentation Alignment**
- **Description:** Ensure CLI flags, help text, and documentation are synchronized and accurate
- **Implementation:** Verified --ai, --explain, --llm-provider flags align with implementation, help text matches README documentation, no outdated flags or missing docs, and AI fallback messaging is correct
- **Usage:** Consistent user experience and accurate documentation
- **Benefits:** Clear user guidance, reduced support burden, and professional CLI interface

**Pattern: Memory Bank Synchronization**
- **Description:** Keep memory bank files updated to reflect true current state of the project
- **Implementation:** Updated activeContext.md (remove outdated references, reflect Phase 2 completion), progress.md (mark completed tasks, ensure Phase 2 tasks fully listed), decisionLog.md (record key architectural decisions from Phase 2 sweeps), systemPatterns.md (add missing patterns for rule export, batching, caching, safety, validation)
- **Usage:** Maintain project context and decision history across development sessions
## [2025-11-29 02:23:00] - Phase 2 Finalization Patterns

**Pattern: Golden Workflows Documentation**
- **Description:** Establish standardized example outputs and workflows for user education and testing
- **Implementation:** Created [`docs/examples/`](docs/examples/) directory with sample markdown and JSON reports, scrubbed of sensitive content but realistic in structure and content
- **Usage:** User onboarding, documentation examples, and regression testing reference
- **Benefits:** Clear user expectations, improved documentation quality, and consistent output validation

**Pattern: Version Management and Milestone Marking**
- **Description:** Systematic version bumping to mark significant development milestones
- **Implementation:** Synchronized version updates in [`pyproject.toml`](pyproject.toml:12) and [`src/sentinel/__init__.py`](src/sentinel/__init__.py:11) from 0.1.0 to 0.2.0 for Phase 2 completion
- **Usage:** Semantic versioning for feature releases, clear project progression tracking
- **Benefits:** Clear version history, milestone documentation, and professional release management

**Pattern: Quickstart-Optimized Documentation**
- **Description:** Condensed installation and usage instructions for rapid user onboarding
- **Implementation:** 90-second quickstart section in README.md with 3-command workflow (install, basic scan, AI scan)
- **Usage:** New user onboarding, documentation efficiency, and reduced time-to-value
- **Benefits:** Faster user adoption, improved documentation structure, and clear value proposition

**Pattern: Architecture Documentation Standardization**
- **Description:** Comprehensive system architecture documentation for development and user understanding
- **Implementation:** Created [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) with system overview, component relationships, data flow, and design patterns
- **Usage:** Development reference, user education, and architectural decision transparency
- **Benefits:** Better project understanding, easier contributor onboarding, and architectural consistency

**Pattern: Memory Bank Synchronization for Phase Transitions**
- **Description:** Systematic updating of all memory bank files during major development phase transitions
- **Implementation:** Updated productContext.md (licensing/positioning), activeContext.md (current focus), progress.md (completed tasks), decisionLog.md (architectural decisions), and systemPatterns.md (new patterns)
- **Usage:** Maintain project context across development phases and team transitions
- **Benefits:** Persistent project knowledge, accurate historical record, and smooth phase transitions
- **Benefits:** Persistent project knowledge, better collaboration, and informed decision-making
## [2025-11-29 02:56:00] - Phase 3 API Freeze Patterns

**Pattern: Frozen API Contract Design**
- **Description:** Establish a stable, forward-compatible API surface that wraps existing backend functionality without breaking changes
- **Implementation:** [`ScanService`](api-freeze-spec.md:185) class with frozen method signatures, optional parameters for new features, and semantic versioning guarantees
- **Usage:** GUI integration layer communicates exclusively through the frozen API contract
- **Benefits:** Stable interface for GUI development, backward compatibility, future-proof design

**Pattern: Enhanced Finding Data Model**
- **Description:** Extend basic finding structure with GUI-specific metadata while maintaining backward compatibility
- **Implementation:** [`EnhancedFinding`](api-freeze-spec.md:67) dataclass with optional fields for AI explanations, code context, resolution tracking, and user notes
- **Usage:** All findings processed through the API are converted to enhanced format with GUI-optimized metadata
- **Benefits:** Rich display capabilities, user interaction tracking, persistent state management

**Pattern: Real-time Event Streaming**
- **Description:** Progressive result delivery through event-based streaming for large scans
- **Implementation:** [`ScanEvent`](api-freeze-spec.md:397) system with WebSocket-compatible event types and structured payloads
- **Usage:** GUI receives live updates during scanning including progress, findings, and completion events
- **Benefits:** Responsive user experience, memory efficiency for large result sets, cancellation support

**Pattern: Graceful Error Hierarchy**
- **Description:** Structured error handling with user-friendly messages and consistent error codes
- **Implementation:** [`CodeSentinelError`](api-freeze-spec.md:445) base class with specialized subclasses for different failure scenarios
- **Usage:** All API operations raise specific error types with actionable error messages
- **Benefits:** Consistent error handling, detailed debugging information, user-friendly error reporting

**Pattern: Shared Configuration Model**
- **Description:** Unified configuration system for both GUI and CLI with synchronized persistence
- **Implementation:** [`SharedConfig`](api-freeze-spec.md:702) dataclass with platform-specific storage and synchronization mechanisms
- **Usage:** Both GUI and CLI read/write from the same configuration store with conflict resolution
- **Benefits:** Consistent user experience, configuration synchronization, reduced duplication

**Pattern: AI Safety Controller**
- **Description:** Centralized safety controls for AI operations with privacy and security guarantees
- **Implementation:** [`AISafetyController`](api-freeze-spec.md:619) with input validation, content sanitization, and environment safety checks
- **Usage:** All AI operations pass through safety layer before reaching external providers
- **Benefits:** Privacy protection, prompt injection prevention, graceful degradation

**Pattern: Backend Module Wrapping**
- **Description:** Transparent wrapping of existing backend functions with enhanced error handling and progress tracking
- **Implementation:** [`ScanServiceImplementation`](api-freeze-spec.md:518) wraps [`walk_directory()`](src/sentinel/scanner/walker.py:36), [`run_rules()`](src/sentinel/scanner/engine.py:271), and [`ExplanationEngine`](src/sentinel/llm/explainer.py:20)
- **Usage:** Internal backend functions are called through API wrapper layer with added functionality
- **Benefits:** Zero breaking changes to existing code, enhanced functionality, consistent error handling
## Dogfooding Automation Patterns

### Automated Dogfooding Runner
- **Location**: [`tools/dogfood_runner.py`](tools/dogfood_runner.py) (planned)
- **Design**: Standard library only, dependency-free implementation
- **Purpose**: Automate systematic testing of CodeSentinel across multiple scenarios
- **Architecture**: Scenario-based execution with comprehensive logging and error handling

### Scenario Matrix Pattern
- **Core Scenarios**: 5 scenarios from dogfooding-experiment-plan.md
- **Additional Scenarios**: 2 extra scenarios for enhanced coverage
- **AI Integration**: Conditional AI scenario execution based on API key availability
- **Output Structure**: Consistent directory hierarchy with timestamp-based organization

### Error Handling Pattern
- **Isolation**: Independent scenario execution with no cross-scenario dependencies
- **Graceful Failure**: Continue execution on individual scenario failures
- **Timeout Protection**: Configurable timeouts per scenario
- **Validation**: Pre-execution environment validation and dependency checking

### Output Organization Pattern
- **Structured Output**: Consistent directory structure across all runs
- **Metadata Tracking**: Comprehensive run metadata and configuration
- **Logging**: Detailed execution logs with timestamps and performance metrics
- **Summary Generation**: Automated summary reports with findings analysis

2025-11-29 04:16:00 - Added dogfooding automation patterns for automated testing runner
## 2025-11-29 06:55:47 - Robust JSON Extraction Pattern

**Pattern:** Advanced JSON extraction with brace counting and string escape handling for log-contaminated output

**Context:** Command-line tools often output log messages before JSON data, breaking simple JSON parsing. This pattern provides resilience for subprocess integration.

**Implementation:**
```python
def _extract_json_from_output(output: str) -> str:
    """Extract JSON from output that may contain log messages."""
    brace_count = 0
    in_string = False
    escape_next = False
    json_start = -1
    
    for i, char in enumerate(output):
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\' and in_string:
            escape_next = True
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            
        if not in_string:
            if char == '{':
                if brace_count == 0:
                    json_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and json_start != -1:
                    return output[json_start:i+1]
    
    return output  # Fallback to original if no complete JSON found
```

**Key Features:**
- Handles log message prefixes and suffixes
- Respects string literals to avoid false brace counting
- Manages escape sequences within strings
- Graceful degradation for malformed JSON

**Usage:**
- Subprocess command output parsing
- CLI tool integration
- Automated testing frameworks
- Log analysis with structured data output

**Benefits:**
- Resilient to tool output variations
- Maintains data integrity
- Provides accurate structured data extraction
- Enables reliable automation pipelines
## [2025-11-30 17:05:00] - Phase 2.5 Rule Hardening Patterns

**Pattern: Provider-Aware Token Classification**
- **Description:** Systematically classify security tokens by provider and type for intelligent deduplication
- **Implementation:** [`token_types.py`](src/sentinel/rules/token_types.py) module with provider classification (AWS, Azure, GCP, Stripe, generic, OAuth, high-entropy)
- **Usage:** Rule engine uses classification to determine precedence during deduplication
- **Benefits:** 67.8% duplicate reduction, resolved Azure rule over-matching, enhanced accuracy

**Pattern: Precedence-Based Deduplication**
- **Description:** Use hierarchical precedence model to select highest-quality findings during deduplication
- **Implementation:** Precedence scores: provider-specific (100) > OAuth tokens (90) > generic API keys (80) > high-entropy strings (70) > configuration rules (60)
- **Usage:** Rule engine groups findings by token and preserves highest-precedence finding
- **Benefits:** Eliminates duplicate reporting while preserving most relevant findings

**Pattern: Token Grouping by Normalized Content**
- **Description:** Group findings by file context, line position, and normalized token content for precise deduplication
- **Implementation:** Grouping key: (file_path, line_number, normalized_excerpt) with O(n) complexity algorithm
- **Usage:** Deduplication engine identifies identical tokens across different rules
- **Benefits:** Accurate duplicate detection, handles partial obfuscation and token variations

**Pattern: Backward-Compatible Rule Enhancement**
- **Description:** Add advanced capabilities to rule engine without breaking existing API or functionality
- **Implementation:** Additive architecture with optional deduplication, preserved API signatures, enhanced finding data without structural changes
- **Usage:** Existing integrations continue working while gaining improved accuracy
- **Benefits:** Zero breaking changes, smooth upgrade path, production-ready stability

**Pattern: Quantitative Rule Validation**
- **Description:** Use empirical data and dogfooding to validate rule improvements and quantify results
- **Implementation:** Automated dogfooding with 7-scenario matrix, accurate findings counting, performance tracking
- **Usage:** Systematic validation of 67.8% duplicate reduction and performance consistency
- **Benefits:** Empirical confidence in improvements, quality assurance, foundation for regression testing

**Pattern: Rule Collision Resolution**
- **Description:** Systematically resolve cases where single tokens trigger multiple rules through provider-aware classification
- **Implementation:** Identify 12 high-collision tokens, apply precedence model to select single most relevant finding
- **Usage:** Rule engine handles complex token collisions without user intervention
- **Benefits:** Reduced noise, improved user experience, more actionable security findings

**Pattern: Enhanced Detection with Partial Obfuscation Handling**
- **Description:** Improve detection of partially obfuscated tokens like JWT and PEM through enhanced pattern matching
- **Implementation:** Extended regex patterns with edge case handling, improved false positive reduction
- **Usage:** All secret detection rules benefit from enhanced pattern recognition
- **Benefits:** Better detection of real security issues, reduced false negatives

**Pattern: Comprehensive Deduplication Testing**
- **Description:** Extensive test coverage for deduplication logic covering all edge cases and scenarios
- **Implementation:** [`test_deduplication.py`](tests/unit/test_deduplication.py) with 590 lines covering precedence, grouping, edge cases, and performance
- **Usage:** Automated validation of deduplication accuracy and performance
- **Benefits:** Production-ready confidence, comprehensive edge case coverage, regression protection
## [2025-12-01 03:12:03] - Phase 2.7 Rule Expansion Patterns

**Pattern: Specialized Misconfiguration Precedence**
- **Description:** Establishment of a new precedence level for structure-aware configuration rules to sit hierarchically between generic secrets and basic config rules.
- **Implementation:** Precedence score set at **65** for rules in the GHA, DOC, JSC, and TFC rule packs.
- **Usage:** Ensures high visibility for critical misconfigurations that require language context.
- **Benefits:** Accurate prioritization and deduplication across different finding types.

**Pattern: Structure-Aware Rule Scanning Requirement**
- **Description:** Introduction of rules that require structural context (e.g., YAML nesting, Dockerfile instruction block, HCL resource context) rather than purely regex-based detection.
- **Implementation:** Phase 2.7 development must incorporate or utilize parsing mechanisms (e.g., lightweight YAML/JSON/HCL parsing) for targeted file types to reduce false positives and improve accuracy in configuration rules.
- **Usage:** Applied to files like `Dockerfile`, `.github/workflows/*.yml`, `package.json`, and `*.tf`.
- **Benefits:** Enables effective detection of IaC, CI/CD, and Supply Chain security flaws that plaintext matching misses.
## [2025-12-14 00:30:00] - Open-Source Community Contribution Patterns

**Pattern: Fork-and-PR Contribution Model**
- **Description:** Standard GitHub fork, branch, and pull request workflow for community contributions
- **Implementation:** Contributors fork repository, make changes in feature branches, and submit PRs
- **Usage:** All external contributions follow this model to ensure proper review and integration
- **Benefits:** Clear contribution path, isolated development, quality control through reviews

**Pattern: Community Rule Pack Development**
- **Description:** Dedicated process for community-contributed security rule packs
- **Implementation:** Template-based rule pack creation with standardized documentation and tests
- **Usage:** Security researchers and community members extend scanning capabilities
- **Benefits:** Expanded detection coverage, specialized expertise, community ownership

**Pattern: Transparent Issue Tracking**
- **Description:** All development planning and bug tracking in public GitHub issues
- **Implementation:** Categorized issue templates for bugs, features, and rule suggestions
- **Usage:** Users report issues, request features, and track development progress openly
- **Benefits:** Community prioritization, transparent roadmap, shared problem-solving

**Pattern: Governance Through Code Owners**
- **Description:** Defined areas of responsibility through GitHub CODEOWNERS file
- **Implementation:** Core components assigned to maintainers with review requirements
- **Usage:** PRs automatically request reviews from appropriate code owners
- **Benefits:** Consistent quality control, expertise-based reviews, clear responsibility

**Pattern: Community Documentation Contributions**
- **Description:** Wiki-style contribution system for documentation improvements
- **Implementation:** Documentation in Markdown format with simplified PR process
- **Usage:** Users improve documentation based on their experiences and needs
- **Benefits:** Better documentation quality, reduced maintainer burden, community perspective

**Pattern: Versioned Releases with Changelog**
- **Description:** Regular versioned releases with comprehensive changelogs
- **Implementation:** Semantic versioning with GitHub Releases feature
- **Usage:** Users and tools reference specific versions with clear upgrade paths
- **Benefits:** Stability for users, clear communication of changes, dependency management