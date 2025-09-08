from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import candidates, interviews, reports
from app.core.database import engine, Base, create_tables
from app.models import *  # Важно импортировать все модели

app = FastAPI(title="HR Avatar System API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gorgeous-douhua-863790.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "HR Avatar System API"}

@app.on_event("startup")
async def startup_event():
    # Создаем таблицы при запуске
    create_tables()
    print("Таблицы базы данных созданы или уже существуют")