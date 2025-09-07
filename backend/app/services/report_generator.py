# backend/app/services/report_generator.py
from typing import Dict, Any
import json
from datetime import datetime
from fpdf import FPDF
import os

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(candidate_data: Dict[str, Any], interview_data: Dict[str, Any]) -> str:
        """Генерация PDF отчета о кандидате"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Заголовок
        pdf.set_font_size(16)
        pdf.cell(200, 10, txt="Отчет о кандидате", ln=True, align='C')
        pdf.ln(10)
        
        # Информация о кандидате
        pdf.set_font_size(12)
        pdf.cell(200, 10, txt=f"Имя: {candidate_data.get('name', '')}", ln=True)
        pdf.cell(200, 10, txt=f"Позиция: {candidate_data.get('position', '')}", ln=True)
        pdf.cell(200, 10, txt=f"Email: {candidate_data.get('email', '')}", ln=True)
        pdf.cell(200, 10, txt=f"Телефон: {candidate_data.get('phone', '')}", ln=True)
        pdf.ln(10)
        
        # Результаты интервью
        pdf.cell(200, 10, txt="Результаты интервью:", ln=True)
        pdf.set_font_size(10)
        
        for qa in interview_data.get('qa_results', []):
            pdf.cell(200, 10, txt=f"Вопрос: {qa['question']}", ln=True)
            pdf.cell(200, 10, txt=f"Ответ: {qa['answer'][:100]}...", ln=True)
            pdf.cell(200, 10, txt=f"Оценка: {qa['overall_score']}/10", ln=True)
            pdf.cell(200, 10, txt=f"Обратная связь: {qa['feedback']}", ln=True)
            pdf.ln(5)
        
        # Общая оценка
        overall_score = interview_data.get('overall_score', 0)
        pdf.set_font_size(12)
        pdf.cell(200, 10, txt=f"Общая оценка: {overall_score}/10", ln=True)
        
        # Сохранение файла
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        filename = f"{report_dir}/report_{candidate_data.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        
        return filename
    
    @staticmethod
    def generate_json_report(candidate_data: Dict[str, Any], interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация JSON отчета о кандидате"""
        return {
            'candidate': candidate_data,
            'interview': interview_data,
            'generated_at': datetime.now().isoformat(),
            'overall_assessment': {
                'score': interview_data.get('overall_score', 0),
                'recommendation': ReportGenerator._get_recommendation(interview_data.get('overall_score', 0))
            }
        }
    
    @staticmethod
    def _get_recommendation(score: float) -> str:
        """Определение рекомендации на основе оценки"""
        if score >= 8:
            return "Сильно рекомендуется к найму"
        elif score >= 6:
            return "Рекомендуется к найму"
        elif score >= 4:
            return "Рассмотреть с другими кандидатами"
        else:
            return "Не рекомендуется"