# backend/app/services/ai_interviewer.py
from typing import List, Dict, Any
import json

class AIInterviewer:
    def __init__(self):
        # База вопросов по разным направлениям
        self.question_bank = {
            'Python разработчик': [
                {
                    'question': 'Расскажите о своем опыте работы с Python',
                    'category': 'Опыт',
                    'difficulty': 'medium',
                    'keywords': ['python', 'разработка', 'проект', 'опыт']
                },
                {
                    'question': 'Какие фреймворки Python вы использовали?',
                    'category': 'Технические навыки',
                    'difficulty': 'medium',
                    'keywords': ['django', 'flask', 'fastapi', 'фреймворк']
                },
                {
                    'question': 'Опишите ваш опыт работы с базами данных',
                    'category': 'Технические навыки',
                    'difficulty': 'medium',
                    'keywords': ['база данных', 'sql', 'orm', 'postgresql']
                },
                {
                    'question': 'Как вы тестируете свой код?',
                    'category': 'Процессы',
                    'difficulty': 'medium',
                    'keywords': ['тестирование', 'unit test', 'pytest', 'tdd']
                },
                {
                    'question': 'Расскажите о вашем опыте работы с Docker',
                    'category': 'DevOps',
                    'difficulty': 'medium',
                    'keywords': ['docker', 'контейнер', 'образ', 'docker-compose']
                }
            ],
            'Frontend разработчик': [
                {
                    'question': 'Расскажите о своем опыте работы с JavaScript',
                    'category': 'Опыт',
                    'difficulty': 'medium',
                    'keywords': ['javascript', 'js', 'разработка', 'проект']
                },
                {
                    'question': 'Какие фреймворки frontend вы использовали?',
                    'category': 'Технические навыки',
                    'difficulty': 'medium',
                    'keywords': ['react', 'angular', 'vue', 'фреймворк']
                }
            ]
        }
    
    def generate_questions(self, position: str, candidate_data: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """Генерация вопросов на основе позиции и данных кандидата"""
        if position not in self.question_bank:
            position = 'Python разработчик'  # По умолчанию
        
        questions = self.question_bank[position]
        
        # Адаптируем вопросы на основе опыта кандидата
        adapted_questions = []
        for q in questions:
            # Если у кандидата есть соответствующие навыки, добавляем вопрос
            if any(skill.lower() in candidate_data.get('skills', []) for skill in q['keywords']):
                adapted_questions.append(q)
        
        # Если не хватает вопросов, добавляем случайные
        if len(adapted_questions) < count:
            adapted_questions.extend([q for q in questions if q not in adapted_questions])
        
        return adapted_questions[:count]
    
    def evaluate_answer(self, question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Оценка ответа кандидата"""
        # Простая оценка на основе ключевых слов
        keywords = question['keywords']
        answer_lower = answer.lower()
        
        found_keywords = [kw for kw in keywords if kw.lower() in answer_lower]
        relevance_score = len(found_keywords) / len(keywords) if keywords else 0
        
        # Оценка полноты ответа
        completeness_score = min(1.0, len(answer.split()) / 50)  # Ориентир: 50 слов
        
        # Общая оценка
        overall_score = (relevance_score * 0.7 + completeness_score * 0.3) * 10
        
        return {
            'question': question['question'],
            'answer': answer,
            'relevance_score': relevance_score,
            'completeness_score': completeness_score,
            'overall_score': round(overall_score, 1),
            'found_keywords': found_keywords,
            'feedback': self._generate_feedback(question, answer, found_keywords, overall_score)
        }
    
    def _generate_feedback(self, question: Dict[str, Any], answer: str, found_keywords: List[str], score: float) -> str:
        """Генерация обратной связи по ответу"""
        if score >= 8:
            return "Отличный ответ! Вы подробно раскрыли тему и затронули все ключевые аспекты."
        elif score >= 6:
            return "Хороший ответ, но можно было бы более подробно раскрыть некоторые аспекты."
        elif score >= 4:
            return "Ответ частично соответствует вопросу. Рекомендуется углубить знания в этой области."
        else:
            return "Ответ не соответствует требованиям вопроса. Необходимо изучить тему более детально."