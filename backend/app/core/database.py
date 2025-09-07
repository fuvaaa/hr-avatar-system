# Для разработки используем SQLite
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if os.getenv("ENVIRONMENT") == "production":
    # Продакшн-база на Render
    SQLALCHEMY_DATABASE_URL = "postgresql://hr_avatar_db_user:uJCa0UVx8Cjfnjp0EyvkGndWeZoZeOHB@dpg-d2u56vmr433s73dvtqng-a/hr_avatar_db"
else:
    # Локальная SQLite для разработки
    SQLALCHEMY_DATABASE_URL = "sqlite:///./hr_avatar.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()