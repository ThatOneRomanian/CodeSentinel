"""
LLM module for CodeSentinel Phase 2 AI Explainer Mode.

Provides AI-powered security explanations, CWE mapping, and remediation guidance
without modifying the core scanning logic.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

from sentinel.llm.provider import LLMProvider, DeepSeekProvider, OpenAIProvider, LocalOllamaProvider
from sentinel.llm.explainer import ExplanationEngine
from sentinel.llm.safety import SafetyLayer, sanitize_input, filter_sensitive_data, truncate_excerpt, ensure_no_private_keys

__all__ = [
    "LLMProvider",
    "DeepSeekProvider", 
    "OpenAIProvider",
    "LocalOllamaProvider",
    "ExplanationEngine",
    "SafetyLayer",
    "sanitize_input",
    "filter_sensitive_data", 
    "truncate_excerpt",
    "ensure_no_private_keys",
]