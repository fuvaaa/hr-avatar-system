from typing import List, Dict, Any
import random

class MockOpenAIService:
    """Заглушка для OpenAI сервиса, используемая когда API недоступен"""
    
    def __init__(self):
        pass
    
    async def generate_interview_questions(
        self, 
        position: str, 
        skills: List[str], 
        experience_level: str = "middle",
        question_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Генерация вопросов для интервью (заглушка)"""
        
        # Базовые вопросы для разных позиций
        base_questions = {
            "Python разработчик": [
                "Расскажите о вашем опыте работы с Python",
                "Какие фреймворки Python вы использовали?",
                "Опишите ваш опыт работы с базами данных",
                "Как вы тестируете свой код?",
                "Расскажите о вашем опыте работы с Django/Flask"
            ],
            "Frontend разработчик": [
                "Расскажите о вашем опыте работы с JavaScript",
                "Какие фреймворки frontend вы использовали?",
                "Опишите ваш опыт работы с React",
                "Как вы оптимизируете производительность frontend?",
                "Расскажите о вашем опыте работы с CSS"
            ],
            "Java разработчик": [
                "Расскажите о вашем опыте работы с Java",
                "Какие фреймворки Java вы использовали?",
                "Опишите ваш опыт работы с Spring",
                "Как вы работаете с базами данных в Java?",
                "Расскажите о вашем опыте с многопоточностью"
            ]
        }
        
        # Получаем вопросы для позиции или используем общие
        questions = base_questions.get(position, base_questions["Python разработчик"])
        
        # Форматируем в нужный формат
        result = []
        for i, question in enumerate(questions[:question_count], 1):
            result.append({
                "id": i,
                "question": question,
                "category": random.choice(["технические навыки", "опыт работы", "решение проблем"]),
                "difficulty": random.choice(["easy", "medium", "hard"])
            })
        
        return result
    
    async def evaluate_answer(
        self, 
        question: str, 
        answer: str, 
        expected_skills: List[str],
        question_category: str
    ) -> Dict[str, Any]:
        """Оценка ответа кандидата (заглушка)"""
        
        # Простая эвристика для оценки
        answer_length = len(answer.split())
        skill_mentions = sum(1 for skill in expected_skills if skill.lower() in answer.lower())
        
        # Базовая оценка
        base_score = min(10, 3 + answer_length // 20 + skill_mentions * 2)
        
        # Добавляем случайность
        score = min(10, max(1, base_score + random.randint(-2, 2)))
        
        # Генерируем фидбек на основе оценки
        if score >= 8:
            feedback = "Отличный ответ! Вы продемонстрировали глубокое понимание темы и умение четко излагать свои мысли."
            strengths = ["Полное понимание темы", "Хорошая структурированность ответа"]
            improvements = []
        elif score >= 6:
            feedback = "Хороший ответ, но есть возможности для улучшения."
            strengths = ["Базовое понимание темы", "Умение приводить примеры"]
            improvements = ["Больше конкретики", "Глубже раскрыть тему"]
        elif score >= 4:
            feedback = "Ответ частично соответствует вопросу. Рекомендуется углубить знания в этой области."
            strengths = ["Понимание основ"]
            improvements = ["Недостаточно конкретики", "Больше практических примеров"]
        else:
            feedback = "Ответ не соответствует требованиям вопроса. Необходимо изучить тему более детально."
            strengths = []
            improvements = ["Изучить основы темы", "Практиковаться на реальных проектах"]
        
        return {
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "improvements": improvements,
            "technical_accuracy": min(10, score + random.randint(-1, 1)),
            "completeness": min(10, score + random.randint(-1, 1)),
            "practical_experience": min(10, score + random.randint(-2, 2)),
            "communication": min(10, score + random.randint(-1, 1))
        }
    
    async def generate_followup_question(
        self, 
        original_question: str, 
        answer: str
    ) -> str:
        """Генерация уточняющего вопроса (заглушка)"""
        
        followup_questions = [
            "Можете привести конкретный пример из вашего опыта?",
            "Как вы справились с подобной задачей в прошлом?",
            "С какими трудностями вы столкнулись и как их преодолели?",
            "Можете рассказать подробнее о технических деталях реализации?"
        ]
        
        return random.choice(followup_questions)
    
    async def generate_interview_summary(
        self, 
        candidate_name: str,
        position: str,
        interview_results: List[Dict[str, Any]],
        overall_score: float
    ) -> str:
        """Генерация итогового резюме интервью (заглушка)"""
        
        if overall_score >= 8:
            recommendation = "Рекомендуется к найму"
            summary = f"{candidate_name} продемонстрировал отличные технические знания и опыт работы. Кандидат хорошо разбирается в необходимых технологиях и показывает высокий уровень профессионализма."
        elif overall_score >= 6:
            recommendation = "Рекомендуется к рассмотрению"
            summary = f"{candidate_name} показал хороший уровень знаний, но есть области для развития. Кандидат может быть полезен команде при наличии должного онбординга."
        elif overall_score >= 4:
            recommendation = "Требуется дополнительное собеседование"
            summary = f"{candidate_name} показал базовые знания, но недостаточно для позиции {position}. Рекомендуется провести дополнительное техническое собеседование."
        else:
            recommendation = "Не рекомендуется"
            summary = f"{candidate_name} не продемонстрировал достаточных знаний и опыта для позиции {position}."
        
        return f"""
Итоги собеседования с кандидатом {candidate_name} на позицию {position}:

Общая оценка: {overall_score}/10
Рекомендация: {recommendation}

{summary}

Сильные стороны:
- Технические навыки
- Опыт работы с проектами

Области для развития:
- Глубина знаний в отдельных областях
- Практический опыт решения сложных задач
        """