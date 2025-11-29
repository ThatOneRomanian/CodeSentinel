"""
Base classes and data structures for CodeSentinel rules.

Defines the Rule protocol and Finding data structure used by all security
rules in the system according to the Phase 1 specification.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Protocol, Dict, Any
import pathlib


@dataclass
class RuleMeta:
    """
    Enhanced metadata for security rules to support AI explanations.
    
    Attributes:
        category: High-level category (e.g., 'secrets', 'config', 'supply_chain')
        cwe_ids: List of related Common Weakness Enumeration IDs
        risk_factors: Factors that contribute to risk assessment
        detection_method: How the rule detects issues (regex, entropy, etc.)
        false_positive_rate: Estimated false positive rate (0.0-1.0)
        remediation_priority: Priority for fixing (low, medium, high, critical)
        tags: Additional categorization tags
        references: Reference URLs for documentation
        language_specificity: How language-specific the rule is (low, medium, high)
        ai_explanation_priority: Priority for AI explanation generation
    """
    
    category: str
    """High-level category for rule grouping."""
    
    cwe_ids: Optional[List[str]] = None
    """List of related CWE identifiers."""
    
    risk_factors: Optional[List[str]] = None
    """Factors that contribute to risk assessment."""
    
    detection_method: Optional[str] = None
    """How the rule detects issues (regex, entropy, pattern, etc.)."""
    
    false_positive_rate: Optional[float] = None
    """Estimated false positive rate (0.0-1.0)."""
    
    remediation_priority: Optional[str] = None
    """Priority for fixing (low, medium, high, critical)."""
    
    tags: Optional[List[str]] = None
    """Additional categorization tags."""
    
    references: Optional[List[str]] = None
    """Reference URLs for documentation."""
    
    language_specificity: Optional[str] = None
    """How language-specific the rule is (low, medium, high)."""
    
    ai_explanation_priority: Optional[str] = None
    """Priority for AI explanation generation."""


@dataclass
class Finding:
    """
    Normalized finding object for security issues.

    Attributes:
        rule_id: Unique identifier for the rule that generated this finding
        file_path: Path to the file where the issue was found
        line: Line number where the issue was found, or None if not applicable
        severity: Severity level of the finding as string
        excerpt: Code excerpt showing the issue, or None if not available
        confidence: Confidence score (0.0 to 1.0), or None if not calculated
        cwe_id: Common Weakness Enumeration ID for vulnerability classification
        category: High-level category for grouping findings (e.g., 'secret', 'config')
        tags: Additional categorization tags (e.g., 'api-key', 'hardcoded', 'crypto')
        remediation: Recommended fix or mitigation steps
        language: Programming language of the file where finding was detected
        risk_score: Numeric risk assessment score (1-10) for prioritization
        references: List of reference URLs (CWE pages, documentation, etc.)
    """

    rule_id: str
    file_path: pathlib.Path
    line: Optional[int]
    severity: str
    excerpt: Optional[str]
    confidence: Optional[float]
    
    # Phase 2 extensibility fields
    cwe_id: Optional[str] = None
    """Common Weakness Enumeration ID for standardized vulnerability classification."""
    
    category: Optional[str] = None
    """High-level category for grouping findings (e.g., 'secret', 'config', 'supply-chain')."""
    
    tags: Optional[List[str]] = None
    """Additional categorization tags for enhanced filtering and organization."""
    
    remediation: Optional[str] = None
    """Recommended fix or mitigation steps for the security issue."""
    
    language: Optional[str] = None
    """Programming language of the file where the finding was detected."""
    
    risk_score: Optional[float] = None
    """Numeric risk assessment score (1-10) for dashboard prioritization and quantitative analysis."""
    
    references: Optional[List[str]] = None
    """List of reference URLs to CWE pages, documentation, or other supporting materials."""


class Rule(Protocol):
    """
    Protocol defining the interface that all security rules must implement.

    Rule modules must provide this interface for compatibility with the
    rule engine and future plugin architecture.
    """

    # Rule metadata attributes
    id: str
    description: str
    severity: str
    meta: RuleMeta

    @abstractmethod
    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        """
        Apply this rule to a file and return any findings.

        Args:
            path: Path to the file being analyzed
            text: Content of the file as string

        Returns:
            List of Finding objects for detected security issues
        """
        ...


def create_default_rule_meta(category: str, **kwargs) -> RuleMeta:
    """
    Create a default RuleMeta instance with sensible defaults.
    
    Args:
        category: High-level category for the rule
        **kwargs: Additional metadata fields to override defaults
        
    Returns:
        RuleMeta instance with default values
    """
    defaults = {
        "cwe_ids": None,
        "risk_factors": None,
        "detection_method": "regex",
        "false_positive_rate": 0.1,
        "remediation_priority": "medium",
        "tags": [],
        "references": [],
        "language_specificity": "low",
        "ai_explanation_priority": "medium",
    }
    
    # Update defaults with provided kwargs
    defaults.update(kwargs)
    
    return RuleMeta(category=category, **defaults)
