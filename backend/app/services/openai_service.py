from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI настройки
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # Модель по умолчанию
    
    # База данных
    DATABASE_URL: str = "sqlite:///./hr_avatar.db"
    
    # Фронтенд
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Другие настройки
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Создаем экземпляр настроек
settings = Settings()