"""
Scanner module for CodeSentinel.

Contains file system walking and rule engine components for security scanning.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

from sentinel.scanner.engine import run_rules, RuleLoader
from sentinel.scanner.walker import walk_directory, validate_target_path

__all__ = ["run_rules", "RuleLoader", "walk_directory", "validate_target_path"]
