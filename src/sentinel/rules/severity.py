"""
Severity mapping utilities for CodeSentinel.

Provides numeric severity mapping for enhanced reporting and prioritization
in Phase 2+ features.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}


def severity_value(level: str) -> int:
    """
    Convert a severity level string to its numeric value.

    Args:
        level: Severity level as string (e.g., 'high', 'medium', 'low')

    Returns:
        Numeric severity value (4 for critical, 3 for high, etc.)
        Returns -1 for unknown severity levels or None input

    Examples:
        >>> severity_value('high')
        3
        >>> severity_value('unknown')
        -1
        >>> severity_value(None)
        -1
        >>> severity_value(" critical ")
        4
    """
    if level is None:
        return -1
    
    # Handle whitespace by stripping and converting to lowercase
    normalized_level = level.strip().lower() if isinstance(level, str) else str(level)
    
    return SEVERITY_RANK.get(normalized_level, -1)