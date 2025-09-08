import openai
from typing import List, Dict
from app.core.config import settings

# Инициализация OpenAI с API ключом
openai.api_key = settings.OPENAI_API_KEY

# Шаблон системного промпта для HR-аватара
HR_SYSTEM_PROMPT = """
Вы - HR-специалист, проводящий техническое собеседование с кандидатом на позицию разработчика.
Ваша задача - задавать релевантные вопросы о опыте, навыках и мотивации кандидата.
Будьте профессиональны, дружелюбны и конкретны.
Не давайте прямых оценок кандидату, сосредоточьтесь на сборе информации.
Ваши вопросы должны быть открытыми и побуждать кандидата к развернутым ответам.
"""

def generate_hr_response(candidate_message: str, conversation_history: List[Dict] = None) -> Dict[str, str]:
    """
    Генерирует ответ HR-аватара на сообщение кандидата с использованием OpenAI API
    """
    # Формируем сообщения для API
    messages = [{"role": "system", "content": HR_SYSTEM_PROMPT}]
    
    # Добавляем историю диалога, если она есть
    if conversation_history:
        messages.extend(conversation_history)
    
    # Добавляем текущее сообщение кандидата
    messages.append({"role": "user", "content": candidate_message})
    
    try:
        # Вызываем OpenAI API
        response = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS
        )
        
        # Извлекаем текст ответа
        hr_response = response.choices[0].message['content'].strip()
        
        # Генерируем дополнительные вопросы
        suggestions = generate_suggestions(candidate_message, hr_response)
        
        return {
            "response": hr_response,
            "suggestions": suggestions
        }
    
    except Exception as e:
        # В случае ошибки возвращаем запасной вариант
        print(f"Error generating HR response: {e}")
        return {
            "response": "Спасибо за ваш ответ. Можете рассказать подробнее о вашем опыте?",
            "suggestions": ["Какие технологии вы использовали в своих проектах?", "Расскажите о самой сложной задаче, которую вам приходилось решать?"]
        }

def generate_suggestions(candidate_message: str, hr_response: str) -> List[str]:
    """
    Генерирует дополнительные вопросы, которые HR может задать кандидату
    """
    # Базовые вопросы по категориям
    base_questions = {
        "experience": [
            "Расскажите о самом сложном проекте, над которым вы работали.",
            "Какие задачи вы выполняли на предыдущем месте работы?",
            "С какими трудностями вы столкнулись в своем последнем проекте?"
        ],
        "skills": [
            "Как вы оцениваете свой уровень владения Python?",
            "Какие фреймворки вы использовали в своей работе?",
            "Как вы поддерживаете свои технические навыки в актуальном состоянии?"
        ],
        "motivation": [
            "Почему вы хотите работать именно в нашей компании?",
            "Что вас привлекает в этой вакансии?",
            "Какие ваши карьерные цели на ближайшие 3 года?"
        ],
        "behavior": [
            "Опишите ситуацию, когда вам пришлось работать в стрессовых условиях.",
            "Как вы разрешаете конфликты в команде?",
            "Приведите пример вашей успешной работы в команде."
        ]
    }
    
    # Простая эвристика для выбора категории
    message_lower = candidate_message.lower()
    
    if any(word in message_lower for word in ["опыт", "работал", "проект", "должность", "компания"]):
        category = "experience"
    elif any(word in message_lower for word in ["навык", "умение", "знание", "технология", "язык"]):
        category = "skills"
    elif any(word in message_lower for word in ["хочу", "цель", "план", "карьера", "работать"]):
        category = "motivation"
    else:
        category = "behavior"
    
    # Возвращаем 2 случайных вопроса из выбранной категории
    import random
    return random.sample(base_questions[category], 2)

def generate_hr_response_with_context(interview_id: int, candidate_message: str, db) -> Dict[str, str]:
    """
    Генерирует ответ HR с учетом полной истории диалога из базы данных
    """
    # Получаем историю диалога из БД
    from app.models import Message
    
    messages = db.query(Message).filter(Message.interview_id == interview_id).order_by(Message.created_at).all()
    
    # Форматируем историю для OpenAI
    conversation_history = []
    for msg in messages:
        role = "user" if msg.sender_type == "candidate" else "assistant"
        conversation_history.append({"role": role, "content": msg.text})
    
    # Генерируем ответ с учетом истории
    return generate_hr_response(candidate_message, conversation_history)