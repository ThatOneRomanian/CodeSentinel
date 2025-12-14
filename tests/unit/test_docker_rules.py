import pathlib
import unittest
from typing import List

from sentinel.rules.docker import (
    RunningAsRootRule,
    HardcodedSecretsInENVRule,
    is_dockerfile,
)
from sentinel.rules.base import Finding


class TestDockerUtils(unittest.TestCase):
    def test_is_dockerfile_detection(self):
        self.assertTrue(is_dockerfile("Dockerfile"))
        self.assertTrue(is_dockerfile("path/to/Dockerfile"))
        self.assertTrue(is_dockerfile("Dockerfile.build"))
        self.assertFalse(is_dockerfile("docker-compose.yml"))
        self.assertFalse(is_dockerfile("dockerfile.txt"))


class TestDockerRulePack(unittest.TestCase):
    def setUp(self):
        self.repo_path = pathlib.Path("/tmp/test-repo")
        self.dockerfile_path = self.repo_path / "Dockerfile"
        self.non_dockerfile_path = self.repo_path / "build.txt"
        self.maxDiff = None

    def assertFindingsMatch(self, findings: List[Finding], expected_lines: List[int], rule_id: str):
        self.assertEqual(len(findings), len(expected_lines), f"Expected {len(expected_lines)} findings, got {len(findings)}")
        actual_lines = [f.line for f in findings]
        self.assertListEqual(sorted(actual_lines), sorted(expected_lines))
        for finding in findings:
            self.assertEqual(finding.rule_id, rule_id)
            self.assertEqual(finding.rule_precedence, 65)

    def test_doc001_running_as_root_detection(self):
        rule = RunningAsRootRule()

        # Test 1: Root replaced by non-root later (should not flag)
        content_1 = "FROM alpine\nUSER root\nRUN apk add nginx\nUSER appuser"
        findings_1 = rule.apply(self.dockerfile_path, content_1)
        self.assertFindingsMatch(findings_1, [], "DOC001")

        # Test 2: Root remains final USER (should flag)
        content_2 = "FROM base\nUSER root\nRUN echo hello"
        findings_2 = rule.apply(self.dockerfile_path, content_2)
        self.assertFindingsMatch(findings_2, [2], "DOC001")

        # Test 3: Lowercase root and no subsequent USER
        content_3 = "FROM base\nUSER Root\n"
        findings_3 = rule.apply(self.dockerfile_path, content_3)
        self.assertFindingsMatch(findings_3, [2], "DOC001")

        # Test 4: Safe user instruction later in file (should not flag)
        content_4 = "FROM base\nUSER nonroot\n"
        findings_4 = rule.apply(self.dockerfile_path, content_4)
        self.assertFindingsMatch(findings_4, [], "DOC001")

        # Test 5: File filtering
        findings_5 = rule.apply(self.non_dockerfile_path, content_2)
        self.assertFindingsMatch(findings_5, [], "DOC001")

    def test_doc002_hardcoded_secret_in_env(self):
        rule = HardcodedSecretsInENVRule()

        # Test 1: AWS live key (should fire)
        content_1 = "FROM base\nENV AWS_SECRET=sk_live_1234567890abcdefghijklmnopqrstuvwx\nRUN echo hello"
        findings_1 = rule.apply(self.dockerfile_path, content_1)
        self.assertFindingsMatch(findings_1, [2], "DOC002")

        # Test 2: AWS Access Key ID (should fire)
        content_2 = "FROM base\nARG VERSION\nENV AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE\n"
        findings_2 = rule.apply(self.dockerfile_path, content_2)
        self.assertFindingsMatch(findings_2, [3], "DOC002")

        # Test 3: Non-secret high entropy (should not fire)
        content_3 = "FROM base\nENV RANDOM_HASH=zxcvbnmasdfghjklqwertyuiop1234567890zxcvbnm"
        findings_3 = rule.apply(self.dockerfile_path, content_3)
        self.assertFindingsMatch(findings_3, [], "DOC002")

        # Test 4: Empty ENV (should not fire)
        content_4 = "FROM base\nENV BUILD_VERSION=1.0.0"
        findings_4 = rule.apply(self.dockerfile_path, content_4)
        self.assertFindingsMatch(findings_4, [], "DOC002")

        # Test 5: Multiple secrets on different lines
        content_5 = "FROM base\nENV KEY1=sk_live_1234567890abcdefghijklmnopqrstuvwx\nENV KEY2=AKIAIOSFODNN7EXAMPLE"
        findings_5 = rule.apply(self.dockerfile_path, content_5)
        self.assertFindingsMatch(findings_5, [2, 3], "DOC002")

        # Test 6: Secret with different instruction (should not fire)
        content_6 = "FROM base\nARG SECRET=sk_live_1234567890abcdefghijklmnopqrstuvwx"
        findings_6 = rule.apply(self.dockerfile_path, content_6)
        self.assertFindingsMatch(findings_6, [], "DOC002")