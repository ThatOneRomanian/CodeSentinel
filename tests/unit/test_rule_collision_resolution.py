"""
Unit tests for rule collision resolution.

Tests that verify the Phase 3 rule hardening has resolved the cross-provider
collision issues identified in Phase 1 analysis.
"""

import pytest
import pathlib
from sentinel.rules.secrets import (
    AzureClientSecretRule,
    AWSAccessKeyRule,
    AWSSecretKeyRule,
    StripeAPIKeyRule,
    OAuthTokenRule,
    GCPServiceAccountRule,
    HighEntropyStringRule,
)
from sentinel.rules.token_types import classify_token, TokenType


class TestRuleCollisionResolution:
    """Test that rule collisions have been resolved."""

    def setup_method(self):
        self.test_file = pathlib.Path("test.py")
        self.azure_rule = AzureClientSecretRule()
        self.aws_access_rule = AWSAccessKeyRule()
        self.aws_secret_rule = AWSSecretKeyRule()
        self.stripe_rule = StripeAPIKeyRule()
        self.oauth_rule = OAuthTokenRule()
        self.gcp_service_rule = GCPServiceAccountRule()
        self.high_entropy_rule = HighEntropyStringRule()

    def test_azure_rule_only_matches_guids(self):
        """Test that Azure rule only matches GUIDs and not other provider tokens."""
        # Azure GUIDs (should match)
        azure_guids = [
            "12345678-1234-1234-1234-123456789012",
            "abcdef12-3456-7890-abcd-ef1234567890",
        ]

        # Other provider tokens that were previously mis-classified by Azure rule
        other_provider_tokens = [
            # AWS tokens
            "AKIAIOSFODNN7EXAMPLE",  # AWS access key
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # AWS secret key
            # Stripe tokens
            "sk_live_1234567890abcdefghijklmnop",
            "pk_test_1234567890abcdefghijklmnop",
            # GitHub tokens
            "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            "github_pat_123456789012345678901234567890123456789012345678901234567890",
            # Slack tokens
            "xoxb-1234567890-1234567890-1234567890-abcdefghijklmnop",
            "xoxp-1234567890-1234567890-1234567890-abcdefghijklmnop",
            # GCP tokens
            "ya29.c.b0ATvPL3MhExampleTokenStringHere1234567890abcdef",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.example.service.account.token",
            # High entropy strings (base64-like)
            "dGVzdDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTA=",
            "U2VjcmV0S2V5MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MA==",
        ]

        # Test Azure GUIDs are detected
        for guid in azure_guids:
            content = f'azure_secret = "{guid}"'
            findings = self.azure_rule.apply(self.test_file, content)
            assert len(findings) == 1, f"Azure GUID {guid} should be detected"
            assert findings[0].rule_id == "SECRET_AZURE_CLIENT_SECRET"

        # Test other provider tokens are NOT detected by Azure rule
        for token in other_provider_tokens:
            content = f'secret = "{token}"'
            findings = self.azure_rule.apply(self.test_file, content)
            assert len(findings) == 0, f"Token {token} should NOT be detected by Azure rule"

    def test_provider_rules_only_match_their_own_tokens(self):
        """Test that each provider rule only matches its intended token type."""
        test_cases = [
            # (rule, valid_token, invalid_tokens)
            (
                self.aws_access_rule,
                "AKIAIOSFODNN7EXAMPLE",
                [
                    "sk_live_1234567890abcdefghijklmnop",  # Stripe
                    "ghp_1234567890abcdefghijklmnopqrstuvwxyz",  # GitHub
                    "12345678-1234-1234-1234-123456789012",  # Azure GUID
                ]
            ),
            (
                self.stripe_rule,
                "sk_live_1234567890abcdefghijklmnop",
                [
                    "AKIAIOSFODNN7EXAMPLE",  # AWS
                    "ghp_1234567890abcdefghijklmnopqrstuvwxyz",  # GitHub
                    "12345678-1234-1234-1234-123456789012",  # Azure GUID
                ]
            ),
        ]

        for rule, valid_token, invalid_tokens in test_cases:
            # Test valid token is detected
            content = f'token = "{valid_token}"'
            findings = rule.apply(self.test_file, content)
            assert len(findings) == 1, f"Valid token {valid_token} should be detected by {rule.__class__.__name__}"

            # Test invalid tokens are NOT detected
            for invalid_token in invalid_tokens:
                content = f'token = "{invalid_token}"'
                findings = rule.apply(self.test_file, content)
                assert len(findings) == 0, f"Invalid token {invalid_token} should NOT be detected by {rule.__class__.__name__}"

    def test_high_entropy_rule_defers_to_provider_classification(self):
        """Test that high entropy rule only fires when no provider-specific classification exists."""
        # Tokens that should be classified as specific providers (high entropy but should NOT trigger generic rule)
        provider_tokens = [
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # AWS secret key (high entropy)
            "sk_live_1234567890abcdefghijklmnop",  # Stripe key (high entropy)
            "ghp_1234567890abcdefghijklmnopqrstuvwxyz",  # GitHub token (high entropy)
            "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789",  # OAuth token (high entropy)
        ]

        # Generic high entropy strings (should trigger the rule) - must match alphanumeric pattern
        generic_high_entropy = [
            "dGVzdDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTA=",  # Base64-like
        ]

        # Test provider tokens are NOT detected by high entropy rule
        for token in provider_tokens:
            content = f'secret = "{token}"'
            findings = self.high_entropy_rule.apply(self.test_file, content)
            assert len(findings) == 0, f"Provider token {token} should NOT trigger high entropy rule"

        # Test generic high entropy strings ARE detected
        for token in generic_high_entropy:
            content = f'secret = "{token}"'
            findings = self.high_entropy_rule.apply(self.test_file, content)
            assert len(findings) == 1, f"Generic high entropy string {token} should trigger high entropy rule"

    def test_token_classification_precedence(self):
        """Test that token classification system correctly identifies tokens and prevents collisions."""
        test_cases = [
            # (token, expected_classification)
            ("AKIAIOSFODNN7EXAMPLE", TokenType.AWS_ACCESS_KEY),
            ("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", TokenType.AWS_SECRET_KEY),
            ("sk_live_1234567890abcdefghijklmnop", TokenType.STRIPE_API_KEY_LIVE),
            ("ghp_1234567890abcdefghijklmnopqrstuvwxyz", TokenType.GITHUB_TOKEN),
            ("12345678-1234-1234-1234-123456789012", TokenType.AZURE_CLIENT_SECRET),
            ("xoxb-1234567890-1234567890-1234567890-abcdefghijklmnop", TokenType.SLACK_BOT_TOKEN),
            ("AbCdEfGhIjKlMnOpQrStUvWxYz0123456789", TokenType.OAUTH_TOKEN),  # Now correctly classified as OAuth
            ("dGVzdDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTA=", TokenType.GENERIC_HIGH_ENTROPY),
        ]

        for token, expected_classification in test_cases:
            result = classify_token(token)
            assert result == expected_classification, f"Token {token} should be classified as {expected_classification}, got {result}"

    def test_phase1_collision_scenarios_resolved(self):
        """Test specific collision scenarios identified in Phase 1 analysis."""
        # These were the specific collision cases from Phase 1 where Azure rule was over-matching
        collision_cases = [
            # AWS secret keys that were mis-classified as Azure
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYANOTHERKEY",
            # Stripe keys that were mis-classified as Azure  
            "sk_live_1234567890abcdefghijklmnop",
            "rk_test_1234567890abcdefghijklmnop",
            # GitHub tokens that were mis-classified as Azure
            "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            "github_pat_123456789012345678901234567890123456789012345678901234567890",
            # Slack tokens that were mis-classified as Azure
            "xoxb-1234567890-1234567890-1234567890-abcdefghijklmnop",
            "xoxp-1234567890-1234567890-1234567890-abcdefghijklmnop",
            # GCP tokens that were mis-classified as Azure
            "ya29.c.b0ATvPL3MhExampleTokenStringHere1234567890abcdef",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.example.service.account.token",
        ]

        for token in collision_cases:
            # Verify Azure rule does NOT match these tokens
            content = f'secret = "{token}"'
            azure_findings = self.azure_rule.apply(self.test_file, content)
            assert len(azure_findings) == 0, f"Token {token} should NOT be detected by Azure rule (was collision case)"

            # Verify token classification is NOT Azure
            classification = classify_token(token)
            assert classification != TokenType.AZURE_CLIENT_SECRET, f"Token {token} should not be classified as Azure"