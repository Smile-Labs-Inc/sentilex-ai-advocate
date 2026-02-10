"""
Stats Router

API endpoints for dashboard statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.config import get_db
from models.user import User
from models.incident import Incident, IncidentStatusEnum
from auth.dependencies import get_current_active_user
from pydantic import BaseModel


router = APIRouter(prefix="/stats", tags=["Statistics"])


class UserStatsResponse(BaseModel):
    """User-specific statistics for dashboard"""
    pending_reports: int
    total_reports: int
    resolved_cases: int
    in_progress_cases: int


class GlobalStatsResponse(BaseModel):
    """Platform-wide statistics"""
    total_cases_solved: int
    active_users: int
    affiliated_lawyers: int
    case_types_handled: int


@router.get("/user", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for the current user.

    Returns:
    - pending_reports: Number of incidents in 'draft' status
    - total_reports: Total number of incidents
    - resolved_cases: Number of incidents in 'resolved' status
    - in_progress_cases: Number of incidents in 'under_review' or 'submitted' status
    """

    user_id = current_user.id

    # Get counts for each status
    pending_count = db.query(func.count(Incident.id)).filter(
        Incident.user_id == user_id,
        Incident.status == IncidentStatusEnum.DRAFT
    ).scalar() or 0

    total_count = db.query(func.count(Incident.id)).filter(
        Incident.user_id == user_id
    ).scalar() or 0

    resolved_count = db.query(func.count(Incident.id)).filter(
        Incident.user_id == user_id,
        Incident.status == IncidentStatusEnum.RESOLVED
    ).scalar() or 0

    # In progress includes both submitted and under_review statuses
    in_progress_count = db.query(func.count(Incident.id)).filter(
        Incident.user_id == user_id,
        Incident.status.in_([IncidentStatusEnum.SUBMITTED, IncidentStatusEnum.UNDER_REVIEW])
    ).scalar() or 0

    return UserStatsResponse(
        pending_reports=pending_count,
        total_reports=total_count,
        resolved_cases=resolved_count,
        in_progress_cases=in_progress_count
    )


@router.get("/global", response_model=GlobalStatsResponse)
async def get_global_stats(
    db: Session = Depends(get_db)
):
    """
    Get platform-wide statistics (visible to all users).

    Returns global numbers for new users to see platform activity.
    """
    from models.lawyers import Lawyer, VerificationStatusEnum as LawyerVerificationStatusEnum
    from models.incident import IncidentTypeEnum

    # Total resolved cases across all users
    total_resolved = db.query(func.count(Incident.id)).filter(
        Incident.status == IncidentStatusEnum.RESOLVED
    ).scalar() or 0

    # Active users (users who have at least one incident)
    active_users = db.query(func.count(func.distinct(Incident.user_id))).scalar() or 0

    # Affiliated lawyers (verified lawyers)
    affiliated_lawyers = db.query(func.count(Lawyer.id)).filter(
        Lawyer.verification_status == LawyerVerificationStatusEnum.approved
    ).scalar() or 0

    # Number of different case types handled (count enum values)
    case_types_handled = len(IncidentTypeEnum)

    return GlobalStatsResponse(
        total_cases_solved=total_resolved,
        active_users=active_users,
        affiliated_lawyers=affiliated_lawyers,
        case_types_handled=case_types_handled
    )
