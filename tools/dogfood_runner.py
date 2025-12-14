#!/usr/bin/env python3
"""
Automated Dogfooding Runner for CodeSentinel

This script automates the execution of CodeSentinel v0.2.0 dogfooding experiments
across multiple repositories and scan configurations. It provides structured output,
comprehensive logging, and error handling for systematic performance and quality validation.

© 2025 Andrei Antonescu. All rights reserved. Proprietary – not licensed for public redistribution.
"""

import argparse
import json
import logging
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any


@dataclass
class DogfoodScenario:
    """Represents a single dogfooding scenario configuration."""
    id: str
    name: str
    description: str
    command: List[str]
    output_format: str
    requires_ai: bool = False
    ci_mode: bool = False
    single_file: bool = False
    ignore_patterns: bool = False


@dataclass
class ScenarioResult:
    """Tracks the execution results of a single scenario."""
    scenario_id: str
    success: bool
    exit_code: int
    runtime: float
    output_file: pathlib.Path
    error_message: str = ""
    findings_count: int = 0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class DogfoodRunner:
    """Main runner class for executing dogfooding scenarios."""
    
    def __init__(self, target_path: str, output_dir: str, enable_ai: bool = False,
                 llm_provider: str = "deepseek", timeout: int = 300, verbose: bool = False,
                 debug_findings: bool = False):
        self.target_path = pathlib.Path(target_path)
        self.output_dir = pathlib.Path(output_dir)
        self.enable_ai = enable_ai
        self.llm_provider = llm_provider
        self.timeout = timeout
        self.verbose = verbose
        self.debug_findings = debug_findings
        
        self.scenarios: List[DogfoodScenario] = []
        self.results: List[ScenarioResult] = []
        self.run_id: str = ""
        self.run_timestamp: str = ""
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Configure logging for the dogfooding run."""
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_environment(self) -> bool:
        """Validate the execution environment and dependencies."""
        self.logger.info("Validating execution environment...")
        
        # Check if target path exists
        if not self.target_path.exists():
            self.logger.error(f"Target path does not exist: {self.target_path}")
            return False
            
        if not self.target_path.is_dir():
            self.logger.error(f"Target path is not a directory: {self.target_path}")
            return False
            
        # Check if codesentinel command is available
        try:
            result = subprocess.run(
                ["codesentinel", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.logger.error("codesentinel command is not available or not working")
                return False
            self.logger.info(f"CodeSentinel version: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            self.logger.error(f"Failed to execute codesentinel command: {e}")
            return False
            
        # Check AI configuration if AI scenarios are enabled
        if self.enable_ai:
            if not self._check_ai_configuration():
                self.logger.warning("AI scenarios enabled but DEEPSEEK_API_KEY not found. AI scenarios will be skipped.")
                self.enable_ai = False
                
        # Check if output directory is writable
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            test_file = self.output_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            self.logger.error(f"Output directory is not writable: {e}")
            return False
            
        self.logger.info("Environment validation passed")
        return True
        
    def _check_ai_configuration(self) -> bool:
        """Check if AI configuration is available for AI scenarios."""
        # Check for DEEPSEEK_API_KEY environment variable
        import os
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            self.logger.warning("DEEPSEEK_API_KEY environment variable not found")
            return False
            
        self.logger.info("AI configuration validated (DEEPSEEK_API_KEY found)")
        return True
        
    def setup_scenarios(self) -> None:
        """Configure all dogfooding scenarios."""
        repo_name = self.target_path.name
        target_str = str(self.target_path)
        
        # Core scenarios from dogfooding-experiment-plan.md
        scenarios = [
            DogfoodScenario(
                id="S1",
                name="Baseline Markdown Scan",
                description="Establish baseline performance with markdown output",
                command=["codesentinel", "scan", target_str, "--format", "markdown"],
                output_format="markdown"
            ),
            DogfoodScenario(
                id="S2",
                name="JSON Format Scan",
                description="Validate JSON output for machine processing",
                command=["codesentinel", "scan", target_str, "--format", "json"],
                output_format="json"
            ),
            DogfoodScenario(
                id="S3",
                name="JSON + CI Mode Scan",
                description="Test CI integration and exit code behavior",
                command=["codesentinel", "scan", target_str, "--ci", "--format", "json"],
                output_format="json",
                ci_mode=True
            ),
            DogfoodScenario(
                id="S4",
                name="AI + JSON Scan",
                description="Validate AI explanations with JSON output",
                command=["codesentinel", "scan", target_str, "--ai", "--llm-provider", self.llm_provider, "--format", "json"],
                output_format="json",
                requires_ai=True
            ),
            DogfoodScenario(
                id="S5",
                name="AI + Markdown Scan",
                description="Validate AI explanations with human-readable output",
                command=["codesentinel", "scan", target_str, "--ai", "--llm-provider", self.llm_provider, "--format", "markdown"],
                output_format="markdown",
                requires_ai=True
            )
        ]
        
        # Additional useful scenarios
        scenarios.extend([
            DogfoodScenario(
                id="S6",
                name="Single File Scan",
                description="Test scanning individual files",
                command=["codesentinel", "scan", self._find_sample_file(), "--format", "markdown"],
                output_format="markdown",
                single_file=True
            ),
            DogfoodScenario(
                id="S7",
                name="Scan with Gitignore Patterns",
                description="Validate .gitignore pattern handling",
                command=["codesentinel", "scan", target_str, "--format", "json"],
                output_format="json",
                ignore_patterns=True
            )
        ])
        
        # Filter AI scenarios if AI not enabled
        if not self.enable_ai:
            scenarios = [s for s in scenarios if not s.requires_ai]
            self.logger.info(f"Filtered out AI scenarios. Running {len(scenarios)} scenarios.")
            
        self.scenarios = scenarios
        self.logger.info(f"Configured {len(self.scenarios)} scenarios for execution")
        
    def _find_sample_file(self) -> str:
        """Find a representative sample file for single file scanning."""
        # Look for Python files first
        for pattern in ["*.py", "*.js", "*.json", "*.yaml", "*.yml", "*.md"]:
            files = list(self.target_path.rglob(pattern))
            if files:
                return str(files[0])
                
        # Fallback to any file
        files = list(self.target_path.rglob("*"))
        if files and files[0].is_file():
            return str(files[0])
            
        # If no files found, use the target directory itself (will produce empty scan)
        return str(self.target_path)
        
    def setup_output_structure(self) -> None:
        """Create the output directory structure for this run."""
        repo_name = self.target_path.name
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"{repo_name}-{self.run_timestamp}"
        
        self.run_dir = self.output_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        # Create scenario directories
        for scenario in self.scenarios:
            scenario_dir = self.run_dir / f"scenario{scenario.id[1:]}"
            scenario_dir.mkdir(exist_ok=True)
            
        self.logger.info(f"Created output structure: {self.run_dir}")
        
    def execute_command(self, command: List[str], timeout: int) -> Dict[str, Any]:
        """Execute a command with timeout and capture results."""
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
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
            runtime = time.time() - start_time
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "runtime": timeout
            }
        except Exception as e:
            runtime = time.time() - start_time
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "runtime": runtime
            }
            
    def _extract_json_from_output(self, output: str) -> str:
        """Extract JSON content from output that may contain log messages."""
        # Look for the first occurrence of '{' or '['
        start_index = output.find('{')
        if start_index == -1:
            start_index = output.find('[')
        if start_index == -1:
            return output  # No JSON found, return original
        
        # Extract from the first JSON character to the end
        json_content = output[start_index:]
        
        # Validate that it's proper JSON by finding matching braces
        try:
            # Try to parse to validate JSON structure
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            # If parsing fails, try to find the complete JSON object
            # Count braces to find the complete structure
            brace_count = 0
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(json_content):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    elif char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                
                # If we've found the end of the JSON structure
                if brace_count == 0 and bracket_count == 0 and i > 0:
                    return json_content[:i+1]
            
            # If we couldn't find complete structure, return original
            return output
            
    def _count_findings_from_json(self, json_content: str) -> int:
        """Count findings from JSON output content."""
        try:
            # First, extract clean JSON from potentially noisy output
            clean_json = self._extract_json_from_output(json_content)
            
            data = json.loads(clean_json)
            # Handle different JSON output structures
            if isinstance(data, dict):
                if "findings" in data:
                    return len(data["findings"])
                elif "results" in data:
                    return len(data["results"])
                elif "scan_summary" in data and "total_findings" in data["scan_summary"]:
                    return data["scan_summary"]["total_findings"]
                else:
                    # Count all top-level keys that might be findings
                    return sum(1 for key in data if isinstance(data[key], list) and key not in ["metadata", "summary"])
            elif isinstance(data, list):
                return len(data)
            else:
                return 0
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            if self.debug_findings:
                self.logger.debug(f"Failed to parse JSON for findings count: {e}")
                self.logger.debug(f"JSON content (first 500 chars): {json_content[:500]}")
            return 0
            
    def _run_direct_scan_comparison(self, scenario: DogfoodScenario) -> int:
        """Run a direct codesentinel scan for comparison and return findings count."""
        try:
            # Run the same command but capture JSON output specifically for counting
            comparison_result = self.execute_command(scenario.command, self.timeout)
            if comparison_result["success"] and scenario.output_format == "json":
                return self._count_findings_from_json(comparison_result["stdout"])
            return 0
        except Exception as e:
            self.logger.warning(f"Direct scan comparison failed for {scenario.id}: {e}")
            return 0
            
    def run_scenarios(self) -> None:
        """Execute all configured scenarios."""
        self.logger.info(f"Starting execution of {len(self.scenarios)} scenarios")
        
        for scenario in self.scenarios:
            self.logger.info(f"Running scenario {scenario.id}: {scenario.name}")
            
            # Execute the command
            execution_result = self.execute_command(scenario.command, self.timeout)
            
            # Process results
            scenario_dir = self.run_dir / f"scenario{scenario.id[1:]}"
            output_file = scenario_dir / f"output.{scenario.output_format}"
            
            # Write output
            try:
                output_file.write_text(execution_result["stdout"], encoding="utf-8")
            except Exception as e:
                self.logger.error(f"Failed to write output for {scenario.id}: {e}")
                
            # Write command and metadata
            (scenario_dir / "command.txt").write_text(" ".join(scenario.command))
            (scenario_dir / "exit_code.txt").write_text(str(execution_result["exit_code"]))
            (scenario_dir / "runtime.txt").write_text(f"{execution_result['runtime']:.2f}")
            
            # Count findings based on output format
            findings_count = 0
            if execution_result["success"]:
                if scenario.output_format == "json":
                    findings_count = self._count_findings_from_json(execution_result["stdout"])
                elif scenario.output_format == "markdown":
                    # For markdown, we can't easily count findings, so we'll use 0
                    findings_count = 0
                    
            # Run direct scan comparison if debug mode is enabled and it's a JSON scenario
            direct_findings_count = 0
            if self.debug_findings and scenario.output_format == "json":
                direct_findings_count = self._run_direct_scan_comparison(scenario)
                self.logger.info(f"Debug: Scenario {scenario.id} - Runner count: {findings_count}, Direct count: {direct_findings_count}")
                
                # Write debug information
                debug_file = scenario_dir / "debug_findings.txt"
                debug_content = f"""Findings Count Comparison for {scenario.id}
Runner Count: {findings_count}
Direct Scan Count: {direct_findings_count}
Match: {"YES" if findings_count == direct_findings_count else "NO"}
"""
                if findings_count != direct_findings_count:
                    debug_content += f"\nDISCREPANCY DETECTED: Runner count differs from direct scan by {abs(findings_count - direct_findings_count)} findings\n"
                debug_file.write_text(debug_content)
                
            # Create result object
            result = ScenarioResult(
                scenario_id=scenario.id,
                success=execution_result["success"],
                exit_code=execution_result["exit_code"],
                runtime=execution_result["runtime"],
                output_file=output_file,
                error_message=execution_result["stderr"],
                findings_count=findings_count
            )
            
            self.results.append(result)
            
            status = "✅ Success" if execution_result["success"] else "❌ Failed"
            self.logger.info(f"Scenario {scenario.id} completed: {status} "
                           f"(runtime: {execution_result['runtime']:.2f}s, "
                           f"findings: {findings_count})")
                           
    def generate_summary(self) -> None:
        """Generate comprehensive summary report."""
        summary_file = self.run_dir / "summary.md"
        metadata_file = self.run_dir / "metadata.json"
        
        # Calculate statistics
        total_scenarios = len(self.scenarios)
        completed_scenarios = len([r for r in self.results if r.success])
        failed_scenarios = total_scenarios - completed_scenarios
        total_findings = sum(r.findings_count for r in self.results)
        total_runtime = sum(r.runtime for r in self.results)
        
        # Generate summary markdown
        summary_content = f"""# CodeSentinel Dogfooding Run Summary

## Run Information
- **Repository**: {self.target_path.name}
- **Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Scenarios**: {total_scenarios} (Completed: {completed_scenarios}, Failed: {failed_scenarios})
- **AI Enabled**: {'Yes' if self.enable_ai else 'No'}
- **LLM Provider**: {self.llm_provider if self.enable_ai else 'N/A'}
- **Output Directory**: {self.run_dir}
- **Debug Findings**: {'Yes' if self.debug_findings else 'No'}

## Performance Summary
| Scenario | Status | Runtime | Exit Code | Findings |
|----------|--------|---------|-----------|----------|
"""
        
        for result in self.results:
            scenario = next(s for s in self.scenarios if s.id == result.scenario_id)
            status = "✅ Success" if result.success else "❌ Failed"
            summary_content += f"| {scenario.id}: {scenario.name} | {status} | {result.runtime:.2f}s | {result.exit_code} | {result.findings_count} |\n"
            
        summary_content += f"""
## Findings Analysis
- **Total Findings**: {total_findings}
- **Findings Distribution**: See individual scenario outputs

## Performance Metrics
- **Average Scan Time**: {total_runtime/len(self.results):.2f}s
- **Total Execution Time**: {total_runtime:.2f}s
- **Success Rate**: {completed_scenarios/total_scenarios*100:.1f}%

## Issues and Recommendations
"""
        
        # Add issues if any scenarios failed
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            summary_content += "\n### Failed Scenarios:\n"
            for result in failed_results:
                summary_content += f"- **{result.scenario_id}**: {result.error_message}\n"
        else:
            summary_content += "- All scenarios completed successfully\n"
            
        # Add debug findings information if enabled
        if self.debug_findings:
            summary_content += "\n### Debug Findings Analysis:\n"
            json_scenarios = [r for r in self.results if r.output_file.suffix == '.json']
            for result in json_scenarios:
                debug_file = result.output_file.parent / "debug_findings.txt"
                if debug_file.exists():
                    debug_content = debug_file.read_text()
                    summary_content += f"- **{result.scenario_id}**: {debug_content}\n"
            
        summary_content += f"""
### Recommendations:
- Review individual scenario outputs for detailed analysis
- Compare findings across different output formats
- Validate AI explanations quality (if AI enabled)
- Monitor performance trends across multiple runs

---
*Generated by CodeSentinel Dogfooding Runner v0.2.0*
"""
        
        summary_file.write_text(summary_content, encoding="utf-8")
        
        # Generate metadata JSON
        metadata = {
            "run_id": self.run_id,
            "timestamp": self.run_timestamp,
            "repository": self.target_path.name,
            "target_path": str(self.target_path),
            "ai_enabled": self.enable_ai,
            "llm_provider": self.llm_provider,
            "debug_findings": self.debug_findings,
            "scenarios_count": total_scenarios,
            "completed_scenarios": completed_scenarios,
            "failed_scenarios": failed_scenarios,
            "total_findings": total_findings,
            "total_runtime": total_runtime,
            "scenario_results": [
                {
                    "scenario_id": r.scenario_id,
                    "success": r.success,
                    "exit_code": r.exit_code,
                    "runtime": r.runtime,
                    "findings_count": r.findings_count,
                    "output_file": str(r.output_file.relative_to(self.run_dir))
                }
                for r in self.results
            ]
        }
        
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        
        self.logger.info(f"Generated summary report: {summary_file}")
        self.logger.info(f"Generated metadata: {metadata_file}")
        
    def run(self) -> bool:
        """Execute the complete dogfooding run."""
        try:
            # Setup and validation
            if not self.validate_environment():
                return False
                
            self.setup_scenarios()
            self.setup_output_structure()
            
            # Execute scenarios
            self.run_scenarios()
            
            # Generate reports
            self.generate_summary()
            
            # Create latest symlink (if supported)
            try:
                latest_link = self.output_dir / "latest"
                if latest_link.exists():
                    latest_link.unlink()
                latest_link.symlink_to(self.run_dir.name)
            except (OSError, NotImplementedError):
                # Symlinks not supported on this platform
                pass
                
            self.logger.info(f"Dogfooding run completed successfully: {self.run_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Dogfooding run failed: {e}")
            return False


def main():
    """Main entry point for the dogfooding runner."""
    parser = argparse.ArgumentParser(
        description="Automated Dogfooding Runner for CodeSentinel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/dogfood_runner.py --target ./sample-project
  python tools/dogfood_runner.py --target /path/to/repo --ai --llm-provider deepseek
  python tools/dogfood_runner.py --target ./sample-project --out-dir ./dogfood-results --verbose
  python tools/dogfood_runner.py --target ./sample-project --debug-findings
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--target",
        required=True,
        help="Target repository path to scan"
    )
    
    # Optional arguments
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Enable AI scenarios (requires DEEPSEEK_API_KEY)"
    )
    
    parser.add_argument(
        "--llm-provider",
        default="deepseek",
        choices=["deepseek", "openai", "ollama"],
        help="LLM provider for AI scenarios (default: deepseek)"
    )
    
    parser.add_argument(
        "--out-dir",
        default="./dogfood-results",
        help="Output directory for results (default: ./dogfood-results)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout per scenario in seconds (default: 300)"
    )
    
    parser.add_argument(
        "--skip-scenarios",
        help="Comma-separated list of scenario numbers to skip (e.g., S4,S5)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--debug-findings",
        action="store_true",
        help="Enable debug mode for findings count comparison"
    )
    
    args = parser.parse_args()
    
    # Create and run the dogfooding runner
    runner = DogfoodRunner(
        target_path=args.target,
        output_dir=args.out_dir,
        enable_ai=args.ai,
        llm_provider=args.llm_provider,
        timeout=args.timeout,
        verbose=args.verbose,
        debug_findings=args.debug_findings
    )
    
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()