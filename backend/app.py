"""
FastAPI Application - Legal AI Multi-Agent System

This is the main entry point for the court-admissible legal reasoning system.

API Endpoints:
- POST /query - Submit a legal query
- GET /health - Health check
- GET /audit/{session_id} - Retrieve audit logs
- GET /export/{session_id} - Export audit report

All queries are logged for court admissibility.
"""

import os
from typing import Union, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from schemas.messages import (
    UserQuery,
    SynthesizerOutput,
    RefusalOutput
)
from chains import invoke_chain
from logging.audit import get_audit_logger, configure_audit_logger
from mcp_client import get_mcp_client


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


# Request/Response models for API
class QueryRequest(BaseModel):
    """API request model for legal queries."""
    question: str = Field(..., min_length=10, description="Legal question")
    case_context: str = Field(None, description="Optional case context")


class QueryResponse(BaseModel):
    """API response model for legal queries."""
    status: str = Field(..., description="'success' or 'refused'")
    data: Union[Dict[str, Any], None] = Field(..., description="Response data")
    session_id: str = Field(..., description="Session ID for audit trail")
    timestamp: str = Field(..., description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    mcp_available: bool
    timestamp: str


# Initialize audit logger
audit_logger = configure_audit_logger(
    log_dir=os.getenv("AUDIT_LOG_DIR", "logs"),
    log_to_file=True
)


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    print("=" * 60)
    print("SentiLex AI Advocate - Legal Reasoning System")
    print("=" * 60)
    print("✓ Multi-agent architecture initialized")
    print("✓ Audit logging enabled")
    print("✓ MCP client configured")
    print(f"✓ Logs directory: {os.getenv('AUDIT_LOG_DIR', 'logs')}")
    print("=" * 60)

    # Check MCP availability
    mcp_client = get_mcp_client()
    if mcp_client.health_check():
        print("✓ MCP service available")
    else:
        print("⚠ WARNING: MCP service not available")
    print("=" * 60)


@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "SentiLex AI Advocate - Legal Reasoning System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
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


@app.post("/query", response_model=QueryResponse, tags=["Legal Queries"])
async def submit_query(request: QueryRequest):
    """
    Submit a legal query to the multi-agent system.

    This endpoint:
    1. Validates the query
    2. Routes it through the agent pipeline
    3. Returns either a legal analysis or refusal
    4. Logs everything for audit trail

    Args:
        request: Query request with question and optional context

    Returns:
        Query response with analysis or refusal
    """
    try:
        # Create UserQuery from request
        user_query = UserQuery(
            question=request.question,
            case_context=request.case_context
        )

        # Invoke the main chain
        result = invoke_chain(user_query)

        # Determine response status
        if isinstance(result, SynthesizerOutput):
            status = "success"
            data = {
                "response": result.response,
                "confidence_note": result.confidence_note,
                "disclaimer": result.disclaimer,
                "metadata": result.metadata,
                "citations": [
                    {
                        "law_name": source.law_name,
                        "section": source.section,
                        "text": source.text
                    }
                    for source in result.citations
                ]
            }
        elif isinstance(result, RefusalOutput):
            status = "refused"
            data = {
                "reason": result.reason,
                "issues": [
                    {
                        "severity": issue.severity,
                        "type": issue.type,
                        "description": issue.description
                    }
                    for issue in result.issues
                ],
                "suggestions": result.suggestions
            }
        else:
            raise ValueError(f"Unexpected result type: {type(result)}")

        return QueryResponse(
            status=status,
            data=data,
            session_id=audit_logger.session_id,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        # Log the error
        audit_logger.logger.error(f"Query processing failed: {str(e)}")

        # Return error response
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@app.get("/audit/{session_id}", tags=["Audit"])
async def get_audit_logs(session_id: str):
    """
    Retrieve audit logs for a session.

    Args:
        session_id: The session ID from a query response

    Returns:
        List of audit log entries
    """
    # For current session
    if session_id == audit_logger.session_id:
        logs = audit_logger.get_session_logs()
        return {
            "session_id": session_id,
            "log_count": len(logs),
            "logs": [log.dict() for log in logs]
        }
    else:
        # For historical sessions, read from file
        log_file = audit_logger.log_dir / f"session_{session_id}.jsonl"

        if not log_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        # Read JSONL file
        import json
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))

        return {
            "session_id": session_id,
            "log_count": len(logs),
            "logs": logs
        }


@app.get("/export/{session_id}", tags=["Audit"])
async def export_audit_report(session_id: str, format: str = "json"):
    """
    Export audit report for a session.

    Args:
        session_id: The session ID from a query response
        format: Export format ('json' or 'markdown')

    Returns:
        Download URL or report content
    """
    if session_id != audit_logger.session_id:
        raise HTTPException(
            status_code=400,
            detail="Can only export current session. Use /audit/{session_id} for historical sessions."
        )

    try:
        if format == "json":
            output_file = audit_logger.export_session_logs()
        elif format == "markdown":
            output_file = audit_logger.generate_audit_report()
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Use 'json' or 'markdown'."
            )

        return {
            "session_id": session_id,
            "format": format,
            "file": output_file,
            "message": f"Report exported to {output_file}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@app.post("/test/query", tags=["Testing"])
async def test_query():
    """
    Test endpoint with a sample query.

    Use this to verify the system is working correctly.
    """
    sample_query = UserQuery(
        question="What is the definition of culpable homicide under Sri Lankan law?",
        case_context=None
    )

    result = invoke_chain(sample_query)

    if isinstance(result, SynthesizerOutput):
        return {
            "status": "success",
            "response": result.response,
            "confidence": result.metadata.get("validation_confidence")
        }
    else:
        return {
            "status": "refused",
            "reason": result.reason
        }


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
