import pathlib
import unittest
from typing import List

from sentinel.rules.terraform import (
    PubliclyExposedS3BucketRule,
    UnencryptedRemoteStateStorageRule,
    is_terraform_file,
)
from sentinel.rules.base import Finding


class TestTerraformUtils(unittest.TestCase):
    def test_is_terraform_file_detection(self):
        self.assertTrue(is_terraform_file("main.tf"))
        self.assertTrue(is_terraform_file("variables.tfvars"))
        self.assertTrue(is_terraform_file("config.hcl"))
        self.assertFalse(is_terraform_file("main.tfx"))


class TestTerraformRulePack(unittest.TestCase):
    def setUp(self):
        self.repo_path = pathlib.Path("/tmp/test-repo")
        self.tf_path = self.repo_path / "main.tf"
        self.non_tf_path = self.repo_path / "config.json"
        self.maxDiff = None

    def assertFindingsMatch(self, findings: List[Finding], expected_lines: List[int], rule_id: str):
        self.assertEqual(len(findings), len(expected_lines), f"Expected {len(expected_lines)} findings, got {len(findings)}")
        actual_lines = [f.line for f in findings]
        self.assertListEqual(sorted(actual_lines), sorted(expected_lines))
        for finding in findings:
            self.assertEqual(finding.rule_id, rule_id)
            self.assertEqual(finding.rule_precedence, 65)

    def test_tfc001_exposed_s3_bucket(self):
        rule = PubliclyExposedS3BucketRule()

        content_1 = """
resource "aws_s3_bucket" "bad_bucket" {
  bucket = "my-public-bucket"
  versioning { enabled = true }
}
"""
        findings_1 = rule.apply(self.tf_path, content_1)
        self.assertFindingsMatch(findings_1, [2], "TFC001")

        content_2 = """
resource "aws_s3_bucket" "another_bad_bucket" {
  bucket = "another-public-bucket"
  acl = "public-read"
}
"""
        findings_2 = rule.apply(self.tf_path, content_2)
        self.assertFindingsMatch(findings_2, [2], "TFC001")

        content_3 = """
resource "aws_s3_bucket" "safe_bucket" {
  bucket = "my-private-bucket"
  acl = "private"
}
"""
        findings_3 = rule.apply(self.tf_path, content_3)
        self.assertFindingsMatch(findings_3, [], "TFC001")

        findings_4 = rule.apply(self.non_tf_path, content_2)
        self.assertFindingsMatch(findings_4, [], "TFC001")

    def test_tfc002_unencrypted_remote_state(self):
        rule = UnencryptedRemoteStateStorageRule()

        content_1 = """
terraform {
  backend "s3" {
    bucket = "my-state-bucket"
    region = "us-east-1"
  }
}
"""
        findings_1 = rule.apply(self.tf_path, content_1)
        self.assertFindingsMatch(findings_1, [3], "TFC002")

        content_2 = """
terraform {
  backend "s3" {
    bucket = "my-state-bucket"
    encrypt = true
  }
}
"""
        findings_2 = rule.apply(self.tf_path, content_2)
        self.assertFindingsMatch(findings_2, [], "TFC002")

        content_3 = """
terraform {
  backend "s3" {
    bucket = "my-state-bucket"
    encrypt = false
  }
}
"""
        findings_3 = rule.apply(self.tf_path, content_3)
        self.assertFindingsMatch(findings_3, [3], "TFC002")

        findings_4 = rule.apply(self.non_tf_path, content_1)
        self.assertFindingsMatch(findings_4, [], "TFC002")