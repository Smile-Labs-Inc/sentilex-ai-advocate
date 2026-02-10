from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database.config import get_db
from models.lawyers import Lawyer, VerificationStatusEnum
from models.lawyerverificationaudit import LawyerVerificationAudit
from schemas.lawyers import (
    VerificationStep2, VerificationStep4, VerificationStatusResponse,
    DocumentUploadResponse, AdminVerificationAction
)
from models.DocumentStorageService import document_storage
from auth.dependencies import get_current_lawyer, get_current_admin
from services.notification_service import LawyerNotificationService

router = APIRouter(prefix="/api/lawyer/verification", tags=["Lawyer Verification"])

def log_audit(db: Session, lawyer_id: int, action: str, step: int = None, 
              performed_by: str = "lawyer", ip: str = None, details: str = None):
    """Helper to log verification actions"""
    audit = LawyerVerificationAudit(
        lawyer_id=lawyer_id,
        action=action,
        step_number=step,
        performed_by=performed_by,
        ip_address=ip,
        details=details
    )
    db.add(audit)
    db.commit()

@router.get("/status", response_model=VerificationStatusResponse)
def get_verification_status(
    db: Session = Depends(get_db),
    current_lawyer: Lawyer = Depends(get_current_lawyer)
):
    """Get current verification status and determine next step"""
    can_proceed = current_lawyer.verification_status in [
        VerificationStatusEnum.not_started,
        VerificationStatusEnum.in_progress,
        VerificationStatusEnum.rejected
    ]
    
    return VerificationStatusResponse(
        verification_step=current_lawyer.verification_step,
        verification_status=current_lawyer.verification_status.value,
        can_proceed=can_proceed,
        rejection_reason=current_lawyer.rejection_reason
    )

@router.post("/step2", status_code=200)
def complete_step2(
    data: VerificationStep2,
    request: Request,
    db: Session = Depends(get_db),
    current_lawyer: Lawyer = Depends(get_current_lawyer)
):
    """Complete legal enrollment details"""
    if current_lawyer.verification_status == VerificationStatusEnum.approved:
        raise HTTPException(403, "Verification already approved. No changes allowed.")
    
    if current_lawyer.verification_status == VerificationStatusEnum.submitted:
        raise HTTPException(403, "Verification submitted. Awaiting admin review.")
    
    # Check if SC enrollment number already exists
    existing = db.query(Lawyer).filter(
        Lawyer.sc_enrollment_number == data.sc_enrollment_number,
        Lawyer.id != current_lawyer.id
    ).first()
    
    if existing:
        raise HTTPException(400, "Supreme Court enrollment number already registered")
    
    # Update lawyer record
    current_lawyer.sc_enrollment_number = data.sc_enrollment_number
    current_lawyer.enrollment_year = data.enrollment_year
    current_lawyer.law_college_reg_number = data.law_college_reg_number
    current_lawyer.verification_step = 3
    current_lawyer.verification_status = VerificationStatusEnum.in_progress
    
    db.commit()
    
    # Send notification about step 2 completion
    notification_service = LawyerNotificationService(db)
    notification_service.send(
        recipient_id=current_lawyer.id,
        title="📋 Enrollment Details Submitted",
        message=f"Your Supreme Court enrollment details have been recorded. Next step: Upload your required documents.",
        notification_type="VERIFICATION",
        priority=2,
        action_url="/profile/verification"
    )
    
    log_audit(
        db, current_lawyer.id, "step_2_completed", 2, 
        "lawyer", request.client.host,
        f"SC Enrollment: {data.sc_enrollment_number}"
    )
    
    return {"message": "Step 2 completed", "next_step": 3}

@router.post("/step3/upload/{document_type}", response_model=DocumentUploadResponse)
async def upload_document(
    document_type: str,
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_lawyer: Lawyer = Depends(get_current_lawyer)
):
    """
    Upload verification document.
    document_type: nic_front | nic_back | attorney_certificate | practising_certificate
    """
    valid_types = ["nic_front", "nic_back", "attorney_certificate", "practising_certificate"]
    if document_type not in valid_types:
        raise HTTPException(400, f"Invalid document type. Must be one of: {valid_types}")
    
    if current_lawyer.verification_status == VerificationStatusEnum.approved:
        raise HTTPException(403, "Verification approved. Documents locked.")
    
    # Check if document already exists (prevent replacement after submission)
    existing_hash = getattr(current_lawyer, f"{document_type}_hash", None)
    if current_lawyer.verification_status == VerificationStatusEnum.submitted and existing_hash:
        raise HTTPException(403, "Documents locked after submission. Contact admin for changes.")
    
    # Upload to S3
    url, file_hash = await document_storage.upload_document(
        current_lawyer.id, document_type, file, existing_hash
    )
    
    # Update lawyer record
    setattr(current_lawyer, f"{document_type}_url", url)
    setattr(current_lawyer, f"{document_type}_hash", file_hash)
    setattr(current_lawyer, f"{document_type}_uploaded_at", datetime.utcnow())
    
    db.commit()
    
    log_audit(
        db, current_lawyer.id, f"document_uploaded_{document_type}", 3,
        "lawyer", request.client.host,
        f"Hash: {file_hash}"
    )
    
    return DocumentUploadResponse(
        document_type=document_type,
        url=url,
        hash=file_hash,
        uploaded_at=getattr(current_lawyer, f"{document_type}_uploaded_at")
    )

@router.post("/step4/declare", status_code=200)
def accept_declaration(
    data: VerificationStep4,
    request: Request,
    db: Session = Depends(get_db),
    current_lawyer: Lawyer = Depends(get_current_lawyer)
):
    """Accept legal declaration and submit for review"""
    if current_lawyer.verification_status == VerificationStatusEnum.approved:
        raise HTTPException(403, "Verification already approved")
    
    # Validate all documents uploaded
    required_docs = ["nic_front", "nic_back", "attorney_certificate", "practising_certificate"]
    missing = [doc for doc in required_docs if not getattr(current_lawyer, f"{doc}_url")]
    
    if missing:
        raise HTTPException(400, f"Missing documents: {', '.join(missing)}")
    
    # Mark as submitted
    current_lawyer.declaration_accepted = True
    current_lawyer.declaration_accepted_at = datetime.utcnow()
    current_lawyer.declaration_ip_address = data.ip_address
    current_lawyer.verification_step = 4
    current_lawyer.verification_status = VerificationStatusEnum.submitted
    current_lawyer.verification_submitted_at = datetime.utcnow()
    
    db.commit()
    
    log_audit(
        db, current_lawyer.id, "verification_submitted", 4,
        "lawyer", data.ip_address,
        "Declaration accepted and verification submitted for admin review"
    )
    
    return {"message": "Verification submitted successfully. Awaiting admin approval."}

# ADMIN ENDPOINTS

@router.post("/admin/{lawyer_id}/verify")
def admin_verify_lawyer(
    lawyer_id: int,
    action_data: AdminVerificationAction,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)  # Your admin auth
):
    """Admin approval/rejection of lawyer verification"""
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(404, "Lawyer not found")
    
    if lawyer.verification_status != VerificationStatusEnum.submitted:
        raise HTTPException(400, "Lawyer verification not in submitted state")
    
    if action_data.action == "approve":
        lawyer.verification_status = VerificationStatusEnum.approved
        lawyer.verified_by_admin_id = admin.id
        lawyer.verified_at = datetime.utcnow()
        lawyer.admin_notes = action_data.admin_notes
        lawyer.rejection_reason = None
        
        log_action = "verification_approved"
        message = "Lawyer verification approved"
        
    else:  # reject
        lawyer.verification_status = VerificationStatusEnum.rejected
        lawyer.rejection_reason = action_data.rejection_reason
        lawyer.admin_notes = action_data.admin_notes
        lawyer.verification_step = 3  # Allow re-upload
        
        log_action = "verification_rejected"
        message = "Lawyer verification rejected"
    
    db.commit()
    
    log_audit(
        db, lawyer_id, log_action, None,
        f"admin:{admin.id}", request.client.host,
        action_data.admin_notes or action_data.rejection_reason
    )
    
    return {"message": message}

@router.get("/admin/{lawyer_id}/documents")
def get_lawyer_documents(
    lawyer_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Get signed URLs for lawyer documents (admin only)"""
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(404, "Lawyer not found")
    
    docs = {}
    for doc_type in ["nic_front", "nic_back", "attorney_certificate", "practising_certificate"]:
        url = getattr(lawyer, f"{doc_type}_url")
        if url:
            docs[doc_type] = {
                "signed_url": document_storage.generate_signed_url(url),
                "hash": getattr(lawyer, f"{doc_type}_hash"),
                "uploaded_at": getattr(lawyer, f"{doc_type}_uploaded_at")
            }
    
    return docs