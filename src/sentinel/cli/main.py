"""
CLI interface for CodeSentinel.

Command-line interface for the CodeSentinel security scanner according to the Phase 1 specification.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import argparse
import pathlib
import sys
from typing import Optional, List

from sentinel.scanner.engine import run_rules
from sentinel.scanner.walker import walk_directory, validate_target_path
from sentinel.reporting.json_report import generate_json_report
from sentinel.reporting.markdown import generate_markdown_report
from sentinel.rules.base import Finding
from sentinel.llm.explainer import ExplanationEngine
from sentinel.llm.provider import get_provider


def main() -> None:
    """
    Main CLI entry point for CodeSentinel.

    Parses command line arguments, validates inputs, executes the scan,
    and generates the requested report format.
    """
    parser = create_parser()
    args = parser.parse_args()

    try:
        if args.command == "version":
            print_version()
            return

        if args.command == "scan":
            run_scan(args)
            return

        # No command provided - show help
        parser.print_help()
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)  # Standard exit code for file not found
    except IsADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)  # Standard exit code for directory errors
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="codesentinel",
        description="""CodeSentinel - Security code scanner for detecting secrets and vulnerabilities

Phase 2 AI Explainer Mode:
  Enable AI-powered security explanations, CWE mapping, and remediation guidance.
  Set DEEPSEEK_API_KEY environment variable for real AI integration.
  Without API key, system uses placeholder explanations with contextual data.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scan with markdown output
  codesentinel scan /path/to/project

  # JSON output for CI integration
  codesentinel scan /path/to/project --format json

  # AI explainer mode (requires DEEPSEEK_API_KEY)
  codesentinel scan /path/to/project --ai --explain

  # AI mode with JSON output for machine processing
  codesentinel scan /path/to/project --ai --llm-provider deepseek --format json

Environment Variables:
  DEEPSEEK_API_KEY      API key for DeepSeek LLM provider (required for real AI)
  DEEPSEEK_BASE_URL     Base URL for DeepSeek API (optional, default: https://api.deepseek.com)
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a directory or file for security issues")
    scan_parser.add_argument(
        "target",
        help="Directory or file to scan"
    )
    scan_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    # Phase 2 AI flags
    scan_parser.add_argument(
        "--ai",
        action="store_true",
        help="""Enable AI-powered security explanations (Phase 2).
        Provides detailed explanations, CWE mapping, and remediation guidance.
        Without DEEPSEEK_API_KEY, uses placeholder explanations with contextual data."""
    )
    scan_parser.add_argument(
        "--explain",
        action="store_true",
        help="""Generate detailed explanations for findings (Phase 2).
        Same as --ai, provided for convenience and future extensibility."""
    )
    scan_parser.add_argument(
        "--llm-provider",
        choices=["deepseek", "openai", "local_ollama"],
        default="deepseek",
        help="""LLM provider to use for AI explanations (default: deepseek).
        Currently supported: deepseek (requires DEEPSEEK_API_KEY).
        OpenAI and LocalOllama are placeholder implementations for future development."""
    )

    # Output file option
    scan_parser.add_argument(
        "--output",
        "-o",
        help="Write output to specified file instead of stdout"
    )

    # CI mode option
    scan_parser.add_argument(
        "--ci",
        action="store_true",
        help="""CI mode: return exit code 1 if findings are detected, 0 otherwise.
        Forces JSON output for machine readability."""
    )

    return parser


def print_version() -> None:
    """
    Print version information and exit.
    """
    from sentinel import __version__
    print(f"CodeSentinel v{__version__}")
    print("Copyright (c) 2025 Andrei Antonescu")
    print("SPDX-License-Identifier: MIT")


def enrich_findings_with_ai(findings: List[Finding], provider_name: str) -> List[Finding]:
    """
    Enrich findings with AI-powered explanations.
    
    During Phase 2, this uses real LLM integration when configured,
    with graceful fallbacks to placeholder data.
    
    Args:
        findings: List of security findings to enrich
        provider_name: Name of the LLM provider to use
        
    Returns:
        List of enriched findings with AI explanations
    """
    try:
        # Get LLM provider
        provider = get_provider(provider_name)
        
        # Initialize explanation engine
        explainer = ExplanationEngine()
        
        enriched_findings = []
        
        for finding in findings:
            try:
                # Generate AI explanation
                explanation_data = explainer.explain_finding(finding, provider)
                
                # Type-safe extraction of explanation data
                cwe_id = explanation_data.get("cwe_id")
                remediation = explanation_data.get("remediation")
                risk_score = explanation_data.get("risk_score")
                references = explanation_data.get("references")
                
                # Ensure types are correct
                if cwe_id is not None and not isinstance(cwe_id, str):
                    cwe_id = None
                if remediation is not None and not isinstance(remediation, str):
                    remediation = None
                if risk_score is not None and not isinstance(risk_score, (int, float)):
                    risk_score = None
                if references is not None and not isinstance(references, list):
                    references = None
                elif references is not None:
                    # Ensure all references are strings
                    references = [str(ref) for ref in references if isinstance(ref, str)]
                
                # Create enriched finding
                enriched_finding = Finding(
                    rule_id=finding.rule_id,
                    file_path=finding.file_path,
                    line=finding.line,
                    severity=finding.severity,
                    excerpt=finding.excerpt,
                    confidence=finding.confidence,
                    cwe_id=cwe_id,
                    category=finding.category,
                    tags=finding.tags,
                    remediation=remediation,
                    language=finding.language,
                    risk_score=float(risk_score) if risk_score is not None else None,
                    references=references
                )
                
                enriched_findings.append(enriched_finding)
                
            except Exception as e:
                # If AI enrichment fails for one finding, continue with others
                print(f"Warning: Failed to enrich finding {finding.rule_id}: {e}", file=sys.stderr)
                enriched_findings.append(finding)  # Keep original finding
        
        return enriched_findings
        
    except Exception as e:
        # If AI system fails completely, return original findings
        print(f"Warning: AI explanation system failed: {e}", file=sys.stderr)
        print("Continuing with standard scan results...", file=sys.stderr)
        return findings


def is_provider_configured(provider_name: str) -> bool:
    """
    Check if the specified provider is properly configured for real API calls.
    
    Args:
        provider_name: Name of the provider to check
        
    Returns:
        True if provider is configured for real API calls, False otherwise
    """
    try:
        # For DeepSeek provider specifically, check if API key is set
        if provider_name == "deepseek":
            # Use a more type-safe approach - check environment variable directly
            import os
            return bool(os.getenv("DEEPSEEK_API_KEY"))
        # For other providers, they are currently placeholders
        return False
    except Exception:
        return False


def run_scan(args) -> None:
    """
    Execute a security scan and generate reports.

    Args:
        args: Parsed command line arguments for scan command
    """
    # Validate and resolve target path
    target_path = validate_target_path(args.target)

    # Discover files to scan
    files = walk_directory(target_path)

    if not files:
        print(f"No files found to scan in: {target_path}")
        # Even for empty scans, generate a report
        findings = []
    else:
        print(f"Scanning {len(files)} files...")

        # Run security rules
        findings = run_rules(files)

    # Apply AI enrichment if requested
    if args.ai or args.explain:
        provider_status = "real API" if is_provider_configured(args.llm_provider) else "placeholder"
        print(f"Applying AI-powered explanations ({provider_status} mode)...")
        findings = enrich_findings_with_ai(findings, args.llm_provider)

    # Force JSON format for CI mode
    if args.ci:
        args.format = "json"

    # Generate report
    if args.format == "json":
        report = generate_json_report(findings)
    else:
        report = generate_markdown_report(findings)

    # Output to file or stdout
    if args.output:
        output_path = pathlib.Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    if args.ci:
        # CI mode: exit code 1 if findings, 0 if clean
        sys.exit(1 if findings else 0)
    else:
        # Normal mode: exit code 1 if findings, 0 if clean
        sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
