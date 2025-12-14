# Contributing to CodeSentinel

Thank you for your interest in contributing to CodeSentinel! We welcome contributions from the community and are excited to work with you to make CodeSentinel better.

## Welcome

CodeSentinel is a local-first security scanner designed to help developers identify security vulnerabilities and misconfigurations in their code. Whether you're reporting bugs, suggesting features, improving documentation, or contributing code, your help is appreciated.

## How to Report Bugs

If you find a bug in CodeSentinel, please help us fix it by following these steps:

1. **Check existing issues** - Search our [GitHub Issues](https://github.com/username/CodeSentinel/issues) to see if the bug has already been reported.

2. **Create a detailed bug report** - If the issue doesn't exist, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce the bug
   - Expected behavior vs. actual behavior
   - Your environment details (OS, Python version, CodeSentinel version)
   - Sample code or files that trigger the bug (if applicable)
   - Any error messages or logs

3. **Use the bug report template** - We provide issue templates to help you include all necessary information.

## How to Request Features

We welcome feature requests! To suggest a new feature:

1. **Check existing feature requests** - Look through our issues to see if someone has already suggested your idea.

2. **Create a feature request** - If it's a new idea, open an issue with:
   - A clear description of the feature
   - The problem it solves or use case it addresses
   - Any implementation ideas you might have
   - Examples of how the feature would be used

## Development Setup

To set up CodeSentinel for development:

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/CodeSentinel.git
   cd CodeSentinel
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies**
   ```bash
   pip install pytest pytest-cov
   ```

5. **Verify installation**
   ```bash
   codesentinel --version
   codesentinel scan --help
   ```

## Code Style Guidelines

We maintain consistent code quality through these guidelines:

### Python Code Standards

- **Follow PEP 8** - Use Python's official style guide
- **Use type hints** - All function signatures should include type annotations
- **Write docstrings** - Use Google-style docstrings for all public functions and classes
- **Follow existing patterns** - Look at existing code to understand our conventions

### Code Quality

- **Keep functions focused** - Each function should have a single, clear purpose
- **Use meaningful names** - Variable and function names should be descriptive
- **Handle errors gracefully** - Use specific exceptions with clear error messages
- **Add comments for complex logic** - Explain the "why" not just the "what"

### Example Code Style

```python
def scan_directory(path: Path, ignore_patterns: List[str] = None) -> List[Finding]:
    """Scan a directory for security vulnerabilities.
    
    Args:
        path: Directory path to scan
        ignore_patterns: Optional list of patterns to ignore
        
    Returns:
        List of security findings
        
    Raises:
        InvalidPathError: If the path doesn't exist or isn't accessible
    """
    if ignore_patterns is None:
        ignore_patterns = []
    
    # Implementation here...
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** - Follow our code style guidelines

3. **Write or update tests** - Ensure your changes are covered by tests

4. **Run the test suite**
   ```bash
   pytest
   ```

5. **Update documentation** - If you're adding features or changing behavior

### Submitting Your Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request** with:
   - A clear title describing the change
   - A detailed description of what you've changed and why
   - References to any related issues
   - Screenshots or examples if applicable

3. **Respond to feedback** - Be prepared to make changes based on code review

### Pull Request Requirements

- All tests must pass
- Code coverage should not decrease significantly
- Follow our code style guidelines
- Include appropriate documentation updates
- Commit messages should be clear and descriptive

## Testing Requirements

We maintain high code quality through comprehensive testing:

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/sentinel

# Run specific test file
pytest tests/unit/test_scanner.py

# Run tests matching a pattern
pytest -k "test_rule_engine"
```

### Writing Tests

- **Write tests for new features** - All new functionality should have corresponding tests
- **Test edge cases** - Consider error conditions and boundary cases
- **Use descriptive test names** - Test names should clearly describe what they're testing
- **Follow existing test patterns** - Look at existing tests for examples

### Test Organization

- Unit tests go in `tests/unit/`
- Integration tests go in `tests/integration/`
- Test files should be named `test_*.py`
- Test functions should be named `test_*`

## Community Guidelines

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** - Treat all community members with respect and kindness
- **Be constructive** - Provide helpful feedback and suggestions
- **Be patient** - Remember that everyone has different experience levels
- **Follow our Code of Conduct** - See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details

## Getting Help

If you need help with contributing:

- **Check the documentation** - Look at our README and architecture docs
- **Ask questions in issues** - Feel free to ask for clarification on existing issues
- **Join discussions** - Participate in GitHub Discussions for broader topics

## Recognition

We appreciate all contributions! Contributors will be:

- Listed in our contributors section
- Mentioned in release notes for significant contributions
- Invited to join our contributor community

## Development Workflow

### Typical Contribution Workflow

1. Find or create an issue to work on
2. Comment on the issue to let others know you're working on it
3. Fork the repository and create a feature branch
4. Make your changes following our guidelines
5. Write tests and ensure they pass
6. Submit a pull request
7. Respond to code review feedback
8. Celebrate when your contribution is merged! 🎉

### Branch Naming

Use descriptive branch names:
- `feature/add-docker-scanning` - for new features
- `fix/memory-leak-in-scanner` - for bug fixes
- `docs/update-installation-guide` - for documentation updates

### Commit Messages

Write clear commit messages:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests when applicable

Thank you for contributing to CodeSentinel! Your efforts help make security scanning more accessible to developers everywhere.