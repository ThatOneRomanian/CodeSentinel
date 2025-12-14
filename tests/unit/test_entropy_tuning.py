"""
Unit tests for entropy tuning and edge-case handling.

Tests the enhanced entropy detection, JWT validation, and PEM detection
improvements implemented in Phase 2.5 Rule Hardening.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pathlib
from unittest.mock import Mock

from sentinel.utils.entropy import (
    shannon_entropy, 
    is_high_entropy, 
    is_likely_secret,
    calculate_entropy_score,
    _is_common_pattern,
    _has_sufficient_diversity,
    _is_sequential_pattern
)
from sentinel.rules.token_types import classify_token, TokenType, _is_jwt_token, _is_valid_jwt_header, _is_valid_jwt_payload
from sentinel.rules.secrets import (
    HighEntropyStringRule,
    JWTSecretRule,
    PrivateKeyRule,
    AWSAccessKeyRule,
    AWSSecretKeyRule,
    AzureClientSecretRule,
    StripeAPIKeyRule,
    OAuthTokenRule
)
from sentinel.rules.base import Finding


class TestEntropyTuning:
    """Test entropy threshold optimizations and filtering improvements."""

    def test_shannon_entropy_calculation(self):
        """Test basic Shannon entropy calculation."""
        # Low entropy strings
        assert shannon_entropy("aaaaa") < 1.0
        assert shannon_entropy("password") < 3.0
        
        # Medium entropy strings
        assert 3.0 < shannon_entropy("Password123!") < 4.0
        
        # High entropy strings
        assert shannon_entropy("LKh7aM#s!@n3*2pQ9rT1vX5z8bD0") > 4.0

    def test_is_high_entropy_thresholds(self):
        """Test entropy threshold detection with various thresholds."""
        test_string = "xYzAbCdEfGhIjKlMnOpQrStUvWxYz1"
        
        # Should be high entropy at 4.0 threshold
        assert is_high_entropy(test_string, threshold=4.0)
        
        # Should not be high entropy at 5.0 threshold
        assert not is_high_entropy(test_string, threshold=5.0)

    def test_is_likely_secret_enhanced_detection(self):
        """Test enhanced secret detection with filtering."""
        # Real secret-like strings
        assert is_likely_secret("xYzAbCdEfGhIjKlMnOpQrStUvWxYz1", min_length=20, threshold=4.0)
        assert is_likely_secret("LKh7aM#s!@n3*2pQ9rT1vX5z8bD0", min_length=20, threshold=4.0)
        
        # Common patterns that should be filtered out
        assert not is_likely_secret("12345678901234567890", min_length=20, threshold=4.0)  # All digits
        assert not is_likely_secret("aaaaaaaaaaaaaaaaaaaa", min_length=20, threshold=4.0)  # Repeated chars
        assert not is_likely_secret("abcdefghijklmnopqrst", min_length=20, threshold=4.0)  # Sequential letters

    def test_common_pattern_filtering(self):
        """Test filtering of common non-secret patterns."""
        # UUIDs (should be filtered)
        assert _is_common_pattern("12345678-1234-1234-1234-123456789012")
        
        # Base64 padding-heavy strings
        assert _is_common_pattern("abc================")
        
        # Test/example patterns
        assert _is_common_pattern("test_token_example_123")
        assert _is_common_pattern("placeholder_secret_key")
        
        # Real secrets should not be filtered
        assert not _is_common_pattern("xYzAbCdEfGhIjKlMnOpQrStUvWxYz1")

    def test_character_diversity_requirements(self):
        """Test character diversity filtering."""
        # High diversity (should pass)
        assert _has_sufficient_diversity("aB1#dE2$fG3%hI4&jK5")
        
        # Low diversity (should fail)
        assert not _has_sufficient_diversity("aaaaaaaaaaaaaaaaaaaa")
        assert not _has_sufficient_diversity("11111111111111111111")

    def test_sequential_pattern_detection(self):
        """Test detection of sequential patterns."""
        # Sequential numbers
        assert _is_sequential_pattern("12345678901234567890")
        
        # Sequential letters
        assert _is_sequential_pattern("abcdefghijklmnopqrst")
        
        # Non-sequential (should return False)
        assert not _is_sequential_pattern("xYzAbCdEfGhIjKlMnOp")

    def test_entropy_score_calculation(self):
        """Test normalized entropy score calculation."""
        # High entropy string should have high score
        high_entropy = "LKh7aM#s!@n3*2pQ9rT1vX5z8bD0"
        high_score = calculate_entropy_score(high_entropy)
        assert high_score > 0.7
        
        # Low entropy string should have low score
        low_entropy = "password123"
        low_score = calculate_entropy_score(low_entropy)
        assert low_score < 0.5
        
        # Score should be between 0 and 1
        assert 0.0 <= calculate_entropy_score("test") <= 1.0


class TestJWTValidation:
    """Test enhanced JWT detection with structural validation."""

    def test_valid_jwt_detection(self):
        """Test detection of valid JWT tokens."""
        # Standard JWT token
        valid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert _is_jwt_token(valid_jwt)
        
        # JWT with different algorithm - use a real JWT with proper signature
        jwt_rs256 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.EkN-DOsNsC9AhBaBgKdMvO6ZSO2R0c8JX_TiKzW4V4Q"
        assert _is_jwt_token(jwt_rs256)

    def test_invalid_jwt_rejection(self):
        """Test rejection of invalid JWT tokens."""
        # Wrong number of parts
        assert not _is_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ")
        
        # Invalid base64 characters
        assert not _is_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c!")
        
        # Invalid header structure
        invalid_header_jwt = "invalid_header.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert not _is_jwt_token(invalid_header_jwt)

    def test_jwt_header_validation(self):
        """Test JWT header validation."""
        # Valid header
        valid_header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        assert _is_valid_jwt_header(valid_header)
        
        # Invalid algorithm
        invalid_alg_header = "eyJhbGciOiJJTlZBTElEX0FMRyIsInR5cCI6IkpXVCJ9"
        assert not _is_valid_jwt_header(invalid_alg_header)
        
        # Invalid type
        invalid_typ_header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IklOVkFMSUQifQ"
        assert not _is_valid_jwt_header(invalid_typ_header)

    def test_jwt_payload_validation(self):
        """Test JWT payload validation."""
        # Valid payload
        valid_payload = "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
        assert _is_valid_jwt_payload(valid_payload)
        
        # Invalid JSON payload
        invalid_json_payload = "bm90X2FfdmFsaWRfanNvbg"
        assert not _is_valid_jwt_payload(invalid_json_payload)

    def test_jwt_classification(self):
        """Test JWT classification in token types."""
        valid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert classify_token(valid_jwt) == TokenType.JWT


class TestPEMDetection:
    """Test improved PEM detection for various key formats."""

    def test_private_key_detection(self):
        """Test detection of various private key formats."""
        # RSA private key
        rsa_key = "-----BEGIN RSA PRIVATE KEY-----"
        assert classify_token(rsa_key) == TokenType.PRIVATE_KEY
        
        # EC private key
        ec_key = "-----BEGIN EC PRIVATE KEY-----"
        assert classify_token(ec_key) == TokenType.PRIVATE_KEY
        
        # OpenSSH private key
        openssh_key = "-----BEGIN OPENSSH PRIVATE KEY-----"
        assert classify_token(openssh_key) == TokenType.PRIVATE_KEY
        
        # Generic private key
        generic_key = "-----BEGIN PRIVATE KEY-----"
        assert classify_token(generic_key) == TokenType.PRIVATE_KEY
        
        # PGP private key
        pgp_key = "-----BEGIN PGP PRIVATE KEY BLOCK-----"
        assert classify_token(pgp_key) == TokenType.PRIVATE_KEY

    def test_pem_with_extra_spacing(self):
        """Test PEM detection with extra spacing and comments."""
        # PEM with spaces
        spaced_pem = "  -----BEGIN RSA PRIVATE KEY-----  "
        assert classify_token(spaced_pem) == TokenType.PRIVATE_KEY
        
        # PEM with comments
        commented_pem = "# This is a private key\n-----BEGIN RSA PRIVATE KEY-----"
        assert classify_token(commented_pem) == TokenType.PRIVATE_KEY

    def test_non_pem_content_rejection(self):
        """Test that non-PEM content is properly rejected."""
        # Similar looking but not PEM
        assert classify_token("-----BEGIN SOMETHING ELSE-----") is None
        assert classify_token("This is not a private key") is None


class TestHighEntropyRuleOptimization:
    """Test optimized high-entropy rule with token classification integration."""

    def setup_method(self):
        self.rule = HighEntropyStringRule()
        self.test_file = pathlib.Path("test.py")

    def test_reduces_noise_from_common_patterns(self):
        """Test that common high-entropy patterns are filtered out."""
        content = """
        # Common patterns that should not trigger high-entropy rule
        uuid = "12345678-1234-1234-1234-123456789012"
        sequential = "12345678901234567890"
        repeated = "aaaaaaaaaaaaaaaaaaaa"
        test_token = "test_example_token_12345"
        """
        
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0

    def test_detects_legitimate_high_entropy(self):
        """Test that legitimate high-entropy secrets are still detected."""
        content = """
        # Real secrets that should be detected
        secret1 = "xYzAbCdEfGhIjKlMnOpQrStUvWxYz1"
        secret2 = "LKh7aM#s!@n3*2pQ9rT1vX5z8bD0"
        """
        
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 2
        assert all(f.rule_id == "SECRET_HIGH_ENTROPY" for f in findings)

    def test_integrates_with_token_classification(self):
        """Test that high-entropy rule defers to provider-specific classification."""
        content = """
        # Provider-specific tokens that should NOT trigger high-entropy rule
        aws_key = "AKIAIOSFODNN7EXAMPLE"
        stripe_key = "sk_test_123456789012345678901234"
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        """
        
        findings = self.rule.apply(self.test_file, content)
        # Should not detect these as they are classified by provider-specific rules
        assert len(findings) == 0

    def test_confidence_based_on_entropy_score(self):
        """Test that confidence is calculated based on entropy score."""
        content = 'secret = "xYzAbCdEfGhIjKlMnOpQrStUvWxYz1"'
        
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1
        assert findings[0].confidence is not None
        assert 0.0 <= findings[0].confidence <= 1.0
        # Higher entropy should result in higher confidence
        assert findings[0].confidence > 0.5


class TestProviderRuleIntegration:
    """Test that provider-specific rules work correctly with entropy improvements."""

    def test_aws_access_key_rule(self):
        """Test AWS Access Key rule with token classification."""
        rule = AWSAccessKeyRule()
        test_file = pathlib.Path("test.py")
        
        content = 'aws_key = "AKIAIOSFODNN7EXAMPLE"'
        findings = rule.apply(test_file, content)
        assert len(findings) == 1
        assert findings[0].rule_id == "SECRET_AWS_ACCESS_KEY"

    def test_aws_secret_key_rule(self):
        """Test AWS Secret Key rule with enhanced validation."""
        rule = AWSSecretKeyRule()
        test_file = pathlib.Path("test.py")
        
        content = 'aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
        findings = rule.apply(test_file, content)
        assert len(findings) == 1
        assert findings[0].rule_id == "SECRET_AWS_SECRET_KEY"

    def test_azure_client_secret_rule(self):
        """Test Azure Client Secret rule with GUID-only matching."""
        rule = AzureClientSecretRule()
        test_file = pathlib.Path("test.py")
        
        content = 'azure_secret = "12345678-1234-1234-1234-123456789012"'
        findings = rule.apply(test_file, content)
        assert len(findings) == 1
        assert findings[0].rule_id == "SECRET_AZURE_CLIENT_SECRET"

    def test_stripe_api_key_rule(self):
        """Test Stripe API Key rule with classification."""
        rule = StripeAPIKeyRule()
        test_file = pathlib.Path("test.py")
        
        content = """
        stripe_live = "sk_live_123456789012345678901234"
        stripe_test = "sk_test_123456789012345678901234"
        """
        findings = rule.apply(test_file, content)
        assert len(findings) == 2
        assert all(f.rule_id == "SECRET_STRIPE_API_KEY" for f in findings)

    def test_oauth_token_rule(self):
        """Test OAuth Token rule with context awareness."""
        rule = OAuthTokenRule()
        test_file = pathlib.Path("test.py")
        
        content = """
        oauth_token = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"
        bearer_token = "1234567890123456789012345678901234567890"
        """
        findings = rule.apply(test_file, content)
        assert len(findings) >= 1
        assert all(f.rule_id == "SECRET_OAUTH_TOKEN" for f in findings)


class TestEdgeCaseHandling:
    """Test edge cases and boundary conditions."""

    def test_short_strings_ignored(self):
        """Test that short strings are properly ignored."""
        assert not is_likely_secret("short", min_length=20, threshold=4.0)
        assert not is_likely_secret("1234567890123456789", min_length=20, threshold=4.0)  # 19 chars
        
        # Exactly at minimum length
        assert is_likely_secret("12345678901234567890", min_length=20, threshold=4.0)  # 20 chars

    def test_empty_and_none_values(self):
        """Test handling of empty and None values."""
        assert shannon_entropy("") == 0.0
        assert not is_high_entropy("", threshold=4.0)
        assert not is_likely_secret("", min_length=20, threshold=4.0)
        
        # None values should be handled by calling code

    def test_binary_and_special_characters(self):
        """Test handling of binary data and special characters."""
        # Binary-like data
        binary_data = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
        entropy = shannon_entropy(binary_data)
        assert entropy > 0.0
        
        # Special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        assert is_high_entropy(special_chars, threshold=4.0)

    def test_unicode_and_international_characters(self):
        """Test handling of Unicode and international characters."""
        unicode_string = "café résumé naïve façade"
        entropy = shannon_entropy(unicode_string)
        assert entropy > 0.0
        
        # Should not be classified as high entropy secret
        assert not is_likely_secret(unicode_string, min_length=20, threshold=4.0)