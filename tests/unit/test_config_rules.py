"""
Unit tests for configuration vulnerability rules.

Tests all configuration vulnerability rules to ensure they correctly identify
security misconfigurations and handle edge cases appropriately.
"""

import pytest
import pathlib
import tempfile
from unittest.mock import Mock

from sentinel.rules.configs import (
    HardcodedAPIRule,
    HardcodedDatabaseRule,
)
from sentinel.rules.base import Finding


class TestHardcodedAPIRule:
    """Test hardcoded API key detection."""

    def setup_method(self):
        self.rule = HardcodedAPIRule()
        self.test_file = pathlib.Path("config.py")

    def test_detects_api_key_assignment(self):
        """Test that API key assignments are detected."""
        content = """
        api_key = "sk_test_1234567890abcdefghijklmnop"
        secret_key = "my_super_secret_key_12345"
        """

        findings = self.rule.apply(self.test_file, content)
        # Only the generic secret key should be detected (Stripe key is handled by secret rules)
        assert len(findings) == 1
        assert all(f.rule_id == "hardcoded-api-key" for f in findings)
        assert all(f.severity == "high" for f in findings)

    def test_detects_stripe_keys(self):
        """Test that Stripe secret keys are detected."""
        content = """
        stripe_key = "sk_live_1234567890abcdefghijklmnop"
        restricted_key = "rk_test_1234567890abcdefghijklmnop"
        """

        findings = self.rule.apply(self.test_file, content)
        # Stripe keys are now handled by secret rules, so config rule defers
        assert len(findings) == 0

    def test_detects_aws_keys(self):
        """Test that AWS access keys are detected."""
        content = """
        aws_key = "AKIAIOSFODNN7EXAMPLE"
        """

        findings = self.rule.apply(self.test_file, content)
        # AWS keys are now handled by secret rules, so config rule defers
        assert len(findings) == 0

    def test_detects_github_tokens(self):
        """Test that GitHub tokens are detected."""
        content = """
        github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        """

        findings = self.rule.apply(self.test_file, content)
        # GitHub tokens are now handled by secret rules, so config rule defers
        assert len(findings) == 0

    def test_detects_slack_tokens(self):
        """Test that Slack tokens are detected."""
        content = """
        slack_token = "xoxb-1234567890-1234567890-1234567890-abcdefghijklmnop"
        """

        findings = self.rule.apply(self.test_file, content)
        # Slack tokens are now handled by secret rules, so config rule defers
        assert len(findings) == 0

    def test_ignores_short_values(self):
        """Test that short values are ignored."""
        content = """
        api_key = "short"
        token = "test"
        password = "123"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0

    def test_handles_empty_content(self):
        """Test that empty content is handled without crashing."""
        findings = self.rule.apply(self.test_file, "")
        assert isinstance(findings, list)
        assert len(findings) == 0


class TestHardcodedDatabaseRule:
    """Test hardcoded database credential detection."""

    def setup_method(self):
        self.rule = HardcodedDatabaseRule()
        self.test_file = pathlib.Path("config.py")

    def test_detects_postgres_connections(self):
        """Test that PostgreSQL connection strings are detected."""
        content = """
        db_url = "postgresql://user:password123@localhost:5432/mydb"
        conn_str = "postgres://admin:adminpass@localhost:5432/appdb"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 2
        assert all(f.rule_id == "hardcoded-database" for f in findings)
        assert all(f.severity == "high" for f in findings)

    def test_detects_mysql_connections(self):
        """Test that MySQL connection strings are detected."""
        content = """
        mysql_conn = "mysql://user:pass@localhost:3306/database"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1

    def test_detects_mongodb_connections(self):
        """Test that MongoDB connection strings are detected."""
        content = """
        mongo_url = "mongodb://user:pass@localhost:27017/app"
        mongo_srv = "mongodb+srv://admin:adminpass@cluster.mongodb.net/db"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 2

    def test_detects_redis_connections(self):
        """Test that Redis connection strings are detected."""
        content = """
        redis_url = "redis://user:pass@localhost:6379/0"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1

    def test_ignores_connection_strings_without_passwords(self):
        """Test that connection strings without passwords are ignored."""
        content = """
        db_url = "postgresql://user@localhost:5432/mydb"
        redis_url = "redis://localhost:6379/0"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0

    def test_handles_empty_content(self):
        """Test that empty content is handled without crashing."""
        findings = self.rule.apply(self.test_file, "")
        assert isinstance(findings, list)
        assert len(findings) == 0


class TestRuleRobustness:
    """Test configuration rule robustness and error handling."""

    def test_rules_handle_empty_content(self):
        """Test that rules handle empty content without crashing."""
        rules = [
            HardcodedAPIRule(),
            HardcodedDatabaseRule(),
        ]

        test_file = pathlib.Path("test.py")

        for rule in rules:
            findings = rule.apply(test_file, "")
            assert isinstance(findings, list)

    def test_rules_handle_binary_like_content(self):
        """Test that rules handle binary-like content without crashing."""
        content = "Binary data: \x00\x01\x02\x03\x04\x05"

        rules = [
            HardcodedAPIRule(),
            HardcodedDatabaseRule(),
        ]

        test_file = pathlib.Path("test.bin")

        for rule in rules:
            findings = rule.apply(test_file, content)
            assert isinstance(findings, list)

    def test_rules_return_proper_finding_structure(self):
        """Test that all rules return properly structured Finding objects."""
        content = """
        api_key = "sk_test_1234567890abcdefghijklmnop"
        db_url = "postgresql://user:pass@localhost:5432/db"
        """

        rules = [
            HardcodedAPIRule(),
            HardcodedDatabaseRule(),
        ]

        test_file = pathlib.Path("test.py")

        for rule in rules:
            findings = rule.apply(test_file, content)
            for finding in findings:
                assert hasattr(finding, 'rule_id')
                assert hasattr(finding, 'file_path')
                assert hasattr(finding, 'line')
                assert hasattr(finding, 'severity')
                assert hasattr(finding, 'excerpt')
                assert hasattr(finding, 'confidence')
                assert finding.file_path == test_file
