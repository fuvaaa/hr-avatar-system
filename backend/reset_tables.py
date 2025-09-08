# reset_tables.py
import os
from sqlalchemy import create_engine
from app.models import Base

DATABASE_URL = "postgresql://hr_avatar_db_user:uJCa0UVx8Cjfnjp0EyvkGndWeZoZeOHB@dpg-d2u56vmr433s73dvtqng-a.oregon-postgres.render.com:5432/hr_avatar_db?sslmode=require"

engine = create_engine(DATABASE_URL)

# Удаляем все таблицы
print("Удаление существующих таблиц...")
Base.metadata.drop_all(bind=engine)

# Создаем таблицы заново
print("Создание таблиц...")
Base.metadata.create_all(bind=engine)

print("Таблицы успешно пересозданы!")