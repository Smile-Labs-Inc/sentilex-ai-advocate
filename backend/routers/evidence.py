"""
Evidence Router

API endpoints for managing evidence files across all user incidents.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime

from database.config import get_db
from models.user import User
from models.evidence import Evidence
from models.incident import Incident
from schemas.evidence import (
    EvidenceResponse,
    EvidenceWithIncidentResponse,
    EvidenceWithIncidentListResponse,
    EvidenceDownloadResponse
)
from auth.dependencies import get_current_active_user


router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("/", response_model=EvidenceWithIncidentListResponse)
async def list_all_evidence(
    incident_id: Optional[int] = Query(None, description="Filter by incident ID"),
    file_type: Optional[str] = Query(None, description="Filter by file type (MIME type)"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in file names"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all evidence files for the current user across all incidents.
    
    Supports filtering by incident, file type, date range, and search.
    """
    
    # Base query: get evidence for user's incidents only
    query = db.query(Evidence).join(Incident).filter(
        Incident.user_id == current_user.id
    ).options(joinedload(Evidence.incident))
    
    # Apply filters
    if incident_id:
        query = query.filter(Evidence.incident_id == incident_id)
    
    if file_type:
        query = query.filter(Evidence.file_type.ilike(f"%{file_type}%"))
    
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.filter(Evidence.uploaded_at >= date_from_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to)
            query = query.filter(Evidence.uploaded_at <= date_to_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    if search:
        query = query.filter(Evidence.file_name.ilike(f"%{search}%"))
    
    # Execute query
    evidence_list = query.order_by(Evidence.uploaded_at.desc()).all()
    
    # Format response with incident details
    evidence_with_incident = []
    for evidence in evidence_list:
        evidence_with_incident.append({
            "id": evidence.id,
            "incident_id": evidence.incident_id,
            "occurrence_id": evidence.occurrence_id,
            "file_name": evidence.file_name,
            "file_key": evidence.file_key,
            "file_hash": evidence.file_hash,
            "file_type": evidence.file_type,
            "file_size": evidence.file_size,
            "uploaded_at": evidence.uploaded_at,
            "description": None,  # Add if you have description field
            "incident_title": evidence.incident.title,
            "incident_type": evidence.incident.incident_type.value,
            "incident_status": evidence.incident.status.value
        })
    
    return EvidenceWithIncidentListResponse(
        evidence=evidence_with_incident,
        total=len(evidence_with_incident)
    )


@router.get("/{evidence_id}", response_model=EvidenceWithIncidentResponse)
async def get_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific evidence file by ID.
    
    Verifies that the evidence belongs to one of the user's incidents.
    """
    
    evidence = db.query(Evidence).options(joinedload(Evidence.incident)).filter(
        Evidence.id == evidence_id
    ).first()
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # Verify ownership
    if evidence.incident.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this evidence"
        )
    
    return {
        "id": evidence.id,
        "incident_id": evidence.incident_id,
        "occurrence_id": evidence.occurrence_id,
        "file_name": evidence.file_name,
        "file_key": evidence.file_key,
        "file_hash": evidence.file_hash,
        "file_type": evidence.file_type,
        "file_size": evidence.file_size,
        "uploaded_at": evidence.uploaded_at,
        "description": None,
        "incident_title": evidence.incident.title,
        "incident_type": evidence.incident.incident_type.value,
        "incident_status": evidence.incident.status.value
    }




@router.get("/{evidence_id}/download", response_model=EvidenceDownloadResponse)
async def download_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a presigned URL for downloading evidence.
    
    Returns a temporary download URL that expires in 15 minutes.
    Does not expose the S3 key directly to the frontend.
    """
    
    evidence = db.query(Evidence).join(Incident).filter(
        Evidence.id == evidence_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found or you do not have permission to access it"
        )
    
    # Generate presigned URL (expires in 15 minutes = 900 seconds)
    from services.s3_service import generate_presigned_url
    from datetime import timedelta
    
    download_url = generate_presigned_url(evidence.file_key, expiration=900)
    expires_at = datetime.utcnow() + timedelta(seconds=900)
    
    return EvidenceDownloadResponse(
        download_url=download_url,
        expires_at=expires_at,
        file_name=evidence.file_name,
        file_size=evidence.file_size
    )


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an evidence file from S3 and database.
    
    Verifies that the evidence belongs to one of the user's incidents.
    """
    
    evidence = db.query(Evidence).join(Incident).filter(
        Evidence.id == evidence_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found or you do not have permission to delete it"
        )
    
    # Delete file from S3
    try:
        from services.s3_service import delete_file_from_s3
        delete_file_from_s3(evidence.file_key)
    except Exception as e:
        import logging
        logging.error(f"Failed to delete file from S3: {evidence.file_key} - {str(e)}")
        # Continue with database deletion even if S3 deletion fails
    
    db.delete(evidence)
    db.commit()
    
    return None

