# CodeSentinel Architecture

## System Overview

CodeSentinel is a local-first security scanner built with a modular, extensible architecture. The system is designed to operate entirely offline by default, with optional AI enhancements through a bring-your-own-LLM approach.

## Core Components

### 1. File Walker (`src/sentinel/scanner/walker.py`)
- **Purpose**: Recursively traverses directory structures
- **Key Features**:
  - Ignores common non-code directories (`.git`, `__pycache__`, etc.)
  - Handles symlinks and permission errors gracefully
  - Filters files by extension and type
  - Memory-efficient streaming of large codebases

### 2. Rule Engine (`src/sentinel/scanner/engine.py`)
- **Purpose**: Applies security rules to file contents
- **Key Features**:
  - Dynamic rule loading from rule packs
  - Abstract class protection and validation
  - Error resilience with detailed logging
  - Rule priority and severity management
  - Plugin architecture for extensibility

### 3. AI Layer (`src/sentinel/llm/`)
- **Purpose**: Optional AI-powered security analysis
- **Key Components**:
  - **Provider Abstraction** (`provider.py`): Unified interface for multiple LLM providers
  - **Explanation Engine** (`explainer.py`): Generates security insights and remediation
  - **Safety Layer** (`safety.py`): Prevents prompt injection and ensures secure API usage
  - **Caching** (`cache.py`): Optimizes performance and reduces API costs
  - **Validation** (`validation.py`): Ensures AI responses meet quality standards

### 4. CLI Interface (`src/sentinel/cli/main.py`)
- **Purpose**: Command-line interface for user interaction
- **Key Features**:
  - Multiple output formats (Markdown, JSON)
  - CI/CD mode with appropriate exit codes
  - AI feature flags and provider selection
  - Configuration through environment variables and CLI arguments

## Data Flow

```
Directory Input
    ↓
File Walker → File List
    ↓
Rule Engine → Security Findings
    ↓
AI Layer (Optional) → Enhanced Findings
    ↓
Reporting → Markdown/JSON Output
```

### Detailed Flow Description

1. **Input Processing**:
   - User provides target directory via CLI
   - File Walker recursively scans for relevant files
   - Files are filtered by type and extension

2. **Security Analysis**:
   - Rule Engine loads all available rule packs
   - Each file is processed by applicable rules
   - Findings are collected with metadata (file, line, severity, confidence)

3. **AI Enhancement (Optional)**:
   - If `--ai` flag is set, findings are sent to configured LLM provider
   - AI generates explanations, CWE mappings, and remediation guidance
   - Results are cached to optimize performance

4. **Output Generation**:
   - Findings are formatted according to `--format` option
   - Markdown: Human-readable reports with code excerpts
   - JSON: Machine-readable for CI/CD integration
   - Exit codes indicate scan results (0=clean, 1=issues, 2=error)

## Component Relationships

### Rule Engine Architecture
```
Rule Engine
├── Rule Loader
│   ├── Core Rules (secrets, configs)
│   ├── Docker Rules (future)
│   ├── GitHub Actions Rules (future)
│   └── Supply Chain Rules (future)
├── Rule Validator
│   ├── Abstract class protection
│   ├── Required attribute validation
│   └── Error handling
└── Rule Executor
    ├── File processing
    ├── Pattern matching
    └── Finding aggregation
```

### AI Provider Abstraction
```
AI Layer
├── Provider Interface
│   ├── DeepSeek Provider
│   ├── OpenAI Provider
│   └── Ollama Provider
├── Explanation Engine
│   ├── Prompt templates
│   ├── Response parsing
│   └── Quality validation
└── Safety & Caching
    ├── Input sanitization
    ├── Response validation
    └── Performance optimization
```

## Key Design Patterns

### 1. Plugin Architecture
- Rules are dynamically loaded from separate modules
- New rule packs can be added without modifying core engine
- Abstract base classes ensure consistency

### 2. Graceful Degradation
- AI features fall back gracefully when not configured
- Invalid rules are skipped without breaking the scan
- Permission errors are logged but don't stop execution

### 3. Local-First Philosophy
- Zero mandatory external dependencies
- All scanning happens on local machine
- Optional AI features require explicit user configuration

### 4. Extensible Reporting
- Multiple output formats through pluggable reporters
- JSON format designed for CI/CD integration
- Markdown format optimized for human readability

## Configuration Management

### Environment Variables
- `DEEPSEEK_API_KEY`: API key for DeepSeek provider
- `OPENAI_API_KEY`: API key for OpenAI provider
- `CODESENTINEL_CACHE_DIR`: Custom cache directory

### CLI Arguments
- `--format`: Output format (markdown/json)
- `--ai`: Enable AI explanations
- `--llm-provider`: Choose AI provider (deepseek/openai/ollama)
- `--ci`: CI mode with appropriate exit codes

## Performance Considerations

- **File Processing**: Stream-based to handle large files
- **AI Caching**: Responses cached to minimize API calls
- **Rule Optimization**: Rules designed for efficient pattern matching
- **Memory Management**: Generator-based processing for large codebases

## Security Considerations

- **No Data Upload**: All processing happens locally
- **API Key Security**: Keys passed via environment variables
- **Input Validation**: All user inputs and file contents are validated
- **Error Handling**: Fail-safe design prevents sensitive data exposure

## Future Architecture Directions

- **GUI Layer**: Cross-platform desktop application (Phase 3)
- **Cloud Dashboard**: Optional team collaboration features (Phase 4)
- **Advanced Rule Packs**: Docker, GitHub Actions, supply chain security
- **Performance Optimizations**: Parallel processing, incremental scanning

---

*Last Updated: 2025-11-29*
*Version: 0.2.0*