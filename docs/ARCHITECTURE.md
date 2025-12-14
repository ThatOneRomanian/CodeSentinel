# CodeSentinel Architecture

## Overview
CodeSentinel is a comprehensive security scanning and analysis tool that helps developers identify and mitigate vulnerabilities in their projects. It utilizes a rule-based engine to detect a wide range of security issues, from misconfigured infrastructure to vulnerable dependencies.

## Phase 2.7 Updates

### New Structure-Aware Rule Packs
As part of Phase 2.7, the following new structure-aware rule packs have been added to CodeSentinel:

1. **GitHub Actions YAML Security Rules**
   - Implements rules to detect common security misconfigurations in GitHub Actions YAML files.
   - Uses a lightweight YAML parser to analyze the structure and content of the YAML files.
   - Assigns a "Specialized Misconfiguration" precedence level (65) to these rules.

2. **Dockerfile Security Rules**
   - Implements rules to identify security issues and best practices in Dockerfiles.
   - Utilizes a minimal custom parser to parse the Dockerfile structure and content.
   - Also assigns a "Specialized Misconfiguration" precedence level (65) to these rules.

3. **NodeJS Supply Chain Rules**
   - Detects security vulnerabilities and misconfigurations in NodeJS projects, focusing on the supply chain.
   - Analyzes package.json files using a JSON parser to identify issues with dependencies, scripts, and other configuration.
   - Precedence level for these rules is also set to "Specialized Misconfiguration" (65).

4. **Terraform IaC Misconfiguration Rules**
   - Implements rules to identify security and compliance issues in Terraform Infrastructure as Code (IaC) configurations.
   - Uses a lightweight HCL parser to parse the Terraform configuration structure and content.
   - Assigns the "Specialized Misconfiguration" precedence level (65) to these rules as well.

These new rule packs have been seamlessly integrated into the existing CodeSentinel rule engine, ensuring full backward compatibility and zero changes to the Phase 3 API.

## Ongoing Maintenance and Improvements
The CodeSentinel team is committed to continuously improving the tool and expanding its capabilities. Future phases will focus on enhancing the rule engine, improving the user experience, and integrating with additional security tools and services.