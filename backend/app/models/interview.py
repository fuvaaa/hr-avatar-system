from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"))
    status = Column(String, default="scheduled")
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    transcript = Column(Text)
    match_score = Column(Float, default=0.0)
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Важные поля для хранения вопросов и ответов
    questions = Column(JSON)
    answers = Column(JSON)
    
    candidate = relationship("Candidate", back_populates="interviews")