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
