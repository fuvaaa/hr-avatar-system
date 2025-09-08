from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Схемы для Candidate
class CandidateBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Схемы для Interview
class InterviewBase(BaseModel):
    candidate_id: int
    title: str
    status: str = "active"

class InterviewCreate(InterviewBase):
    pass

class InterviewResponse(InterviewBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Схемы для Message
class MessageBase(BaseModel):
    text: str
    sender_type: str  # "candidate" или "hr"

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    interview_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Схема для ответа HR
class HRResponse(BaseModel):
    response: str
    suggestions: List[str] = []