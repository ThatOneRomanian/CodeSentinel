"""
Unit tests for finding deduplication logic in CodeSentinel.

Tests the deduplication functionality implemented in Phase 4 to prevent
multiple findings for the same token while maintaining precedence rules.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pathlib
import pytest

from sentinel.rules.base import Finding
from sentinel.scanner.engine import (
    _get_rule_precedence, 
    _extract_token_from_excerpt,
    _get_finding_group_key,
    _deduplicate_findings,
    _select_best_finding
)


class TestDeduplicationPrecedence:
    """Test cases for rule precedence calculation."""
    
    def test_provider_specific_rules_highest_precedence(self):
        """Test that provider-specific rules have highest precedence."""
        finding = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            excerpt="AKIA1234567890123456",
            confidence=0.9
        )
        assert _get_rule_precedence(finding) == 100
    
    def test_oauth_tokens_medium_precedence(self):
        """Test that OAuth tokens have medium precedence."""
        finding = Finding(
            rule_id="SECRET_OAUTH_TOKEN",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="medium",
            excerpt="oauth_token = 'ya29.abcdefg'",
            confidence=0.8
        )
        assert _get_rule_precedence(finding) == 90
    
    def test_generic_api_keys_lower_precedence(self):
        """Test that generic API keys have lower precedence."""
        finding = Finding(
            rule_id="SECRET_GENERIC_API_KEY",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="medium",
            excerpt="api_key = 'abcdef123456'",
            confidence=0.7
        )
        assert _get_rule_precedence(finding) == 80
    
    def test_high_entropy_lowest_precedence(self):
        """Test that high entropy strings have lowest precedence."""
        finding = Finding(
            rule_id="SECRET_HIGH_ENTROPY",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            excerpt="random_string = 'AbCdEfGhIjKlMnOpQrStUvWxYz123456'",
            confidence=0.6
        )
        assert _get_rule_precedence(finding) == 70
    
    def test_configuration_rules_separate_category(self):
        """Test that configuration rules are in separate precedence category."""
        finding = Finding(
            rule_id="debug-enabled",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="medium",
            excerpt="DEBUG = True",
            confidence=0.8
        )
        assert _get_rule_precedence(finding) == 60
    
    def test_unknown_rule_default_precedence(self):
        """Test that unknown rules get default precedence."""
        finding = Finding(
            rule_id="UNKNOWN_RULE",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="low",
            excerpt="test = 'value'",
            confidence=0.5
        )
        assert _get_rule_precedence(finding) == 50


class TestTokenExtraction:
    """Test cases for token extraction from excerpts."""
    
    def test_extract_quoted_string(self):
        """Test extracting token from quoted string."""
        excerpt = 'api_key = "sk_test_abcdefghijklmnopqrstuvwx"'
        token = _extract_token_from_excerpt(excerpt)
        assert token == "sk_test_abcdefghijklmnopqrstuvwx"
    
    def test_extract_single_quoted_string(self):
        """Test extracting token from single quoted string."""
        excerpt = "password = 'MySecretPassword123'"
        token = _extract_token_from_excerpt(excerpt)
        assert token == "MySecretPassword123"
    
    def test_extract_unquoted_assignment(self):
        """Test extracting token from unquoted assignment."""
        excerpt = "token = abcdefghijklmnopqrstuvwxyz123456"
        token = _extract_token_from_excerpt(excerpt)
        assert token == "abcdefghijklmnopqrstuvwxyz123456"
    
    def test_extract_yaml_style(self):
        """Test extracting token from YAML-style assignment."""
        excerpt = 'secret_key: "AKIA1234567890123456"'
        token = _extract_token_from_excerpt(excerpt)
        assert token == "AKIA1234567890123456"
    
    def test_extract_fallback_long_string(self):
        """Test fallback extraction of long alphanumeric strings."""
        excerpt = "This contains a long string ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
        token = _extract_token_from_excerpt(excerpt)
        assert token == "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    
    def test_no_token_found(self):
        """Test when no token can be extracted."""
        excerpt = "This is a normal line without any tokens"
        token = _extract_token_from_excerpt(excerpt)
        assert token is None
    
    def test_empty_excerpt(self):
        """Test extraction from empty excerpt."""
        token = _extract_token_from_excerpt("")
        assert token is None


class TestFindingGrouping:
    """Test cases for finding grouping logic."""
    
    def test_group_key_same_file_line_excerpt(self):
        """Test that same file, line, and excerpt produce same group key."""
        finding1 = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        finding2 = Finding(
            rule_id="SECRET_HIGH_ENTROPY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.7
        )
        
        key1 = _get_finding_group_key(finding1)
        key2 = _get_finding_group_key(finding2)
        
        assert key1 == key2
    
    def test_group_key_different_line(self):
        """Test that different line numbers produce different group keys."""
        finding1 = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        finding2 = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=11,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        key1 = _get_finding_group_key(finding1)
        key2 = _get_finding_group_key(finding2)
        
        assert key1 != key2
    
    def test_group_key_different_excerpt(self):
        """Test that different excerpts produce different group keys."""
        finding1 = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        finding2 = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='secret = "SKIA9876543210987654"',
            confidence=0.9
        )
        
        key1 = _get_finding_group_key(finding1)
        key2 = _get_finding_group_key(finding2)
        
        assert key1 != key2
    
    def test_group_key_normalizes_whitespace(self):
        """Test that group key normalizes whitespace in excerpts."""
        finding1 = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key   =   "AKIA1234567890123456"',
            confidence=0.9
        )
        
        finding2 = Finding(
            rule_id="SECRET_HIGH_ENTROPY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.7
        )
        
        key1 = _get_finding_group_key(finding1)
        key2 = _get_finding_group_key(finding2)
        
        assert key1 == key2
    
    def test_group_key_handles_none_line(self):
        """Test that group key handles None line numbers."""
        finding = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=None,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        key = _get_finding_group_key(finding)
        assert key[1] == 0  # Should use 0 as placeholder for None
    
    def test_group_key_handles_none_excerpt(self):
        """Test that group key handles None excerpts."""
        finding = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt=None,
            confidence=0.9
        )
        
        key = _get_finding_group_key(finding)
        assert key[2] == ""  # Should use empty string for None


class TestBestFindingSelection:
    """Test cases for selecting the best finding from duplicates."""
    
    def test_select_higher_precedence_rule(self):
        """Test that higher precedence rule is selected."""
        provider_finding = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",  # Precedence 100
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.8
        )
        
        generic_finding = Finding(
            rule_id="SECRET_HIGH_ENTROPY",  # Precedence 70
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        best = _select_best_finding([provider_finding, generic_finding])
        assert best.rule_id == "SECRET_AWS_ACCESS_KEY"
    
    def test_select_higher_confidence_same_precedence(self):
        """Test that higher confidence is selected when precedence is same."""
        finding1 = Finding(
            rule_id="SECRET_OAUTH_TOKEN",  # Precedence 90
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="medium",
            excerpt='token = "abcdef123456"',
            confidence=0.9
        )
        
        finding2 = Finding(
            rule_id="SECRET_HARDCODED_PASSWORD",  # Precedence 90
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='token = "abcdef123456"',
            confidence=0.7
        )
        
        best = _select_best_finding([finding1, finding2])
        assert best.rule_id == "SECRET_OAUTH_TOKEN"
    
    def test_select_alphabetical_tie_break(self):
        """Test alphabetical tie-breaking when precedence and confidence are equal."""
        finding1 = Finding(
            rule_id="SECRET_A",  # Precedence 100
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='key = "value"',
            confidence=0.8
        )
        
        finding2 = Finding(
            rule_id="SECRET_B",  # Precedence 100
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='key = "value"',
            confidence=0.8
        )
        
        best = _select_best_finding([finding1, finding2])
        assert best.rule_id == "SECRET_A"  # Alphabetical order
    
    def test_single_finding_returns_itself(self):
        """Test that single finding list returns the finding itself."""
        finding = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt='api_key = "AKIA1234567890123456"',
            confidence=0.9
        )
        
        best = _select_best_finding([finding])
        assert best == finding


class TestDeduplicationIntegration:
    """Integration tests for the complete deduplication process."""
    
    def test_deduplicate_provider_specific_over_generic(self):
        """Test deduplication prefers provider-specific over generic rules."""
        # Facebook token that triggers multiple rules
        findings = [
            Finding(
                rule_id="SECRET_HIGH_ENTROPY",  # Precedence 70
                file_path=pathlib.Path("config.yaml"),
                line=29,
                severity="high",
                excerpt='facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"',
                confidence=0.53
            ),
            Finding(
                rule_id="SECRET_AWS_SECRET_KEY",  # Precedence 100
                file_path=pathlib.Path("config.yaml"),
                line=29,
                severity="high",
                excerpt='facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"',
                confidence=0.85
            ),
            Finding(
                rule_id="SECRET_AZURE_CLIENT_SECRET",  # Precedence 100
                file_path=pathlib.Path("config.yaml"),
                line=29,
                severity="high",
                excerpt='facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"',
                confidence=0.80
            ),
            Finding(
                rule_id="SECRET_OAUTH_TOKEN",  # Precedence 90
                file_path=pathlib.Path("config.yaml"),
                line=29,
                severity="medium",
                excerpt='facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"',
                confidence=0.75
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should keep only one finding (highest precedence)
        assert len(deduplicated) == 1
        # Should prefer AWS_SECRET_KEY over AZURE_CLIENT_SECRET due to higher confidence
        assert deduplicated[0].rule_id == "SECRET_AWS_SECRET_KEY"
    
    def test_deduplicate_stripe_key_scenario(self):
        """Test deduplication for Stripe API key scenario."""
        findings = [
            Finding(
                rule_id="hardcoded-api-key",  # Precedence 80
                file_path=pathlib.Path("config.yaml"),
                line=14,
                severity="medium",
                excerpt='secret_key: "sk_test_7777777777abcdefghijklmnop"',
                confidence=0.80
            ),
            Finding(
                rule_id="SECRET_AZURE_CLIENT_SECRET",  # Precedence 100
                file_path=pathlib.Path("config.yaml"),
                line=14,
                severity="high",
                excerpt='secret_key: "sk_test_7777777777abcdefghijklmnop"',
                confidence=0.80
            ),
            Finding(
                rule_id="SECRET_STRIPE_API_KEY",  # Precedence 100
                file_path=pathlib.Path("config.yaml"),
                line=14,
                severity="high",
                excerpt='secret_key: "sk_test_7777777777abcdefghijklmnop"',
                confidence=0.95
            ),
            Finding(
                rule_id="SECRET_GENERIC_API_KEY",  # Precedence 80
                file_path=pathlib.Path("config.yaml"),
                line=14,
                severity="medium",
                excerpt='secret_key: "sk_test_7777777777abcdefghijklmnop"',
                confidence=0.70
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should keep only one finding (highest precedence + confidence)
        assert len(deduplicated) == 1
        # Should prefer STRIPE_API_KEY as it's provider-specific with highest confidence
        assert deduplicated[0].rule_id == "SECRET_STRIPE_API_KEY"
    
    def test_no_duplicates_returns_original(self):
        """Test that findings without duplicates are returned unchanged."""
        findings = [
            Finding(
                rule_id="SECRET_AWS_ACCESS_KEY",
                file_path=pathlib.Path("file1.py"),
                line=10,
                severity="high",
                excerpt='key = "AKIA1234567890123456"',
                confidence=0.9
            ),
            Finding(
                rule_id="SECRET_STRIPE_API_KEY",
                file_path=pathlib.Path("file2.py"),
                line=20,
                severity="high",
                excerpt='secret = "sk_test_abcdefghijklmnop"',
                confidence=0.95
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should return both findings unchanged
        assert len(deduplicated) == 2
        assert deduplicated == findings
    
    def test_empty_findings_returns_empty(self):
        """Test that empty findings list returns empty list."""
        deduplicated = _deduplicate_findings([])
        assert deduplicated == []
    
    def test_deduplicate_mixed_scenarios(self):
        """Test deduplication with mixed scenarios (some duplicates, some not)."""
        findings = [
            # Group 1: Facebook token duplicates
            Finding(
                rule_id="SECRET_HIGH_ENTROPY",
                file_path=pathlib.Path("config.yaml"),
                line=29,
                severity="high",
                excerpt='facebook: "EAACEdEose0cBAExampleToken777"',
                confidence=0.53
            ),
            Finding(
                rule_id="SECRET_AWS_SECRET_KEY",
                file_path=pathlib.Path("config.yaml"),
                line=29,
                severity="high",
                excerpt='facebook: "EAACEdEose0cBAExampleToken777"',
                confidence=0.85
            ),
            # Group 2: Stripe key duplicates
            Finding(
                rule_id="SECRET_STRIPE_API_KEY",
                file_path=pathlib.Path("config.yaml"),
                line=14,
                severity="high",
                excerpt='secret_key: "sk_test_7777777777abcdef"',
                confidence=0.95
            ),
            Finding(
                rule_id="SECRET_AZURE_CLIENT_SECRET",
                file_path=pathlib.Path("config.yaml"),
                line=14,
                severity="high",
                excerpt='secret_key: "sk_test_7777777777abcdef"',
                confidence=0.80
            ),
            # Group 3: Unique finding
            Finding(
                rule_id="debug-enabled",
                file_path=pathlib.Path("settings.py"),
                line=5,
                severity="medium",
                excerpt="DEBUG = True",
                confidence=0.8
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should have 3 groups reduced to 3 findings
        assert len(deduplicated) == 3
        # Should contain the highest precedence finding from each group
        rule_ids = {f.rule_id for f in deduplicated}
        assert "SECRET_AWS_SECRET_KEY" in rule_ids  # Group 1
        assert "SECRET_STRIPE_API_KEY" in rule_ids   # Group 2
        assert "debug-enabled" in rule_ids           # Group 3 (unique)


class TestEdgeCases:
    """Test edge cases and error handling in deduplication."""
    
    def test_findings_with_none_confidence(self):
        """Test deduplication with findings that have None confidence."""
        findings = [
            Finding(
                rule_id="SECRET_AWS_ACCESS_KEY",  # Precedence 100
                file_path=pathlib.Path("test.py"),
                line=10,
                severity="high",
                excerpt='key = "AKIA1234567890123456"',
                confidence=None
            ),
            Finding(
                rule_id="SECRET_HIGH_ENTROPY",  # Precedence 70
                file_path=pathlib.Path("test.py"),
                line=10,
                severity="high",
                excerpt='key = "AKIA1234567890123456"',
                confidence=0.9
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should prefer AWS_ACCESS_KEY despite None confidence due to higher precedence
        assert len(deduplicated) == 1
        assert deduplicated[0].rule_id == "SECRET_AWS_ACCESS_KEY"
    
    def test_findings_with_none_excerpt(self):
        """Test deduplication with findings that have None excerpt."""
        findings = [
            Finding(
                rule_id="SECRET_AWS_ACCESS_KEY",
                file_path=pathlib.Path("test.py"),
                line=10,
                severity="high",
                excerpt=None,
                confidence=0.9
            ),
            Finding(
                rule_id="SECRET_HIGH_ENTROPY",
                file_path=pathlib.Path("test.py"),
                line=10,
                severity="high",
                excerpt=None,
                confidence=0.8
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should group by same file/line/None excerpt and deduplicate
        assert len(deduplicated) == 1
        assert deduplicated[0].rule_id == "SECRET_AWS_ACCESS_KEY"
    
    def test_findings_with_none_line(self):
        """Test deduplication with findings that have None line numbers."""
        findings = [
            Finding(
                rule_id="SECRET_AWS_ACCESS_KEY",
                file_path=pathlib.Path("test.py"),
                line=None,
                severity="high",
                excerpt='key = "AKIA1234567890123456"',
                confidence=0.9
            ),
            Finding(
                rule_id="SECRET_HIGH_ENTROPY",
                file_path=pathlib.Path("test.py"),
                line=None,
                severity="high",
                excerpt='key = "AKIA1234567890123456"',
                confidence=0.8
            )
        ]
        
        deduplicated = _deduplicate_findings(findings)
        
        # Should group by same file/None line/excerpt and deduplicate
        assert len(deduplicated) == 1
        assert deduplicated[0].rule_id == "SECRET_AWS_ACCESS_KEY"