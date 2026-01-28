"""
FastAPI Application - Legal AI Multi-Agent System

Main entry point for the SentiLex AI Advocate system.
All business logic is organized in routers for maintainability.
"""

import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from routers import lawyers, lawyer_verification, legal_queries
from mcp_server.mcp_client import get_mcp_client


# Initialize FastAPI app
app = FastAPI(
    title="SentiLex AI Advocate - Legal Reasoning System",
    description="Court-admissible multi-agent legal reasoning for Sri Lankan law",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(lawyers.router)
app.include_router(lawyer_verification.router)
app.include_router(legal_queries.router)


# Response models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    mcp_available: bool
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    print("=" * 60)
    print("SentiLex AI Advocate - Legal Reasoning System")
    print("=" * 60)
    print(" Multi-agent architecture initialized")
    print(" Audit logging enabled")
    print(" MCP client configured")
    print(f" Logs directory: {os.getenv('AUDIT_LOG_DIR', 'logs')}")
    print("=" * 60)

    # Check MCP availability
    mcp_client = get_mcp_client()
    if mcp_client.health_check():
        print(" MCP service available")
    else:
        print(" WARNING: MCP service not available")
    print("=" * 60)


@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "message": "SentiLex AI Advocate - Legal Reasoning System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Verifies that the system and MCP service are operational.
    """
    mcp_client = get_mcp_client()
    mcp_available = mcp_client.health_check()

    return HealthResponse(
        status="healthy" if mcp_available else "degraded",
        mcp_available=mcp_available,
        timestamp=datetime.utcnow().isoformat()
    )


# Run the application
if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    print(f"\nStarting server on {host}:{port}")
    print(f"Docs: http://{host}:{port}/docs\n")

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
