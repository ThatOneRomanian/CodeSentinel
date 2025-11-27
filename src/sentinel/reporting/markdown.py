"""
Markdown reporter for CodeSentinel.

Generates human-readable Markdown reports from security scan findings.
"""

from typing import List
from datetime import datetime

from ..rules.base import Finding


class MarkdownReporter:
    """
    Generates Markdown format security reports.

    Creates reports with:
    - Summary section
    - List of findings grouped by severity
    - Per-file breakdown
    - Excerpts
    - Recommendations
    """

    def __init__(self):
        """Initialize the Markdown reporter."""
        pass

    def generate_report(self, findings: List[Finding], scan_path: str) -> str:
        """
        Generate a Markdown report from security findings.

        Args:
            findings: List of Finding objects from the scan
            scan_path: Path that was scanned

        Returns:
            Markdown formatted report string
        """
        report_lines = []

        # Header
        report_lines.append("# CodeSentinel Security Scan Report")
        report_lines.append("")
        report_lines.append(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Scan Path:** `{scan_path}`")
        report_lines.append("")

        # Summary section
        summary = self._generate_summary(findings)
        report_lines.extend(summary)
        report_lines.append("")

        # Findings by severity
        findings_by_severity = self._group_findings_by_severity(findings)
        for severity, severity_findings in findings_by_severity.items():
            if severity_findings:
                report_lines.append(f"## {severity.value.capitalize()} Severity Findings")
                report_lines.append("")
                for finding in severity_findings:
                    report_lines.extend(self._format_finding(finding))
                report_lines.append("")

        # Per-file breakdown
        report_lines.extend(self._generate_file_breakdown(findings))
        report_lines.append("")

        # Recommendations
        report_lines.extend(self._generate_recommendations(findings))
        report_lines.append("")

        return "\n".join(report_lines)

    def _generate_summary(self, findings: List[Finding]) -> List[str]:
        """Generate summary section of the report."""
        summary = ["## Summary", ""]

        total_findings = len(findings)
        severity_counts = {
            "critical": len([f for f in findings if f.severity.value == "critical"]),
            "high": len([f for f in findings if f.severity.value == "high"]),
            "medium": len([f for f in findings if f.severity.value == "medium"]),
            "low": len([f for f in findings if f.severity.value == "low"]),
        }

        summary.append(f"- **Total Findings:** {total_findings}")
        for severity, count in severity_counts.items():
            if count > 0:
                summary.append(f"- **{severity.capitalize()} Severity:** {count}")

        return summary

    def _group_findings_by_severity(self, findings: List[Finding]) -> dict:
        """Group findings by severity level."""
        grouped = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for finding in findings:
            grouped[finding.severity.value].append(finding)

        return grouped

    def _format_finding(self, finding: Finding) -> List[str]:
        """Format a single finding for the report."""
        lines = []
        lines.append(f"### {finding.rule_id}")
        lines.append("")
        lines.append(f"- **File:** `{finding.file_path}`")
        lines.append(f"- **Line:** {finding.line}")
        lines.append(f"- **Confidence:** {finding.confidence:.2f}")
        lines.append(f"- **Message:** {finding.message}")
        lines.append("")
        lines.append("**Code Excerpt:**")
        lines.append("```")
        lines.append(finding.excerpt)
        lines.append("```")
        lines.append("")

        return lines

    def _generate_file_breakdown(self, findings: List[Finding]) -> List[str]:
        """Generate per-file breakdown of findings."""
        file_findings = {}
        for finding in findings:
            file_path = str(finding.file_path)
            if file_path not in file_findings:
                file_findings[file_path] = []
            file_findings[file_path].append(finding)

        lines = ["## Per-File Breakdown", ""]
        for file_path, file_finds in file_findings.items():
            if file_finds:
                lines.append(f"### `{file_path}`")
                lines.append("")
                for finding in file_finds:
                    lines.append(f"- **Line {finding.line}:** {finding.rule_id} ({finding.severity.value})")
                lines.append("")

        return lines

    def _generate_recommendations(self, findings: List[Finding]) -> List[str]:
        """Generate recommendations based on findings."""
        lines = ["## Recommendations", ""]

        if not findings:
            lines.append("No security issues detected. Continue following secure coding practices.")
            return lines

        # Placeholder recommendations - will be enhanced in Phase 1
        lines.append("### General Security Recommendations")
        lines.append("")
        lines.append("- Review all detected secrets and consider rotating them")
        lines.append("- Move hardcoded secrets to environment variables or secure storage")
        lines.append("- Ensure DEBUG mode is disabled in production environments")
        lines.append("- Use strong cryptographic algorithms (avoid md5, sha1)")
        lines.append("- Implement proper access controls and authentication")
        lines.append("- Regularly update dependencies to patch security vulnerabilities")
        lines.append("")

        return lines