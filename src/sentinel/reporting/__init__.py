"""
Reporting module for CodeSentinel.

Contains report generation components for security scan results.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

from sentinel.reporting.json_report import generate_json_report
from sentinel.reporting.markdown import generate_markdown_report

__all__ = ["generate_json_report", "generate_markdown_report"]
