# CodeSentinel Phase 3: GUI MVP Specification

## Overview

This specification outlines the design and implementation plan for CodeSentinel Phase 3 - a local-first GUI that builds upon the existing CLI/core architecture without requiring rewrites. The GUI will provide an accessible interface for developers and students while maintaining the project's local-first, privacy-first principles.

## Target User & Use Cases

### Primary Phase 3 Persona
- **Student/Developer on Laptop**: Individual developer working on personal or educational projects
- **Technical Level**: Comfortable with basic security concepts but prefers visual interfaces
- **Environment**: Local development machine (Windows, macOS, Linux)
- **Workflow**: Periodic security scanning during development, not continuous monitoring

### Minimum Viable Workflows

#### 1. Project Selection & Scan Initiation
- Choose project folder via file browser
- View recent project history (last 5 scans)
- One-click scan initiation with default settings
- Real-time scan progress visualization

#### 2. Results Review & Filtering
- View aggregated scan results with severity breakdown
- Filter findings by:
  - Severity level (high, medium, low)
  - File path/pattern
  - Rule type/category
  - Confidence score threshold
- Group findings by file, rule, or severity

#### 3. Individual Finding Analysis
- View detailed finding information including:
  - Code excerpt with syntax highlighting
  - Rule description and metadata
  - AI-generated explanation (when configured)
  - Remediation guidance
  - CWE references and risk score
- Navigate between findings with keyboard shortcuts

## Architecture Choice

### Recommendation: Local Web UI

**Rationale:**
- **Cross-Platform Compatibility**: Web technologies work consistently across Windows, macOS, Linux
- **Integration Flexibility**: Can run as local server, communicate via API with Python backend
- **Future Extensibility**: Web-based architecture naturally extends to Phase 4 cloud dashboard
- **Development Efficiency**: Rich ecosystem of visualization libraries (charts, tables, syntax highlighting)
- **User Experience**: Modern, responsive interfaces with minimal installation footprint

**Alternative Considered: TUI (Terminal User Interface)**
- **Pros**: Terminal-native, no browser dependency, potentially faster
- **Cons**: Limited visualization capabilities, steeper learning curve, less extensible for Phase 4
- **Decision**: Web UI better aligns with long-term vision and user accessibility goals

### Technical Stack Selection
- **Frontend**: React + TypeScript (for type safety and component reusability)
- **Backend Integration**: FastAPI (Python) serving as bridge between GUI and existing CLI core
- **Communication**: REST API for scan control, WebSocket for real-time progress
- **Packaging**: Electron for desktop distribution, with option for browser-only usage

## Integration Strategy

### Communication Approach: Hybrid API + CLI

**Recommended Architecture:**
```
GUI Layer (React/Electron)
    ↓ HTTP/REST + WebSocket
API Bridge (FastAPI)
    ↓ Python Subprocess/Import
Existing CLI Core (No Changes)
    ↓
Scan Results & Real-time Updates
```

**Implementation Details:**

1. **Direct Python API Integration** (Primary):
   - Import and call existing scanning modules directly
   - Leverage [`run_rules()`](src/sentinel/scanner/engine.py:1) from [`engine.py`](src/sentinel/scanner/engine.py)
   - Use [`walk_directory()`](src/sentinel/scanner/walker.py:1) from [`walker.py`](src/sentinel/scanner/walker.py)
   - Access [`ExplanationEngine`](src/sentinel/llm/explainer.py:20) from [`explainer.py`](src/sentinel/llm/explainer.py)

2. **CLI Shell-Out Fallback** (Backup):
   - Execute `codesentinel scan --format json` as subprocess
   - Parse JSON output for display
   - Used only if direct API integration encounters issues

**Rationale for Direct API Approach:**
- **Performance**: No process startup overhead for repeated scans
- **Real-time Data**: Can stream progress updates during scanning
- **Error Handling**: Better integration with existing exception handling
- **Future Proof**: Easier to extend with new features

## Data Model & API

### Backend-Frontend Communication Structure

#### Scan Configuration
```json
{
  "target_path": "/path/to/project",
  "enable_ai": true,
  "llm_provider": "deepseek",
  "output_format": "gui_enhanced",
  "scan_options": {
    "include_patterns": ["*.py", "*.js", "*.json"],
    "exclude_patterns": [".git", "node_modules"],
    "max_file_size": 10485760
  }
}
```

#### Real-time Scan Progress
```json
{
  "scan_id": "scan_12345",
  "status": "in_progress",
  "current_file": "src/app.py",
  "files_processed": 45,
  "total_files": 120,
  "findings_count": 8,
  "estimated_time_remaining": 45
}
```

#### Enhanced Finding Representation
```json
{
  "scan_summary": {
    "scan_id": "scan_12345",
    "timestamp": "2025-11-29T02:42:33Z",
    "target_directory": "/path/to/project",
    "total_files": 120,
    "files_with_issues": 15,
    "total_findings": 23,
    "severity_breakdown": {
      "high": 5,
      "medium": 10,
      "low": 8
    },
    "scan_duration_seconds": 12.5
  },
  "findings": [
    {
      "id": "finding_67890",
      "rule_id": "hardcoded-api-key",
      "rule_name": "Hardcoded API Key Detection",
      "file_path": "config.py",
      "line": 15,
      "severity": "high",
      "confidence": 0.92,
      "excerpt": "api_key = \"AKIAIOSFODNN7EXAMPLE\"",
      "category": "secrets",
      "tags": ["aws", "api-key", "hardcoded"],
      
      // AI-enhanced fields (when available)
      "ai_explanation": "This appears to be an AWS Access Key ID...",
      "remediation": "Rotate the exposed AWS access key immediately...",
      "cwe_id": "CWE-798",
      "risk_score": 8.7,
      "references": [
        "https://cwe.mitre.org/data/definitions/798.html"
      ],
      
      // GUI-specific enhancements
      "code_context": {
        "before": "def initialize_api():",
        "after": "return api_client"
      },
      "file_language": "python",
      "is_resolved": false,
      "user_notes": ""
    }
  ],
  "recommendations": {
    "immediate_actions": [
      "Rotate exposed AWS credentials",
      "Review hardcoded database passwords"
    ],
    "prevention": [
      "Add .env to .gitignore",
      "Use environment variables"
    ]
  }
}
```

### API Endpoints

#### Scan Management
- `POST /api/scans` - Start new scan
- `GET /api/scans/{scan_id}` - Get scan results
- `GET /api/scans/{scan_id}/progress` - Real-time progress (WebSocket)
- `DELETE /api/scans/{scan_id}` - Cancel ongoing scan

#### Project History
- `GET /api/projects` - List recent projects
- `GET /api/projects/{project_path}/scans` - Scan history for project
- `DELETE /api/projects/{project_path}` - Remove project history

#### Finding Management
- `PATCH /api/findings/{finding_id}` - Update finding status (resolved, ignored)
- `POST /api/findings/{finding_id}/notes` - Add user notes
- `GET /api/findings/{finding_id}/context` - Get additional code context

## Screens & Flows (Text-Level)

### Core Application Screens

#### 1. Project Selection & Dashboard
**Purpose**: Entry point for choosing projects and viewing scan history

**Layout**:
- Left sidebar: Recent projects (max 5) with last scan date and finding count
- Main area: Project selection controls and welcome information
- Bottom status bar: Version info and settings access

**Interactions**:
- "Choose Project" button opens system file browser
- Recent project cards show:
  - Project name (folder name)
  - Last scan date and time
  - Total findings count with severity indicators
  - Quick "Rescan" button
- Drag-and-drop folder support
- Settings gear icon in corner for configuration

**Fields**:
- Project path (display only)
- Scan date (display only)
- Finding counts by severity (display only)

#### 2. Scan Configuration Modal
**Purpose**: Configure scan options before execution

**Layout**:
- Modal overlay on top of dashboard
- Form with scan options grouped by category
- Preview of selected project path
- Action buttons (Start Scan, Cancel)

**Configuration Options**:
- **Basic Options**:
  - Target path (pre-filled, editable)
  - Enable AI explanations (checkbox)
  - LLM provider dropdown (DeepSeek, OpenAI, LocalOllama)
- **Advanced Options** (collapsible):
  - File patterns to include (multi-select with common presets)
  - File patterns to exclude (multi-select with common presets)
  - Maximum file size (slider with MB units)
  - Scan depth limit (number input)

**Interactions**:
- Form validation for path existence
- Real-time preview of file count based on filters
- "Use Defaults" button to reset to recommended settings

#### 3. Scan Progress & Real-time Results
**Purpose**: Monitor ongoing scan and see findings as they're discovered

**Layout**:
- Top progress bar: Overall scan completion percentage
- Left panel: Real-time file processing list with status icons
- Right panel: Accumulating findings list with live updates
- Center: Scan statistics and visualization

**Components**:
- **Progress Indicators**:
  - Overall progress percentage
  - Files processed/total
  - Current file being scanned
  - Estimated time remaining
- **Real-time Findings**:
  - Live list of findings as they're discovered
  - Severity badges (color-coded)
  - File and rule information
  - Expandable details on click
- **Visualizations**:
  - Severity distribution pie chart
  - Files with issues vs clean files
  - Finding rate over time graph

**Interactions**:
- Pause/resume scan button
- Expand finding details inline
- Filter findings during scan
- Cancel scan with confirmation

#### 4. Scan Results Dashboard
**Purpose**: Comprehensive view of completed scan results

**Layout**:
- Header: Scan summary with key metrics
- Left sidebar: Filtering and grouping controls
- Main area: Findings table with sortable columns
- Right panel: Detailed finding view when selected

**Filtering Controls**:
- Severity toggle (high, medium, low)
- File path search with autocomplete
- Rule category multi-select
- Confidence score slider
- Show only unresolved findings toggle

**Grouping Options**:
- By severity (default)
- By file path
- By rule category
- By resolution status

**Findings Table Columns**:
- Severity (with color-coded indicator)
- File path (truncated with full path on hover)
- Rule name
- Line number
- Confidence score
- Resolution status (badge)
- Quick actions (resolve, ignore)

**Interactions**:
- Click row to show detailed view in right panel
- Sort by any column
- Bulk actions (resolve selected, export selected)
- Persistent filters across sessions

#### 5. Finding Detail View
**Purpose**: In-depth analysis of individual security finding

**Layout**:
- Split view or modal showing complete finding context
- Tabbed interface for different information types

**Tabs/Content**:
- **Overview** (default):
  - Code excerpt with syntax highlighting
  - Line numbers and file context
  - Severity and confidence indicators
  - Rule description and metadata
- **AI Explanation** (when available):
  - Security risk explanation
  - Business impact analysis
  - Remediation guidance with step-by-step instructions
  - CWE reference links
- **Code Context**:
  - Expanded code view (10 lines before/after)
  - File structure navigation
  - Quick jump to file in external editor
- **Resolution**:
  - Mark as resolved/ignored options
  - User notes field
  - Resolution reason selection

**Interactions**:
- Navigate between findings with arrow keys
- Copy code excerpts to clipboard
- Open file in default editor
- Add to ignore list with patterns
- Export individual finding report

## Phase 3 Scope vs Phase 4

### Phase 3 MVP Scope (Local-First GUI)

**Included Features**:
- Single-project scanning and analysis
- Basic project history (local storage)
- Real-time scan progress monitoring
- Finding filtering and grouping
- AI explanation integration (existing providers)
- Local results persistence
- Export reports (PDF, HTML, JSON)
- Basic settings configuration

**Excluded from Phase 3**:
- Multi-project dashboards
- Team collaboration features
- Cloud synchronization
- Advanced reporting and analytics
- User management and permissions
- Integration with external systems
- Historical trend analysis

### Future Hooks for Phase 4

**Data Model Extensions**:
- Scan IDs with UUIDs for cloud synchronization
- User accounts and project permissions
- Resolution workflow states (open, in-progress, resolved)
- Comment threads on findings
- Scan comparison and diff views

**Architecture Considerations**:
- API designed for both local and remote backends
- Modular authentication system
- Event sourcing for audit trails
- Plugin system for additional rule packs
- Webhook support for CI/CD integration

## Implementation Plan

### Milestone 1: Foundation & Basic UI (Week 1-2)
**Objective**: Establish GUI framework and basic project selection

**Tasks**:
- Set up React + TypeScript + Electron foundation
- Create basic project selection screen
- Implement file browser integration
- Design and implement core UI components
- Create basic navigation structure

**Files to Create**:
- `src/gui/` - New GUI source directory
- `src/gui/components/` - Reusable UI components
- `src/gui/screens/` - Main application screens
- `src/gui/api/` - API communication layer
- `src/gui/main.js` - Electron main process
- `src/gui/package.json` - GUI dependencies

### Milestone 2: API Bridge & Scan Integration (Week 3-4)
**Objective**: Connect GUI to existing CodeSentinel core

**Tasks**:
- Implement FastAPI bridge server
- Create direct Python API integration
- Add CLI fallback mechanism
- Implement real-time progress streaming
- Design and implement scan configuration UI

**Files to Create/Modify**:
- `src/sentinel/api/` - New API module
- `src/sentinel/api/server.py` - FastAPI server
- `src/sentinel/api/models.py` - API data models
- `src/sentinel/api/routes.py` - API endpoint definitions
- Enhance [`src/sentinel/cli/main.py`](src/sentinel/cli/main.py:1) with API-friendly methods

### Milestone 3: Results Visualization & Interaction (Week 5-6)
**Objective**: Complete scan results interface and user interactions

**Tasks**:
- Implement findings table with sorting/filtering
- Create detailed finding view with tabs
- Add real-time results during scanning
- Implement finding resolution workflow
- Add export functionality (PDF, HTML)

**Components to Build**:
- FindingsTable with virtual scrolling
- FindingDetail modal/tabbed interface
- Real-time progress indicators
- Filter and grouping controls
- Export dialog with format options

### Milestone 4: Polish & Performance (Week 7-8)
**Objective**: Refine user experience and ensure performance

**Tasks**:
- Optimize large results handling
- Add keyboard shortcuts and accessibility
- Implement settings persistence
- Add error handling and user feedback
- Performance testing with large codebases
- Cross-platform testing and packaging

**Final Deliverables**:
- Packaged Electron application for all platforms
- Standalone web version option
- Comprehensive user documentation
- Updated project README with GUI instructions

### Testing Strategy

**Unit Tests**:
- GUI component testing with React Testing Library
- API endpoint testing with pytest
- Integration tests for scan workflows

**Performance Testing**:
- Large codebase scanning (10k+ files)
- Memory usage monitoring during scans
- UI responsiveness with 1000+ findings

**Cross-Platform Testing**:
- Windows 10/11
- macOS (Intel & Apple Silicon)
- Linux (Ubuntu, Fedora)

## Risks & Open Questions

### Technical Risks

1. **Performance with Large Codebases**
   - **Mitigation**: Implement virtual scrolling, pagination, and progressive loading
   - **Fallback**: Offer simplified view for very large result sets

2. **Cross-Platform File System Issues**
   - **Mitigation**: Extensive testing on all target platforms
   - **Fallback**: Use Node.js fs module via Electron for consistent behavior

3. **Real-time Data Streaming Complexity**
   - **Mitigation**: Use WebSocket with reconnection logic
   - **Fallback**: Polling-based progress updates

### Design Decisions Pending

1. **Electron vs Pure Web App**
   - **Question**: Should we require Electron installation or offer browser-only mode?
   - **Recommendation**: Support both, with Electron as primary distribution

2. **Results Persistence Strategy**
   - **Question**: How much scan history should be stored locally?
   - **Recommendation**: Last 10 scans per project, with option to clear

3. **External Editor Integration**
   - **Question**: Which editors should we support for "Open in Editor" feature?
   - **Recommendation**: VS Code, Sublime Text, Atom with configurable commands

### Integration Concerns

1. **Backward Compatibility**
   - Ensure GUI works with existing CLI installation
   - Maintain ability to run scans without GUI

2. **Configuration Synchronization**
   - How to sync settings between CLI and GUI?
   - **Solution**: Shared configuration file in user home directory

3. **AI Provider Configuration**
   - Duplicate API key configuration between CLI and GUI
   - **Solution**: Centralized configuration management

## Success Metrics

### Phase 3 Completion Criteria
- [ ] User can select project folder and run scan via GUI
- [ ] Real-time progress is visible during scanning
- [ ] Findings can be filtered by severity, file, and rule
- [ ] Individual findings show AI explanations when configured
- [ ] Scan results can be exported to PDF/HTML
- [ ] Application runs on Windows, macOS, and Linux
- [ ] Performance: < 2GB memory usage with 1000+ findings
- [ ] User testing: 90% success rate on core workflows

This specification provides a comprehensive roadmap for implementing CodeSentinel Phase 3 GUI while building upon the solid foundation established in Phases 1 and 2. The local-first, privacy-first principles are maintained throughout the design.