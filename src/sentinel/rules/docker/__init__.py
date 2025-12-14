import re
import pathlib
from typing import List, Optional

from sentinel.rules.base import Finding
from sentinel.rules.token_types import classify_token, TokenType
from sentinel.utils.parsers import parse_dockerfile


def is_dockerfile(filepath: str) -> bool:
    """Return True if the path likely points to a Dockerfile."""
    return filepath.endswith("Dockerfile") or filepath.endswith("Dockerfile.build")


class RunningAsRootRule:
    """DOC001: Detect `USER root` only when it is the final user instruction."""

    id = "DOC001"
    name = "Running Container as Root (Last USER Root)"
    description = "Detects Dockerfiles that retain root as the final user."
    severity = "high"
    confidence = 0.90
    category = "container.config.security"
    tags = ["user", "root", "security-misconfiguration", "docker"]
    precedence = 65

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_dockerfile(str(path)):
            return []

        instructions = parse_dockerfile(text)
        last_user_line: Optional[int] = None
        last_user_was_root = False

        for instruction, arguments, line_num in instructions:
            if instruction == "USER":
                normalized = arguments.strip().lower()
                last_user_line = line_num
                last_user_was_root = normalized == "root"

        if last_user_line and last_user_was_root:
            return [
                Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=last_user_line,
                    severity=self.severity,
                    excerpt=f"USER root",
                    confidence=self.confidence,
                    category=self.category,
                    tags=self.tags,
                    rule_precedence=self.precedence,
                )
            ]

        return []


class HardcodedSecretsInENVRule:
    """DOC002: Detect hardcoded provider secrets embedded in ENV instructions."""

    id = "DOC002"
    name = "Hardcoded Secret in Docker ENV Instruction"
    description = "Detects high confidence provider secrets declared through ENV."
    severity = "critical"
    confidence = 0.95
    category = "container.secret.leakage"
    tags = ["env", "hardcoded-secret", "docker", "secret-leakage"]
    precedence = 65

    _secret_prefix_pattern = re.compile(
        r"((?:AKIA|ghp_|ya29|sk_live|pk_live)[A-Za-z0-9_/\+\-]{15,})", re.IGNORECASE
    )

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_dockerfile(str(path)):
            return []

        findings: List[Finding] = []
        instructions = parse_dockerfile(text)

        for instruction, arguments, line_num in instructions:
            if instruction != "ENV" or "=" not in arguments:
                continue

            candidate = arguments.split("=", 1)[1].strip().strip("\"'")
            match = self._secret_prefix_pattern.search(candidate)
            if not match:
                continue

            token_value = match.group(1)
            token_type = classify_token(token_value)
            if not token_type or token_type == TokenType.GENERIC_HIGH_ENTROPY:
                continue

            findings.append(
                Finding(
                    rule_id=self.id,
                    file_path=path,
                    line=line_num,
                    severity=self.severity,
                    excerpt=f"{instruction} {arguments}",
                    confidence=self.confidence,
                    category=self.category,
                    tags=self.tags + [token_type.name.lower()],
                    rule_precedence=self.precedence,
                )
            )

        return findings


rules: List[object] = [
    RunningAsRootRule(),
    HardcodedSecretsInENVRule(),
]