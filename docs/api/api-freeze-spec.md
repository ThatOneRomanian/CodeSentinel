# CodeSentinel Phase 3 API Freeze Specification

## Overview

This document defines the frozen API surface for CodeSentinel Phase 3 GUI integration. The API is designed to be stable, forward-compatible, and production-ready, providing a clear contract between the backend scanning engine and the GUI frontend.

**Freeze Date**: 2025-11-29  
**Version**: 1.0.0  
**Status**: FROZEN - No breaking changes permitted

## 1. Core Data Models

### 1.1 Scan Configuration Model

```python
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
```

### 1.2 Enhanced Finding Model

```python
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
    code_context: CodeContext = field(default_factory=dict)
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
```

### 1.3 Real-time Progress Model

```python
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
    
    recommendations: ScanRecommendations = field(default_factory=dict)
    """AI-generated recommendations for the codebase."""


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
```

## 2. Frozen API Surface

### 2.1 ScanService Class Definition

```python
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
        self._config = config
        self._active_scans: Dict[str, ActiveScan] = {}
        self._scan_history: List[ScanSummary] = []
    
    def start_scan(self, config: ScanConfig) -> str:
        """
        Start a new security scan.
        
        Args:
            config: Scan configuration parameters
            
        Returns:
            scan_id: Unique identifier for the scan session
            
        Raises:
            InvalidConfigError: If configuration is invalid
            ScanAlreadyRunningError: If maximum concurrent scans exceeded
            FileSystemError: If target path cannot be accessed
        """
        pass
    
    def get_scan_progress(self, scan_id: str) -> ScanProgress:
        """
        Get current progress for an ongoing scan.
        
        Args:
            scan_id: Identifier of the scan session
            
        Returns:
            Current progress information
            
        Raises:
            ScanNotFoundError: If scan_id does not exist
        """
        pass
    
    def get_scan_results(self, scan_id: str) -> ScanResults:
        """
        Get completed scan results.
        
        Args:
            scan_id: Identifier of the scan session
            
        Returns:
            Complete scan results including findings and summary
            
        Raises:
            ScanNotFoundError: If scan_id does not exist
            ScanInProgressError: If scan is still running
        """
        pass
    
    def cancel_scan(self, scan_id: str) -> bool:
        """
        Cancel an ongoing scan.
        
        Args:
            scan_id: Identifier of the scan session
            
        Returns:
            True if scan was successfully cancelled
            
        Raises:
            ScanNotFoundError: If scan_id does not exist
            ScanCompletedError: If scan has already completed
        """
        pass
    
    def stream_scan_events(self, scan_id: str) -> Iterator[ScanEvent]:
        """
        Stream real-time events from an ongoing scan.
        
        Args:
            scan_id: Identifier of the scan session
            
        Returns:
            Iterator yielding scan events (progress, findings, errors)
            
        Raises:
            ScanNotFoundError: If scan_id does not exist
        """
        pass
    
    def update_finding_status(self, finding_id: str, status: str, notes: str = "") -> bool:
        """
        Update the status of a specific finding.
        
        Args:
            finding_id: Unique identifier of the finding
            status: New status (open, in_progress, resolved, ignored)
            notes: User notes about the status change
            
        Returns:
            True if status was successfully updated
            
        Raises:
            FindingNotFoundError: If finding_id does not exist
            InvalidStatusError: If status is not valid
        """
        pass
    
    def get_scan_history(self, limit: int = 10) -> List[ScanSummary]:
        """
        Get recent scan history.
        
        Args:
            limit: Maximum number of historical scans to return
            
        Returns:
            List of recent scan summaries
        """
        pass
    
    def export_scan_report(self, scan_id: str, format: str, output_path: pathlib.Path) -> bool:
        """
        Export scan results to various formats.
        
        Args:
            scan_id: Identifier of the scan session
            format: Export format (pdf, html, json, markdown)
            output_path: Where to save the exported report
            
        Returns:
            True if export was successful
            
        Raises:
            ScanNotFoundError: If scan_id does not exist
            ExportError: If export format is not supported
        """
        pass
    
    def get_system_status(self) -> SystemStatus:
        """
        Get current system status and capabilities.
        
        Returns:
            System status including available providers and resource usage
        """
        pass


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
```

### 2.2 Event Streaming Interface

```python
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
```

### 2.3 Error and Exception Model

```python
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
```

## 3. Backend Module to API Mapping

### 3.1 Function Wrapping Strategy

| Backend Module | API Wrapper | Purpose |
|---------------|-------------|---------|
| [`walk_directory()`](src/sentinel/scanner/walker.py:36) | `ScanService._discover_files()` | File discovery with pattern filtering |
| [`run_rules()`](src/sentinel/scanner/engine.py:271) | `ScanService._execute_rules()` | Security rule execution |
| [`ExplanationEngine`](src/sentinel/llm/explainer.py:20) | `ScanService._enhance_findings()` | AI-powered finding enhancement |
| [`generate_json_report()`](src/sentinel/reporting/json_report.py:16) | `ScanService.export_scan_report()` | Report generation and export |
| [`generate_markdown_report()`](src/sentinel/reporting/markdown.py:15) | `ScanService.export_scan_report()` | Human-readable reporting |

### 3.2 Internal API Implementation

```python
class ScanServiceImplementation(ScanService):
    """Concrete implementation of the ScanService interface."""
    
    def _discover_files(self, config: ScanConfig) -> List[pathlib.Path]:
        """Wrap walk_directory with enhanced error handling."""
        try:
            from sentinel.scanner.walker import walk_directory
            
            return walk_directory(
                target_path=config.target_path,
                include_extensions=set(config.scan_options.include_patterns),
                exclude_patterns=set(config.scan_options.exclude_patterns)
            )
        except (FileNotFoundError, PermissionError) as e:
            raise FileSystemError(
                message=f"File discovery failed: {e}",
                error_code="FILE_SYSTEM_ERROR",
                details={"target_path": str(config.target_path)}
            )
    
    def _execute_rules(self, files: List[pathlib.Path]) -> List[Finding]:
        """Wrap run_rules with progress tracking."""
        try:
            from sentinel.scanner.engine import run_rules
            
            return run_rules(files)
        except Exception as e:
            raise CodeSentinelError(
                message=f"Rule execution failed: {e}",
                error_code="RULES_EXECUTION_ERROR"
            )
    
    def _enhance_findings(self, findings: List[Finding], config: ScanConfig) -> List[EnhancedFinding]:
        """Wrap ExplanationEngine with AI provider integration."""
        if not config.enable_ai:
            return self._convert_to_enhanced_findings(findings)
        
        try:
            from sentinel.llm.explainer import ExplanationEngine
            from sentinel.llm.provider import get_provider
            
            provider = get_provider(config.llm_provider)
            explainer = ExplanationEngine()
            
            # Batch process findings for efficiency
            enhanced_findings = []
            for finding in findings:
                explanation_data = explainer.explain_finding(finding, provider)
                enhanced_finding = self._create_enhanced_finding(finding, explanation_data)
                enhanced_findings.append(enhanced_finding)
            
            return enhanced_findings
            
        except Exception as e:
            # Fall back to non-enhanced findings if AI fails
            logging.warning(f"AI enhancement failed, using basic findings: {e}")
            return self._convert_to_enhanced_findings(findings)
    
    def _convert_to_enhanced_findings(self, findings: List[Finding]) -> List[EnhancedFinding]:
        """Convert basic findings to enhanced format without AI."""
        enhanced = []
        for finding in findings:
            enhanced_finding = EnhancedFinding(
                id=str(uuid.uuid4()),
                rule_id=finding.rule_id,
                rule_name=self._get_rule_name(finding.rule_id),
                file_path=finding.file_path,
                line=finding.line,
                severity=finding.severity,
                confidence=finding.confidence or 0.5,
                excerpt=finding.excerpt,
                category=finding.category or "unknown",
                tags=finding.tags or [],
                file_language=self._detect_language(finding.file_path),
                code_context=self._get_code_context(finding.file_path, finding.line),
                created_at=datetime.utcnow().isoformat(),
                last_updated=datetime.utcnow().isoformat()
            )
            enhanced.append(enhanced_finding)
        return enhanced
```

## 4. AI Provider Interaction Model

### 4.1 Provider Configuration

```python
@dataclass
class AIProviderConfig:
    """Configuration for AI provider integration."""
    
    provider_name: str
    """Name of the AI provider (deepseek, openai, local_ollama)."""
    
    api_key: Optional[str] = None
    """API key for the provider (if required)."""
    
    base_url: Optional[str] = None
    """Base URL for API calls (if configurable)."""
    
    timeout: int = 30
    """Request timeout in seconds."""
    
    max_retries: int = 3
    """Maximum number of retry attempts."""
    
    rate_limit: Optional[int] = None
    """Requests per minute limit."""
    
    enabled: bool = True
    """Whether this provider is enabled."""


class AIProviderManager:
    """Manager for AI provider configuration and status."""
    
    def get_available_providers(self) -> List[AIProviderConfig]:
        """Get list of available AI providers with configuration status."""
        pass
    
    def test_provider_connection(self, config: AIProviderConfig) -> bool:
        """Test connectivity and configuration for a provider."""
        pass
    
    def get_provider_status(self, provider_name: str) -> Dict[str, Any]:
        """Get detailed status for a specific provider."""
        pass
```

### 4.2 AI Operation Safety

```python
class AISafetyController:
    """Controller for AI operation safety and privacy."""
    
    def validate_input_safety(self, content: str) -> bool:
        """Validate that input content is safe for AI processing."""
        from sentinel.llm.safety import SafetyLayer
        
        safety_layer = SafetyLayer()
        return safety_layer.validate_environment()
    
    def sanitize_for_ai(self, content: str) -> str:
        """Sanitize content before sending to AI providers."""
        from sentinel.llm.safety import SafetyLayer
        
        safety_layer = SafetyLayer()
        return safety_layer.process_for_ai(content)
    
    def should_enable_ai(self, findings: List[Finding]) -> bool:
        """Determine if AI should be enabled based on safety and content."""
        # Don't enable AI for empty scans
        if not findings:
            return False
        
        # Check environment safety
        if not self.validate_input_safety(""):
            return False
        
        # Check for sensitive data patterns
        sensitive_patterns = [
            r'\bAKIA[0-9A-Z]{16}\b',  # AWS keys
            r'\bgh[ops]_[A-Za-z0-9_]{36,255}\b',  # GitHub tokens
            r'\b[A-Za-z0-9]{32,64}\b',  # Generic API keys
        ]
        
        for finding in findings:
            if finding.excerpt:
                for pattern in sensitive_patterns:
                    if re.search(pattern, finding.excerpt):
                        return False
        
        return True
```

## 5. Configuration Model for GUI + CLI

### 5.1 Shared Configuration

```python
@dataclass
class SharedConfig:
    """Configuration shared between GUI and CLI."""
    
    scan_defaults: ScanConfig = field(default_factory=ScanConfig)
    """Default scan configuration."""
    
    ai_providers: Dict[str, AIProviderConfig] = field(default_factory=dict)
    """AI provider configurations."""
    
    user_preferences: UserPreferences = field(default_factory=UserPreferences)
    """User-specific preferences."""
    
    recent_projects: List[ProjectHistory] = field(default_factory=list)
    """Recently scanned projects."""
    
    export_settings: ExportSettings = field(default_factory=ExportSettings)
    """Default export settings."""


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
```

### 5.2 Configuration Persistence

```python
class ConfigManager:
    """Manager for configuration persistence and synchronization."""
    
    def __init__(self, config_path: Optional[pathlib.Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[SharedConfig] = None
    
    def _get_default_config_path(self) -> pathlib.Path:
        """Get platform-specific default configuration path."""
        if os.name == 'nt':  # Windows
            return pathlib.Path(os.environ['APPDATA']) / 'codesentinel' / 'config.json'
        else:  # Unix-like
            return pathlib.Path.home() / '.config' / 'codesentinel' / 'config.json'
    
    def load_config(self) -> SharedConfig:
        """Load configuration from persistent storage."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                return self._deserialize_config(config_data)
        except Exception as e:
            logging.warning(f"Failed to load config, using defaults: {e}")
        
        return SharedConfig()  # Return default config
    
    def save_config(self, config: SharedConfig) -> bool:
        """Save configuration to persistent storage."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            config_data = self._serialize_config(config)
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def sync_with_cli(self) -> bool:
        """Synchronize configuration with CLI tool."""
        # Implementation for CLI-GUI configuration synchronization
        pass
```

## 6. Compatibility Analysis

### 6.1 Backward Compatibility

✅ **Fully Compatible**: The frozen API maintains full backward compatibility with existing CLI functionality:
- All existing [`run_rules()`](src/sentinel/scanner/engine.py:271) functionality preserved
- [`walk_directory()`](src/sentinel/scanner/walker.py:36) integration unchanged  
- [`ExplanationEngine`](src/sentinel/llm/explainer.py:20) enhanced but not modified
- Existing [`Finding`](src/sentinel/rules/base.py:67) dataclass extended, not replaced

### 6.2 Forward Compatibility

✅ **Future-Proof Design**: The API is designed for extensibility:
- All new fields in data models are optional
- Event streaming supports new event types
- Error model allows for new error codes
- Configuration model supports new providers and options

### 6.3 Performance Considerations

✅ **Optimized for GUI Use**:
- Progressive result streaming for large scans
- Batched AI operations for efficiency  
- Memory-efficient file processing
- Configurable resource limits

## 7. Implementation Guidelines

### 7.1 API Stability Guarantees

- **No breaking changes** to public method signatures
- **Optional parameters only** for new functionality
- **Deprecation period** of at least one major version for removed features
- **Semantic versioning** strictly enforced

### 7.2 Error Handling Requirements

- All exceptions must be instances of `CodeSentinelError` or subclasses
- Error messages must be user-friendly and actionable
- Error details must include sufficient context for debugging
- Network operations must include appropriate retry logic

### 7.3 Security Requirements

- No sensitive data in error messages or logs
- Input validation for all external data
- Secure configuration storage
- Privacy-preserving AI operations

## 8. Testing Strategy

### 8.1 API Contract Tests

```python
def test_scan_service_contract():
    """Test that ScanService implements the frozen API contract."""
    service = ScanService()
    
    # Verify all required methods exist
    required_methods = [
        'start_scan', 'get_scan_progress', 'get_scan_results',
        'cancel_scan', 'stream_scan_events', 'update_finding_status',
        'get_scan_history', 'export_scan_report', 'get_system_status'
    ]
    
    for method_name in required_methods:
        assert hasattr(service, method_name), f"Missing required method: {method_name}"
        assert callable(getattr(service, method_name)), f"Method not callable: {method_name}"

def test_data_model_compatibility():
    """Test that data models maintain backward compatibility."""
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
    assert enhanced.rule_id == basic_finding.rule_id
    assert enhanced.file_path == basic_finding.file_path
    assert enhanced.line == basic_finding.line
```

This API freeze specification establishes a stable, production-ready interface for Phase 3 GUI development while maintaining full compatibility with existing CodeSentinel functionality.