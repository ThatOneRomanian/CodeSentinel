# Phase 2.7 Rule Pack Design Specification

**Date:** 2025-12-01
**Goal:** Design detailed specifications for four new rule packs targeting critical security blindspots in DevOps, Infrastructure-as-Code (IaC), and Software Supply Chain (SSC) domains, as identified in Phase 2.6 Validation.
**Target Precedence:** 65 (Specialized Misconfiguration - above generic config 60, below generic high-entropy secret 70).
**Rule Location Scaffolding:**
* GitHub Actions: [`src/sentinel/rules/gh_actions/`](src/sentinel/rules/gh_actions/__init__.py)
* Dockerfile: [`src/sentinel/rules/docker/`](src/sentinel/rules/docker/__init__.py)
* JS Supply Chain: [`src/sentinel/rules/js_supply_chain/`](src/sentinel/rules/js_supply_chain/__init__.py)
* Terraform: New directory planned for IaC/HCL rules.

---

## 1. GitHub Actions Security (GHA Rule Pack)

**Focus:** Insecure workflow configurations, token over-permissioning, and command injection vulnerabilities.

| Field | GHA001: Overly Permissive Token Scope |
| :--- | :--- |
| **ID** | GHA001 |
| **Description** | Detects overly broad `permissions: write-all` setting in GitHub Actions workflows, granting excessive privileges to the GITHUB_TOKEN. |
| **Detection Strategy** | YAML structure analysis for the top-level `permissions` key. |
| **Severity** | Critical |
| **Sample Regex** | `^permissions:\s*(?:read-all|write-all)\s*$` |
| **Mitigation Notes** | Restrict to files matching `*.yml` or `*.yaml` within the `.github/workflows/` directory. Ignore if context suggests required repository setup action. |
| **Dedup Precedence** | 65 |

| Field | GHA002: Insecure Output Parameter Usage |
| :--- | :--- |
| **ID** | GHA002 |
| **Description** | Detects use of deprecated and insecure `::set-output` command, vulnerable to injection attacks via untrusted user input or environment variables. |
| **Detection Strategy** | String matching within `run` blocks for the deprecated syntax. |
| **Severity** | High |
| **Sample Regex** | `::set-output\s+name=` |
| **Mitigation Notes** | Restrict to `run:` blocks within GitHub Actions workflows. Suggest migration to environment file approach (`$GITHUB_OUTPUT`). |
| **Dedup Precedence** | 65 |

---

## 2. Dockerfile Security (DOC Rule Pack)

**Focus:** Base image vulnerabilities, root execution, and secret leakage during image build.

| Field | DOC001: Running as Root (Explicit) |
| :--- | :--- |
| **ID** | DOC001 |
| **Description** | Detects explicit use of `USER root` command, which bypasses modern container security best practices. |
| **Detection Strategy** | Line-by-line inspection for the `USER` instruction keyword. |
| **Severity** | High |
| **Sample Regex** | `^\s*USER\s+root\s*$` |
| **Mitigation Notes** | Flag only if `USER root` is the last executed `USER` command or if `USER` is never specified. Restrict to files named `Dockerfile`. |
| **Dedup Precedence** | 65 |

| Field | DOC002: Hardcoded Secrets in ENV |
| :--- | :--- |
| **ID** | DOC002 |
| **Description** | Detects hardcoded high-entropy secrets or API keys assigned directly within an `ENV` instruction in a Dockerfile. |
| **Detection Strategy** | Combined check: `ENV` instruction keyword + high entropy/prefix pattern detection. |
| **Severity** | Critical |
| **Sample Regex** | `^\s*ENV\s+[A-Z_]+=\s*(AKIA|ghp_|ya29|sk_live|pk_live)[A-Za-z0-9_-]{20,}\s*$` |
| **Mitigation Notes** | Deduplication precedence must be 100 for secret value, 65 for the misconfiguration context. Requires high entropy validation. |
| **Dedup Precedence** | 100 (Secret Detection) / 65 (Configuration Context) |

---

## 3. JavaScript Supply Chain (JSC Rule Pack)

**Focus:** Malicious package scripts, insecure dependency definitions, and sensitive file contents.

| Field | JSC001: Malicious Package Script Hooks |
| :--- | :--- |
| **ID** | JSC001 |
| **Description** | Flags high-risk scripts defined in `package.json` that run automatically (e.g., `preinstall`, `postinstall`, `prepare`). |
| **Detection Strategy** | JSON field parsing for `scripts` object keys. Analysis of script value for known malicious commands. |
| **Severity** | Critical |
| **Sample Regex** | `"(preinstall|postinstall|prepare)"\s*:\s*".*?(curl|wget|nc|chmod|exec|sh)\s+.*"` |
| **Mitigation Notes** | Must restrict to `package.json` files. False positive mitigation: maintain an allow-list of known benign scripts (e.g., simple `echo` commands). |
| **Dedup Precedence** | 65 |

| Field | JSC002: Wildcard Dependency Version |
| :--- | :--- |
| **ID** | JSC002 |
| **Description** | Detects dependencies specified with wildcard versions (`*`) or highly permissive ranges, increasing the risk of pulling vulnerable or malicious packages. |
| **Detection Strategy** | JSON field parsing within `dependencies` and `devDependencies` for version strings containing `*` or ranges beyond acceptable boundaries. |
| **Severity** | Medium |
| **Sample Regex** | `"(dependencies|devDependencies)"\s*:\s*\{[^}]*?"[a-zA-Z0-9_-]+?"\s*:\s*"\*"` |
| **Mitigation Notes** | Restrict to `package.json` files. Ignore internal/local package references if possible. |
| **Dedup Precedence** | 65 |

---

## 4. Terraform Security (TFC Rule Pack)

**Focus:** IaC misconfigurations leading to exposed cloud resources, unencrypted state, and hardcoded credentials.

| Field | TFC001: Publicly Exposed S3 Bucket |
| :--- | :--- |
| **ID** | TFC001 |
| **Description** | Detects `aws_s3_bucket` resources missing mandatory access control blocks (`acl = "private"`), potentially exposing data. |
| **Detection Strategy** | HCL block structure analysis (`resource "aws_s3_bucket"` block) for absence of required private access rules. |
| **Severity** | High |
| **Sample Regex** | `resource\s+"aws_s3_bucket"\s+".*?"\s*\{(?:.|\n)*?(?<!acl\s*=\s*"private")(?:.|\n)*?\}$` (Conceptual: focuses on block content) |
| **Mitigation Notes** | Must be restricted to `.tf`, `.tfvars`, or `.hcl` files. Requires robust parser implementation to accurately handle nested blocks and conditional logic. |
| **Dedup Precedence** | 65 |

| Field | TFC002: Unencrypted Remote State Storage |
| :--- | :--- |
| **ID** | TFC002 |
| **Description** | Detects Terraform remote state configuration (`backend "s3"`) that does not enforce server-side encryption. |
| **Detection Strategy** | HCL block structure analysis (`terraform {}` block, `backend "s3"`) for absence of `encrypt = true`. |
| **Severity** | Critical |
| **Sample Regex** | `backend\s+"s3"\s*\{(?:.|\n)*?(?<!encrypt\s*=\s*true)(?:.|\n)*?\}$` (Conceptual: focuses on block content) |
| **Mitigation Notes** | Strict file type restriction. High confidence finding if `encrypt` field is absent or set to `false`. |
| **Dedup Precedence** | 65 |