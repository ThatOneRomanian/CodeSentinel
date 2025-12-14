"""
Unit tests for token type classification module.

Tests the provider-aware token classification system to ensure accurate
identification of token types and proper precedence handling.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pytest
from sentinel.rules.token_types import (
    TokenType,
    classify_token,
    _is_aws_access_key,
    _is_aws_secret_key,
    _is_stripe_api_key,
    _is_slack_token,
    _is_github_token,
    _is_gcp_oauth_token,
    _is_facebook_access_token,
    _is_jwt_token,
    _is_private_key,
    _is_gcp_service_account,
    _is_azure_client_secret,
    _is_generic_oauth_token,
    _is_high_entropy_token,
)


class TestTokenTypeEnum:
    """Test TokenType enum values and coverage."""
    
    def test_token_type_values(self):
        """Verify all expected token types are defined."""
        expected_types = [
            'aws_access_key', 'aws_secret_key',
            'gcp_oauth_token', 'gcp_service_account',
            'azure_client_secret',
            'stripe_api_key_live', 'stripe_api_key_test',
            'slack_bot_token', 'slack_user_token',
            'github_token',
            'facebook_access_token',
            'jwt',
            'generic_high_entropy',
            'private_key',
            'oauth_token'
        ]
        
        actual_types = [t.value for t in TokenType]
        assert set(expected_types) == set(actual_types)


class TestAWSTokenClassification:
    """Test AWS token classification."""
    
    def test_aws_access_key_valid(self):
        """Test valid AWS Access Key classification."""
        valid_keys = [
            "AKIAIOSFODNN7EXAMPLE",
            "AKIA0123456789ABCDEF",
            "AKIAABCDEFGHIJKLMNOP"
        ]
        
        for key in valid_keys:
            result = classify_token(key)
            assert result == TokenType.AWS_ACCESS_KEY
            assert _is_aws_access_key(key)
    
    def test_aws_access_key_invalid(self):
        """Test invalid AWS Access Key rejection."""
        invalid_keys = [
            "AKIA",  # Too short
            "AKIAIOSFODNN7EXAMPL",  # Too short (15 chars)
            "AKIAIOSFODNN7EXAMPLE1",  # Too long (17 chars)
            "akiaiosfodnn7example",  # Lowercase
            "XKIAIOSFODNN7EXAMPLE",  # Wrong prefix
            "AK1AIOSFODNN7EXAMPLE",  # Invalid character
        ]
        
        for key in invalid_keys:
            result = classify_token(key)
            assert result != TokenType.AWS_ACCESS_KEY
            assert not _is_aws_access_key(key)
    
    def test_aws_secret_key_valid(self):
        """Test valid AWS Secret Key classification."""
        # Note: These are example patterns, not real secrets
        valid_secrets = [
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/==",
            "abcdefghijklmnopqrstuvwxyz0123456789+/ab"
        ]
        
        for secret in valid_secrets:
            result = classify_token(secret)
            assert result == TokenType.AWS_SECRET_KEY
            assert _is_aws_secret_key(secret)
    
    def test_aws_secret_key_invalid(self):
        """Test invalid AWS Secret Key rejection."""
        invalid_secrets = [
            "short",  # Too short
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAM",  # Too short (39 chars)
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # Low entropy
            "1111111111111111111111111111111111111111",  # All digits
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  # All letters
        ]
        
        for secret in invalid_secrets:
            result = classify_token(secret)
            assert result != TokenType.AWS_SECRET_KEY
            assert not _is_aws_secret_key(secret)


class TestStripeTokenClassification:
    """Test Stripe token classification."""
    
    def test_stripe_live_key_valid(self):
        """Test valid Stripe live key classification."""
        valid_keys = [
            "sk_live_123456789012345678901234",
            "pk_live_abcdefghijklmnopqrstuvwx"
        ]
        
        for key in valid_keys:
            result = classify_token(key)
            assert result == TokenType.STRIPE_API_KEY_LIVE
            assert _is_stripe_api_key(key) == TokenType.STRIPE_API_KEY_LIVE
    
    def test_stripe_test_key_valid(self):
        """Test valid Stripe test key classification."""
        valid_keys = [
            "sk_test_123456789012345678901234",
            "pk_test_abcdefghijklmnopqrstuvwx"
        ]
        
        for key in valid_keys:
            result = classify_token(key)
            assert result == TokenType.STRIPE_API_KEY_TEST
            assert _is_stripe_api_key(key) == TokenType.STRIPE_API_KEY_TEST
    
    def test_stripe_key_invalid(self):
        """Test invalid Stripe key rejection."""
        invalid_keys = [
            "sk_live_short",  # Too short
            "xk_live_123456789012345678901234",  # Wrong prefix
            "sk_live_12345678901234567890123",  # Too short (23 chars)
        ]
        
        for key in invalid_keys:
            result = classify_token(key)
            assert result not in [TokenType.STRIPE_API_KEY_LIVE, TokenType.STRIPE_API_KEY_TEST]
            assert _is_stripe_api_key(key) is None


class TestSlackTokenClassification:
    """Test Slack token classification."""
    
    def test_slack_bot_token_valid(self):
        """Test valid Slack bot token classification."""
        valid_tokens = [
            "xoxb-123456789012-123456789012-abcdefghijklmnopqrstuvwx",
            "xoxb-abcdefghijklmnopqrstuvwxyz-1234567890123456789012"
        ]
        
        for token in valid_tokens:
            result = classify_token(token)
            assert result == TokenType.SLACK_BOT_TOKEN
            assert _is_slack_token(token) == TokenType.SLACK_BOT_TOKEN
    
    def test_slack_user_token_valid(self):
        """Test valid Slack user token classification."""
        valid_tokens = [
            "xoxp-123456789012-123456789012-abcdefghijklmnopqrstuvwx",
            "xoxp-abcdefghijklmnopqrstuvwxyz-1234567890123456789012"
        ]
        
        for token in valid_tokens:
            result = classify_token(token)
            assert result == TokenType.SLACK_USER_TOKEN
            assert _is_slack_token(token) == TokenType.SLACK_USER_TOKEN
    
    def test_slack_token_invalid(self):
        """Test invalid Slack token rejection."""
        invalid_tokens = [
            "xoxb-short",  # Too short
            "xoxc-123456789012-123456789012-abcdefghijklmnopqrstuvwx",  # Wrong type
        ]
        
        for token in invalid_tokens:
            result = classify_token(token)
            assert result not in [TokenType.SLACK_BOT_TOKEN, TokenType.SLACK_USER_TOKEN]
            assert _is_slack_token(token) is None


class TestGitHubTokenClassification:
    """Test GitHub token classification."""
    
    def test_github_token_valid(self):
        """Test valid GitHub token classification."""
        valid_tokens = [
            "ghp_123456789012345678901234567890123456",  # 40 chars total
            "github_pat_123456789012345678901234567890123456789012345678901234567890"  # 71 chars total (test token)
        ]
        
        for token in valid_tokens:
            result = classify_token(token)
            assert result == TokenType.GITHUB_TOKEN
            assert _is_github_token(token)
    
    def test_github_token_invalid(self):
        """Test invalid GitHub token rejection."""
        invalid_tokens = [
            "ghp_short",  # Too short
            "ghp_12345678901234567890123456789012345",  # Too short (39 chars)
            "ghs_123456789012345678901234567890123456",  # Wrong prefix
        ]
        
        for token in invalid_tokens:
            result = classify_token(token)
            assert result != TokenType.GITHUB_TOKEN
            assert not _is_github_token(token)


class TestGCPTokenClassification:
    """Test GCP token classification."""
    
    def test_gcp_oauth_token_valid(self):
        """Test valid GCP OAuth token classification."""
        # GCP OAuth tokens are typically ~180 chars starting with 'ya29.'
        valid_token = "ya29." + "a" * 140
        
        result = classify_token(valid_token)
        assert result == TokenType.GCP_OAUTH_TOKEN
        assert _is_gcp_oauth_token(valid_token)
    
    def test_gcp_oauth_token_invalid(self):
        """Test invalid GCP OAuth token rejection."""
        invalid_tokens = [
            "ya29.short",  # Too short
            "yb29." + "a" * 140,  # Wrong prefix
        ]
        
        for token in invalid_tokens:
            result = classify_token(token)
            assert result != TokenType.GCP_OAUTH_TOKEN
            assert not _is_gcp_oauth_token(token)
    
    def test_gcp_service_account_valid(self):
        """Test valid GCP service account classification."""
        valid_indicators = [
            '"type": "service_account"',
            '"private_key_id": "1234567890abcdef"',
            '"private_key": "-----BEGIN PRIVATE KEY-----\\nMII...'
        ]
        
        for indicator in valid_indicators:
            result = classify_token(indicator)
            assert result == TokenType.GCP_SERVICE_ACCOUNT
            assert _is_gcp_service_account(indicator)


class TestFacebookTokenClassification:
    """Test Facebook token classification."""
    
    def test_facebook_access_token_valid(self):
        """Test valid Facebook access token classification."""
        valid_tokens = [
            "EAACEdEose0cBA1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "EAACEdEose0cBA" + "a" * 50  # Minimum length
        ]
        
        for token in valid_tokens:
            result = classify_token(token)
            assert result == TokenType.FACEBOOK_ACCESS_TOKEN
            assert _is_facebook_access_token(token)
    
    def test_facebook_access_token_invalid(self):
        """Test invalid Facebook access token rejection."""
        invalid_tokens = [
            "EAACEdEose0cBA",  # Too short
            "EBACEdEose0cBA" + "a" * 50,  # Wrong prefix
        ]
        
        for token in invalid_tokens:
            result = classify_token(token)
            assert result != TokenType.FACEBOOK_ACCESS_TOKEN
            assert not _is_facebook_access_token(token)


class TestJWTTokenClassification:
    """Test JWT token classification."""
    
    def test_jwt_token_valid(self):
        """Test valid JWT token classification."""
        # These are example JWTs with proper structure but fake signatures
        valid_jwts = [
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJleGFtcGxlLmNvbSIsImV4cCI6MTYxNzIyMzAwMH0.signature_here_but_not_real"
        ]
        
        for jwt in valid_jwts:
            result = classify_token(jwt)
            assert result == TokenType.JWT
            assert _is_jwt_token(jwt)
    
    def test_jwt_token_invalid(self):
        """Test invalid JWT token rejection."""
        invalid_jwts = [
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",  # Only one part
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkw",  # Only two parts
            "invalid.jwt.token",  # Invalid base64
        ]
        
        for jwt in invalid_jwts:
            result = classify_token(jwt)
            assert result != TokenType.JWT
            assert not _is_jwt_token(jwt)


class TestPrivateKeyClassification:
    """Test private key classification."""
    
    def test_private_key_valid(self):
        """Test valid private key classification."""
        valid_indicators = [
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN DSA PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN PRIVATE KEY-----",
            "-----BEGIN OPENSSH PRIVATE KEY-----",
        ]
        
        for indicator in valid_indicators:
            # Add some context to make it more realistic
            key_with_context = f"{indicator}\\nMII...private key data...\\n-----END PRIVATE KEY-----"
            result = classify_token(key_with_context)
            assert result == TokenType.PRIVATE_KEY
            assert _is_private_key(key_with_context)


class TestAzureTokenClassification:
    """Test Azure token classification."""
    
    def test_azure_client_secret_valid(self):
        """Test valid Azure client secret classification."""
        # Only GUIDs are classified as Azure client secrets
        valid_secrets = [
            "12345678-1234-1234-1234-123456789012",  # GUID format
        ]
        
        for secret in valid_secrets:
            result = classify_token(secret)
            assert result == TokenType.AZURE_CLIENT_SECRET
            assert _is_azure_client_secret(secret)
    
    def test_azure_client_secret_invalid(self):
        """Test invalid Azure client secret rejection."""
        # High entropy strings are now classified as generic OAuth tokens, not Azure
        invalid_secrets = [
            "12345678-1234-1234-1234-12345678901",  # Too short GUID
            "short",  # Too short
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # Low entropy
            "abcdefghijklmnopqrstuvwxyz0123456789",  # High entropy string (now generic OAuth)
        ]
        
        for secret in invalid_secrets:
            result = classify_token(secret)
            assert result != TokenType.AZURE_CLIENT_SECRET
            assert not _is_azure_client_secret(secret)


class TestGenericTokenClassification:
    """Test generic token classification."""
    
    def test_generic_oauth_token_valid(self):
        """Test valid generic OAuth token classification."""
        valid_tokens = [
            "abcdefghijklmnopqrstuvwxyz0123456789",  # 32 chars, high entropy
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",  # 32 chars, high entropy
        ]
        
        for token in valid_tokens:
            result = classify_token(token)
            # Should be OAUTH_TOKEN for base64-like high entropy strings
            assert result == TokenType.OAUTH_TOKEN
            assert _is_generic_oauth_token(token)
    
    def test_generic_high_entropy_valid(self):
        """Test valid generic high entropy token classification."""
        valid_tokens = [
            "abcdefghijklmnopqrstuvwxyz012345!@#$%",  # High entropy with non-base64 symbols
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnop!@#$%^&*",  # Longer with symbols
        ]
        
        for token in valid_tokens:
            result = classify_token(token)
            assert result == TokenType.GENERIC_HIGH_ENTROPY
            assert _is_high_entropy_token(token)
    
    def test_low_entropy_rejection(self):
        """Test rejection of low entropy strings."""
        low_entropy_strings = [
            "password",  # Common word
            "aaaaaaaaaaaaaaaaaaaa",  # Repeated character
            "12345678901234567890",  # All digits
            "abcdefghijklmnopqrst",  # All letters, sequential
        ]
        
        for string in low_entropy_strings:
            result = classify_token(string)
            assert result is None
            assert not _is_high_entropy_token(string)


class TestClassificationPrecedence:
    """Test classification precedence and edge cases."""
    
    def test_empty_and_short_values(self):
        """Test that empty and short values return None."""
        empty_values = [
            "",
            " ",
            "short",
            "123456789012345",  # 15 chars
        ]
        
        for value in empty_values:
            result = classify_token(value)
            assert result is None
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        token_with_whitespace = "  AKIAIOSFODNN7EXAMPLE  "
        result = classify_token(token_with_whitespace)
        assert result == TokenType.AWS_ACCESS_KEY
    
    def test_precedence_aws_over_generic(self):
        """Test that specific patterns take precedence over generic ones."""
        # This should be classified as AWS Access Key, not generic high entropy
        aws_key = "AKIAIOSFODNN7EXAMPLE"
        result = classify_token(aws_key)
        assert result == TokenType.AWS_ACCESS_KEY
    
    def test_precedence_stripe_over_generic(self):
        """Test that Stripe patterns take precedence over generic ones."""
        stripe_key = "sk_live_123456789012345678901234"
        result = classify_token(stripe_key)
        assert result == TokenType.STRIPE_API_KEY_LIVE


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_string_handling(self):
        """Test that empty string input returns None."""
        result = classify_token("")
        assert result is None
    
    def test_very_long_string(self):
        """Test classification with very long strings."""
        # Private key indicator in a long string
        long_string = "a" * 1000 + "-----BEGIN PRIVATE KEY-----" + "b" * 1000
        result = classify_token(long_string)
        assert result == TokenType.PRIVATE_KEY
    
    def test_mixed_content(self):
        """Test classification with mixed content."""
        # JWT in JSON context
        json_with_jwt = '{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"}'
        result = classify_token(json_with_jwt)
        assert result == TokenType.JWT
    
    def test_very_short_values(self):
        """Test that very short values are rejected."""
        short_values = ["a", "12", "abc", "1234"]
        for value in short_values:
            result = classify_token(value)
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__])