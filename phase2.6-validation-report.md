# Phase 2.6 Real-World Validation Report (Simulated)

**Date:** 2025-12-01
**Engine Version Validated:** v0.2.0 (Post Phase 2.5 Hardening)
**Objective:** Simulate analysis of diverse real-world repositories to detect remaining noise, blindspots, and rule gaps in the Phase 2.5 hardened engine.

---

## 1. Django Application Repository

**Focus:** Security settings, secrets, DB URLs (Python/INI/YAML/Env)

| Finding Category | Likely Findings | Collisions/Noise | Blindspots/False Negatives | Suggested Patch for 2.6 | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Secrets | `SECRET_KEY` (GENERIC_HIGH_ENTROPY), `DB_PASSWORD` (GENERIC_HIGH_ENTROPY) | Low; Deduplication precedence (70) should resolve collisions with generic config rules (60). | **Django-specific misconfigurations** (e.g., `DEBUG=True` in production, `ALLOWED_HOSTS=['*']`). Python framework-specific context is missing. | Introduce framework-aware rules for Python web frameworks (Django/Flask). | Medium |
| Config | Database connection strings (if complex) | Possible over-matching on common, non-secret configuration variables if entropy is high. | Lack of validation for secure database access methods and explicit password storage policies. | Refine regex patterns in `configs.py` to be more context-aware of Python settings files. | Low |

## 2. PyTorch ML Repository

**Focus:** Config files, CI workflows (YAML/Python/Env)

| Finding Category | Likely Findings | Collisions/Noise | Blindspots/False Negatives | Suggested Patch for 2.6 | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Secrets | Embedded AWS/GCP/etc. keys in config YAML or CI secrets. | None, due to strong provider classification precedence (100). | Model artifact repository keys, specific ML framework tokens (e.g., Hugging Face tokens) are missed. | Expand provider awareness to include common ML platform services. | Medium |
| CI/CD | Hardcoded secrets in shell commands within workflows. | Low; secrets are typically high entropy. | **Insecure CI/CD practices** (e.g., passing secrets through environment variables in logs, insecure caching). | Requires a dedicated CI/CD rule pack (Phase 2.7). | High |

## 3. NodeJS Web App Repository

**Focus:** .env, package.json, OAuth secrets (JS/JSON/Env)

| Finding Category | Likely Findings | Collisions/Noise | Blindspots/False Negatives | Suggested Patch for 2.6 | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Secrets | `API_KEY`, `JWT_TOKEN`, `CLIENT_SECRET` (OAUTH_TOKEN, JWT, GENERIC_HIGH_ENTROPY) | Low, especially for JWTs (precedence 95) and OAuth (precedence 90). | **NodeJS Supply Chain Risks** (e.g., `package.json` audit for malicious scripts (`preinstall`, `postinstall`) or known vulnerable dependencies by hash). | Requires a dedicated JS Supply Chain Rule Pack (Phase 2.7). | Critical |
| Config | Insecure CORS settings, vulnerable dependency version ranges (e.g., `*` or `~`) in `package.json`. | Potential collisions with generic config rules (60). | Configuration issues specific to JS frameworks (Express, Next.js). | Introduce rules for common `package.json` misconfigurations. | Medium |

## 4. Docker-Heavy Repository

**Focus:** Dockerfiles, entrypoints (Dockerfile/Shell)

| Finding Category | Likely Findings | Collisions/Noise | Blindspots/False Negatives | Suggested Patch for 2.6 | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Secrets | Hardcoded credentials in `ENV` instructions or `ADD/COPY` source paths. | Low, due to high entropy detection. | Secrets injected via `RUN --mount=type=secret` or `docker build --secret` that are *not* high entropy strings. | Implement language-aware scanning for Dockerfile syntax. | High |
| Config | None, current engine lacks Dockerfile configuration rules. | N/A | **All Dockerfile security misconfigurations** (e.g., `FROM latest`, `RUN apt update`, running as root (`USER root`), unnecessary package installation). | Requires a dedicated Dockerfile Rule Pack (Phase 2.7). | Critical |

## 5. GitHub Actions Workflow Repository

**Focus:** Workflow misconfigurations (YAML)

| Finding Category | Likely Findings | Collisions/Noise | Blindspots/False Negatives | Suggested Patch for 2.6 | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Secrets | Hardcoded secrets accidentally pasted into workflow steps. | Low. | **Insecure command usage** (`set-output`, `add-path`), over-permissioning via `permissions: write-all`, use of unverified external actions. Secrets referenced via `${{ secrets.MY_SECRET }}` are missed (False Negative). | Requires a dedicated GitHub Actions Rule Pack (Phase 2.7). | Critical |
| Config | Overly permissive environment configurations. | Possible conflict with generic YAML config rules (60) if present. | Lack of validation for required checks (e.g., explicit checkout of specific SHA). | Implement syntax-aware scanning for GH Actions YAML structure. | High |

## 6. Terraform Infrastructure-as-Code Repository

**Focus:** AWS keys, provider blocks, remote states (HCL/TF)

| Finding Category | Likely Findings | Collisions/Noise | Blindspots/False Negatives | Suggested Patch for 2.6 | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Secrets | Hardcoded AWS/GCP keys in `provider` blocks. | Low, due to provider classification precedence (100). | **Terraform-specific secrets** (e.g., HashiCorp Vault tokens, specific module source URLs with embedded credentials). | Expand token classification for dedicated IaC platform secrets. | High |
| Config | None, current engine lacks HCL configuration rules. | N/A | **All IaC misconfigurations** (e.g., public S3 bucket, unencrypted remote state, exposed security groups, hardcoded AWS keys *not* in secret format). | Requires a dedicated Terraform Rule Pack (Phase 2.7). | Critical |