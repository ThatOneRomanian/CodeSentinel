# CodeSentinel v0.2.0 Dogfooding Experiment Plan

## Experiment Overview

**Objective**: Validate CodeSentinel v0.2.0 performance, noise level, and usefulness on real-world repositories before Phase 3 GUI development.

**Time Constraint**: 1-2 evenings of testing  
**Scope**: 3-5 real-world repositories  
**Focus Areas**: Performance, noise level, overall usefulness

## Test Repository Selection

### Recommended Test Repositories
1. **Small Project** (1-10 files): [`sample-project/`](sample-project/) - Already available for baseline testing
2. **Medium Python Project**: Flask/Django application (500-2000 files)
3. **JavaScript/Node.js Project**: Express/React application (1000-3000 files)  
4. **Mixed Language Project**: Python + JavaScript + Config files (2000-5000 files)
5. **Large Monorepo** (Optional): 5000+ files for performance stress testing

### Repository Acquisition Strategy
- Clone popular open-source projects from GitHub
- Use personal/work projects with permission
- Ensure variety in file types and complexity

## Experiment Methodology

### Test Matrix
Each repository will be tested with 4 scan configurations:

1. **Baseline Scan**: `codesentinel scan <path> --format markdown`
2. **JSON Output**: `codesentinel scan <path> --format json` 
3. **AI Mode (Placeholder)**: `codesentinel scan <path> --ai --format markdown`
4. **AI Mode (Real)**: `codesentinel scan <path> --ai --llm-provider deepseek --format markdown` (if DEEPSEEK_API_KEY available)

## Exact CLI Commands

### Core Commands for Each Repository
```bash
# 1. Baseline performance test
time codesentinel scan /path/to/repo --format markdown

# 2. JSON output for machine processing  
time codesentinel scan /path/to/repo --format json

# 3. AI mode with placeholder explanations
time codesentinel scan /path/to/repo --ai --format markdown

# 4. AI mode with real explanations (if configured)
time codesentinel scan /path/to/repo --ai --llm-provider deepseek --format markdown

# 5. CI mode integration test
codesentinel scan /path/to/repo --ci --format json
echo "Exit code: $?"
```

### Performance Benchmarking Commands
```bash
# Memory usage tracking
/usr/bin/time -v codesentinel scan /path/to/repo --format markdown

# CPU and memory profiling (Linux)
valgrind --tool=massif codesentinel scan /path/to/repo

# File count verification
find /path/to/repo -type f | wc -l
```

## Metrics to Record

### Performance Metrics
- **Total Scan Time** (seconds): From command start to completion
- **Files Processed Per Second**: Total files / scan time
- **Memory Usage**: Peak memory consumption during scan
- **CPU Utilization**: Average CPU usage during scan
- **AI Processing Time**: Additional time when --ai flag used

### Effectiveness Metrics
- **Total Findings**: Count of all security issues detected
- **Findings by Severity**: Breakdown of critical/high/medium/low/info
- **Findings by Category**: Secrets vs. config vulnerabilities vs. supply chain
- **Noise Ratio**: Percentage of findings that are false positives or irrelevant
- **Rule Performance**: Which rules generate most findings and false positives

### AI Quality Metrics
- **Explanation Quality**: 1-5 scale for usefulness of AI explanations
- **Remediation Actionability**: 1-5 scale for practical remediation steps
- **CWE Mapping Accuracy**: Percentage of correct CWE mappings
- **Risk Score Relevance**: How well risk scores align with severity

## Field Notes Structure

### Repository Profile
```
REPOSITORY: [Name]
SIZE: [File count] files, [Lines of code] LOC
LANGUAGES: [Primary languages]
SCAN DATE: [YYYY-MM-DD]
TESTER: [Name]
```

### Scan Session Log
```markdown
## [Configuration Name] - [Timestamp]

**Command**: `codesentinel scan [path] [flags]`

**Performance**:
- Scan time: [X] seconds
- Files processed: [Y] 
- Memory usage: [Z] MB
- Notes: [Observations]

**Findings Analysis**:
- Total findings: [count]
- Severity breakdown: Critical:[#], High:[#], Medium:[#], Low:[#], Info:[#]
- Noise estimate: [X]% false positives
- Notable patterns: [Observations]

**Rule Performance**:
- Top 3 rules by findings: [rule1], [rule2], [rule3]
- Most noisy rules: [rule1], [rule2]
- Missing rule gaps: [Observations]

**Output Quality**:
- Markdown readability: [Good/Fair/Poor]
- JSON structure: [Good/Fair/Poor] 
- Error handling: [Observations]
- CI integration: [Observations]

**AI Performance** (if applicable):
- Explanation quality: [1-5]
- Remediation usefulness: [1-5]
- Setup complexity: [Easy/Moderate/Difficult]
- Performance impact: [X]% slower

**UX Observations**:
- Command flags: [What worked well, what was confusing]
- Output formatting: [Strengths and weaknesses]
- Error messages: [Clarity and helpfulness]
- Configuration: [Ease of use and flexibility]
```

## Key UX Areas to Validate

### 1. Rule Configuration and Exclusion
- **Test**: How easy is it to identify and exclude noisy rules?
- **Validation**: Can users quickly identify which rules to disable?
- **GUI Implications**: Need for rule filtering and customization interface

### 2. Output Format Usefulness
- **Test**: Compare markdown vs JSON for different use cases
- **Validation**: Which format is more actionable for developers?
- **GUI Implications**: Report design and export functionality

### 3. AI Explanation Quality and Setup
- **Test**: Compare placeholder vs real AI explanations
- **Validation**: Is the AI setup process straightforward?
- **GUI Implications**: AI configuration wizard and explanation display

### 4. Performance Across Project Sizes
- **Test**: Scan time and resource usage scaling
- **Validation**: Where are the performance bottlenecks?
- **GUI Implications**: Progress indicators and cancellation support

### 5. Noise Level Management
- **Test**: False positive rate across different project types
- **Validation**: How much manual review is required?
- **GUI Implications**: Finding triage and filtering capabilities

## Pre-Dogfooding Tweaks

### Essential CLI Improvements
1. **Add --quiet flag**: Reduce verbose output during performance testing
2. **Enhanced progress indicators**: Show file processing progress for large repos
3. **Rule-specific scanning**: Add `--rules` flag to test specific rule subsets
4. **Better error messages**: Improve clarity for common configuration issues

### Configuration Enhancements  
1. **Exclude patterns file**: Support `.codesentinelignore` for project-specific exclusions
2. **Rule severity customization**: Allow users to adjust rule severity thresholds
3. **Output customization**: More control over report detail level

### Output Formatting Tweaks
1. **Summary statistics**: Add scan summary at beginning of markdown reports
2. **Severity grouping**: Organize findings by severity in output
3. **File context**: Show file paths more prominently in findings
4. **CI optimization**: Streamline JSON output for automation

## Experiment Execution Plan

### Evening 1: Setup and Initial Testing (2-3 hours)
1. **Environment Setup** (30 min)
   - Install CodeSentinel v0.2.0
   - Configure DEEPSEEK_API_KEY if available
   - Clone test repositories

2. **Small Project Testing** (45 min)
   - Run all scan configurations on sample-project
   - Establish baseline metrics
   - Test CI integration

3. **Medium Project Testing** (45 min)
   - Test 1-2 medium-sized repositories
   - Focus on performance and noise level

### Evening 2: Comprehensive Testing (2-3 hours)  
1. **Large Project Testing** (60 min)
   - Test on large JavaScript/Python projects
   - Measure performance scaling
   - Evaluate AI impact on large result sets

2. **UX Deep Dive** (60 min)
   - Test configuration options
   - Evaluate output formats for different use cases
   - Document friction points and improvement opportunities

3. **Analysis and Reporting** (30 min)
   - Compile metrics across all tests
   - Identify patterns and trends
   - Generate actionable recommendations

## Success Criteria

### Performance Targets
- **Scan Time**: < 30 seconds for 1000 files
- **Memory Usage**: < 500MB for large repositories  
- **AI Processing**: < 2x time increase with --ai flag

### Quality Targets
- **Noise Level**: < 30% false positive rate
- **AI Explanation Quality**: > 3/5 average rating
- **Output Usefulness**: > 4/5 for intended use cases

### UX Targets
- **Setup Time**: < 10 minutes for new users
- **Configuration**: Intuitive within 15 minutes of use
- **Output Actionability**: Clear next steps for 80% of findings

## Deliverables

1. **Experiment Results Document**: Complete metrics and observations
2. **Actionable Recommendations**: Specific improvements for Phase 3
3. **Priority Feature List**: GUI features validated through testing
4. **Performance Baselines**: Reference metrics for future development

## Risk Mitigation

- **Time Overrun**: Focus on 3 core repositories if time constrained
- **API Limitations**: Have placeholder AI mode as fallback
- **Repository Access**: Have backup repositories ready
- **Performance Issues**: Test on smaller subsets if scans take too long

This experiment plan provides maximum learning with minimal time investment while generating actionable data for Phase 3 GUI development planning.