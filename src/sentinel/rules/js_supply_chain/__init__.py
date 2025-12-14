import re
import pathlib
from typing import Dict, List, Optional, Tuple

from sentinel.rules.base import Finding
from sentinel.utils.parsers import parse_json


def is_package_json(filepath: str) -> bool:
    """Return True if path ends with package.json."""
    return filepath.endswith("package.json")


class MaliciousPackageScriptHooksRule:
    """JSC001: Detects risky scripts executing in lifecycle hooks."""

    id = "JSC001"
    name = "Malicious Package Script Hook Detection"
    description = (
        "Flags lifecycle scripts (preinstall/postinstall/prepare/install) invoking "
        "network or execution commands."
    )
    severity = "critical"
    confidence = 0.90
    category = "supply_chain.package.scripts"
    tags = ["npm", "scripts", "preinstall", "postinstall", "malware"]
    precedence = 65

    HOOK_SCRIPTS = {"preinstall", "postinstall", "prepare", "install"}
    MALICIOUS_COMMANDS = re.compile(r"(curl|wget|nc|chmod|exec|sh|bash|python|node)\s+", re.IGNORECASE)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_package_json(str(path)):
            return []

        package_data = parse_json(text)
        if not package_data or "scripts" not in package_data:
            return []

        scripts: Dict[str, str] = package_data["scripts"]
        for script, body in scripts.items():
            if script in self.HOOK_SCRIPTS and self.MALICIOUS_COMMANDS.search(body):
                return [
                    Finding(
                        rule_id=self.id,
                        file_path=path,
                        line=1,
                        severity=self.severity,
                        excerpt=f'"{script}": "{body}"',
                        confidence=self.confidence,
                        category=self.category,
                        tags=self.tags,
                        rule_precedence=self.precedence,
                    )
                ]
        return []


class WildcardDependencyVersionRule:
    """JSC002: Detects wildcard or empty dependency versions."""

    id = "JSC002"
    name = "Wildcard Dependency Version Usage"
    description = "Flags dependency versions using '*' or empty strings."
    severity = "medium"
    confidence = 0.70
    category = "supply_chain.package.dependencies"
    tags = ["npm", "dependency", "wildcard", "version-pinning"]
    precedence = 65

    DEP_SECTIONS = ["dependencies", "devDependencies", "optionalDependencies"]

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_package_json(str(path)):
            return []

        package_data = parse_json(text)
        if not package_data:
            return []

        findings: List[Finding] = []
        for section in self.DEP_SECTIONS:
            section_data = package_data.get(section)
            if isinstance(section_data, dict):
                for dependency, version in section_data.items():
                    if isinstance(version, str) and (version.strip() == "" or "*" in version):
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                file_path=path,
                                line=1,
                                severity=self.severity,
                                excerpt=f'"{dependency}": "{version}" in "{section}"',
                                confidence=self.confidence,
                                category=self.category,
                                tags=self.tags + [section],
                                rule_precedence=self.precedence,
                            )
                        )
        return findings


rules: List[object] = [
    MaliciousPackageScriptHooksRule(),
    WildcardDependencyVersionRule(),
]