"""
Unit tests for AI Explanation Batching in CodeSentinel Phase 2.

Tests the batching functionality that groups findings by rule type
to minimize LLM API calls and improve performance.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pytest
import pathlib
from unittest.mock import Mock, patch

from sentinel.llm.explainer import ExplanationEngine
from sentinel.rules.base import Finding, RuleMeta, create_default_rule_meta
from sentinel.llm.provider import LLMProvider


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    def generate(self, prompt: str) -> str:
        return f"Mock response for: {prompt[:50]}..."


class TestExplanationBatching:
    """Test explanation batching functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = MockProvider()
        self.explainer = ExplanationEngine()
        
        # Create sample findings for testing
        self.findings = [
            Finding(
                rule_id="secret_aws_key",
                file_path=pathlib.Path("test1.py"),
                line=10,
                severity="high",
                excerpt="AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
                confidence=0.95,
                category="secrets",
                language="python"
            ),
            Finding(
                rule_id="secret_aws_key",
                file_path=pathlib.Path("test2.py"),
                line=25,
                severity="high",
                excerpt="aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                confidence=0.95,
                category="secrets",
                language="python"
            ),
            Finding(
                rule_id="config_debug_enabled",
                file_path=pathlib.Path("config.json"),
                line=5,
                severity="medium",
                excerpt='"debug": true',
                confidence=0.85,
                category="config",
                language="json"
            ),
            Finding(
                rule_id="config_debug_enabled",
                file_path=pathlib.Path("settings.py"),
                line=15,
                severity="medium",
                excerpt="DEBUG = True",
                confidence=0.85,
                category="config",
                language="python"
            ),
            Finding(
                rule_id="hardcoded_password",
                file_path=pathlib.Path("auth.py"),
                line=42,
                severity="critical",
                excerpt='password = "secret123"',
                confidence=0.90,
                category="secrets",
                language="python"
            )
        ]
    
    def test_explain_batch_groups_by_rule_id(self):
        """Test that explain_batch groups findings by rule_id."""
        batch_result = self.explainer.explain_batch(self.findings, self.provider)
        
        # Should have explanations for each unique rule_id
        expected_rules = {"secret_aws_key", "config_debug_enabled", "hardcoded_password"}
        assert set(batch_result.keys()) == expected_rules
    
    def test_explain_batch_returns_correct_structure(self):
        """Test that explain_batch returns the correct data structure."""
        batch_result = self.explainer.explain_batch(self.findings, self.provider)
        
        for rule_id, explanation in batch_result.items():
            assert isinstance(explanation, dict)
            assert "explanation" in explanation
            assert "cwe_id" in explanation
            assert "remediation" in explanation
            assert "risk_score" in explanation
            assert "references" in explanation
    
    def test_explain_batch_uses_first_finding_as_representative(self):
        """Test that explain_batch uses the first finding of each rule as representative."""
        batch_result = self.explainer.explain_batch(self.findings, self.provider)
        
        # For secret_aws_key, the first finding has excerpt about AWS_ACCESS_KEY_ID
        aws_explanation = batch_result["secret_aws_key"]
        assert "AWS_ACCESS_KEY_ID" in aws_explanation["explanation"]
    
    def test_explain_batch_handles_empty_findings(self):
        """Test explain_batch with empty findings list."""
        batch_result = self.explainer.explain_batch([], self.provider)
        
        assert batch_result == {}
    
    def test_explain_batch_handles_single_finding(self):
        """Test explain_batch with single finding."""
        single_finding = [self.findings[0]]
        batch_result = self.explainer.explain_batch(single_finding, self.provider)
        
        assert len(batch_result) == 1
        assert "secret_aws_key" in batch_result
    
    def test_explain_batch_respects_safety_checks(self):
        """Test that explain_batch respects environment safety checks."""
        with patch.object(self.explainer, '_validate_environment_safety', return_value=False):
            batch_result = self.explainer.explain_batch(self.findings, self.provider)
            
            # Should return safety failure explanation for all rule_ids
            for rule_id, explanation in batch_result.items():
                assert "Safety check failed" in explanation["explanation"]
                assert explanation["cwe_id"] is None
                assert explanation["remediation"] is None
                assert explanation["risk_score"] is None
                assert explanation["references"] == []
    
    def test_explain_batch_with_mock_llm_calls(self):
        """Test explain_batch with mocked LLM provider."""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "Mock AI explanation"
        
        # Mock the explain_finding method to verify it's called per rule
        with patch.object(self.explainer, 'explain_finding') as mock_explain:
            mock_explain.return_value = {
                "explanation": "Mock explanation",
                "cwe_id": "CWE-798",
                "remediation": "Mock remediation",
                "risk_score": 7.5,
                "references": ["https://example.com"]
            }
            
            batch_result = self.explainer.explain_batch(self.findings, mock_provider)
            
            # Should call explain_finding once per unique rule_id
            assert mock_explain.call_count == 3  # 3 unique rule_ids
    
    def test_explain_batch_preserves_rule_metadata(self):
        """Test that explain_batch preserves rule metadata in explanations."""
        batch_result = self.explainer.explain_batch(self.findings, self.provider)
        
        for rule_id, explanation in batch_result.items():
            # Should include rule_id context in the explanation
            assert rule_id in explanation["explanation"]
    
    def test_explain_batch_performance_with_large_batch(self):
        """Test explain_batch performance with a large number of findings."""
        # Create many findings with few unique rule_ids
        large_findings = []
        for i in range(100):
            rule_id = f"rule_{i % 5}"  # Only 5 unique rule_ids
            large_findings.append(
                Finding(
                    rule_id=rule_id,
                    file_path=pathlib.Path(f"file_{i}.py"),
                    line=i,
                    severity="medium",
                    excerpt=f"Finding {i}",
                    confidence=0.8,
                    category="test",
                    language="python"
                )
            )
        
        batch_result = self.explainer.explain_batch(large_findings, self.provider)
        
        # Should only generate 5 explanations (one per unique rule_id)
        assert len(batch_result) == 5


class TestRuleMetaIntegration:
    """Test integration with RuleMeta for enhanced explanations."""
    
    def test_rule_meta_creation(self):
        """Test RuleMeta dataclass creation."""
        meta = create_default_rule_meta(
            category="secrets",
            cwe_ids=["CWE-798", "CWE-259"],
            risk_factors=["exposure", "hardcoded"],
            detection_method="regex",
            false_positive_rate=0.1,
            remediation_priority="high",
            tags=["api-key", "aws"],
            references=["https://cwe.mitre.org/data/definitions/798.html"],
            language_specificity="low",
            ai_explanation_priority="high"
        )
        
        assert meta.category == "secrets"
        assert meta.cwe_ids == ["CWE-798", "CWE-259"]
        assert meta.risk_factors == ["exposure", "hardcoded"]
        assert meta.detection_method == "regex"
        assert meta.false_positive_rate == 0.1
        assert meta.remediation_priority == "high"
        assert meta.tags == ["api-key", "aws"]
        assert meta.references == ["https://cwe.mitre.org/data/definitions/798.html"]
        assert meta.language_specificity == "low"
        assert meta.ai_explanation_priority == "high"
    
    def test_default_rule_meta(self):
        """Test create_default_rule_meta with minimal parameters."""
        meta = create_default_rule_meta(category="config")
        
        assert meta.category == "config"
        assert meta.cwe_ids is None
        assert meta.risk_factors is None
        assert meta.detection_method == "regex"
        assert meta.false_positive_rate == 0.1
        assert meta.remediation_priority == "medium"
        assert meta.tags == []
        assert meta.references == []
        assert meta.language_specificity == "low"
        assert meta.ai_explanation_priority == "medium"


if __name__ == "__main__":
    pytest.main([__file__])