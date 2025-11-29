"""
Unit tests for the Rule Engine.

Tests rule discovery, loading, application, and error handling using
mock rules defined inline to avoid import issues.
"""

import pathlib
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from sentinel.rules.base import Finding, Rule
from sentinel.scanner.engine import RuleLoader, run_rules


# Define test rule classes inline to avoid import issues
# Using "Mock" prefix to avoid pytest collection warnings
class MockSimpleRule:
    """Simple test rule that finds patterns in text."""

    def __init__(self):
        self.id = "MOCK_SIMPLE_RULE"
        self.description = "Mock simple rule for pattern matching"
        self.severity = "medium"

    def apply(self, path, text):
        findings = []
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            if "TEST_PATTERN" in line:
                findings.append(Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=i,
                    severity=self.severity,
                    excerpt=line.strip(),
                    confidence=0.8
                ))
        return findings


class MockEmptyRule:
    """Test rule that never finds anything."""

    def __init__(self):
        self.id = "MOCK_EMPTY_RULE"
        self.description = "Mock rule that returns no findings"
        self.severity = "low"

    def apply(self, path, text):
        return []


class MockErrorRule:
    """Test rule that raises exceptions."""

    def __init__(self):
        self.id = "MOCK_ERROR_RULE"
        self.description = "Mock rule that raises exceptions"
        self.severity = "high"

    def apply(self, path, text):
        if "RAISE_VALUE_ERROR" in text:
            raise ValueError("Test error from rule")
        return []


class TestRuleLoader:
    """Test cases for RuleLoader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_rules_dir = pathlib.Path(tempfile.mkdtemp())
        # Create __init__.py to make it a package
        (self.test_rules_dir / "__init__.py").write_text("# Test rules package")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_rules_dir)

    def test_load_rules_valid_directory(self):
        """Test loading rules from a valid directory."""
        # Create test rule files
        rule1_file = self.test_rules_dir / "test_rule1.py"
        rule1_file.write_text('''
class TestRule1:
    def __init__(self):
        self.id = "TEST_RULE_1"
        self.description = "Test rule 1"
        self.severity = "low"

    def apply(self, path, text):
        return []
''')

        rule2_file = self.test_rules_dir / "test_rule2.py"
        rule2_file.write_text('''
class TestRule2:
    def __init__(self):
        self.id = "TEST_RULE_2"
        self.description = "Test rule 2"
        self.severity = "medium"

    def apply(self, path, text):
        return []
''')

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert "TEST_RULE_1" in rule_ids
        assert "TEST_RULE_2" in rule_ids

    def test_load_rules_skips_base_and_init(self):
        """Test that base.py and __init__.py are skipped."""
        # Create files that should be skipped
        base_file = self.test_rules_dir / "base.py"
        base_file.write_text('''
class BaseRule:
    pass
''')

        init_file = self.test_rules_dir / "__init__.py"
        init_file.write_text("# Empty init")

        # Create a valid rule file
        valid_rule = self.test_rules_dir / "valid_rule.py"
        valid_rule.write_text('''
class ValidRule:
    def __init__(self):
        self.id = "VALID_RULE"
        self.description = "Valid rule"
        self.severity = "low"

    def apply(self, path, text):
        return []
''')

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        assert len(rules) == 1
        assert rules[0].id == "VALID_RULE"

    def test_load_rules_invalid_directory(self):
        """Test loading rules from non-existent directory."""
        invalid_dir = pathlib.Path("/nonexistent/directory")
        loader = RuleLoader(invalid_dir)

        with pytest.raises(FileNotFoundError):
            loader.load_rules()

    def test_load_rules_file_instead_of_directory(self):
        """Test loading rules when path is a file, not directory."""
        file_path = self.test_rules_dir / "not_a_dir.py"
        file_path.write_text("# Not a directory")

        loader = RuleLoader(file_path)

        with pytest.raises(ValueError):
            loader.load_rules()


class TestRunRules:
    """Test cases for run_rules function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_with_findings(self, mock_loader):
        """Test run_rules with files that generate findings."""
        # Create test files
        file1 = pathlib.Path(self.temp_dir) / "test1.py"
        file1.write_text("TEST_PATTERN_123\nLINE_NUMBER_456")

        file2 = pathlib.Path(self.temp_dir) / "test2.py"
        file2.write_text("TEST_PATTERN_789")

        # Mock the rule loader to return our test rules
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_rules.return_value = [MockSimpleRule()]
        mock_loader.return_value = mock_loader_instance

        files = [file1, file2]
        findings = run_rules(files)

        # Should find 2 patterns total: one in file1 (line 1), one in file2 (line 1)
        assert len(findings) == 2
        assert all(isinstance(f, Finding) for f in findings)
        assert all(f.rule_id == "MOCK_SIMPLE_RULE" for f in findings)

        # Verify file paths and line numbers
        file1_finding = next(f for f in findings if str(f.file_path) == str(file1))
        file2_finding = next(f for f in findings if str(f.file_path) == str(file2))
        assert file1_finding.line == 1
        assert file2_finding.line == 1

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_empty_findings(self, mock_loader):
        """Test run_rules with files that generate no findings."""
        # Create test file with no patterns
        file1 = pathlib.Path(self.temp_dir) / "test.py"
        file1.write_text("normal content without patterns")

        # Mock the rule loader to return test rules
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_rules.return_value = [MockEmptyRule()]
        mock_loader.return_value = mock_loader_instance

        files = [file1]
        findings = run_rules(files)

        assert len(findings) == 0

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_error_handling(self, mock_loader):
        """Test run_rules error handling when rules raise exceptions."""
        # Create test file that triggers errors
        file1 = pathlib.Path(self.temp_dir) / "test.py"
        file1.write_text("RAISE_VALUE_ERROR")

        # Mock the rule loader to return error rule
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_rules.return_value = [MockErrorRule()]
        mock_loader.return_value = mock_loader_instance

        files = [file1]
        findings = run_rules(files)

        # Should handle the error gracefully and continue
        assert len(findings) == 0

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_nonexistent_file(self, mock_loader):
        """Test run_rules with nonexistent files."""
        nonexistent_file = pathlib.Path(self.temp_dir) / "nonexistent.py"

        # Mock the rule loader to return empty rules
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_rules.return_value = [MockEmptyRule()]
        mock_loader.return_value = mock_loader_instance

        files = [nonexistent_file]
        findings = run_rules(files)

        # Should handle nonexistent file gracefully
        assert len(findings) == 0

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_no_rules_loaded(self, mock_loader):
        """Test run_rules when no rules are loaded."""
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_rules.return_value = []
        mock_loader.return_value = mock_loader_instance

        with pytest.raises(RuntimeError, match="No rules were successfully loaded"):
            run_rules([pathlib.Path("test.py")])
