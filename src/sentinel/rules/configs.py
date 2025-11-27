"""
Configuration vulnerability rules for CodeSentinel.

Provides rules for detecting insecure configurations in various configuration files.
"""

import re
from typing import List
import pathlib

from .base import Rule, Finding, Severity


class ConfigRules(Rule):
    """
    Collection of rules for detecting insecure configurations.

    Detects:
    - DEBUG=True (Flask/Django)
    - Bind to 0.0.0.0
    - Weak crypto (md5, sha1)
    - Default credentials
    - Missing environment variable usage
    - Unsecured TLS flags
    - Insecure config literals
    """

    def __init__(self):
        """Initialize configuration vulnerability rules."""
        super().__init__()
        self.rule_id = "ConfigRules"
        self.description = "Detects insecure configurations in code and config files"
        self.severity = Severity.MEDIUM

        # Placeholder patterns - will be implemented in Phase 1
        self.patterns = {
            "DEBUG_ENABLED": r"DEBUG\s*=\s*True",
            "BIND_ALL_INTERFACES": r"0\.0\.0\.0",
            "WEAK_CRYPTO": r"(md5|sha1)",
            "DEFAULT_CREDENTIALS": r"(admin:admin|root:root|user:user)",
            "HARDCODED_SECRETS": r"(secret|password|key)\s*=\s*['\"][^'\"]+['\"]",
        }

    def scan(self, file_path: pathlib.Path, content: str) -> List[Finding]:
        """
        Scan file content for insecure configurations.

        Args:
            file_path: Path to the file being scanned
            content: Content of the file as string

        Returns:
            List of Finding objects for detected configuration issues
        """
        findings = []

        # Placeholder implementation - will be enhanced in Phase 1
        # This will include context-aware pattern matching and file type detection

        return findings

    def _detect_debug_enabled(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect DEBUG=True in Flask/Django applications."""
        # Placeholder - will be implemented in Phase 1
        return []

    def _detect_bind_all_interfaces(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect binding to 0.0.0.0 (all interfaces)."""
        # Placeholder - will be implemented in Phase 1
        return []

    def _detect_weak_crypto(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect weak cryptographic algorithms (md5, sha1)."""
        # Placeholder - will be implemented in Phase 1
        return []

    def _detect_default_credentials(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect default or hardcoded credentials."""
        # Placeholder - will be implemented in Phase 1
        return []

    def _detect_missing_env_vars(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect missing environment variable usage for secrets."""
        # Placeholder - will be implemented in Phase 1
        return []

    def _detect_unsecured_tls(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect unsecured TLS/SSL configurations."""
        # Placeholder - will be implemented in Phase 1
        return []

    def _detect_insecure_config_literals(self, content: str, file_path: pathlib.Path) -> List[Finding]:
        """Detect insecure configuration literals."""
        # Placeholder - will be implemented in Phase 1
        return []