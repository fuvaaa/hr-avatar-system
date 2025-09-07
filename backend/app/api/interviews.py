from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview import Interview
from app.models.candidate import Candidate
from typing import List, Dict, Any
import os
import json

router = APIRouter()

@router.post("/", response_model=dict)
async def create_interview(
    candidate_id: int,
    vacancy_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    interview = Interview(
        candidate_id=candidate_id,
        status="scheduled"
    )
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return {
        "id": interview.id,
        "candidate_id": interview.candidate_id,
        "status": interview.status
    }

# Добавьте этот эндпоинт для получения списка всех интервью
@router.get("/", response_model=List[dict])
async def get_interviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interviews = db.query(Interview).offset(skip).limit(limit).all()
    return [
        {
            "id": interview.id,
            "candidate_id": interview.candidate_id,
            "status": interview.status,
            "start_time": interview.start_time,
            "end_time": interview.end_time,
            "match_score": interview.match_score,
            "feedback": interview.feedback
        }
        for interview in interviews
    ]

@router.get("/{interview_id}", response_model=dict)
async def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return {
        "id": interview.id,
        "candidate_id": interview.candidate_id,
        "status": interview.status,
        "start_time": interview.start_time,
        "end_time": interview.end_time,
        "match_score": interview.match_score,
        "feedback": interview.feedback
    }