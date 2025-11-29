"""
Unit tests for secret detection rules.

Tests all secret detection rules to ensure they correctly identify
vulnerabilities and handle edge cases appropriately.
"""

import pytest
import pathlib
import tempfile
from unittest.mock import Mock

from sentinel.rules.secrets import (
    HighEntropyStringRule,
    AWSAccessKeyRule,
    AWSSecretKeyRule,
    GCPServiceAccountRule,
    AzureClientSecretRule,
    StripeAPIKeyRule,
    JWTSecretRule,
    PrivateKeyRule,
    HardcodedPasswordRule,
    OAuthTokenRule,
    GenericAPIKeyRule,
)
from sentinel.rules.base import Finding


class TestHighEntropyStringRule:
    """Test high entropy string detection."""

    def setup_method(self):
        self.rule = HighEntropyStringRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_high_entropy_string(self):
        """Test that high entropy strings are detected."""
        content = """
        api_key = "ThisIsAVeryRandomStringWithHighEntropy1234567890"
        password = "weakpassword"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1
        assert findings[0].rule_id == "SECRET_HIGH_ENTROPY"
        assert findings[0].severity == "high"

    def test_ignores_low_entropy_strings(self):
        """Test that low entropy strings are ignored."""
        content = """
        message = "This is a normal sentence with words and punctuation."
        number = "12345678901234567890"
        repeated = "aaaaaaaaaaaaaaaaaaaa"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0

    def test_ignores_short_strings(self):
        """Test that short strings are ignored."""
        content = 'token = "short"'
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0

    def test_confidence_calculation(self):
        """Test that confidence is calculated based on entropy."""
        content = 'key = "ThisIsAVeryRandomStringWithHighEntropy1234567890"'
        findings = self.rule.apply(self.test_file, content)
        assert findings[0].confidence is not None
        assert 0.0 <= findings[0].confidence <= 1.0


class TestAWSAccessKeyRule:
    """Test AWS Access Key detection."""

    def setup_method(self):
        self.rule = AWSAccessKeyRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_aws_access_key(self):
        """Test that AWS Access Keys are detected."""
        content = """
        aws_key = "AKIAIOSFODNN7EXAMPLE"
        another_key = "AKIAJABCDEFGHIJKLMNO"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 2
        assert all(f.rule_id == "SECRET_AWS_ACCESS_KEY" for f in findings)
        assert all(f.severity == "high" for f in findings)

    def test_ignores_invalid_aws_keys(self):
        """Test that invalid AWS Access Keys are ignored."""
        content = """
        invalid1 = "AKIA1234567890123"     # Too short (15 chars)
        invalid2 = "AKIAIOSFODNN7EXAMP"    # Too short (17 chars)
        invalid3 = "AKIAiosfodnn7example"  # Lowercase
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0

    def test_confidence_is_high(self):
        """Test that AWS Access Key findings have high confidence."""
        content = 'key = "AKIAIOSFODNN7EXAMPLE"'
        findings = self.rule.apply(self.test_file, content)
        assert findings[0].confidence == 0.95


class TestAWSSecretKeyRule:
    """Test AWS Secret Key detection."""

    def setup_method(self):
        self.rule = AWSSecretKeyRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_aws_secret_key(self):
        """Test that AWS Secret Keys are detected."""
        content = """
        aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        another_secret = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 1
        assert all(f.rule_id == "SECRET_AWS_SECRET_KEY" for f in findings)
        assert all(f.severity == "high" for f in findings)

    def test_ignores_low_entropy_secrets(self):
        """Test that low entropy 40-char strings are ignored."""
        content = """
        not_secret = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        all_digits = "1234567890123456789012345678901234567890"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0


class TestGCPServiceAccountRule:
    """Test GCP Service Account detection."""

    def setup_method(self):
        self.rule = GCPServiceAccountRule()
        self.test_file = pathlib.Path("test.json")

    def test_detects_gcp_service_account(self):
        """Test that GCP service account patterns are detected."""
        content = '''
        {
          "type": "service_account",
          "project_id": "my-project",
          "private_key_id": "abc123def456",
          "private_key": "-----BEGIN PRIVATE KEY-----\\nMII..."
        }
        '''

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 1
        assert all(f.rule_id == "SECRET_GCP_SERVICE_ACCOUNT" for f in findings)
        assert all(f.severity == "high" for f in findings)


class TestAzureClientSecretRule:
    """Test Azure Client Secret detection."""

    def setup_method(self):
        self.rule = AzureClientSecretRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_azure_guid_secrets(self):
        """Test that Azure GUID secrets are detected."""
        content = """
        azure_secret = "12345678-1234-1234-1234-123456789012"
        another_secret = "abcdef00-1234-5678-9abc-def123456789"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 1
        assert all(f.rule_id == "SECRET_AZURE_CLIENT_SECRET" for f in findings)

    def test_detects_azure_base64_secrets(self):
        """Test that Azure base64-like secrets are detected."""
        content = 'secret = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"'
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 1


class TestStripeAPIKeyRule:
    """Test Stripe API Key detection."""

    def setup_method(self):
        self.rule = StripeAPIKeyRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_stripe_live_keys(self):
        """Test that Stripe live keys are detected."""
        content = """
        stripe_secret = "sk_live_123456789012345678901234"
        stripe_public = "pk_live_123456789012345678901234"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 2
        assert all(f.rule_id == "SECRET_STRIPE_API_KEY" for f in findings)

    def test_detects_stripe_test_keys(self):
        """Test that Stripe test keys are detected."""
        content = """
        stripe_test_secret = "sk_test_123456789012345678901234"
        stripe_test_public = "pk_test_123456789012345678901234"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 2

    def test_ignores_invalid_stripe_keys(self):
        """Test that invalid Stripe keys are ignored."""
        content = """
        too_short = "sk_test_123"
        wrong_prefix = "ak_test_123456789012345678901234"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0


class TestJWTSecretRule:
    """Test JWT token detection."""

    def setup_method(self):
        self.rule = JWTSecretRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_jwt_tokens(self):
        """Test that JWT tokens are detected."""
        content = """
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        another_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwic3ViIjoidGVzdCJ9.signature"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 2
        assert all(f.rule_id == "SECRET_JWT" for f in findings)
        assert all(f.severity == "medium" for f in findings)


class TestPrivateKeyRule:
    """Test private key detection."""

    def setup_method(self):
        self.rule = PrivateKeyRule()
        self.test_file = pathlib.Path("test.key")

    def test_detects_rsa_private_key(self):
        """Test that RSA private keys are detected."""
        content = "-----BEGIN RSA PRIVATE KEY-----"
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1
        assert findings[0].rule_id == "SECRET_PRIVATE_KEY"
        assert findings[0].confidence == 0.99

    def test_detects_ec_private_key(self):
        """Test that EC private keys are detected."""
        content = "-----BEGIN EC PRIVATE KEY-----"
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1

    def test_detects_openssh_private_key(self):
        """Test that OpenSSH private keys are detected."""
        content = "-----BEGIN OPENSSH PRIVATE KEY-----"
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 1

    def test_ignores_non_key_content(self):
        """Test that non-key content is ignored."""
        content = "This is not a private key"
        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0


class TestHardcodedPasswordRule:
    """Test hardcoded password detection."""

    def setup_method(self):
        self.rule = HardcodedPasswordRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_hardcoded_passwords(self):
        """Test that hardcoded passwords are detected."""
        content = """
        password = "mysecretpassword123"
        passwd = "anotherpassword"
        pwd = "securepwd"
        secret = "verysecretvalue"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 3
        assert all(f.rule_id == "SECRET_HARDCODED_PASSWORD" for f in findings)
        assert all(f.severity == "high" for f in findings)

    def test_ignores_test_values(self):
        """Test that test/example values are ignored."""
        content = """
        password = "test"
        password = "example"
        password = "placeholder"
        password = "changeme"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) == 0


class TestOAuthTokenRule:
    """Test OAuth token detection."""

    def setup_method(self):
        self.rule = OAuthTokenRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_oauth_tokens_with_context(self):
        """Test that OAuth tokens are detected when context suggests it."""
        content = """
        oauth_token = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"
        bearer_token = "1234567890123456789012345678901234567890"
        token = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 2
        assert all(f.rule_id == "SECRET_OAUTH_TOKEN" for f in findings)
        assert all(f.severity == "medium" for f in findings)


class TestGenericAPIKeyRule:
    """Test generic API key detection."""

    def setup_method(self):
        self.rule = GenericAPIKeyRule()
        self.test_file = pathlib.Path("test.py")

    def test_detects_generic_api_keys(self):
        """Test that generic API keys are detected."""
        content = """
        api_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
        apikey = "abcdefghijklmnopqrstuvwxyz123456"
        api-key = "12345678901234567890123456789012"
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"
        """

        findings = self.rule.apply(self.test_file, content)
        assert len(findings) >= 3
        assert all(f.rule_id == "SECRET_GENERIC_API_KEY" for f in findings)
        assert all(f.severity == "medium" for f in findings)


class TestRuleRobustness:
    """Test rule robustness and error handling."""

    def test_rules_handle_empty_content(self):
        """Test that rules handle empty content without crashing."""
        rules = [
            HighEntropyStringRule(),
            AWSAccessKeyRule(),
            AWSSecretKeyRule(),
            GCPServiceAccountRule(),
            AzureClientSecretRule(),
            StripeAPIKeyRule(),
            JWTSecretRule(),
            PrivateKeyRule(),
            HardcodedPasswordRule(),
            OAuthTokenRule(),
            GenericAPIKeyRule(),
        ]

        test_file = pathlib.Path("test.py")

        for rule in rules:
            findings = rule.apply(test_file, "")
            assert isinstance(findings, list)
            # Rules should not crash on empty content

    def test_rules_handle_binary_like_content(self):
        """Test that rules handle binary-like content without crashing."""
        content = "Binary data: \x00\x01\x02\x03\x04\x05"

        rules = [
            HighEntropyStringRule(),
            AWSAccessKeyRule(),
            PrivateKeyRule(),
        ]

        test_file = pathlib.Path("test.bin")

        for rule in rules:
            findings = rule.apply(test_file, content)
            assert isinstance(findings, list)
            # Rules should not crash on binary-like content

    def test_rules_return_proper_finding_structure(self):
        """Test that all rules return properly structured Finding objects."""
        content = """
        password = "testpassword123"
        api_key = "testapikey12345678901234567890"
        """

        rules = [
            HardcodedPasswordRule(),
            GenericAPIKeyRule(),
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
