"""
Utilities module for CodeSentinel.

Provides common utility functions and patterns used across the CodeSentinel codebase.
"""

from .entropy import calculate_entropy, is_high_entropy
from .patterns import compile_patterns, match_patterns

__all__ = ["calculate_entropy", "is_high_entropy", "compile_patterns", "match_patterns"]