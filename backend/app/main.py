from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import candidates, interviews, reports


# Импорты из текущего пакета
from .api import candidates, interviews, reports
from .core.database import engine
from app.core.database import Base


app = FastAPI(title="HR Avatar System API")

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

@app.on_event("startup")
async def startup_event():
    # Создаем таблицы при запуске
    from app.core.database import engine
    from app.models import Base
    Base.metadata.create_all(bind=engine)