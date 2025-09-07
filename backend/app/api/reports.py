from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview import Interview
from app.models.candidate import Candidate
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/{interview_id}/pdf")
async def generate_report(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
    
    # Создание простого текстового отчета
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"candidate_{candidate.id}_report.txt")
    
    with open(report_path, "w") as f:
        f.write(f"Отчет по кандидату: {candidate.name}\n")
        f.write(f"Должность: {candidate.position}\n")
        f.write(f"Email: {candidate.email}\n")
        f.write(f"Телефон: {candidate.phone}\n\n")
        f.write("Результаты собеседования:\n")
        f.write(f"Статус: {interview.status}\n")
        f.write(f"Оценка соответствия: {interview.match_score * 100:.1f}%\n")
        f.write(f"Рекомендация: {interview.feedback}\n")
    
    return FileResponse(
        path=report_path,
        filename=f"candidate_{candidate.id}_report.txt",
        media_type='text/plain'
    )