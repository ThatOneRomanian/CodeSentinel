# Security Policy

## Reporting Security Vulnerabilities

We take the security of CodeSentinel seriously. If you believe you have found a security vulnerability in CodeSentinel, we encourage you to report it to us responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report a Security Issue

To report a security vulnerability, please email us directly at:

**Email:** [security@codesentinel.dev](mailto:security@codesentinel.dev)

If this email address is not available, you can contact the project maintainer directly:

**Maintainer:** Andrei Antonescu  
**Contact:** Please create a private GitHub issue or reach out through GitHub's private vulnerability reporting feature.

### What to Include in Your Report

To help us understand and resolve the issue quickly, please include as much of the following information as possible:

- **Type of issue** (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- **Full paths of source file(s) related to the manifestation of the issue**
- **The location of the affected source code** (tag/branch/commit or direct URL)
- **Any special configuration required to reproduce the issue**
- **Step-by-step instructions to reproduce the issue**
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the issue**, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### Response Timeline

We will acknowledge receipt of your vulnerability report within **48 hours** and will send a more detailed response within **7 days** indicating the next steps in handling your report.

After the initial reply to your report, we will:

- Confirm the problem and determine the affected versions
- Audit code to find any potential similar problems
- Prepare fixes for all supported releases
- Release patched versions as soon as possible

We will keep you informed of our progress throughout the process.

### Disclosure Policy

- We ask that you give us a reasonable amount of time to fix the issue before any disclosure to the public or a third party
- We will credit you in our security advisory (unless you prefer to remain anonymous)
- We will coordinate the disclosure timeline with you

### Security Update Process

When we receive a security bug report, we will:

1. **Confirm the vulnerability** and determine affected versions
2. **Develop and test fixes** for all supported versions
3. **Prepare security advisories** for publication
4. **Release patched versions** and publish security advisories
5. **Update this security policy** if necessary

### Scope of Security Concerns

Given that CodeSentinel is a security scanning tool, we are particularly interested in vulnerabilities that could:

#### High Priority Security Issues

- **Code injection vulnerabilities** that could allow malicious code execution during scanning
- **Path traversal vulnerabilities** that could allow access to files outside the intended scan scope
- **Privilege escalation** issues that could allow unauthorized access to system resources
- **Information disclosure** vulnerabilities that could expose sensitive data from scanned files
- **AI/LLM prompt injection** vulnerabilities that could manipulate AI explanations or expose sensitive data
- **Dependency vulnerabilities** in third-party libraries that could compromise security
- **Configuration vulnerabilities** that could lead to insecure default behavior

#### Medium Priority Security Issues

- **Denial of service** vulnerabilities that could crash or hang the scanner
- **Memory safety issues** that could lead to crashes or undefined behavior
- **Input validation issues** that could cause unexpected behavior with malformed files
- **Logging vulnerabilities** that could expose sensitive information in logs

#### Lower Priority Issues

- **Performance issues** that significantly impact scanning speed
- **Usability issues** that could lead to security misconfigurations
- **Documentation issues** that could lead to insecure usage patterns

### Security Best Practices for Users

While using CodeSentinel, we recommend:

- **Keep CodeSentinel updated** to the latest version
- **Review scan results carefully** before acting on them
- **Use appropriate file permissions** when running scans
- **Be cautious with AI features** and avoid scanning files with sensitive data when using external LLM providers
- **Validate findings** independently, especially for critical security decisions
- **Use version control** to track changes made based on scan results

### Security Features in CodeSentinel

CodeSentinel includes several security features designed to protect users:

- **Local-first scanning** - No mandatory cloud dependencies
- **Input sanitization** - Protection against malicious file content
- **AI safety layer** - Protection against prompt injection and data exposure when using LLM features
- **Configurable ignore patterns** - Ability to exclude sensitive files from scanning