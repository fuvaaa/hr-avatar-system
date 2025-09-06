import json
import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.vacancy import Vacancy
from app.ml.speech_to_text import SpeechToText
from app.ml.emotion_detector import EmotionDetector
from app.ml.nlp_analyzer import NLPAnalyzer
from app.services.openai_service import OpenAIService
from datetime import datetime

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.speech_to_text = SpeechToText()
        self.emotion_detector = EmotionDetector()
        self.nlp_analyzer = NLPAnalyzer()
        self.openai_service = OpenAIService()
    
    def create_interview(self, candidate_id: int, vacancy_id: int) -> Interview:
        interview = Interview(
            candidate_id=candidate_id,
            vacancy_id=vacancy_id,
            status="scheduled"
        )
        
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        
        return interview
    
    def get_interview(self, interview_id: int) -> Interview:
        return self.db.query(Interview).filter(Interview.id == interview_id).first()
    
    def start_interview(self, interview_id: int) -> Dict[str, Any]:
        interview = self.get_interview(interview_id)
        if not interview:
            return None
        
        interview.status = "in_progress"
        interview.start_time = datetime.utcnow()
        self.db.commit()
        
        # Генерация первого вопроса с помощью OpenAI
        first_question = self._generate_first_question(interview.vacancy_id, interview.candidate_id)
        
        return {
            "interview_id": interview_id,
            "status": "in_progress",
            "question": first_question
        }
    
    def process_answer(self, interview_id: int, audio_file_path: str) -> Dict[str, Any]:
        interview = self.get_interview(interview_id)
        if not interview or interview.status != "in_progress":
            return None
        
        # Распознавание речи
        speech_result = self.speech_to_text.transcribe_file(audio_file_path)
        answer_text = speech_result["text"]
        
        # Анализ эмоций
        emotion_result = self.emotion_detector.predict_emotion(audio_file_path)
        
        # Получаем текущий вопрос (в реальном приложении нужно хранить)
        # Для примера используем последний вопрос из транскрипта
        current_question = "Расскажите о вашем опыте работы"  # По умолчанию
        
        # Получаем историю вопросов
        transcript = json.loads(interview.transcript) if interview.transcript else []
        if transcript:
            current_question = transcript[-1]["question"]
        
        # Получаем информацию о вакансии для оценки
        vacancy = self.db.query(Vacancy).filter(Vacancy.id == interview.vacancy_id).first()
        evaluation_criteria = "Технические навыки и опыт работы"  # По умолчанию
        
        if vacancy:
            try:
                requirements = json.loads(vacancy.requirements)
                evaluation_criteria = requirements.get("criteria", "Технические навыки и опыт работы")
            except:
                pass
        
        # Анализ качества ответа с помощью OpenAI
        answer_quality = self.openai_service.analyze_answer_quality(
            question=current_question,
            answer=answer_text,
            evaluation_criteria=evaluation_criteria
        )
        
        # Сохранение расшифровки и эмоций
        transcript.append({
            "question": current_question,
            "answer": answer_text,
            "emotion": emotion_result["emotion"],
            "confidence": emotion_result["confidence"],
            "quality_score": answer_quality,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        interview.transcript = json.dumps(transcript)
        interview.emotion_scores = json.dumps(emotion_result["scores"])
        self.db.commit()
        
        # Генерация следующего вопроса с помощью OpenAI
        next_question = self._generate_next_question(interview_id, answer_text, interview.candidate_id)
        
        return {
            "interview_id": interview_id,
            "question": next_question,
            "transcript": transcript[-1],
            "emotion": emotion_result,
            "answer_quality": answer_quality
        }
    
    def complete_interview(self, interview_id: int) -> Dict[str, Any]:
        interview = self.get_interview(interview_id)
        if not interview:
            return None
        
        interview.status = "completed"
        interview.end_time = datetime.utcnow()
        self.db.commit()
        
        # Расчет итоговой оценки
        match_score = self._calculate_interview_score(interview_id)
        interview.match_score = match_score
        
        # Генерация фидбека с помощью OpenAI
        feedback = self._generate_feedback(interview_id)
        interview.feedback = feedback
        
        self.db.commit()
        
        return {
            "interview_id": interview_id,
            "status": "completed",
            "match_score": match_score,
            "feedback": feedback
        }
    
    def _generate_first_question(self, vacancy_id: int, candidate_id: int) -> str:
        vacancy = self.db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
        if not vacancy:
            return "Расскажите о себе"
        
        # Получаем информацию о кандидате
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        candidate_context = f"Имя: {candidate.name}, Позиция: {candidate.position}, Навыки: {candidate.skills}"
        
        # Генерируем вопрос с помощью OpenAI
        return self.openai_service.generate_interview_question(
            candidate_context=candidate_context,
            vacancy_requirements=vacancy.requirements
        )
    
    def _generate_next_question(self, interview_id: int, answer_text: str, candidate_id: int) -> str:
        interview = self.get_interview(interview_id)
        if not interview:
            return "Повторите, пожалуйста"
        
        vacancy = self.db.query(Vacancy).filter(Vacancy.id == interview.vacancy_id).first()
        if not vacancy:
            return "Расскажите о своем образовании"
        
        # Получаем историю вопросов
        transcript = json.loads(interview.transcript) if interview.transcript else []
        previous_questions = [item["question"] for item in transcript]
        
        # Получаем информацию о кандидате
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        candidate_context = f"Имя: {candidate.name}, Позиция: {candidate.position}, Навыки: {candidate.skills}"
        
        # Генерируем следующий вопрос с помощью OpenAI
        return self.openai_service.generate_interview_question(
            candidate_context=candidate_context,
            vacancy_requirements=vacancy.requirements,
            previous_questions=previous_questions
        )
    
    def _calculate_interview_score(self, interview_id: int) -> float:
        interview = self.get_interview(interview_id)
        if not interview:
            return 0.0
        
        transcript = json.loads(interview.transcript) if interview.transcript else []
        emotion_scores = json.loads(interview.emotion_scores) if interview.emotion_scores else {}
        
        # Расчет средней оценки качества ответов
        quality_scores = [entry.get("quality_score", 5.0) for entry in transcript]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 5.0
        
        # Оценка по эмоциональному состоянию
        emotion_score = emotion_scores.get("neutral", 0.5) + emotion_scores.get("happy", 0)
        
        # Оценка по полноте ответов
        completeness_score = min(len(transcript) * 0.2, 1.0)
        
        # Итоговая оценка с весами
        total_score = (
            avg_quality_score * 0.5 +      # 50% - качество ответов
            emotion_score * 0.3 +          # 30% - эмоциональное состояние
            completeness_score * 0.2        # 20% - полнота ответов
        )
        
        # Нормализация в диапазон 0-1
        return max(0.0, min(1.0, total_score))
    
    def _generate_feedback(self, interview_id: int) -> str:
        interview = self.get_interview(interview_id)
        if not interview:
            return ""
        
        candidate = self.db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        
        # Формируем результаты интервью
        transcript = json.loads(interview.transcript) if interview.transcript else []
        interview_results = []
        
        for entry in transcript:
            interview_results.append({
                "question": entry["question"],
                "emotion": entry["emotion"],
                "quality": entry.get("quality_score", 5.0)
            })
        
        # Генерируем фидбек с помощью OpenAI
        return self.openai_service.generate_feedback(
            candidate_name=candidate.name,
            interview_results=interview_results,
            overall_score=interview.match_score * 10
        )