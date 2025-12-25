# CodeSentinel GUI - React + TypeScript Frontend

A modern, responsive web interface for CodeSentinel security scanner. Built with React 18, TypeScript, and Vite.

## Features

- **Project Selection**: Choose directories to scan with path validation
- **Real-time Progress**: WebSocket-based live scanning updates
- **Results Dashboard**: Interactive findings visualization with filtering
- **Severity Breakdown**: Categorized view of security issues by severity
- **Finding Details**: Comprehensive analysis with AI explanations and remediation guidance
- **Responsive Design**: Works on desktop and tablet devices

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- CodeSentinel backend running on `http://localhost:8000`

### Installation

```bash
cd gui
npm install
```

### Development

```bash
# Start development server (runs on http://localhost:3000)
npm run dev

# Run type checking
npm run type-check

# Lint code
npm run lint
```

### Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

### Directory Structure

```
gui/
├── src/
│   ├── components/        # Reusable React components
│   ├── pages/             # Page components (Dashboard, ScanResults)
│   ├── services/          # API client and backend communication
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Application entry point
│   └── index.css           # Global styles
├── index.html             # HTML template
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies
```

### Component Overview

- **Dashboard**: Entry point for starting new scans
- **ScanResults**: Results viewer with filtering and detail exploration
- **SeverityBadge**: Reusable severity indicator component

### API Integration

The frontend communicates with the backend via:
- **REST API** for starting scans and fetching results
- **WebSocket** for real-time progress updates

See [services/api.ts](src/services/api.ts) for API client implementation.

## Configuration

Environment variables (optional):

```bash
REACT_APP_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

## Development Workflow

1. Start the backend FastAPI server
2. Run `npm run dev` to start the development server
3. Open http://localhost:3000 in your browser
4. Make changes to React components - they'll hot-reload automatically

## Building for Production

```bash
npm run build
```

This creates a production-ready build in the `dist/` directory.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT - See LICENSE in root directory
