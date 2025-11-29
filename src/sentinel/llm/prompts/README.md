# Prompt Templates

This directory contains prompt templates for CodeSentinel's AI Explainer Mode.

## Available Templates

- **explanation.txt** - Security risk analysis and explanation
- **remediation.txt** - Step-by-step fix instructions  
- **cwe_mapping.txt** - Common Weakness Enumeration mapping
- **severity_justification.txt** - Severity level rationale

## Template Variables

All templates support these variables:
- `{{rule_id}}` - The rule identifier
- `{{severity}}` - Finding severity level
- `{{file_path}}` - Path to the affected file
- `{{line}}` - Line number in the file
- `{{excerpt}}` - Code excerpt showing the issue
- `{{language}}` - Programming language detected

## Usage

Templates are loaded by the ExplanationEngine and populated with finding data before being sent to LLM providers.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.