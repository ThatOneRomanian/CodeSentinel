"""
Unit tests for the Rule Engine module.

Tests rule discovery, loading, application, error handling, and finding normalization
according to the Phase 1 specification.
"""

import os
import tempfile
import pathlib
import pytest
from unittest.mock import patch, MagicMock

from sentinel.scanner.engine import RuleLoader, run_rules
from sentinel.rules.base import Finding


class TestRuleLoader:
    """Test suite for RuleLoader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_rules_dir = pathlib.Path(self.temp_dir) / "test_rules"
        self.test_rules_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_rules_valid_directory(self):
        """Test loading rules from a valid directory."""
        # Create test rule files
        rule1_file = self.test_rules_dir / "test_rule1.py"
        rule1_file.write_text("""
class TestRule1:
    def __init__(self):
        self.id = "TEST_RULE_1"
        self.description = "Test rule 1"
        self.severity = "low"

    def apply(self, path, text):
        return []
""")

        rule2_file = self.test_rules_dir / "test_rule2.py"
        rule2_file.write_text("""
class TestRule2:
    def __init__(self):
        self.id = "TEST_RULE_2"
        self.description = "Test rule 2"
        self.severity = "medium"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        assert len(rules) == 2
        rule_ids = [rule.id for rule in rules]
        assert "TEST_RULE_1" in rule_ids
        assert "TEST_RULE_2" in rule_ids


class TestRunRules:
    """Test suite for run_rules function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_with_findings(self, mock_loader):
        """Test run_rules with files that generate findings."""
        # Create test files
        file1 = pathlib.Path(self.temp_dir) / "test1.py"
        file1.write_text("TEST_PATTERN_123\nLINE_NUMBER_456")

        file2 = pathlib.Path(self.temp_dir) / "test2.py"
        file2.write_text("TEST_PATTERN_789")

        # Create a simple test rule class directly
        class TestSimpleRule:
            def __init__(self):
                self.id = "TEST_SIMPLE_RULE"
                self.description = "Test rule that returns findings for specific patterns"
                self.severity = "low"

            def apply(self, path, text):
                findings = []
                lines = text.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if "TEST_PATTERN_" in line:
                        confidence = 0.9 if "123" in line else 0.8
                        findings.append(Finding(
                            rule_id=self.id,
                            file_path=path,
                            line=line_num,
                            severity=self.severity,
                            excerpt=line.strip(),
                            confidence=confidence
                        ))
                    elif "LINE_NUMBER_" in line:
                        findings.append(Finding(
                            rule_id=self.id,
                            file_path=path,
                            line=line_num,
                            severity=self.severity,
                            excerpt=line.strip(),
                            confidence=0.7
                        ))
                return findings

        # Mock the rule loader to return our test rules
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load_rules.return_value = [TestSimpleRule()]

        findings = run_rules([file1, file2])

        # Should find 3 patterns total
        assert len(findings) == 3
        assert all(isinstance(f, Finding) for f in findings)

        # Verify finding structure
        for finding in findings:
            assert finding.rule_id == "TEST_SIMPLE_RULE"
            assert finding.file_path in [file1, file2]
            assert finding.severity == "low"
            assert finding.excerpt is not None
            assert finding.confidence in [0.9, 0.8, 0.7]

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_empty_findings(self, mock_loader):
        """Test run_rules with files that generate no findings."""
        # Create test file with no patterns
        file1 = pathlib.Path(self.temp_dir) / "test.py"
        file1.write_text("normal content without patterns")

        # Create a simple test rule class directly
        class TestSimpleRule:
            def __init__(self):
                self.id = "TEST_SIMPLE_RULE"
                self.description = "Test rule that returns findings for specific patterns"
                self.severity = "low"

            def apply(self, path, text):
                return []

        # Mock the rule loader to return test rules
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load_rules.return_value = [TestSimpleRule()]

        findings = run_rules([file1])

        assert len(findings) == 0

    @patch('sentinel.scanner.engine.RuleLoader')
    def test_run_rules_error_handling(self, mock_loader):
        """Test run_rules error handling when rules raise exceptions."""
        # Create test file that triggers errors
        file1 = pathlib.Path(self.temp_dir) / "test.py"
        file1.write_text("RAISE_VALUE_ERROR")

        # Create an error test rule class directly
        class TestErrorRule:
            def __init__(self):
                self.id = "TEST_ERROR_RULE"
                self.description = "Test rule that raises exceptions for error handling"
                self.severity = "high"

            def apply(self, path, text):
                if "RAISE_VALUE_ERROR" in text:
                    raise ValueError("Test value error from TestErrorRule")
                return []

        # Mock the rule loader to return error rule
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load_rules.return_value = [TestErrorRule()]

        # Should not raise exception, should handle gracefully
        findings = run_rules([file1])

        # No findings should be returned due to the error
        assert len(findings) == 0


if __name__ == "__main__":
    pytest.main([__file__])
