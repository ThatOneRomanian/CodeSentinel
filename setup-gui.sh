#!/bin/bash
# CodeSentinel Phase 3 GUI - Quick Start Script

set -e

echo "═══════════════════════════════════════════════════════════"
echo "CodeSentinel Phase 3 GUI - Development Quick Start"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "  Found Python $PYTHON_VERSION"

# Check Node
echo "✓ Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found. Please install Node.js 16+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "  Found Node $NODE_VERSION"

# Install Python dependencies
echo ""
echo "✓ Installing Python dependencies..."
pip install -q fastapi uvicorn python-multipart
pip install -q -e ".[dev]" 2>/dev/null || echo "  (CodeSentinel already installed or in development mode)"

# Install Node dependencies
echo "✓ Installing Node.js dependencies..."
cd gui
npm install --silent 2>/dev/null || npm install
cd ..

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Setup Complete! 🎉"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "To start development:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    $ python -m sentinel.api.fastapi_bridge"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    $ cd gui && npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "For more information, see docs/GUI_DEVELOPMENT.md"
echo ""
