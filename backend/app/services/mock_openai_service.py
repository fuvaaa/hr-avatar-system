import random
import re
from typing import Dict, Any, List

class MockOpenAIService:
    def __init__(self):
        # Инициализация без реального API ключа
        pass
    
    def generate_interview_question(self, candidate_context, vacancy_requirements, previous_questions=None):
        """Генерация вопроса для интервью с помощью шаблонов"""
        # Извлекаем ключевые навыки из требований вакансии
        skills = self._extract_skills(vacancy_requirements)
        position = self._extract_position(vacancy_requirements)
        
        # Базовые вопросы по категориям
        question_templates = {
            "experience": [
                f"Расскажите о вашем опыте работы с {random.choice(skills) if skills else 'этой технологией'}",
                "Опишите самый сложный проект, над которым вы работали",
                "С какими сложностями вы столкнулись в предыдущих проектах?"
            ],
            "technical": [
                f"Как вы решаете проблемы, связанные с {random.choice(skills) if skills else 'техническими задачами'}?",
                f"Опишите ваш опыт работы с {random.choice(skills) if skills else 'базами данных'}",
                "Какие паттерны проектирования вы использовали в своей практике?"
            ],
            "soft_skills": [
                "Как вы работаете в команде?",
                "Опишите ситуацию, когда вам пришлось разрешить конфликт",
                "Как вы справляетесь с дедлайнами и давлением?"
            ],
            "motivation": [
                "Почему вы хотите работать в нашей компании?",
                "Какие ваши карьерные цели на ближайшие 3 года?",
                "Что вас привлекает в этой позиции?"
            ]
        }
        
        # Выбираем категорию вопроса
        if not previous_questions:
            category = "experience"
        elif len(previous_questions) < 3:
            category = "technical"
        elif len(previous_questions) < 5:
            category = "soft_skills"
        else:
            category = "motivation"
        
        # Выбираем случайный вопрос из категории
        question = random.choice(question_templates[category])
        
        # Проверяем, что вопрос не повторялся
        if previous_questions and question in previous_questions:
            # Если вопрос повторился, берем другой
            available_questions = [q for q in question_templates[category] if q not in previous_questions]
            if available_questions:
                question = random.choice(available_questions)
            else:
                # Если все вопросы из категории заданы, переходим к следующей
                categories = list(question_templates.keys())
                current_index = categories.index(category)
                next_category = categories[(current_index + 1) % len(categories)]
                question = random.choice(question_templates[next_category])
        
        return question
    
    def analyze_answer_quality(self, question, answer, evaluation_criteria):
        """Анализ качества ответа кандидата на основе ключевых слов и длины"""
        # Базовая оценка
        score = 5.0
        
        # Увеличиваем оценку за длину ответа
        if len(answer) > 200:
            score += 1.0
        elif len(answer) > 100:
            score += 0.5
        
        # Увеличиваем оценку за наличие технических терминов
        tech_terms = ["алгоритм", "база данных", "API", "фреймворк", "библиотека", 
                     "архитектура", "оптимизация", "тестирование", "развертывание", "безопасность"]
        for term in tech_terms:
            if term.lower() in answer.lower():
                score += 0.3
        
        # Увеличиваем оценку за наличие примеров
        if "например" in answer.lower() or "к примеру" in answer.lower():
            score += 0.5
        
        # Увеличиваем оценку за структурированность ответа
        if re.search(r'\d+\.', answer):  # Наличие нумерованных списков
            score += 0.3
        
        # Уменьшаем оценку за избегание ответа
        avoidance_phrases = ["не знаю", "не работал", "не имею опыта", "не могу сказать"]
        for phrase in avoidance_phrases:
            if phrase in answer.lower():
                score -= 1.0
        
        # Ограничиваем оценку от 0 до 10
        return max(0.0, min(10.0, score))
    
    def generate_feedback(self, candidate_name, interview_results, overall_score):
        """Генерация фидбека для кандидата на основе оценки"""
        # Определяем уровень кандидата
        if overall_score >= 8.0:
            level = "высокий"
            strengths = ["технические навыки", "опыт работы", "коммуникативные навыки"]
            improvements = []
            recommendation = "сильно рекомендуем"
        elif overall_score >= 6.0:
            level = "хороший"
            strengths = ["технические навыки"]
            improvements = ["некоторые аспекты, требующие развития"]
            recommendation = "рекомендуем"
        elif overall_score >= 4.0:
            level = "средний"
            strengths = ["мотивация"]
            improvements = ["технические навыки", "опыт работы"]
            recommendation = "рассмотрим на следующие этапы"
        else:
            level = "низкий"
            strengths = ["мотивация к обучению"]
            improvements = ["технические навыки", "опыт работы", "коммуникативные навыки"]
            recommendation = "не рекомендуем"
        
        # Генерируем фидбек
        feedback = f"""
{candidate_name}, спасибо за уделенное время на прохождение интервью.

Наши эксперты оценили ваши ответы на {overall_score:.1f} баллов из 10, что соответствует {level} уровню.

Сильные стороны:
"""
        
        # Добавляем сильные стороны
        for strength in strengths:
            feedback += f"- Хорошо проявили себя в области {strength}\n"
        
        if improvements:
            feedback += "\nОбласти для улучшения:\n"
            for improvement in improvements:
                feedback += f"- Рекомендуем обратить внимание на {improvement}\n"
        
        feedback += f"""
На основании результатов нашего интервью мы {recommendation} вас к следующему этапу отбора.

Желаем успехов в поиске работы!
        """
        
        return feedback.strip()
    
    def _extract_skills(self, text: str) -> List[str]:
        """Извлечение навыков из текста"""
        # Простое извлечение навыков на основе ключевых слов
        common_skills = [
            "Python", "JavaScript", "Java", "C++", "React", "Angular", "Vue.js",
            "Django", "Flask", "Spring", "Node.js", "Express", "PostgreSQL",
            "MongoDB", "MySQL", "Docker", "Kubernetes", "AWS", "Git", "Linux"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills if found_skills else ["программирование"]
    
    def _extract_position(self, text: str) -> str:
        """Извлечение должности из текста"""
        # Простое извлечение должности
        positions = [
            "разработчик", "программист", "инженер", "архитектор", "аналитик",
            "менеджер", "дизайнер", "тестировщик", "devops", "data scientist"
        ]
        
        text_lower = text.lower()
        
        for position in positions:
            if position in text_lower:
                return position
        
        return "специалист"