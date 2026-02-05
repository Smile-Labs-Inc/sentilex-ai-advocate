"""
Incidents Router

API endpoints for creating and managing incident reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database.config import get_db
from models.user import User
from models.incident import Incident, IncidentStatusEnum as ModelIncidentStatus, IncidentTypeEnum as ModelIncidentType
from schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentStatusEnum,
    IncidentTypeEnum
)
from auth.dependencies import get_current_active_user


router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new incident report.
    
    The incident is automatically associated with the authenticated user
    and set to 'submitted' status.
    """
    
    # Create incident with user association
    new_incident = Incident(
        user_id=current_user.id,
        incident_type=ModelIncidentType(incident_data.incident_type.value),
        title=incident_data.title,
        description=incident_data.description,
        date_occurred=incident_data.date_occurred,
        location=incident_data.location,
        jurisdiction=incident_data.jurisdiction,
        platforms_involved=incident_data.platforms_involved,
        perpetrator_info=incident_data.perpetrator_info,
        evidence_notes=incident_data.evidence_notes,
        status=ModelIncidentStatus.SUBMITTED
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    
    return new_incident


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    status_filter: Optional[IncidentStatusEnum] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all incidents for the current user.
    
    Optionally filter by status.
    """
    
    query = db.query(Incident).filter(Incident.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Incident.status == ModelIncidentStatus(status_filter.value))
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    
    return IncidentListResponse(
        incidents=incidents,
        total=len(incidents)
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific incident by ID.
    
    Users can only access their own incidents.
    """
    
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    update_data: IncidentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing incident.
    
    Users can only update their own incidents.
    Status can only be changed to 'draft' by the user.
    """
    
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        if field == "status" and value is not None:
            # Users can only set status to draft
            if value != IncidentStatusEnum.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Users can only change status to 'draft'"
                )
            setattr(incident, field, ModelIncidentStatus(value.value))
        elif field == "incident_type" and value is not None:
            setattr(incident, field, ModelIncidentType(value.value))
        elif value is not None:
            setattr(incident, field, value)
    
    db.commit()
    db.refresh(incident)
    
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an incident.
    
    Users can only delete their own incidents that are in 'draft' status.
    """
    
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    if incident.status != ModelIncidentStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only draft incidents can be deleted"
        )
    
    db.delete(incident)
    db.commit()
    
    return None


# ============================================================================
# Incident Chat Endpoints
# ============================================================================

from models.incident_chat import IncidentChatMessage, IncidentChatRoleEnum as ModelChatRole
from schemas.incident import (
    IncidentChatMessageCreate,
    IncidentChatMessageResponse,
    IncidentChatExchangeResponse
)
from schemas.messages import UserQuery
from chains import invoke_chain


@router.post("/{incident_id}/messages", response_model=IncidentChatExchangeResponse)
async def send_incident_message(
    incident_id: int,
    message_data: IncidentChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in incident chat and get AI response.
    
    This endpoint:
    1. Verifies the incident belongs to the user
    2. Saves the user's message
    3. Gets AI response using the legal reasoning chain
    4. Saves the AI response
    5. Returns both messages
    """
    
    # Verify incident exists and belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Save user message
    user_message = IncidentChatMessage(
        incident_id=incident_id,
        user_id=current_user.id,
        role=ModelChatRole.USER,
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Get AI response using the legal reasoning chain
    try:
        # Create context from incident details
        case_context = f"""
Incident Type: {incident.incident_type.value}
Title: {incident.title}
Description: {incident.description}
Date Occurred: {incident.date_occurred}
Location: {incident.location or 'Not specified'}
Jurisdiction: {incident.jurisdiction or 'Sri Lanka'}
Platforms Involved: {incident.platforms_involved or 'Not specified'}
"""
        
        # Create UserQuery for the chain
        user_query = UserQuery(
            question=message_data.content,
            case_context=case_context
        )
        
        # Invoke the AI chain
        ai_response = invoke_chain(user_query)
        
        # Extract response text
        if hasattr(ai_response, 'response'):
            assistant_content = ai_response.response
        elif hasattr(ai_response, 'answer'):
            assistant_content = ai_response.answer
        elif hasattr(ai_response, 'reason'):
            assistant_content = ai_response.reason
        else:
            assistant_content = str(ai_response)
            
    except Exception as e:
        # Fallback response if AI fails
        assistant_content = "I apologize, but I'm having trouble processing your request right now. Please try rephrasing your question or contact support if the issue persists."
        import logging
        logging.error(f"AI chain error for incident {incident_id}: {str(e)}")
    
    # Save assistant message
    assistant_message = IncidentChatMessage(
        incident_id=incident_id,
        user_id=None,  # AI messages don't have a user_id
        role=ModelChatRole.ASSISTANT,
        content=assistant_content
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    return IncidentChatExchangeResponse(
        user_message=IncidentChatMessageResponse.model_validate(user_message),
        assistant_message=IncidentChatMessageResponse.model_validate(assistant_message)
    )


@router.get("/{incident_id}/messages", response_model=list[IncidentChatMessageResponse])
async def get_incident_messages(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all chat messages for an incident.
    
    Returns messages in chronological order.
    """
    
    # Verify incident exists and belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get all messages for this incident
    messages = db.query(IncidentChatMessage).filter(
        IncidentChatMessage.incident_id == incident_id
    ).order_by(IncidentChatMessage.created_at.asc()).all()
    
    return [IncidentChatMessageResponse.model_validate(msg) for msg in messages]


# ============================================================================
# Evidence Upload Endpoints
# ============================================================================

from fastapi import UploadFile, File
from models.evidence import Evidence
from schemas.incident import EvidenceResponse, EvidenceListResponse
from pathlib import Path
import os
import uuid


# Evidence storage directory
EVIDENCE_DIR = Path("uploaded_evidence")
EVIDENCE_DIR.mkdir(exist_ok=True)


@router.post("/{incident_id}/evidence", response_model=list[EvidenceResponse])
async def upload_evidence(
    incident_id: int,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload evidence files for an incident.
    
    Accepts multiple files and stores them securely.
    Returns metadata for all uploaded files.
    """
    
    # Verify incident exists and belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    uploaded_evidence = []
    
    for file in files:
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create incident-specific directory
        incident_dir = EVIDENCE_DIR / f"incident_{incident_id}"
        incident_dir.mkdir(exist_ok=True)
        
        # Save file to disk
        file_path = incident_dir / unique_filename
        
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Create evidence record
            evidence = Evidence(
                incident_id=incident_id,
                file_name=file.filename,
                file_path=str(file_path),
                file_type=file.content_type,
                file_size=len(contents)
            )
            
            db.add(evidence)
            db.commit()
            db.refresh(evidence)
            
            uploaded_evidence.append(evidence)
            
        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename}: {str(e)}"
            )
    
    return [EvidenceResponse.model_validate(e) for e in uploaded_evidence]


@router.get("/{incident_id}/evidence", response_model=EvidenceListResponse)
async def get_incident_evidence(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all evidence for an incident.
    
    Returns metadata for all uploaded files.
    """
    
    # Verify incident exists and belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get all evidence for this incident
    evidence_list = db.query(Evidence).filter(
        Evidence.incident_id == incident_id
    ).order_by(Evidence.uploaded_at.desc()).all()
    
    return EvidenceListResponse(
        evidence=[EvidenceResponse.model_validate(e) for e in evidence_list],
        total=len(evidence_list)
    )


@router.delete("/{incident_id}/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    incident_id: int,
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an evidence file.
    
    Removes both the file from disk and the database record.
    """
    
    # Verify incident exists and belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get evidence
    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id,
        Evidence.incident_id == incident_id
    ).first()
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # Delete file from disk
    file_path = Path(evidence.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            import logging
            logging.error(f"Failed to delete file {file_path}: {str(e)}")
    
    # Delete database record
    db.delete(evidence)
    db.commit()
    
    return None

