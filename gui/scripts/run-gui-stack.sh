#!/bin/bash

# CodeSentinel Phase 3 GUI - Full Stack Launcher
# Starts both backend FastAPI server and React frontend dev server

set -e

PROJECT_ROOT="/home/andrei/CodeSentinel"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON="$VENV_PATH/bin/python"
UVICORN="$VENV_PATH/bin/uvicorn"

echo "═══════════════════════════════════════════════════════════"
echo "  CodeSentinel Phase 3 GUI - Full Stack Launcher"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}✗ Python virtual environment not found${NC}"
    echo "  Run: python3 -m venv $VENV_PATH"
    exit 1
fi

if [ ! -x "$PYTHON" ]; then
    echo -e "${RED}✗ Python executable not found${NC}"
    exit 1
fi

if [ ! -x "$UVICORN" ]; then
    echo -e "${RED}✗ Uvicorn not installed${NC}"
    echo "  Run: pip install uvicorn[standard]"
    exit 1
fi

if [ ! -d "$PROJECT_ROOT/gui/node_modules" ]; then
    echo -e "${YELLOW}⚠ Frontend dependencies not installed${NC}"
    echo "  Run: ./gui/scripts/setup-gui.sh"
    echo ""
fi

echo -e "${GREEN}✓ All checks passed${NC}"
echo ""

# Setup environment
export PYTHONPATH="$PROJECT_ROOT/src"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "Done."
}

trap cleanup EXIT

# Start backend
echo "Starting FastAPI backend..."
cd "$PROJECT_ROOT"
$UVICORN sentinel.api.fastapi_bridge:app \
    --host 127.0.0.1 \
    --port 8000 \
    --log-level info &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend PID: $BACKEND_PID${NC}"
sleep 2

# Start frontend (if Node.js installed)
if command -v npm &> /dev/null; then
    echo "Starting React frontend..."
    cd "$PROJECT_ROOT/gui"
    npm run dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}✓ Frontend PID: $FRONTEND_PID${NC}"
else
    echo -e "${YELLOW}⚠ Node.js not found - frontend will not start${NC}"
    echo "  To start frontend manually:"
    echo "    cd $PROJECT_ROOT/gui && npm run dev"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Services Running${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for interruption
wait
