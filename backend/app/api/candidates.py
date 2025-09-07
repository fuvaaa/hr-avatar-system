from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.candidate import Candidate
from typing import List
import os
import json

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    vacancy_id: int = 1,
    db: Session = Depends(get_db)
):
    # Сохранение файла
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Создание кандидата (упрощенно)
    candidate = Candidate(
        name="Иван Иванов",
        email="ivan@example.com",
        phone="+7 (999) 123-45-67",
        resume_path=file_path,
        position="Python разработчик",
        skills=json.dumps(["Python", "Django", "PostgreSQL"]),
        experience=json.dumps([{
            "company": "Компания А",
            "position": "Python разработчик",
            "period": "2018-2022"
        }]),
        education=json.dumps([{
            "institution": "Университет",
            "degree": "Бакалавр",
            "specialty": "Программная инженерия",
            "year": "2018"
        }])
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "status": "uploaded"
    }

@router.get("/", response_model=List[dict])
async def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "position": c.position,
            "match_percentage": c.match_percentage,
            "status": c.status
        }
        for c in candidates
    ]

@router.get("/{candidate_id}", response_model=dict)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "position": candidate.position,
        "skills": candidate.skills,
        "experience": candidate.experience,
        "education": candidate.education,
        "match_percentage": candidate.match_percentage,
        "status": candidate.status
    }