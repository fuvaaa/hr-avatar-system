import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.utils.file_processor import extract_resume_data
from app.ml.nlp_analyzer import NLPAnalyzer

class CandidateService:
    def __init__(self, db: Session):
        self.db = db
        self.nlp_analyzer = NLPAnalyzer()
    
    def create_candidate(self, file_path: str, vacancy_id: int) -> Candidate:
        # Извлечение данных из резюме
        resume_data = extract_resume_data(file_path)
        
        # Создание кандидата в БД
        candidate = Candidate(
            name=resume_data["name"],
            email=resume_data["email"],
            phone=resume_data["phone"],
            resume_path=file_path,
            position=resume_data["position"],
            skills=json.dumps(resume_data["skills"]),
            experience=json.dumps(resume_data["experience"]),
            education=json.dumps(resume_data["education"])
        )
        
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        
        return candidate
    
    def get_candidate(self, candidate_id: int) -> Candidate:
        return self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    def get_candidates(self, skip: int = 0, limit: int = 100) -> List[Candidate]:
        return self.db.query(Candidate).offset(skip).limit(limit).all()
    
    def update_candidate_match(self, candidate_id: int, match_percentage: float, status: str):
        candidate = self.get_candidate(candidate_id)
        if candidate:
            candidate.match_percentage = match_percentage
            candidate.status = status
            self.db.commit()
    
    def calculate_candidate_match(self, candidate_id: int, vacancy_requirements: Dict[str, Any]) -> Dict[str, Any]:
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return None
        
        candidate_data = {
            "skills": json.loads(candidate.skills),
            "experience": json.loads(candidate.experience),
            "education": json.loads(candidate.education)
        }
        
        match_details = self.nlp_analyzer.calculate_match(candidate_data, vacancy_requirements)
        
        # Обновление кандидата
        match_percentage = match_details["total_score"] * 100
        status = "approved" if match_percentage > 70 else "rejected" if match_percentage < 50 else "clarification"
        
        self.update_candidate_match(candidate_id, match_percentage, status)
        
        return {
            "candidate_id": candidate_id,
            "match_percentage": match_percentage,
            "status": status,
            "details": match_details
        }