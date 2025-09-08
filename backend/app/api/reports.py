from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Interview, Candidate, Message
from app.schemas import InterviewResponse

router = APIRouter()

@router.get("/", response_model=List[InterviewResponse])
def get_all_interviews(db: Session = Depends(get_db)):
    interviews = db.query(Interview).all()
    return interviews

@router.get("/stats")
def get_interview_stats(db: Session = Depends(get_db)):
    total_interviews = db.query(Interview).count()
    total_candidates = db.query(Candidate).count()
    total_messages = db.query(Message).count()
    
    return {
        "total_interviews": total_interviews,
        "total_candidates": total_candidates,
        "total_messages": total_messages
    }