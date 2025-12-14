import re
import pathlib
from typing import List

from sentinel.rules.base import Finding
from sentinel.utils.parsers import find_hcl_blocks


def is_terraform_file(filepath: str) -> bool:
    """Return True if the path points to an HCL/Terraform file."""
    return filepath.endswith(".tf") or filepath.endswith(".tfvars") or filepath.endswith(".hcl")


class PubliclyExposedS3BucketRule:
    """TFC001: Detects aws_s3_bucket resources missing private ACL or enforcing public ACL."""

    id = "TFC001"
    name = "AWS S3 Bucket Lacks Private ACL"
    description = "Flags aws_s3_bucket resources that omit private/bucket-owner ACLs."
    severity = "high"
    confidence = 0.95
    category = "iac.config.aws"
    tags = ["terraform", "aws", "s3", "public-exposure"]
    precedence = 65

    ACL_PATTERN = re.compile(r'acl\s*=\s*"(private|bucket-owner-full-control)"', re.IGNORECASE)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_terraform_file(str(path)):
            return []

        findings: List[Finding] = []
        s3_blocks = find_hcl_blocks(text, block_type="resource", block_name="aws_s3_bucket")
        for block_content, line_num in s3_blocks:
            match = self.ACL_PATTERN.search(block_content)
            if not match:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        file_path=path,
                        line=line_num,
                        severity=self.severity,
                        excerpt=block_content.splitlines()[0] + " { ... }",
                        confidence=self.confidence,
                        category=self.category,
                        tags=self.tags,
                        rule_precedence=self.precedence,
                    )
                )
        return findings


class UnencryptedRemoteStateStorageRule:
    """TFC002: Detects S3 backend remote state configuration missing server-side encryption."""

    id = "TFC002"
    name = "Unencrypted Remote State Storage (S3 Backend)"
    description = "Flags terraform backend \"s3\" configs that omit encrypt = true."
    severity = "critical"
    confidence = 0.98
    category = "iac.config.terraform"
    tags = ["terraform", "s3", "state", "encryption", "critical"]
    precedence = 65

    ENCRYPT_PATTERN = re.compile(r'encrypt\s*=\s*true', re.IGNORECASE)
    BACKEND_S3_PATTERN = re.compile(r'backend\s+"s3"', re.IGNORECASE)
    ENCRYPT_FALSE_PATTERN = re.compile(r'encrypt\s*=\s*false', re.IGNORECASE)

    def apply(self, path: pathlib.Path, text: str) -> List[Finding]:
        if not is_terraform_file(str(path)):
            return []

        findings: List[Finding] = []
        backend_blocks = find_hcl_blocks(text, block_type="backend")
        for block_content, line_num in backend_blocks:
            if not self.BACKEND_S3_PATTERN.search(block_content):
                continue

            if not self.ENCRYPT_PATTERN.search(block_content) or self.ENCRYPT_FALSE_PATTERN.search(block_content):
                findings.append(
                    Finding(
                        rule_id=self.id,
                        file_path=path,
                        line=line_num,
                        severity=self.severity,
                        excerpt=block_content.splitlines()[0] + " { ... }",
                        confidence=self.confidence,
                        category=self.category,
                        tags=self.tags,
                        rule_precedence=self.precedence,
                    )
                )
        return findings


rules: List[object] = [
    PubliclyExposedS3BucketRule(),
    UnencryptedRemoteStateStorageRule(),
]