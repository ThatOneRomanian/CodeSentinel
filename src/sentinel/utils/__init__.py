"""
Utility module for CodeSentinel.

Contains helper functions and utilities for security scanning operations.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

from sentinel.utils.entropy import shannon_entropy, is_high_entropy
from sentinel.utils.patterns import (
    compile_patterns,
    match_patterns,
    validate_pattern,
    create_secret_patterns,
    create_config_patterns
)

__all__ = [
    "shannon_entropy",
    "is_high_entropy",
    "compile_patterns",
    "match_patterns",
    "validate_pattern",
    "create_secret_patterns",
    "create_config_patterns"
]
