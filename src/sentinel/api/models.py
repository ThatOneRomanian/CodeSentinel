"""
Data models for CodeSentinel Phase 3 API freeze.

Defines all dataclasses and error hierarchy for the frozen API surface.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pathlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union


@dataclass
class ScanOptions:
    """Advanced scanning configuration options."""

    include_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.js", "*.json", "*.yaml", "*.yml", "*.env"])
    """File patterns to include in scanning."""

    exclude_patterns: List[str] = field(default_factory=lambda: [".git", "node_modules", "__pycache__", ".pytest_cache"])
    """File patterns to exclude from scanning."""

    max_file_size: int = 10485760  # 10MB
    """Maximum file size to process (bytes)."""

    scan_depth: Optional[int] = None
    """Maximum directory depth for recursive scanning."""

    enable_entropy_analysis: bool = True
    """Enable entropy-based secret detection."""

    confidence_threshold: float = 0.5
    """Minimum confidence threshold for reporting findings."""

    enable_profiling: bool = False
    """Enable profiling timers and diagnostics for large repositories."""


@dataclass
class ScanConfig:
    """Configuration for security scanning operations."""

    target_path: pathlib.Path
    """Directory or file path to scan."""

    enable_ai: bool = False
    """Enable AI-powered explanations and enhancements."""

    llm_provider: str = "deepseek"
    """LLM provider for AI features (deepseek, openai, local_ollama)."""

    output_format: str = "gui_enhanced"
    """Output format specification for GUI consumption."""

    scan_options: ScanOptions = field(default_factory=ScanOptions)
    """Advanced scanning configuration options."""

    enable_debug: bool = False
    """Enable verbose Debug logging within ScanService operations."""


@dataclass
class CodeContext:
    """Expanded code context for GUI display."""

    before: Optional[str] = None
    """Code lines before the finding (for context)."""

    after: Optional[str] = None
    """Code lines after the finding (for context)."""

    full_function: Optional[str] = None
    """Full function/method containing the finding."""

    syntax_highlighting: bool = True
    """Whether syntax highlighting should be applied."""


@dataclass
class EnhancedFinding:
    """Enhanced security finding with GUI-specific metadata."""

    # Core finding data (from Phase 1/2)
    id: str
    """Unique identifier for this finding instance."""

    rule_id: str
    """Identifier of the rule that generated this finding."""

    rule_name: str
    """Human-readable rule name."""

    file_path: pathlib.Path
    """Path to the file containing the finding."""

    line: Optional[int]
    """Line number where the finding was detected."""

    severity: str
    """Severity level (critical, high, medium, low, info)."""

    confidence: float
    """Confidence score (0.0 to 1.0)."""

    excerpt: Optional[str]
    """Code excerpt showing the detected issue."""

    category: str
    """Finding category (secrets, config, supply_chain, etc.)."""

    tags: List[str]
    """Additional categorization tags."""

    # AI-enhanced fields (from Phase 2)
    ai_explanation: Optional[str] = None
    """AI-generated security risk explanation."""

    remediation: Optional[str] = None
    """AI-generated remediation guidance."""

    cwe_id: Optional[str] = None
    """Common Weakness Enumeration identifier."""

    risk_score: Optional[float] = None
    """Numeric risk assessment score (1-10)."""

    references: List[str] = field(default_factory=list)
    """Reference URLs for additional information."""

    # GUI-specific enhancements
    code_context: CodeContext = field(default_factory=CodeContext)
    """Expanded code context for display."""

    file_language: str = "unknown"
    """Programming language of the file."""

    is_resolved: bool = False
    """Whether this finding has been marked as resolved."""

    user_notes: str = ""
    """User-provided notes about this finding."""

    resolution_status: str = "open"
    """Current resolution status (open, in_progress, resolved, ignored)."""

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    """Timestamp when finding was created."""

    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    """Timestamp when finding was last updated."""


@dataclass
class ScanProgress:
    """Real-time progress information for ongoing scans."""

    scan_id: str
    """Unique identifier for the scan session."""

    status: str
    """Current scan status (queued, in_progress, completed, failed, cancelled)."""

    current_file: Optional[str] = None
    """Current file being processed."""

    files_processed: int = 0
    """Number of files processed so far."""

    total_files: int = 0
    """Total number of files to process."""

    findings_count: int = 0
    """Number of findings detected so far."""

    estimated_time_remaining: Optional[int] = None
    """Estimated time remaining in seconds."""

    progress_percentage: float = 0.0
    """Overall progress percentage (0.0 to 100.0)."""

    current_operation: Optional[str] = None
    """Current operation being performed."""

    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    """Timestamp of this progress update."""

    profiling_timers: Dict[str, float] = field(default_factory=dict)
    """Timing information for each scanning phase (seconds)."""


@dataclass
class ScanRecommendations:
    """AI-generated security recommendations."""

    immediate_actions: List[str]
    """Actions that should be taken immediately."""

    prevention: List[str]
    """Preventative measures for future development."""

    priority_fixes: List[str]
    """High-priority fixes based on risk assessment."""

    technical_debt: List[str]
    """Technical debt and architectural improvements."""


@dataclass
class ScanSummary:
    """Comprehensive summary of completed scan results."""

    scan_id: str
    """Unique identifier for the scan session."""

    timestamp: str
    """When the scan was completed."""

    target_directory: pathlib.Path
    """Directory that was scanned."""

    total_files: int
    """Total number of files scanned."""

    files_with_issues: int
    """Number of files containing security issues."""

    total_findings: int
    """Total number of security findings."""

    severity_breakdown: Dict[str, int]
    """Count of findings by severity level."""

    scan_duration_seconds: float
    """How long the scan took to complete."""

    ai_enabled: bool = False
    """Whether AI explanations were enabled."""

    llm_provider: Optional[str] = None
    """Which LLM provider was used (if AI enabled)."""

    recommendations: ScanRecommendations = field(default_factory=lambda: ScanRecommendations([], [], [], []))
    """AI-generated recommendations for the codebase."""


@dataclass
class ScanResults:
    """Complete results from a security scan."""

    summary: ScanSummary
    """Summary statistics and metadata."""

    findings: List[EnhancedFinding]
    """All security findings from the scan."""

    recommendations: ScanRecommendations
    """AI-generated security recommendations."""

    raw_data: Optional[Dict] = None
    """Raw scan data for advanced processing."""


@dataclass
class SystemResources:
    """System resource usage information."""

    memory_usage_mb: float
    """Current memory usage in MB."""

    cpu_percentage: float
    """Current CPU usage percentage."""

    disk_usage_gb: float
    """Current disk usage in GB."""

    active_threads: int
    """Number of active threads."""


@dataclass
class SystemStatus:
    """Current system status and capabilities."""

    version: str
    """CodeSentinel version."""

    ai_providers_available: List[str]
    """Available AI providers with configuration status."""

    active_scans: int
    """Number of currently active scans."""

    system_resources: SystemResources
    """Current system resource usage."""

    rule_packs_loaded: List[str]
    """Loaded rule packs and their status."""


@dataclass
class ScanEvent:
    """Base class for all scan events."""

    event_type: str
    """Type of event (progress, finding, error, completion)."""

    scan_id: str
    """Associated scan session identifier."""

    timestamp: str
    """When the event occurred."""

    data: Dict[str, Any]
    """Event-specific data payload."""


@dataclass
class NotificationSettings:
    """Notification preferences for the GUI."""

    enable_toasts: bool = True
    """Display toast notifications."""

    enable_email_alerts: bool = False
    """Send email alerts for critical findings."""

    alert_level: str = "high"
    """Minimum severity that triggers notifications."""


@dataclass
class ExportSettings:
    """Default export settings shared between CLI and GUI."""

    default_format: str = "markdown"
    """Preferred export format."""

    auto_attach_history: bool = False
    """Automatically attach export history to reports."""

    legacy_output_path: Optional[pathlib.Path] = None
    """Optional legacy export path override."""


@dataclass
class AIProviderConfig:
    """Configuration for an individual AI provider."""

    provider_name: str
    """Name of the provider (deepseek, openai, local_ollama)."""

    api_key: Optional[str] = None
    """API key for the provider (if required)."""

    base_url: Optional[str] = None
    """Base URL for API calls (if configurable)."""

    timeout: int = 30
    """Request timeout in seconds."""

    max_retries: int = 3
    """Maximum number of retry attempts."""

    enabled: bool = True
    """Whether this provider is enabled."""


@dataclass
class UserPreferences:
    """User-specific preferences and settings."""

    theme: str = "dark"
    """UI theme preference."""

    default_severity_filter: List[str] = field(default_factory=lambda: ["high", "medium", "critical"])
    """Default severity levels to show."""

    auto_save_reports: bool = False
    """Whether to automatically save reports."""

    max_history_items: int = 50
    """Maximum number of historical scans to keep."""

    language: str = "en"
    """UI language preference."""

    notification_settings: NotificationSettings = field(default_factory=NotificationSettings)
    """Notification preferences."""


@dataclass
class ProjectHistory:
    """History of scans for a specific project."""

    project_path: pathlib.Path
    """Path to the project directory."""

    last_scan_date: str
    """When the project was last scanned."""

    total_findings: int
    """Total findings from last scan."""

    severity_breakdown: Dict[str, int]
    """Finding counts by severity."""

    scan_count: int = 1
    """Number of times this project has been scanned."""


@dataclass
class SharedConfig:
    """Configuration shared between GUI and CLI."""

    scan_defaults: ScanConfig = field(default_factory=lambda: ScanConfig(pathlib.Path(".")))
    """Default scan configuration."""

    ai_providers: Dict[str, AIProviderConfig] = field(default_factory=dict)
    """AI provider configurations."""

    user_preferences: UserPreferences = field(default_factory=UserPreferences)
    """User-specific preferences."""

    recent_projects: List[ProjectHistory] = field(default_factory=list)
    """Recently scanned projects."""

    export_settings: ExportSettings = field(default_factory=ExportSettings)
    """Default export settings."""

    notification_settings: NotificationSettings = field(default_factory=NotificationSettings)
    """Notification preferences."""
    

# Error hierarchy
class CodeSentinelError(Exception):
    """Base exception for all CodeSentinel errors."""

    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class InvalidConfigError(CodeSentinelError):
    """Raised when scan configuration is invalid."""
    pass


class ScanNotFoundError(CodeSentinelError):
    """Raised when a scan ID cannot be found."""
    pass


class ScanAlreadyRunningError(CodeSentinelError):
    """Raised when maximum concurrent scans are exceeded."""
    pass


class ScanInProgressError(CodeSentinelError):
    """Raised when an operation requires a completed scan."""
    pass


class FileSystemError(CodeSentinelError):
    """Raised for file system access issues."""
    pass


class AIProviderError(CodeSentinelError):
    """Raised when AI provider operations fail."""
    pass


class FindingNotFoundError(CodeSentinelError):
    """Raised when a finding ID cannot be found."""
    pass


class InvalidStatusError(CodeSentinelError):
    """Raised when an invalid status is provided."""
    pass


class ExportError(CodeSentinelError):
    """Raised when report export fails."""
    pass


# Error codes for consistent error handling
ERROR_CODES = {
    "INVALID_CONFIG": "Configuration parameters are invalid",
    "SCAN_NOT_FOUND": "Requested scan session does not exist",
    "SCAN_ALREADY_RUNNING": "Maximum concurrent scans exceeded",
    "SCAN_IN_PROGRESS": "Operation requires completed scan",
    "FILE_SYSTEM_ERROR": "File system access failed",
    "AI_PROVIDER_ERROR": "AI provider operation failed",
    "FINDING_NOT_FOUND": "Requested finding does not exist",
    "INVALID_STATUS": "Provided status is not valid",
    "EXPORT_ERROR": "Report export operation failed",
    "PERMISSION_DENIED": "Insufficient permissions for operation",
    "RESOURCE_EXHAUSTED": "System resources exhausted",
}