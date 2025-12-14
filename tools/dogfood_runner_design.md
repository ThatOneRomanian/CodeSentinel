# Automated Dogfooding Runner Design Specification

## Overview

The automated dogfooding runner is a Python script that automates the execution of CodeSentinel v0.2.0 dogfooding experiments across multiple repositories and scan configurations. It provides structured output, comprehensive logging, and error handling for systematic performance and quality validation.

## Requirements Analysis

### Core Requirements
- **Location**: `tools/dogfood_runner.py`
- **Dependencies**: Python standard library only
- **Execution**: `python tools/dogfood_runner.py --target /path/to/repo [--ai] [--llm-provider] [--out-dir]`
- **Scenarios**: 5 core scenarios from dogfooding-experiment-plan.md + 2 additional useful scenarios
- **Output**: Structured output with timestamps, comprehensive logging
- **Error Handling**: Graceful error handling without aborting entire run
- **Integration**: Compatible with existing project structure and patterns

## Script Architecture

### Command-Line Interface
```python
python tools/dogfood_runner.py --target /path/to/repo [options]

Required:
  --target TARGET        Target repository path to scan

Optional:
  --ai                   Enable AI scenarios (requires DEEPSEEK_API_KEY)
  --llm-provider PROVIDER LLM provider for AI scenarios (default: deepseek)
  --out-dir DIR          Output directory for results (default: ./dogfood-results)
  --timeout SECONDS      Timeout per scenario in seconds (default: 300)
  --skip-scenarios LIST  Comma-separated list of scenario numbers to skip
  --verbose              Enable verbose logging
  --help                 Show help message
```

### Core Components

#### 1. Main Runner Class
```python
class DogfoodRunner:
    def __init__(self, target_path: str, output_dir: str, enable_ai: bool = False, 
                 llm_provider: str = "deepseek", timeout: int = 300):
        self.target_path = Path(target_path)
        self.output_dir = Path(output_dir)
        self.enable_ai = enable_ai
        self.llm_provider = llm_provider
        self.timeout = timeout
        self.scenarios = []
        self.results = []
        
    def validate_environment(self) -> bool
    def setup_output_structure(self) -> None
    def run_scenarios(self) -> None
    def generate_summary(self) -> None
    def cleanup(self) -> None
```

#### 2. Scenario Definition
```python
@dataclass
class DogfoodScenario:
    id: str
    name: str
    description: str
    command: List[str]
    output_format: str
    requires_ai: bool = False
    ci_mode: bool = False
    single_file: bool = False
    ignore_patterns: bool = False
```

#### 3. Result Tracking
```python
@dataclass
class ScenarioResult:
    scenario_id: str
    success: bool
    exit_code: int
    runtime: float
    output_file: Path
    error_message: str = ""
    findings_count: int = 0
    performance_metrics: Dict = field(default_factory=dict)
```

## Scenario Matrix

### Core Scenarios (from dogfooding-experiment-plan.md)

#### S1: Baseline Markdown Scan
- **Command**: `codesentinel scan {target} --format markdown`
- **Purpose**: Establish baseline performance and findings
- **Output**: `scenario1/output.md`

#### S2: JSON Format Scan
- **Command**: `codesentinel scan {target} --format json`
- **Purpose**: Validate JSON output for machine processing
- **Output**: `scenario2/output.json`

#### S3: JSON + CI Mode Scan
- **Command**: `codesentinel scan {target} --ci --format json`
- **Purpose**: Test CI integration and exit code behavior
- **Output**: `scenario3/output.json`
- **Expected Exit Codes**: 0 (no findings), 1 (findings present)

#### S4: AI + JSON (if --ai enabled)
- **Command**: `codesentinel scan {target} --ai --llm-provider {provider} --format json`
- **Purpose**: Validate AI explanations with JSON output
- **Output**: `scenario4/output.json`
- **Requires**: `--ai` flag and DEEPSEEK_API_KEY

#### S5: AI + Markdown (if --ai enabled)
- **Command**: `codesentinel scan {target} --ai --llm-provider {provider} --format markdown`
- **Purpose**: Validate AI explanations with human-readable output
- **Output**: `scenario5/output.md`
- **Requires**: `--ai` flag and DEEPSEEK_API_KEY

### Additional Useful Scenarios

#### S6: Single File Scan
- **Command**: `codesentinel scan {sample_file} --format markdown`
- **Purpose**: Test scanning individual files
- **Output**: `scenario6/output.md`
- **Sample File**: First Python file found in target repository

#### S7: Scan with Gitignore Patterns
- **Command**: `codesentinel scan {target} --format json`
- **Purpose**: Validate .gitignore pattern handling
- **Output**: `scenario7/output.json`
- **Note**: Relies on existing .gitignore support in walker.py

## Output Structure

```
<out-dir>/
├── <repo-name>-<timestamp>/
│   ├── summary.md                 # Comprehensive run summary
│   ├── run.log                   # Detailed execution log
│   ├── metadata.json             # Run metadata and configuration
│   ├── scenario1/                # S1: Baseline markdown
│   │   ├── command.txt           # Exact command executed
│   │   ├── output.md             # Scan output
│   │   ├── exit_code.txt         # Exit code
│   │   └── runtime.txt           # Execution time
│   ├── scenario2/                # S2: JSON format
│   │   ├── command.txt
│   │   ├── output.json
│   │   ├── exit_code.txt
│   │   └── runtime.txt
│   └── ... (scenario directories 3-7)
└── latest -> <repo-name>-<timestamp>/  # Symlink to latest run
```

### Summary Report Structure
```markdown
# CodeSentinel Dogfooding Run Summary

## Run Information
- **Repository**: {repo_name}
- **Scan Date**: {timestamp}
- **Total Scenarios**: {total} (Completed: {completed}, Failed: {failed})
- **AI Enabled**: {yes/no}
- **LLM Provider**: {provider}

## Performance Summary
| Scenario | Status | Runtime | Exit Code | Findings |
|----------|--------|---------|-----------|----------|
| S1: Baseline Markdown | ✅ Success | 12.3s | 0 | 5 |
| S2: JSON Format | ✅ Success | 11.8s | 0 | 5 |
| ... | ... | ... | ... | ... |

## Findings Analysis
- **Total Findings**: {total_findings}
- **Findings by Severity**: Critical: {x}, High: {y}, Medium: {z}, Low: {w}, Info: {v}
- **Noise Estimate**: {noise_percentage}%

## Performance Metrics
- **Average Scan Time**: {avg_time}s
- **Total Execution Time**: {total_time}s
- **Memory Usage**: Peak {peak_memory}MB

## Issues and Recommendations
- {List of any issues encountered}
- {Performance observations}
- {Configuration recommendations}
```

## Error Handling Strategy

### Validation Phase
1. **Target Validation**: Verify target path exists and is accessible
2. **CodeSentinel Availability**: Verify `codesentinel` command is available
3. **AI Configuration**: Validate DEEPSEEK_API_KEY if AI scenarios enabled
4. **Output Directory**: Ensure writable output directory

### Execution Phase
1. **Scenario Isolation**: Each scenario runs independently
2. **Timeout Protection**: Prevent hanging scenarios
3. **Graceful Failure**: Continue execution on individual scenario failures
4. **Error Recovery**: Capture and log errors without aborting entire run

### Error Categories
- **Configuration Errors**: Invalid paths, missing dependencies
- **Execution Errors**: Timeouts, command failures, permission issues
- **Output Errors**: Invalid JSON, malformed reports
- **AI Errors**: API failures, quota limits, network issues

## Integration Requirements

### Project Structure Integration
- **Location**: `tools/dogfood_runner.py`
- **Git Integration**: Add `dogfood-results/` to `.gitignore`
- **Documentation**: Update README.md with usage examples
- **Dependencies**: Zero external dependencies (standard library only)

### Memory Bank Updates
- **productContext.md**: Document new dogfooding automation capability
- **systemPatterns.md**: Add dogfooding runner patterns and architecture
- **progress.md**: Track dogfooding automation implementation
- **decisionLog.md**: Record design decisions for dogfooding runner

### Compatibility Requirements
- **Python Version**: 3.8+ (matches CodeSentinel requirements)
- **Platform Support**: Windows, macOS, Linux
- **CodeSentinel Version**: v0.2.0+ (supports AI explainer mode)

## Implementation Details

### Standard Library Dependencies
```python
import argparse
import json
import logging
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
```

### Key Functions

#### Command Execution
```python
def execute_command(self, command: List[str], timeout: int) -> Dict:
    """Execute a command with timeout and capture results."""
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.target_path
        )
        runtime = time.time() - start_time
        
        return {
            "success": result.returncode in [0, 1],  # Accept 0 (clean) or 1 (findings)
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "runtime": runtime
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "runtime": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "runtime": time.time() - start_time
        }
```

#### Scenario Configuration
```python
def setup_scenarios(self) -> List[DogfoodScenario]:
    """Configure all dogfooding scenarios."""
    scenarios = [
        DogfoodScenario(
            id="S1",
            name="Baseline Markdown Scan",
            description="Establish baseline performance with markdown output",
            command=["codesentinel", "scan", str(self.target_path), "--format", "markdown"],
            output_format="markdown"
        ),
        # ... other scenarios
    ]
    
    # Filter AI scenarios if AI not enabled
    if not self.enable_ai:
        scenarios = [s for s in scenarios if not s.requires_ai]
    
    return scenarios
```

## Testing Strategy

### Validation Tests
1. **Basic Functionality**: Run against sample-project directory
2. **Error Handling**: Test with invalid paths and missing dependencies
3. **AI Scenarios**: Test with and without DEEPSEEK_API_KEY
4. **Large Repositories**: Validate performance with medium-sized projects
5. **Output Validation**: Verify structured output generation

### Performance Considerations
- **Memory Usage**: Minimal memory footprint (standard library only)
- **Execution Time**: Efficient scenario execution with timeouts
- **Disk Usage**: Structured output with clear organization
- **Network Usage**: Only for AI scenarios when enabled

## Security Considerations

### Local-First Design
- No external network calls except for optional AI scenarios
- All processing happens locally
- No sensitive data transmitted externally

### Input Validation
- Validate all file paths and command arguments
- Sanitize user inputs to prevent injection attacks
- Restrict file system access to target directory only

## Future Enhancements

### Potential Extensions
1. **Comparative Analysis**: Compare results across multiple runs
2. **Performance Benchmarking**: Track performance trends over time
3. **Rule-Specific Testing**: Test individual rule performance
4. **Custom Scenario Support**: User-defined scenario configurations
5. **CI/CD Integration**: Automated dogfooding in build pipelines

### Integration Opportunities
1. **GUI Integration**: Visual dogfooding results in Phase 3 GUI
2. **API Integration**: Programmatic access to dogfooding results
3. **Reporting Enhancements**: Generate detailed performance reports
4. **Alerting System**: Notify on performance regressions

## Conclusion

This design specification provides a comprehensive blueprint for implementing an automated dogfooding runner that aligns with CodeSentinel's local-first philosophy and existing project structure. The runner will enable systematic validation of CodeSentinel v0.2.0 performance, noise levels, and AI explainer functionality across diverse codebases.

The implementation will be dependency-free, using only Python's standard library, and will integrate seamlessly with the existing CodeSentinel ecosystem while providing valuable insights for Phase 3 GUI development planning.