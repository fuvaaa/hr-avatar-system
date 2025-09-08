from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Обратная связь с Candidate
    candidate = relationship("Candidate", back_populates="interviews")
    
    # Связь с Message
    messages = relationship(
        "Message", 
        back_populates="interview",
        cascade="all, delete-orphan"
    )