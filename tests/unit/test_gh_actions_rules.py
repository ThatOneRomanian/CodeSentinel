import pathlib
import unittest
from typing import List

from sentinel.rules.gh_actions import (
    OverlyPermissiveTokenScopeRule, 
    InsecureOutputParameterUsageRule, 
    is_gha_workflow
)
from sentinel.rules.base import Finding

class TestGHAUtils(unittest.TestCase):
    def test_is_gha_workflow_detection(self):
        self.assertTrue(is_gha_workflow(".github/workflows/main.yml"))
        self.assertTrue(is_gha_workflow("/repo/path/.github/workflows/build.yaml"))
        self.assertFalse(is_gha_workflow("src/app.py"))
        self.assertFalse(is_gha_workflow(".github/config.yml")) # Not in workflows dir
        self.assertFalse(is_gha_workflow(".github/workflows/config.txt"))

class TestGHARulePack(unittest.TestCase):
    def setUp(self):
        self.repo_path = pathlib.Path("/tmp/test-repo")
        self.workflow_path = self.repo_path / ".github/workflows/build.yml"
        self.non_workflow_path = self.repo_path / "deployment.yaml"
        self.maxDiff = None

    def assertFindingsMatch(self, findings: List[Finding], expected_lines: List[int], rule_id: str):
        self.assertEqual(len(findings), len(expected_lines))
        actual_lines = [f.line for f in findings]
        self.assertListEqual(sorted(actual_lines), sorted(expected_lines))
        for finding in findings:
            self.assertEqual(finding.rule_id, rule_id)
            self.assertEqual(finding.category, "ci.config.github_actions" if rule_id == "GHA001" else "ci.vulnerability.github_actions")
            self.assertEqual(finding.confidence, 0.95 if rule_id == "GHA001" else 0.85)

    def test_gha001_permissive_scope_detection(self):
        rule = OverlyPermissiveTokenScopeRule()
        
        # Test 1: write-all permission
        content_1 = "name: Build\non: push\npermissions: write-all\njobs:\n  build:"
        findings_1 = rule.apply(self.workflow_path, content_1)
        self.assertFindingsMatch(findings_1, [3], "GHA001")

        # Test 2: read-all permission
        content_2 = "name: Test\npermissions: read-all\njobs:\n  test:"
        findings_2 = rule.apply(self.workflow_path, content_2)
        self.assertFindingsMatch(findings_2, [2], "GHA001")
        
        # Test 3: Specific permissions (should pass)
        content_3 = "name: Deploy\npermissions:\n  contents: read\n  pull-requests: write"
        findings_3 = rule.apply(self.workflow_path, content_3)
        self.assertFindingsMatch(findings_3, [], "GHA001")

        # Test 4: Nested permissions (our simple parser might miss, but should pass top-level check)
        content_4 = "name: Test\njobs:\n  build:\n    permissions: write-all\n    steps:"
        findings_4 = rule.apply(self.workflow_path, content_4)
        self.assertFindingsMatch(findings_4, [], "GHA001")
        
    def test_gha001_file_filtering(self):
        rule = OverlyPermissiveTokenScopeRule()
        content = "permissions: write-all"
        
        # Should not fire on non-workflow file
        findings = rule.apply(self.non_workflow_path, content)
        self.assertEqual(len(findings), 0)

    def test_gha002_insecure_output_detection(self):
        rule = InsecureOutputParameterUsageRule()
        
        content_1 = """
jobs:
  build:
    steps:
    - name: Set output
      run: echo "::set-output name=result::value"
    - name: Run another command
      run: echo "safe command"
    - run: echo "::set-output name=flag::true"
"""
        findings_1 = rule.apply(self.workflow_path, content_1)
        self.assertFindingsMatch(findings_1, [5, 8], "GHA002")

        content_2 = """
jobs:
  build:
    steps:
    - name: Safe way
      run: echo "result=value" >> $GITHUB_OUTPUT
"""
        findings_2 = rule.apply(self.workflow_path, content_2)
        self.assertFindingsMatch(findings_2, [], "GHA002")
        
        content_3 = "run: ::set-output name=token::SECRET"
        findings_3 = rule.apply(self.workflow_path, content_3)
        self.assertFindingsMatch(findings_3, [1], "GHA002")
        
    def test_gha002_file_filtering(self):
        rule = InsecureOutputParameterUsageRule()
        content = "echo ::set-output name=result::value"
        
        # Should not fire on non-workflow file
        findings = rule.apply(self.non_workflow_path, content)
        self.assertEqual(len(findings), 0)