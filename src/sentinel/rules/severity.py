"""
Severity mapping utilities for CodeSentinel.

Provides numeric severity mapping for enhanced reporting and prioritization
in Phase 2+ features.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

from typing import Dict, List, Optional
from sentinel.rules.token_types import TokenType, classify_token

SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}

# Provider-specific severity adjustments
PROVIDER_SEVERITY_ADJUSTMENTS = {
    # Cloud provider secrets - highest severity
    TokenType.AWS_ACCESS_KEY: 0.2,      # +20% for AWS access keys
    TokenType.AWS_SECRET_KEY: 0.3,      # +30% for AWS secret keys
    TokenType.GCP_SERVICE_ACCOUNT: 0.25, # +25% for GCP service accounts
    TokenType.AZURE_CLIENT_SECRET: 0.2,  # +20% for Azure client secrets
    
    # Payment provider secrets - high severity
    TokenType.STRIPE_API_KEY_LIVE: 0.25, # +25% for live Stripe keys
    TokenType.STRIPE_API_KEY_TEST: -0.3, # -30% for test Stripe keys
    
    # Authentication tokens - medium severity
    TokenType.JWT: 0.1,                 # +10% for JWTs
    TokenType.OAUTH_TOKEN: 0.05,        # +5% for generic OAuth
    TokenType.GCP_OAUTH_TOKEN: 0.1,     # +10% for GCP OAuth
    
    # Social/API tokens - variable severity
    TokenType.SLACK_BOT_TOKEN: 0.15,    # +15% for Slack bot tokens
    TokenType.SLACK_USER_TOKEN: 0.1,    # +10% for Slack user tokens
    TokenType.GITHUB_TOKEN: 0.2,        # +20% for GitHub tokens
    TokenType.FACEBOOK_ACCESS_TOKEN: 0.1, # +10% for Facebook tokens
    
    # Cryptographic materials - highest severity
    TokenType.PRIVATE_KEY: 0.3,         # +30% for private keys
    
    # Generic high entropy - base severity
    TokenType.GENERIC_HIGH_ENTROPY: 0.0, # No adjustment for generic
}

# Test vs production adjustments
TEST_PRODUCTION_ADJUSTMENTS = {
    "test": -0.4,      # -40% for test keys
    "live": 0.1,       # +10% for live keys
    "production": 0.15, # +15% for production keys
}

# Language-specific risk adjustments
LANGUAGE_RISK_ADJUSTMENTS = {
    "python": 0.05,    # +5% for Python (commonly used for sensitive operations)
    "javascript": 0.0, # No adjustment for JavaScript
    "typescript": 0.0, # No adjustment for TypeScript
    "java": 0.1,       # +10% for Java (enterprise applications)
    "go": 0.05,        # +5% for Go
    "rust": 0.0,       # No adjustment for Rust
    "php": 0.05,       # +5% for PHP
    "ruby": 0.05,      # +5% for Ruby
    "csharp": 0.1,     # +10% for C# (enterprise applications)
    "cpp": 0.05,       # +5% for C++
    "config": -0.1,    # -10% for config files (often contain test values)
    "unknown": 0.0,    # No adjustment for unknown languages
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


def calculate_enhanced_risk_score(
    base_severity: str,
    token_value: Optional[str] = None,
    tags: Optional[List[str]] = None,
    language: Optional[str] = None,
    confidence: float = 0.5
) -> float:
    """
    Calculate enhanced risk score accounting for provider-specific factors.
    
    Args:
        base_severity: Base severity level (critical, high, medium, low, info)
        token_value: The actual token value for classification
        tags: List of tags from the finding
        language: Programming language of the file
        confidence: Rule confidence score (0.0 to 1.0)
        
    Returns:
        Enhanced risk score between 1.0 and 10.0
    """
    # Base severity score mapping
    base_scores = {
        "critical": 8.5,
        "high": 7.0,
        "medium": 5.0,
        "low": 3.0,
        "info": 1.0
    }
    
    base_score = base_scores.get(base_severity.lower(), 5.0)
    
    # Apply token classification adjustments
    token_adjustment = 0.0
    if token_value:
        token_type = classify_token(token_value)
        if token_type:
            token_adjustment = PROVIDER_SEVERITY_ADJUSTMENTS.get(token_type, 0.0)
    
    # Apply test/production adjustments from tags
    test_prod_adjustment = 0.0
    if tags:
        for tag in tags:
            if tag in TEST_PRODUCTION_ADJUSTMENTS:
                test_prod_adjustment += TEST_PRODUCTION_ADJUSTMENTS[tag]
                break  # Use first matching tag
    
    # Apply language-specific adjustments
    language_adjustment = LANGUAGE_RISK_ADJUSTMENTS.get(language or "unknown", 0.0)
    
    # Apply confidence weighting
    confidence_factor = 0.5 + (confidence * 0.5)  # Maps 0.0->0.5, 1.0->1.0
    
    # Calculate final score with adjustments
    adjusted_score = base_score * (1 + token_adjustment + test_prod_adjustment + language_adjustment)
    final_score = adjusted_score * confidence_factor
    
    # Ensure score stays within bounds
    return max(1.0, min(10.0, final_score))


def get_provider_aware_severity(
    base_severity: str,
    token_value: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Adjust severity level based on provider context and test/production indicators.
    
    Args:
        base_severity: Original severity level
        token_value: Token value for provider classification
        tags: Finding tags for context
        
    Returns:
        Adjusted severity level
    """
    if not token_value and not tags:
        return base_severity
    
    severity_rank = severity_value(base_severity)
    if severity_rank == -1:
        return base_severity
    
    # Check for test indicators that should lower severity
    if tags:
        test_indicators = ["test", "staging", "development", "sandbox"]
        if any(indicator in tags for indicator in test_indicators):
            # Downgrade severity by one level for test environments
            if severity_rank > 1:  # Don't downgrade below low
                adjusted_rank = severity_rank - 1
                for level, rank in SEVERITY_RANK.items():
                    if rank == adjusted_rank:
                        return level
    
    # Check for production indicators that might increase severity
    if tags:
        prod_indicators = ["live", "production", "prod"]
        if any(indicator in tags for indicator in prod_indicators):
            # Upgrade severity by one level for production (if not already critical)
            if severity_rank < 4:  # Don't upgrade above critical
                adjusted_rank = severity_rank + 1
                for level, rank in SEVERITY_RANK.items():
                    if rank == adjusted_rank:
                        return level
    
    return base_severity


def get_token_type_risk_context(token_value: Optional[str]) -> Dict[str, str]:
    """
    Get risk context information for a token type.
    
    Args:
        token_value: Token value to classify
        
    Returns:
        Dictionary with risk context information
    """
    if not token_value:
        return {"type": "unknown", "risk_level": "medium"}
    
    token_type = classify_token(token_value)
    if not token_type:
        return {"type": "generic", "risk_level": "medium"}
    
    # Map token types to risk levels
    risk_levels = {
        TokenType.AWS_ACCESS_KEY: "high",
        TokenType.AWS_SECRET_KEY: "critical",
        TokenType.GCP_SERVICE_ACCOUNT: "critical",
        TokenType.AZURE_CLIENT_SECRET: "high",
        TokenType.STRIPE_API_KEY_LIVE: "high",
        TokenType.STRIPE_API_KEY_TEST: "low",
        TokenType.JWT: "medium",
        TokenType.OAUTH_TOKEN: "medium",
        TokenType.GCP_OAUTH_TOKEN: "medium",
        TokenType.SLACK_BOT_TOKEN: "medium",
        TokenType.SLACK_USER_TOKEN: "medium",
        TokenType.GITHUB_TOKEN: "high",
        TokenType.FACEBOOK_ACCESS_TOKEN: "medium",
        TokenType.PRIVATE_KEY: "critical",
        TokenType.GENERIC_HIGH_ENTROPY: "medium",
    }
    
    return {
        "type": token_type.value,
        "risk_level": risk_levels.get(token_type, "medium")
    }