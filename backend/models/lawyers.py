from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from database.config import Base

class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialties = Column(String(255), nullable=False)
    experience_years = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    district = Column(String(50), nullable=False)
    availability = Column(String(50), default="Available")
    rating = Column(DECIMAL(2,1), default=0.0)
    reviews_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP)
