# backend/app/services/resume_parser.py
import PyPDF2
import docx
import re
from typing import Dict, Any

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return " ".join([page.extract_text() for page in reader.pages])
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])
    
    @staticmethod
    def parse_resume(file_path: str) -> Dict[str, Any]:
        if file_path.endswith('.pdf'):
            text = ResumeParser.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = ResumeParser.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Извлечение данных с помощью регулярных выражений
        data = {
            'name': ResumeParser._extract_name(text),
            'email': ResumeParser._extract_email(text),
            'phone': ResumeParser._extract_phone(text),
            'skills': ResumeParser._extract_skills(text),
            'experience': ResumeParser._extract_experience(text),
            'education': ResumeParser._extract_education(text)
        }
        
        return data
    
    @staticmethod
    def _extract_name(text: str) -> str:
        # Упрощенный алгоритм извлечения имени
        lines = text.split('\n')
        for line in lines[:5]:  # Имя обычно в начале документа
            if len(line.split()) >= 2 and all(word[0].isupper() for word in line.split()[:2]):
                return line.strip()
        return ""
    
    @staticmethod
    def _extract_email(text: str) -> str:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else ""
    
    @staticmethod
    def _extract_phone(text: str) -> str:
        phone_pattern = r'(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,6})'
        match = re.search(phone_pattern, text)
        return match.group() if match else ""
    
    @staticmethod
    def _extract_skills(text: str) -> list:
        # Базовый список навыков для поиска
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'HTML', 'CSS',
            'React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'Git', 'Linux'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def _extract_experience(text: str) -> list:
        # Упрощенное извлечение опыта работы
        experience = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Поиск строк с годами (2018-2020, 2019 - настоящее время)
            year_pattern = r'(19|20)\d{2}[\s-–—]*(19|20)\d{2}|настоящее время'
            if re.search(year_pattern, line):
                # Берем предыдущую строку как должность/компанию
                if i > 0:
                    experience.append({
                        'position': lines[i-1].strip(),
                        'period': line.strip()
                    })
        
        return experience
    
    @staticmethod
    def _extract_education(text: str) -> list:
        # Упрощенное извлечение образования
        education = []
        lines = text.split('\n')
        
        education_keywords = ['университет', 'институт', 'академия', 'образование']
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in education_keywords):
                # Берем следующую строку как специальность
                if i+1 < len(lines):
                    education.append({
                        'institution': line.strip(),
                        'degree': lines[i+1].strip()
                    })
        
        return education