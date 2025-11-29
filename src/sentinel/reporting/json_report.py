"""
JSON reporting module for CodeSentinel.

Generates JSON-formatted security scan reports according to the Phase 1 specification.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import json
from typing import List, Dict, Any

from sentinel.rules.base import Finding


def generate_json_report(findings: List[Finding]) -> str:
    """
    Generate a JSON report from a list of findings.

    Args:
        findings: List of Finding objects to include in the report

    Returns:
        JSON string containing the formatted report

    Example:
        >>> findings = [Finding(...), Finding(...)]
        >>> report = generate_json_report(findings)
        >>> print(report)
        {
            "scan_summary": {
                "total_findings": 2,
                "by_severity": {
                    "high": 1,
                    "medium": 1,
                    "low": 0
                }
            },
            "findings": [...]
        }
    """
    # Build scan summary
    severity_counts = {"high": 0, "medium": 0, "low": 0}

    for finding in findings:
        severity_counts[finding.severity] += 1

    scan_summary = {
        "total_findings": len(findings),
        "by_severity": severity_counts
    }

    # Convert findings to dictionaries
    findings_data = []
    for finding in findings:
        finding_dict = {
            "rule_id": finding.rule_id,
            "file_path": str(finding.file_path),
            "line": finding.line,
            "severity": finding.severity,
            "excerpt": finding.excerpt,
            "confidence": finding.confidence
        }
        findings_data.append(finding_dict)

    # Build complete report
    report = {
        "scan_summary": scan_summary,
        "findings": findings_data
    }

    return json.dumps(report, indent=2, ensure_ascii=False)
