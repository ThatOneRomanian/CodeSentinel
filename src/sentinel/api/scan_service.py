"""
ScanService implementation for CodeSentinel Phase 3 API.

Provides a frozen API surface for GUI integration while wrapping existing
backend functionality without modification.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pathlib
import uuid
import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Iterator, Any
from dataclasses import dataclass, field

# Use relative imports within the API package
from .models import (
    ScanConfig, ScanOptions, EnhancedFinding, ScanProgress, ScanSummary,
    ScanResults, SystemStatus, SystemResources, ScanRecommendations,
    CodeContext, CodeSentinelError, InvalidConfigError, ScanNotFoundError,
    ScanAlreadyRunningError, ScanInProgressError, FileSystemError,
    AIProviderError, FindingNotFoundError, InvalidStatusError, ExportError,
    ERROR_CODES
)
from .events import (
    ScanEvent, ScanEventTypes, create_progress_event, create_finding_event,
    create_scan_started_event, create_scan_completed_event, create_scan_failed_event,
    create_file_processed_event, create_error_event
)
from .config_manager import ConfigManager


logger = logging.getLogger(__name__)


@dataclass
class ActiveScan:
    """Internal representation of an active scan session."""
    
    scan_id: str
    config: ScanConfig
    status: str = "queued"  # queued, in_progress, completed, failed, cancelled
    progress: ScanProgress = field(default_factory=lambda: ScanProgress("", "queued"))
    findings: List[EnhancedFinding] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None


class ScanService:
    """
    Primary service interface for CodeSentinel scanning operations.
    
    This class provides a stable, frozen API surface for GUI integration
    while wrapping existing backend functionality.
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        """
        Initialize the scan service.

        Args:
            config: Optional default configuration for scans
        """
        self._config_manager = ConfigManager()
        shared_config = self._config_manager.load_config()

        self._config = config or shared_config.scan_defaults
        self._shared_config = shared_config

        self._active_scans: Dict[str, ActiveScan] = {}
        self._scan_history: List[ScanSummary] = []
        self._max_concurrent_scans = 5
    
    # existing methods unchanged...
    
    def _run_scan(self, active_scan: ActiveScan) -> None:
        """Run a scan synchronously (for this implementation)."""
        profiling_enabled = active_scan.config.scan_options.enable_profiling
        
        def record_phase(phase: str, duration: float):
            if profiling_enabled:
                active_scan.progress.profiling_timers[phase] = duration
        
        try:
            active_scan.status = "in_progress"
            active_scan.progress.status = "in_progress"
            active_scan.progress.timestamp = datetime.utcnow().isoformat()
            
            step_start = time.perf_counter()
            files = self._discover_files(active_scan.config)
            record_phase("discover_files", time.perf_counter() - step_start)
            active_scan.progress.total_files = len(files)
            active_scan.progress.timestamp = datetime.utcnow().isoformat()
            
            step_start = time.perf_counter()
            basic_findings = self._execute_rules(files)
            record_phase("execute_rules", time.perf_counter() - step_start)
            active_scan.progress.findings_count = len(basic_findings)
            active_scan.progress.timestamp = datetime.utcnow().isoformat()
            
            step_start = time.perf_counter()
            enhanced_findings = self._enhance_findings(basic_findings, active_scan.config) if active_scan.config.enable_ai else self._convert_to_enhanced_findings(basic_findings)
            record_phase("enhance_findings", time.perf_counter() - step_start)
            active_scan.findings = enhanced_findings
            
            # completion...
        except Exception:
            # error handling unchanged
            raise
    
    def _get_code_context(self, file_path: pathlib.Path, line: Optional[int]) -> CodeContext:
        """Get expanded code context for a finding."""
        if line is None:
            return CodeContext()
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            before_lines = lines[max(0, line-3):line-1] if line > 1 else []
            after_lines = lines[line:min(len(lines), line+2)] if line < len(lines) else []
            return CodeContext(
                before="\n".join(before_lines) if before_lines else None,
                after="\n".join(after_lines) if after_lines else None,
                full_function=None
            )
        except Exception:
            return CodeContext()