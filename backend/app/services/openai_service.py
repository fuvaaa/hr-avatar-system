# app/services/openai_service.py
import os
import json
from typing import List, Dict, Any, Optional
import openai
from app.core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_interview_questions(
        self, 
        position: str, 
        skills: List[str], 
        experience_level: str = "middle",
        previous_questions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Генерация вопросов для интервью с помощью OpenAI GPT-4"""
        
        system_prompt = """
        Ты опытный технический интервьюер в крупной IT-компании.
        Твоя задача - создавать качественные вопросы для технического собеседования.
        """
        
        user_prompt = f"""
        Сгенерируй 5 вопросов для технического собеседования на позицию {position}.
        
        Уровень кандидата: {experience_level}
        Навыки кандидата: {', '.join(skills)}
        
        Требования к вопросам:
        1. Вопросы должны проверять практические навыки, а не теоретические знания
        2. Каждый вопрос должен иметь категорию (технические навыки, решение проблем, опыт работы, системное мышление)
        3. Вопросы должны быть разными по сложности (easy, medium, hard)
        4. Избегай вопросов с ответами "да/нет"
        
        {f"Учти, что следующие вопросы уже были заданы: {', '.join(previous_questions)}" if previous_questions else ""}
        
        Верни результат в формате JSON массива объектов:
        [
            {{
                "id": 1,
                "question": "Текст вопроса",
                "category": "технические навыки|решение проблем|опыт работы|системное мышление",
                "difficulty": "easy|medium|hard",
                "skills_tested": ["навык1", "навык2"]
            }}
        ]
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_default_questions(position, skills)
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_skills: List[str],
        question_category: str
    ) -> Dict[str, Any]:
        """Анализ качества ответа кандидата с детальной оценкой"""
        
        system_prompt = """
        Ты опытный технический интервьюер с 10-летним опытом.
        Твоя задача - объективно оценивать ответы кандидатов на технических собеседованиях.
        """
        
        user_prompt = f"""
        Оцени ответ кандидата на вопрос технического собеседования.
        
        Вопрос: {question}
        Ответ кандидата: {answer}
        Категория вопроса: {question_category}
        Ожидаемые навыки: {', '.join(expected_skills)}
        
        Оцени ответ по следующим критериям (шкала 1-10):
        1. technical_accuracy - Техническая точность и корректность информации
        2. completeness - Полнота и глубина ответа
        3. clarity - Ясность и структурированность изложения
        4. relevance - Соответствие заданному вопросу
        5. practical_knowledge - Демонстрация практического опыта
        
        Также предоставь:
        6. strengths - Сильные стороны ответа (2-3 пункта)
        7. improvements - Что можно улучшить (1-2 пункта)
        8. followup_suggestion - Уточняющий вопрос, если нужно
        
        Верни результат в формате JSON:
        {{
            "overall_score": 7.5,
            "technical_accuracy": 8,
            "completeness": 7,
            "clarity": 8,
            "relevance": 9,
            "practical_knowledge": 7,
            "strengths": ["Хорошо объяснил концепцию", "Привел практический пример"],
            "improvements": ["Не хватило деталей о производительности"],
            "followup_suggestion": "Можете рассказать о конкретном случае, когда вы оптимизировали производительность?"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._get_default_evaluation()
    
    async def generate_followup_question(
        self,
        original_question: str,
        candidate_answer: str,
        evaluation: Dict[str, Any]
    ) -> str:
        """Генерация уточняющего вопроса на основе ответа и оценки"""
        
        system_prompt = """
        Ты опытный технический интервьюер.
        Твоя задача - задавать уточняющие вопросы для более глубокой оценки кандидата.
        """
        
        user_prompt = f"""
        На основе ответа кандидата сгенерируй уточняющий вопрос.
        
        Оригинальный вопрос: {original_question}
        Ответ кандидата: {candidate_answer}
        Оценка ответа: {evaluation.get('overall_score', 'N/A')}/10
        
        Сфокусируй на аспектах, где балл ниже 7 или где нужны дополнительные детали.
        Уточняющий вопрос должен быть:
        1. Конкретным и сфокусированным
        2. Помогающим выявить глубину знаний
        3. Связанным с исходным вопросом
        
        Верни только текст уточняющего вопроса без дополнительных пояснений.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return "Можете рассказать подробнее о вашем опыте в этой области?"
    
    async def generate_interview_summary(
        self,
        candidate_name: str,
        position: str,
        interview_results: List[Dict[str, Any]],
        overall_score: float
    ) -> str:
        """Генерация итогового резюме интервью"""
        
        system_prompt = """
        Ты HR-директор в крупной IT-компании.
        Твоя задача - создавать профессиональные и мотивирующие резюме интервью.
        """
        
        # Форматируем результаты для промпта
        results_text = []
        for i, result in enumerate(interview_results, 1):
            results_text.append(f"Вопрос {i}: {result.get('question', 'N/A')}")
            results_text.append(f"Оценка: {result.get('overall_score', 'N/A')}/10")
            if result.get('strengths'):
                results_text.append(f"Сильные стороны: {', '.join(result['strengths'])}")
        
        user_prompt = f"""
        Сгенерируй итоговое резюме технического собеседования для кандидата {candidate_name} на позицию {position}.
        
        Результаты интервью:
        {chr(10).join(results_text)}
        
        Общая оценка: {overall_score}/10
        
        Резюме должно включать:
        1. Общую оценку кандидата
        2. Ключевые сильные стороны
        3. Основные области для развития
        4. Рекомендацию по найму
        5. Следующие шаги в процессе найма
        
        Тон должен быть профессиональным, но дружелюбным и мотивирующим.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Кандидат {candidate_name} показал общий результат {overall_score}/10. Рекомендуется дальнейшее рассмотрение."
    
    def _get_default_questions(self, position: str, skills: List[str]) -> List[Dict[str, Any]]:
        """Запасные вопросы на случай ошибки API"""
        return [
            {
                "id": 1,
                "question": f"Расскажите о вашем опыте работы с {skills[0] if skills else 'технологиями'}",
                "category": "опыт работы",
                "difficulty": "medium",
                "skills_tested": skills[:1]
            },
            {
                "id": 2,
                "question": "Как вы решаете сложные технические задачи?",
                "category": "решение проблем",
                "difficulty": "hard",
                "skills_tested": ["решение проблем"]
            }
        ]
    
    def _get_default_evaluation(self) -> Dict[str, Any]:
        """Запасная оценка на случай ошибки API"""
        return {
            "overall_score": 5.0,
            "technical_accuracy": 5,
            "completeness": 5,
            "clarity": 5,
            "relevance": 5,
            "practical_knowledge": 5,
            "strengths": ["Ответил на вопрос"],
            "improvements": ["Нужно больше деталей"],
            "followup_suggestion": "Можете привести конкретный пример?"
        }


# Фабрика для создания сервиса
def get_ai_service():
    """Фабрика для получения AI сервиса (реальный или заглушка)"""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key":
        return OpenAIService()
    else:
        from app.services.mock_openai_service import MockOpenAIService
        return MockOpenAIService()