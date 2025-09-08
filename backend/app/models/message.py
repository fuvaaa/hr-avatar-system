from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    text = Column(Text, nullable=False)
    sender_type = Column(String(20), nullable=False)  # "candidate" или "hr"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Обратная связь с Interview
    interview = relationship("Interview", back_populates="messages")