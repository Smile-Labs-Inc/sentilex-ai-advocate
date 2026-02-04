"""
Case Agent Router

API endpoint for interacting with the case agent per incident.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.config import get_db
from models.user import User
from models.incident import Incident
from auth.dependencies import get_current_active_user
from agents.case_agent_graph import invoke_case_agent


router = APIRouter(prefix="/incidents", tags=["Case Agent"])


class CaseAgentRequest(BaseModel):
    """Request body for case agent endpoint."""
    message: str


class CaseAgentResponse(BaseModel):
    """Response from case agent."""
    response: str
    user_context_used: str


@router.post(
    "/{incident_id}/agent",
    response_model=CaseAgentResponse,
    summary="Chat with case agent",
    description="Send a message to the AI case agent for a specific incident."
)
async def run_case_agent(
    incident_id: int,
    request: CaseAgentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Run the case agent for a specific incident.
    
    The agent has access to:
    - Per-incident chat history
    - Global user history across incidents
    - User profile and preferences (via RLS-protected DB query)
    - Main legal reasoning chain
    """
    # Verify user owns this incident
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or access denied"
        )
    
    try:
        result = invoke_case_agent(
            incident_id=incident_id,
            user_id=current_user.id,
            message=request.message
        )
        
        return CaseAgentResponse(
            response=result["response"],
            user_context_used=result["user_context_used"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Case agent error: {str(e)}"
        )
