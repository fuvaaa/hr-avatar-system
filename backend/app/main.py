from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import candidates, interviews, reports
from app.core.database import Base, engine

app = FastAPI(title="HR Avatar System API")

# Отладочный вывод
print("Проверка импортов:")
print("candidates.router:", candidates.router)
print("interviews.router:", interviews.router)
print("reports.router:", reports.router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.get("/test")
async def test():
    return {"message": "Тестовый эндпоинт работает"}

@app.on_event("startup")
async def startup_event():
    # Создаем таблицы при запуске
    Base.metadata.create_all(bind=engine)
    print("Таблицы базы данных созданы")