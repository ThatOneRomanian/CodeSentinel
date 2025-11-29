"""
Entropy calculation utilities for CodeSentinel.

Provides Shannon entropy calculation for detecting high-entropy strings that
may indicate secrets or cryptographic material according to the Phase 1 specification.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import math
from typing import Dict


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
