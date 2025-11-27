"""
Entropy calculation utilities for CodeSentinel.

Provides functions for calculating Shannon entropy of strings to detect
potential secrets and high-entropy data that may be sensitive.
"""

import math
from typing import Optional


def calculate_entropy(data: str) -> float:
    """
    Calculate the Shannon entropy of a string.

    Entropy is a measure of randomness in data. Higher entropy values
    indicate more random data, which can be indicative of secrets, tokens,
    or other sensitive information.

    Args:
        data: Input string to calculate entropy for

    Returns:
        Entropy value (bits per character)
    """
    if not data:
        return 0.0

    # Count frequency of each character
    freq_dict = {}
    for char in data:
        freq_dict[char] = freq_dict.get(char, 0) + 1

    # Calculate entropy
    entropy = 0.0
    data_len = len(data)
    for count in freq_dict.values():
        p_x = count / data_len
        entropy += -p_x * math.log2(p_x)

    return entropy


def is_high_entropy(data: str, threshold: float = 4.5, min_length: int = 20) -> bool:
    """
    Determine if a string has high entropy, potentially indicating a secret.

    High entropy strings are more likely to be cryptographic keys, tokens,
    or other sensitive data rather than natural language or structured data.

    Args:
        data: Input string to check
        threshold: Entropy threshold (default: 4.5 bits per character)
        min_length: Minimum string length to consider (default: 20)

    Returns:
        True if string has high entropy, False otherwise
    """
    if len(data) < min_length:
        return False

    entropy = calculate_entropy(data)
    return entropy >= threshold


def analyze_string_entropy(data: str) -> dict:
    """
    Perform comprehensive entropy analysis on a string.

    Args:
        data: Input string to analyze

    Returns:
        Dictionary containing entropy analysis results
    """
    entropy = calculate_entropy(data)
    high_entropy = is_high_entropy(data)

    return {
        "entropy": entropy,
        "is_high_entropy": high_entropy,
        "length": len(data),
        "unique_chars": len(set(data)),
        "threshold_met": entropy >= 4.5,
    }