from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db  # Исправленный путь
from app.models import Interview, Candidate, Message  # Импортируем модели
from app.schemas import InterviewCreate, InterviewResponse, MessageCreate, MessageResponse, HRResponse
from app.services.hr_avatar import generate_hr_response_with_context

router = APIRouter()

@router.post("/", response_model=InterviewResponse)
def create_interview(interview: InterviewCreate, db: Session = Depends(get_db)):
    db_interview = Interview(**interview.dict())
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.post("/{interview_id}/messages", response_model=MessageResponse)
def add_message(
    interview_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    # Проверяем существование интервью
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Сохраняем сообщение кандидата
    db_message = Message(
        interview_id=interview_id,
        text=message.text,
        sender_type=message.sender_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Если сообщение от кандидата - генерируем ответ HR
    if message.sender_type == "candidate":
        # Используем новую функцию с контекстом
        hr_response_data = generate_hr_response_with_context(interview_id, message.text, db)
        
        # Сохраняем ответ HR
        hr_message = Message(
            interview_id=interview_id,
            text=hr_response_data["response"],
            sender_type="hr"
        )
        db.add(hr_message)
        db.commit()
        db.refresh(hr_message)
        
        # Возвращаем ответ HR
        return hr_message
    
    return db_message

@router.post("/{interview_id}/generate-response", response_model=HRResponse)
def generate_hr_avatar_response(
    interview_id: int,
    candidate_message: str,
    db: Session = Depends(get_db)
):
    # Проверяем существование интервью
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Генерируем ответ HR с контекстом
    return generate_hr_response_with_context(interview_id, candidate_message, db)