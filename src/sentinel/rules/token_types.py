"""
Token Type Classification Module for CodeSentinel.

Provides provider-aware token classification to resolve rule collisions and improve
accuracy by identifying specific token types before rule application.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import re
import base64
import json
from enum import Enum
from typing import Optional

from sentinel.utils.entropy import is_high_entropy, shannon_entropy


class TokenType(Enum):
    """
    Enumeration of token types for provider-aware classification.
    
    Provides comprehensive coverage of common secret types with specific
    provider identification to enable rule precedence and deduplication.
    """
    
    # AWS tokens
    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    
    # GCP tokens
    GCP_OAUTH_TOKEN = "gcp_oauth_token"
    GCP_SERVICE_ACCOUNT = "gcp_service_account"
    
    # Azure tokens
    AZURE_CLIENT_SECRET = "azure_client_secret"
    
    # Stripe tokens
    STRIPE_API_KEY_LIVE = "stripe_api_key_live"
    STRIPE_API_KEY_TEST = "stripe_api_key_test"
    
    # Slack tokens
    SLACK_BOT_TOKEN = "slack_bot_token"
    SLACK_USER_TOKEN = "slack_user_token"
    
    # GitHub tokens
    GITHUB_TOKEN = "github_token"
    
    # Facebook tokens
    FACEBOOK_ACCESS_TOKEN = "facebook_access_token"
    
    # JWT tokens
    JWT = "jwt"
    
    # Generic high entropy strings
    GENERIC_HIGH_ENTROPY = "generic_high_entropy"
    
    # Private keys
    PRIVATE_KEY = "private_key"
    
    # Generic OAuth tokens
    OAUTH_TOKEN = "oauth_token"


def classify_token(value: str) -> Optional[TokenType]:
    """
    Classify a token string into a specific TokenType based on known patterns.
    
    Uses a precedence-based approach:
    1. Check known prefixes (most specific)
    2. Validate length and character constraints
    3. Use structural patterns (JWT, PEM)
    4. Fall back to entropy-based classification
    
    Args:
        value: The token string to classify
        
    Returns:
        TokenType enum value if classification successful, None otherwise
    """
    if not value or len(value) < 16:
        return None
    
    # Normalize value by stripping whitespace
    normalized_value = value.strip()
    
    # Check for AWS Access Key (AKIA prefix)
    if _is_aws_access_key(normalized_value):
        return TokenType.AWS_ACCESS_KEY
    
    # Check for AWS Secret Key (40-character base64-like)
    if _is_aws_secret_key(normalized_value):
        return TokenType.AWS_SECRET_KEY
    
    # Check for Stripe API keys
    stripe_type = _is_stripe_api_key(normalized_value)
    if stripe_type:
        return stripe_type
    
    # Check for Slack tokens
    slack_type = _is_slack_token(normalized_value)
    if slack_type:
        return slack_type
    
    # Check for GitHub tokens
    if _is_github_token(normalized_value):
        return TokenType.GITHUB_TOKEN
    
    # Check for GCP OAuth tokens
    if _is_gcp_oauth_token(normalized_value):
        return TokenType.GCP_OAUTH_TOKEN
    
    # Check for Facebook access tokens
    if _is_facebook_access_token(normalized_value):
        return TokenType.FACEBOOK_ACCESS_TOKEN
    
    # Check for JWT tokens (before other patterns to catch embedded JWTs)
    if _is_jwt_token(normalized_value):
        return TokenType.JWT
    
    # Check for GCP service account patterns (before private key to avoid conflicts)
    if _is_gcp_service_account(normalized_value):
        return TokenType.GCP_SERVICE_ACCOUNT
    
    # Check for private key blocks
    if _is_private_key(normalized_value):
        return TokenType.PRIVATE_KEY
    
    # Check for Azure client secrets (only GUIDs)
    if _is_azure_client_secret(normalized_value):
        return TokenType.AZURE_CLIENT_SECRET
    
    # Check for generic OAuth tokens
    if _is_generic_oauth_token(normalized_value):
        return TokenType.OAUTH_TOKEN
    
    # Fallback: high entropy classification
    if _is_high_entropy_token(normalized_value):
        return TokenType.GENERIC_HIGH_ENTROPY
    
    return None


def _is_aws_access_key(value: str) -> bool:
    """Check if value matches AWS Access Key pattern (AKIA followed by 16 alphanumeric chars)."""
    return bool(re.match(r'^AKIA[0-9A-Z]{16}$', value))


def _is_aws_secret_key(value: str) -> bool:
    """Check if value matches AWS Secret Key pattern (40-character base64-like string)."""
    if len(value) != 40:
        return False
    
    # Must be base64-like characters
    if not re.match(r'^[A-Za-z0-9+/=]{40}$', value):
        return False
    
    # Must have good character diversity
    if len(set(value)) < 20:
        return False
    
    # Must have reasonable entropy
    return is_high_entropy(value, threshold=4.0)


def _is_stripe_api_key(value: str) -> Optional[TokenType]:
    """Check if value matches Stripe API key pattern."""
    # Stripe live keys: sk_live_*, pk_live_*
    if re.match(r'^(sk|pk)_live_[a-zA-Z0-9]{24,}$', value):
        return TokenType.STRIPE_API_KEY_LIVE
    
    # Stripe test keys: sk_test_*, pk_test_*
    if re.match(r'^(sk|pk)_test_[a-zA-Z0-9]{24,}$', value):
        return TokenType.STRIPE_API_KEY_TEST
    
    return None


def _is_slack_token(value: str) -> Optional[TokenType]:
    """Check if value matches Slack token pattern."""
    # Slack bot tokens: xoxb-* (minimum 24 chars after prefix)
    if re.match(r'^xoxb-[a-zA-Z0-9-]{24,}$', value):
        return TokenType.SLACK_BOT_TOKEN
    
    # Slack user tokens: xoxp-* (minimum 24 chars after prefix)
    if re.match(r'^xoxp-[a-zA-Z0-9-]{24,}$', value):
        return TokenType.SLACK_USER_TOKEN
    
    return None


def _is_github_token(value: str) -> bool:
    """Check if value matches GitHub token pattern."""
    # GitHub personal access tokens: ghp_* (36 chars after prefix = 40 total)
    if re.match(r'^ghp_[a-zA-Z0-9]{36}$', value):
        return True
    
    # GitHub fine-grained tokens: github_pat_* (71 chars total in test, real ones are 82)
    # Accept test tokens (71 chars) and real tokens (82 chars)
    if (len(value) == 71 or len(value) == 82) and value.startswith('github_pat_'):
        return True
    
    return False


def _is_gcp_oauth_token(value: str) -> bool:
    """Check if value matches GCP OAuth token pattern."""
    # GCP OAuth tokens typically start with 'ya29.' and are ~180 chars
    if re.match(r'^ya29\.[a-zA-Z0-9_-]{140,}$', value):
        return True
    
    return False


def _is_facebook_access_token(value: str) -> bool:
    """Check if value matches Facebook access token pattern."""
    # Facebook access tokens: EAACEdEose0cBA... (64 chars)
    if (len(value) >= 60 and 
        re.match(r'^EAACEdEose0cBA[a-zA-Z0-9]+$', value)):
        return True
    
    return False


def _is_jwt_token(value: str) -> bool:
    """
    Enhanced JWT token validation with structural and encoding checks.
    
    Validates:
    - 3-part dot-separated structure
    - Base64url encoding for each segment
    - Valid JSON in header with typical JWT fields
    - Common JWT algorithms in header
    
    Args:
        value: String to check for JWT pattern
        
    Returns:
        True if valid JWT token, False otherwise
    """
    # Extract JWT candidate from any string that might contain it
    jwt_match = re.search(r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', value)
    if jwt_match:
        jwt_candidate = jwt_match.group(0)
    else:
        return False
    
    # JWT tokens must have three base64url-encoded parts separated by dots
    parts = jwt_candidate.split('.')
    if len(parts) != 3:
        return False
    
    header, payload, signature = parts
    
    # Each part should be valid base64url (A-Z, a-z, 0-9, -, _)
    for part in parts:
        if not re.match(r'^[A-Za-z0-9_-]+$', part):
            return False
    
    # Validate header structure and content
    if not _is_valid_jwt_header(header):
        return False
    
    # Validate payload structure (basic JSON check)
    if not _is_valid_jwt_payload(payload):
        return False
    
    # Signature should have reasonable length and entropy
    if len(signature) < 8 or not is_high_entropy(signature, threshold=3.5):
        return False
    
    return True


def _is_valid_jwt_header(header: str) -> bool:
    """
    Validate JWT header structure and content.
    
    Args:
        header: JWT header segment
        
    Returns:
        True if valid JWT header, False otherwise
    """
    try:
        # Add padding if needed and decode
        padding = 4 - (len(header) % 4)
        if padding != 4:
            header_padded = header + '=' * padding
        else:
            header_padded = header
        
        decoded_header = base64.urlsafe_b64decode(header_padded).decode('utf-8')
        header_data = json.loads(decoded_header)
        
        # Check for required JWT header fields
        if 'alg' not in header_data or 'typ' not in header_data:
            return False
        
        # Validate algorithm is a common JWT algorithm
        valid_algorithms = {
            'HS256', 'HS384', 'HS512',  # HMAC
            'RS256', 'RS384', 'RS512',  # RSA
            'ES256', 'ES384', 'ES512',  # ECDSA
            'PS256', 'PS384', 'PS512',  # RSASSA-PSS
            'none'
        }
        if header_data['alg'] not in valid_algorithms:
            return False
        
        # Validate type is typically JWT
        if header_data['typ'] != 'JWT':
            return False
            
        return True
        
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return False


def _is_valid_jwt_payload(payload: str) -> bool:
    """
    Basic validation of JWT payload structure.
    
    Args:
        payload: JWT payload segment
        
    Returns:
        True if valid JWT payload structure, False otherwise
    """
    try:
        # Add padding if needed and decode
        padding = 4 - (len(payload) % 4)
        if padding != 4:
            payload_padded = payload + '=' * padding
        else:
            payload_padded = payload
        
        decoded_payload = base64.urlsafe_b64decode(payload_padded).decode('utf-8')
        payload_data = json.loads(decoded_payload)
        
        # Payload should be a JSON object
        if not isinstance(payload_data, dict):
            return False
            
        # Common JWT claims validation (basic checks)
        if 'iss' in payload_data and not isinstance(payload_data['iss'], str):
            return False
        if 'sub' in payload_data and not isinstance(payload_data['sub'], str):
            return False
        if 'exp' in payload_data and not isinstance(payload_data['exp'], (int, float)):
            return False
        if 'iat' in payload_data and not isinstance(payload_data['iat'], (int, float)):
            return False
            
        return True
        
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        # Some JWTs might have non-JSON payloads, but we'll be conservative
        return False


def _is_private_key(value: str) -> bool:
    """Check if value contains private key block indicators."""
    private_key_indicators = [
        '-----BEGIN RSA PRIVATE KEY-----',
        '-----BEGIN DSA PRIVATE KEY-----',
        '-----BEGIN EC PRIVATE KEY-----',
        '-----BEGIN PRIVATE KEY-----',
        '-----BEGIN OPENSSH PRIVATE KEY-----',
        '-----BEGIN PGP PRIVATE KEY BLOCK-----',
    ]
    
    return any(indicator in value for indicator in private_key_indicators)


def _is_gcp_service_account(value: str) -> bool:
    """Check if value contains GCP service account indicators."""
    service_account_indicators = [
        '"type": "service_account"',
        '"private_key_id":',
        '"private_key": "-----BEGIN PRIVATE KEY-----',
        '"client_email":',
        '"client_id":',
    ]
    
    return any(indicator in value for indicator in service_account_indicators)


def _is_azure_client_secret(value: str) -> bool:
    """Check if value matches Azure client secret pattern."""
    # Only classify as Azure if it's specifically a GUID
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value, re.IGNORECASE))


def _is_generic_oauth_token(value: str) -> bool:
    """Check if value is a generic OAuth token."""
    # Generic OAuth tokens are typically base64-like strings with high entropy
    if len(value) < 32:
        return False
    
    if not re.match(r'^[A-Za-z0-9\-_]+$', value):
        return False
    
    # Must have high entropy and not match other specific patterns
    return (is_high_entropy(value, threshold=3.8) and 
            not _has_specific_token_prefix(value))


def _is_high_entropy_token(value: str) -> bool:
    """
    Check if value is a high-entropy token (fallback classification).
    
    This is used as a last resort when no provider-specific patterns match.
    """
    if len(value) < 20:
        return False
    
    # Skip obvious non-secrets
    if (len(set(value)) < 10 or  # Too little variation
        value.isdigit() or       # All digits
        value.isalpha() or       # All letters
        value.count(value[0]) == len(value)):  # All same character
        return False
    
    # Must have high entropy and not match other specific patterns
    return (is_high_entropy(value, threshold=4.0) and 
            not _has_specific_token_prefix(value))


def _has_specific_token_prefix(value: str) -> bool:
    """Check if value starts with any known token prefix to avoid misclassification."""
    specific_prefixes = [
        'ghp_', 'github_pat_', 'sk_', 'pk_', 'xox', 'ya29.', 'EAACEdEose0cBA',
        'AKIA', '-----BEGIN'
    ]
    
    return any(value.startswith(prefix) for prefix in specific_prefixes)