from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import get_db
from models.lawyers import Lawyer
from schemas.lawyers import LawyerCreate, LawyerResponse

router = APIRouter(
    prefix="/lawyers",
    tags=["Lawyers"]
)

@router.post("/", response_model=LawyerResponse)
def create_lawyer(lawyer: LawyerCreate, db: Session = Depends(get_db)):
    existing = db.query(Lawyer).filter(Lawyer.email == lawyer.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lawyer already exists")

    new_lawyer = Lawyer(**lawyer.dict())
    db.add(new_lawyer)
    db.commit()
    db.refresh(new_lawyer)
    return new_lawyer


@router.get("/", response_model=list[LawyerResponse])
def get_lawyers(
    district: str | None = None,
    specialty: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Lawyer)

    if district:
        query = query.filter(Lawyer.district == district)

    if specialty:
        query = query.filter(Lawyer.specialties.like(f"%{specialty}%"))

    return query.all()