from sqlalchemy import Column, Integer, String, Float, Text, JSON
from sqlalchemy.orm import relationship  # Добавьте этот импорт
from app.core.database import Base

class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    resume_path = Column(String)
    position = Column(String)
    skills = Column(JSON)
    experience = Column(JSON)
    education = Column(JSON)
    match_percentage = Column(Float, default=0.0)
    status = Column(String, default="uploaded")
    interviews = relationship("Interview", back_populates="candidate")