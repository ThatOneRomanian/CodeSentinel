"""
AI Safety Layer for CodeSentinel Phase 2.

Provides security and privacy protections for AI explanations, including
input sanitization, data filtering, and content safety controls.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import re
from typing import Optional, Set


def sanitize_input(content: str) -> str:
    """
    Sanitize input content to prevent prompt injection and malicious input.
    
    Args:
        content: Raw input content to sanitize
        
    Returns:
        Sanitized content with potentially dangerous patterns removed
    """
    if not content:
        return ""
    
    # Remove or escape potentially dangerous patterns
    sanitized = content
    
    # Remove common prompt injection attempts
    injection_patterns = [
        r'ignore.*previous.*instructions',
        r'disregard.*previous',
        r'you are now',
        r'act as',
        r'pretend you are',
        r'forget.*rules',
        r'break.*rules',
        r'override.*system',
        r'system.*override',
        r'bypass.*safety',
        r'security.*bypass',
    ]
    
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Remove excessive whitespace that might be used for obfuscation
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Remove control characters except basic whitespace
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    # Limit maximum length as additional safety measure
    sanitized = truncate_excerpt(sanitized, max_chars=2000)
    
    return sanitized.strip()


def truncate_excerpt(excerpt: str, max_chars: int = 500) -> str:
    """
    Truncate code excerpt to safe length for AI processing.
    
    Args:
        excerpt: Code excerpt to truncate
        max_chars: Maximum allowed characters (default: 500)
        
    Returns:
        Truncated excerpt with ellipsis if necessary
    """
    if not excerpt:
        return ""
    
    if len(excerpt) <= max_chars:
        return excerpt
    
    # Truncate and add ellipsis, trying to break at a word boundary
    # Ensure total length doesn't exceed max_chars including ellipsis
    max_content_chars = max_chars - 3  # Reserve 3 chars for "..."
    truncated = excerpt[:max_content_chars]
    
    # Find the last space to break at word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_content_chars * 0.8:  # Only if we have a reasonable break point
        truncated = truncated[:last_space]
    
    return truncated + "..."


def filter_sensitive_data(content: str) -> str:
    """
    Filter out potentially sensitive data from content before sending to AI.
    
    Args:
        content: Content that may contain sensitive data
        
    Returns:
        Content with sensitive patterns redacted
    """
    if not content:
        return ""
    
    filtered = content
    
    # Common sensitive data patterns
    sensitive_patterns = {
        # API keys and tokens (generic patterns)
        r'\b[A-Za-z0-9]{32,64}\b': '[REDACTED_API_KEY]',
        r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b': '[REDACTED_UUID]',
        r'\bgh[ops]_[A-Za-z0-9_]{36,255}\b': '[REDACTED_GITHUB_TOKEN]',
        r'\bAKIA[0-9A-Z]{16}\b': '[REDACTED_AWS_KEY]',
        r'\bsk-[A-Za-z0-9]{20,}\b': '[REDACTED_OPENAI_KEY]',
        
        # Email addresses
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[REDACTED_EMAIL]',
        
        # IP addresses
        r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b': '[REDACTED_IP]',
        
        # URLs with sensitive parameters
        r'https?://[^\s]*(?:token|key|password|secret)=[^&\s]+': '[REDACTED_SENSITIVE_URL]',
    }
    
    for pattern, replacement in sensitive_patterns.items():
        filtered = re.sub(pattern, replacement, filtered)
    
    return filtered


def ensure_no_private_keys() -> bool:
    """
    Ensure no private keys are present in the environment or configuration.
    
    Returns:
        True if no private keys detected, False otherwise
    """
    # Check for common private key environment variables
    private_key_vars = {
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'DEEPSEEK_API_KEY',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'GITHUB_TOKEN',
        'SLACK_TOKEN',
        'DISCORD_TOKEN',
    }
    
    import os
    
    for var in private_key_vars:
        if os.getenv(var):
            return False
    
    return True


class SafetyLayer:
    """
    Comprehensive safety layer for AI operations.
    
    Provides coordinated safety controls for input sanitization,
    data filtering, and security checks.
    """
    
    def __init__(self, max_excerpt_length: int = 500, enable_filtering: bool = True):
        """
        Initialize the safety layer.
        
        Args:
            max_excerpt_length: Maximum allowed excerpt length
            enable_filtering: Whether to enable sensitive data filtering
        """
        self.max_excerpt_length = max_excerpt_length
        self.enable_filtering = enable_filtering
    
    def process_for_ai(self, content: str) -> str:
        """
        Process content for safe AI consumption.
        
        Args:
            content: Raw content to process
            
        Returns:
            Safe, sanitized content ready for AI processing
        """
        if not content:
            return ""
        
        # Apply safety transformations in sequence
        processed = content
        
        # 1. Sanitize input for security
        processed = sanitize_input(processed)
        
        # 2. Filter sensitive data if enabled
        if self.enable_filtering:
            processed = filter_sensitive_data(processed)
        
        # 3. Truncate to safe length
        processed = truncate_excerpt(processed, self.max_excerpt_length)
        
        return processed
    
    def validate_environment(self) -> bool:
        """
        Validate that the environment is safe for AI operations.
        
        Returns:
            True if environment is safe, False otherwise
        """
        return ensure_no_private_keys()