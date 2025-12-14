"""
Unit tests for CodeSentinel Phase 3 API freeze contract.

Tests the ScanService API implementation, error hierarchy, and event streaming
without modifying existing backend functionality.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pathlib
import tempfile
import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Import the API modules
from sentinel.api.scan_service import ScanService, ScanConfig, ScanOptions, ActiveScan
from sentinel.api.models import (
    EnhancedFinding, ScanProgress, ScanSummary, ScanResults, SystemStatus,
    CodeSentinelError, InvalidConfigError, ScanNotFoundError, ScanAlreadyRunningError,
    ScanInProgressError, FileSystemError, FindingNotFoundError, InvalidStatusError, ExportError
)
from sentinel.api.events import ScanEvent, ScanEventTypes


class TestScanServiceAPI(unittest.TestCase):
    """Test the frozen API surface of ScanService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = ScanService()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = ScanConfig(
            target_path=pathlib.Path(self.temp_dir),
            enable_ai=False,
            llm_provider="deepseek",
            output_format="gui_enhanced",
            scan_options=ScanOptions()
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_service_contract(self):
        """Test that ScanService implements the frozen API contract."""
        service = ScanService()
        
        # Verify all required methods exist and are callable
        required_methods = [
            'start_scan', 'get_scan_progress', 'get_scan_results',
            'cancel_scan', 'stream_scan_events', 'update_finding_status',
            'get_scan_history', 'export_scan_report', 'get_system_status'
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(service, method_name), 
                          f"Missing required method: {method_name}")
            self.assertTrue(callable(getattr(service, method_name)), 
                          f"Method not callable: {method_name}")
    
    def test_data_model_compatibility(self):
        """Test that data models maintain backward compatibility."""
        from sentinel.rules.base import Finding
        
        # Test that EnhancedFinding can be created from basic Finding
        basic_finding = Finding(
            rule_id="test-rule",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            excerpt="test code",
            confidence=0.8
        )
        
        enhanced = EnhancedFinding(
            id="test-id",
            rule_id=basic_finding.rule_id,
            rule_name="Test Rule",
            file_path=basic_finding.file_path,
            line=basic_finding.line,
            severity=basic_finding.severity,
            confidence=basic_finding.confidence,
            excerpt=basic_finding.excerpt,
            category="test",
            tags=[],
            file_language="python"
        )
        
        # Verify core fields are preserved
        self.assertEqual(enhanced.rule_id, basic_finding.rule_id)
        self.assertEqual(enhanced.file_path, basic_finding.file_path)
        self.assertEqual(enhanced.line, basic_finding.line)
        self.assertEqual(enhanced.severity, basic_finding.severity)
        self.assertEqual(enhanced.excerpt, basic_finding.excerpt)
        self.assertEqual(enhanced.confidence, basic_finding.confidence)
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_start_scan_success(self, mock_run_scan):
        """Test successful scan start."""
        scan_id = self.service.start_scan(self.test_config)
        
        self.assertIsInstance(scan_id, str)
        self.assertGreater(len(scan_id), 0)
        self.assertIn(scan_id, self.service._active_scans)
        
        active_scan = self.service._active_scans[scan_id]
        self.assertEqual(active_scan.config, self.test_config)
        self.assertEqual(active_scan.status, "queued")
    
    def test_start_scan_invalid_config(self):
        """Test scan start with invalid configuration."""
        invalid_config = ScanConfig(
            target_path=pathlib.Path("/nonexistent/path"),
            enable_ai=False
        )
        
        with self.assertRaises(InvalidConfigError) as context:
            self.service.start_scan(invalid_config)
        
        self.assertEqual(context.exception.error_code, "INVALID_CONFIG")
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_start_scan_concurrent_limit(self, mock_run_scan):
        """Test concurrent scan limit enforcement."""
        # Fill up the concurrent scan slots
        for i in range(5):
            config = ScanConfig(
                target_path=pathlib.Path(self.temp_dir) / f"project{i}",
                enable_ai=False
            )
            self.service.start_scan(config)
        
        # Try to start another scan
        with self.assertRaises(ScanAlreadyRunningError) as context:
            self.service.start_scan(self.test_config)
        
        self.assertEqual(context.exception.error_code, "SCAN_ALREADY_RUNNING")
    
    def test_get_scan_progress_not_found(self):
        """Test getting progress for non-existent scan."""
        with self.assertRaises(ScanNotFoundError) as context:
            self.service.get_scan_progress("nonexistent-scan-id")
        
        self.assertEqual(context.exception.error_code, "SCAN_NOT_FOUND")
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_get_scan_progress_success(self, mock_run_scan):
        """Test getting progress for existing scan."""
        scan_id = self.service.start_scan(self.test_config)
        progress = self.service.get_scan_progress(scan_id)
        
        self.assertIsInstance(progress, ScanProgress)
        self.assertEqual(progress.scan_id, scan_id)
        self.assertEqual(progress.status, "queued")
    
    def test_get_scan_results_not_found(self):
        """Test getting results for non-existent scan."""
        with self.assertRaises(ScanNotFoundError) as context:
            self.service.get_scan_results("nonexistent-scan-id")
        
        self.assertEqual(context.exception.error_code, "SCAN_NOT_FOUND")
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_get_scan_results_in_progress(self, mock_run_scan):
        """Test getting results for in-progress scan."""
        scan_id = self.service.start_scan(self.test_config)
        
        with self.assertRaises(ScanInProgressError) as context:
            self.service.get_scan_results(scan_id)
        
        self.assertEqual(context.exception.error_code, "SCAN_IN_PROGRESS")
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_cancel_scan_success(self, mock_run_scan):
        """Test successful scan cancellation."""
        scan_id = self.service.start_scan(self.test_config)
        
        result = self.service.cancel_scan(scan_id)
        self.assertTrue(result)
        
        active_scan = self.service._active_scans[scan_id]
        self.assertEqual(active_scan.status, "cancelled")
    
    def test_cancel_scan_not_found(self):
        """Test cancelling non-existent scan."""
        with self.assertRaises(ScanNotFoundError) as context:
            self.service.cancel_scan("nonexistent-scan-id")
        
        self.assertEqual(context.exception.error_code, "SCAN_NOT_FOUND")
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_stream_scan_events_completed(self, mock_run_scan):
        """Test event streaming for completed scan."""
        # Create a completed scan
        scan_id = self.service.start_scan(self.test_config)
        active_scan = self.service._active_scans[scan_id]
        active_scan.status = "completed"
        active_scan.findings = [
            EnhancedFinding(
                id="test-finding-1",
                rule_id="test-rule",
                rule_name="Test Rule",
                file_path=pathlib.Path("test.py"),
                line=1,
                severity="high",
                confidence=0.8,
                excerpt="test code",
                category="test",
                tags=[],
                file_language="python"
            )
        ]
        
        events = list(self.service.stream_scan_events(scan_id))
        
        self.assertGreater(len(events), 0)
        
        # Check event types
        event_types = [event.event_type for event in events]
        self.assertIn(ScanEventTypes.SCAN_STARTED, event_types)
        self.assertIn(ScanEventTypes.FINDING_DETECTED, event_types)
        self.assertIn(ScanEventTypes.SCAN_COMPLETED, event_types)
    
    def test_stream_scan_events_not_found(self):
        """Test event streaming for non-existent scan."""
        with self.assertRaises(ScanNotFoundError) as context:
            next(self.service.stream_scan_events("nonexistent-scan-id"))
        
        self.assertEqual(context.exception.error_code, "SCAN_NOT_FOUND")
    
    def test_update_finding_status_invalid_status(self):
        """Test updating finding status with invalid status."""
        with self.assertRaises(InvalidStatusError) as context:
            self.service.update_finding_status("test-finding", "invalid_status")
        
        self.assertEqual(context.exception.error_code, "INVALID_STATUS")
    
    def test_update_finding_status_not_found(self):
        """Test updating status for non-existent finding."""
        with self.assertRaises(FindingNotFoundError) as context:
            self.service.update_finding_status("nonexistent-finding", "resolved")
        
        self.assertEqual(context.exception.error_code, "FINDING_NOT_FOUND")
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_update_finding_status_success(self, mock_run_scan):
        """Test successful finding status update."""
        # Create a scan with a finding
        scan_id = self.service.start_scan(self.test_config)
        active_scan = self.service._active_scans[scan_id]
        
        finding = EnhancedFinding(
            id="test-finding",
            rule_id="test-rule",
            rule_name="Test Rule",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            confidence=0.8,
            excerpt="test code",
            category="test",
            tags=[],
            file_language="python"
        )
        active_scan.findings = [finding]
        
        result = self.service.update_finding_status("test-finding", "resolved", "Fixed the issue")
        self.assertTrue(result)
        
        self.assertEqual(finding.resolution_status, "resolved")
        self.assertEqual(finding.user_notes, "Fixed the issue")
        self.assertTrue(finding.is_resolved)
    
    def test_get_scan_history_empty(self):
        """Test getting scan history when empty."""
        history = self.service.get_scan_history()
        self.assertEqual(history, [])
    
    def test_get_scan_history_with_limit(self):
        """Test getting scan history with limit."""
        # Add some mock history
        for i in range(5):
            summary = ScanSummary(
                scan_id=f"scan-{i}",
                timestamp=datetime.utcnow().isoformat(),
                target_directory=pathlib.Path(f"/test/{i}"),
                total_files=10,
                files_with_issues=2,
                total_findings=5,
                severity_breakdown={"high": 2, "medium": 3},
                scan_duration_seconds=1.5
            )
            self.service._scan_history.append(summary)
        
        history = self.service.get_scan_history(limit=3)
        self.assertEqual(len(history), 3)
    
    @patch('sentinel.api.scan_service.ScanService._run_scan')
    def test_export_scan_report_json(self, mock_run_scan):
        """Test exporting scan report as JSON."""
        scan_id = self.service.start_scan(self.test_config)
        active_scan = self.service._active_scans[scan_id]
        active_scan.status = "completed"
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            output_path = pathlib.Path(temp_file.name)
        
        try:
            result = self.service.export_scan_report(scan_id, "json", output_path)
            self.assertTrue(result)
            self.assertTrue(output_path.exists())
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_export_scan_report_not_found(self):
        """Test exporting report for non-existent scan."""
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            output_path = pathlib.Path(temp_file.name)
            
            with self.assertRaises(ScanNotFoundError) as context:
                self.service.export_scan_report("nonexistent-scan", "json", output_path)
            
            self.assertEqual(context.exception.error_code, "SCAN_NOT_FOUND")
    
    def test_export_scan_report_unsupported_format(self):
        """Test exporting report with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_file:
            output_path = pathlib.Path(temp_file.name)
            
            with self.assertRaises(ExportError) as context:
                self.service.export_scan_report("test-scan", "pdf", output_path)
            
            self.assertEqual(context.exception.error_code, "EXPORT_ERROR")
    
    @patch('sentinel.llm.provider.get_available_providers')
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.disk_usage')
    @patch('psutil.Process')
    def test_get_system_status(self, mock_process, mock_disk, mock_cpu, mock_memory, mock_providers):
        """Test getting system status."""
        # Mock system resources
        mock_memory.return_value.used = 1024 * 1024 * 500  # 500MB
        mock_cpu.return_value = 25.5
        mock_disk.return_value.used = 1024 * 1024 * 1024 * 10  # 10GB
        mock_process.return_value.num_threads.return_value = 8
        mock_providers.return_value = ["deepseek", "openai"]
        
        status = self.service.get_system_status()
        
        self.assertIsInstance(status, SystemStatus)
        self.assertEqual(status.version, "0.2.0")
        self.assertEqual(status.ai_providers_available, ["deepseek", "openai"])
        self.assertEqual(status.active_scans, 0)
        self.assertEqual(status.system_resources.memory_usage_mb, 500.0)
        self.assertEqual(status.system_resources.cpu_percentage, 25.5)
        self.assertEqual(status.system_resources.disk_usage_gb, 10.0)
        self.assertEqual(status.system_resources.active_threads, 8)


class TestErrorHierarchy(unittest.TestCase):
    """Test the CodeSentinel error hierarchy."""
    
    def test_base_error_creation(self):
        """Test creating base CodeSentinelError."""
        error = CodeSentinelError(
            message="Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.error_code, "TEST_ERROR")
        self.assertEqual(error.details, {"key": "value"})
        self.assertEqual(str(error), "Test error")
    
    def test_error_inheritance(self):
        """Test that specific errors inherit from CodeSentinelError."""
        errors = [
            InvalidConfigError("Invalid config", "INVALID_CONFIG"),
            ScanNotFoundError("Scan not found", "SCAN_NOT_FOUND"),
            ScanAlreadyRunningError("Too many scans", "SCAN_ALREADY_RUNNING"),
            ScanInProgressError("Scan in progress", "SCAN_IN_PROGRESS"),
            FileSystemError("File system error", "FILE_SYSTEM_ERROR"),
            FindingNotFoundError("Finding not found", "FINDING_NOT_FOUND"),
            InvalidStatusError("Invalid status", "INVALID_STATUS"),
            ExportError("Export failed", "EXPORT_ERROR")
        ]
        
        for error in errors:
            self.assertIsInstance(error, CodeSentinelError)


class TestEventStreaming(unittest.TestCase):
    """Test the event streaming functionality."""
    
    def test_event_creation(self):
        """Test creating different types of events."""
        from sentinel.api.events import (
            create_progress_event, create_finding_event, create_scan_started_event,
            create_scan_completed_event, create_scan_failed_event
        )
        
        scan_id = "test-scan"
        
        # Test progress event
        progress = ScanProgress(scan_id=scan_id, status="in_progress")
        progress_event = create_progress_event(scan_id, progress)
        self.assertEqual(progress_event.event_type, ScanEventTypes.PROGRESS_UPDATE)
        self.assertEqual(progress_event.scan_id, scan_id)
        
        # Test finding event
        finding = EnhancedFinding(
            id="test-finding",
            rule_id="test-rule",
            rule_name="Test Rule",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            confidence=0.8,
            excerpt="test code",
            category="test",
            tags=[],
            file_language="python"
        )
        finding_event = create_finding_event(scan_id, finding)
        self.assertEqual(finding_event.event_type, ScanEventTypes.FINDING_DETECTED)
        
        # Test scan started event
        started_event = create_scan_started_event(scan_id, {"target": "test"})
        self.assertEqual(started_event.event_type, ScanEventTypes.SCAN_STARTED)
        
        # Test scan completed event
        completed_event = create_scan_completed_event(scan_id, {"findings": 5})
        self.assertEqual(completed_event.event_type, ScanEventTypes.SCAN_COMPLETED)
        
        # Test scan failed event
        failed_event = create_scan_failed_event(scan_id, "Test error")
        self.assertEqual(failed_event.event_type, ScanEventTypes.SCAN_FAILED)


class TestBackendWiring(unittest.TestCase):
    """Test that ScanService properly wires to existing backend functionality."""
    
    @patch('sentinel.scanner.walker.walk_directory')
    def test_file_discovery_wiring(self, mock_walk):
        """Test that file discovery wires to walk_directory."""
        mock_walk.return_value = [pathlib.Path("test1.py"), pathlib.Path("test2.py")]
        
        service = ScanService()
        config = ScanConfig(target_path=pathlib.Path("."))
        
        files = service._discover_files(config)
        
        mock_walk.assert_called_once()
        self.assertEqual(len(files), 2)
    
    @patch('sentinel.scanner.engine.run_rules')
    def test_rule_execution_wiring(self, mock_run_rules):
        """Test that rule execution wires to run_rules."""
        from sentinel.rules.base import Finding
        
        mock_finding = Finding(
            rule_id="test-rule",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            excerpt="test code",
            confidence=0.8
        )
        mock_run_rules.return_value = [mock_finding]
        
        service = ScanService()
        files = [pathlib.Path("test.py")]
        
        findings = service._execute_rules(files)
        
        mock_run_rules.assert_called_once_with(files)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "test-rule")
    
    @patch('sentinel.llm.explainer.ExplanationEngine')
    @patch('sentinel.llm.provider.get_provider')
    def test_ai_enhancement_wiring(self, mock_get_provider, mock_explainer):
        """Test that AI enhancement wires to ExplanationEngine."""
        from sentinel.rules.base import Finding
        
        # Mock the AI components
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        
        mock_explainer_instance = MagicMock()
        mock_explainer.return_value = mock_explainer_instance
        mock_explainer_instance.explain_finding.return_value = {
            "explanation": "AI explanation",
            "remediation": "Fix this",
            "cwe_id": "CWE-79",
            "risk_score": 7.5,
            "references": ["https://example.com"]
        }
        
        service = ScanService()
        config = ScanConfig(target_path=pathlib.Path("."), enable_ai=True, llm_provider="deepseek")
        
        finding = Finding(
            rule_id="test-rule",
            file_path=pathlib.Path("test.py"),
            line=1,
            severity="high",
            excerpt="test code",
            confidence=0.8
        )
        
        enhanced_findings = service._enhance_findings([finding], config)
        
        mock_get_provider.assert_called_once_with("deepseek")
        mock_explainer.assert_called_once()
        mock_explainer_instance.explain_finding.assert_called_once_with(finding, mock_provider)
        
        self.assertEqual(len(enhanced_findings), 1)
        self.assertEqual(enhanced_findings[0].ai_explanation, "AI explanation")
        self.assertEqual(enhanced_findings[0].cwe_id, "CWE-79")


if __name__ == '__main__':
    unittest.main()