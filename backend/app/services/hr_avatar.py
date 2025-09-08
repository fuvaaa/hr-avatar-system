# app/services/hr_avatar.py
import requests
import openai
from typing import List, Dict
from app.core.config import settings

# Инициализация API ключей
HUGGINGFACE_API_KEY = getattr(settings, 'HUGGINGFACE_API_KEY', None)
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)

# Проверяем доступность провайдеров
HUGGINGFACE_AVAILABLE = bool(HUGGINGFACE_API_KEY)
OPENAI_AVAILABLE = False

if OPENAI_API_KEY:
    try:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        openai_client.models.list()
        OPENAI_AVAILABLE = True
    except:
        pass

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
    Генерирует ответ HR-аватара с использованием доступного провайдера
    """
    # Пробуем в порядке приоритета: Hugging Face -> OpenAI -> Заглушка
    if HUGGINGFACE_AVAILABLE:
        return generate_huggingface_response(candidate_message, conversation_history)
    elif OPENAI_AVAILABLE:
        return generate_openai_response(candidate_message, conversation_history)
    else:
        return generate_fallback_response(candidate_message)

# app/services/hr_avatar.py
def generate_huggingface_response(candidate_message: str, conversation_history: List[Dict] = None) -> Dict[str, str]:
    # Используем более продвинутую модель
    API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    
    # Формируем промпт с учетом истории
    context = ""
    if conversation_history:
        for msg in conversation_history[-3:]:  # Берем только последние 3 сообщения
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            context += f"{role}: {msg['content']}\n"
    
    prompt = f"{context}Пользователь: {candidate_message}\nАссистент:"
    
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
            # Извлекаем только последний ответ ассистента
            if "Ассистент:" in generated_text:
                hr_response = generated_text.split("Ассистент:")[-1].strip()
            else:
                hr_response = generated_text.replace(prompt, "").strip()
            
            # Фильтруем нежелательные ответы
            if len(hr_response) > 10 and "расскажите" not in hr_response.lower():
                return {
                    "response": hr_response,
                    "suggestions": generate_suggestions(candidate_message, hr_response)
                }
        
        # Если ответ не подошел, используем умную заглушку
        return generate_smart_fallback(candidate_message, conversation_history)
        
    except Exception as e:
        print(f"Error generating Hugging Face response: {e}")
        return generate_fallback_response(candidate_message)
    
def generate_openai_response(candidate_message: str, conversation_history: List[Dict] = None) -> Dict[str, str]:
    """
    Генерирует ответ с использованием OpenAI API
    """
    messages = [{"role": "system", "content": HR_SYSTEM_PROMPT}]
    
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": candidate_message})
    
    try:
        response = openai_client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=messages,
            temperature=getattr(settings, 'OPENAI_TEMPERATURE', 0.7),
            max_tokens=getattr(settings, 'OPENAI_MAX_TOKENS', 150)
        )
        
        hr_response = response.choices[0].message.content.strip()
        suggestions = generate_suggestions(candidate_message, hr_response)
        
        return {
            "response": hr_response,
            "suggestions": suggestions
        }
    except Exception as e:
        print(f"Error generating OpenAI response: {e}")
        return generate_fallback_response(candidate_message)

def generate_fallback_response(candidate_message: str) -> Dict[str, str]:
    """
    Генерирует ответ HR-аватара с помощью заглушки
    """
    suggestions = generate_suggestions(candidate_message, "")
    
    message_lower = candidate_message.lower()
    
    if any(word in message_lower for word in ["опыт", "работал", "проект", "должность", "компания"]):
        response = "Спасибо за информацию. Расскажите подробнее о проектах, над которыми вы работали?"
    elif any(word in message_lower for word in ["навык", "умение", "знание", "технология", "язык"]):
        response = "Интересно. Как вы оцениваете свой уровень в этой области?"
    elif any(word in message_lower for word in ["хочу", "цель", "план", "карьера", "работать"]):
        response = "Понятно. Почему вы хотите работать именно в нашей компании?"
    else:
        response = "Спасибо за ваш ответ. Можете рассказать подробнее о вашем опыте?"
    
    return {
        "response": response,
        "suggestions": suggestions
    }

def generate_suggestions(candidate_message: str, hr_response: str) -> List[str]:
    """
    Генерирует дополнительные вопросы, которые HR может задать кандидату
    """
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
            "Приведите пример вашей успешной работы в команде"
        ]
    }
    
    message_lower = candidate_message.lower()
    
    if any(word in message_lower for word in ["опыт", "работал", "проект", "должность", "компания"]):
        category = "experience"
    elif any(word in message_lower for word in ["навык", "умение", "знание", "технология", "язык"]):
        category = "skills"
    elif any(word in message_lower for word in ["хочу", "цель", "план", "карьера", "работать"]):
        category = "motivation"
    else:
        category = "behavior"
    
    import random
    return random.sample(base_questions[category], 2)

def generate_hr_response_with_context(interview_id: int, candidate_message: str, db) -> Dict[str, str]:
    """
    Генерирует ответ HR с учетом полной истории диалога из базы данных
    """
    from app.models import Message
    
    messages = db.query(Message).filter(Message.interview_id == interview_id).order_by(Message.created_at).all()
    
    conversation_history = []
    for msg in messages:
        role = "user" if msg.sender_type == "candidate" else "assistant"
        conversation_history.append({"role": role, "content": msg.text})
    
    return generate_hr_response(candidate_message, conversation_history)

# Дополнительные функции для распознавания и синтеза речи
def speech_to_text(audio_file_path: str) -> str:
    """
    Распознает речь в текст с использованием Hugging Face
    """
    if not HUGGINGFACE_API_KEY:
        raise ValueError("Hugging Face API key not configured")
    
    API_URL = "https://api-inference.huggingface.co/models/facebook/wav2vec2-base-960h"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    with open(audio_file_path, "rb") as f:
        data = f.read()
    
    try:
        response = requests.post(API_URL, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")
    except Exception as e:
        print(f"Error in speech-to-text: {e}")
        return ""

def text_to_speech(text: str, output_file: str = "output.wav") -> str:
    """
    Преобразует текст в речь с использованием Hugging Face
    """
    if not HUGGINGFACE_API_KEY:
        raise ValueError("Hugging Face API key not configured")
    
    API_URL = "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    payload = {"inputs": text}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        return output_file
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return ""