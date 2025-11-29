"""
Error test rule for unit testing the Rule Engine error handling.

This rule raises exceptions to test how the engine handles rule failures.
"""

from typing import List
import pathlib

from sentinel.rules.base import Finding


class TestErrorRule:
    """
    Test rule that raises exceptions for testing error handling.

    This rule intentionally raises exceptions when certain conditions are met
    to test the engine's error handling capabilities.
    """

    def __init__(self):
        self.id = "TEST_ERROR_RULE"
        self.description = "Test rule that raises exceptions for error handling"
        self.severity = "high"

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        """
        Apply test rule to file content - raises exceptions for testing.

        Args:
            path: Path to the file being analyzed
            text: Content of the file as string

        Returns:
            List of Finding objects, or raises exception

        Raises:
            ValueError: If file content contains "RAISE_VALUE_ERROR"
            RuntimeError: If file content contains "RAISE_RUNTIME_ERROR"
        """
        if "RAISE_VALUE_ERROR" in text:
            raise ValueError("Test value error from TestErrorRule")

        if "RAISE_RUNTIME_ERROR" in text:
            raise RuntimeError("Test runtime error from TestErrorRule")

        # Return empty findings if no error conditions
        return []
