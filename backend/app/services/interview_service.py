from typing import List, Dict, Any, Optional
import os

# Пытаемся импортировать и использовать реальный OpenAI
try:
    from app.services.openai_service import OpenAIService
    REAL_OPENAI_AVAILABLE = True
except ImportError:
    REAL_OPENAI_AVAILABLE = False

# Импортируем заглушку
from app.services.mock_openai_service import MockOpenAIService

class InterviewService:
    def __init__(self):
        # Проверяем наличие API ключа и доступность OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key and REAL_OPENAI_AVAILABLE:
            try:
                self.service = OpenAIService()
                self.use_real_openai = True
                print("Используется реальный OpenAI API")
            except Exception as e:
                print(f"Ошибка при инициализации OpenAI: {e}")
                self.service = MockOpenAIService()
                self.use_real_openai = False
        else:
            self.service = MockOpenAIService()
            self.use_real_openai = False
            print("Используется заглушка OpenAI")
    
    async def generate_interview_questions(
        self, 
        position: str, 
        skills: List[str], 
        experience_level: str = "middle",
        question_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Генерация вопросов для интервью"""
        return await self.service.generate_interview_questions(
            position, skills, experience_level, question_count
        )
    
    async def evaluate_answer(
        self, 
        question: str, 
        answer: str, 
        expected_skills: List[str],
        question_category: str
    ) -> Dict[str, Any]:
        """Оценка ответа кандидата"""
        return await self.service.evaluate_answer(
            question, answer, expected_skills, question_category
        )
    
    async def generate_followup_question(
        self, 
        original_question: str, 
        answer: str
    ) -> str:
        """Генерация уточняющего вопроса"""
        return await self.service.generate_followup_question(original_question, answer)
    
    async def generate_interview_summary(
        self, 
        candidate_name: str,
        position: str,
        interview_results: List[Dict[str, Any]],
        overall_score: float
    ) -> str:
        """Генерация итогового резюме интервью"""
        return await self.service.generate_interview_summary(
            candidate_name, position, interview_results, overall_score
        )
    
    def get_service_info(self) -> Dict[str, Any]:
        """Информация о используемом сервисе"""
        return {
            "service_type": "OpenAI" if self.use_real_openai else "Mock",
            "use_real_openai": self.use_real_openai,
            "model": "gpt-3.5-turbo" if self.use_real_openai else "mock"
        }