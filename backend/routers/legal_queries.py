"""
Legal Query Router - Court-Admissible Legal Reasoning

Handles all legal query processing, audit logs, and report exports.
"""

import os
from typing import Union, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from schemas.messages import UserQuery, SynthesizerOutput, RefusalOutput
from chains import invoke_chain
from audit_logging.audit import get_audit_logger, configure_audit_logger
from mcp_server.mcp_client import get_mcp_client


router = APIRouter(prefix="/api/legal", tags=["Legal Queries"])


# Request/Response models
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


# Initialize audit logger
audit_logger = configure_audit_logger(
    log_dir=os.getenv("AUDIT_LOG_DIR", "logs"),
    log_to_file=True
)


# @router.post("/query", response_model=QueryResponse)
# async def submit_query(request: QueryRequest):
#     """
#     MOVED TO backend/routers/lawbook.py
#     
#     Submit a legal query to the multi-agent system.
# 
#     This endpoint:
#     1. Validates the query
#     2. Routes it through the agent pipeline
#     3. Returns either a legal analysis or refusal
#     4. Logs everything for audit trail
# 
#     Args:
#         request: Query request with question and optional context
# 
#     Returns:
#         Query response with analysis or refusal
#     """
#     try:
#         # Create UserQuery from request
#         user_query = UserQuery(
#             question=request.question,
#             case_context=request.case_context
#         )
# 
#         # Invoke the main chain
#         result = invoke_chain(user_query)
# 
#         # Determine response status
#         if isinstance(result, SynthesizerOutput):
#             status = "success"
#             data = {
#                 "response": result.response,
#                 "confidence_note": result.confidence_note,
#                 "disclaimer": result.disclaimer,
#                 "metadata": result.metadata,
#                 "citations": [
#                     {
#                         "law_name": source.law_name,
#                         "section": source.section,
#                         "text": source.text
#                     }
#                     for source in result.citations
#                 ]
#             }
#         elif isinstance(result, RefusalOutput):
#             status = "refused"
#             data = {
#                 "reason": result.reason,
#                 "issues": [
#                     {
#                         "severity": issue.severity,
#                         "type": issue.type,
#                         "description": issue.description
#                     }
#                     for issue in result.issues
#                 ],
#                 "suggestions": result.suggestions
#             }
#         else:
#             raise ValueError(f"Unexpected result type: {type(result)}")
# 
#         return QueryResponse(
#             status=status,
#             data=data,
#             session_id=audit_logger.session_id,
#             timestamp=datetime.utcnow().isoformat()
#         )
# 
#     except Exception as e:
#         # Log the error
#         audit_logger.logger.error(f"Query processing failed: {str(e)}")
# 
#         # Return error response
#         raise HTTPException(
#             status_code=500,
#             detail=f"Query processing failed: {str(e)}"
#         )


@router.get("/audit/{session_id}")
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


@router.get("/export/{session_id}")
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


@router.post("/test/query")
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
