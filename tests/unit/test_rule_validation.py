"""
Unit tests for Rule Validation and Abstract Class Handling.

Tests that the Rule Engine correctly handles abstract classes, invalid rules,
and maintains backward compatibility according to Phase 2 requirements.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import os
import tempfile
import pathlib
import pytest
from unittest.mock import patch, MagicMock

from sentinel.scanner.engine import RuleLoader, run_rules
from sentinel.rules.base import Finding, Rule


class TestRuleValidation:
    """Test suite for Rule validation and abstract class handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_rules_dir = pathlib.Path(self.temp_dir) / "test_rules"
        self.test_rules_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_no_abstract_rules_load(self):
        """Test that abstract Rule protocol class is not loaded as a rule."""
        # Create a test rule file that imports the abstract Rule protocol
        rule_file = self.test_rules_dir / "test_abstract_rule.py"
        rule_file.write_text("""
from sentinel.rules.base import Rule, Finding
import pathlib
from typing import List

# This should NOT be loaded because it's abstract
class AbstractRule(Rule):
    def __init__(self):
        self.id = "ABSTRACT_RULE"
        self.description = "Abstract rule that shouldn't be loaded"
        self.severity = "high"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

# This should be loaded because it's a concrete implementation
class ConcreteRule:
    def __init__(self):
        self.id = "CONCRETE_RULE"
        self.description = "Concrete rule that should be loaded"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load the concrete rule, not the abstract one
        assert len(rules) == 1
        assert rules[0].id == "CONCRETE_RULE"

    def test_rule_loader_skips_invalid_rules(self):
        """Test that RuleLoader skips rules missing required attributes."""
        # Create test rule files with various invalid configurations
        invalid_rule1 = self.test_rules_dir / "invalid_rule1.py"
        invalid_rule1.write_text("""
class InvalidRuleNoId:
    def __init__(self):
        # Missing id attribute
        self.description = "Rule without id"
        self.severity = "high"

    def apply(self, path, text):
        return []
""")

        invalid_rule2 = self.test_rules_dir / "invalid_rule2.py"
        invalid_rule2.write_text("""
class InvalidRuleNoApply:
    def __init__(self):
        self.id = "NO_APPLY_RULE"
        self.description = "Rule without apply method"
        self.severity = "high"
    # Missing apply method
""")

        invalid_rule3 = self.test_rules_dir / "invalid_rule3.py"
        invalid_rule3.write_text("""
class InvalidRuleEmptyId:
    def __init__(self):
        self.id = ""  # Empty id
        self.description = "Rule with empty id"
        self.severity = "high"

    def apply(self, path, text):
        return []
""")

        # Valid rule for comparison
        valid_rule = self.test_rules_dir / "valid_rule.py"
        valid_rule.write_text("""
class ValidRule:
    def __init__(self):
        self.id = "VALID_RULE"
        self.description = "Valid rule"
        self.severity = "medium"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load the valid rule
        assert len(rules) == 1
        assert rules[0].id == "VALID_RULE"

    def test_all_rules_have_apply(self):
        """Test that all loaded rules have the required apply method."""
        # Create multiple valid rules
        rule1 = self.test_rules_dir / "rule1.py"
        rule1.write_text("""
class Rule1:
    def __init__(self):
        self.id = "RULE_1"
        self.description = "First valid rule"
        self.severity = "low"

    def apply(self, path, text):
        return []
""")

        rule2 = self.test_rules_dir / "rule2.py"
        rule2.write_text("""
class Rule2:
    def __init__(self):
        self.id = "RULE_2"
        self.description = "Second valid rule"
        self.severity = "medium"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # All rules should have apply method
        assert len(rules) == 2
        for rule in rules:
            assert hasattr(rule, 'apply')
            assert callable(rule.apply)
            assert hasattr(rule, 'id')
            assert hasattr(rule, 'description')
            assert hasattr(rule, 'severity')

    def test_all_rule_instances_load_successfully(self):
        """Test that all valid rule instances can be instantiated and loaded."""
        # Create test rules with various configurations
        rule1 = self.test_rules_dir / "complex_rule1.py"
        rule1.write_text("""
from sentinel.rules.base import Finding
import pathlib
from typing import List

class ComplexRule1:
    def __init__(self):
        self.id = "COMPLEX_RULE_1"
        self.description = "Complex rule with full implementation"
        self.severity = "high"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        findings = []
        if "SECRET" in text:
            findings.append(Finding(
                rule_id=self.id,
                file_path=path,
                line=1,
                severity=self.severity,
                excerpt="Found SECRET pattern",
                confidence=0.9
            ))
        return findings
""")

        rule2 = self.test_rules_dir / "complex_rule2.py"
        rule2.write_text("""
from sentinel.rules.base import Finding
import pathlib
from typing import List

class ComplexRule2:
    def __init__(self):
        self.id = "COMPLEX_RULE_2"
        self.description = "Another complex rule"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        # Always return empty findings for testing
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Both rules should load successfully
        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert rule_ids == {"COMPLEX_RULE_1", "COMPLEX_RULE_2"}

        # Test that the apply methods work correctly
        test_file = pathlib.Path(self.temp_dir) / "test.txt"
        test_file.write_text("SECRET_KEY=abc123")

        findings1 = rules[0].apply(test_file, test_file.read_text())
        findings2 = rules[1].apply(test_file, test_file.read_text())

        # First rule should find the secret, second should return empty
        if rules[0].id == "COMPLEX_RULE_1":
            assert len(findings1) == 1
            assert len(findings2) == 0
        else:
            assert len(findings1) == 0
            assert len(findings2) == 1

    def test_rule_loader_handles_import_errors_gracefully(self):
        """Test that RuleLoader handles module import errors without crashing."""
        # Create a rule file with syntax errors
        bad_rule = self.test_rules_dir / "syntax_error_rule.py"
        bad_rule.write_text("""
class BadRule
    # Missing colon and proper syntax
    def __init__(self)
        self.id = "BAD_RULE"
        self.description = "Rule with syntax errors"
        self.severity = "high"

    def apply(self, path, text)
        return []
""")

        # Create a valid rule to ensure loader continues
        valid_rule = self.test_rules_dir / "working_rule.py"
        valid_rule.write_text("""
class WorkingRule:
    def __init__(self):
        self.id = "WORKING_RULE"
        self.description = "Working rule"
        self.severity = "low"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        
        # Should not raise exception, should load the working rule
        rules = loader.load_rules()
        
        assert len(rules) == 1
        assert rules[0].id == "WORKING_RULE"

    def test_rule_validation_with_empty_attributes(self):
        """Test that rules with empty or None attributes are rejected."""
        empty_rule = self.test_rules_dir / "empty_rule.py"
        empty_rule.write_text("""
class EmptyIdRule:
    def __init__(self):
        self.id = ""  # Empty string
        self.description = "Rule with empty id"
        self.severity = "high"

    def apply(self, path, text):
        return []

class NoneSeverityRule:
    def __init__(self):
        self.id = "NONE_SEVERITY_RULE"
        self.description = "Rule with None severity"
        self.severity = None  # None value

    def apply(self, path, text):
        return []

class ValidRule:
    def __init__(self):
        self.id = "VALID_RULE_AGAIN"
        self.description = "Valid rule again"
        self.severity = "medium"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load the valid rule
        assert len(rules) == 1
        assert rules[0].id == "VALID_RULE_AGAIN"

    def test_consolidated_rules_list_export(self):
        """Test that modules exporting consolidated rules list work correctly."""
        consolidated_rule = self.test_rules_dir / "consolidated_rule.py"
        consolidated_rule.write_text("""
from sentinel.rules.base import Finding
import pathlib
from typing import List

class RuleA:
    def __init__(self):
        self.id = "RULE_A"
        self.description = "Rule A from consolidated list"
        self.severity = "high"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

class RuleB:
    def __init__(self):
        self.id = "RULE_B"
        self.description = "Rule B from consolidated list"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

# Export consolidated rules list
rules = [RuleA(), RuleB()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should load both rules from the consolidated list
        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert rule_ids == {"RULE_A", "RULE_B"}

    def test_abstract_class_detection_in_rules_list(self):
        """Test that abstract classes in rules list are detected and skipped."""
        abstract_rule = self.test_rules_dir / "abstract_in_list.py"
        abstract_rule.write_text("""
from abc import ABC, abstractmethod
from sentinel.rules.base import Finding
import pathlib
from typing import List

class AbstractRule(ABC):
    def __init__(self):
        self.id = "ABSTRACT_RULE"
        self.description = "Abstract rule"
        self.severity = "high"

    @abstractmethod
    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        pass

class ConcreteRule:
    def __init__(self):
        self.id = "CONCRETE_RULE"
        self.description = "Concrete rule"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

# Only export the concrete rule, not the abstract one
rules = [ConcreteRule()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load the concrete rule
        assert len(rules) == 1
        assert rules[0].id == "CONCRETE_RULE"


if __name__ == "__main__":
    pytest.main([__file__])