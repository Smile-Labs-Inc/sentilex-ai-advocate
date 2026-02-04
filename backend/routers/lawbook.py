from fastapi import APIRouter, HTTPException
from typing import List
import os
from pathlib import Path

router = APIRouter(prefix="/lawbook", tags=["lawbook"])

# Path to markdown laws directory
MARKDOWN_LAWS_DIR = Path(__file__).parent.parent / "data" / "markdown-laws"

from typing import Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from schemas.messages import UserQuery, SynthesizerOutput, RefusalOutput
from chains import invoke_chain
from audit_logging.audit import get_audit_logger, configure_audit_logger

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


@router.get("/")
async def list_laws():
    """
    List all available markdown law files.
    Returns a list of law metadata including id and title.
    """
    try:
        if not MARKDOWN_LAWS_DIR.exists():
            raise HTTPException(status_code=404, detail="Markdown laws directory not found")
        
        laws = []
        for file_path in MARKDOWN_LAWS_DIR.glob("*.md"):
            # Use filename without extension as id
            file_id = file_path.stem
            # Use filename as title (can be enhanced later)
            title = file_path.stem.replace("_", " ")
            
            laws.append({
                "id": file_id,
                "title": title,
                "filename": file_path.name
            })
        
        # Sort by filename for consistent ordering
        laws.sort(key=lambda x: x["filename"])
        
        return {"laws": laws}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing laws: {str(e)}")


@router.get("/{filename}")
async def get_law_content(filename: str):
    """
    Get the content of a specific markdown law file.
    
    Args:
        filename: The filename (with or without .md extension)
    
    Returns:
        The markdown content of the law file
    """
    try:
        # Ensure filename has .md extension
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = MARKDOWN_LAWS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Law file '{filename}' not found")
        
        # Read the markdown content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "filename": filename,
            "content": content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading law file: {str(e)}")


@router.post("/query", response_model=QueryResponse)
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
        else:...
        
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
