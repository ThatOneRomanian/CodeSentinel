"""
JSON reporter for CodeSentinel.

Generates structured JSON reports from security scan findings for machine processing.
"""

import json
from typing import List, Dict, Any
from datetime import datetime

from ..rules.base import Finding


class JSONReporter:
    """
    Generates JSON format security reports.

    Creates structured JSON output suitable for CI/CD integration and
    machine processing with the following format:
    [
      {
        "rule_id": "...",
        "severity": "...",
        "file_path": "...",
        "line": 0,
        "excerpt": "...",
        "confidence": 0.0
      }
    ]
    """

    def __init__(self):
        """Initialize the JSON reporter."""
        pass

    def generate_report(self, findings: List[Finding], scan_path: str) -> str:
        """
        Generate a JSON report from security findings.

        Args:
            findings: List of Finding objects from the scan
            scan_path: Path that was scanned

        Returns:
            JSON formatted report string
        """
        report_data = self._build_report_data(findings, scan_path)
        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def _build_report_data(self, findings: List[Finding], scan_path: str) -> Dict[str, Any]:
        """
        Build the complete report data structure.

        Args:
            findings: List of Finding objects
            scan_path: Path that was scanned

        Returns:
            Dictionary containing all report data
        """
        report_data = {
            "metadata": self._generate_metadata(scan_path),
            "summary": self._generate_summary(findings),
            "findings": [finding.to_dict() for finding in findings],
        }

        return report_data

    def _generate_metadata(self, scan_path: str) -> Dict[str, Any]:
        """
        Generate report metadata.

        Args:
            scan_path: Path that was scanned

        Returns:
            Dictionary containing metadata
        """
        from .. import __version__

        return {
            "tool": "CodeSentinel",
            "version": __version__,
            "scan_path": scan_path,
            "timestamp": datetime.now().isoformat(),
            "format_version": "1.0",
        }

    def _generate_summary(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Generate summary statistics for the report.

        Args:
            findings: List of Finding objects

        Returns:
            Dictionary containing summary statistics
        """
        total_findings = len(findings)
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for finding in findings:
            severity_counts[finding.severity.value] += 1

        file_count = len(set(str(finding.file_path) for finding in findings))

        return {
            "total_findings": total_findings,
            "severity_breakdown": severity_counts,
            "files_affected": file_count,
            "scan_duration": 0.0,  # Will be populated in Phase 1
        }

    def generate_ci_report(self, findings: List[Finding], scan_path: str) -> str:
        """
        Generate a CI-optimized JSON report.

        This version is optimized for CI/CD systems with minimal metadata
        and strict exit code requirements.

        Args:
            findings: List of Finding objects from the scan
            scan_path: Path that was scanned

        Returns:
            JSON formatted CI report string
        """
        ci_data = {
            "findings": [finding.to_dict() for finding in findings],
            "has_findings": len(findings) > 0,
            "critical_findings": len([f for f in findings if f.severity.value == "critical"]),
            "high_findings": len([f for f in findings if f.severity.value == "high"]),
        }

        return json.dumps(ci_data, indent=2, ensure_ascii=False)