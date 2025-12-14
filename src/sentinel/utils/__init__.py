from .parsers import (
    parse_json, 
    parse_dockerfile, 
    get_yaml_key_value, 
    find_hcl_blocks
)
"""
Utility module for CodeSentinel.

Contains helper functions and utilities for security scanning operations.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
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
