from pydantic import BaseModel, EmailStr
from typing import Optional

class LawyerBase(BaseModel):
    name: str
    specialties: str
    experience_years: int
    email: EmailStr
    phone: str
    district: str
    availability: Optional[str] = "Available"

class LawyerCreate(LawyerBase):
    pass

class LawyerResponse(LawyerBase):
    id: int
    rating: float
    reviews_count: int

    class Config:
        from_attributes = True
