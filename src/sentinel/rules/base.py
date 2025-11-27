"""
Base classes and data structures for CodeSentinel rules.

Defines the Rule abstract base class and Finding data structure used by
all security rules in the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
import pathlib


class Severity(Enum):
    """Severity levels for security findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """
    Normalized finding object for security issues.

    Attributes:
        rule_id: Unique identifier for the rule that generated this finding
        file_path: Path to the file where the issue was found
        line: Line number where the issue was found (0 if not applicable)
        severity: Severity level of the finding
        excerpt: Code excerpt showing the issue
        confidence: Confidence score (0.0 to 1.0)
        message: Human-readable description of the issue
        context: Additional context data (optional)
    """

    rule_id: str
    file_path: pathlib.Path
    line: int
    severity: Severity
    excerpt: str
    confidence: float
    message: str
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert finding to dictionary for serialization.

        Returns:
            Dictionary representation of the finding
        """
        return {
            "rule_id": self.rule_id,
            "file_path": str(self.file_path),
            "line": self.line,
            "severity": self.severity.value,
            "excerpt": self.excerpt,
            "confidence": self.confidence,
            "message": self.message,
            "context": self.context or {},
        }


class Rule(ABC):
    """
    Abstract base class for all security rules.

    All rule implementations must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self):
        """Initialize the rule with default values."""
        self.rule_id = self.__class__.__name__
        self.description = "Security rule"
        self.severity = Severity.MEDIUM

    @abstractmethod
    def scan(self, file_path: pathlib.Path, content: str) -> List[Finding]:
        """
        Scan a file for security issues.

        Args:
            file_path: Path to the file being scanned
            content: Content of the file as string

        Returns:
            List of Finding objects for detected issues
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get rule metadata.

        Returns:
            Dictionary containing rule metadata
        """
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "severity": self.severity.value,
        }