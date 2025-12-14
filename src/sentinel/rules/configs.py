"""
Configuration rule implementations for CodeSentinel.

Detects hardcoded configuration values, API keys, and other sensitive configuration
patterns according to the Phase 1 specification.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pathlib
import re
from typing import List, Dict

from sentinel.rules.base import Finding, RuleMeta, create_default_rule_meta
from sentinel.rules.token_types import classify_token, TokenType


# TODO: Phase 2 - Add CWE mapping for hardcoded API keys (CWE-798)
# TODO: Phase 2 - Add remediation guidance for environment variables/secrets management
# TODO: Phase 2 - Add tags: ['credentials', 'api-keys', 'secrets-management']
# TODO: Phase 2 - Integrate with language detection for context-aware reporting
class HardcodedAPIRule:
    """
    Rule to detect hardcoded API keys and tokens in source code.
    """

    id = "hardcoded-api-key"
    description = "Hardcoded API key or token detected"
    severity = "high"
    precedence = 80  # Generic API keys precedence
    meta = create_default_rule_meta(
        category="secrets",
        cwe_ids=["CWE-798"],
        risk_factors=["hardcoded", "credentials", "api-key"],
        detection_method="regex",
        false_positive_rate=0.1,
        remediation_priority="high",
        tags=["credentials", "api-keys", "secrets-management"],
        references=["https://cwe.mitre.org/data/definitions/798.html"],
        language_specificity="low",
        ai_explanation_priority="high"
    )

    # Common API key patterns
    API_KEY_PATTERNS = {
        "api_key_assignment": r'\bapi[_-]?key\s*[=:]\s*["\']([^"\']{20,})["\']',
        "secret_key_assignment": r'\bsecret[_-]?key\s*[=:]\s*["\']([^"\']{20,})["\']',
        "token_assignment": r'\btoken\s*[=:]\s*["\']([^"\']{20,})["\']',
        "password_assignment": r'\bpassword\s*[=:]\s*["\']([^"\']{8,})["\']',
        "stripe_secret_key": r'["\'](sk_(live|test)_[a-zA-Z0-9]{20,})["\']',
        "stripe_restricted_key": r'["\'](rk_(live|test)_[a-zA-Z0-9]{20,})["\']',
        "aws_access_key": r'["\'](AKIA[0-9A-Z]{16})["\']',
        "github_token": r'["\'](gh[ops]_[a-zA-Z0-9]{36})["\']',
        "slack_token": r'["\'](xox[pbar]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})["\']',
    }

    def __init__(self):
        """Initialize the rule with compiled patterns."""
        import sentinel.utils.patterns as patterns_module
        self.compiled_patterns = patterns_module.compile_patterns(self.API_KEY_PATTERNS)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        """
        Apply hardcoded API key detection to file content.

        Args:
            path: Path to the file being analyzed
            text: Content of the file as string

        Returns:
            List of Finding objects for detected API keys
        """
        findings: List[Finding] = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            import sentinel.utils.patterns as patterns_module
            matches = patterns_module.match_patterns(line, self.compiled_patterns)

            # Only create one finding per line, even if multiple patterns match
            if matches:
                # Extract the actual token value for classification
                token_value = None
                for pattern_match in matches:
                    # Extract the captured group (the actual token)
                    if pattern_match.pattern_id in ["stripe_secret_key", "stripe_restricted_key", 
                                                  "aws_access_key", "github_token", "slack_token"]:
                        # Extract the token from matched_text using regex
                        token_match = re.search(r'["\']([^"\']+)["\']', pattern_match.matched_text)
                        if token_match:
                            token_value = token_match.group(1)
                    else:
                        # For assignment patterns, extract the value
                        assignment_patterns = ["api_key_assignment", "secret_key_assignment", 
                                             "token_assignment", "password_assignment"]
                        if pattern_match.pattern_id in assignment_patterns:
                            # Extract the value inside quotes
                            quote_match = re.search(r'["\']([^"\']+)["\']', line)
                            if quote_match:
                                token_value = quote_match.group(1)
                    break  # Only process first match per line

                # Skip if this token is already classified by a more specific secret rule
                if token_value:
                    token_type = classify_token(token_value)
                    # Don't create finding if it's a specific provider token (avoid double-counting)
                    if token_type and token_type not in [TokenType.GENERIC_HIGH_ENTROPY, None]:
                        continue

                # Create excerpt (truncate if too long)
                excerpt = line.strip()
                if len(excerpt) > 100:
                    excerpt = excerpt[:97] + "..."

                finding = Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=line_num,
                    severity=self.severity,
                    excerpt=excerpt,
                    confidence=0.8  # High confidence for pattern matches
                )
                findings.append(finding)

        return findings


# TODO: Phase 2 - Add CWE mapping for hardcoded database credentials (CWE-798)
# TODO: Phase 2 - Add remediation guidance for secure credential storage
# TODO: Phase 2 - Add tags: ['database', 'credentials', 'connection-strings']
# TODO: Phase 2 - Integrate with language detection for context-aware reporting
class HardcodedDatabaseRule:
    """
    Rule to detect hardcoded database credentials and connection strings.
    """

    id = "hardcoded-database"
    description = "Hardcoded database credentials detected"
    severity = "high"
    precedence = 60  # Configuration rules precedence
    meta = create_default_rule_meta(
        category="secrets",
        cwe_ids=["CWE-798"],
        risk_factors=["hardcoded", "credentials", "database"],
        detection_method="regex",
        false_positive_rate=0.05,
        remediation_priority="high",
        tags=["database", "credentials", "connection-strings"],
        references=["https://cwe.mitre.org/data/definitions/798.html"],
        language_specificity="low",
        ai_explanation_priority="high"
    )

    # Database connection patterns
    DATABASE_PATTERNS = {
        "postgres_connection": r'\bpostgres(ql)?://[^:]+:[^@]+@[^"\'\s]+',
        "mysql_connection": r'\bmysql://[^:]+:[^@]+@[^"\'\s]+',
        "mongodb_connection": r'\bmongodb(\+srv)?://[^:]+:[^@]+@[^"\'\s]+',
        "redis_connection": r'\bredis://[^:]+:[^@]+@[^"\'\s]+',
        "database_credential_block": r'\bhost\s*[=:]\s*["\'][^"\']+["\']\s*,\s*port\s*[=:]\s*["\'][^"\']+["\']\s*,\s*(user|username)\s*[=:]\s*["\'][^"\']+["\']\s*,\s*(password|pass)\s*[=:]\s*["\'][^"\']+["\']',
    }

    def __init__(self):
        """Initialize the rule with compiled patterns."""
        import sentinel.utils.patterns as patterns_module
        self.compiled_patterns = patterns_module.compile_patterns(self.DATABASE_PATTERNS)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        """
        Apply hardcoded database credential detection to file content.

        Args:
            path: Path to the file being analyzed
            text: Content of the file as string

        Returns:
            List of Finding objects for detected database credentials
        """
        findings: List[Finding] = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            import sentinel.utils.patterns as patterns_module
            matches = patterns_module.match_patterns(line, self.compiled_patterns)

            # Only create one finding per line, even if multiple patterns match
            if matches:
                # Create excerpt (truncate if too long)
                excerpt = line.strip()
                if len(excerpt) > 100:
                    excerpt = excerpt[:97] + "..."

                finding = Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=line_num,
                    severity=self.severity,
                    excerpt=excerpt,
                    confidence=0.9  # Very high confidence for connection strings
                )
                findings.append(finding)

        return findings


# Export consolidated rules list for dynamic loading
rules = [
    HardcodedAPIRule(),
    HardcodedDatabaseRule(),
]
