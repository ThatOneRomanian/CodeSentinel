"""
API module for CodeSentinel Phase 3 GUI integration.

Provides a frozen, stable API surface for GUI integration while wrapping
existing backend functionality without modification.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

from sentinel.api.scan_service import ScanService, ScanConfig, ScanOptions
from sentinel.api.models import (
    EnhancedFinding, ScanProgress, ScanSummary, ScanEvent, 
    ScanResults, SystemStatus, SystemResources, ScanRecommendations,
    CodeContext, SharedConfig, UserPreferences, ProjectHistory,
    CodeSentinelError, InvalidConfigError, ScanNotFoundError,
    ScanAlreadyRunningError, ScanInProgressError, FileSystemError,
    AIProviderError, FindingNotFoundError, InvalidStatusError, ExportError
)
from sentinel.api.events import ScanEventTypes, create_progress_event, create_finding_event

__all__ = [
    # Core service
    "ScanService", "ScanConfig", "ScanOptions",
    
    # Data models
    "EnhancedFinding", "ScanProgress", "ScanSummary", "ScanEvent",
    "ScanResults", "SystemStatus", "SystemResources", "ScanRecommendations",
    "CodeContext", "SharedConfig", "UserPreferences", "ProjectHistory",
    
    # Error hierarchy
    "CodeSentinelError", "InvalidConfigError", "ScanNotFoundError",
    "ScanAlreadyRunningError", "ScanInProgressError", "FileSystemError",
    "AIProviderError", "FindingNotFoundError", "InvalidStatusError", "ExportError",
    
    # Event system
    "ScanEventTypes", "create_progress_event", "create_finding_event",
]