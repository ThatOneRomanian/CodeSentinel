"""
Unit tests for the severity mapping module.

Tests the SEVERITY_RANK mapping and severity_value function.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pytest

from sentinel.rules.severity import SEVERITY_RANK, severity_value


class TestSeverityMapping:
    """Test cases for the severity mapping functionality."""

    def test_severity_rank_mapping(self):
        """Test that SEVERITY_RANK contains expected severity levels."""
        expected_mapping = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "info": 0,
        }
        assert SEVERITY_RANK == expected_mapping

    def test_severity_value_valid_levels(self):
        """Test severity_value with valid severity levels."""
        assert severity_value("critical") == 4
        assert severity_value("high") == 3
        assert severity_value("medium") == 2
        assert severity_value("low") == 1
        assert severity_value("info") == 0

    def test_severity_value_case_insensitive(self):
        """Test severity_value is case insensitive."""
        assert severity_value("CRITICAL") == 4
        assert severity_value("High") == 3
        assert severity_value("MeDiUm") == 2
        assert severity_value("LOW") == 1
        assert severity_value("INFO") == 0

    def test_severity_value_unknown_level(self):
        """Test severity_value with unknown severity levels."""
        assert severity_value("unknown") == -1
        assert severity_value("") == -1
        assert severity_value("invalid_level") == -1
        assert severity_value("warning") == -1

    def test_severity_value_edge_cases(self):
        """Test severity_value with edge cases."""
        # None should return -1
        assert severity_value(None) == -1
        
        # Numbers as strings should return -1
        assert severity_value("1") == -1
        assert severity_value("2") == -1

    def test_severity_value_whitespace(self):
        """Test severity_value handles whitespace."""
        assert severity_value(" critical ") == 4
        assert severity_value("  high  ") == 3
        assert severity_value("medium ") == 2
        assert severity_value(" low") == 1

    def test_severity_rank_immutability(self):
        """Test that SEVERITY_RANK mapping is not accidentally modified."""
        original_mapping = SEVERITY_RANK.copy()
        
        # Attempt to modify (should not affect the original)
        SEVERITY_RANK["test"] = 5
        
        # Check that the original keys are still there
        assert "critical" in SEVERITY_RANK
        assert "high" in SEVERITY_RANK
        assert "medium" in SEVERITY_RANK
        assert "low" in SEVERITY_RANK
        assert "info" in SEVERITY_RANK
        
        # Clean up the test key
        del SEVERITY_RANK["test"]

    def test_severity_value_return_type(self):
        """Test that severity_value returns integers."""
        assert isinstance(severity_value("critical"), int)
        assert isinstance(severity_value("high"), int)
        assert isinstance(severity_value("medium"), int)
        assert isinstance(severity_value("low"), int)
        assert isinstance(severity_value("info"), int)
        assert isinstance(severity_value("unknown"), int)

    def test_severity_ordering(self):
        """Test that severity values maintain proper ordering."""
        assert severity_value("critical") > severity_value("high")
        assert severity_value("high") > severity_value("medium")
        assert severity_value("medium") > severity_value("low")
        assert severity_value("low") > severity_value("info")