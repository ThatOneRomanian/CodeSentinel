"""
Unit tests for Provider-Aware AI Explainer Integration in CodeSentinel Phase 2.

Tests the AI explainer integration with provider-aware findings, including
token classification, enhanced risk scoring, and provider-specific explanations.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pytest
import pathlib
from unittest.mock import Mock, patch
from typing import List, Dict, Any, Optional

from sentinel.llm.explainer import ExplanationEngine
from sentinel.rules.base import Finding
from sentinel.rules.severity import (
    calculate_enhanced_risk_score,
    get_provider_aware_severity,
    get_token_type_risk_context
)
from sentinel.rules.token_types import TokenType, classify_token
from sentinel.llm.provider import LLMProvider


class MockProvider(LLMProvider):
    """Mock LLM provider for testing provider-aware explanations."""
    
    def generate(self, prompt: str) -> str:
        # Simulate provider-aware responses based on prompt content
        if "AWS" in prompt or "aws" in prompt:
            return "This is an AWS-related security risk with critical impact on cloud infrastructure."
        elif "test" in prompt.lower():
            return "This is a test key with reduced risk in non-production environments."
        elif "production" in prompt.lower():
            return "This is a production key with elevated risk requiring immediate attention."
        else:
            return "Generic security explanation for the detected finding."


class TestProviderAwareRiskScoring:
    """Test provider-aware risk scoring and severity adjustments."""
    
    def test_calculate_enhanced_risk_score_aws_access_key(self):
        """Test enhanced risk scoring for AWS access keys."""
        token = "AKIAIOSFODNN7EXAMPLE"
        score = calculate_enhanced_risk_score(
            base_severity="high",
            token_value=token,
            tags=["aws", "access-key", "cloud-provider"],
            language="python",
            confidence=0.95
        )
        
        # AWS access keys should have elevated risk scores
        assert 7.0 <= score <= 10.0
        assert score > 7.0  # Should be higher than base high severity
    
    def test_calculate_enhanced_risk_score_stripe_test_key(self):
        """Test enhanced risk scoring for Stripe test keys."""
        token = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
        score = calculate_enhanced_risk_score(
            base_severity="high",
            token_value=token,
            tags=["stripe", "api-key", "payment-provider", "test"],
            language="javascript",
            confidence=0.85
        )
        
        # Test keys should have reduced risk scores
        assert 1.0 <= score <= 7.0
        assert score < 7.0  # Should be lower than base high severity
    
    def test_calculate_enhanced_risk_score_stripe_live_key(self):
        """Test enhanced risk scoring for Stripe live keys."""
        token = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
        score = calculate_enhanced_risk_score(
            base_severity="high",
            token_value=token,
            tags=["stripe", "api-key", "payment-provider", "live"],
            language="javascript",
            confidence=0.95
        )
        
        # Live keys should have elevated risk scores
        assert 7.0 <= score <= 10.0
        assert score > 7.0  # Should be higher than base high severity
    
    def test_calculate_enhanced_risk_score_private_key(self):
        """Test enhanced risk scoring for private keys."""
        token = "-----BEGIN RSA PRIVATE KEY-----"
        score = calculate_enhanced_risk_score(
            base_severity="critical",
            token_value=token,
            tags=["private-key", "pem", "cryptographic-material"],
            language="python",
            confidence=0.99
        )
        
        # Private keys should have the highest risk scores
        assert 8.0 <= score <= 10.0
    
    def test_calculate_enhanced_risk_score_generic_high_entropy(self):
        """Test enhanced risk scoring for generic high entropy strings."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        score = calculate_enhanced_risk_score(
            base_severity="medium",
            token_value=token,
            tags=["high-entropy", "unclassified-token"],
            language="python",
            confidence=0.7
        )
        
        # Generic high entropy should have base risk scores
        assert 4.0 <= score <= 6.0
    
    def test_calculate_enhanced_risk_score_without_token(self):
        """Test enhanced risk scoring without token classification."""
        score = calculate_enhanced_risk_score(
            base_severity="medium",
            token_value=None,
            tags=["generic"],
            language="python",
            confidence=0.8
        )
        
        # Should fall back to base scoring
        assert 4.0 <= score <= 6.0
    
    def test_get_provider_aware_severity_test_environment(self):
        """Test severity adjustment for test environments."""
        adjusted_severity = get_provider_aware_severity(
            base_severity="high",
            token_value="sk_test_4eC39HqLyjWDarjtT1zdp7dc",
            tags=["test", "staging", "api-key"]
        )
        
        # Test environments should downgrade severity
        assert adjusted_severity == "medium"
    
    def test_get_provider_aware_severity_production_environment(self):
        """Test severity adjustment for production environments."""
        adjusted_severity = get_provider_aware_severity(
            base_severity="high",
            token_value="sk_live_4eC39HqLyjWDarjtT1zdp7dc",
            tags=["production", "live", "api-key"]
        )
        
        # Production environments should upgrade severity
        assert adjusted_severity == "critical"
    
    def test_get_provider_aware_severity_no_adjustment(self):
        """Test severity adjustment when no context is provided."""
        adjusted_severity = get_provider_aware_severity(
            base_severity="medium",
            token_value=None,
            tags=None
        )
        
        # Should return original severity
        assert adjusted_severity == "medium"
    
    def test_get_token_type_risk_context_aws(self):
        """Test risk context for AWS token types."""
        context = get_token_type_risk_context("AKIAIOSFODNN7EXAMPLE")
        
        assert context["type"] == "aws_access_key"
        assert context["risk_level"] == "high"
    
    def test_get_token_type_risk_context_stripe_live(self):
        """Test risk context for Stripe live keys."""
        context = get_token_type_risk_context("sk_live_4eC39HqLyjWDarjtT1zdp7dc")
        
        assert context["type"] == "stripe_api_key_live"
        assert context["risk_level"] == "high"
    
    def test_get_token_type_risk_context_stripe_test(self):
        """Test risk context for Stripe test keys."""
        context = get_token_type_risk_context("sk_test_4eC39HqLyjWDarjtT1zdp7dc")
        
        assert context["type"] == "stripe_api_key_test"
        assert context["risk_level"] == "low"
    
    def test_get_token_type_risk_context_private_key(self):
        """Test risk context for private keys."""
        context = get_token_type_risk_context("-----BEGIN RSA PRIVATE KEY-----")
        
        assert context["type"] == "private_key"
        assert context["risk_level"] == "critical"
    
    def test_get_token_type_risk_context_unknown(self):
        """Test risk context for unknown token types."""
        context = get_token_type_risk_context("some_random_string")
        
        assert context["type"] == "generic"
        assert context["risk_level"] == "medium"


class TestProviderAwareAIExplainer:
    """Test AI explainer integration with provider-aware findings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = MockProvider()
        self.explainer = ExplanationEngine()
        
        # Create provider-aware findings for testing
        self.provider_aware_findings = [
            # AWS Access Key
            Finding(
                rule_id="SECRET_AWS_ACCESS_KEY",
                file_path=pathlib.Path("config.py"),
                line=15,
                severity="high",
                excerpt="AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
                confidence=0.95,
                category="secrets.aws",
                tags=["aws", "access-key", "cloud-provider"],
                language="python"
            ),
            # Stripe Test Key
            Finding(
                rule_id="SECRET_STRIPE_API_KEY",
                file_path=pathlib.Path("payment.js"),
                line=42,
                severity="medium",
                excerpt="stripe_key: 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'",
                confidence=0.85,
                category="secrets.stripe.test",
                tags=["stripe", "api-key", "payment-provider", "test"],
                language="javascript"
            ),
            # Stripe Live Key
            Finding(
                rule_id="SECRET_STRIPE_API_KEY",
                file_path=pathlib.Path("production.js"),
                line=88,
                severity="high",
                excerpt="stripe_key: 'sk_live_4eC39HqLyjWDarjtT1zdp7dc'",
                confidence=0.95,
                category="secrets.stripe.live",
                tags=["stripe", "api-key", "payment-provider", "live", "production"],
                language="javascript"
            ),
            # Private Key
            Finding(
                rule_id="SECRET_PRIVATE_KEY",
                file_path=pathlib.Path("key.pem"),
                line=1,
                severity="critical",
                excerpt="-----BEGIN RSA PRIVATE KEY-----",
                confidence=0.99,
                category="secrets.crypto",
                tags=["private-key", "pem", "cryptographic-material"],
                language="text"
            ),
            # Generic High Entropy
            Finding(
                rule_id="SECRET_HIGH_ENTROPY",
                file_path=pathlib.Path("auth.py"),
                line=33,
                severity="medium",
                excerpt="token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'",
                confidence=0.7,
                category="secrets.generic",
                tags=["high-entropy", "unclassified-token"],
                language="python"
            )
        ]
    
    def test_explain_finding_with_provider_metadata(self):
        """Test explain_finding includes provider metadata in prompts."""
        aws_finding = self.provider_aware_findings[0]
        
        with patch.object(self.explainer, '_load_prompt_template') as mock_load:
            mock_load.return_value = "Template with {{category}} and {{tags}}"
            
            with patch.object(self.explainer, '_populate_template') as mock_populate:
                mock_populate.return_value = "Populated template"
                
                # Use a mock provider to avoid actual LLM calls
                mock_provider = Mock(spec=LLMProvider)
                mock_provider.generate.return_value = "Mock explanation"
                
                result = self.explainer.explain_finding(aws_finding, mock_provider)
                
                # Verify template population was called with provider metadata
                mock_populate.assert_called()
                call_args = mock_populate.call_args[0]
                assert call_args[1] == aws_finding
                assert "secrets.aws" in call_args[0]  # Category in template
                assert "aws" in call_args[0]  # Tags in template
    
    def test_explain_batch_with_provider_aware_findings(self):
        """Test explain_batch handles provider-aware findings correctly."""
        batch_result = self.explainer.explain_batch(self.provider_aware_findings, self.provider)
        
        # Should generate explanations for all unique rule_ids
        expected_rules = {
            "SECRET_AWS_ACCESS_KEY",
            "SECRET_STRIPE_API_KEY", 
            "SECRET_PRIVATE_KEY",
            "SECRET_HIGH_ENTROPY"
        }
        assert set(batch_result.keys()) == expected_rules
        
        # Each explanation should have the required structure
        for rule_id, explanation in batch_result.items():
            assert isinstance(explanation, dict)
            assert "explanation" in explanation
            assert "cwe_id" in explanation
            assert "remediation" in explanation
            assert "risk_score" in explanation
            assert "references" in explanation
    
    def test_template_population_includes_provider_fields(self):
        """Test template population includes category and tags fields."""
        finding = self.provider_aware_findings[0]  # AWS finding
        template = "Category: {{category}}, Tags: {{tags}}"
        
        populated = self.explainer._populate_template(template, finding)
        
        assert "secrets.aws" in populated
        assert "aws" in populated
        assert "access-key" in populated
        assert "cloud-provider" in populated
    
    def test_provider_aware_prompt_enhancement(self):
        """Test that prompts are enhanced with provider context."""
        finding = self.provider_aware_findings[1]  # Stripe test key
        
        # Mock the template loading and LLM generation
        with patch.object(self.explainer, '_load_prompt_template') as mock_load:
            mock_load.return_value = "Explain: {{category}} with tags {{tags}}"
            
            # Use a mock provider to capture the generated prompt
            mock_provider = Mock(spec=LLMProvider)
            mock_provider.generate.return_value = "Test key explanation"
            
            result = self.explainer.explain_finding(finding, mock_provider)
            
            # Verify the prompt was generated with provider context
            mock_provider.generate.assert_called_once()
            prompt = mock_provider.generate.call_args[0][0]
            assert "secrets.stripe.test" in prompt
            assert "test" in prompt
    
    def test_risk_score_alignment_with_provider_context(self):
        """Test that risk scores align with provider context."""
        # Test with production Stripe key (should have higher risk)
        production_finding = self.provider_aware_findings[2]
        
        with patch.object(self.explainer, 'explain_finding_with_templates') as mock_explain:
            mock_explain.return_value = {
                "explanation": "Production key risk",
                "cwe_id": "CWE-798",
                "remediation": "Rotate immediately",
                "risk_score": 8.5,  # Higher risk for production
                "references": ["https://example.com"]
            }
            
            # Use a mock provider
            mock_provider = Mock(spec=LLMProvider)
            result = self.explainer.explain_finding(production_finding, mock_provider)
            
            assert result["risk_score"] == 8.5
            # Check that explanation is a string and contains production context
            explanation = result["explanation"]
            assert isinstance(explanation, str)
            assert "production" in explanation.lower()
    
    def test_batch_explanation_preserves_provider_context(self):
        """Test that batch explanations preserve provider context across findings."""
        # Create multiple findings of the same rule but different providers
        stripe_findings = [
            f for f in self.provider_aware_findings 
            if f.rule_id == "SECRET_STRIPE_API_KEY"
        ]
        
        batch_result = self.explainer.explain_batch(stripe_findings, self.provider)
        
        # Should generate one explanation for the rule
        assert "SECRET_STRIPE_API_KEY" in batch_result
        
        explanation = batch_result["SECRET_STRIPE_API_KEY"]
        
        # The explanation should account for both test and live contexts
        assert isinstance(explanation["explanation"], str)
        assert len(explanation["explanation"]) > 0


class TestTokenClassificationIntegration:
    """Test integration between token classification and AI explainer."""
    
    def test_classify_token_integration_with_findings(self):
        """Test token classification integration with finding metadata."""
        test_cases = [
            ("AKIAIOSFODNN7EXAMPLE", "aws_access_key", "high"),
            ("sk_test_4eC39HqLyjWDarjtT1zdp7dc", "stripe_api_key_test", "low"),
            ("sk_live_4eC39HqLyjWDarjtT1zdp7dc", "stripe_api_key_live", "high"),
            ("-----BEGIN RSA PRIVATE KEY-----", "private_key", "critical"),
            ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "jwt", "medium"),
        ]
        
        for token_value, expected_type, expected_risk in test_cases:
            token_type = classify_token(token_value)
            assert token_type is not None
            assert token_type.value == expected_type
            
            context = get_token_type_risk_context(token_value)
            assert context["risk_level"] == expected_risk
    
    def test_provider_metadata_flow_to_ai_prompts(self):
        """Test that provider metadata flows correctly to AI prompts."""
        explainer = ExplanationEngine()
        
        # Create finding with provider metadata
        finding = Finding(
            rule_id="SECRET_AWS_ACCESS_KEY",
            file_path=pathlib.Path("test.py"),
            line=10,
            severity="high",
            excerpt="key = 'AKIAIOSFODNN7EXAMPLE'",
            confidence=0.95,
            category="secrets.aws",
            tags=["aws", "access-key", "cloud-provider"],
            language="python"
        )
        
        # Test template population
        template = "Rule: {{rule_id}}, Category: {{category}}, Tags: {{tags}}"
        populated = explainer._populate_template(template, finding)
        
        assert "SECRET_AWS_ACCESS_KEY" in populated
        assert "secrets.aws" in populated
        assert "aws" in populated
        assert "access-key" in populated
        assert "cloud-provider" in populated


if __name__ == "__main__":
    pytest.main([__file__])