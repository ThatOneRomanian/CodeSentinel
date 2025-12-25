# CodeSentinel Phase 3 GUI Development Guide

## Overview

This guide provides comprehensive instructions for developing and running the CodeSentinel Phase 3 GUI. The GUI consists of:

- **Frontend**: React 18 + TypeScript (in `/gui` directory)
- **Backend Bridge**: FastAPI (in `src/sentinel/api/fastapi_bridge.py`)
- **Core Engine**: Existing CodeSentinel scanning logic (no changes needed)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React GUI (Port 3000)                   │
│  - Dashboard (Project Selection)                             │
│  - Scan Results (Findings Visualization)                     │
│  - Finding Details (AI Explanations)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API + WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│              FastAPI Bridge (Port 8000)                      │
│  - /api/scans (POST)           - Start scan                 │
│  - /api/scans/{id} (GET)       - Get results                │
│  - /api/scans/{id}/progress    - WebSocket stream           │
│  - /api/findings/{id} (GET)    - Finding details            │
│  - /api/findings/{id} (PATCH)  - Update finding status      │
│  - /api/projects (GET)         - Project history            │
└─────────────────────┬───────────────────────────────────────┘
                      │ Python Import
┌─────────────────────▼───────────────────────────────────────┐
│            CodeSentinel Core (Phase 3 API)                  │
│  - ScanService (Frozen Interface)                            │
│  - Rule Engine & Walker                                      │
│  - LLM Integration                                           │
│  - Reporting                                                 │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Backend Requirements
- Python 3.8+
- FastAPI and Uvicorn
- Existing CodeSentinel packages

### Frontend Requirements
- Node.js 16+
- npm or yarn

## Setup Instructions

### 1. Install Backend Dependencies

```bash
# In project root
pip install -e ".[dev]"  # Install CodeSentinel with dev dependencies
pip install fastapi uvicorn python-multipart
```

Or use the requirements file:

```bash
pip install -r requirements-gui.txt
```

### 2. Install Frontend Dependencies

```bash
cd gui
npm install
```

### 3. Environment Configuration

#### Backend (.env or environment variables)

```bash
# Optional: Configure LLM
export DEEPSEEK_API_KEY=sk_xxx...

# Optional: API port (default 8000)
export API_PORT=8000
```

#### Frontend (.env.local in gui/ directory)

```bash
# Optional: Backend API URL (default http://localhost:8000)
REACT_APP_API_URL=http://localhost:8000
```

## Running the Development Environment

### Option A: Separate Terminal Windows (Recommended)

**Terminal 1 - Backend FastAPI Server:**

```bash
# In project root
python -m sentinel.api.fastapi_bridge
```

This starts the FastAPI server on `http://localhost:8000`.

**Terminal 2 - Frontend Development Server:**

```bash
# In project root/gui
npm run dev
```

This starts Vite on `http://localhost:3000` with hot module reloading.

### Option B: Single Terminal with Background Process

```bash
# Start backend in background
python -m sentinel.api.fastapi_bridge &

# Start frontend
cd gui && npm run dev

# To stop backend later: kill %1
```

### Option C: Using VS Code Tasks

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "python",
      "args": ["-m", "sentinel.api.fastapi_bridge"],
      "isBackground": true,
      "problemMatcher": {
        "pattern": {
          "regexp": "^.*$",
          "file": 1,
          "location": 2,
          "message": 3
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": "^.*Uvicorn running.*",
          "endsPattern": "^.*Application startup complete.*"
        }
      }
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "npm",
      "args": ["run", "dev"],
      "cwd": "${workspaceFolder}/gui",
      "isBackground": true,
      "dependsOn": ["Start Backend"]
    }
  ]
}
```

Then run from VS Code: `Ctrl+Shift+B` → Select "Start Frontend"

## Testing Workflow

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "healthy", "version": "0.2.0", "api_version": "1.0.0"}
```

### 2. Manual API Testing

Start a scan:
```bash
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "target_path": "./sample-project",
    "enable_ai": false,
    "llm_provider": "deepseek",
    "include_patterns": ["*.py", "*.js"],
    "exclude_patterns": [".git", "node_modules"]
  }'
```

Get results:
```bash
curl http://localhost:8000/api/scans/{scan_id}
```

### 3. GUI Testing

1. Open http://localhost:3000 in your browser
2. Enter a project path (e.g., `./sample-project`)
3. Click "Start Scan"
4. Monitor progress and view results

## Development Tasks

### Frontend Development

```bash
cd gui

# Development with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend Development

```bash
# Run FastAPI with auto-reload
python -m sentinel.api.fastapi_bridge --reload

# Run with debug logging
LOGLEVEL=DEBUG python -m sentinel.api.fastapi_bridge
```

## Key Features to Implement

### Phase 1 (MVP - Current)
- ✅ Project selection screen
- ✅ Scan initiation
- ✅ Results dashboard
- ✅ Finding details view
- ✅ Severity filtering

### Phase 2 (Enhanced)
- ⏳ Real-time progress updates (WebSocket)
- ⏳ Project history/recent projects
- ⏳ Scan history comparison
- ⏳ Export reports (PDF/HTML)
- ⏳ Finding status management

### Phase 3 (Advanced)
- ⏳ Custom rule configuration
- ⏳ Scheduled scans
- ⏳ Multiple project dashboard
- ⏳ Team collaboration features

## Debugging Tips

### Frontend Issues

```bash
cd gui

# Check for type errors
npm run type-check

# View browser console (F12)
# Check Network tab for API calls

# Debug specific component
# Add breakpoints in Chrome DevTools
```

### Backend Issues

```bash
# Check API logs
python -m sentinel.api.fastapi_bridge

# Test endpoint directly
curl http://localhost:8000/api/config

# Check for 404s - verify routes exist
# Check for CORS issues - verify middleware config
```

### Common Issues

**CORS Error:**
- Solution: Ensure FastAPI is running on 8000 and frontend on 3000
- Check vite.config.ts proxy settings

**API Not Responding:**
- Check if FastAPI is running: `curl http://localhost:8000/health`
- Verify target path exists and is readable

**Hot Reload Not Working:**
- Restart dev server: `npm run dev`
- Clear .vite cache: `rm -rf node_modules/.vite`

## Project Structure Reference

```
CodeSentinel/
├── gui/                           # GUI Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   ├── pages/                 # Page components
│   │   ├── services/              # API client
│   │   ├── types/                 # TypeScript types
│   │   ├── App.tsx                # Root component
│   │   └── main.tsx               # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── src/sentinel/
│   ├── api/
│   │   ├── fastapi_bridge.py      # FastAPI bridge (NEW)
│   │   ├── scan_service.py        # Frozen API interface
│   │   └── models.py              # Data models
│   ├── scanner/
│   │   ├── engine.py              # Scanning engine
│   │   └── walker.py              # File walker
│   ├── rules/                     # Rule packs
│   └── llm/                       # AI integration
│
├── tests/
│   ├── unit/
│   └── integration/
│
└── README.md
```

## Next Steps

1. **Install dependencies**: Run setup commands above
2. **Start servers**: Run both backend and frontend
3. **Test basic flow**: Create scan through GUI
4. **Implement features**: Follow Phase 2 feature list
5. **Add tests**: Create UI and API tests
6. **Optimize**: Performance tuning for large scans

## Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vite Documentation](https://vitejs.dev)
- [CodeSentinel API Specification](../docs/api/api-freeze-spec.md)

## Support

For issues or questions:
1. Check existing documentation
2. Review error logs (browser console + terminal)
3. Verify all services are running
4. Check API connectivity with curl commands
