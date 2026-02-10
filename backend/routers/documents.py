"""
Documents Router

API endpoints for generating and exporting case documents (PDFs, ZIPs).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import zipstream
from pathlib import Path
from datetime import datetime

from database.config import get_db
from models.user import User
from models.incident import Incident
from models.evidence import Evidence
from models.occurrence import Occurrence
from auth.dependencies import get_current_active_user
from services.pdf_generator import (
    generate_police_statement_pdf,
    generate_cert_report_pdf,
    generate_evidence_manifest_pdf
)

router = APIRouter(prefix="/documents", tags=["documents"])


def _incident_to_dict(incident: Incident) -> dict:
    """Convert Incident model to dictionary for template rendering."""
    return {
        "id": incident.id,
        "title": incident.title,
        "incident_type": incident.incident_type,
        "description": incident.description,
        "date_occurred": incident.date_occurred.strftime('%d %B %Y') if incident.date_occurred else None,
        "location": incident.location,
        "jurisdiction": incident.jurisdiction,
        "platforms_involved": incident.platforms_involved,
        "perpetrator_info": incident.perpetrator_info,
        "status": incident.status,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at
    }


def _user_to_dict(user: User) -> dict:
    """Convert User model to dictionary for template rendering."""
    return {
        "full_name": user.full_name,
        "email": user.email,
        "phone_number": user.phone_number
    }


def _evidence_to_dict(evidence: Evidence) -> dict:
    """Convert Evidence model to dictionary for template rendering."""
    return {
        "id": evidence.id,
        "file_name": evidence.file_name,
        "file_type": evidence.file_type,
        "file_size": evidence.file_size,
        "file_path": evidence.file_path,
        "file_hash": evidence.file_hash,
        "uploaded_at": evidence.uploaded_at
    }


def _occurrence_to_dict(occurrence: Occurrence) -> dict:
    """Convert Occurrence model to dictionary for template rendering."""
    return {
        "id": occurrence.id,
        "title": occurrence.title,
        "description": occurrence.description,
        "date_occurred": occurrence.date_occurred.strftime('%d %B %Y') if occurrence.date_occurred else None
    }


@router.get("/incidents/{incident_id}/export/police-statement")
async def export_police_statement(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download a police statement PDF for an incident.
    
    Returns a professionally formatted police report suitable for filing
    with law enforcement agencies.
    """
    # Get incident and verify ownership
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
    evidence_list = db.query(Evidence).filter(
        Evidence.incident_id == incident_id
    ).all()
    
    # Get occurrences
    occurrences = db.query(Occurrence).filter(
        Occurrence.incident_id == incident_id
    ).order_by(Occurrence.date_occurred).all()
    
    # Convert to dicts
    incident_dict = _incident_to_dict(incident)
    user_dict = _user_to_dict(current_user)
    evidence_dicts = [_evidence_to_dict(e) for e in evidence_list]
    occurrence_dicts = [_occurrence_to_dict(o) for o in occurrences]
    
    # Generate PDF
    pdf_file = generate_police_statement_pdf(
        incident=incident_dict,
        user=user_dict,
        evidence_list=evidence_dicts,
        occurrences=occurrence_dicts
    )
    
    # Return as downloadable file
    filename = f"Police_Statement_{incident_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/incidents/{incident_id}/export/cert-report")
async def export_cert_report(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download a CERT technical report PDF for an incident.
    
    Returns a technical analysis report suitable for submission to
    Sri Lanka CERT and cybercrime investigators.
    """
    # Get incident and verify ownership
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
    evidence_list = db.query(Evidence).filter(
        Evidence.incident_id == incident_id
    ).all()
    
    # Get occurrences
    occurrences = db.query(Occurrence).filter(
        Occurrence.incident_id == incident_id
    ).order_by(Occurrence.date_occurred).all()
    
    # Convert to dicts
    incident_dict = _incident_to_dict(incident)
    user_dict = _user_to_dict(current_user)
    evidence_dicts = [_evidence_to_dict(e) for e in evidence_list]
    occurrence_dicts = [_occurrence_to_dict(o) for o in occurrences]
    
    # Generate PDF
    pdf_file = generate_cert_report_pdf(
        incident=incident_dict,
        user=user_dict,
        evidence_list=evidence_dicts,
        occurrences=occurrence_dicts
    )
    
    # Return as downloadable file
    filename = f"CERT_Report_{incident_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/incidents/{incident_id}/export/evidence-manifest")
async def export_evidence_manifest(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download an evidence manifest PDF.
    
    Returns a detailed listing of all evidence files associated with
    the incident.
    """
    # Get incident and verify ownership
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
    evidence_list = db.query(Evidence).filter(
        Evidence.incident_id == incident_id
    ).all()
    
    # Convert to dicts
    incident_dict = _incident_to_dict(incident)
    evidence_dicts = [_evidence_to_dict(e) for e in evidence_list]
    
    # Generate PDF
    pdf_file = generate_evidence_manifest_pdf(
        incident=incident_dict,
        evidence_list=evidence_dicts
    )
    
    # Return as downloadable file
    filename = f"Evidence_Manifest_{incident_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/incidents/{incident_id}/export/case-file")
async def export_case_file(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download a complete case file package (ZIP).
    
    Includes:
    - Police statement PDF
    - CERT technical report PDF
    - Evidence manifest PDF
    - All evidence files
    - Case metadata (JSON)
    """
    # Get incident and verify ownership
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.user_id == current_user.id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get evidence and occurrences
    evidence_list = db.query(Evidence).filter(
        Evidence.incident_id == incident_id
    ).all()
    
    occurrences = db.query(Occurrence).filter(
        Occurrence.incident_id == incident_id
    ).order_by(Occurrence.date_occurred).all()
    
    # Convert to dicts
    incident_dict = _incident_to_dict(incident)
    user_dict = _user_to_dict(current_user)
    evidence_dicts = [_evidence_to_dict(e) for e in evidence_list]
    occurrence_dicts = [_occurrence_to_dict(o) for o in occurrences]
    
    # Generate PDFs
    police_pdf = generate_police_statement_pdf(
        incident=incident_dict,
        user=user_dict,
        evidence_list=evidence_dicts,
        occurrences=occurrence_dicts
    )
    
    cert_pdf = generate_cert_report_pdf(
        incident=incident_dict,
        user=user_dict,
        evidence_list=evidence_dicts,
        occurrences=occurrence_dicts
    )
    
    manifest_pdf = generate_evidence_manifest_pdf(
        incident=incident_dict,
        evidence_list=evidence_dicts
    )
    
    # Create ZIP stream
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    
    # Add PDFs to ZIP
    z.writestr(f"Police_Statement_{incident_id}.pdf", police_pdf.read())
    z.writestr(f"CERT_Report_{incident_id}.pdf", cert_pdf.read())
    z.writestr(f"Evidence_Manifest_{incident_id}.pdf", manifest_pdf.read())
    
    # Add evidence files to ZIP
    for evidence in evidence_list:
        if evidence.file_path and Path(evidence.file_path).exists():
            z.write(
                evidence.file_path,
                arcname=f"evidence/{evidence.file_name}"
            )
    
    # Add metadata JSON
    import json
    metadata = {
        "incident_id": incident.id,
        "title": incident.title,
        "type": incident.incident_type,
        "status": incident.status,
        "created_at": incident.created_at.isoformat(),
        "evidence_count": len(evidence_list),
        "occurrence_count": len(occurrences),
        "export_date": datetime.now().isoformat()
    }
    z.writestr("metadata.json", json.dumps(metadata, indent=2))
    
    # Return ZIP as streaming response
    filename = f"Case_File_{incident_id}_{datetime.now().strftime('%Y%m%d')}.zip"
    
    return StreamingResponse(
        iter(z),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
