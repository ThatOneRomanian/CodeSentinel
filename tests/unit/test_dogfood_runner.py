"""
Unit tests for the dogfooding runner functionality.

Tests the findings counting logic, JSON extraction, and debug mode features
of the CodeSentinel dogfooding runner.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Import the dogfood runner module
import sys
import os

# Add the project root to the Python path to import tools
project_root = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.dogfood_runner import DogfoodRunner, DogfoodScenario, ScenarioResult


class TestDogfoodRunnerJSONExtraction(unittest.TestCase):
    """Test JSON extraction and findings counting logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = DogfoodRunner(
            target_path="./sample-project",
            output_dir="./test-output",
            debug_findings=True
        )
        
    def test_extract_json_from_clean_output(self):
        """Test extracting JSON from clean output without log messages."""
        clean_json = '{"findings": [{"id": 1}, {"id": 2}], "summary": "test"}'
        result = self.runner._extract_json_from_output(clean_json)
        self.assertEqual(result, clean_json)
        
    def test_extract_json_from_output_with_logs(self):
        """Test extracting JSON from output with log messages."""
        output_with_logs = """Scanning 6 files...
Module severity does not export 'rules' list, using legacy class discovery
{
  "scan_summary": {
    "total_findings": 152
  },
  "findings": [
    {"id": 1},
    {"id": 2}
  ]
}"""
        result = self.runner._extract_json_from_output(output_with_logs)
        # Should extract the JSON part only
        self.assertTrue(result.startswith('{'))
        self.assertTrue('"scan_summary"' in result)
        self.assertTrue('"findings"' in result)
        
    def test_extract_json_from_malformed_output(self):
        """Test extracting JSON from malformed output."""
        malformed_output = """Some log messages
{ "incomplete": "json"""
        result = self.runner._extract_json_from_output(malformed_output)
        # Should return the original input if JSON is malformed
        self.assertEqual(result, malformed_output)
        
    def test_count_findings_from_json_with_findings_array(self):
        """Test counting findings from JSON with findings array."""
        json_data = {
            "findings": [
                {"rule_id": "test1", "file": "file1.py"},
                {"rule_id": "test2", "file": "file2.py"}
            ]
        }
        count = self.runner._count_findings_from_json(json.dumps(json_data))
        self.assertEqual(count, 2)
        
    def test_count_findings_from_json_with_scan_summary(self):
        """Test counting findings from JSON with scan_summary."""
        json_data = {
            "scan_summary": {
                "total_findings": 152,
                "by_severity": {
                    "high": 128,
                    "medium": 24
                }
            },
            "findings": [{"rule_id": "test1"}, {"rule_id": "test2"}]  # Actual findings array
        }
        count = self.runner._count_findings_from_json(json.dumps(json_data))
        self.assertEqual(count, 2)  # Should use findings array length, not scan_summary
        
    def test_count_findings_from_json_with_results_array(self):
        """Test counting findings from JSON with results array."""
        json_data = {
            "results": [
                {"finding": 1},
                {"finding": 2},
                {"finding": 3}
            ]
        }
        count = self.runner._count_findings_from_json(json.dumps(json_data))
        self.assertEqual(count, 3)
        
    def test_count_findings_from_json_top_level_array(self):
        """Test counting findings from JSON that is a top-level array."""
        json_data = [
            {"rule_id": "test1"},
            {"rule_id": "test2"},
            {"rule_id": "test3"}
        ]
        count = self.runner._count_findings_from_json(json.dumps(json_data))
        self.assertEqual(count, 3)
        
    def test_count_findings_from_invalid_json(self):
        """Test counting findings from invalid JSON."""
        invalid_json = "This is not JSON"
        count = self.runner._count_findings_from_json(invalid_json)
        self.assertEqual(count, 0)
        
    def test_count_findings_from_empty_json(self):
        """Test counting findings from empty JSON object."""
        empty_json = "{}"
        count = self.runner._count_findings_from_json(empty_json)
        self.assertEqual(count, 0)


class TestDogfoodRunnerDebugMode(unittest.TestCase):
    """Test debug mode functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = DogfoodRunner(
            target_path="./sample-project",
            output_dir="./test-output",
            debug_findings=True
        )
        
    @patch('tools.dogfood_runner.DogfoodRunner.execute_command')
    def test_run_direct_scan_comparison_success(self, mock_execute):
        """Test direct scan comparison with successful execution."""
        # Mock successful command execution with JSON output
        mock_execute.return_value = {
            "success": True,
            "stdout": '{"findings": [{"id": 1}, {"id": 2}]}',
            "stderr": "",
            "exit_code": 0,
            "runtime": 1.0
        }
        
        scenario = DogfoodScenario(
            id="S2",
            name="JSON Format Scan",
            description="Test",
            command=["codesentinel", "scan", "./sample-project", "--format", "json"],
            output_format="json"
        )
        
        count = self.runner._run_direct_scan_comparison(scenario)
        self.assertEqual(count, 2)
        mock_execute.assert_called_once_with(scenario.command, self.runner.timeout)
        
    @patch('tools.dogfood_runner.DogfoodRunner.execute_command')
    def test_run_direct_scan_comparison_failure(self, mock_execute):
        """Test direct scan comparison with failed execution."""
        # Mock failed command execution
        mock_execute.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "Command failed",
            "exit_code": 1,
            "runtime": 0.5
        }
        
        scenario = DogfoodScenario(
            id="S2",
            name="JSON Format Scan",
            description="Test",
            command=["codesentinel", "scan", "./sample-project", "--format", "json"],
            output_format="json"
        )
        
        count = self.runner._run_direct_scan_comparison(scenario)
        self.assertEqual(count, 0)
        
    @patch('tools.dogfood_runner.DogfoodRunner.execute_command')
    def test_run_direct_scan_comparison_non_json(self, mock_execute):
        """Test direct scan comparison with non-JSON scenario."""
        # Mock successful command execution but non-JSON format
        mock_execute.return_value = {
            "success": True,
            "stdout": "Markdown output\n# Findings\n- Finding 1\n- Finding 2",
            "stderr": "",
            "exit_code": 0,
            "runtime": 1.0
        }
        
        scenario = DogfoodScenario(
            id="S1",
            name="Markdown Scan",
            description="Test",
            command=["codesentinel", "scan", "./sample-project", "--format", "markdown"],
            output_format="markdown"
        )
        
        count = self.runner._run_direct_scan_comparison(scenario)
        self.assertEqual(count, 0)


class TestDogfoodRunnerScenarios(unittest.TestCase):
    """Test scenario setup and execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = DogfoodRunner(
            target_path="./sample-project",
            output_dir=self.temp_dir,
            debug_findings=False
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_setup_scenarios_without_ai(self):
        """Test scenario setup without AI enabled."""
        self.runner.enable_ai = False
        self.runner.setup_scenarios()
        
        # Should have 5 scenarios (S1, S2, S3, S6, S7) - AI scenarios filtered out
        self.assertEqual(len(self.runner.scenarios), 5)
        scenario_ids = [s.id for s in self.runner.scenarios]
        self.assertIn("S1", scenario_ids)
        self.assertIn("S2", scenario_ids)
        self.assertIn("S3", scenario_ids)
        self.assertIn("S6", scenario_ids)
        self.assertIn("S7", scenario_ids)
        self.assertNotIn("S4", scenario_ids)  # AI scenario
        self.assertNotIn("S5", scenario_ids)  # AI scenario
        
    def test_setup_scenarios_with_ai(self):
        """Test scenario setup with AI enabled."""
        self.runner.enable_ai = True
        # Mock AI configuration check to return True
        with patch.object(self.runner, '_check_ai_configuration', return_value=True):
            self.runner.setup_scenarios()
            
            # Should have 7 scenarios when AI is enabled
            self.assertEqual(len(self.runner.scenarios), 7)
            scenario_ids = [s.id for s in self.runner.scenarios]
            self.assertIn("S4", scenario_ids)  # AI scenario
            self.assertIn("S5", scenario_ids)  # AI scenario
            
    def test_find_sample_file(self):
        """Test finding a representative sample file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_py = pathlib.Path(temp_dir) / "test.py"
            test_py.write_text("# Test Python file")
            
            test_js = pathlib.Path(temp_dir) / "test.js"
            test_js.write_text("// Test JavaScript file")
            
            self.runner.target_path = pathlib.Path(temp_dir)
            sample_file = self.runner._find_sample_file()
            
            # Should find a Python file first
            self.assertTrue(sample_file.endswith(".py") or sample_file.endswith(".js"))
            
    def test_find_sample_file_no_files(self):
        """Test finding sample file when no files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.runner.target_path = pathlib.Path(temp_dir)
            sample_file = self.runner._find_sample_file()
            
            # Should return the directory itself
            self.assertEqual(sample_file, str(self.runner.target_path))


class TestDogfoodRunnerIntegration(unittest.TestCase):
    """Integration tests for the dogfood runner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('tools.dogfood_runner.subprocess.run')
    def test_validate_environment_success(self, mock_subprocess):
        """Test environment validation with successful checks."""
        # Mock successful codesentinel version check
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "CodeSentinel v0.2.0"
        
        runner = DogfoodRunner(
            target_path="./sample-project",
            output_dir=self.temp_dir
        )
        
        # Mock target path exists and is directory
        with patch.object(pathlib.Path, 'exists', return_value=True), \
             patch.object(pathlib.Path, 'is_dir', return_value=True), \
             patch.object(pathlib.Path, 'mkdir'):
            
            result = runner.validate_environment()
            self.assertTrue(result)
            
    @patch('tools.dogfood_runner.subprocess.run')
    def test_validate_environment_codesentinel_not_found(self, mock_subprocess):
        """Test environment validation when codesentinel is not available."""
        # Mock codesentinel not found
        mock_subprocess.side_effect = FileNotFoundError
        
        runner = DogfoodRunner(
            target_path="./sample-project",
            output_dir=self.temp_dir
        )
        
        # Mock target path exists and is directory
        with patch.object(pathlib.Path, 'exists', return_value=True), \
             patch.object(pathlib.Path, 'is_dir', return_value=True):
            
            result = runner.validate_environment()
            self.assertFalse(result)
            
    def test_validate_environment_target_not_exists(self):
        """Test environment validation when target doesn't exist."""
        runner = DogfoodRunner(
            target_path="/nonexistent/path",
            output_dir=self.temp_dir
        )
        
        # Mock target path doesn't exist
        with patch.object(pathlib.Path, 'exists', return_value=False):
            result = runner.validate_environment()
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()