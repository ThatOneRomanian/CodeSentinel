"""
Scanner module for CodeSentinel.

Contains file system walking and rule engine components for security scanning.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

from sentinel.scanner.engine import run_rules, RuleLoader
from sentinel.scanner.walker import walk_directory, validate_target_path

__all__ = ["run_rules", "RuleLoader", "walk_directory", "validate_target_path"]
