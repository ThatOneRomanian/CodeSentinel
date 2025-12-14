import re
import pathlib
from typing import List, Optional

from sentinel.rules.base import Finding
from sentinel.utils.parsers import get_yaml_key_value


def is_gha_workflow(filepath: str) -> bool:
    """Return True if the file path is likely a GitHub Actions workflow."""
    return ".github/workflows/" in filepath and filepath.endswith((".yml", ".yaml"))


def _leading_blank_line_count(text: str) -> int:
    """Count leading blank lines to adjust reported line numbers."""
    count = 0
    for line in text.splitlines():
        if line.strip() == "":
            count += 1
            continue
        break
    return count


class OverlyPermissiveTokenScopeRule:
    """GHA001: Detect overly permissive GITHUB_TOKEN permissions blocking principle of least privilege."""

    id = "GHA001"
    name = "Overly Permissive GITHUB_TOKEN Scope"
    description = "Detects workflows that use permissions: write-all/read-all for GITHUB_TOKEN."
    severity = "critical"
    confidence = 0.95
    category = "ci.config.github_actions"
    tags = ["permissions", "github-actions", "security-misconfiguration"]
    precedence = 65

    _pattern = re.compile(r"\b(?:write-all|read-all)\b", re.IGNORECASE)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_gha_workflow(str(path)):
            return []

        key_value = get_yaml_key_value(text, "permissions")
        if not key_value:
            return []

        value, line_num = key_value
        if self._pattern.search(value):
            return [
                Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=line_num,
                    severity=self.severity,
                    excerpt=f"permissions: {value}",
                    confidence=self.confidence,
                    category=self.category,
                    tags=self.tags,
                    rule_precedence=self.precedence,
                )
            ]

        return []


class InsecureOutputParameterUsageRule:
    """GHA002: Detects deprecated ::set-output usage inside run blocks."""

    id = "GHA002"
    name = "Deprecated ::set-output Command Usage"
    description = "Flags ::set-output usage inside run blocks, replaced by $GITHUB_OUTPUT."
    severity = "high"
    confidence = 0.85
    category = "ci.vulnerability.github_actions"
    tags = ["deprecated", "command-injection", "github-actions"]
    precedence = 65

    _command_pattern = re.compile(r"::set-output\s+name=", re.IGNORECASE)
    _run_line_pattern = re.compile(r"^-?\s*run\s*:", re.IGNORECASE)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_gha_workflow(str(path)):
            return []

        findings: List[Finding] = []
        in_run_block = False
        run_block_indent: Optional[int] = None
        leading_blanks = _leading_blank_line_count(text)

        for idx, raw_line in enumerate(text.splitlines()):
            line_num = max(1, idx + 1 - leading_blanks)
            stripped = raw_line.strip()
            indent = len(raw_line) - len(raw_line.lstrip(" "))

            is_run_line = bool(self._run_line_pattern.match(stripped))
            if is_run_line:
                in_run_block = True
                run_block_indent = indent

            if self._command_pattern.search(stripped):
                if is_run_line or (
                    run_block_indent is not None and in_run_block and indent >= (run_block_indent or 0)
                ):
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            file_path=path,
                            line=line_num,
                            severity=self.severity,
                            excerpt=stripped,
                            confidence=self.confidence,
                            category=self.category,
                            tags=self.tags,
                            rule_precedence=self.precedence,
                        )
                    )

            if (
                in_run_block
                and stripped
                and run_block_indent is not None
                and indent <= run_block_indent
                and not is_run_line
            ):
                in_run_block = False
                run_block_indent = None

        return findings


rules: List[object] = [
    OverlyPermissiveTokenScopeRule(),
    InsecureOutputParameterUsageRule(),
]