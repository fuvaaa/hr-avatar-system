from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview import Interview
from app.models.candidate import Candidate
from typing import List, Dict, Any
import os
import json
from datetime import datetime, timedelta

router = APIRouter()

class AIInterviewer:
    """Простой AI-интервьюер для генерации вопросов и оценки ответов"""
    
    def __init__(self):
        # База вопросов по разным направлениям
        self.question_bank = {
            'Python разработчик': [
                {
                    'id': 1,
                    'question': 'Расскажите о своем опыте работы с Python',
                    'category': 'Опыт',
                    'difficulty': 'medium',
                    'keywords': ['python', 'разработка', 'проект', 'опыт']
                },
                {
                    'id': 2,
                    'question': 'Какие фреймворки Python вы использовали?',
                    'category': 'Технические навыки',
                    'difficulty': 'medium',
                    'keywords': ['django', 'flask', 'fastapi', 'фреймворк']
                },
                {
                    'id': 3,
                    'question': 'Опишите ваш опыт работы с базами данных',
                    'category': 'Технические навыки',
                    'difficulty': 'medium',
                    'keywords': ['база данных', 'sql', 'orm', 'postgresql']
                },
                {
                    'id': 4,
                    'question': 'Как вы тестируете свой код?',
                    'category': 'Процессы',
                    'difficulty': 'medium',
                    'keywords': ['тестирование', 'unit test', 'pytest', 'tdd']
                },
                {
                    'id': 5,
                    'question': 'Расскажите о вашем опыте работы с Docker',
                    'category': 'DevOps',
                    'difficulty': 'medium',
                    'keywords': ['docker', 'контейнер', 'образ', 'docker-compose']
                }
            ],
            'Frontend разработчик': [
                {
                    'id': 6,
                    'question': 'Расскажите о своем опыте работы с JavaScript',
                    'category': 'Опыт',
                    'difficulty': 'medium',
                    'keywords': ['javascript', 'js', 'разработка', 'проект']
                },
                {
                    'id': 7,
                    'question': 'Какие фреймворки frontend вы использовали?',
                    'category': 'Технические навыки',
                    'difficulty': 'medium',
                    'keywords': ['react', 'angular', 'vue', 'фреймворк']
                }
            ]
        }
    
    def generate_questions(self, position: str, candidate_skills: List[str], count: int = 5) -> List[Dict[str, Any]]:
        """Генерация вопросов на основе позиции и навыков кандидата"""
        if position not in self.question_bank:
            position = 'Python разработчик'  # По умолчанию
        
        questions = self.question_bank[position]
        
        # Адаптируем вопросы на основе навыков кандидата
        adapted_questions = []
        for q in questions:
            # Если у кандидата есть соответствующие навыки, добавляем вопрос
            if any(skill.lower() in [s.lower() for s in candidate_skills] for skill in q['keywords']):
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

@router.post("/", response_model=dict)
async def create_interview(
    candidate_id: int,
    vacancy_id: int,
    db: Session = Depends(get_db)
):
    """Создание интервью с AI-генерацией вопросов"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Получаем навыки кандидата
    candidate_skills = json.loads(candidate.skills) if candidate.skills else []
    
    # Генерация вопросов
    ai_interviewer = AIInterviewer()
    questions = ai_interviewer.generate_questions(candidate.position, candidate_skills)
    
    # Создание интервью
    interview = Interview(
        candidate_id=candidate_id,
        vacancy_id=vacancy_id,
        status="scheduled",
        questions=json.dumps(questions),  # Сохраняем вопросы как JSON
        start_time=datetime.now() + timedelta(days=1)  # Запланируем на завтра
    )
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return {
        "id": interview.id,
        "candidate_id": interview.candidate_id,
        "status": interview.status,
        "scheduled_time": interview.start_time.isoformat() if interview.start_time else None,
        "questions": questions
    }

@router.get("/", response_model=List[dict])
async def get_interviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interviews = db.query(Interview).offset(skip).limit(limit).all()
    return [
        {
            "id": interview.id,
            "candidate_id": interview.candidate_id,
            "status": interview.status,
            "start_time": interview.start_time,
            "end_time": interview.end_time,
            "match_score": interview.match_score,
            "feedback": interview.feedback
        }
        for interview in interviews
    ]

@router.get("/{interview_id}", response_model=dict)
async def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return {
        "id": interview.id,
        "candidate_id": interview.candidate_id,
        "status": interview.status,
        "start_time": interview.start_time,
        "end_time": interview.end_time,
        "match_score": interview.match_score,
        "feedback": interview.feedback,
        "questions": json.loads(interview.questions) if interview.questions else [],
        "answers": json.loads(interview.answers) if interview.answers else []
    }

@router.post("/{interview_id}/submit-answers")
async def submit_answers(
    interview_id: int,
    answers: List[Dict[str, Any]],  # [{"question_id": 1, "answer": "текст ответа"}]
    db: Session = Depends(get_db)
):
    """Отправка ответов и их AI-оценка"""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Получаем вопросы
    questions = json.loads(interview.questions) if interview.questions else []
    
    # Оценка ответов
    ai_interviewer = AIInterviewer()
    qa_results = []
    total_score = 0
    
    for answer_data in answers:
        question_id = answer_data.get('question_id')
        answer_text = answer_data.get('answer', '')
        
        # Находим вопрос
        question = next((q for q in questions if q.get('id') == question_id), None)
        if not question:
            continue
        
        # Оцениваем ответ
        evaluation = ai_interviewer.evaluate_answer(question, answer_text)
        qa_results.append(evaluation)
        total_score += evaluation['overall_score']
    
    # Обновляем интервью
    interview.answers = json.dumps(qa_results)  # Сохраняем ответы как JSON
    interview.match_score = total_score / len(qa_results) if qa_results else 0
    interview.status = "completed"
    interview.end_time = datetime.now()
    db.commit()
    
    # Обновляем процент соответствия кандидата
    candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
    if candidate:
        candidate.match_percentage = interview.match_score
        db.commit()
    
    return {
        "interview_id": interview.id,
        "match_score": interview.match_score,
        "qa_results": qa_results,
        "status": "completed",
        "candidate_match_percentage": candidate.match_percentage if candidate else None
    }

@router.post("/generate-example")
async def generate_interview_example(db: Session = Depends(get_db)):
    """Генерация примера прохождения интервью с тестовыми данными"""
    
    # Создаем тестового кандидата
    candidate = Candidate(
        name="Иван Петров",
        email="ivan.petrov@example.com",
        phone="+7 (900) 123-45-67",
        resume_path="uploads/ivan_petrov_resume.pdf",
        position="Python разработчик",
        skills=json.dumps(["Python", "FastAPI", "PostgreSQL", "Docker", "Git"]),
        experience=json.dumps([
            {
                "company": "Технологии Будущего",
                "position": "Middle Python Developer",
                "period": "2020-2023"
            },
            {
                "company": "Цифровые Решения",
                "position": "Junior Python Developer",
                "period": "2018-2020"
            }
        ]),
        education=json.dumps([
            {
                "institution": "Московский Технический Университет",
                "degree": "Магистр",
                "specialty": "Программная инженерия",
                "year": "2018"
            }
        ]),
        match_percentage=85.5,
        status="processed"
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    # Создаем тестовое интервью
    start_time = datetime.now() - timedelta(days=5)
    end_time = start_time + timedelta(hours=1, minutes=30)
    
    ai_interviewer = AIInterviewer()
    questions = ai_interviewer.generate_questions(candidate.position, json.loads(candidate.skills))
    
    # Генерируем ответы
    answers = []
    for q in questions:
        answers.append({
            "question_id": q['id'],
            "answer": f"Пример ответа на вопрос: {q['question']}. Я имею большой опыт в этой области..."
        })
    
    # Оцениваем ответы
    qa_results = []
    total_score = 0
    for i, answer_data in enumerate(answers):
        evaluation = ai_interviewer.evaluate_answer(questions[i], answer_data['answer'])
        qa_results.append(evaluation)
        total_score += evaluation['overall_score']
    
    interview = Interview(
        candidate_id=candidate.id,
        status="completed",
        start_time=start_time,
        end_time=end_time,
        match_score=total_score / len(qa_results) if qa_results else 0,
        feedback="Кандидат показал отличные технические знания. Хорошо разбирается в Python и фреймворках. Имеет практический опыт работы с базами данных. Рекомендуется к найму.",
        questions=json.dumps(questions),  # Сохраняем вопросы как JSON
        answers=json.dumps(qa_results)    # Сохраняем ответы как JSON
    )
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return {
        "message": "Пример интервью успешно создан",
        "candidate_id": candidate.id,
        "interview_id": interview.id,
        "details": {
            "candidate": {
                "name": candidate.name,
                "position": candidate.position,
                "match_percentage": candidate.match_percentage
            },
            "interview": {
                "status": interview.status,
                "match_score": interview.match_score,
                "duration": str(interview.end_time - interview.start_time) if interview.end_time and interview.start_time else "N/A"
            }
        }
    }