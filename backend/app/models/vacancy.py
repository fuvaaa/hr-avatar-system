from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    requirements = Column(JSON)
    salary_min = Column(Float)
    salary_max = Column(Float)
    position = Column(String, index=True)
    department = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    interviews = relationship("Interview", back_populates="vacancy")