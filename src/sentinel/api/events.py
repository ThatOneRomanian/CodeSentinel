"""
Event system for CodeSentinel Phase 3 API.

Provides real-time event streaming for scan operations without modifying
existing backend functionality.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

from datetime import datetime
from typing import Any, Dict

# Use relative imports within the API package
from .models import ScanEvent, ScanProgress, EnhancedFinding


class ScanEventTypes:
    """Constants for scan event types."""
    
    PROGRESS_UPDATE = "progress_update"
    FINDING_DETECTED = "finding_detected"
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    SCAN_CANCELLED = "scan_cancelled"
    FILE_PROCESSED = "file_processed"
    ERROR_OCCURRED = "error_occurred"


def create_progress_event(scan_id: str, progress: ScanProgress) -> ScanEvent:
    """Create a progress update event."""
    return ScanEvent(
        event_type=ScanEventTypes.PROGRESS_UPDATE,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"progress": progress}
    )


def create_finding_event(scan_id: str, finding: EnhancedFinding) -> ScanEvent:
    """Create a finding detected event."""
    return ScanEvent(
        event_type=ScanEventTypes.FINDING_DETECTED,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"finding": finding}
    )


def create_scan_started_event(scan_id: str, config: Dict[str, Any]) -> ScanEvent:
    """Create a scan started event."""
    return ScanEvent(
        event_type=ScanEventTypes.SCAN_STARTED,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"config": config}
    )


def create_scan_completed_event(scan_id: str, summary: Dict[str, Any]) -> ScanEvent:
    """Create a scan completed event."""
    return ScanEvent(
        event_type=ScanEventTypes.SCAN_COMPLETED,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"summary": summary}
    )


def create_scan_failed_event(scan_id: str, error: str) -> ScanEvent:
    """Create a scan failed event."""
    return ScanEvent(
        event_type=ScanEventTypes.SCAN_FAILED,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"error": error}
    )


def create_file_processed_event(scan_id: str, file_path: str, findings_count: int) -> ScanEvent:
    """Create a file processed event."""
    return ScanEvent(
        event_type=ScanEventTypes.FILE_PROCESSED,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"file_path": file_path, "findings_count": findings_count}
    )


def create_error_event(scan_id: str, error: str, details: Dict[str, Any]) -> ScanEvent:
    """Create an error occurred event."""
    return ScanEvent(
        event_type=ScanEventTypes.ERROR_OCCURRED,
        scan_id=scan_id,
        timestamp=datetime.utcnow().isoformat(),
        data={"error": error, "details": details}
    )


__all__ = [
    "ScanEvent",
    "ScanEventTypes", 
    "create_progress_event",
    "create_finding_event",
    "create_scan_started_event",
    "create_scan_completed_event",
    "create_scan_failed_event",
    "create_file_processed_event",
    "create_error_event"
]