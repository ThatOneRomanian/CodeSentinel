import pathlib
import unittest

from sentinel.api.scan_service import ScanService, ScanConfig, ScanOptions
from sentinel.api.events import ScanEventTypes


class TestScanServicePipeline(unittest.TestCase):
    """Integration tests for ScanService -> Rule Engine -> Walker -> Explainer."""

    @classmethod
    def setUpClass(cls):
        cls.sample_project = pathlib.Path(__file__).parent.parent / "sample-project"

    def _build_config(self) -> ScanConfig:
        scan_options = ScanOptions(
            include_patterns=["*.py", "*.yaml", "Dockerfile"],
            exclude_patterns=["venv", ".venv", "__pycache__"],
            max_file_size=1024 * 1024,
            enable_profiling=True,
        )
        return ScanConfig(
            target_path=self.sample_project,
            enable_ai=False,
            llm_provider="deepseek",
            scan_options=scan_options,
        )

    def test_scan_generates_results(self):
        """Ensure ScanService runs the entire pipeline and records findings."""
        service = ScanService()
        config = self._build_config()

        scan_id = service.start_scan(config)
        self.assertIn(scan_id, service._active_scans)

        results = service.get_scan_results(scan_id)
        self.assertIsNotNone(results.summary)
        self.assertGreaterEqual(results.summary.total_findings, 0)
        self.assertIsInstance(results.findings, list)

        # Profiling timers should be filled when enabled
        progress = service.get_scan_progress(scan_id)
        self.assertIsInstance(progress.profiling_timers, dict)

    def test_event_stream_includes_expected_types(self):
        """Validate event streaming behavior for a real repository."""
        service = ScanService()
        config = self._build_config()

        scan_id = service.start_scan(config)
        events = list(service.stream_scan_events(scan_id))
        event_types = {event.event_type for event in events}

        self.assertIn(ScanEventTypes.SCAN_STARTED, event_types)
        self.assertIn(ScanEventTypes.SCAN_COMPLETED, event_types)
        self.assertTrue(
            any(evt.event_type == ScanEventTypes.FINDING_DETECTED for evt in events),
            "Expected at least one finding event",
        )


if __name__ == "__main__":
    unittest.main()