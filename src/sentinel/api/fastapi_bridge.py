"""
FastAPI Bridge - REST API server connecting GUI frontend to CodeSentinel backend.

This module provides HTTP/WebSocket endpoints that bridge the GUI frontend with
the frozen ScanService API, enabling real-time scanning with progress updates.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sentinel.api.models import (
    EnhancedFinding,
    ScanConfig,
    ScanEvent,
    ScanOptions,
    ScanProgress,
    ScanSummary,
    SharedConfig,
)
from sentinel.api.scan_service import ScanService
from sentinel.scanner.engine import Engine
from sentinel.scanner.walker import FileWalker

logger = logging.getLogger(__name__)

# ============================================================================
# Request/Response Models
# ============================================================================


class ScanRequest(BaseModel):
    """Request to start a new scan."""

    target_path: str = Field(..., description="Directory or file path to scan")
    enable_ai: bool = Field(default=False, description="Enable AI-powered explanations")
    llm_provider: str = Field(default="deepseek", description="LLM provider (deepseek, openai, local_ollama)")
    include_patterns: List[str] = Field(
        default_factory=lambda: ["*.py", "*.js", "*.json", "*.yaml", "*.yml", "*.env"],
        description="File patterns to include",
    )
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [".git", "node_modules", "__pycache__", ".pytest_cache"],
        description="File patterns to exclude",
    )


class ScanResponseDTO(BaseModel):
    """Response containing scan results."""

    scan_id: str
    summary: dict
    findings: List[dict]
    recommendations: Optional[dict] = None


class ProjectHistoryItem(BaseModel):
    """Historical scan record for a project."""

    project_path: str
    last_scan_date: str
    finding_count: int
    severity_breakdown: Dict[str, int]


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    api_version: str


# ============================================================================
# FastAPI Application Setup
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup/shutdown."""
    logger.info("CodeSentinel GUI API starting up...")
    yield
    logger.info("CodeSentinel GUI API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="CodeSentinel GUI API",
    description="REST API bridge for CodeSentinel GUI frontend",
    version="0.2.0",
    lifespan=lifespan,
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
service = ScanService()
scan_sessions: Dict[str, dict] = {}  # Track active scan sessions


# ============================================================================
# Health & Status Endpoints
# ============================================================================


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check API health status."""
    return HealthCheckResponse(
        status="healthy",
        version="0.2.0",
        api_version="1.0.0",
    )


@app.get("/api/config")
async def get_config():
    """Get current API configuration."""
    return {
        "llm_providers": ["deepseek", "openai", "local_ollama"],
        "default_include_patterns": ["*.py", "*.js", "*.json", "*.yaml", "*.yml", "*.env"],
        "default_exclude_patterns": [".git", "node_modules", "__pycache__", ".pytest_cache"],
        "max_file_size": 10485760,  # 10MB
    }


# ============================================================================
# Scan Management Endpoints
# ============================================================================


@app.post("/api/scans", response_model=dict)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a new security scan."""
    try:
        # Validate target path
        target_path = Path(request.target_path)
        if not target_path.exists():
            raise HTTPException(status_code=400, detail=f"Path not found: {request.target_path}")

        # Create scan configuration
        scan_config = SharedConfig(
            target_path=target_path,
            enable_ai=request.enable_ai,
            llm_provider=request.llm_provider,
            output_format="gui_enhanced",
            scan_options=ScanOptions(
                include_patterns=request.include_patterns,
                exclude_patterns=request.exclude_patterns,
            ),
        )

        # Start scan using service
        result = service.scan_directory(target_path, scan_config)

        # Store session for tracking
        scan_sessions[result.scan_id] = {
            "config": scan_config,
            "status": "completed",
            "result": result,
        }

        return {
            "scan_id": result.scan_id,
            "status": "completed",
            "findings_count": result.total_findings,
            "severity_breakdown": result.severity_breakdown,
        }

    except Exception as e:
        logger.error(f"Scan failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/api/scans/{scan_id}")
async def get_scan_results(scan_id: str):
    """Get completed scan results."""
    if scan_id not in scan_sessions:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")

    session = scan_sessions[scan_id]
    if session["status"] != "completed":
        return {"status": session["status"], "message": "Scan still in progress"}

    result = session["result"]
    return {
        "scan_id": scan_id,
        "summary": {
            "total_files": result.total_files,
            "files_with_issues": result.files_with_issues,
            "total_findings": result.total_findings,
            "severity_breakdown": result.severity_breakdown,
            "scan_duration_seconds": result.scan_duration_seconds,
        },
        "findings": [
            {
                "id": f.id,
                "rule_id": f.rule_id,
                "rule_name": f.rule_name,
                "file_path": str(f.file_path),
                "line": f.line,
                "severity": f.severity,
                "confidence": f.confidence,
                "excerpt": f.excerpt,
                "category": f.category,
                "tags": f.tags,
                "ai_explanation": f.ai_explanation,
                "remediation": f.remediation,
                "cwe_id": f.cwe_id,
                "risk_score": f.risk_score,
                "references": f.references,
            }
            for f in result.findings
        ],
        "recommendations": result.recommendations if hasattr(result, "recommendations") else None,
    }


@app.websocket("/api/scans/{scan_id}/progress")
async def websocket_progress(websocket: WebSocket, scan_id: str):
    """WebSocket endpoint for real-time scan progress updates."""
    await websocket.accept()

    try:
        if scan_id not in scan_sessions:
            await websocket.send_json({"error": f"Scan not found: {scan_id}"})
            await websocket.close(code=1008)
            return

        session = scan_sessions[scan_id]

        # Send initial status
        await websocket.send_json(
            {
                "type": "status",
                "status": session["status"],
                "scan_id": scan_id,
            }
        )

        # For completed scans, send completion message
        if session["status"] == "completed":
            result = session["result"]
            await websocket.send_json(
                {
                    "type": "completed",
                    "scan_id": scan_id,
                    "total_findings": result.total_findings,
                    "severity_breakdown": result.severity_breakdown,
                }
            )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for scan {scan_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        await websocket.close(code=1011)


@app.delete("/api/scans/{scan_id}")
async def cancel_scan(scan_id: str):
    """Cancel an ongoing scan."""
    if scan_id not in scan_sessions:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")

    session = scan_sessions[scan_id]
    if session["status"] == "completed":
        del scan_sessions[scan_id]
        return {"status": "deleted"}

    session["status"] = "cancelled"
    return {"status": "cancelled"}


# ============================================================================
# Finding Management Endpoints
# ============================================================================


@app.get("/api/findings/{finding_id}")
async def get_finding(finding_id: str):
    """Get details about a specific finding."""
    # Search through scan sessions for the finding
    for session in scan_sessions.values():
        if session["status"] == "completed":
            result = session["result"]
            for finding in result.findings:
                if finding.id == finding_id:
                    return {
                        "id": finding.id,
                        "rule_id": finding.rule_id,
                        "rule_name": finding.rule_name,
                        "file_path": str(finding.file_path),
                        "line": finding.line,
                        "severity": finding.severity,
                        "confidence": finding.confidence,
                        "excerpt": finding.excerpt,
                        "category": finding.category,
                        "ai_explanation": finding.ai_explanation,
                        "remediation": finding.remediation,
                        "cwe_id": finding.cwe_id,
                        "risk_score": finding.risk_score,
                        "references": finding.references,
                    }

    raise HTTPException(status_code=404, detail=f"Finding not found: {finding_id}")


@app.patch("/api/findings/{finding_id}")
async def update_finding(finding_id: str, update_data: dict):
    """Update finding status (resolved, ignored, etc.)."""
    # This would be implemented with persistent storage
    return {
        "finding_id": finding_id,
        "status": update_data.get("resolution_status", "open"),
        "updated_at": "2025-12-24T00:00:00Z",
    }


@app.post("/api/findings/{finding_id}/notes")
async def add_finding_notes(finding_id: str, notes: dict):
    """Add user notes to a finding."""
    return {
        "finding_id": finding_id,
        "notes": notes.get("notes", ""),
        "updated_at": "2025-12-24T00:00:00Z",
    }


# ============================================================================
# Project History Endpoints
# ============================================================================


@app.get("/api/projects", response_model=List[ProjectHistoryItem])
async def get_projects():
    """Get list of recent projects with scan history."""
    # This would be implemented with persistent storage
    return []


@app.get("/api/projects/{project_path}/scans")
async def get_project_scans(project_path: str):
    """Get scan history for a specific project."""
    return {
        "project_path": project_path,
        "scans": [],
    }


@app.delete("/api/projects/{project_path}")
async def delete_project(project_path: str):
    """Remove project from history."""
    return {
        "project_path": project_path,
        "status": "deleted",
    }


# ============================================================================
# Utility Functions
# ============================================================================


def get_app() -> FastAPI:
    """Get the FastAPI application instance."""
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
