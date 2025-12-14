# Phase 2.6 Gap Analysis (Cross-Repository Findings)

**Date:** 2025-12-01
**Analysis Scope:** Cross-referencing findings from six simulated repositories against the Phase 2.5 hardened rule engine (v0.2.0).

---

## 1. Uncovered Classification Gaps (token_types.py)

The current token classification in [`token_types.py`](src/sentinel/rules/token_types.py) is highly effective at identifying major cloud and generic secrets, leveraging a robust precedence model (100 for provider-specific, 70-90 for generic/OAuth/high-entropy).

However, the simulation revealed gaps in specialized domains:

| Gap Type | Example Repositories | Missing Classification | Impact/Precedence Need |
| :--- | :--- | :--- | :--- |
| **IaC Platform Secrets** | Terraform | HashiCorp Vault tokens, specific module source credentials. | Medium/High. Needs dedicated precedence score (e.g., 95) higher than generic OAuth. |
| **ML/Data Tokens** | PyTorch | Hugging Face API tokens (`hf_`), Weights & Biases keys (`wandb_`). | Medium. These are often high entropy but lack provider context, risking lower precedence (70). |
| **CI/CD References** | GitHub Actions | Specific reference patterns like `${{ secrets.MY_SECRET }}` (False Negative). | Critical. These are known secret patterns that must be identified even if the value is obscured. |
| **Framework Secrets** | NodeJS | Keys specific to certain ecosystem tools (e.g., Netlify, Vercel). | Medium. Often masked by generic high entropy detection, losing valuable context. |

## 2. Missing Rule Coverage Map (Functional Blindspots)

The Phase 2.5 engine is fundamentally a **Secrets and Basic Config Scanner**. Major functional categories are completely uncovered, leading to critical false negatives in modern repositories.

| Missing Category | Impacted Repositories | Severity Level of Missing Rules | Current Fallback |
| :--- | :--- | :--- | :--- |
| **Infrastructure-as-Code (IaC)** | Terraform, Docker-heavy | Critical (Exposed assets, RCE risk) | None (HCL files often missed entirely) |
| **Container Security** | Docker-heavy | Critical (Root execution, vulnerable base images) | None (Dockerfile syntax unparsed) |
| **Software Supply Chain** | NodeJS, PyTorch | Critical (Malicious scripts, vulnerable dependencies) | Basic generic file extension checks |
| **CI/CD Security** | GitHub Actions, PyTorch | High/Critical (Secret leakage, over-permissioning) | High entropy secrets (only if hardcoded) |
| **Framework Configuration** | Django, NodeJS | Medium (Insecure settings: DEBUG=True) | Basic generic config rules (low coverage) |

## 3. Regex Patterns Needing Hardening

The current pattern set for secrets is robust, leveraging provider prefixes and entropy analysis effectively. The hardening need is not primarily in existing secrets, but in implementing new, **context-aware** configuration detection.

| Current Regex Strength | Area for Improvement (Hardening) | Proposed Approach |
| :--- | :--- | :--- |
| **High Entropy / Prefix** | Excellent (AWS, Stripe, JWT are well-classified and precise). | Focus efforts on new, language/structure-specific rules. |
| **Generic Config Rules** | Currently weak, relies on string matching (e.g., `DEBUG=True`) which can be brittle across languages (Python vs. Bash vs. JSON). | **Hardening Focus:** Must switch from simple string/regex matching to **language-aware scanning** for configuration files to capture context and reduce noise. |
| **False Negative Handling** | Secret reference patterns (e.g., `process.env.MY_SECRET` or `${{ secrets.MY_TOKEN }}`) are currently false negatives unless the token value itself is present. | Requires look-behind/look-ahead checks for variable assignment names, not just values, for configuration files. |

## 4. Requirement for Language-Aware Rules

The transition from a Phase 2.5 general-purpose engine to a Phase 3 production tool hinges on the ability to understand structure.

| Language/Format | Required Structure Awareness | Misconfigurations Missed |
| :--- | :--- | :--- |
| **YAML (CI/CD)** | Key/value pair context, nested array parsing. | Over-permissioning (e.g., `permissions: write-all`), insecure `run` step commands. |
| **Dockerfile** | Instruction set (`FROM`, `RUN`, `ENV`, `USER`) context. | Running as root, unsafe `curl` commands, hardcoded `ENV` values. |
| **HCL (Terraform)** | Block structure (`resource`, `provider`, `variable`). | Public S3 buckets, hardcoded credentials in `provider` blocks. |
| **JSON/JS** | Dependency structure, script definitions (`package.json`). | Malicious `preinstall` scripts, vulnerable dependency ranges. |

**Conclusion:** Phase 2.7 development must prioritize dedicated, language/structure-aware rule packs for **GitHub Actions, Dockerfile, JS Supply Chain, and Terraform** to effectively close the functional blindspots identified by this validation phase.