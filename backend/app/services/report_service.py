import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.vacancy import Vacancy
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_candidate_report(self, interview_id: int) -> str:
        interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return None
        
        candidate = self.db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        vacancy = self.db.query(Vacancy).filter(Vacancy.id == interview.vacancy_id).first()
        
        # Создание PDF отчета
        report_path = f"reports/{candidate.id}_report.pdf"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Заголовок
        story.append(Paragraph(f"Отчет по кандидату: {candidate.name}", styles['h1']))
        story.append(Spacer(1, 12))
        
        # Основная информация
        story.append(Paragraph(f"<b>Должность:</b> {vacancy.title}", styles['Normal']))
        story.append(Paragraph(f"<b>Email:</b> {candidate.email}", styles['Normal']))
        story.append(Paragraph(f"<b>Телефон:</b> {candidate.phone}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Результаты собеседования
        story.append(Paragraph("Результаты собеседования", styles['h2']))
        story.append(Paragraph(f"<b>Статус:</b> {interview.status}", styles['Normal']))
        story.append(Paragraph(f"<b>Оценка соответствия:</b> {interview.match_score * 100:.1f}%", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Детализация оценки
        if interview.transcript:
            transcript = json.loads(interview.transcript)
            story.append(Paragraph("Детализация ответов", styles['h2']))
            
            for entry in transcript:
                story.append(Paragraph(f"<b>Вопрос:</b> {entry['question']}", styles['Normal']))
                story.append(Paragraph(f"<b>Ответ:</b> {entry['answer']}", styles['Normal']))
                story.append(Paragraph(f"<b>Эмоция:</b> {entry['emotion']}", styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Фидбек
        if interview.feedback:
            story.append(Paragraph("Рекомендация", styles['h2']))
            story.append(Paragraph(interview.feedback, styles['Normal']))
        
        doc.build(story)
        
        return report_path