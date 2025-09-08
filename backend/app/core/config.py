from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # OpenAI настройки
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # База данных
    DATABASE_URL: str = "sqlite:///./hr_avatar.db"
    
    # Фронтенд
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Другие настройки
    DEBUG: bool = False
    
    # Генерируем секретный ключ, если он не задан
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()