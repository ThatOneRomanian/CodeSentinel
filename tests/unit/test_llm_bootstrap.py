"""
Unit tests for CodeSentinel Phase 2 LLM bootstrap components.

Tests the LLM provider interface, explanation engine, and CLI integration
without actual LLM integration during the bootstrap phase.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pytest
import pathlib
from unittest.mock import Mock, patch

from sentinel.rules.base import Finding
from sentinel.llm.provider import (
    LLMProvider, 
    DeepSeekProvider, 
    OpenAIProvider, 
    LocalOllamaProvider,
    get_provider
)
from sentinel.llm.explainer import ExplanationEngine


class TestLLMProvider:
    """Test LLM provider interface and implementations."""
    
    def test_llm_provider_abstract_class(self):
        """Test that LLMProvider is an abstract base class."""
        with pytest.raises(TypeError):
            LLMProvider()  # Cannot instantiate abstract class
    
    def test_deepseek_provider_generate(self):
        """Test DeepSeekProvider generates placeholder response."""
        provider = DeepSeekProvider()
        result = provider.generate("test prompt")
        
        assert isinstance(result, str)
        assert "DeepSeek" in result
        assert "placeholder" in result
    
    def test_openai_provider_generate(self):
        """Test OpenAIProvider generates placeholder response."""
        provider = OpenAIProvider()
        result = provider.generate("test prompt")
        
        assert isinstance(result, str)
        assert "OpenAI" in result
        assert "placeholder" in result
    
    def test_local_ollama_provider_generate(self):
        """Test LocalOllamaProvider generates placeholder response."""
        provider = LocalOllamaProvider()
        result = provider.generate("test prompt")
        
        assert isinstance(result, str)
        assert "LocalOllama" in result
        assert "placeholder" in result
    
    def test_get_provider_valid_names(self):
        """Test get_provider returns correct provider instances."""
        providers = {
            "deepseek": DeepSeekProvider,
            "openai": OpenAIProvider,
            "local_ollama": LocalOllamaProvider,
        }
        
        for name, provider_class in providers.items():
            provider = get_provider(name)
            assert isinstance(provider, provider_class)
    
    def test_get_provider_invalid_name(self):
        """Test get_provider raises ValueError for unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("invalid_provider")


class TestExplanationEngine:
    """Test Explanation Engine functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ExplanationEngine()
        self.test_finding = Finding(
            rule_id="test-rule",
            file_path=pathlib.Path("test.py"),
            line=42,
            severity="high",
            excerpt="test_api_key = 'sk_test_1234567890'",
            confidence=0.8,
            language="python"
        )
        self.mock_provider = Mock(spec=LLMProvider)
        self.mock_provider.generate.return_value = "Mocked LLM response"
    
    def test_explanation_engine_initialization(self):
        """Test ExplanationEngine initializes with default prompts directory."""
        engine = ExplanationEngine()
        assert engine.prompts_dir.exists()
        assert engine.prompts_dir.name == "prompts"
    
    def test_explanation_engine_custom_prompts_dir(self):
        """Test ExplanationEngine with custom prompts directory."""
        custom_dir = pathlib.Path("/tmp/custom_prompts")
        engine = ExplanationEngine(prompts_dir=custom_dir)
        assert engine.prompts_dir == custom_dir
    
    def test_explain_finding_returns_dict(self):
        """Test explain_finding returns expected dictionary structure."""
        result = self.engine.explain_finding(self.test_finding, self.mock_provider)
        
        assert isinstance(result, dict)
        assert "explanation" in result
        assert "cwe_id" in result
        assert "remediation" in result
        assert "risk_score" in result
        assert "references" in result
        
        # Check types
        assert isinstance(result["explanation"], str)
        assert result["cwe_id"] is None or isinstance(result["cwe_id"], str)
        assert isinstance(result["remediation"], str)
        assert result["risk_score"] is None or isinstance(result["risk_score"], (int, float))
        assert isinstance(result["references"], list)
    
    def test_explain_finding_placeholder_content(self):
        """Test explain_finding returns placeholder content during bootstrap."""
        result = self.engine.explain_finding(self.test_finding, self.mock_provider)
        
        # Updated to match current placeholder format
        assert "placeholder" in result["explanation"].lower()
        assert "placeholder" in result["remediation"].lower()
    
    def test_populate_template_with_finding(self):
        """Test template population with finding data."""
        template = "Rule: {{rule_id}}, File: {{file_path}}, Line: {{line}}, Excerpt: {{excerpt}}, Language: {{language}}"
        result = self.engine._populate_template(template, self.test_finding)
        
        assert "test-rule" in result
        assert "test.py" in result
        assert "42" in result
        assert "test_api_key" in result
        assert "python" in result
    
    def test_populate_template_with_none_excerpt(self):
        """Test template population handles None excerpt."""
        finding = Finding(
            rule_id="test-rule",
            file_path=pathlib.Path("test.py"),
            line=42,
            severity="high",
            excerpt=None,
            confidence=0.8
        )
        template = "Excerpt: {{excerpt}}"
        result = self.engine._populate_template(template, finding)
        
        assert "No excerpt available" in result
    
    def test_load_prompt_template_success(self):
        """Test loading existing prompt template."""
        # Create a temporary template file for testing
        test_template_dir = pathlib.Path("/tmp/test_prompts")
        test_template_dir.mkdir(exist_ok=True)
        test_template_file = test_template_dir / "test_template.txt"
        test_template_file.write_text("Test template content")
        
        engine = ExplanationEngine(prompts_dir=test_template_dir)
        content = engine._load_prompt_template("test_template")
        
        assert content == "Test template content"
        
        # Cleanup
        test_template_file.unlink()
        test_template_dir.rmdir()
    
    def test_load_prompt_template_not_found(self):
        """Test loading non-existent prompt template raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.engine._load_prompt_template("non_existent_template")


class TestCLIIntegration:
    """Test CLI integration for Phase 2 flags."""
    
    def test_cli_accepts_ai_flag(self):
        """Test CLI parser accepts --ai flag."""
        from sentinel.cli.main import create_parser
        
        parser = create_parser()
        args = parser.parse_args(["scan", "test_path", "--ai"])
        
        assert args.ai is True
        assert args.command == "scan"
        assert args.target == "test_path"
    
    def test_cli_accepts_explain_flag(self):
        """Test CLI parser accepts --explain flag."""
        from sentinel.cli.main import create_parser
        
        parser = create_parser()
        args = parser.parse_args(["scan", "test_path", "--explain"])
        
        assert args.explain is True
        assert args.command == "scan"
    
    def test_cli_accepts_llm_provider_flag(self):
        """Test CLI parser accepts --llm-provider flag."""
        from sentinel.cli.main import create_parser
        
        parser = create_parser()
        args = parser.parse_args(["scan", "test_path", "--llm-provider", "openai"])
        
        assert args.llm_provider == "openai"
        assert args.command == "scan"
    
    def test_cli_llm_provider_default(self):
        """Test CLI parser uses deepseek as default LLM provider."""
        from sentinel.cli.main import create_parser
        
        parser = create_parser()
        args = parser.parse_args(["scan", "test_path"])
        
        assert args.llm_provider == "deepseek"  # Default value


def test_imports_work():
    """Test that all Phase 2 modules can be imported successfully."""
    # This test will fail if there are import issues
    from sentinel.llm import (
        LLMProvider,
        DeepSeekProvider,
        OpenAIProvider, 
        LocalOllamaProvider,
        ExplanationEngine
    )
    
    # Just verify the imports work
    assert LLMProvider is not None
    assert DeepSeekProvider is not None
    assert OpenAIProvider is not None
    assert LocalOllamaProvider is not None
    assert ExplanationEngine is not None