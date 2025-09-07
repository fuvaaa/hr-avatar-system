# app/services/mock_openai_service.py
import random
import time
from typing import List, Dict, Any, Optional

class MockOpenAIService:
    """Mock-сервис для разработки без реального OpenAI API"""
    
    def __init__(self):
        self.questions_db = {
            "Python разработчик": [
                {
                    "id": 1,
                    "question": "Расскажите о вашем опыте работы с Python",
                    "category": "опыт работы",
                    "difficulty": "medium",
                    "skills_tested": ["Python"]
                },
                {
                    "id": 2,
                    "question": "Какие фреймворки Python вы использовали?",
                    "category": "технические навыки",
                    "difficulty": "medium",
                    "skills_tested": ["Django", "Flask"]
                },
                {
                    "id": 3,
                    "question": "Опишите ваш опыт работы с базами данных",
                    "category": "технические навыки",
                    "difficulty": "medium",
                    "skills_tested": ["SQL", "PostgreSQL"]
                }
            ],
            "Frontend разработчик": [
                {
                    "id": 1,
                    "question": "Расскажите о вашем опыте работы с JavaScript",
                    "category": "опыт работы",
                    "difficulty": "medium",
                    "skills_tested": ["JavaScript"]
                },
                {
                    "id": 2,
                    "question": "Какие фреймворки frontend вы использовали?",
                    "category": "технические навыки",
                    "difficulty": "medium",
                    "skills_tested": ["React", "Vue"]
                }
            ]
        }
    
    async def generate_interview_questions(
        self, 
        position: str, 
        skills: List[str], 
        experience_level: str = "middle",
        previous_questions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Генерация вопросов (мок)"""
        # Имитируем задержку сети
        await asyncio.sleep(0.5)
        
        # Берем вопросы из базы или генерируем стандартные
        questions = self.questions_db.get(position, [
            {
                "id": 1,
                "question": f"Расскажите о вашем опыте работы с {skills[0] if skills else 'технологиями'}",
                "category": "опыт работы",
                "difficulty": "medium",
                "skills_tested": skills[:1]
            }
        ])
        
        # Исключаем уже заданные вопросы
        if previous_questions:
            questions = [q for q in questions if q["question"] not in previous_questions]
        
        return questions[:3]  # Возвращаем до 3 вопросов
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_skills: List[str],
        question_category: str
    ) -> Dict[str, Any]:
        """Оценка ответа (мок)"""
        # Имитируем задержку сети
        await asyncio.sleep(1)
        
        # Генерируем случайную оценку
        overall_score = random.uniform(4.0, 9.5)
        overall_score = round(overall_score, 1)
        
        # Генерируем оценки по критериям
        return {
            "overall_score": overall_score,
            "technical_accuracy": random.uniform(3.0, 10.0),
            "completeness": random.uniform(3.0, 10.0),
            "clarity": random.uniform(3.0, 10.0),
            "relevance": random.uniform(3.0, 10.0),
            "practical_knowledge": random.uniform(3.0, 10.0),
            "strengths": random.sample([
                "Хорошо объяснил концепцию",
                "Привел практический пример",
                "Показал глубокое понимание темы",
                "Структурированный ответ",
                "Отличная коммуникация"
            ], 2),
            "improvements": random.sample([
                "Нужно больше конкретики",
                "Не хватило технических деталей",
                "Стоит углубить знания в области",
                "Рекомендую привести больше примеров"
            ], 1),
            "followup_suggestion": random.choice([
                "Можете привести конкретный пример из вашего опыта?",
                "Как вы решаете подобные проблемы на практике?",
                "С какими сложностями вы сталкивались в этой области?"
            ])
        }
    
    async def generate_followup_question(
        self,
        original_question: str,
        candidate_answer: str,
        evaluation: Dict[str, Any]
    ) -> str:
        """Генерация уточняющего вопроса (мок)"""
        await asyncio.sleep(0.5)
        
        followups = [
            "Можете привести конкретный пример из вашего опыта?",
            "Как вы решаете подобные проблемы на практике?",
            "С какими сложностями вы сталкивались в этой области?",
            "Можете рассказать подробнее о вашем подходе?"
        ]
        
        return random.choice(followups)
    
    async def generate_interview_summary(
        self,
        candidate_name: str,
        position: str,
        interview_results: List[Dict[str, Any]],
        overall_score: float
    ) -> str:
        """Генерация итогового резюме (мок)"""
        await asyncio.sleep(1)
        
        if overall_score >= 8:
            recommendation = "сильно рекомендуется к найму"
        elif overall_score >= 6:
            recommendation = "рекомендуется к дальнейшему рассмотрению"
        else:
            recommendation = "не рекомендуется"
        
        return f"""
Кандидат {candidate_name} прошел техническое собеседование на позицию {position}.
        
Общая оценка: {overall_score}/10
Рекомендация: {recommendation}

Ключевые сильные стороны:
- Демонстрирует хорошие технические знания
- Показывает умение решать сложные задачи
- Хорошо коммуницирует технические концепции

Области для развития:
- Углубить знания в специфических технологиях
- Больше практического опыта в реальных проектах

Следующие шаги:
- Рекомендуется техническое собеседование с командой
- Тестовое задание для проверки практических навыков
        """.strip()