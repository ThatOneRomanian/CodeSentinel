CodeSentinel Phase 2 – AI Explainer Mode Specification
1. Overview

Phase 2 introduces AI-powered security explanations, CWE mapping, and remediation guidance built on top of the Phase 1 scanning engine.

The goal is to transform CodeSentinel from a static scanner into an intelligent security assistant.

Phase 2 does not modify scanning logic — instead, it enhances the findings generated in Phase 1 with LLM-powered metadata and explanations.

2. Core Features
2.1 AI Explanation Engine

For every finding:

Why it’s a risk (root-cause explanation)

How attackers might exploit it

Severity justification

Contextual risk information

Environment-specific warnings (Python, JS, cloud)

2.2 CWE Mapping

Each rule/finding linked to a CWE when applicable:

CWE ID

CWE name

CWE description in short form

Supporting references

2.3 Remediation Guidance

Concrete steps:

How to fix the issue

Safer alternatives

Code examples

Config recommendations

2.4 Structured Metadata Output

Extension of the JSON reporter to include:

"explanation": "...",
"cwe_id": "CWE-798",
"remediation": "Rotate leaked API key and restrict scope.",
"risk_score": 7.8,
"references": [
    "https://cwe.mitre.org/data/definitions/798.html"
]

2.5 CLI Enhancements

New flags:

codesentinel explain <path>
codesentinel scan <path> --ai
codesentinel scan <path> --explain
codesentinel scan <path> --explain --format json
codesentinel scan <path> --explain --llm deepseek

2.6 LLM Abstraction Layer

Support for:

DeepSeek

OpenAI

Anthropic

Local models (Ollama)

Using a provider interface:

class LLMProvider:
    def generate(self, prompt: str) -> str:
        ...


This abstracts LLM behavior from CLI logic.

3. Architectural Design
3.1 High-Level Workflow
FileWalker ──> RuleEngine ──> Findings ──> AI Explainer ──> Enhanced Findings ──> Reporters

3.2 New Component: sentinel/llm/explainer.py

Responsible for:

prompt construction

LLM calls

post-processing

output validation

error fallback

3.3 Prompt Templates

Stored in:
sentinel/llm/prompts/*.txt

Templates for:

explanation

remediation

CWE matching

severity justification

Supports variable interpolation:

{{excerpt}}
{{rule_id}}
{{severity}}
{{language}}

3.4 Caching Layer

To avoid paying or repeating inference:

.cache/explanations/
.cache/prompts/
.cache/cwe/

4. Data Structure Updates

Phase 2 fully activates the future-proofing fields you already added:

cwe_id

category

tags

remediation

language

Additions:

risk_score: float | None
Used for dashboards in Phase 3.

references: list[str] | None
Links to CWE pages or docs.

5. Performance Considerations

AI explanation mode is expensive.
Therefore:

Batching Strategy

Group findings by type

One LLM call per rule (optional mode)

Parallel Execution

Use Python concurrency for LLM calls

Fail-safe output

If LLM fails:

Produce minimal static explanation

Never break normal scanning

6. CLI Additions
New command:
codesentinel explain <path or report.json>

New flags:
--ai
--explain
--llm-provider <provider>
--llm-key <api key> (or env var)
--risk-score
--no-cwe
--no-remediation

Exit Codes:

0 → success

1 → findings but no fatal errors

2 → LLM integration error

3 → provider misconfiguration

7. Test Strategy
Unit Tests

Prompt construction

LLMProvider mocks

Caching interactions

Fallback logic

Integration Tests

Run scan → explanation mode → JSON output

Stress-test with sample_project

Validate format, not content

LLM Safety Tests

Ensure explanations never:

include hallucinated code

invent CVEs

produce insecure remediation

Performance Tests

Run on a medium repo

Ensure timeouts behave correctly

8. Security & Privacy Considerations

AI scanning introduces risks:

Never send full files

Only send excerpts (you already support this)

Allow user to disable network calls

For CI:

Only allow local LLM by default

Never send private keys or large secrets

9. Phase 2 Deliverables Summary
Deliverable 1: LLM Provider Interface
Deliverable 2: Prompt Templates
Deliverable 3: Explanation Engine
Deliverable 4: CWE Mapping
Deliverable 5: Remediation Engine
Deliverable 6: JSON Enhancements
Deliverable 7: CLI Enhancements
Deliverable 8: Test Coverage
Deliverable 9: Docs Update