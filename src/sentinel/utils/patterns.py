"""
Pattern matching utilities for CodeSentinel.

Provides functions for compiling and matching regex patterns for security scanning.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Pattern
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class PatternMatch:
    """Represents a pattern match result."""

    pattern_id: str
    matched_text: str
    start_pos: int
    end_pos: int
    line_number: int
    confidence: float = 1.0


def compile_patterns(pattern_definitions: Dict[str, str]) -> Dict[str, Pattern]:
    """
    Compile regex patterns for efficient matching.

    Args:
        pattern_definitions: Dictionary mapping pattern IDs to regex strings

    Returns:
        Dictionary mapping pattern IDs to compiled regex patterns
    """
    compiled_patterns = {}
    for pattern_id, regex in pattern_definitions.items():
        try:
            compiled_patterns[pattern_id] = re.compile(regex, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            logger.warning(f"Failed to compile pattern {pattern_id}: {e}")
    return compiled_patterns


def match_patterns(
    content: str,
    compiled_patterns: Dict[str, Pattern],
    context_lines: int = 2
) -> List[PatternMatch]:
    """
    Match multiple patterns against content and return matches with context.

    Args:
        content: Text content to scan
        compiled_patterns: Dictionary of compiled regex patterns
        context_lines: Number of lines to include around matches for context

    Returns:
        List of PatternMatch objects for all matches found
    """
    matches = []

    for pattern_id, pattern in compiled_patterns.items():
        pattern_matches = pattern.finditer(content)
        for match in pattern_matches:
            # Calculate line number
            line_number = content[:match.start()].count('\n') + 1

            # Extract context around the match
            start_pos = max(0, match.start() - 100)  # 100 chars before
            end_pos = min(len(content), match.end() + 100)  # 100 chars after
            matched_text = content[start_pos:end_pos]

            matches.append(PatternMatch(
                pattern_id=pattern_id,
                matched_text=matched_text,
                start_pos=match.start(),
                end_pos=match.end(),
                line_number=line_number
            ))

    return matches


def validate_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a regex pattern for correctness.

    Args:
        pattern: Regex pattern string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        re.compile(pattern)
        return True, None
    except re.error as e:
        return False, str(e)


def extract_context_lines(content: str, position: int, lines_before: int = 2, lines_after: int = 2) -> str:
    """
    Extract context lines around a specific position in content.

    Args:
        content: Full text content
        position: Character position in content
        lines_before: Number of lines to include before the match
        lines_after: Number of lines to include after the match

    Returns:
        String containing the context lines around the position
    """
    lines = content.split('\n')
    current_line = 0
    char_count = 0

    # Find the line containing the position
    for i, line in enumerate(lines):
        if char_count <= position < char_count + len(line) + 1:  # +1 for newline
            current_line = i
            break
        char_count += len(line) + 1

    # Extract context lines
    start_line = max(0, current_line - lines_before)
    end_line = min(len(lines), current_line + lines_after + 1)

    context_lines = lines[start_line:end_line]
    return '\n'.join(context_lines)


def create_secret_patterns() -> Dict[str, str]:
    """
    Create common secret detection patterns.

    Returns:
        Dictionary of pattern IDs to regex strings for secret detection
    """
    return {
        "AWS_ACCESS_KEY": r"AKIA[0-9A-Z]{16}",
        "AWS_SECRET_KEY": r"[0-9a-zA-Z/+]{40}",
        "GCP_API_KEY": r"AIza[0-9A-Za-z\\-_]{35}",
        "STRIPE_API_KEY": r"(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}",
        "JWT_TOKEN": r"eyJ[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.?[A-Za-z0-9-_.+/=]*",
        "PRIVATE_KEY": r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
        "BASIC_AUTH": r"https?://[^:]+:[^@]+@",
        "EMAIL_PASSWORD": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}:[^\\s]+",
    }


def create_config_patterns() -> Dict[str, str]:
    """
    Create common configuration vulnerability patterns.

    Returns:
        Dictionary of pattern IDs to regex strings for config vulnerabilities
    """
    return {
        "DEBUG_ENABLED": r"DEBUG\\s*=\\s*True",
        "BIND_ALL_INTERFACES": r"0\\.0\\.0\\.0",
        "WEAK_CRYPTO": r"(md5|sha1)",
        "DEFAULT_CREDENTIALS": r"(admin:admin|root:root|user:user)",
        "HARDCODED_SECRETS": r"(secret|password|key)\\s*=\\s*['\"][^'\"]+['\"]",
        "INSECURE_TLS": r"verify\\s*=\\s*False",
    }
