"""
Entropy calculation utilities for CodeSentinel.

Provides Shannon entropy calculation for detecting high-entropy strings that
may indicate secrets or cryptographic material according to the Phase 1 specification.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import math
import re
from typing import Dict, Set


def shannon_entropy(data: str) -> float:
    """
    Calculate the Shannon entropy of a string.

    Shannon entropy measures the randomness or uncertainty in a string.
    Higher entropy values indicate more random data, which may suggest
    cryptographic keys, tokens, or other secrets.

    Args:
        data: Input string to analyze

    Returns:
        Entropy value between 0.0 (completely predictable) and ~8.0 (completely random for bytes)

    Example:
        >>> shannon_entropy("password")
        2.75
        >>> shannon_entropy("LKh7aM#s!@n3*2")
        3.25
    """
    if not data:
        return 0.0

    # Count frequency of each character
    frequency: Dict[str, int] = {}
    for char in data:
        frequency[char] = frequency.get(char, 0) + 1

    # Calculate entropy
    entropy = 0.0
    data_len = len(data)

    for count in frequency.values():
        probability = count / data_len
        entropy -= probability * math.log2(probability)

    return entropy


def is_high_entropy(data: str, threshold: float = 4.0) -> bool:
    """
    Determine if a string has high entropy based on a threshold.

    High entropy strings are more likely to be secrets, tokens, or cryptographic
    material rather than human-readable text or structured data.

    Args:
        data: String to evaluate
        threshold: Entropy threshold (default: 4.0)

    Returns:
        True if entropy exceeds threshold, False otherwise

    Example:
        >>> is_high_entropy("password")
        False
        >>> is_high_entropy("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        True
    """
    return shannon_entropy(data) > threshold


def is_likely_secret(data: str, min_length: int = 20, threshold: float = 4.0) -> bool:
    """
    Enhanced entropy-based secret detection with additional filtering.

    Combines entropy analysis with length requirements and character diversity
    checks to reduce false positives from generic high-entropy patterns.

    Args:
        data: String to evaluate
        min_length: Minimum string length requirement (default: 20)
        threshold: Entropy threshold (default: 4.0)

    Returns:
        True if string is likely to be a secret, False otherwise

    Example:
        >>> is_likely_secret("password1234567890")
        False
        >>> is_likely_secret("LKh7aM#s!@n3*2pQ9rT1vX5z8bD0")
        True
    """
    if len(data) < min_length:
        return False

    # Skip obvious non-secrets
    if _is_common_pattern(data):
        return False

    # Check character diversity requirements
    if not _has_sufficient_diversity(data):
        return False

    # Apply entropy threshold
    return is_high_entropy(data, threshold)


def _is_common_pattern(data: str) -> bool:
    """
    Check if string matches common non-secret patterns.

    Filters out UUIDs, common base64 padding patterns, repeated characters,
    and other patterns that are high entropy but typically not secrets.

    Args:
        data: String to check

    Returns:
        True if string matches common non-secret pattern, False otherwise
    """
    # UUID pattern (version 1-5)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    if re.match(uuid_pattern, data, re.IGNORECASE):
        return True

    # Common base64 padding patterns (often appear in encoded data)
    if data.endswith(('==', '=')) and len(data) % 4 == 0:
        # Check if it's just padding without meaningful content
        if data.count('=') > len(data) * 0.3:  # More than 30% padding
            return True

    # Repeated characters or simple patterns
    if (len(set(data)) < 8 or  # Too little character diversity
        data.isdigit() or       # All digits (likely numeric ID)
        data.isalpha() or       # All letters (likely word/name)
        data.count(data[0]) == len(data)):  # All same character
        return True

    # Common test/example patterns
    test_patterns = {
        'test', 'example', 'demo', 'sample', 'placeholder',
        'changeme', 'password', 'secret', 'key', 'token'
    }
    data_lower = data.lower()
    if any(pattern in data_lower for pattern in test_patterns):
        return True

    # Sequential patterns (123456, abcdef, etc.)
    if _is_sequential_pattern(data):
        return True

    return False


def _has_sufficient_diversity(data: str, min_unique_ratio: float = 0.4) -> bool:
    """
    Check if string has sufficient character diversity.

    Args:
        data: String to check
        min_unique_ratio: Minimum ratio of unique characters to total length

    Returns:
        True if diversity is sufficient, False otherwise
    """
    if len(data) < 10:
        return True  # Short strings can have lower diversity

    unique_chars = len(set(data))
    diversity_ratio = unique_chars / len(data)
    
    return diversity_ratio >= min_unique_ratio


def _is_sequential_pattern(data: str) -> bool:
    """
    Detect sequential patterns that are unlikely to be secrets.

    Args:
        data: String to check

    Returns:
        True if string contains sequential pattern, False otherwise
    """
    # Check for numeric sequences
    if data.isdigit():
        # Simple numeric sequence check
        for i in range(len(data) - 1):
            if abs(int(data[i]) - int(data[i + 1])) != 1:
                break
        else:
            return True  # All consecutive numbers

    # Check for alphabetical sequences (basic)
    if data.isalpha():
        data_lower = data.lower()
        for i in range(len(data_lower) - 1):
            if ord(data_lower[i + 1]) - ord(data_lower[i]) != 1:
                break
        else:
            return True  # All consecutive letters

    return False


def calculate_entropy_score(data: str) -> float:
    """
    Calculate normalized entropy score for confidence assessment.

    Returns a score between 0.0 and 1.0 where higher values indicate
    higher likelihood of being a secret.

    Args:
        data: String to evaluate

    Returns:
        Normalized entropy score (0.0 to 1.0)
    """
    if not data or len(data) < 10:
        return 0.0

    base_entropy = shannon_entropy(data)
    
    # Normalize by maximum possible entropy (log2 of character set size)
    char_set_size = len(set(data))
    max_possible_entropy = math.log2(char_set_size) if char_set_size > 0 else 0
    
    if max_possible_entropy == 0:
        return 0.0
    
    # Calculate normalized score
    normalized_entropy = base_entropy / max_possible_entropy
    
    # Apply length factor (longer strings get slight boost)
    length_factor = min(1.0, len(data) / 64.0)  # Cap at 64 chars
    
    final_score = normalized_entropy * 0.7 + length_factor * 0.3
    
    return min(final_score, 1.0)
