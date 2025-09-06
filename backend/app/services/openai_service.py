# Пытаемся импортировать и использовать реальный OpenAI
try:
    import openai
    from app.core.config import settings
    
    # Реализация с использованием реального OpenAI API
    class OpenAIService:
        def __init__(self):
            openai.api_key = settings.OPENAI_API_KEY
        
        def generate_interview_question(self, candidate_context, vacancy_requirements, previous_questions=None):
            """Генерация вопроса для интервью с помощью OpenAI"""
            prompt = f"""
            Ты - HR-специалист, проводящий техническое собеседование.
            
            Информация о кандидате: {candidate_context}
            Требования вакансии: {vacancy_requirements}
            
            История заданных вопросов: {previous_questions or "Нет"}
            
            Сгенерируй следующий вопрос для интервью, который поможет оценить соответствие кандидата требованиям.
            Вопрос должен быть:
            1. Конкретным и релевантным вакансии
            2. Открытым (не требующим ответа "да/нет")
            3. Помогающим выявить технические навыки или опыт
            """
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].text.strip()
        
        def analyze_answer_quality(self, question, answer, evaluation_criteria):
            """Анализ качества ответа кандидата"""
            prompt = f"""
            Оцени качество ответа кандидата на вопрос собеседования.
            
            Вопрос: {question}
            Ответ: {answer}
            Критерии оценки: {evaluation_criteria}
            
            Оцени ответ по шкале от 0 до 10, где:
            0 - ответ совершенно не релевантный или некорректный
            10 - ответ полный, точный и демонстрирующий экспертизу
            
            Верни только число (оценку) без пояснений.
            """
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=5,
                temperature=0.3
            )
            
            try:
                return float(response.choices[0].text.strip())
            except:
                # Если не удалось распарсить ответ, используем заглушку
                from app.services.mock_openai_service import MockOpenAIService
                mock_service = MockOpenAIService()
                return mock_service.analyze_answer_quality(question, answer, evaluation_criteria)
        
        def generate_feedback(self, candidate_name, interview_results, overall_score):
            """Генерация фидбека для кандидата"""
            prompt = f"""
            Сгенерируй конструктивный фидбек для кандидата {candidate_name} по результатам собеседования.
            
            Результаты интервью: {interview_results}
            Общая оценка: {overall_score}/10
            
            Фидбек должен быть:
            1. Профессиональным и вежливым
            2. Содержать конкретные сильные стороны
            3. Указать на области для улучшения
            4. Быть мотивирующим, даже если оценка низкая
            """
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                temperature=0.5
            )
            
            return response.choices[0].text.strip()

except ImportError:
    # Если openai не установлен, используем заглушку
    from app.services.mock_openai_service import MockOpenAIService
    OpenAIService = MockOpenAIService