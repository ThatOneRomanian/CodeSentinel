"""
Unit tests for Rule Export Patterns and Architecture Integrity.

Tests that enforce the consolidated rule export pattern and prevent
abstract class instantiation regressions.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import os
import tempfile
import pathlib
import pytest
from unittest.mock import patch, MagicMock

from sentinel.scanner.engine import RuleLoader, run_rules
from sentinel.rules.base import Finding, Rule


class TestRuleExportPatterns:
    """Test suite for rule export patterns and architecture integrity."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_rules_dir = pathlib.Path(self.temp_dir) / "test_rules"
        self.test_rules_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rule_modules_export_rules_list(self):
        """Test that rule modules properly export consolidated rules list."""
        # Create a module with proper rules list export
        proper_module = self.test_rules_dir / "proper_module.py"
        proper_module.write_text("""
from sentinel.rules.base import Finding
import pathlib
from typing import List

class Rule1:
    def __init__(self):
        self.id = "RULE_1"
        self.description = "First rule"
        self.severity = "high"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

class Rule2:
    def __init__(self):
        self.id = "RULE_2"
        self.description = "Second rule"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

# Proper consolidated export
rules = [Rule1(), Rule2()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should load both rules from consolidated list
        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert rule_ids == {"RULE_1", "RULE_2"}

    def test_rule_loader_prefers_rules_list_over_legacy(self):
        """Test that RuleLoader prefers consolidated rules list over legacy discovery."""
        mixed_module = self.test_rules_dir / "mixed_module.py"
        mixed_module.write_text("""
from sentinel.rules.base import Finding
import pathlib
from typing import List

class LegacyRule:
    def __init__(self):
        self.id = "LEGACY_RULE"
        self.description = "Legacy rule (should not be loaded)"
        self.severity = "low"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

class ConsolidatedRule:
    def __init__(self):
        self.id = "CONSOLIDATED_RULE"
        self.description = "Consolidated rule (should be loaded)"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

# Consolidated rules list takes precedence
rules = [ConsolidatedRule()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load from consolidated list, not legacy classes
        assert len(rules) == 1
        assert rules[0].id == "CONSOLIDATED_RULE"

    def test_rule_pack_scaffold_skipping(self):
        """Test that empty rule pack scaffold directories are properly skipped."""
        # Create a rule pack directory with only README (scaffold)
        pack_dir = self.test_rules_dir / "docker"
        pack_dir.mkdir()
        
        # Add only README (no Python files)
        readme_file = pack_dir / "README.md"
        readme_file.write_text("# Docker Rule Pack (scaffold)")
        
        # Create __init__.py but no actual rules
        init_file = pack_dir / "__init__.py"
        init_file.write_text("# Empty rule pack scaffold")

        # Create a real rule module for comparison
        real_rule = self.test_rules_dir / "real_rule.py"
        real_rule.write_text("""
class RealRule:
    def __init__(self):
        self.id = "REAL_RULE"
        self.description = "Real rule"
        self.severity = "high"

    def apply(self, path, text):
        return []

rules = [RealRule()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load the real rule, skip the scaffold pack
        assert len(rules) == 1
        assert rules[0].id == "REAL_RULE"

    def test_rule_protocol_isolation(self):
        """Test that the abstract Rule protocol is never instantiated."""
        # Create a module that imports the Rule protocol
        protocol_module = self.test_rules_dir / "protocol_module.py"
        protocol_module.write_text("""
from sentinel.rules.base import Rule, Finding
import pathlib
from typing import List

# This should not be instantiated because it inherits from abstract Rule
class BadRule(Rule):
    def __init__(self):
        self.id = "BAD_RULE"
        self.description = "Bad rule inheriting from Rule protocol"
        self.severity = "high"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

class GoodRule:
    def __init__(self):
        self.id = "GOOD_RULE"
        self.description = "Good rule not inheriting from Rule protocol"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

rules = [BadRule(), GoodRule()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should skip the BadRule (abstract) and only load GoodRule
        assert len(rules) == 1
        assert rules[0].id == "GOOD_RULE"

    def test_severity_validation(self):
        """Test that rules with invalid severity values are rejected."""
        invalid_severity_module = self.test_rules_dir / "invalid_severity.py"
        invalid_severity_module.write_text("""
class InvalidSeverityRule:
    def __init__(self):
        self.id = "INVALID_SEVERITY_RULE"
        self.description = "Rule with invalid severity"
        self.severity = "invalid_severity"  # Not in allowed list

    def apply(self, path, text):
        return []

class ValidSeverityRule:
    def __init__(self):
        self.id = "VALID_SEVERITY_RULE"
        self.description = "Rule with valid severity"
        self.severity = "high"  # Valid severity

    def apply(self, path, text):
        return []

rules = [InvalidSeverityRule(), ValidSeverityRule()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should only load the rule with valid severity
        assert len(rules) == 1
        assert rules[0].id == "VALID_SEVERITY_RULE"

    def test_rule_meta_attribute_handling(self):
        """Test that rules with RuleMeta attributes are handled correctly."""
        meta_rule_module = self.test_rules_dir / "meta_rule.py"
        meta_rule_module.write_text("""
from sentinel.rules.base import Finding, RuleMeta, create_default_rule_meta
import pathlib
from typing import List

class RuleWithMeta:
    def __init__(self):
        self.id = "RULE_WITH_META"
        self.description = "Rule with RuleMeta attribute"
        self.severity = "high"
        self.meta = create_default_rule_meta(
            category="secrets",
            cwe_ids=["CWE-798"],
            risk_factors=["hardcoded"],
            detection_method="regex"
        )

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

class RuleWithoutMeta:
    def __init__(self):
        self.id = "RULE_WITHOUT_META"
        self.description = "Rule without RuleMeta attribute"
        self.severity = "medium"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        return []

rules = [RuleWithMeta(), RuleWithoutMeta()]
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should load both rules (meta attribute is optional)
        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert rule_ids == {"RULE_WITH_META", "RULE_WITHOUT_META"}

    def test_rule_loader_logging_coverage(self):
        """Test that RuleLoader provides adequate logging for debugging."""
        with patch('sentinel.scanner.engine.logger') as mock_logger:
            # Create a module with both valid and invalid rules
            logging_module = self.test_rules_dir / "logging_module.py"
            logging_module.write_text("""
class ValidRule:
    def __init__(self):
        self.id = "VALID_RULE"
        self.description = "Valid rule for logging test"
        self.severity = "high"

    def apply(self, path, text):
        return []

class InvalidRule:
    def __init__(self):
        self.id = ""  # Empty ID
        self.description = "Invalid rule for logging test"
        self.severity = "high"

    def apply(self, path, text):
        return []

rules = [ValidRule(), InvalidRule()]
""")

            loader = RuleLoader(self.test_rules_dir)
            rules = loader.load_rules()

            # Should only load valid rule
            assert len(rules) == 1
            assert rules[0].id == "VALID_RULE"

            # Verify logging was called for invalid rule
            mock_logger.warning.assert_called()
            warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
            assert any("invalid id" in str(call).lower() for call in warning_calls)

    def test_backward_compatibility_with_legacy_modules(self):
        """Test that legacy modules without rules list still work."""
        legacy_module = self.test_rules_dir / "legacy_module.py"
        legacy_module.write_text("""
class LegacyRule1:
    def __init__(self):
        self.id = "LEGACY_RULE_1"
        self.description = "First legacy rule"
        self.severity = "high"

    def apply(self, path, text):
        return []

class LegacyRule2:
    def __init__(self):
        self.id = "LEGACY_RULE_2"
        self.description = "Second legacy rule"
        self.severity = "medium"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should load both legacy rules using fallback discovery
        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert rule_ids == {"LEGACY_RULE_1", "LEGACY_RULE_2"}

    def test_mixed_export_patterns(self):
        """Test that mixed export patterns (some with rules list, some legacy) work."""
        # Module with rules list
        modern_module = self.test_rules_dir / "modern_module.py"
        modern_module.write_text("""
class ModernRule:
    def __init__(self):
        self.id = "MODERN_RULE"
        self.description = "Modern rule with rules list"
        self.severity = "high"

    def apply(self, path, text):
        return []

rules = [ModernRule()]
""")

        # Legacy module without rules list
        legacy_module = self.test_rules_dir / "legacy_module.py"
        legacy_module.write_text("""
class LegacyRule:
    def __init__(self):
        self.id = "LEGACY_RULE"
        self.description = "Legacy rule without rules list"
        self.severity = "medium"

    def apply(self, path, text):
        return []
""")

        loader = RuleLoader(self.test_rules_dir)
        rules = loader.load_rules()

        # Should load both rules using appropriate methods
        assert len(rules) == 2
        rule_ids = {rule.id for rule in rules}
        assert rule_ids == {"MODERN_RULE", "LEGACY_RULE"}


if __name__ == "__main__":
    pytest.main([__file__])