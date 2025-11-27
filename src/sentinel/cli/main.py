"""
Main CLI entry point for CodeSentinel.

Provides the command-line interface for scanning directories and reporting
security findings in codebases.
"""

import argparse
import sys
from typing import List, Optional


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CodeSentinel CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="codesentinel",
        description="Local-first security scanner for developers and students",
        epilog="Run 'codesentinel scan --help' for more information on scanning.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a directory for security issues")
    scan_parser.add_argument("target_path", help="Path to scan (file or directory)")
    scan_parser.add_argument(
        "--format",
        choices=["json", "md"],
        default="md",
        help="Output format (default: md)",
    )
    scan_parser.add_argument(
        "--exclude",
        action="append",
        help="Glob/regex patterns to exclude",
    )
    scan_parser.add_argument(
        "--show-entropy",
        action="store_true",
        help="Display entropy scores for findings",
    )
    scan_parser.add_argument(
        "--exit-on-findings",
        action="store_true",
        help="Exit with code 1 when issues are detected",
    )
    scan_parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: JSON only, no color, strict exit codes",
    )
    scan_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detailed logging output",
    )

    # Version command
    subparsers.add_parser("version", help="Show version information")

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "version":
        from .. import __version__
        print(f"CodeSentinel v{__version__}")
        return 0
    elif parsed_args.command == "scan":
        # Placeholder for scan functionality
        print(f"Scanning {parsed_args.target_path}...")
        print("(Scan functionality will be implemented in Phase 1)")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())