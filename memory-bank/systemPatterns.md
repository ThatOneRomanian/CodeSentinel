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

* **Private Git Repository**: Using private Git repository for development with proper .gitignore for Python + VS Code
* **Memory-Bank Driven Development**: Using memory-bank pattern for persistent project context and decision tracking
* **Private Development Workflow**: Internal development only, with proprietary licensing during development phase