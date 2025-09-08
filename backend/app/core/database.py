from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Используем переменную окружения для подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Создание таблиц если они не существуют"""
    Base.metadata.create_all(bind=engine, checkfirst=True)