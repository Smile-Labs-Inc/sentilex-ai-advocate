"""
Occurrences Router

API endpoints for managing occurrences within incidents.
Occurrences represent individual recurring events within a case.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.config import get_db
from models.user import User
from models.incident import Incident
from models.occurrence import Occurrence
from schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceUpdate,
    OccurrenceResponse,
    OccurrenceListResponse
)
from auth.dependencies import get_current_active_user


router = APIRouter(tags=["Occurrences"])


@router.post("/incidents/{incident_id}/occurrences", response_model=OccurrenceResponse, status_code=status.HTTP_201_CREATED)
async def create_occurrence(
    incident_id: int,
    occurrence_data: OccurrenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new occurrence for an incident.
    
    Occurrences represent individual events within a recurring case.
    For example, if a user is being cyberbullied repeatedly, each new attack
    can be recorded as a separate occurrence.
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
    
    # Create new occurrence
    new_occurrence = Occurrence(
        incident_id=incident_id,
        title=occurrence_data.title,
        description=occurrence_data.description,
        date_occurred=occurrence_data.date_occurred
    )
    
    db.add(new_occurrence)
    db.commit()
    db.refresh(new_occurrence)
    
    return new_occurrence


@router.get("/incidents/{incident_id}/occurrences", response_model=OccurrenceListResponse)
async def list_occurrences(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all occurrences for an incident.
    
    Returns occurrences in reverse chronological order (most recent first).
    """
    
    # Verify incident belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get all occurrences for this incident
    occurrences = db.query(Occurrence).filter(
        Occurrence.incident_id == incident_id
    ).order_by(Occurrence.date_occurred.desc()).all()
    
    return OccurrenceListResponse(
        occurrences=occurrences,
        total=len(occurrences)
    )


@router.get("/incidents/{incident_id}/occurrences/{occurrence_id}", response_model=OccurrenceResponse)
async def get_occurrence(
    incident_id: int,
    occurrence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific occurrence by ID.
    
    Users can only access occurrences from their own incidents.
    """
    
    # Verify incident belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get the occurrence
    occurrence = db.query(Occurrence).filter(
        Occurrence.id == occurrence_id,
        Occurrence.incident_id == incident_id
    ).first()
    
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Occurrence not found"
        )
    
    return occurrence


@router.patch("/incidents/{incident_id}/occurrences/{occurrence_id}", response_model=OccurrenceResponse)
async def update_occurrence(
    incident_id: int,
    occurrence_id: int,
    update_data: OccurrenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing occurrence.
    
    Users can only update occurrences from their own incidents.
    """
    
    # Verify incident belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get the occurrence
    occurrence = db.query(Occurrence).filter(
        Occurrence.id == occurrence_id,
        Occurrence.incident_id == incident_id
    ).first()
    
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Occurrence not found"
        )
    
    # Update fields that are provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if value is not None:
            setattr(occurrence, field, value)
    
    db.commit()
    db.refresh(occurrence)
    
    return occurrence


@router.delete("/incidents/{incident_id}/occurrences/{occurrence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_occurrence(
    incident_id: int,
    occurrence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an occurrence.
    
    Users can only delete occurrences from their own incidents.
    All evidence linked to this occurrence will have their occurrence_id set to NULL.
    """
    
    # Verify incident belongs to user
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get the occurrence
    occurrence = db.query(Occurrence).filter(
        Occurrence.id == occurrence_id,
        Occurrence.incident_id == incident_id
    ).first()
    
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Occurrence not found"
        )
    
    # Delete the occurrence (evidence will be orphaned but not deleted)
    db.delete(occurrence)
    db.commit()
    
    return None
