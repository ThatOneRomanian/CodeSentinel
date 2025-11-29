"""
Unit tests for JSON reporting functionality.

Tests JSON report generation and formatting for CodeSentinel security findings.
"""

import pytest
import json
from unittest.mock import Mock

from sentinel.reporting.json_report import generate_json_report
from sentinel.rules.base import Finding
import pathlib


class TestJSONReport:
    """Test JSON report generation."""

    def test_generate_json_report_empty_findings(self):
        """Test generating JSON report with empty findings."""
        findings = []
        report = generate_json_report(findings)
        
        # Parse JSON to validate structure
        report_data = json.loads(report)
        
        assert "scan_summary" in report_data
        assert "findings" in report_data
        assert report_data["scan_summary"]["total_findings"] == 0
        assert report_data["scan_summary"]["by_severity"]["high"] == 0
        assert report_data["scan_summary"]["by_severity"]["medium"] == 0
        assert report_data["scan_summary"]["by_severity"]["low"] == 0
        assert report_data["findings"] == []

    def test_generate_json_report_with_findings(self):
        """Test generating JSON report with actual findings."""
        findings = [
            Finding(
                rule_id="test-rule-1",
                file_path=pathlib.Path("/test/file1.py"),
                line=10,
                severity="high",
                excerpt="api_key = 'secret123'",
                confidence=0.8
            ),
            Finding(
                rule_id="test-rule-2", 
                file_path=pathlib.Path("/test/file2.py"),
                line=20,
                severity="medium",
                excerpt="password = 'weak'",
                confidence=0.6
            )
        ]
        
        report = generate_json_report(findings)
        report_data = json.loads(report)
        
        assert report_data["scan_summary"]["total_findings"] == 2
        assert report_data["scan_summary"]["by_severity"]["high"] == 1
        assert report_data["scan_summary"]["by_severity"]["medium"] == 1
        assert report_data["scan_summary"]["by_severity"]["low"] == 0
        
        assert len(report_data["findings"]) == 2
        assert report_data["findings"][0]["rule_id"] == "test-rule-1"
        assert report_data["findings"][0]["severity"] == "high"
        assert report_data["findings"][1]["rule_id"] == "test-rule-2"
        assert report_data["findings"][1]["severity"] == "medium"

    def test_generate_json_report_severity_counts(self):
        """Test that severity counts are calculated correctly."""
        findings = [
            Finding(
                rule_id="test-rule",
                file_path=pathlib.Path("/test/file.py"),
                line=1,
                severity="high",
                excerpt="test",
                confidence=0.9
            ),
            Finding(
                rule_id="test-rule",
                file_path=pathlib.Path("/test/file.py"), 
                line=2,
                severity="high",
                excerpt="test",
                confidence=0.9
            ),
            Finding(
                rule_id="test-rule",
                file_path=pathlib.Path("/test/file.py"),
                line=3,
                severity="medium", 
                excerpt="test",
                confidence=0.7
            ),
            Finding(
                rule_id="test-rule",
                file_path=pathlib.Path("/test/file.py"),
                line=4,
                severity="low",
                excerpt="test", 
                confidence=0.5
            )
        ]
        
        report = generate_json_report(findings)
        report_data = json.loads(report)
        
        assert report_data["scan_summary"]["total_findings"] == 4
        assert report_data["scan_summary"]["by_severity"]["high"] == 2
        assert report_data["scan_summary"]["by_severity"]["medium"] == 1
        assert report_data["scan_summary"]["by_severity"]["low"] == 1

    def test_generate_json_report_finding_structure(self):
        """Test that each finding has the expected structure."""
        findings = [
            Finding(
                rule_id="test-rule",
                file_path=pathlib.Path("/test/file.py"),
                line=42,
                severity="high",
                excerpt="sensitive_data = 'exposed'",
                confidence=0.95
            )
        ]
        
        report = generate_json_report(findings)
        report_data = json.loads(report)
        
        finding = report_data["findings"][0]
        assert finding["rule_id"] == "test-rule"
        assert finding["file_path"] == "/test/file.py"
        assert finding["line"] == 42
        assert finding["severity"] == "high"
        assert finding["excerpt"] == "sensitive_data = 'exposed'"
        assert finding["confidence"] == 0.95

    def test_generate_json_report_unicode_support(self):
        """Test that JSON report handles unicode characters correctly."""
        findings = [
            Finding(
                rule_id="test-rule",
                file_path=pathlib.Path("/test/文件.py"),
                line=1,
                severity="medium",
                excerpt="password = '密码123'",
                confidence=0.8
            )
        ]
        
        report = generate_json_report(findings)
        # Should not raise Unicode encoding errors
        report_data = json.loads(report)
        
        assert report_data["findings"][0]["file_path"] == "/test/文件.py"
        assert report_data["findings"][0]["excerpt"] == "password = '密码123'"
