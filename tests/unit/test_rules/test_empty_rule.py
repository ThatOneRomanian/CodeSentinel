"""
Empty test rule for unit testing the Rule Engine.

This rule always returns empty findings, used for testing rule loading and application.
"""
from typing import List
import pathlib

from sentinel.rules.base import Finding


class TestEmptyRule:
    """
    Test rule that never returns any findings.

    Used to test that rules can be loaded and applied without generating findings.
    """

    def __init__(self):
        self.id = "TEST_EMPTY_RULE"
        self.description = "Test rule that returns no findings"
        self.severity = "info"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        """
        Apply test rule to file content - always returns empty list.

        Args:
            path: Path to the file being analyzed
            text: Content of the file as string

        Returns:
            Empty list of Finding objects
        """
        return []
