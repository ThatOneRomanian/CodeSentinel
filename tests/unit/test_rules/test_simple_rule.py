"""
Simple test rule for unit testing the Rule Engine.

This rule returns findings for specific patterns, used for testing rule application
and finding normalization.
"""
from typing import List
import pathlib

from sentinel.rules.base import Finding


class TestSimpleRule:
    """
    Test rule that returns findings for specific patterns.

    Used to test that rules can be loaded, applied, and generate normalized findings.
    """

    def __init__(self):
        self.id = "TEST_SIMPLE_RULE"
        self.description = "Test rule that returns findings for specific patterns"
        self.severity = "low"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        """
        Apply test rule to file content - returns findings for specific patterns.

        Args:
            path: Path to the file being analyzed
            text: Content of the file as string

        Returns:
            List of Finding objects for detected patterns
        """
        findings = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            if "TEST_PATTERN_" in line:
                confidence = 0.9 if "123" in line else 0.8
                findings.append(Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=line_num,
                    severity=self.severity,
                    excerpt=line.strip(),
                    confidence=confidence
                ))
            elif "LINE_NUMBER_" in line:
                findings.append(Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=line_num,
                    severity=self.severity,
                    excerpt=line.strip(),
                    confidence=0.7
                ))

        return findings
